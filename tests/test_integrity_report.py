import copy
import json
from pathlib import Path
import tempfile
import unittest
from scripts.evaluation.integrity_report import summarize, figures, write_svg
from scripts.evaluation.publication import check

ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/'docs/testing/reports/2026-11-03'


class ReportTests(unittest.TestCase):
    def test_publication_hashes(self):
        self.assertGreater(check(REPORT),10)
    def test_zero_sample_is_unknown_not_zero_effect(self):
        pilot={'attempts':[], 'not_run':[str(i) for i in range(24)]}
        summary=summarize({'observations':[]},pilot)
        self.assertEqual(summary['grid']['not_run'],972)
        self.assertIsNone(summary['grid']['paired_metrics']['mean_pair_token_delta_percent'])

    def test_published_inputs_reproduce_and_reject_tampering(self):
        data=json.loads((REPORT/'historical.json').read_text())
        pilot=json.loads((REPORT/'pilot.json').read_text())
        actual=summarize(data,pilot)
        expected=json.loads((REPORT/'summary.json').read_text())
        # Tuples in the in-memory pairing key serialize as arrays.
        self.assertEqual(json.loads(json.dumps(actual)),expected)
        self.assertEqual(actual['grid']['paired_metrics']['n'],66)
        self.assertEqual(actual['grid']['quota_after_tool_start'],1)
        self.assertEqual(actual['grid']['quota_without_tool_start'],151)
        for bad in ('duplicate','usage','missing'):
            changed=copy.deepcopy(data);p=copy.deepcopy(pilot)
            if bad=='duplicate':changed['observations'].append(changed['observations'][0])
            if bad=='usage':changed['observations'][0]['calls'][0]['usage']['cached_input_tokens']=10**12
            if bad=='missing':p['not_run'].pop()
            with self.assertRaises(ValueError):summarize(changed,p)
        changed=copy.deepcopy(data)
        row=next(r for r in changed['observations'] if r['dataset']=='attention-grid-20261103' and r['arm']=='attention' and r['original_status']=='PASS')
        row['calls'][0]['usage']['output_tokens']+=10000
        self.assertNotEqual(summarize(changed,pilot)['grid']['paired_metrics'],actual['grid']['paired_metrics'])

    def test_figures_show_missingness_and_exact_chart_data(self):
        summary=json.loads((REPORT/'summary.json').read_text())
        protocol=json.loads((REPORT/'protocol.json').read_text())
        scenes=figures(summary,protocol)
        self.assertEqual(scenes,json.loads((REPORT/'chart-data.json').read_text()))
        self.assertIn('NOT_RUN',str(scenes['single-axis-pilot']))
        with tempfile.TemporaryDirectory() as raw:
            for name,scene in scenes.items():
                path=Path(raw)/(name+'.svg');write_svg(path,scene)
                self.assertEqual(path.read_bytes(),(REPORT/path.name).read_bytes())


if __name__=='__main__':unittest.main()
