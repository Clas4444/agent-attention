#!/usr/bin/env python3
"""Workflow graph contract v1. Design, validate and route; never execute tasks."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat

AXES = ('focus', 'sync', 'batch', 'explore', 'verify')
STATUSES = ('PASS', 'FAIL', 'BLOCKED', 'NOT_RUN')
TERMINALS = ('DONE', 'STOP')


class MissingFacts(ValueError):
    def __init__(self, keys):
        self.keys = keys
        super().__init__('missing condition facts: '+', '.join(keys))


def slug(value):
    if not isinstance(value, str) or not re.fullmatch('[a-z][a-z0-9-]{0,63}', value):
        raise ValueError('IDs and skill names must be lowercase slugs')
    return value


def text(value):
    if not isinstance(value, str) or not value.strip() or len(value) > 2000 or '\n' in value or '\r' in value:
        raise ValueError('expected a nonempty single-line description (max 2000 characters)')


def relative(value):
    if (not isinstance(value, str) or not value or '\\' in value or ':' in value
            or any(c in value for c in '\x00\n\r<>') or value.startswith('/')
            or any(part == '..' or part.casefold() == '.git' for part in value.split('/'))
            or str(PurePosixPath(value)) != value or value == '.'):
        raise ValueError('source/output paths must be normalized project-relative paths')
    for part in value.split('/'):
        if (part.rstrip(' .') != part or any(ord(c) < 32 or c in '"|?*' for c in part)
                or re.fullmatch('(?i:con|prn|aux|nul|com[1-9]|lpt[1-9])', part.split('.')[0])):
            raise ValueError('source/output paths require portable ordinary filenames')
    return value


def profile(value):
    if not isinstance(value, dict) or any(k not in AXES or type(v) is not int or not 1 <= v <= 5 for k, v in value.items()):
        raise ValueError('attention must contain only axis=integer levels 1..5')


def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key: '+key)
        result[key] = value
    return result


def load(path):
    with Path(path).open('rb') as stream: raw = stream.read(1_000_001)
    if len(raw) > 1_000_000:
        raise ValueError('workflow/state input exceeds 1 MB')
    return json.loads(raw.decode('utf-8'), object_pairs_hook=unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError('nonfinite JSON number')))


def condition(value, keys):
    if not isinstance(value, dict) or any(k not in keys or type(v) not in (str, int, bool) for k, v in value.items()):
        raise ValueError('conditions must compare declared fact keys to JSON strings, integers or booleans')


def validate(document, known_skills=None):
    if not isinstance(document, dict) or type(document.get('schema_version')) is not int or document['schema_version'] != 1:
        raise ValueError('expected workflow schema_version 1')
    if set(document)-{'schema_version','id','goal','entry','limits','attention','skill_root',
                      'fact_keys','fact_sources','boundaries','steps'}:
        raise ValueError('unknown workflow fields; correct typos instead of ignoring configuration')
    slug(document.get('id')); text(document.get('goal'))
    limits = document.get('limits', {})
    if not isinstance(limits, dict) or set(limits)-{'max_steps','max_cycles'}:
        raise ValueError('limits accepts max_steps and max_cycles only')
    for key, maximum in (('max_steps', 1000), ('max_cycles', 100)):
        if type(limits.get(key)) is not int or not 1 <= limits[key] <= maximum:
            raise ValueError(key+' must be a positive bounded integer')
    profile(document.get('attention', {}))
    relative(document.get('skill_root', '.agents/skills'))
    keys = document.get('fact_keys')
    if not isinstance(keys, list) or any(not isinstance(k,str) for k in keys) or len(keys) > 32 or len(set(keys)) != len(keys):
        raise ValueError('fact_keys must be a unique list (max 32)')
    for key in keys: slug(key)
    provenance = document.get('fact_sources', {})
    if not isinstance(provenance, dict) or any(key not in keys for key in provenance):
        raise ValueError('fact_sources must describe declared fact keys')
    for value in provenance.values(): text(value)
    boundaries = document.get('boundaries', [])
    if not isinstance(boundaries, list) or len(boundaries) > 10: raise ValueError('invalid boundaries')
    for value in boundaries: text(value)
    steps = document.get('steps')
    if not isinstance(steps, list) or not 1 <= len(steps) <= 64:
        raise ValueError('workflow requires 1..64 steps')
    by_id = {}
    for step in steps:
        if not isinstance(step, dict): raise ValueError('step must be an object')
        if set(step)-{'id','title','sources','acceptance','cycle_end','bindings','transitions'}:
            raise ValueError('unknown step fields')
        name = slug(step.get('id')); text(step.get('title'))
        if name in by_id: raise ValueError('duplicate step ID')
        by_id[name] = step
    if document.get('entry') not in by_id: raise ValueError('entry step is missing')
    cycles = []
    fact_types = {}
    for step in steps:
        sources = step.get('sources')
        if not isinstance(sources, list) or any(not isinstance(p,str) for p in sources) or len(sources) > 5 or len(set(sources)) != len(sources):
            raise ValueError('each step needs 0..5 unique exact source pointers')
        for source in sources: relative(source)
        criteria = step.get('acceptance')
        if not isinstance(criteria, list) or not criteria or len(criteria) > 10:
            raise ValueError('each step needs 1..10 acceptance criteria')
        for criterion in criteria: text(criterion)
        if type(step.get('cycle_end', False)) is not bool: raise ValueError('cycle_end must be boolean')
        if step.get('cycle_end'): cycles.append(step)
        bindings = step.get('bindings')
        if not isinstance(bindings, list) or not 1 <= len(bindings) <= 16:
            raise ValueError('each step needs 1..16 ordered bindings')
        for index, binding in enumerate(bindings):
            if not isinstance(binding, dict): raise ValueError('binding must be an object')
            if set(binding)-{'when','skills','attention'}: raise ValueError('unknown binding fields')
            when = binding.get('when'); condition(when, keys)
            if (not when) != (index == len(bindings)-1):
                raise ValueError('bindings need exactly one unconditional fallback, last')
            skills = binding.get('skills', [])
            if not isinstance(skills, list) or any(not isinstance(s,str) for s in skills) or len(skills) > 10 or len(set(skills)) != len(skills):
                raise ValueError('binding skills must be unique (max 10)')
            for skill in skills:
                slug(skill)
                if known_skills is not None and skill not in known_skills:
                    raise ValueError('unknown/unavailable skill: '+skill)
            profile(binding.get('attention', {}))
        transitions = step.get('transitions')
        if not isinstance(transitions, list) or not 4 <= len(transitions) <= 32:
            raise ValueError('each step needs ordered transitions for all four statuses')
        fallback = set()
        for edge in transitions:
            if not isinstance(edge, dict) or edge.get('status') not in STATUSES:
                raise ValueError('transition status must be PASS/FAIL/BLOCKED/NOT_RUN')
            if set(edge)-{'status','when','next'}: raise ValueError('unknown transition fields')
            status = edge['status']; when = edge.get('when', {}); condition(when, keys)
            if status in fallback: raise ValueError('transition after unconditional fallback is unreachable')
            if not when: fallback.add(status)
            if edge.get('next') not in (*by_id, *TERMINALS): raise ValueError('transition points to an unknown step')
        if fallback != set(STATUSES): raise ValueError('every status needs an unconditional fallback')
        for row in [*bindings, *transitions]:
            for key, value in row.get('when', {}).items():
                if key in fact_types and fact_types[key] is not type(value):
                    raise ValueError('a fact must have one consistent scalar type')
                fact_types[key] = type(value)
    if not cycles or not any(edge['next'] == document['entry'] for step in cycles for edge in step['transitions']):
        raise ValueError('mark a cycle_end step with an explicit return to entry')
    reached = {document['entry']}
    while True:
        expanded = reached | {e['next'] for name in reached for e in by_id[name]['transitions'] if e['next'] in by_id}
        if expanded == reached: break
        reached = expanded
    if reached != set(by_id): raise ValueError('workflow contains unreachable steps')
    return by_id


def fingerprint(document):
    return hashlib.sha256(json.dumps(document, sort_keys=True, ensure_ascii=True, separators=(',', ':')).encode()).hexdigest()


def facts_check(document, facts):
    condition(facts, document['fact_keys'])
    for step in document['steps']:
        for row in [*step['bindings'], *step['transitions']]:
            for key, value in row.get('when', {}).items():
                if key in facts and type(facts[key]) is not type(value):
                    raise ValueError('wrong fact type: '+key)


def choose(rows, facts):
    for row in rows:
        when = row.get('when', {})
        if any(key in facts and facts[key] != value for key, value in when.items()): continue
        missing = [key for key in when if key not in facts]
        if missing: raise MissingFacts(missing)
        return row
    raise ValueError('no matching route')


def start(document, facts=None):
    validate(document)
    if facts is None: facts = {}
    facts_check(document, facts); facts = dict(facts)
    return {'workflow_sha256': fingerprint(document), 'step': document['entry'],
            'steps_completed': 0, 'cycles_completed': 0, 'status': 'ACTIVE', 'facts': facts}


def cursor(document, state):
    steps = validate(document)
    if not isinstance(state, dict) or state.get('workflow_sha256') != fingerprint(document):
        raise ValueError('state belongs to a different or changed workflow')
    if state.get('status') != 'ACTIVE' or state.get('step') not in steps:
        raise ValueError('workflow is finished or cursor is invalid')
    for key, limit in (('steps_completed', 'max_steps'), ('cycles_completed', 'max_cycles')):
        if type(state.get(key)) is not int or not 0 <= state[key] < document['limits'][limit]:
            raise ValueError('cursor is outside its execution budget')
    facts_check(document, state.get('facts'))
    return steps


def select(document, state):
    steps = cursor(document, state)
    binding = choose(steps[state['step']]['bindings'], state['facts'])
    effective = dict.fromkeys(AXES, 3)
    effective.update(document.get('attention', {})); effective.update(binding.get('attention', {}))
    return {'step': state['step'], 'skills': binding.get('skills', []), 'attention': effective,
            'attention_requested': bool(document.get('attention') or binding.get('attention')),
            'instruction_paths': [document.get('skill_root', '.agents/skills')+'/'+name+'/SKILL.md'
                                  for name in binding.get('skills', [])],
            'skill_availability': 'NOT_RUN',
            'goal': document['goal'], 'boundaries': document.get('boundaries', []),
            'sources': steps[state['step']]['sources'], 'acceptance': steps[state['step']]['acceptance'],
            'execution': 'NONE', 'scope': 'Read only listed sources and selected installed instructions; no permissions granted.'}


def advance(document, state, status, evidence, facts=None):
    steps = cursor(document, state)
    if status not in STATUSES: raise ValueError('invalid observed status')
    text(evidence)
    if facts is None: facts = {}
    facts_check(document, facts)
    observed = dict(state['facts']); observed.update(facts); facts_check(document, observed)
    step = steps[state['step']]
    edge = choose([row for row in step['transitions'] if row['status'] == status], observed)
    target = edge['next']; count = state['steps_completed']+1
    cycles = state['cycles_completed']+int(bool(step.get('cycle_end')) and target in (document['entry'], 'DONE'))
    reason = 'ROUTE'
    if target not in TERMINALS:
        if count >= document['limits']['max_steps']: target, reason = 'STOP', 'MAX_STEPS'
        elif cycles >= document['limits']['max_cycles']: target, reason = 'STOP', 'MAX_CYCLES'
    return {'workflow_sha256': fingerprint(document), 'step': target, 'steps_completed': count,
            'cycles_completed': cycles, 'status': target if target in TERMINALS else 'ACTIVE',
            'facts': observed, 'last': {'step': state['step'], 'status': status, 'evidence': evidence, 'reason': reason},
            'execution': 'NONE', 'evidence_scope': 'Caller-supplied observation; routing does not verify task execution.'}


def template(layer='skills'):
    if layer not in ('skills', 'attention', 'both'): raise ValueError('unknown setup layer')
    def binding(when, skill, attention):
        return dict(when=when, **({'skills': [skill]} if layer in ('skills', 'both') else {}),
                    **({'attention': attention} if layer in ('attention', 'both') else {}))
    def edges(passed, failed):
        return [{'status': 'PASS', 'next': passed}, {'status': 'FAIL', 'next': failed},
                {'status': 'BLOCKED', 'next': 'STOP'}, {'status': 'NOT_RUN', 'next': 'STOP'}]
    return {'schema_version': 1, 'id': 'my-workflow', 'goal': 'Complete and verify the user-defined outcome',
            'entry': 'work', 'limits': {'max_cycles': 3, 'max_steps': 20},
            'fact_keys': ['kind', 'risk', 'done'],
            'fact_sources': {'kind':'User task classification', 'risk':'User-confirmed risk assessment',
                             'done':'Observed acceptance checks against the user goal'},
            'boundaries':['Keep external actions within existing user authorization'], 'steps': [
                {'id': 'work', 'title': 'Do one useful work item', 'sources': ['README.md'],
                 'acceptance': ['The requested item is ready for verification'],
                 'bindings': [binding({'kind': 'bug'}, 'loop-debug', {'focus': 2, 'batch': 4}),
                              binding({}, 'loop-code', {'focus': 3})], 'transitions': edges('verify', 'work')},
                {'id': 'verify', 'title': 'Verify criteria and choose next action', 'sources': ['README.md'],
                 'acceptance': ['Required checks ran; gaps and completion are recorded'], 'cycle_end': True,
                 'bindings': [binding({'risk': 'high'}, 'loop-review', {'verify': 5}),
                              binding({}, 'loop-test', {'verify': 3})],
                 'transitions': [{'status': 'PASS', 'when': {'done': True}, 'next': 'DONE'},
                                 *edges('work', 'work')]}]}


def questions(layer):
    return [{'id': key, 'question': question} for key, question in (
        ('outcome', 'What outcome and observable completion criteria should end the loop?'),
        ('steps', 'Which steps are needed, in which order, and which exact files (0–5) should each read?'),
        ('branches', 'For each PASS, FAIL, BLOCKED and NOT_RUN result, what happens next?'),
        ('choices', 'Which conditions choose the '+('skills' if layer == 'skills' else 'skills and attention profiles' if layer == 'both' else 'attention profiles')+' before each step?'),
        ('facts', 'Where will each condition fact come from, and what should happen if it is unknown?'),
        ('cycle', 'Which step completes a cycle and returns to the first step when more work remains?'),
        ('budget', 'What maximum cycles/steps and external-action boundaries apply?'),
        ('location', 'Which project and local-only output directory should hold the graph and agent map?'))]


def attach_attention(document, patch):
    """Attach explicit profiles to existing binding indexes; preserve routing/skills."""
    validate(document)
    if not isinstance(patch, dict) or set(patch)-{'attention', 'steps'}:
        raise ValueError('attention patch accepts only attention and steps')
    updated = copy.deepcopy(document)
    if 'attention' in patch:
        profile(patch['attention']); updated['attention'] = patch['attention'].copy()
    changes = patch.get('steps', {})
    if not isinstance(changes, dict): raise ValueError('step patches must be keyed by step ID')
    steps = {step['id']: step for step in updated['steps']}
    for name, bindings in changes.items():
        if name not in steps or not isinstance(bindings, list): raise ValueError('unknown step or invalid binding patch')
        seen = set()
        for change in bindings:
            if not isinstance(change, dict) or set(change) != {'binding', 'attention'}:
                raise ValueError('binding patch needs binding index and attention only')
            index = change['binding']
            if type(index) is not int or not 0 <= index < len(steps[name]['bindings']) or index in seen:
                raise ValueError('unknown/duplicate binding index')
            seen.add(index); profile(change['attention'])
            steps[name]['bindings'][index]['attention'] = change['attention'].copy()
    validate(updated)
    return updated


def diagram(document):
    validate(document)
    ids = {step['id']: 'step_'+step['id'].replace('-', '_') for step in document['steps']}
    ids.update(DONE='terminal_done', STOP='terminal_stop')
    lines = ['flowchart TD', '  terminal_done(["DONE"])', '  terminal_stop(["STOP"])']
    for step in document['steps']: lines.append('  '+ids[step['id']]+'["'+step['id']+'"]')
    for step in document['steps']:
        for edge in step['transitions']:
            label = edge['status']+(' conditional' if edge.get('when') else ' fallback')
            lines.append('  '+ids[step['id']]+' -->|'+label+'| '+ids[edge['next']])
    return '\n'.join(lines)+'\n'


def agent_map(document, project=None):
    validate(document)
    lines = ['# Local agent route map', '', 'Goal: '+document['goal'], '',
             'Read workflow.json and this map first. Start at `'+document['entry']+'`.',
             'Only load the current step, its selected skill instructions and its exact source pointers.',
             'Do not scan the whole project. Unknown facts require clarification, not a guessed branch.',
             'Bindings and transitions use first matching rule order; fallback is last.',
             'Conditions compare explicit facts; no expression, shell or code evaluation.',
             'Respect permissions and required checks. This map does not grant external-action authority.',
             'Use select before work and advance only after an evidenced outcome. Keep returned state',
             'in existing task context or an explicitly chosen cursor file. Routing does not execute tasks.',
             'Attention overrides last for one step; recompute from the task profile at the next step.',
             'End on DONE, STOP, user stop, deadline, non-progress or budget exhaustion.', '',
             'Limits: '+json.dumps(document['limits'], sort_keys=True)+'.', '',
             'Project root: '+str(project or 'the explicitly selected project')+'.',
             'Fact sources: '+json.dumps(document.get('fact_sources', {}), sort_keys=True)+'.',
             'Boundaries: '+json.dumps(document.get('boundaries', []), ensure_ascii=True)+'.', '',
             'Source pointers are project-relative, not relative to this map directory.', '']
    for step in document['steps']:
        lines += ['## '+step['id'], '', step['title'], '', 'Read first: '+(', '.join('`'+p+'`' for p in step['sources']) or 'supplied task context only'), '',
                  'Acceptance: '+json.dumps(step['acceptance'], ensure_ascii=True), '',
                  'Choose before work:']
        lines += ['- '+json.dumps(row, ensure_ascii=True, sort_keys=True) for row in step['bindings']]
        paths = sorted({document.get('skill_root', '.agents/skills')+'/'+skill+'/SKILL.md'
                        for row in step['bindings'] for skill in row.get('skills', [])})
        lines += ['', 'Candidate instruction paths (read only the selected binding): '+', '.join('`'+p+'`' for p in paths)]
        lines += ['', 'Route after observation:']+['- '+json.dumps(row, ensure_ascii=True, sort_keys=True) for row in step['transitions']]
        lines += ['', 'Cycle end: '+str(step.get('cycle_end', False))+'.', '']
    return '\n'.join(lines)


def plain_entry(path):
    if path.exists() or path.is_symlink():
        meta = path.lstat()
        if stat.S_ISLNK(meta.st_mode) or getattr(meta, 'st_file_attributes', 0)&0x400:
            raise ValueError('output aliases/reparse points are not supported')


def export(document, project, output=None):
    validate(document)
    project = Path(project).resolve()
    if not project.is_dir(): raise ValueError('project root must already exist')
    location = relative(output or '.loop/workflows/'+document['id'])
    destination = project/location
    resolved = destination.resolve()
    if not resolved.is_relative_to(project):
        raise ValueError('output escapes the selected project')
    if any(part.casefold() == '.git' for part in resolved.relative_to(project).parts):
        raise ValueError('output may not write repository metadata')
    current = project
    for part in PurePosixPath(location).parts:
        current = current/part; plain_entry(current)
    destination.mkdir(parents=True, exist_ok=False)
    # Ignore all generated artifacts, including this .gitignore. No existing
    # project config is modified. Exclusive creation never overwrites a design.
    for name, contents in (('.gitignore', '*\n'), ('AGENT-MAP.md', agent_map(document, project)),
                           ('diagram.mmd', diagram(document)),
                           ('workflow.json', json.dumps(document, indent=2, ensure_ascii=False)+'\n')):
        with (destination/name).open('x', encoding='utf-8', newline='\n') as stream: stream.write(contents)
    return {'status': 'PASS', 'directory': str(destination), 'workflow_sha256': fingerprint(document),
            'files': ['workflow.json', 'AGENT-MAP.md', 'diagram.mmd', '.gitignore'],
            'execution': 'NONE', 'privacy': 'Generated directory ignores its contents; force-add can still publish them.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('questions', 'template', 'check', 'export', 'start', 'select', 'advance', 'map', 'attach'))
    parser.add_argument('--layer', choices=('skills', 'attention', 'both'), default='skills')
    parser.add_argument('--file', type=Path); parser.add_argument('--catalog', type=Path)
    parser.add_argument('--project', type=Path); parser.add_argument('--output')
    parser.add_argument('--state', type=Path)
    fact_options = parser.add_mutually_exclusive_group()
    fact_options.add_argument('--facts', help='Explicit JSON fact object')
    fact_options.add_argument('--facts-file', type=Path, help='UTF-8 JSON fact object; avoids shell quoting')
    parser.add_argument('--status', choices=STATUSES); parser.add_argument('--evidence')
    parser.add_argument('--patch', type=Path)
    args = parser.parse_args()
    try:
        if args.command == 'questions': result = questions(args.layer)
        elif args.command == 'template': result = template(args.layer)
        else:
            if args.file is None: raise ValueError('--file is required')
            document = load(args.file)
            known = set(load(args.catalog)['skills']) if args.catalog else None
            validate(document, known)
            facts = load(args.facts_file) if args.facts_file else json.loads(args.facts or '{}', object_pairs_hook=unique)
            if args.command == 'check': result = {'status': 'PASS', 'workflow_sha256': fingerprint(document),
                'steps': len(document['steps']), 'limits': document['limits'], 'execution': 'NONE',
                'registered_skills': 'CHECKED' if args.catalog else 'NOT_RUN', 'installed_skills': 'NOT_RUN'}
            elif args.command == 'attach':
                if args.patch is None: raise ValueError('--patch is required')
                result = attach_attention(document, load(args.patch))
            elif args.command == 'map': print(agent_map(document)); return 0
            elif args.command == 'export':
                if args.project is None: raise ValueError('--project is required')
                result = export(document, args.project, args.output)
            elif args.command == 'start': result = start(document, facts)
            else:
                if args.state is None: raise ValueError('--state is required')
                state = load(args.state)
                if args.command == 'select': result = select(document, state)
                else: result = advance(document, state, args.status, args.evidence, facts)
        print(json.dumps(result, indent=2, ensure_ascii=True)); return 0
    except MissingFacts as error:
        print(json.dumps({'status':'BLOCKED','missing_facts':error.keys,'execution':'NONE'}))
        return 2
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        parser.exit(1, 'FAIL: '+str(error)+'\n')


if __name__ == '__main__':
    raise SystemExit(main())
