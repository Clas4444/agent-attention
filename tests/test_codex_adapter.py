import json
from pathlib import Path
import tempfile
import unittest
from scripts.evaluation.codex_adapter import inventory,arguments,freeze
from scripts.evaluation.control import failure_reason


class CodexAdapterTests(unittest.TestCase):
    def test_alias_inventory_requires_exact_candidate_and_neutral_baseline(self):
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw)
            candidate=root/'.agents/skills'
            text='- `r0` = `'+candidate.as_posix()+'`\n(file: r0/agent-attention/SKILL.md)'
            prompt=[{'content':[{'text':text}]}]
            self.assertEqual(inventory(prompt,root,'attention')['status'],'PASS')
            self.assertEqual(inventory(prompt,root,'baseline')['status'],'BLOCKED')
            self.assertEqual(inventory([{'content':[{'text':'neutral'}]}],root,'baseline')['status'],'PASS')

    def test_auth_root_cause_precedes_missing_usage(self):
        self.assertEqual(failure_reason([],'Error: No authentication information found.'),'AUTH_FAILURE')
        self.assertIsNone(failure_reason([{'type':'item.completed','item':{'type':'agent_message',
                           'text':'No authentication information found.'}}],''))

    def test_failed_preflight_never_freezes_or_calls(self):
        with tempfile.TemporaryDirectory() as raw:
            with self.assertRaisesRegex(ValueError,'BLOCKED'):freeze(Path(raw)/'out','fake',[],{'status':'BLOCKED'})
            self.assertEqual(list(Path(raw).iterdir()),[])

    def test_supported_host_auth_uses_no_credential_or_home_override(self):
        flags=arguments(['opaque/example/SKILL.md'])
        text=' '.join(flags)
        self.assertNotIn('auth.json',text)
        self.assertNotIn('CODEX_HOME',text)
        self.assertNotIn('--model',text)
        for feature in ('apps','plugins','memories','multi_agent'):self.assertIn(feature,flags)
