import tempfile
from pathlib import Path
import unittest
import os
from unittest import mock
from scripts.evaluation.control import failure_reason, classify, pending, append_attempt, parse_usage, execute_plan
from scripts.evaluation.paired import design, prompt
from scripts.evaluation.cases import load_case


class CampaignControlTests(unittest.TestCase):
    def test_reserved_interrupted_call_is_unknown_not_not_run_or_auto_retry(self):
        import json
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw);ledger=root/'ledger.jsonl'
            ledger.with_suffix('.reserved.jsonl').write_text('{"id":"a","attempt":1}\n')
            calls=[]
            result=execute_plan([{'id':'a'}],ledger,root/'STOP.json',lambda row:calls.append(row))
            self.assertEqual(calls,[])
            self.assertEqual(result['not_run'],[])
            self.assertEqual(result['reserved_without_result'],['a'])
    def test_relative_pilot_output_is_resolved_before_cli_cwd(self):
        from scripts.evaluation.pilot import freeze, run
        from scripts.evaluation.cases import ROOT
        import json
        import subprocess
        with tempfile.TemporaryDirectory(dir=ROOT) as raw:
            base=Path(raw); output=base/'pilot';marker=base/'STOP.json'
            relative=Path(os.path.relpath(output,Path.cwd()))
            freeze(relative,['fixture-cli'],marker)
            real_run=subprocess.run;calls=[]
            def cli(command,*args,**kwargs):
                if command[0]!='fixture-cli':return real_run(command,*args,**kwargs)
                calls.append(command)
                self.assertTrue(Path(command[command.index('-C')+1]).is_absolute())
                self.assertTrue(Path(kwargs['cwd']).is_absolute())
                self.assertTrue(Path(command[command.index('-C')+1]).is_dir())
                workspace=Path(command[command.index('-C')+1])
                self.assertFalse((workspace/'.agents').exists())
                self.assertFalse(any(w in (workspace/'AGENTS.md').read_text().casefold() for w in ('attention','skill','profile')))
                return subprocess.CompletedProcess(command,1,'','authentication failed')
            with mock.patch('scripts.evaluation.pilot.subprocess.run',side_effect=cli):
                result=run(relative)
            self.assertEqual(len(calls),1)
            self.assertEqual(len(result['not_run']),23)
            self.assertEqual(json.loads(marker.read_text())['reason'],'AUTH_FAILURE')
            with mock.patch('scripts.evaluation.pilot.sha',return_value='changed'):
                with self.assertRaises(ValueError): run(relative)
    def test_stop_first_capacity_and_resume_never_retries_blocked(self):
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw); calls=[]; plan=[{'id':'a'},{'id':'b'}]
            def invoke(row):
                calls.append(row['id'])
                return {'status':'BLOCKED_ENVIRONMENT','stop_reason':'MODEL_CAPACITY'}
            result=execute_plan(plan,root/'ledger.jsonl',root/'STOP.json',invoke)
            self.assertEqual(calls,['a']);self.assertEqual(result['not_run'],['b'])
            execute_plan(plan,root/'ledger.jsonl',root/'STOP.json',invoke)
            self.assertEqual(calls,['a'])

    def test_pilot_has_both_extremes_and_no_baseline_cue(self):
        rows=design()
        self.assertEqual(len(rows),24)
        self.assertEqual(rows,design())
        for axis in ('focus','sync','batch','explore','verify'):
            self.assertEqual({r['levels'][axis] for r in rows if r['profile'].startswith(axis+'-')},{1,5})
            for row in rows:
                if row['profile'].startswith(axis+'-'):
                    self.assertTrue(all(v==3 for k,v in row['levels'].items() if k!=axis))
        for row in rows:
            text=prompt(load_case(row['case']),row)
            if row['arm']=='baseline':
                self.assertFalse(any(w in text.casefold() for w in ('attention','profile','skill')))
        self.assertEqual(sum(r['arm']=='baseline' for r in rows[::2]),6)

    def test_first_partial_quota_is_fail_and_stops(self):
        events = [{'type':'tool.execution_start'}, {'type':'session.error',
                   'data':{'message':'You have exceeded your monthly quota'}}]
        self.assertEqual(failure_reason(events, ''), 'QUOTA_LIMIT')
        self.assertEqual(classify(1, events, '', False, True), 'FAIL')
        self.assertEqual(classify(1, events[1:], '', False, False), 'BLOCKED_ENVIRONMENT')

    def test_model_text_is_not_transport(self):
        self.assertIsNone(failure_reason([{'type':'assistant.message',
                          'data':{'content':'monthly quota exceeded'}}], ''))

    def test_blocked_is_not_silently_retried_and_retry_is_append_only(self):
        plan = [{'id':'a'}, {'id':'b'}]
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw)/'attempts.jsonl'
            row = {'id':'a', 'attempt':1, 'status':'BLOCKED_ENVIRONMENT'}
            append_attempt(path, row)
            self.assertEqual(pending(plan, [row]), ['b'])
            before = path.read_bytes()
            with self.assertRaises(ValueError): append_attempt(path, row)
            self.assertEqual(before, path.read_bytes())
            append_attempt(path, dict(row, attempt=2, retry_of=1))
            self.assertTrue(path.read_bytes().startswith(before))

    def test_unknown_and_malformed_usage_are_not_zero(self):
        self.assertIsNone(parse_usage(None))
        for usage in [{}, {'input_tokens':3,'output_tokens':1,'cached_input_tokens':4},
                      {'input_tokens':True,'output_tokens':1,'cached_input_tokens':0}]:
            with self.assertRaises(ValueError): parse_usage(usage)


if __name__ == '__main__': unittest.main()
