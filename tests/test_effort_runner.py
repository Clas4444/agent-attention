import contextlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

from scripts.evaluate_effort import classify_trial, environment_failure, run


class ClassificationTests(unittest.TestCase):
    def test_zero_exit_without_completion_is_not_pass(self):
        self.assertEqual(classify_trial(0, [], '', [], 0), 'FAIL')

    def test_429_before_work_is_environment_block(self):
        self.assertEqual(classify_trial(None, [], 'HTTP 429 Too Many Requests', [], 1), 'BLOCKED_ENVIRONMENT')

    def test_structured_quota_before_work_is_environment_block(self):
        events=[{'type':'turn.failed','error':{'message':"You've hit your usage limit."}}]
        self.assertEqual(classify_trial(1,events,'',[],1),'BLOCKED_ENVIRONMENT')

    def test_model_text_and_command_output_cannot_spoof_environment_blocks(self):
        events=[{'type':'item.completed','item':{'type':'agent_message','text':"You've hit your usage limit."}},
                {'type':'item.completed','item':{'type':'command_execution',
                  'aggregated_output':'HTTP 429 Too Many Requests'}}]
        self.assertIsNone(environment_failure(events,''))

    def test_429_does_not_excuse_work_or_protected_changes(self):
        event={'type':'item.started','item':{'type':'command_execution'}}
        self.assertEqual(classify_trial(None,[event],'HTTP 429',[],1),'FAIL')
        self.assertEqual(classify_trial(None,[],'HTTP 429',['checks.py'],1),'FAIL')
        self.assertEqual(classify_trial(None,[],'HTTP 429',[],1,True),'FAIL')

    def test_completed_claim_still_requires_oracle_and_protected_integrity(self):
        events=[{'type':'turn.completed'}]
        self.assertEqual(classify_trial(0,events,'',[],0),'PASS')
        self.assertEqual(classify_trial(0,events,'',[],1),'FAIL')
        self.assertEqual(classify_trial(0,events,'',['checks.py'],0),'FAIL')


