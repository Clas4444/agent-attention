import copy
import json
from pathlib import Path
import unittest
from scripts.function03_report import summarize


class FunctionReportTests(unittest.TestCase):
    def setUp(self):
        self.rows=json.loads((Path(__file__).resolve().parents[1]/'docs/testing/reports/2026-11-03/function-03/observations.json').read_text())['attempts']

    def test_saved_observations_and_unknown_usage(self):
        summary=summarize(self.rows)
        self.assertEqual(summary['CLI_attempts'],12)
        self.assertEqual(summary['functional_PASS'],12)
        rows=copy.deepcopy(self.rows);rows[0]['usage']=None
        self.assertEqual(summarize(rows)['missing_usage'],1)

    def test_duplicate_and_invalid_accounting_rejected(self):
        with self.assertRaises(ValueError):summarize(self.rows+[self.rows[0]])
        rows=copy.deepcopy(self.rows);rows[0]['usage']['total_tokens']+=1
        with self.assertRaises(ValueError):summarize(rows)
        for bad in (True,-1,float('inf')):
            rows=copy.deepcopy(self.rows);rows[0]['seconds']=bad
            with self.assertRaises(ValueError):summarize(rows)
            rows=copy.deepcopy(self.rows);rows[0]['usage']['input_tokens']=bad
            with self.assertRaises(ValueError):summarize(rows)
