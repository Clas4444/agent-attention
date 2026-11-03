from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import tempfile
import unittest
import subprocess
import sys
from scripts.evaluation.coordination import Budget,blocks,marker,stop_reasons,write_marker,diagnostic
from scripts.evaluation.coordination import LOCAL,validate

FIXTURE=Path(__file__).with_name('fixtures')/'coordination-v1.json'


class CoordinationTests(unittest.TestCase):
    def test_all_local_faults_stay_local(self):
        own={'provider':'codex','account_domain':None,'campaign':'own'}
        for reason in LOCAL:
            value=marker(own,reason,'evidence/local.json')
            self.assertTrue(blocks(value,own))
            self.assertFalse(blocks(value,dict(own,campaign='peer')))

    def test_conflicting_scope_or_malformed_marker_is_not_coerced(self):
        own={'provider':'codex','account_domain':None,'campaign':'own'}
        base=marker(own,'QUOTA','evidence/quota.json')
        for patch in ({'scope':'campaign'},{'reason':'QUOTA'},{'time':None},{'evidence':['C:/private/file']}):
            with self.assertRaises(ValueError):validate(dict(base,**patch))
    def test_stale_provider_stop_requires_review_but_not_other_provider(self):
        context={'provider':'codex','account_domain':None,'campaign':'current'}
        old=marker(dict(context,campaign='old'),'QUOTA','evidence/quota.json',when='2000-01-01T00:00:00Z')
        self.assertEqual(diagnostic(old,context),'STALE_MARKER_REVIEW_REQUIRED')
        self.assertFalse(blocks(old,dict(context,provider='copilot')))
    def test_contract_cases_and_stale_scopes(self):
        fixture=json.loads(FIXTURE.read_text())
        for case in fixture['cases']:
            context={'provider':case['marker_provider'],'account_domain':case['marker_domain'],'campaign':case['marker_campaign']}
            value=marker(context,case['reason'].upper(),'evidence/transport.json',when='2000-01-01T00:00:00Z')
            target={'provider':case['provider'],'account_domain':case['account_domain'],'campaign':case['campaign']}
            with self.subTest(case=case['id']):self.assertEqual(blocks(value,target),case['blocked'])

    def test_marker_preserves_history_and_rejects_unknown_format(self):
        with tempfile.TemporaryDirectory() as raw:
            context={'provider':'provider-a','campaign':'own','account_domain':None}
            one=write_marker(raw,marker(context,'AUTH_HOME','evidence/home.json'))
            before=one.read_bytes()
            write_marker(raw,marker(context,'QUOTA','evidence/quota.json'))
            self.assertEqual(one.read_bytes(),before)
            self.assertEqual(len(stop_reasons([raw],context)),2)
            with self.assertRaises(ValueError):blocks({'version':2},context)

    def test_concurrent_reservation_and_absolute_cap_across_campaigns(self):
        with tempfile.TemporaryDirectory() as raw:
            path=Path(raw)/'budget.db';budget=Budget(path,cap=4)
            def attempt(index):
                try:return Budget(path,4).reserve(str(index),'campaign-'+str(index))
                except ValueError:return None
            with ThreadPoolExecutor(max_workers=8) as pool:results=list(pool.map(attempt,range(8)))
            self.assertEqual(sum(r is not None for r in results),1)
            winner=str(next(i for i,r in enumerate(results) if r is not None));budget.finish(winner,'FAIL')
            for i in range(3):budget.reserve('next'+str(i),'new-campaign');budget.finish('next'+str(i),'TIMEOUT')
            self.assertEqual(budget.count(),4)
            with self.assertRaisesRegex(ValueError,'budget exhausted'):budget.reserve('fifth','another-campaign')
            with self.assertRaisesRegex(ValueError,'cannot be reset'):Budget(path,cap=24)

    def test_interrupted_reservation_never_auto_expires(self):
        with tempfile.TemporaryDirectory() as raw:
            path=Path(raw)/'budget.db';Budget(path).reserve('one','old')
            with self.assertRaisesRegex(ValueError,'interrupted'):Budget(path).reserve('two','new')

    def test_real_processes_share_one_inflight_gate(self):
        with tempfile.TemporaryDirectory() as raw:
            path=Path(raw)/'budget.db';Budget(path)
            script="from scripts.evaluation.coordination import Budget; import sys; "\
                   "Budget(sys.argv[1]).reserve(sys.argv[2], 'process-campaign')"
            processes=[subprocess.Popen([sys.executable,'-c',script,str(path),name],
                        stdout=subprocess.PIPE,stderr=subprocess.PIPE) for name in ('one','two')]
            codes=[]
            for process in processes:
                process.communicate(timeout=20);codes.append(process.returncode)
            self.assertEqual(sorted(codes),[0,1])
            self.assertEqual(Budget(path).count(),1)
