"""Verify sanitized delivery packet bytes and distinguish stale source receipts."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[2]


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def check(directory,write=False):
    directory=Path(directory).resolve()
    files={p.relative_to(directory).as_posix():digest(p) for p in sorted(directory.rglob('*'))
           if p.is_file() and p.name!='sha256.json'}
    receipt=directory/'sha256.json'
    if write:
        paths=[*ROOT.joinpath('scripts').rglob('*.py'),*ROOT.joinpath('tests').rglob('*.py'),
               *ROOT.joinpath('skills').rglob('SKILL.md'),ROOT/'README.md',
               ROOT/'docs/guides/attention-profiles.md',ROOT/'docs/guides/attention-setup.md']
        sources={p.relative_to(ROOT).as_posix():digest(p) for p in sorted(paths)}
        receipt.write_text(json.dumps({'schema':1,'artifacts':files,'publication_sources':sources},indent=2)+'\n',encoding='utf-8',newline='\n')
    saved=json.loads(receipt.read_text(encoding='utf-8'))
    if files!=saved['artifacts']:raise ValueError('delivery artifact byte mismatch')
    stale=[p for p,h in saved['publication_sources'].items() if not (ROOT/p).is_file() or digest(ROOT/p)!=h]
    for row in json.loads((directory/'snapshot-index.json').read_text())['snapshots']:
        archive=directory/row['archive']
        if digest(archive)!=row['sha256']:raise ValueError('measured archive mismatch')
        with zipfile.ZipFile(archive) as z:
            if len(z.namelist())!=len(set(z.namelist())) or set(z.namelist())!=set(row['source_pins']):
                raise ValueError('measured archive member mismatch')
            for name,h in row['source_pins'].items():
                if hashlib.sha256(z.read(name)).hexdigest()!=h:raise ValueError('measured source mismatch')
    return {'artifact_status':'PASS','artifacts':len(files),'measured_sources':'PASS',
            'publication_source_status':'STALE' if stale else 'PASS','stale_source_paths':stale}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--directory',type=Path,required=True);p.add_argument('--write',action='store_true')
    a=p.parse_args();print(json.dumps(check(a.directory,a.write),indent=2))