class RunnerTests(unittest.TestCase):
    def exercise(self, mode, order=('low',), campaign=None, disabled_skills=()):
        real_run=subprocess.run
        calls=[]
        def fixture(command, *args, **kwargs):
            if command[-1]=='checks.py' and mode=='oracle-timeout':
                raise subprocess.TimeoutExpired(command,15)
            if command[0]!='fixture-codex': return real_run(command,*args,**kwargs)
            calls.append(command)
            if mode=='429':
                return subprocess.CompletedProcess(command,1,'{"type":"turn.started"}\n','HTTP 429 Too Many Requests')
            folder=Path(command[command.index('-C')+1])
            if mode in ('json-quota','json-quota-after-work','json-capacity'):
                events=[]
                if mode=='json-quota-after-work':
                    (folder/'discount.py').write_text('def discount(cents):\n    return cents * 9 // 10\n')
                    events.append({'type':'item.started','item':{'type':'command_execution'}})
                message='Selected model is at capacity.' if mode=='json-capacity' else "You've hit your usage limit."
                events.append({'type':'turn.failed','error':{'message':message}})
                return subprocess.CompletedProcess(command,1,'\n'.join(json.dumps(e) for e in events),'')
            if mode=='429-after-delete':
                (folder/'discount.py').unlink()
                return subprocess.CompletedProcess(command,1,'','HTTP 429 Too Many Requests')
            (folder/'discount.py').write_text('def discount(cents):\n    return cents * 9 // 10\n')
            (folder/'checkout.py').write_text('from discount import discount\nfrom shipping import shipping\ndef total(cents):\n    amount = discount(cents)\n    return amount + shipping(amount)\n')
            if mode=='tamper': (folder/'checks.py').write_text("print('forged PASS')\n")
            usage={'input_tokens':100,'cached_input_tokens':80,'output_tokens':10}
            if mode=='invalid-usage': usage['cached_input_tokens']=101
            event={'type':'turn.completed','usage':usage}
            out=json.dumps(event)+'\n' if mode!='no-completion' else ''
            return subprocess.CompletedProcess(command,0,out,'')
        with tempfile.TemporaryDirectory() as temporary:
            output=Path(temporary)/'campaign'
            with mock.patch('scripts.evaluate_effort.subprocess.run',side_effect=fixture), contextlib.redirect_stdout(io.StringIO()):
                results=run(output,'fixture-codex',5,order,campaign,disabled_skills=disabled_skills)
            self.assertTrue((output/'protocol.json').is_file())
            self.assertTrue((output/f'1-{order[0]}/input-pins.json').is_file())
            summary=json.loads((output/'summary.json').read_text())
            self.assertEqual(summary['recorded_trials'],len(results))
            if campaign:
                self.assertEqual(summary['axis'],campaign['axis'])
                for number,label in enumerate(order,1):
                    self.assertIn(campaign['profiles'][label],(output/f'{number}-{label}/prompt.txt').read_text())
            persisted=json.loads((output/'results.json').read_text())
            self.assertEqual(results,persisted)
            remaining=json.loads((output/'not-run.json').read_text()) if (output/'not-run.json').exists() else None
            return results,calls,remaining

    def test_real_fixture_git_oracle_and_saved_inputs(self):
        results,_,_=self.exercise('pass')
        self.assertEqual(results[0]['status'],'PASS')
        self.assertEqual(results[0]['usage']['total_tokens'],110)

    def test_host_skill_exclusions_are_forwarded_without_changing_global_config(self):
        paths=['C:/fixture/user skills/example/SKILL.md']
        results,calls,_=self.exercise('pass',disabled_skills=paths)
        command=calls[0]
        self.assertIn('skills.config=[{path="C:/fixture/user skills/example/SKILL.md",enabled=false}]',command)
        self.assertIn('plugins',command)
        self.assertIn('multi_agent',command)
        self.assertEqual(results[0]['status'],'PASS')

    def test_single_axis_design_executes_and_summarizes_correct_profiles(self):
        from scripts.effort_campaign import campaign_plan
        campaign=campaign_plan('batch',[1,5],1)
        results,calls,_=self.exercise('pass',campaign['order'],campaign)
        self.assertEqual([r['profile'] for r in results],['batch-1','batch-5'])
        self.assertEqual(len(calls),2)
        self.assertTrue(all(r['status']=='PASS' for r in results))

    def test_forged_completion_or_modified_oracle_cannot_pass(self):
        for mode in ('no-completion','tamper'):
            with self.subTest(mode=mode):
                results,_,_=self.exercise(mode)
                self.assertEqual(results[0]['status'],'FAIL')

    def test_invalid_usage_is_saved_as_failure(self):
        results,_,_=self.exercise('invalid-usage')
        self.assertEqual(results[0]['status'],'FAIL')
        self.assertIsNone(results[0]['usage'])
        self.assertTrue(results[0]['usage_error'])

    def test_oracle_timeout_is_saved_as_failure(self):
        results,_,_=self.exercise('oracle-timeout')
        self.assertEqual(results[0]['status'],'FAIL')
        self.assertEqual(results[0]['acceptance_error'],'TimeoutExpired')

    def test_deleted_work_cannot_be_classified_as_pre_action_block(self):
        results,_,_=self.exercise('429-after-delete')
        self.assertEqual(results[0]['status'],'FAIL')

    def test_rate_limit_stops_further_model_invocations(self):
        results,calls,remaining=self.exercise('429',('low','high'))
        self.assertEqual(len(calls),1)
        self.assertEqual(results[0]['status'],'BLOCKED_ENVIRONMENT')
        self.assertEqual(remaining,['high'])

    def test_json_environment_failures_stop_even_after_partial_work(self):
        for mode,status in [('json-quota','BLOCKED_ENVIRONMENT'),
                            ('json-quota-after-work','FAIL'),('json-capacity','BLOCKED_ENVIRONMENT')]:
            with self.subTest(mode=mode):
                results,calls,remaining=self.exercise(mode,('low','high'))
                self.assertEqual(len(calls),1)
                self.assertEqual(results[0]['status'],status)
                self.assertEqual(remaining,['high'])
