import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from scripts.evaluation.suite import plan_suite, run_suite

ROOT = Path(__file__).resolve().parents[1]


class SuiteTests(unittest.TestCase):
    def test_plan_freezes_three_separate_cases_and_eighteen_calls(self):
        plan = plan_suite()
        self.assertEqual(plan['planned_trials'], 18)
        self.assertEqual(plan['case_order'], ['ledger','dependencies','cents'])
        for campaign in plan['campaigns'].values():
            self.assertEqual(campaign['order'], ['low','balanced','high','high','balanced','low'])
        with self.assertRaises(ValueError): plan_suite(['cents','cents'])

    def test_quota_in_one_case_stops_all_later_cases(self):
        with tempfile.TemporaryDirectory() as raw:
            row={'trial':1,'profile':'low','status':'BLOCKED_ENVIRONMENT','usage':None,
                 'environment_failure':'QUOTA_LIMIT'}
            with mock.patch('scripts.evaluation.suite.run',return_value=[row]) as execute:
                result=run_suite(Path(raw)/'study')
            self.assertEqual(execute.call_count,1)
            self.assertEqual(result['recorded_trials'],1)
            self.assertEqual(len(result['not_run']),17)
            self.assertEqual(result['cases']['dependencies']['status'],'NOT_RUN')

    def test_plan_cli_never_calls_model_or_creates_output(self):
        with tempfile.TemporaryDirectory() as raw:
            output=Path(raw)/'absent'
            process=subprocess.run([sys.executable,str(ROOT/'scripts/evaluate_suite.py'),
                '--plan','--output',str(output),'--cli','not-a-real-cli'],capture_output=True,text=True)
            self.assertEqual(process.returncode,0,process.stderr)
            self.assertEqual(json.loads(process.stdout)['planned_trials'],18)
            self.assertFalse(output.exists())
