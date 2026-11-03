"""Import read-only historical campaign snapshots into portable observations.

python -m scripts.evaluation.copilot_audit --source-root PRIVATE --output NEW
Raw code is not executed in its original workspace. Only frozen cents checks
run against source-only disposable copies. Revision regrades remain historical.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import tempfile
from .acceptance import check_candidate
from .cases import load_case
from .control import parse_usage

DATASETS = ('agent-attention-copilot-cli-20261102', 'combined-campaign-20261102',
            'attention-grid-20261103')


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def import_campaigns(source, output):
    source, output = Path(source), Path(output)
    output.mkdir(parents=True, exist_ok=False)
    pins, observations = {}, []
    for name in ('run_attention_copilot.py','run_combined_campaign.py','run_attention_grid.py'):
        if (source/name).exists():pins[name]=sha(source/name)
    case = load_case('cents')
    for dataset in DATASETS:
        root = source/dataset
        for name in ('protocol.json', 'observations.json', 'observations-regraded.json'):
            if (root/name).exists(): pins[dataset+'/'+name] = sha(root/name)
        rows = json.loads((root/'observations.json').read_text(encoding='utf-8'))
        regraded = json.loads((root/'observations-regraded.json').read_text()) if (root/'observations-regraded.json').exists() else None
        for index, row in enumerate(rows):
            case_id = row.get('case', 'cents')
            if 'levels' in row:
                relative = case_id+'/'+'-'.join(map(str, row['levels']))+'/'+row['arm']
            else:
                relative = (case_id+'-' if dataset.startswith('combined') else '')+f"rep-{row['rep']:02d}-{row['arm']}"
            folder = root/relative
            calls = row.get('calls', [row.get('call')])
            tool_starts, quota, skills = 0, False, set()
            raw_pins = {}; models=set()
            for path in folder.rglob('usage.json'):
                raw_pins[path.relative_to(folder).as_posix()] = sha(path)
                model=json.loads(path.read_text(encoding='utf-8')).get('currentModel')
                if model:models.add(model)
            for path in folder.rglob('events.jsonl'):
                raw_pins[path.relative_to(folder).as_posix()] = sha(path)
                for line in path.read_text(encoding='utf-8').splitlines():
                    try: event = json.loads(line)
                    except ValueError: continue
                    tool_starts += event.get('type') == 'tool.execution_start'
                    if event.get('type') in ('session.error', 'error'):
                        quota |= 'quota' in json.dumps(event.get('data', event)).casefold()
                    if event.get('type') == 'session.skills_loaded':
                        skills.update(s.get('source','unknown') for s in event.get('data',{}).get('skills',[]))
            functional = None
            if case_id == 'cents':
                with tempfile.TemporaryDirectory(dir=output) as tmp:
                    process, error, mutations = check_candidate(folder/'workspace', case, Path(tmp))
                    functional = process.returncode == 0 and error is None and not mutations
            old_accept = row.get('acceptance', {})
            normalized_calls = []
            for call in calls:
                normalized_calls.append({'seconds':call['seconds'], 'returncode':call['returncode'],
                                         'usage':parse_usage(call.get('usage'))})
            observations.append({'dataset':dataset, 'index':index+1, 'case':case_id,
                'arm':row['arm'], 'rep':row.get('rep'), 'levels':row.get('levels'),
                'original_status':row['status'], 'calls':normalized_calls,
                'original_checks_exit':old_accept.get('check_exit'),
                'original_protected_ok':old_accept.get('protected_ok'),
                'original_reference_match':old_accept.get('reference_match'),
                'functional_cents':functional,
                'stored_regraded_status':regraded[index]['status'] if regraded else None,
                'stored_independent_acceptance':regraded[index].get('independent_acceptance') if regraded else None,
                'revision_semantics':'HISTORICAL_NOT_REVALIDATED' if case_id=='revision' else None,
                'policy':'NOT_VERIFIED: no external-effects sandbox attestation',
                'skill_integrity':'NOT_VERIFIED: historical scope excluded skill payload',
                'tool_starts':tool_starts, 'quota_event':quota,
                'reported_models':sorted(models),
                'discovery_sources':sorted(skills), 'raw_sha256':raw_pins})
    value={'schema':1, 'kind':'HISTORICAL_REAUDIT', 'source_sha256':pins,
           'functional_oracle_case_sha256':sha(Path(__file__).resolve().parents[2]/'benchmarks/cases/cents.json'),
           'observations':observations}
    (output/'historical.json').write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n')
    return value


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-root',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args(); data=import_campaigns(a.source_root,a.output)
    print(dict(Counter(r['dataset'] for r in data['observations'])))
