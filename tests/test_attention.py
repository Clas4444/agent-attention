import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from scripts.attention import AXES, parse_attention, resolve, inherit
from scripts.attention_assets import check

ROOT = Path(__file__).resolve().parents[1]


class AttentionTests(unittest.TestCase):
    def test_default_and_balanced_add_no_overrides(self):
        self.assertEqual(resolve(), resolve('balanced'))
        self.assertEqual(resolve()['directives'], {})
        self.assertEqual(resolve()['levels'], dict.fromkeys(AXES, 3))

    def test_all_3125_profiles_preserve_requested_levels_and_invariants(self):
        for levels in itertools.product(range(1, 6), repeat=5):
            expected = dict(zip(AXES, levels))
            result = resolve(','.join(f'{k}={v}' for k,v in expected.items()))
            self.assertEqual(result['levels'], expected)
            self.assertEqual(result['invariants'], resolve()['invariants'])
            self.assertEqual(result['execution'], 'NONE')
            self.assertEqual(result['writes'], 'NONE')

    def test_workflow_switch_preserves_task_configuration(self):
        profiles = [resolve('focus=2,sync=4', name) for name in ('direct','loop-code','other-skill','research')]
        for profile in profiles:
            self.assertEqual(profile['levels'], profiles[0]['levels'])
            self.assertEqual(profile['directives'], profiles[0]['directives'])

    def test_step_override_inherits_and_does_not_mutate_task(self):
        base = parse_attention('focus=2,sync=4')
        step = inherit(base, 'verify=5')
        self.assertEqual(step, dict(base, verify=5))
        self.assertEqual(base['verify'], 3)
        self.assertEqual(inherit(base), base)
        self.assertIsNot(inherit(base), base)
        self.assertEqual(inherit(base, 'balanced'), dict.fromkeys(AXES, 3))

    def test_bad_base_or_overrides_rejected(self):
        for base in ({}, dict.fromkeys(AXES, True), dict.fromkeys(AXES, 6), None):
            with self.assertRaises(ValueError): inherit(base, 'verify=4')
        with self.assertRaises(ValueError): inherit(parse_attention(), 'verify=4,verify=5')

    def test_invalid_profiles_and_command_labels_fail(self):
        for value in ('','focus=0','focus=6','focus=true','focus=1.0','focus=01',
                      'focus=2,focus=3','x=1','focus=1,','focus=1; echo x',False,3):
            with self.subTest(value=value), self.assertRaises(ValueError): parse_attention(value)
        for name in ('../escape','direct; echo x','',False):
            with self.assertRaises(ValueError): resolve(None, name)

    def test_risky_profile_warns_without_rewriting(self):
        row = resolve('focus=1,sync=1,batch=5,explore=5,verify=1')
        self.assertEqual(len(row['warnings']), 3)
        self.assertEqual(row['levels']['batch'], 5)
        self.assertIn('mandatory', row['directives']['verify'])

    def test_generated_resources_match(self):
        self.assertEqual(check(ROOT), [])

    def test_five_illustrations_explain_every_level(self):
        for axis in AXES:
            tree=ET.parse(ROOT/f'docs/assets/attention-{axis}.svg')
            words=[n.text for n in tree.iter() if n.tag.endswith('}text')]
            for heading in ('LOOP BEHAVIOR','CHOOSE WHEN','DO','AVOID'):
                self.assertEqual(words.count(heading),5)
            self.assertIn('03 / BALANCED',words)

    def test_single_installed_skill_runs_isolated_and_preserves_unrelated_files(self):
        import shutil
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); target=root/'.agents/skills/agent-attention'
            shutil.copytree(ROOT/'skills/agent-attention',target)
            sentinel=root/'keep.txt';sentinel.write_bytes(b'keep')
            before={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in root.rglob('*') if p.is_file()}
            helper=target/'scripts/attention.py'
            result=subprocess.run([sys.executable,'-I','-B',str(helper),'--attention','focus=2,sync=4',
                                   '--workflow','research'],cwd=root,capture_output=True,text=True,timeout=10)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(json.loads(result.stdout)['levels']['sync'],4)
            bad=subprocess.run([sys.executable,'-I','-B',str(helper),'--attention','verify=6'],
                               cwd=root,capture_output=True,text=True,timeout=10)
            self.assertEqual(bad.returncode,2)
            after={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in root.rglob('*') if p.is_file()}
            self.assertEqual(before,after)


if __name__ == '__main__': unittest.main()
