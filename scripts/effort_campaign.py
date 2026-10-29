"""Plan controlled attention comparisons and summarize recorded outcomes; no model calls."""
import argparse
import json
from pathlib import Path
import statistics

if __package__:
    from .attention import AXES, parse_attention
else:
    from attention import AXES, parse_attention


def campaign_plan(axis=None, levels=(1, 3, 5), repeats=2):
    if type(repeats) is not int or not 1 <= repeats <= 10:
        raise ValueError('repeats must be 1..10')
    profiles = {}
    if axis is None:
        for label, level in (('low', 1), ('balanced', 3), ('high', 5)):
            profiles[label] = ','.join(f'{name}={level}' for name in AXES)
    else:
        if axis not in AXES:
            raise ValueError('unknown attention axis')
        if (not levels or any(type(n) is not int or not 1 <= n <= 5 for n in levels)
                or len(set(levels)) != len(levels)):
            raise ValueError('levels must be unique integers 1..5')
        for level in levels:
            values = dict.fromkeys(AXES, 3)
            values[axis] = level
            profiles[f'{axis}-{level}'] = ','.join(f'{name}={value}' for name, value in values.items())
    names = list(profiles)
    order = [name for repeat in range(repeats) for name in (names if repeat % 2 == 0 else names[::-1])]
    return {'design': 'single-axis' if axis else 'composite', 'axis': axis,
            'profiles': profiles, 'order': order, 'planned_trials': len(order),
            'other_axes': 'balanced (3)' if axis else 'changed together',
            'model_calls': 'NONE while planning; execution consumes account usage',
            'order_policy': 'alternating forward/reverse; not randomized', 'writes': 'NONE'}


def summarize_campaign(plan, results):
    if (not isinstance(plan, dict) or not isinstance(plan.get('profiles'), dict)
            or not plan['profiles'] or not isinstance(plan.get('order'), (list, tuple))
            or not plan['order'] or any(label not in plan['profiles'] for label in plan['order'])
            or plan.get('design') not in ('single-axis','composite','legacy-composite')
            or plan.get('axis') not in (*AXES, None)):
        raise ValueError('invalid frozen campaign design')
    if not isinstance(results, list) or any(not isinstance(row, dict) for row in results):
        raise ValueError('results must be a list of trial objects')
    for setting in plan['profiles'].values():
        if not isinstance(setting, str):
            raise ValueError('frozen profiles require explicit settings')
        levels = parse_attention(setting)
        if plan['design'] == 'single-axis' and (plan['axis'] is None or
                any(value != 3 for name, value in levels.items() if name != plan['axis'])):
            raise ValueError('single-axis design must keep other axes balanced')
    seen = set()
    for row in results:
        trial = row.get('trial')
        if (type(trial) is not int or trial in seen or not 1 <= trial <= len(plan['order'])
                or row.get('profile') != plan['order'][trial-1]
                or row.get('status') not in ('PASS', 'FAIL', 'BLOCKED_ENVIRONMENT')):
            raise ValueError('result does not match a unique planned trial')
        seen.add(trial)
    groups = {}
    for label, profile in plan['profiles'].items():
        rows = [r for r in results if r['profile'] == label]
        usage = [r['usage'] for r in rows if r.get('usage') is not None]
        for item in usage:
            if (not isinstance(item, dict)
                    or any(type(item.get(k)) is not int or item[k] < 0 for k in
                           ('input_tokens', 'cached_input_tokens', 'output_tokens'))
                    or item['cached_input_tokens'] > item['input_tokens']):
                raise ValueError('invalid usage in recorded result')
        counts = {status: sum(r['status'] == status for r in rows)
                  for status in ('PASS', 'FAIL', 'BLOCKED_ENVIRONMENT')}
        evaluated = counts['PASS'] + counts['FAIL']
        groups[label] = {'levels': parse_attention(profile), 'planned': plan['order'].count(label),
                         'observed': len(rows), 'counts': counts,
                         'not_run': plan['order'].count(label) - len(rows),
                         'success_rate': counts['PASS']/evaluated if evaluated else None,
                         'usage_samples': len(usage), 'usage_missing': len(rows)-len(usage),
                         'tool_command_failures': sum(a.get('type') == 'command_execution' and a.get('exit_code') != 0
                                                      for r in rows for a in r.get('actions', [])),
                         'mean_input_tokens': statistics.mean(u['input_tokens'] for u in usage) if usage else None,
                         'mean_cached_input_tokens': statistics.mean(u['cached_input_tokens'] for u in usage) if usage else None,
                         'mean_uncached_input_tokens': statistics.mean(u['input_tokens']-u['cached_input_tokens'] for u in usage) if usage else None,
                         'mean_output_tokens': statistics.mean(u['output_tokens'] for u in usage) if usage else None,
                         'mean_total_tokens': statistics.mean(u['input_tokens']+u['output_tokens'] for u in usage) if usage else None}
    return {'design': plan['design'], 'axis': plan['axis'], 'planned_trials': len(plan['order']),
            'recorded_trials': len(results), 'not_run': len(plan['order'])-len(results),
            'groups': groups, 'status': 'MEASURED' if results else 'NOT_RUN',
            'limits': ['Means include failed attempts with available usage; missing usage is not zero.',
                       'Cached input is a subset of input, not an extra token quantity.',
                       'Single-axis control on this task is not proof of general causal effects or cost savings.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--axis', choices=AXES)
    parser.add_argument('--levels', nargs='+', type=int)
    parser.add_argument('--repeats', type=int, default=2)
    parser.add_argument('--report', type=Path, help='Existing campaign directory; summarize protocol/results without model calls or writes')
    args = parser.parse_args()
    if args.report and (args.axis or args.levels is not None or args.repeats != 2):
        parser.error('--report reads the frozen design; do not override it')
    if args.levels is not None and not args.axis:
        parser.error('--levels requires --axis')
    try:
        if args.report:
            protocol = json.loads((args.report/'protocol.json').read_text(encoding='utf-8'))
            if not isinstance(protocol, dict):
                raise ValueError('protocol must be an object')
            plan = protocol.get('campaign') or {'design':'legacy-composite','axis':None,
                                               'profiles':protocol['profiles'],'order':protocol['order']}
            results = json.loads((args.report/'results.json').read_text(encoding='utf-8'))
            result = summarize_campaign(plan, results)
        else:
            result = campaign_plan(args.axis, args.levels or (1,3,5), args.repeats)
        print(json.dumps(result, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, 'FAIL: '+str(error)+'\n')


if __name__ == '__main__':
    raise SystemExit(main())
