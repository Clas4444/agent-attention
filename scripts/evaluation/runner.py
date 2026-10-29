"""Run versioned real-Codex benchmark trials. Requires explicit local CLI access; never run in CI.

Output must be a new directory outside this repository. Records private raw traces
there. All model invocations are billable/consume host usage; inspect before use.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path
import shutil
import subprocess
import sys
import time

if __package__.startswith("scripts."):
    from ..effort_campaign import campaign_plan, summarize_campaign
else:
    from effort_campaign import campaign_plan, summarize_campaign
from .cases import ROOT, CASE_IDS, load_case
from .acceptance import changes, check_candidate

_DEFAULT_CASE = load_case()
FILES, TASK = _DEFAULT_CASE['files'], _DEFAULT_CASE['task']
PROFILES = {label: ','.join(f'{axis}={level}' for axis in
            ('focus', 'sync', 'batch', 'explore', 'verify'))
            for label, level in [('low', 1), ('balanced', 3), ('high', 5)]}
ORDER = ('low', 'balanced', 'high', 'high', 'balanced', 'low')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assess_usage(usage):
    """Keep unavailable usage unknown; reject impossible totals."""
    if usage is None:
        return None
    if not isinstance(usage, dict):
        raise ValueError('usage must be an object')
    fields = ('input_tokens', 'cached_input_tokens', 'output_tokens')
    if any(type(usage.get(k)) is not int or usage[k] < 0 for k in fields):
        raise ValueError('invalid usage')
    if usage['cached_input_tokens'] > usage['input_tokens']:
        raise ValueError('cached input exceeds total')
    return dict(usage, uncached_input_tokens=usage['input_tokens'] - usage['cached_input_tokens'],
                total_tokens=usage['input_tokens'] + usage['output_tokens'])


def environment_failure(events, stderr):
    """Inspect transport failures, never model messages or command output."""
    messages = [stderr]
    for event in events:
        if event.get('type') == 'error':
            messages.append(event.get('message'))
        elif event.get('type') == 'turn.failed':
            error = event.get('error')
            messages.append(error.get('message') if isinstance(error, dict) else error)
    text = '\n'.join(message for message in messages if isinstance(message, str)).casefold()
    if 'hit your usage limit' in text:
        return 'QUOTA_LIMIT'
    if '429 too many requests' in text or 'http 429' in text:
        return 'RATE_LIMIT'
    if 'selected model is at capacity' in text:
        return 'MODEL_CAPACITY'
    return None


def classify_trial(code, events, stderr, changed, acceptance_exit, work_changed=False):
    """An environment hint cannot excuse failed or partially executed work."""
    actions = [e for e in events if e.get('type') in ('item.started', 'item.completed')
               and e.get('item', {}).get('type') in ('command_execution', 'file_change', 'mcp_tool_call')]
    completed = any(e.get('type') == 'turn.completed' for e in events)
    if not actions and not completed and not changed and not work_changed and environment_failure(events, stderr):
        return 'BLOCKED_ENVIRONMENT'
    return 'PASS' if code == 0 and completed and not changed and acceptance_exit == 0 else 'FAIL'


def run(output, cli, timeout, order=ORDER, campaign=None, disabled_skills=(), case_id='cents'):
    case = load_case(case_id)
    if type(timeout) is not int or timeout <= 0:
        raise ValueError('timeout must be a positive integer')
    if (not isinstance(disabled_skills, (list, tuple))
            or any(not isinstance(path, str) or not path or '\n' in path or '\r' in path
                   for path in disabled_skills)):
        raise ValueError('disabled skills must be a list of exact SKILL.md paths')
    campaign = campaign or dict(campaign_plan(), order=list(order), planned_trials=len(order))
    profiles = campaign['profiles']
    if (not order or list(order) != list(campaign['order'])
            or any(label not in profiles or not re.fullmatch('[a-z][a-z0-9-]{0,63}',label) for label in order)):
        raise ValueError('execution order must match known campaign profile labels')
    summarize_campaign(campaign, [])  # Validate before writing or invoking a model.
    output = output.resolve()
    if output == ROOT or ROOT in output.parents:
        raise ValueError('output must be outside the source repository')
    output.mkdir(parents=True, exist_ok=False)
    frozen = output / 'frozen-skill'
    shutil.copytree(ROOT / 'skills/agent-attention', frozen)
    skill_hashes = {p.relative_to(frozen).as_posix(): digest(p)
                    for p in frozen.rglob('*') if p.is_file()}
    protocol = {'protocol_schema': 2, 'case_id': case_id,
                'order': order, 'profiles': profiles, 'campaign': campaign, 'task': case['task'],
                'files': case['files'], 'allowed_edits': case['allowed_edits'],
                'case_sha256': digest(ROOT/'benchmarks/cases'/f'{case_id}.json'),
                'evaluator_sha256': {str(path.relative_to(ROOT).as_posix()): digest(path) for path in
                    [ROOT/'scripts/evaluate_effort.py', ROOT/'scripts/effort_campaign.py',
                     *sorted((ROOT/'scripts/evaluation').glob('*.py'))]},
                'skill_sha256': skill_hashes,
                'oracle': 'CLI completed, protected hashes unchanged, unchanged checks.py passes',
                'model_requested': 'gpt-6.1-sol', 'reasoning_effort': 'medium',
                'disabled_host_skills': list(disabled_skills),
                'isolation': 'NOT_VERIFIED: inspect actual prompt discovery; exclusions alone are not proof'}
    (output / 'protocol.json').write_text(json.dumps(protocol, indent=2), encoding='utf-8')
    results = []
    for number, label in enumerate(order, 1):
        folder = output / f'{number}-{label}'
        folder.mkdir()
        workspace = folder/'workspace'
        workspace.mkdir()
        for name, content in case['files'].items():
            (workspace / name).write_text(content, encoding='utf-8', newline='\n')
        shutil.copytree(frozen, workspace / '.agents/skills/agent-attention')
        # A real baseline makes git diff inspect changes, not compare the two
        # positional paths as unrelated files outside a repository.
        for args in (['init', '--quiet'], ['add', '--', *case['files'], '.agents'],
                     ['-c', 'user.name=Attention Eval', '-c', 'user.email=eval@example.invalid',
                      'commit', '--quiet', '-m', 'fixture baseline']):
            subprocess.run(['git', *args], cwd=workspace, check=True, capture_output=True)
        pins = {p.relative_to(workspace).as_posix(): digest(p)
                for p in workspace.rglob('*') if p.is_file() and '.git' not in p.relative_to(workspace).parts}
        (folder/'input-pins.json').write_text(json.dumps(pins, indent=2), encoding='utf-8')
        prompt = case['task'].format(profile=profiles[label])
        (folder / 'prompt.txt').write_text(prompt, encoding='utf-8')
        command = [cli, 'exec', '--ignore-user-config', '--ephemeral', '--json',
                   '--skip-git-repo-check', '--disable', 'apps', '--disable', 'memories',
                   '--disable', 'plugins', '--disable', 'multi_agent',
                   '-m', 'gpt-6.1-sol', '--approve-for-me',
                   '-c', 'model_reasoning_effort="medium"', '-C', str(workspace), '-']
        if disabled_skills:
            # CLI-local overrides preserve the user's installed skills/settings.
            exclusions = ','.join('{path='+json.dumps(path)+',enabled=false}' for path in disabled_skills)
            command[-1:-1] = ['-c', 'skills.config=['+exclusions+']']
        start = time.monotonic()
        startup_error = None
        try:
            proc = subprocess.run(command, input=prompt, text=True, encoding='utf-8',
                                  capture_output=True, timeout=timeout)
            code, out, err = proc.returncode, proc.stdout, proc.stderr
        except subprocess.TimeoutExpired as exc:
            code, out, err = None, exc.stdout or b'', exc.stderr or b''
            if isinstance(out, bytes): out = out.decode('utf-8', errors='replace')
            if isinstance(err, bytes): err = err.decode('utf-8', errors='replace')
        except OSError as error:
            startup_error = type(error).__name__
            code, out, err = None, '', startup_error+': '+str(error)
        (folder / 'events.jsonl').write_text(out, encoding='utf-8')
        (folder / 'stderr.txt').write_text(err, encoding='utf-8')
        changed = changes(workspace, pins, case['allowed_edits'])
        acceptance_error, oracle_changes = None, []
        try:
            if not changed:
                check, acceptance_error, oracle_changes = check_candidate(workspace, case, folder)
            else:
                check = None
        except (subprocess.TimeoutExpired, OSError) as error:
            check, acceptance_error = None, type(error).__name__
        changed = sorted(set(changed + changes(workspace, pins, case['allowed_edits'])
                             + ['oracle:'+name for name in oracle_changes]))
        acceptance_exit = (check.returncode if check and check.returncode else
                           (1 if acceptance_error or oracle_changes else 0)) if check else None
        events = []
        for line in out.splitlines():
            try:
                event = json.loads(line)
                if isinstance(event, dict) and isinstance(event.get('item', {}), dict):
                    events.append(event)
            except ValueError: pass
        actions = [e['item'] for e in events if e.get('type') == 'item.completed'
                   and e.get('item', {}).get('type') in ('command_execution', 'file_change')]
        usage = next((e.get('usage') for e in events if e.get('type') == 'turn.completed'), None)
        usage_error = None
        try:
            usage = assess_usage(usage)
        except ValueError as error:
            usage, usage_error = None, str(error)
        work_changed = any(not (workspace/name).is_file() or digest(workspace/name) != pins[name]
                           for name in case['allowed_edits'])
        classification = classify_trial(code, events, err, changed, acceptance_exit, work_changed)
        stop_reason = environment_failure(events, err)
        if startup_error:
            stop_reason = 'CLI_STARTUP_ERROR'
            classification = 'BLOCKED_ENVIRONMENT' if not changed and not work_changed else 'FAIL'
        if usage_error:
            classification = 'FAIL'
        result = {'trial': number, 'profile': label,
                  'status': classification, 'usage_error': usage_error, 'acceptance_error': acceptance_error,
                  'environment_failure': stop_reason,
                  'startup_error': startup_error,
                  'exit_code': code, 'elapsed_seconds': round(time.monotonic()-start, 3),
                  'protected_changes': changed, 'acceptance_exit': acceptance_exit,
                  'oracle_process_exit': check.returncode if check else None, 'case_id': case_id,
                  'usage': usage, 'trace_sha256': digest(folder/'events.jsonl'),
                  'actions': [{k: v for k, v in a.items() if k != 'aggregated_output'} for a in actions]}
        (folder/'result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
        results.append(result)
        print(json.dumps({k: v for k, v in result.items() if k != 'actions'}), flush=True)
        (output/'results.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
        (output/'summary.json').write_text(json.dumps(summarize_campaign(campaign, results), indent=2), encoding='utf-8')
        # A quota/capacity failure after actions stays FAIL, but must still stop
        # new calls. Otherwise a partially executed attempt exhausts the plan.
        if stop_reason:
            (output/'not-run.json').write_text(json.dumps(list(order[number:]), indent=2), encoding='utf-8')
            break
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--case', choices=CASE_IDS, default='cents')
    parser.add_argument('--cli', default='codex')
    parser.add_argument('--timeout', default=180, type=int)
    parser.add_argument('--profiles', nargs='+', choices=PROFILES,
                        help='Default six-trial counterbalanced order; override only for explicitly labeled regressions')
    parser.add_argument('--axis', choices=('focus', 'sync', 'batch', 'explore', 'verify'))
    parser.add_argument('--levels', nargs='+', type=int)
    parser.add_argument('--repeats', type=int, default=2)
    parser.add_argument('--plan', action='store_true', help='Preview profiles and maximum model calls without writing or executing')
    parser.add_argument('--disabled-skills-file', type=Path,
                        help='Private JSON list of exact host SKILL.md paths to exclude for this invocation only')
    args = parser.parse_args()
    if args.axis and args.profiles:
        parser.error('--axis and --profiles are different comparison designs')
    if args.levels is not None and not args.axis:
        parser.error('--levels requires --axis')
    try:
        campaign = campaign_plan(args.axis, args.levels or (1,3,5), args.repeats)
    except ValueError as error:
        parser.error(str(error))
    if args.profiles:
        campaign.update(order=args.profiles, planned_trials=len(args.profiles))
    campaign.update(case_id=args.case, case_sha256=digest(ROOT/'benchmarks/cases'/f'{args.case}.json'))
    if args.plan:
        print(json.dumps(campaign, indent=2))
        raise SystemExit(0)
    if args.output is None:
        parser.error('--output is required for model execution; use --plan for a read-only preview')
    disabled_skills = json.loads(args.disabled_skills_file.read_text(encoding='utf-8')) if args.disabled_skills_file else []
    outcomes = run(args.output, args.cli, args.timeout, campaign['order'], campaign, disabled_skills, args.case)
    raise SystemExit(0 if all(row['status'] == 'PASS' for row in outcomes) else 1)
