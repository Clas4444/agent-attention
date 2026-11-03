"""Conservative command evidence; a filename mention is not test execution."""
import re


def task_status(returncode,completed,functional,protected,mandatory,reason,started):
    """Required trace checks and transport/accounting faults cannot earn PASS."""
    if reason and not started and not protected and not completed:
        return 'BLOCKED_ENVIRONMENT'
    return 'PASS' if (returncode==0 and completed and functional and not protected
                      and mandatory and reason is None) else 'FAIL'


def successful_mandatory_check(actions):
    invocation=re.compile(r'''(?:^|[;\n])\s*(?:&\s*)?(?:python(?:[0-9.]+)?(?:\.exe)?|py(?:\.exe)?)['"]?(?:\s+(?:-[IB]|-3))*\s+['"]?(?:\./)?checks\.py\b''',re.I)
    for action in actions:
        if action.get('type')!='command_execution' or action.get('exit_code')!=0:continue
        command=action.get('command','')
        # Unwrap the observed shell command, never evaluate its contents.
        shell=re.search(r'''\s(?:-Command|-lc|-c)\s+['"]''',command)
        if shell:command=command[shell.end():]
        if invocation.search(command.lstrip(" '\"")):return True
    return False
