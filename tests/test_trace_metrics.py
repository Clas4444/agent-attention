import unittest
from scripts.evaluation.trace_metrics import successful_mandatory_check


class TraceMetricTests(unittest.TestCase):
    def test_read_echo_and_self_report_are_not_execution(self):
        for command in ('Get-Content checks.py','echo "python checks.py"',
                        'python -c "print(\'python checks.py\')"'):
            self.assertFalse(successful_mandatory_check([{'type':'command_execution','exit_code':0,'command':command}]))
    def test_actual_successful_python_invocations(self):
        for command in ('python -B checks.py','py -3 -B checks.py',
                        '"pwsh.exe" -Command \'Get-Content graph.py; python -B checks.py\''):
            self.assertTrue(successful_mandatory_check([{'type':'command_execution','exit_code':0,'command':command}]))
        self.assertFalse(successful_mandatory_check([{'type':'command_execution','exit_code':1,'command':'python checks.py'}]))
