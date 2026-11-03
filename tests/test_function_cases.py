import copy
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from scripts.evaluation.function_cases import case
from scripts.evaluation.acceptance import check_candidate


class FunctionCaseTests(unittest.TestCase):
    def test_reference_controls_and_wrong_outputs(self):
        for name in ('focus','batch','explore','verify','sync'):
            data=case(name)
            with self.subTest(case=name),tempfile.TemporaryDirectory() as raw:
                root=Path(raw);work=root/'workspace';work.mkdir()
                for path,source in data['files'].items():(work/path).write_text(source,encoding='utf-8',newline='\n')
                oracle=copy.deepcopy(data);oracle['files']=data.get('oracle_files',data['files'])
                p,error,mutations=check_candidate(work,oracle,root)
                self.assertTrue(p.returncode!=0 or error or mutations)
                for path,source in data['reference'].items():(work/path).write_text(source,encoding='utf-8',newline='\n')
                if name=='sync':
                    process=subprocess.run([sys.executable,'source_tool.py','refresh'],cwd=work,capture_output=True,text=True)
                    self.assertEqual(process.returncode,0,process.stderr)
                    for path,value in data['expected_updates'].items():self.assertEqual((work/path).read_bytes(),value.encode())
                p,error,mutations=check_candidate(work,oracle,root)
                self.assertEqual(p.returncode,0,p.stderr);self.assertIsNone(error);self.assertFalse(mutations)

    def test_smoke_pass_is_not_functional_oracle_pass(self):
        data=case('verify')
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw);work=root/'workspace';work.mkdir()
            for name,source in data['files'].items():(work/name).write_text(source,encoding='utf-8',newline='\n')
            source=data['files']['windows.py'].replace('    result=[]',"    for a,b in windows:\n        if a>b:raise ValueError('bad')\n    result=[]")
            (work/'windows.py').write_text(source,encoding='utf-8')
            p=subprocess.run([sys.executable,'-B','checks.py'],cwd=work,capture_output=True,text=True)
            self.assertEqual(p.returncode,0)
            oracle=copy.deepcopy(data);oracle['files']=data['oracle_files']
            p,error,mutations=check_candidate(work,oracle,root)
            self.assertNotEqual(p.returncode,0)
