"""Independent acceptance controls; these tests never invoke a model."""
import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import subprocess
import unittest
from unittest import mock

from scripts.evaluation.acceptance import check_candidate, changes, digest
from scripts.evaluation.cases import CASE_IDS, load_case
from scripts.evaluation.runner import run


class CaseControls(unittest.TestCase):
    def prepare(self, folder, case):
        for name, content in case['files'].items():
            (folder/name).write_text(content, encoding='utf-8')

    def test_all_cases_reject_broken_missing_and_forged_content_but_accept_reference(self):
        for case_id in CASE_IDS:
            for control in ('broken', 'reference', 'wrong', 'missing', 'early-exit', 'forged-pass'):
                with self.subTest(case=case_id,control=control), tempfile.TemporaryDirectory() as raw:
                    base=Path(raw); folder=base/'workspace'; folder.mkdir()
                    case=load_case(case_id); self.prepare(folder,case)
                    if control=='reference':
                        for name, source in case['reference'].items():
                            (folder/name).write_text(source,encoding='utf-8')
                    elif control=='missing': (folder/case['allowed_edits'][0]).unlink()
                    elif control in ('early-exit', 'forged-pass', 'wrong'):
                        source={'early-exit':'raise SystemExit(0)\n',
                                'forged-pass':"print('PASS'); raise SystemExit(0)\n",
                                'wrong':'# Valid Python but no required implementation\n'}[control]
                        (folder/case['allowed_edits'][0]).write_text(source,encoding='utf-8')
                    if control=='missing':
                        with self.assertRaises(OSError): check_candidate(folder,case,base)
                    else:
                        process,error,mutated=check_candidate(folder,case,base)
                        self.assertEqual(process.returncode==0 and error is None and not mutated,
                                         control=='reference')

    def test_scope_guard_rejects_new_files_and_deleted_sources(self):
        with tempfile.TemporaryDirectory() as raw:
            folder=Path(raw); case=load_case(); self.prepare(folder,case)
            pins={name:digest(folder/name) for name in case['files']}
            self.assertEqual(changes(folder,pins,case['allowed_edits']),[])
            (folder/'extra.py').write_text('pass\n')
            self.assertIn('extra.py',changes(folder,pins,case['allowed_edits']))
            (folder/'discount.py').unlink()
            self.assertIn('discount.py',changes(folder,pins,case['allowed_edits']))

    def test_scope_guard_rejects_symlinks(self):
        with tempfile.TemporaryDirectory() as raw:
            folder=Path(raw); case=load_case(); self.prepare(folder,case)
            pins={name:digest(folder/name) for name in case['files']}
            (folder/'discount.py').unlink()
            try: (folder/'discount.py').symlink_to(folder/'shipping.py')
            except OSError: self.skipTest('symlink creation is unavailable')
            self.assertIn('discount.py',changes(folder,pins,case['allowed_edits']))

    def test_scope_guard_rejects_hardlinked_protected_sources(self):
        with tempfile.TemporaryDirectory() as raw:
            base=Path(raw); folder=base/'workspace'; folder.mkdir()
            case=load_case(); self.prepare(folder,case)
            pins={name:digest(folder/name) for name in case['files']}
            external=base/'control.py'; external.write_bytes((folder/'shipping.py').read_bytes())
            (folder/'shipping.py').unlink()
            try: os.link(external,folder/'shipping.py')
            except OSError: self.skipTest('hardlink creation is unavailable')
            self.assertIn('shipping.py',changes(folder,pins,case['allowed_edits']))

    def test_every_case_runs_through_real_git_and_external_oracle(self):
        real_run=subprocess.run
        for case_id in CASE_IDS:
            case=load_case(case_id)
            def fixture(command, *args, **kwargs):
                if command[0]!='fixture-codex': return real_run(command,*args,**kwargs)
                workspace=Path(command[command.index('-C')+1])
                for name,source in case['reference'].items():
                    (workspace/name).write_text(source,encoding='utf-8')
                event={'type':'turn.completed','usage':{'input_tokens':100,'cached_input_tokens':0,'output_tokens':10}}
                return subprocess.CompletedProcess(command,0,json.dumps(event),'')
            with self.subTest(case=case_id),tempfile.TemporaryDirectory() as raw:
                output=Path(raw)/'campaign'
                with mock.patch('scripts.evaluation.runner.subprocess.run',side_effect=fixture),contextlib.redirect_stdout(io.StringIO()):
                    rows=run(output,'fixture-codex',5,('low',),case_id=case_id)
                self.assertEqual(rows[0]['status'],'PASS')
                self.assertEqual(rows[0]['case_id'],case_id)
                self.assertTrue((output/'1-low/workspace/checks.py').is_file())
                self.assertFalse((output/'1-low/workspace/events.jsonl').exists())
                protocol=json.loads((output/'protocol.json').read_text())
                self.assertEqual(protocol['protocol_schema'],2)
                self.assertTrue(protocol['evaluator_sha256'])

    def test_unknown_case_is_rejected(self):
        for value in ('../escape','unknown',None):
            with self.subTest(value=value),self.assertRaises(ValueError): load_case(value)
