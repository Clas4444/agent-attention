"""Bounded multi-case orchestration; never pool heterogeneous task means."""
import argparse
import json
from pathlib import Path

from .cases import CASE_IDS, ROOT, load_case
from .runner import campaign_plan, digest, run, summarize_campaign


def plan_suite(case_ids=('ledger', 'dependencies', 'cents'), repeats=2):
    if not case_ids or len(set(case_ids)) != len(case_ids):
        raise ValueError('select distinct benchmark cases')
    plans = {}
    for case_id in case_ids:
        case = load_case(case_id)
        plans[case_id] = dict(campaign_plan(repeats=repeats), case_id=case_id,
                             case_sha256=digest(ROOT/'benchmarks/cases'/f'{case_id}.json'),
                             description=case['description'])
    return {'suite_schema': 1, 'case_order': list(case_ids), 'campaigns': plans,
            'planned_trials': sum(p['planned_trials'] for p in plans.values()),
            'stop_policy': 'Stop the entire suite on environment/prerequisite failure; never retry or replace a trial.',
            'model_calls': 'NONE during planning; execution consumes account usage',
            'aggregation': 'Per case only; do not pool different task means.'}


def run_suite(output, cli='codex', timeout=180,
              case_ids=('ledger', 'dependencies', 'cents'), repeats=2, disabled_skills=()):
    plan = plan_suite(case_ids, repeats)
    output = Path(output).resolve()
    if output == ROOT or ROOT in output.parents:
        raise ValueError('output must be outside the source repository')
    output.mkdir(parents=True, exist_ok=False)
    sources = [ROOT/'scripts/evaluate_effort.py', ROOT/'scripts/evaluate_suite.py',
               ROOT/'scripts/effort_campaign.py', *sorted((ROOT/'scripts/evaluation').glob('*.py')),
               *(ROOT/'benchmarks/cases'/f'{name}.json' for name in case_ids),
               *(p for p in (ROOT/'skills/agent-attention').rglob('*') if p.is_file())]
    pins = {p.relative_to(ROOT).as_posix(): digest(p) for p in sources}
    (output/'protocol.json').write_text(json.dumps(dict(plan, source_sha256=pins), indent=2)+'\n', encoding='utf-8')
    case_results, stopped = {}, None
    for case_id in case_ids:
        if any(not (ROOT/name).is_file() or digest(ROOT/name) != value for name, value in pins.items()):
            stopped = 'SOURCE_DRIFT'
            break
        campaign = plan['campaigns'][case_id]
        rows = run(output/case_id, cli, timeout, campaign['order'], campaign, disabled_skills, case_id)
        case_results[case_id] = rows
        if any(row.get('environment_failure') or row['status'] == 'BLOCKED_ENVIRONMENT' for row in rows):
            stopped = next((row.get('environment_failure') for row in rows if row.get('environment_failure')), 'BLOCKED_ENVIRONMENT')
            break
    remaining = [{'case_id': case_id, 'trial': number, 'profile': profile}
                 for case_id in case_ids
                 for number, profile in enumerate(plan['campaigns'][case_id]['order'], 1)
                 if number > len(case_results.get(case_id, []))]
    summaries = {case_id: summarize_campaign(plan['campaigns'][case_id], case_results.get(case_id, []))
                 for case_id in case_ids}
    result = {'suite_schema': 1, 'planned_trials': plan['planned_trials'],
              'recorded_trials': sum(len(rows) for rows in case_results.values()),
              'stop_reason': stopped, 'not_run': remaining, 'cases': summaries}
    (output/'results.json').write_text(json.dumps(case_results, indent=2)+'\n', encoding='utf-8')
    (output/'summary.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cases', choices=CASE_IDS, nargs='+', default=['ledger', 'dependencies', 'cents'])
    parser.add_argument('--repeats', type=int, default=2)
    parser.add_argument('--timeout', type=int, default=180)
    parser.add_argument('--cli', default='codex')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--disabled-skills-file', type=Path)
    parser.add_argument('--plan', action='store_true')
    args = parser.parse_args()
    try:
        plan = plan_suite(args.cases, args.repeats)
        if args.plan:
            print(json.dumps(plan, indent=2)); return 0
        if args.output is None:
            raise ValueError('--output is required; --plan makes no calls or writes')
        exclusions = json.loads(args.disabled_skills_file.read_text(encoding='utf-8')) if args.disabled_skills_file else []
        result = run_suite(args.output, args.cli, args.timeout, args.cases, args.repeats, exclusions)
        print(json.dumps(result, indent=2))
        complete = not result['not_run'] and not result['stop_reason']
        passing = all(group['counts']['FAIL'] == 0 and group['counts']['BLOCKED_ENVIRONMENT'] == 0
                      for report in result['cases'].values() for group in report['groups'].values())
        return 0 if complete and passing else 1
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, 'FAIL: '+str(error)+'\n')
