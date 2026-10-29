#!/usr/bin/env python3
"""Design/select an independent attention plan. No workflow graph or scheduler."""
import argparse
import importlib.util
import json
from pathlib import Path, PurePosixPath
import re
import stat

_spec = importlib.util.spec_from_file_location('attention_core', Path(__file__).with_name('attention.py'))
attention = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(attention)


class MissingFacts(ValueError):
    def __init__(self, keys):
        self.keys = keys
        super().__init__('missing condition facts: '+', '.join(keys))


def text(value):
    if not isinstance(value, str) or not value.strip() or len(value) > 2000 or any(ord(c) < 32 for c in value):
        raise ValueError('expected a nonempty single-line description, max 2000 characters')


def slug(value):
    if not isinstance(value, str) or not re.fullmatch('[a-z][a-z0-9-]{0,63}', value):
        raise ValueError('expected a lowercase label')


def levels(value):
    if not isinstance(value, dict) or any(k not in attention.AXES or type(v) is not int or not 1 <= v <= 5 for k, v in value.items()):
        raise ValueError('levels must contain only known axes and integer levels 1..5')


def relative(value):
    if (not isinstance(value, str) or not value or value == '.' or value.startswith('/')
            or '\\' in value or ':' in value or str(PurePosixPath(value)) != value):
        raise ValueError('expected a normalized project-relative path')
    for part in value.split('/'):
        if (part == '..' or part.casefold() == '.git' or part.rstrip(' .') != part
                or any(ord(c) < 32 or c in '<>"|?*' for c in part)
                or re.fullmatch('(?i:con|prn|aux|nul|com[1-9]|lpt[1-9])', part.split('.')[0])):
            raise ValueError('expected a portable ordinary path')
    return value


def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result: raise ValueError('duplicate JSON key: '+key)
        result[key] = value
    return result


def load(path):
    with Path(path).open('rb') as stream: raw = stream.read(1_000_001)
    if len(raw) > 1_000_000: raise ValueError('input exceeds 1 MB')
    return json.loads(raw.decode('utf-8'), object_pairs_hook=unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError('nonfinite number')))


def validate(plan):
    required = {'attention_schema', 'id', 'scope', 'base', 'fact_sources', 'rules', 'sources', 'restore'}
    if not isinstance(plan, dict) or set(plan) != required or type(plan.get('attention_schema')) is not int or plan['attention_schema'] != 1:
        raise ValueError('expected attention_schema 1 and attention-plan fields only; no workflow steps/routes')
    slug(plan['id']); text(plan['scope']); levels(plan['base'])
    if plan['restore'] != 'base-after-context': raise ValueError('restore must be base-after-context')
    sources = plan['sources']
    if not isinstance(sources, list) or len(sources) > 5: raise ValueError('sources must list 0..5 exact paths')
    for source in sources: relative(source)
    if len(set(sources)) != len(sources): raise ValueError('duplicate source')
    facts = plan['fact_sources']
    if not isinstance(facts, dict) or len(facts) > 32: raise ValueError('invalid fact_sources')
    for key, value in facts.items(): slug(key); text(value)
    rules = plan['rules']
    if not isinstance(rules, list) or len(rules) > 16: raise ValueError('rules must list at most 16 attention contexts')
    names, types = set(), {}
    for rule in rules:
        if not isinstance(rule, dict) or set(rule) != {'id', 'when', 'levels', 'reason'}:
            raise ValueError('attention rules accept id, when, levels and reason only')
        slug(rule['id']); text(rule['reason']); levels(rule['levels'])
        if rule['id'] in names: raise ValueError('duplicate rule ID')
        names.add(rule['id'])
        when = rule['when']
        if not isinstance(when, dict) or not when: raise ValueError('rule conditions must be nonempty; base is the fallback')
        for key, value in when.items():
            if key not in facts or type(value) not in (str, int, bool): raise ValueError('conditions require declared typed scalar facts')
            if key in types and types[key] is not type(value): raise ValueError('inconsistent fact type')
            types[key] = type(value)
    return types


def select(plan, facts=None):
    types = validate(plan)
    if facts is None: facts = {}
    if not isinstance(facts, dict): raise ValueError('facts must be an object')
    for key, value in facts.items():
        if key not in plan['fact_sources'] or type(value) not in (str, int, bool): raise ValueError('unknown fact or invalid scalar')
        if key in types and type(value) is not types[key]: raise ValueError('wrong fact type: '+key)
    selected = None
    for rule in plan['rules']:
        if any(k in facts and facts[k] != v for k, v in rule['when'].items()): continue
        missing = [k for k in rule['when'] if k not in facts]
        if missing: raise MissingFacts(missing)
        selected = rule
        break
    effective = dict.fromkeys(attention.AXES, 3)
    effective.update(plan['base'])
    if selected: effective.update(selected['levels'])
    result = attention.resolve(','.join(f'{k}={v}' for k, v in effective.items()))
    result.update(plan_id=plan['id'], selected_rule=selected['id'] if selected else None,
                  scope=plan['scope'], sources=plan['sources'], restore=plan['restore'],
                  routing='NONE', notice='Apply to the existing task; no steps, skills or routes are created.')
    return result


