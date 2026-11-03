"""COORD-02 product boundaries; fixture plumbing is not model adherence."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from scripts.attention import AXES,resolve
from scripts.attention_setup import select,template,MissingFacts,export
from scripts.workflow_setup import attach_attention,template as workflow,start,select as choice,advance

ROOT=Path(__file__).resolve().parents[1]


class ProductBoundaryTests(unittest.TestCase):
    def test_axis_directions_and_mandatory_invariants_all_3125_profiles(self):
        import itertools
        baseline=resolve()
        self.assertEqual(baseline['levels'],dict.fromkeys(AXES,3))
        self.assertEqual(baseline['directives'],{})
        for values in itertools.product(range(1,6),repeat=5):
            result=resolve(','.join(f'{k}={v}' for k,v in zip(AXES,values)))
            self.assertEqual(result['invariants'],baseline['invariants'])
            self.assertEqual(result['execution'],'NONE')
        for invalid in ('verify=0','focus=6','verify=true','verify=1,verify=5','route=5'):
            with self.assertRaises(ValueError):resolve(invalid)

    def test_exception_early_stop_and_missing_fact_do_not_leak_selection(self):
        plan=template();original=copy.deepcopy(plan)
        try:
            selected=select(plan,{'risk':'high'})
            self.assertEqual(selected['levels']['verify'],5)
            raise RuntimeError('fixture early stop')
        except RuntimeError:pass
        self.assertEqual(select(plan,{'risk':'ordinary'})['levels']['verify'],3)
        self.assertEqual(plan,original)
        with self.assertRaises(MissingFacts):select(plan,{})

    def test_combined_v1_changes_attention_only_not_routes_or_skills(self):
        graph=workflow('skills');original=copy.deepcopy(graph)
        updated=attach_attention(graph,{'attention':{'focus':2},
            'steps':{'verify':[{'binding':0,'attention':{'verify':5}}]}})
        stripped=copy.deepcopy(updated);stripped.pop('attention',None)
        for step in stripped['steps']:
            for binding in step['bindings']:binding.pop('attention',None)
        self.assertEqual(stripped,original)
        state=start(updated,{'kind':'bug','risk':'high'})
        self.assertTrue(choice(updated,state)['attention_requested'])
        reviewed=advance(updated,state,'PASS','fixture step complete')
        self.assertEqual(choice(updated,reviewed)['attention']['verify'],5)
        ordinary=advance(updated,reviewed,'PASS','fixture more work',{'done':False})
        self.assertEqual(choice(updated,ordinary)['attention']['verify'],3)
        unsupported=copy.deepcopy(graph);unsupported['schema_version']=2
        with self.assertRaisesRegex(ValueError,'schema_version 1'):start(unsupported)
        for patch in ({'routes':[]},{'attention':None},{'attention':{'verify':True}}):
            with self.assertRaises(ValueError):attach_attention(graph,patch)

    def test_standalone_installed_helper_has_no_peer_checkout_or_cross_write(self):
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw);installed=root/'attention-setup';shutil.copytree(ROOT/'skills/attention-setup',installed)
            draft=root/'plan.json';draft.write_text(json.dumps(template()))
            cmd=[sys.executable,'-I','-B',str(installed/'scripts/attention_setup.py'),'select','--file',str(draft)]
            p=subprocess.run(cmd,cwd=root,capture_output=True,text=True,timeout=10)
            self.assertEqual(p.returncode,2);self.assertEqual(json.loads(p.stdout)['status'],'BLOCKED')
            self.assertFalse((root/'agent-workflows').exists())
            outside=root/'sentinel';outside.write_text('unchanged')
            project=root/'project';project.mkdir()
            for bad in ('../sentinel','C:/fixed-machine-path','.git/config'):
                with self.assertRaises(ValueError):export(template(),project,bad)
            self.assertEqual(outside.read_text(),'unchanged')
            self.assertEqual(list(project.iterdir()),[])
