import copy
import json
from pathlib import Path
import tempfile
import unittest
import re
from scripts.evaluation.delivery import check
from scripts.evaluation.function_cases import case
from scripts.evaluation.cases import load_case
from scripts.evaluation.acceptance import check_candidate
from scripts.evaluation.trace_metrics import successful_mandatory_check
from scripts.evaluation.function03 import executed_full_checks

ROOT=Path(__file__).resolve().parents[1]


class DeliveryTests(unittest.TestCase):
    def test_published_reports_embed_both_png_charts_and_use_current_headings(self):
        expected={'function-03':{'actual-costs.png','acceptance-behavior.png'},
                  'coord-02':{'axis-paired-effects.png','quality-behavior.png'}}
        for name,images in expected.items():
            page=ROOT/'docs/testing/reports/2026-11-03'/name/'README.md'
            body=page.read_text(encoding='utf-8')
            self.assertTrue(images.issubset(set(re.findall(r'!\[[^\]]*\]\(([^)]+)\)',body))))
            self.assertNotIn('NO_PUSH',body.splitlines()[0])
            self.assertIn('Source',body)
            for image in images:self.assertTrue((page.parent/image).is_file())

    def test_public_receipts_and_measured_source_archives(self):
        for name in ('coord-02','function-03'):
            result=check(ROOT/'docs/testing/reports/2026-11-03'/name)
            self.assertEqual(result['artifact_status'],'PASS')
            self.assertEqual(result['measured_sources'],'PASS')

    def test_public_candidates_pass_independent_frozen_oracles_and_required_commands(self):
        # No raw traces, private snapshots, CLI or model calls are needed.
        for name in ('coord-02','function-03'):
            directory=ROOT/'docs/testing/reports/2026-11-03'/name
            rows={r['id']:r for r in json.loads((directory/'observations.json').read_text())['attempts']}
            for sample in json.loads((directory/'trace-evidence.json').read_text())['attempts']:
                row=rows[sample['id']]
                data=case(row['case']) if name=='function-03' else load_case(row['case'])
                with self.subTest(task=name,id=row['id']),tempfile.TemporaryDirectory() as raw:
                    root=Path(raw);workspace=root/'workspace';workspace.mkdir()
                    for path,source in data['files'].items():(workspace/path).write_text(source,encoding='utf-8',newline='\n')
                    self.assertEqual(set(sample['candidate_outputs']),set(data['allowed_edits']))
                    for path,source in sample['candidate_outputs'].items():(workspace/path).write_text(source,encoding='utf-8',newline='\n')
                    oracle=copy.deepcopy(data);oracle['files']=data.get('oracle_files',data['files'])
                    p,error,mutations=check_candidate(workspace,oracle,root)
                    self.assertEqual(p.returncode,0,p.stderr);self.assertIsNone(error);self.assertFalse(mutations)
                    mandatory=executed_full_checks(sample['actions']) if name=='function-03' else successful_mandatory_check(sample['actions'])
                    self.assertTrue(mandatory)
