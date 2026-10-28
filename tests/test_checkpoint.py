import json
import os
import subprocess
import sys
from pathlib import Path
import tempfile
import unittest
from scripts.checkpoint import execute


class CheckpointTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'checkpoint.json'

    def init(self):
        return execute('init',self.path,'task-1','implementation','focus=2,sync=4')

    def test_switch_override_and_restore_are_observable(self):
        first=self.init()
        review=execute('enter',self.path,'task-1','review',override='verify=5')
        final=execute('enter',self.path,'task-1','testing')
        self.assertEqual(review['effective_levels']['focus'],2)
        self.assertEqual(review['effective_levels']['verify'],5)
        self.assertEqual(final['effective_levels'],first['task_levels'])
        self.assertFalse(final['override_active'])
        self.assertEqual([r['workflow'] for r in final['history']],['implementation','review','testing'])

    def test_wrong_task_and_duplicate_init_never_overwrite(self):
        self.init();before=self.path.read_bytes()
        for action,task in [('enter','task-2'),('init','task-1')]:
            with self.assertRaises(ValueError):execute(action,self.path,task)
            self.assertEqual(self.path.read_bytes(),before)

    def test_legacy_or_other_semantics_require_explicit_new_profile(self):
        initial=self.init()
        for version in (None,'0.1.0','future'):
            row=dict(initial)
            if version is None: row.pop('semantics_version')
            else: row['semantics_version']=version
            self.path.write_text(json.dumps(row),encoding='utf-8')
            before=self.path.read_bytes()
            with self.subTest(version=version), self.assertRaisesRegex(ValueError,'semantics changed'):
                execute('enter',self.path,'task-1','review')
            self.assertEqual(self.path.read_bytes(),before)

    def test_finished_task_cannot_leak_into_new_work(self):
        self.init();result=execute('finish',self.path,'task-1')
        self.assertEqual(result['status'],'finished')
        self.assertFalse(result['override_active'])
        before=self.path.read_bytes()
        with self.assertRaises(ValueError):execute('enter',self.path,'task-1','another-step')
        self.assertEqual(self.path.read_bytes(),before)

    def test_invalid_profiles_write_nothing(self):
        with self.assertRaises(ValueError):execute('init',self.path,'task-1',attention='focus=1,focus=5')
        self.assertFalse(self.path.exists())
        self.init();before=self.path.read_bytes()
        with self.assertRaises(ValueError):execute('enter',self.path,'task-1',override='verify=6')
        self.assertEqual(self.path.read_bytes(),before)

    def test_show_is_read_only_and_task_profile_cannot_be_replaced(self):
        self.init();before=self.path.read_bytes()
        execute('show',self.path,'task-1')
        self.assertEqual(self.path.read_bytes(),before)
        with self.assertRaises(ValueError):execute('enter',self.path,'task-1',attention='focus=5')
        self.assertEqual(self.path.read_bytes(),before)

    def test_malformed_history_rejected(self):
        state=self.init();state['history'][-1]['override_active']='false'
        self.path.write_text(json.dumps(state),encoding='utf-8');before=self.path.read_bytes()
        with self.assertRaises(ValueError):execute('show',self.path,'task-1')
        self.assertEqual(self.path.read_bytes(),before)

    def test_false_override_flag_cannot_hide_drift(self):
        state=self.init()
        state['effective_levels']=dict(state['task_levels'],verify=5)
        state['history'][-1]['effective_levels']=state['effective_levels']
        self.path.write_text(json.dumps(state),encoding='utf-8')
        with self.assertRaises(ValueError):execute('show',self.path,'task-1')

    def test_boolean_version_and_non_object_history_rejected(self):
        state=self.init()
        for field,value in [('version',True),('history',['untrusted'])]:
            changed=dict(state,**{field:value})
            self.path.write_text(json.dumps(changed),encoding='utf-8')
            with self.assertRaises(ValueError):execute('show',self.path,'task-1')

    def test_hardlinked_state_is_rejected_without_changing_original(self):
        self.init();alias=self.path.with_name('alias.json')
        os.link(self.path,alias);before=self.path.read_bytes()
        with self.assertRaises(ValueError):execute('enter',alias,'task-1','review')
        self.assertEqual(self.path.read_bytes(),before)

    def test_duplicate_json_and_directory_destination_rejected(self):
        self.path.write_text('{"version":1,"version":1}',encoding='utf-8')
        before=self.path.read_bytes()
        with self.assertRaises(ValueError):execute('show',self.path,'task-1')
        self.assertEqual(self.path.read_bytes(),before)
        with self.assertRaises(ValueError):execute('init',self.path.parent,'task-1')

    def test_compact_cli_preserves_full_history_on_disk(self):
        helper=Path(__file__).resolve().parents[1]/'scripts/checkpoint.py'
        command=[sys.executable,str(helper),'init','--state',str(self.path),'--task','task-1',
                 '--attention','focus=2,sync=4','--quiet']
        result=subprocess.run(command,capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,0,result.stderr)
        displayed=json.loads(result.stdout)
        saved=json.loads(self.path.read_text())
        self.assertNotIn('history',displayed)
        self.assertNotIn('task_levels',displayed)
        self.assertEqual(displayed['effective_levels'],saved['task_levels'])
        self.assertEqual(len(saved['history']),1)

    def test_installed_checkpoint_runs_with_isolated_python(self):
        import shutil
        root=Path(__file__).resolve().parents[1]
        installed=self.path.parent/'installed skill'
        shutil.copytree(root/'skills/agent-attention',installed)
        result=subprocess.run([sys.executable,'-I','-B',str(installed/'scripts/checkpoint.py'),
            'init','--state',str(self.path),'--task','task-1','--attention','focus=2,sync=4','--quiet'],
            cwd=self.path.parent,capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(json.loads(self.path.read_text())['effective_levels']['sync'],4)


if __name__=='__main__':unittest.main()
