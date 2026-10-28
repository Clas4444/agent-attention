"""Run six real-Codex smoke trials. Requires explicit local CLI access; never run in CI.

Output must be a new directory outside this repository. Records private raw traces
there. All model invocations are billable/consume host usage; inspect before use.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
FILES = {
    'discount.py': 'def discount(cents):\n    return cents * 0.9\n',
    'shipping.py': 'def shipping(cents):\n    return 500 if cents < 5000 else 0\n',
    'checkout.py': 'from discount import discount\nfrom shipping import shipping\ndef total(cents):\n    return discount(cents) + shipping(cents)\n',
    'FLOW.md': 'Nonnegative integer cents. discount returns integer cents after 10 percent off, rounded down. Shipping is free from 5000 cents AFTER discount. checkout combines both. No other callers.\n',
    'checks.py': "from discount import discount\nfrom shipping import shipping\nfrom checkout import total\nassert discount(101) == 90 and type(discount(101)) is int\nassert discount(10**18 + 1) == (10**18 + 1) * 9 // 10\nassert shipping(5000) == 0 and shipping(4999) == 500\nassert total(5500) == 5450 and total(6000) == 5400\nassert total(5555) == 5499 and total(5556) == 5000\nprint('PASS')\n",
    'AGENTS.md': 'Isolated evaluation fixture. Only edit discount.py and checkout.py. FLOW.md describes the relevant flow. Run python checks.py; do not edit checks.py, shipping.py, FLOW.md or installed skill. No network, other repositories, global skills or extra agents.\n',
}
TASK = ('Use the installed .agents/skills/agent-attention/SKILL.md explicitly with '
        '{profile} for this task. Fix discount.py to return integer cents rounded '
        'down; fix checkout.py so free shipping uses the discounted amount. '
        'Preserve the shipping API. Only edit discount.py and checkout.py. '
        'Run python checks.py. Apply the profile to your working decisions. '
        'Stop when complete; keep the final response concise.')
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
    fields = ('input_tokens', 'cached_input_tokens', 'output_tokens')
    if any(type(usage.get(k)) is not int or usage[k] < 0 for k in fields):
        raise ValueError('invalid usage')
    if usage['cached_input_tokens'] > usage['input_tokens']:
        raise ValueError('cached input exceeds total')
    return dict(usage, uncached_input_tokens=usage['input_tokens'] - usage['cached_input_tokens'],
                total_tokens=usage['input_tokens'] + usage['output_tokens'])


def run(output, cli, timeout, order=ORDER):
    output = output.resolve()
    if output == ROOT or ROOT in output.parents:
        raise ValueError('output must be outside the source repository')
    output.mkdir(parents=True, exist_ok=False)
    frozen = output / 'frozen-skill'
    shutil.copytree(ROOT / 'skills/agent-attention', frozen)
    skill_hashes = {p.relative_to(frozen).as_posix(): digest(p)
                    for p in frozen.rglob('*') if p.is_file()}
    protocol = {'order': order, 'profiles': PROFILES, 'task': TASK,
                'files': FILES, 'skill_sha256': skill_hashes,
                'oracle': 'CLI completed, protected hashes unchanged, unchanged checks.py passes',
                'model_requested': 'gpt-6.1-sol', 'reasoning_effort': 'medium'}
    (output / 'protocol.json').write_text(json.dumps(protocol, indent=2), encoding='utf-8')
    results = []
    for number, label in enumerate(order, 1):
        folder = output / f'{number}-{label}'
        folder.mkdir()
        for name, content in FILES.items():
            (folder / name).write_text(content, encoding='utf-8')
        shutil.copytree(frozen, folder / '.agents/skills/agent-attention')
        # A real baseline makes git diff inspect changes, not compare the two
        # positional paths as unrelated files outside a repository.
        for args in (['init', '--quiet'], ['add', 'discount.py', 'checkout.py', 'shipping.py',
                     'checks.py', 'FLOW.md', 'AGENTS.md', '.agents'],
                     ['-c', 'user.name=Attention Eval', '-c', 'user.email=eval@example.invalid',
                      'commit', '--quiet', '-m', 'fixture baseline']):
            subprocess.run(['git', *args], cwd=folder, check=True, capture_output=True)
        pins = {p.relative_to(folder).as_posix(): digest(p)
                for p in folder.rglob('*') if p.is_file() and '.git' not in p.relative_to(folder).parts}
        (folder/'input-pins.json').write_text(json.dumps(pins, indent=2), encoding='utf-8')
        prompt = TASK.format(profile=PROFILES[label])
        (folder / 'prompt.txt').write_text(prompt, encoding='utf-8')
        command = [cli, 'exec', '--ignore-user-config', '--ephemeral', '--json',
                   '--skip-git-repo-check', '--disable', 'apps', '--disable', 'memories',
                   '-m', 'gpt-6.1-sol', '--approve-for-me',
                   '-c', 'model_reasoning_effort="medium"', '-C', str(folder), '-']
        start = time.monotonic()
        try:
            proc = subprocess.run(command, input=prompt, text=True, encoding='utf-8',
                                  capture_output=True, timeout=timeout)
            code, out, err = proc.returncode, proc.stdout, proc.stderr
        except subprocess.TimeoutExpired as exc:
            code, out, err = None, exc.stdout or b'', exc.stderr or b''
            if isinstance(out, bytes): out = out.decode('utf-8', errors='replace')
            if isinstance(err, bytes): err = err.decode('utf-8', errors='replace')
        (folder / 'events.jsonl').write_text(out, encoding='utf-8')
        (folder / 'stderr.txt').write_text(err, encoding='utf-8')
        protected = [name for name in pins if name not in ('discount.py', 'checkout.py')]
        changed = [name for name in protected if not (folder/name).is_file()
                   or digest(folder/name) != pins[name]]
        check = subprocess.run([sys.executable, '-B', 'checks.py'], cwd=folder,
                               capture_output=True, text=True, timeout=15) if not changed else None
        events = []
        for line in out.splitlines():
            try: events.append(json.loads(line))
            except ValueError: pass
        actions = [e['item'] for e in events if e.get('type') == 'item.completed'
                   and e.get('item', {}).get('type') in ('command_execution', 'file_change')]
        usage = next((e.get('usage') for e in events if e.get('type') == 'turn.completed'), None)
        result = {'trial': number, 'profile': label,
                  'status': 'PASS' if code == 0 and not changed and check and check.returncode == 0 else 'FAIL',
                  'exit_code': code, 'elapsed_seconds': round(time.monotonic()-start, 3),
                  'protected_changes': changed, 'acceptance_exit': check.returncode if check else None,
                  'usage': assess_usage(usage), 'trace_sha256': digest(folder/'events.jsonl'),
                  'actions': [{k: v for k, v in a.items() if k != 'aggregated_output'} for a in actions]}
        (folder/'result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
        results.append(result)
        print(json.dumps({k: v for k, v in result.items() if k != 'actions'}), flush=True)
        (output/'results.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--cli', default='codex')
    parser.add_argument('--timeout', default=180, type=int)
    parser.add_argument('--profiles', nargs='+', choices=PROFILES, default=ORDER,
                        help='Default six-trial counterbalanced order; override only for explicitly labeled regressions')
    args = parser.parse_args()
    outcomes = run(args.output, args.cli, args.timeout, args.profiles)
    raise SystemExit(0 if all(row['status'] == 'PASS' for row in outcomes) else 1)
