#!/usr/bin/env python3
"""Resolve a task-wide agent attention profile; emits guidance, never executes work."""
import argparse
import json
import re

SEMANTICS_VERSION = '0.1.1'

AXES = {
    'focus': (
        'One bounded action; retain pointers to relevant dependencies in task context.',
        'One component and its immediate contract.',
        'Use the existing skill task scope; expand context when needed.',
        'Keep the changed component and its direct dependents in view.',
        'Keep the authorized end-to-end flow and cross-component contracts in view.'),
    'sync': (
        'Reconcile at task completion; reconcile earlier if a shared contract changes.',
        'Reconcile after each completed group of related work.',
        'Use the existing skill checkpoints and reconcile at important boundaries.',
        'Reconcile after each change that affects another component.',
        'Reconcile after each step that changes shared state or assumptions.'),
    'batch': (
        'Group straightforward related changes; use one acceptance check without optional intermediate decomposition.',
        'Use a few coherent work items; inspect only consequential intermediate boundaries.',
        'Use the existing skill batch size for a complete bounded work item.',
        'Split related changes at dependency boundaries and inspect each meaningful intermediate result.',
        'Decompose consequential work into explicit reversible steps; inspect each result before the next dependent change.'),
    'explore': (
        'Start from supplied sources; follow required dependencies when discovered.',
        'Inspect the target and immediate references first.',
        'Use the existing skill discovery strategy; expand for concrete unknowns.',
        'Proactively inspect direct dependencies and conflicting assumptions.',
        'Map the relevant authorized flow before selecting the first action.'),
    'verify': (
        'Check the direct result plus all mandatory and risk-triggered checks.',
        'Check the changed area and its immediate contract.',
        'Use the existing skill risk-based verification.',
        'Add nearby regressions and relevant boundary cases.',
        'Add independent checks of consequential assumptions and affected contracts.')}


def parse_attention(value=None):
    levels = dict.fromkeys(AXES, 3)
    if value is None or value == 'balanced':
        return levels
    if not isinstance(value, str) or not value.strip():
        raise ValueError('use balanced or comma-separated axis=1..5 assignments')
    seen = set()
    for assignment in value.split(','):
        parts = assignment.strip().split('=')
        if len(parts) != 2:
            raise ValueError('expected axis=1..5')
        name, level = (part.strip() for part in parts)
        if name not in AXES or name in seen or level not in ('1', '2', '3', '4', '5'):
            raise ValueError('unknown/duplicate axis or invalid level: '+assignment)
        seen.add(name)
        levels[name] = int(level)
    return levels


def inherit(task_levels, override=None):
    """Compose a temporary step profile without mutating the task checkpoint."""
    if (not isinstance(task_levels, dict) or set(task_levels) != set(AXES)
            or any(type(n) is not int or not 1 <= n <= 5 for n in task_levels.values())):
        raise ValueError('task profile must contain all five integer levels')
    result = task_levels.copy()
    if override is None:
        return result
    parsed = parse_attention(override)
    if override == 'balanced':
        return parsed
    for assignment in override.split(','):
        key = assignment.split('=')[0].strip()
        result[key] = parsed[key]
    return result


def resolve(value=None, workflow='direct'):
    if not isinstance(workflow, str) or not re.fullmatch(r'[a-z][a-z0-9-]{0,63}', workflow):
        raise ValueError('workflow must be a simple label, not a command or task')
    levels = parse_attention(value)
    warnings = []
    if levels['focus'] <= 2 and levels['batch'] >= 4:
        warnings.append('Narrow focus with detailed decomposition can lose the shared goal; retain dependency pointers without repeated summaries.')
    if levels['sync'] <= 2 and (levels['focus'] <= 2 or levels['batch'] >= 4):
        warnings.append('Sparse reconciliation can accumulate drift; reconcile immediately on shared-contract changes.')
    if levels['explore'] >= 4 and levels['focus'] <= 2:
        warnings.append('Broad exploration may dominate a narrow task; record findings, then return to the selected action.')
    return {
        'version': 1, 'semantics_version': SEMANTICS_VERSION, 'workflow': workflow, 'levels': levels,
        'mode': 'balanced' if all(n == 3 for n in levels.values()) else 'custom',
        'directives': {name: AXES[name][level-1] for name, level in levels.items() if level != 3},
        'warnings': warnings,
        'invariants': [
            'Preserve permissions, task scope and mandatory/risk-triggered checks.',
            'Never require a minimum iteration count or wait to consume a time budget.',
            'Stop on completion, deadline, missing prerequisites or repeated non-progress.',
            'On shared-contract changes, reconcile before dependent work regardless of sync level.',
            'Retain the profile in task context; explain material deviations without mandatory state writes.',
            'No model reasoning-effort setting, token budget or token savings is implied.'],
        'execution': 'NONE', 'writes': 'NONE'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--attention', default=None)
    parser.add_argument('--workflow', default='direct', help='Descriptive label only; no dispatch')
    args = parser.parse_args(argv)
    try:
        result = resolve(args.attention, args.workflow)
    except ValueError as error:
        parser.exit(2, 'FAIL: '+str(error)+'\n')
    print(json.dumps(result, indent=2, ensure_ascii=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