def template():
    return {'attention_schema': 1, 'id': 'my-attention',
            'scope': 'Current authorized task; replace with the actual task and attention tradeoffs',
            'base': {}, 'fact_sources': {'risk': 'Observed task risk confirmed during setup'},
            'rules': [{'id': 'high-risk', 'when': {'risk': 'high'}, 'levels': {'verify': 5, 'sync': 4},
                       'reason': 'Check consequential assumptions and reconcile dependent work'}],
            'sources': [], 'restore': 'base-after-context'}


def questions():
    return ['Which task and session should this attention plan cover?',
            'What tradeoff matters: lower discretionary effort, balanced work, or more coverage?',
            'Which of focus, sync, batch, explore and verify need explicit levels (1..5)?',
            'Which observed conditions or existing phases temporarily change those levels, and why?',
            'Where do condition facts and exact source pointers come from? Unknown facts must be clarified.',
            'When does each context end and restore the base; should the plan stay in context or be saved locally?']


def agent_map(plan, project):
    validate(plan)
    lines = ['# Local attention map', '', 'Project: '+str(project), 'Scope: '+plan['scope'], '',
             'Read attention.json and the selected attention guidance only.',
             'Use the existing task/skills. This plan supplies no task order, cycle or status routes.',
             'Recompute from base for each context; do not carry the last override forward.',
             'First matching rule wins; missing relevant facts block selection, not a guessed base.',
             'Keep required checks and permissions. This map is configuration, not execution evidence.', '',
             'Base: '+json.dumps(plan['base'], sort_keys=True), 'Restore: '+plan['restore'], '', '## Exact sources']
    lines += ['- '+source for source in plan['sources']]
    lines += ['', '## Condition provenance']+['- '+k+': '+v for k, v in plan['fact_sources'].items()]
    lines += ['', '## Ordered attention contexts']
    for rule in plan['rules']:
        lines += ['- '+rule['id']+': '+json.dumps(rule['when'], sort_keys=True)+' → '+json.dumps(rule['levels'], sort_keys=True),
                  '  Reason: '+rule['reason']]
    return '\n'.join(lines)+'\n'


def export(plan, project, output=None):
    validate(plan)
    project = Path(project).resolve()
    if not project.is_dir(): raise ValueError('project root must exist')
    location = relative(output or '.attention/plans/'+plan['id'])
    destination = project/location
    resolved = destination.resolve()
    if not resolved.is_relative_to(project) or any(p.casefold() == '.git' for p in resolved.relative_to(project).parts):
        raise ValueError('output escapes project or writes repository metadata')
    current = project
    for part in location.split('/'):
        current /= part
        if current.exists() or current.is_symlink():
            meta = current.lstat()
            if stat.S_ISLNK(meta.st_mode) or getattr(meta, 'st_file_attributes', 0) & 0x400:
                raise ValueError('output aliases/reparse points are not supported')
    destination.mkdir(parents=True, exist_ok=False)
    for name, contents in (('.gitignore', '*\n'), ('attention.json', json.dumps(plan, indent=2)+'\n'),
                           ('ATTENTION-MAP.md', agent_map(plan, project))):
        with (destination/name).open('x', encoding='utf-8', newline='\n') as stream: stream.write(contents)
    return {'status': 'PASS', 'directory': str(destination), 'execution': 'NONE', 'routing': 'NONE',
            'privacy': 'Ignored by default; force-add/manual sharing can still publish files.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('questions', 'template', 'check', 'select', 'map', 'export'))
    parser.add_argument('--file', type=Path)
    parser.add_argument('--facts-file', type=Path)
    parser.add_argument('--project', type=Path)
    parser.add_argument('--output')
    args = parser.parse_args()
    try:
        if args.command == 'questions': result = questions()
        elif args.command == 'template': result = template()
        else:
            if args.file is None: raise ValueError('--file is required')
            plan = load(args.file); validate(plan)
            if args.command == 'check': result = {'status': 'PASS', 'attention_schema': 1, 'execution': 'NONE', 'routing': 'NONE'}
            elif args.command == 'select': result = select(plan, load(args.facts_file) if args.facts_file else {})
            elif args.command == 'map':
                if args.project is None: raise ValueError('--project is required')
                print(agent_map(plan, args.project)); return 0
            else:
                if args.project is None: raise ValueError('--project is required')
                result = export(plan, args.project, args.output)
        print(json.dumps(result, indent=2)); return 0
    except MissingFacts as error:
        print(json.dumps({'status': 'BLOCKED', 'missing_facts': error.keys, 'execution': 'NONE'})); return 2
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        parser.exit(1, 'FAIL: '+str(error)+'\n')


if __name__ == '__main__':
    raise SystemExit(main())
