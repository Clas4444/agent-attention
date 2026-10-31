"""Independent attention setup: no companion checkout or graph is needed."""
import copy
import json
import itertools
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from scripts.attention_setup import agent_map, export, load, MissingFacts, questions, select, template, validate

ROOT = Path(__file__).resolve().parents[1]


class AttentionSetupTests(unittest.TestCase):
    def test_all_3125_base_combinations_restore_after_conflicting_contexts(self):
        axes = ('focus', 'sync', 'batch', 'explore', 'verify')
        for values in itertools.product(range(1, 6), repeat=5):
            base = dict(zip(axes, values))
            plan = template(); plan['base'] = base
            plan['rules'].append({'id': 'editing', 'when': {'risk': 'edit'},
                                  'levels': {'batch': 1, 'explore': 2}, 'reason': 'Bounded edit'})
            frozen = copy.deepcopy(plan)
            for risk, override in [('high', {'verify': 5, 'sync': 4}),
                                   ('edit', {'batch': 1, 'explore': 2}), ('ordinary', {})]:
                self.assertEqual(select(plan, {'risk': risk})['levels'], dict(base, **override))
            self.assertEqual(plan, frozen)

    def test_exported_map_is_self_contained_at_every_level_and_context(self):
        from scripts.attention import AXES
        for level in range(1, 6):
            plan = template()
            plan['base'] = dict.fromkeys(AXES, level)
            mapped = agent_map(plan, Path('fixture'))
            for axis in AXES:
                self.assertIn(AXES[axis][level - 1], mapped)
            selected = select(plan, {'risk': 'high'})
            for axis, value in selected['levels'].items():
                self.assertIn(AXES[axis][value - 1], mapped)
            for invariant in selected['invariants']:
                self.assertIn(invariant, mapped)
            self.assertIn('Semantics: 0.1.1', mapped)

    def test_base_only_plan_needs_no_rules_facts_graph_or_skill(self):
        plan = template(); plan['rules'] = []; plan['fact_sources'] = {}; plan['base'] = {'focus': 2}
        result = select(plan)
        self.assertEqual(result['levels'], dict(focus=2, sync=3, batch=3, explore=3, verify=3))
        self.assertIsNone(result['selected_rule'])
        self.assertEqual(result['routing'], 'NONE')
        self.assertEqual(result['execution'], 'NONE')
        self.assertNotIn('skills', result)
        self.assertNotIn('steps', plan)
        self.assertEqual(len(questions()), 6)

    def test_context_override_inherits_and_restores_without_mutation(self):
        plan = template(); plan['base'] = {'focus': 2}
        original = copy.deepcopy(plan)
        high = select(plan, {'risk': 'high'})
        ordinary = select(plan, {'risk': 'ordinary'})
        self.assertEqual(high['levels']['focus'], 2)
        self.assertEqual(high['levels']['verify'], 5)
        self.assertEqual(ordinary['levels']['verify'], 3)
        self.assertEqual(ordinary['levels']['sync'], 3)
        self.assertEqual(plan, original)
        self.assertIn('verify', high['directives'])
        self.assertTrue(high['invariants'])

    def test_missing_and_mistyped_facts_do_not_guess_base(self):
        with self.assertRaises(MissingFacts): select(template())
        for facts in ({'risk': True}, {'unknown': 'high'}, []):
            with self.assertRaises(ValueError): select(template(), facts)

    def test_priority_and_known_false_condition(self):
        plan = template(); plan['fact_sources']['phase'] = 'Current observed phase'
        plan['rules'][0]['when']['phase'] = 'review'
        plan['rules'].append({'id': 'later', 'when': {'risk': 'ordinary'},
                              'levels': {'focus': 1}, 'reason': 'Focus one action'})
        self.assertEqual(select(plan, {'risk': 'ordinary'})['selected_rule'], 'later')
        with self.assertRaises(MissingFacts): select(plan, {'risk': 'high'})

    def test_reject_graph_fields_invalid_levels_and_ambiguous_rules(self):
        for patch in ({'steps': []}, {'base': {'verify': True}}, {'base': {'verify': 6}},
                      {'base': {'unknown': 2}}, {'restore': 'never'}, {'attention_schema': True}):
            plan = template(); plan.update(patch)
            with self.assertRaises(ValueError): validate(plan)
        plan = template(); plan['rules'].append(copy.deepcopy(plan['rules'][0]))
        with self.assertRaises(ValueError): validate(plan)
        plan = template(); plan['rules'][0]['when'] = {}
        with self.assertRaises(ValueError): validate(plan)

    def test_private_attention_export_has_no_workflow_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            subprocess.run(['git', 'init', '-q', directory], check=True)
            target = Path(export(template(), directory)['directory'])
            self.assertEqual(set(p.name for p in target.iterdir()), {'attention.json', 'ATTENTION-MAP.md', '.gitignore'})
            mapped = (target/'ATTENTION-MAP.md').read_text(encoding='utf-8')
            self.assertIn('Condition provenance', mapped)
            self.assertIn('no task order, cycle or status routes', mapped)
            ignored = subprocess.run(['git', 'check-ignore', str(target/'attention.json')], cwd=directory,
                                     capture_output=True, text=True)
            self.assertEqual(ignored.returncode, 0, ignored.stderr)
            with self.assertRaises(FileExistsError): export(template(), directory)

    def test_export_rejects_escape_and_portable_aliases_before_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            for output in ('../escape', '.git/plan', '.GiT/plan', 'bad./plan', 'NUL/a', 'C:/outside'):
                with self.assertRaises(ValueError): export(template(), directory, output)
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_export_rejects_symlink(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
            link = Path(directory)/'alias'
            try: link.symlink_to(outside, target_is_directory=True)
            except OSError: self.skipTest('directory symlink creation is unavailable')
            with self.assertRaises(ValueError): export(template(), directory, 'alias/plan')
            self.assertEqual(list(Path(outside).iterdir()), [])

    def test_json_duplicate_and_oversized_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'bad.json'
            for data in ('{"base":{},"base":{}}', '{"x":NaN}', ' '*1_000_001):
                path.write_text(data, encoding='utf-8')
                with self.assertRaises(ValueError): load(path)

    def test_installed_attention_helper_works_without_any_graph_helper(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory); installed = base/'only-attention'
            shutil.copytree(ROOT/'skills/agent-attention', installed)
            # Deliberately omit the entire optional graph bridge from this fixture.
            (installed/'scripts/workflow_setup.py').unlink()
            (installed/'assets/workflow-example.json').unlink()
            helper = str(installed/'scripts/attention_setup.py')
            draft = base/'attention.json'; draft.write_text(json.dumps(template()), encoding='utf-8')
            facts = base/'facts.json'; facts.write_text('{"risk":"high"}', encoding='utf-8')
            for command in ('questions', 'template', 'check', 'select', 'export'):
                args = [sys.executable, '-I', '-B', helper, command]
                if command not in ('questions', 'template'): args += ['--file', str(draft)]
                if command == 'select': args += ['--facts-file', str(facts)]
                if command == 'export': args += ['--project', str(base)]
                result = subprocess.run(args, cwd=base, capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, 0, result.stderr)
                json.loads(result.stdout)
            blocked = subprocess.run([sys.executable, '-I', '-B', helper, 'select', '--file', str(draft)],
                                     cwd=base, capture_output=True, text=True, timeout=10)
            self.assertEqual(blocked.returncode, 2)
            self.assertEqual(json.loads(blocked.stdout)['status'], 'BLOCKED')
            self.assertFalse((base/'.loop').exists())

    def test_generated_reference_and_picture_are_attention_specific(self):
        from scripts.generators.setup import check, REFERENCE, picture
        self.assertEqual(check(ROOT), [])
        self.assertIn('No agent-workflows installation', REFERENCE)
        self.assertIn('ATTENTION SETUP', picture())
        self.assertNotIn('Repo 1', picture())
        self.assertNotIn('Repo 2', picture())
        self.assertIn('attention_setup.py', (ROOT/'skills/agent-attention/SKILL.md').read_text(encoding='utf-8'))


    def test_direct_setup_skill_is_a_complete_isolated_entrypoint(self):
        folder = ROOT/'skills/attention-setup'
        entry = (folder/'SKILL.md').read_text(encoding='utf-8')
        self.assertTrue(entry.startswith('---\nname: attention-setup\n'))
        self.assertIn('description:', entry.split('---', 2)[1])
        metadata = (folder/'agents/openai.yaml').read_text(encoding='utf-8')
        self.assertIn('$attention-setup', metadata)
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            installed = base/'attention-setup'
            shutil.copytree(folder, installed)
            self.assertFalse((installed/'scripts/workflow_setup.py').exists())
            facts = base/'facts.json'; facts.write_text('{"risk":"high"}',encoding='utf-8')
            helper = str(installed/'scripts/attention_setup.py')
            for command in ('questions','template','check','select','export'):
                args = [sys.executable,'-I','-B',helper,command]
                if command not in ('questions','template'):
                    args += ['--file',str(installed/'assets/attention-example.json')]
                if command=='select': args += ['--facts-file',str(facts)]
                if command=='export': args += ['--project',str(base)]
                result = subprocess.run(args,cwd=directory,capture_output=True,text=True,timeout=10)
                self.assertEqual(result.returncode,0,result.stderr)
                payload = json.loads(result.stdout)
                if command=='select': self.assertEqual(payload['levels']['verify'],5)
                if command in ('check','export'): self.assertEqual(payload['status'],'PASS')
            self.assertTrue((base/'.attention/plans/my-attention/ATTENTION-MAP.md').is_file())
