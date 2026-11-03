import copy
import unittest
from scripts.coord02_report import summarize,figures


class CoordReportTests(unittest.TestCase):
    def row(self,arm):
        return {'id':'01-'+arm,'arm':arm,'profile':'focus-1','case':'dependencies',
            'usage':{'input_tokens':100,'output_tokens':20,'cached_input_tokens':50,'total_tokens':120},
            'seconds':10,'status':'PASS','functional':True,'integrity':'PASS','actual_model':None,
            'model_turn_completed':True,'behavior':{'mandatory_check_command':True,'terminal_commands':3}}

    def test_reported_model_is_not_required_to_count_real_completed_turn(self):
        # Synthetic rows test aggregation only; not RUN model evidence.
        rows=[self.row('baseline'),self.row('attention')]
        result=summarize(rows)
        self.assertEqual(result['completed_model_sessions'],2)
        self.assertEqual(result['actual_model_reported'],0)
        self.assertEqual(result['pairs'][0]['token_delta_percent'],0)
        scenes=figures(result,rows)
        self.assertIn('n=1',str(scenes))

    def test_unknown_usage_is_not_zero_and_duplicates_rejected(self):
        rows=[self.row('baseline'),self.row('attention')]
        rows[-1]['usage']=None
        result=summarize(rows)
        self.assertEqual(result['usage_missing'],1);self.assertEqual(result['pairs'],[])
        with self.assertRaises(ValueError):summarize([rows[0],copy.deepcopy(rows[0])])
        bad=self.row('baseline');bad['usage']['total_tokens']=999
        with self.assertRaises(ValueError):summarize([bad])
        for value in (True,float('inf'),-1):
            bad=self.row('baseline');bad['seconds']=value
            with self.assertRaises(ValueError):summarize([bad])
