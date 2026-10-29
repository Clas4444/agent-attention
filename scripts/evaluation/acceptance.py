"""Check exact fixture scope, then run frozen checks in a fresh source-only copy.

This catches accidental/fixture-level bypasses, not arbitrary hostile Python.
It is an acceptance oracle, not an operating-system sandbox.
"""
from pathlib import Path
import hashlib
import shutil
import stat
import subprocess
import sys
import tempfile
import uuid


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def changes(folder, pins, allowed):
    """Reject protected changes, aliases and extra source files; ignore Git/cache."""
    problems = []
    for name, expected in pins.items():
        path = folder/name
        try:
            meta = path.lstat()
            if (not stat.S_ISREG(meta.st_mode) or meta.st_nlink != 1
                    or getattr(meta, 'st_file_attributes', 0) & 0x400):
                problems.append(name)
            elif name not in allowed and digest(path) != expected:
                problems.append(name)
        except OSError:
            problems.append(name)
    for path in folder.rglob('*'):
        relative = path.relative_to(folder)
        if '.git' in relative.parts:
            continue
        meta = path.lstat()
        if stat.S_ISLNK(meta.st_mode) or getattr(meta, 'st_file_attributes', 0) & 0x400:
            problems.append(relative.as_posix())
        elif path.is_file() and relative.as_posix() not in pins:
            if not ('__pycache__' in relative.parts[:-1] and path.suffix == '.pyc'):
                problems.append(relative.as_posix())
    return sorted(set(problems))


def check_candidate(workspace, case, trial_folder):
    """Return raw process result, completion error, and oracle-side mutations."""
    with tempfile.TemporaryDirectory(prefix='oracle-', dir=trial_folder) as raw:
        oracle = Path(raw)
        for name, source in case['files'].items():
            if name in case['allowed_edits']:
                shutil.copyfile(workspace/name, oracle/name)
            else:
                (oracle/name).write_text(source, encoding='utf-8', newline='\n')
        pins = {name: digest(oracle/name) for name in case['files']}
        marker = 'ATTENTION_ORACLE_COMPLETE_' + uuid.uuid4().hex
        script = ("import runpy,sys; sys.path.insert(0,'.'); "
                  "runpy.run_path('checks.py',run_name='__main__'); print("+repr(marker)+")")
        process = subprocess.run([sys.executable, '-I', '-B', '-c', script], cwd=oracle,
                                 capture_output=True, text=True, timeout=15)
        # Zero exit alone is insufficient: imported code can call sys.exit(0).
        complete = process.stdout.splitlines()[-1:] == [marker]
        error = None if complete else 'OracleIncomplete'
        return process, error, changes(oracle, pins, ())
