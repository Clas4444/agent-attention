import unittest
from scripts.validation_metrics import summarize


class ValidationMetricsTests(unittest.TestCase):
    def test_environment_failures_do_not_become_skill_improvements(self):
        records=[{'trial_id':str(i),'kind':'model_trial','classification':s} for i,s in
                 enumerate(['BLOCKED_ENVIRONMENT','PASS','FAIL'])]
        result=summarize(records)
        self.assertEqual(result['attempts'],3)
        self.assertEqual(result['evaluated_attempts'],2)
        self.assertEqual(result['success_rate'],0.5)

    def test_duplicate_copied_results_and_controls_do_not_inflate_denominators(self):
        row={'trial_id':'baseline/handoff','kind':'model_trial','classification':'PASS'}
        with self.assertRaises(ValueError):summarize([row,row.copy()])
        with self.assertRaises(ValueError):summarize([dict(row,kind='scorer_control')])

    def test_no_behavior_execution_is_not_a_pass(self):
        self.assertIsNone(summarize([])['success_rate'])
        self.assertEqual(summarize([])['status'],'NOT_RUN')


if __name__=='__main__':unittest.main()
