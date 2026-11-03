"""Pin/verify public report and reproduction bytes; excludes the index itself."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]


def manifest(directory):
    files=[p for p in directory.iterdir() if p.is_file() and p.name!='sha256.json']
    files += [ROOT/'scripts/evaluation'/name for name in
              ('control.py','copilot_audit.py','integrity_report.py','research_figures.py','paired.py','pilot.py','publication.py','render_figures.ps1')]
    files += [ROOT/'tests'/name for name in ('test_campaign_control.py','test_integrity_report.py')]
    files += list((ROOT/'task').glob('*.md'))
    files += [ROOT/name for name in ('CHANGELOG.md','README.md','docs/development/release.md',
                                    'docs/testing/README.md','docs/testing/campaigns.md','docs/testing/results.md')]
    return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}


def check(directory,write=False):
    actual=manifest(directory);index=directory/'sha256.json'
    if write:index.write_text(json.dumps({'schema':1,'sha256':actual},indent=2)+'\n',encoding='utf-8',newline='\n')
    saved=json.loads(index.read_text(encoding='utf-8'))
    if actual!=saved['sha256']:raise ValueError('publication byte hashes differ')
    return len(actual)


def audit_historical(directory):
    """Old source receipts become STALE as development proceeds; data stays pinned.

    Never rewrite the old hash receipt to make a new task pass. Only immutable
    report artifact mismatches fail this historical audit. Changed source/task
    paths are explicitly STALE, not fresh verification of the historical release.
    """
    expected=json.loads((directory/'sha256.json').read_text(encoding='utf-8'))['sha256']
    artifacts=[];stale=[]
    prefix=directory.relative_to(ROOT).as_posix()+'/'
    for name,digest in expected.items():
        path=ROOT/name
        same=path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest()==digest
        if name.startswith(prefix):
            if not same:raise ValueError('historical artifact changed: '+name)
            artifacts.append(name)
        elif not same:stale.append(name)
    return {'artifact_status':'PASS','artifacts':len(artifacts),
            'source_status':'STALE' if stale else 'PASS','stale_source_paths':stale}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--directory',type=Path,required=True);p.add_argument('--write',action='store_true')
    a=p.parse_args();print('PASS:',check(a.directory.resolve(),a.write),'publication hashes')
