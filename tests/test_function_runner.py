import unittest
from scripts.evaluation.function03 import plan,prompt,executed_script,executed_full_checks
from scripts.evaluation.function_cases import case
from scripts.evaluation.trace_metrics import task_status


class FunctionRunnerTests(unittest.TestCase):
    def test_correct_artifact_without_required_trace_or_accounting_cannot_pass(self):
        self.assertEqual(task_status(0,True,True,[],True,None,True),'PASS')
        self.assertEqual(task_status(0,True,True,[],False,None,True),'FAIL')
        self.assertEqual(task_status(0,True,True,[],True,'USAGE',True),'FAIL')
        self.assertEqual(task_status(None,False,False,[],False,'PROCESS',False),'BLOCKED_ENVIRONMENT')
        self.assertEqual(task_status(None,False,False,['source.py'],False,'PROCESS',False),'FAIL')
    def test_preregistered_plan_and_neutral_no_profile_contamination(self):
        rows=plan();self.assertEqual(len(rows),12);self.assertEqual(rows,plan())
        for axis in ('focus','sync','batch','explore','verify'):
            self.assertEqual({r['setting'] for r in rows if r['case']==axis and r['profile'] not in ('neutral','balanced')},{axis+'=1',axis+'=5'})
        neutral=next(r for r in rows if r['arm']=='baseline')
        text=prompt(case(neutral['case']),neutral).lower()
        self.assertFalse(any(term in text for term in ('attention','profile','skill')))

    def test_read_or_echo_is_not_a_source_refresh_or_compiler(self):
        for command in ('Get-Content source_tool.py','echo "python source_tool.py refresh"'):
            self.assertFalse(executed_script([{'command':command,'exit_code':0}],'source_tool.py','refresh'))
        self.assertTrue(executed_script([{'command':'py -3 -B source_tool.py refresh','exit_code':0}],'source_tool.py','refresh'))
        self.assertTrue(executed_script([{'command':'python .agents/skills/agent-attention/scripts/attention.py --format prompt','exit_code':0}],'attention.py','--format'))
        self.assertFalse(executed_full_checks([{'command':'python -B checks.py net','exit_code':0}]))
        self.assertFalse(executed_full_checks([{'command':"python 'checks.py' invoice",'exit_code':0}]))
        self.assertTrue(executed_full_checks([{'command':'python -B checks.py','exit_code':0}]))
