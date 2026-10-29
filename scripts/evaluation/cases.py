"""Load versioned, repository-owned benchmark inputs without model calls."""
import json
from pathlib import Path, PurePosixPath
import re

ROOT = Path(__file__).resolve().parents[2]
CASE_IDS = ('cents', 'ledger', 'dependencies')


def load_case(case_id='cents'):
    if case_id not in CASE_IDS:
        raise ValueError('unknown benchmark case')
    path = ROOT/'benchmarks/cases'/f'{case_id}.json'
    case = json.loads(path.read_text(encoding='utf-8'))
    if (case.get('schema') != 1 or case.get('id') != case_id
            or not isinstance(case.get('files'), dict)
            or not isinstance(case.get('task'), str)
            or '{profile}' not in case['task']
            or not isinstance(case.get('allowed_edits'), list)
            or not case['allowed_edits'] or 'checks.py' not in case['files']):
        raise ValueError('malformed benchmark case')
    for name, source in case['files'].items():
        if (not re.fullmatch(r'[A-Za-z0-9_.-]+', name) or name in ('.', '..', '.git')
                or not isinstance(source, str) or str(PurePosixPath(name)) != name):
            raise ValueError('benchmark filenames must be ordinary root files')
    if (len(set(case['allowed_edits'])) != len(case['allowed_edits'])
            or any(name not in case['files'] or name == 'checks.py' for name in case['allowed_edits'])
            or set(case.get('reference', {})) != set(case['allowed_edits'])):
        raise ValueError('benchmark edit/reference contract is inconsistent')
    return case
