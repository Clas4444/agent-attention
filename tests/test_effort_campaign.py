import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from scripts.attention import AXES, parse_attention
from scripts.effort_campaign import campaign_plan, summarize_campaign

ROOT=Path(__file__).resolve().parents[1]


class CampaignTests(unittest.TestCase):
    def test_each_axis_can_cover_five_levels_without_changing_other_axes(self):
        for axis in AXES:
            plan=campaign_plan(axis,(1,2,3,4,5),2)
            self.assertEqual(plan['planned_trials'],10)
            self.assertEqual(plan['order'][5:],plan['order'][:5][::-1])
            for label,setting in plan['profiles'].items():
                levels=parse_attention(setting)
                self.assertEqual(levels[axis],int(label[-1]))
                self.assertTrue(all(levels[name]==3 for name in AXES if name!=axis))

    def test_bad_designs_are_rejected(self):
        for axis,levels,repeats in [('other',[1],2),('focus',[1,1],2),('focus',[0,5],2),
                                    ('focus',[True,3],2),('focus',[],2),('focus',[1],0),('focus',[1],11)]:
            with self.subTest(axis=axis,levels=levels,repeats=repeats),self.assertRaises(ValueError):
                campaign_plan(axis,levels,repeats)

    def test_report_retains_failed_cost_and_excludes_blocked_from_success_denominator(self):
        plan=campaign_plan('verify',[1,3],2)
        usage={'input_tokens':100,'cached_input_tokens':80,'output_tokens':10}
        rows=[{'trial':1,'profile':'verify-1','status':'FAIL','usage':usage},
              {'trial':2,'profile':'verify-3','status':'BLOCKED_ENVIRONMENT','usage':None}]
        report=summarize_campaign(plan,rows)
        low=report['groups']['verify-1'];balanced=report['groups']['verify-3']
        self.assertEqual(report['not_run'],2)
        self.assertEqual(low['success_rate'],0)
        self.assertEqual(low['mean_total_tokens'],110)
        self.assertEqual(low['mean_uncached_input_tokens'],20)
        self.assertIsNone(balanced['success_rate'])
        self.assertIsNone(balanced['mean_total_tokens'])
        self.assertEqual(balanced['usage_missing'],1)

    def test_duplicate_mislabeled_and_impossible_usage_results_fail(self):
        plan=campaign_plan()
        row={'trial':1,'profile':'low','status':'PASS','usage':None}
        for rows in ([row,row],[dict(row,profile='high')],[dict(row,trial=True)],
                     [dict(row,usage={'input_tokens':1,'cached_input_tokens':2,'output_tokens':0})]):
            with self.subTest(rows=rows),self.assertRaises(ValueError): summarize_campaign(plan,rows)
        self.assertEqual(summarize_campaign(plan,[])['status'],'NOT_RUN')

    def test_claimed_single_axis_design_cannot_change_other_axes(self):
        plan=campaign_plan('focus',[1,5],1)
        plan['profiles']['focus-1']='focus=1,verify=5'
        with self.assertRaises(ValueError): summarize_campaign(plan,[])
        for results in (None,'results',[False]):
            with self.subTest(results=results),self.assertRaises(ValueError):
                summarize_campaign(campaign_plan(),results)

    def test_tool_errors_are_retained_even_when_acceptance_passed(self):
        row={'trial':1,'profile':'low','status':'PASS','usage':None,
             'actions':[{'type':'command_execution','exit_code':1}]}
        report=summarize_campaign(campaign_plan(),[row])
        self.assertEqual(report['groups']['low']['counts']['PASS'],1)
        self.assertEqual(report['groups']['low']['tool_command_failures'],1)

    def test_legacy_composite_protocol_stays_readable(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory);plan=campaign_plan()
            (folder/'protocol.json').write_text(json.dumps({'order':plan['order'],'profiles':plan['profiles']}))
            (folder/'results.json').write_text('[]')
            result=subprocess.run([sys.executable,str(ROOT/'scripts/effort_campaign.py'),'--report',str(folder)],
                                  capture_output=True,text=True,timeout=10)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(json.loads(result.stdout)['design'],'legacy-composite')

    def test_cli_dry_plan_never_invokes_model_or_creates_output(self):
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)/'never-created'
            result=subprocess.run([sys.executable,str(ROOT/'scripts/evaluate_effort.py'),
                '--axis','batch','--levels','1','3','5','--repeats','2','--plan',
                '--cli','definitely-not-a-real-command','--output',str(output)],
                capture_output=True,text=True,timeout=10)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(json.loads(result.stdout)['planned_trials'],6)
            self.assertFalse(output.exists())

    def test_read_only_report_cli_uses_saved_design(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory);plan=campaign_plan('focus',[1,5],1)
            (folder/'protocol.json').write_text(json.dumps({'campaign':plan}))
            (folder/'results.json').write_text('[]')
            before={p.name:p.read_bytes() for p in folder.iterdir()}
            result=subprocess.run([sys.executable,str(ROOT/'scripts/effort_campaign.py'),
                '--report',str(folder)],capture_output=True,text=True,timeout=10)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(json.loads(result.stdout)['not_run'],2)
            self.assertEqual(before,{p.name:p.read_bytes() for p in folder.iterdir()})
