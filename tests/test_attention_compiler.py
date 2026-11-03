import json
from pathlib import Path
import subprocess
import sys
import unittest
import tempfile
from scripts.attention import AXES,compile_prompt,ProfileSession,from_artifact,parse_attention


class CompilerTests(unittest.TestCase):
    def test_lazy_compiler_all_levels_and_invariant(self):
        for axis in AXES:
            for level in range(1,6):
                value=compile_prompt(f'{axis}={level}',scope='work')
                self.assertIn('mandatory',value)
                self.assertIn('No routing',value)
                if level!=3:self.assertIn(AXES[axis][level-1],value)
                else:self.assertNotIn('Override:',value)
                for other in AXES:
                    if other!=axis:self.assertNotIn(AXES[other][0],value)
                self.assertLess(len(value),1500)

    def test_scope_exception_return_and_finish(self):
        session=ProfileSession('focus=2')
        with self.assertRaises(RuntimeError):
            with session.scope('review','verify=5') as profile:
                self.assertEqual(profile['levels']['focus'],2)
                self.assertEqual(profile['levels']['verify'],5)
                raise RuntimeError('fixture')
        self.assertEqual(session.levels,parse_attention('focus=2'))
        def early():
            with session.scope('edit','batch=5'):return
        early();self.assertEqual(session.levels,parse_attention('focus=2'))
        with session.scope('outer','verify=5'):
            with session.scope('inner','sync=1') as inner:
                self.assertEqual(inner['levels']['verify'],3)
            self.assertEqual(session.levels['verify'],5)
            session.finish()
        self.assertEqual(session.levels,parse_attention('focus=2'))
        with self.assertRaises(ValueError):
            with session.scope('late','verify=1'):pass

    def test_combined_opt_in_strict_artifact(self):
        artifact={'attention_contract':1,'scope':'review','levels':parse_attention('verify=5')}
        with self.assertRaises(ValueError):from_artifact(artifact)
        for consent in ('false',1,None):
            with self.assertRaises(ValueError):from_artifact(artifact,opt_in=consent)
        self.assertEqual(from_artifact(artifact,opt_in=True)['levels']['verify'],5)
        for patch in ({'attention_contract':2},{'route':'next'},{'authority':'all'},{'levels':{'verify':True}}):
            with self.assertRaises(ValueError):from_artifact(dict(artifact,**patch),opt_in=True)

    def test_actual_cli_prompt_and_json_compatibility(self):
        helper=Path(__file__).resolve().parents[1]/'scripts/attention.py'
        p=subprocess.run([sys.executable,'-I','-B',str(helper),'--attention','focus=5','--format','prompt'],capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stderr);self.assertIn('focus=5',p.stdout)
        p=subprocess.run([sys.executable,'-I','-B',str(helper),'--attention','focus=5'],capture_output=True,text=True)
        self.assertEqual(json.loads(p.stdout)['levels']['focus'],5)
        for extra in (['--scope','review'],['--format','prompt','--workflow','../bad']):
            p=subprocess.run([sys.executable,'-I','-B',str(helper),*extra],capture_output=True,text=True)
            self.assertEqual(p.returncode,2)

    def test_setup_select_compiles_effective_profile_without_graph(self):
        from scripts.attention_setup import template
        helper=Path(__file__).resolve().parents[1]/'scripts/attention_setup.py'
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw);plan=root/'plan.json';facts=root/'facts.json'
            plan.write_text(json.dumps(template()));facts.write_text('{"risk":"high"}')
            p=subprocess.run([sys.executable,'-I','-B',str(helper),'select','--file',str(plan),'--facts-file',str(facts),'--format','prompt'],capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stderr);self.assertIn('verify=5',p.stdout)
            self.assertNotIn('focus=3',p.stdout)
