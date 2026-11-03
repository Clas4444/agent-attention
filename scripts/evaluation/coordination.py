"""Experiment-only coordination v1. No product routing or peer runtime import."""
from datetime import datetime, timezone
import json
from pathlib import Path,PurePosixPath
import re
import sqlite3
from contextlib import contextmanager

VERSION='coordination-v1'
GLOBAL={'QUOTA','RATE_LIMIT','CAPACITY','AUTH_ACCOUNT'}
LOCAL={'CWD','PROCESS','PARSE','OUTPUT','SCHEMA','FIXTURE','AUTH_HOME','USAGE','UNKNOWN_LOCAL'}


def label(value):
    if not isinstance(value,str) or not re.fullmatch('[a-z0-9][a-z0-9_.-]{0,63}',value):
        raise ValueError('expected opaque nonsecret identifier')


def marker(context,reason,evidence,when=None):
    if reason not in GLOBAL|LOCAL:raise ValueError('unsupported stop reason')
    value={'contract_version':1,'scope':'provider_account' if reason in GLOBAL else 'campaign',
           'provider':context['provider'],'account_domain':context.get('account_domain'),
           'campaign':context['campaign'],'reason':'accounting' if reason=='USAGE' else reason.lower(),
           'evidence':[evidence] if isinstance(evidence,str) else evidence,
           'time':when or datetime.now(timezone.utc).isoformat()}
    validate(value);return value


def validate(value):
    fields={'contract_version','scope','provider','account_domain','campaign','reason','evidence','time'}
    if not isinstance(value,dict) or set(value)!=fields or type(value['contract_version']) is not int or value['contract_version']!=1:
        raise ValueError('unsupported coordination marker version/fields; review required')
    label(value['provider']);label(value['campaign'])
    if value['account_domain'] is not None:label(value['account_domain'])
    if not isinstance(value['reason'],str):raise ValueError('stop reason must be a label')
    if value['reason']!=value['reason'].lower():raise ValueError('wire fault categories must be lowercase')
    reason='USAGE' if value['reason']=='accounting' else value['reason'].upper()
    if value['scope']!=('provider_account' if reason in GLOBAL else 'campaign') or reason not in GLOBAL|LOCAL:
        raise ValueError('stop scope/reason mismatch')
    if not isinstance(value['evidence'],list) or not value['evidence']:
        raise ValueError('nonsecret evidence reference required')
    for item in value['evidence']:
        if (not isinstance(item,str) or not item or ':' in item or '\\' in item or item.startswith('/')
                or '..' in item.split('/') or str(PurePosixPath(item))!=item or any(ord(c)<32 for c in item)):
            raise ValueError('evidence must be portable relative identifiers, never secrets/paths')
    if not isinstance(value['time'],str):raise ValueError('marker time requires ISO8601 text')
    date=datetime.fromisoformat(value['time'].replace('Z','+00:00'))
    if date.tzinfo is None:raise ValueError('marker time requires timezone')


def blocks(value,context):
    """No TTL bypass: identity-unknown provider stops require explicit review."""
    validate(value)
    if value['provider']!=context['provider']:return False
    source,target=value['account_domain'],context.get('account_domain')
    if source is not None and target is not None and source!=target:return False
    if value['scope']=='campaign':return value['campaign']==context['campaign']
    return source is None or target is None or source==target


def diagnostic(value,context,now=None):
    blocked=blocks(value,context)
    if not blocked:return 'OTHER_PROVIDER_DOMAIN_OR_CAMPAIGN'
    date=datetime.fromisoformat(value['time'].replace('Z','+00:00'))
    age=((now or datetime.now(timezone.utc))-date).total_seconds()
    if age<0 or age>86400:return 'STALE_MARKER_REVIEW_REQUIRED'
    if value['scope']=='provider_account' and (value['account_domain'] is None or context.get('account_domain') is None):
        return 'UNKNOWN_ACCOUNT_DOMAIN_PAUSE_PROVIDER'
    return 'MATCHING_SCOPE_STOP'


def write_marker(directory,value):
    validate(value);directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    # Append unique marker bytes atomically, without changing any old marker.
    import uuid,os
    temp=directory/('.'+uuid.uuid4().hex+'.tmp')
    final=directory/(uuid.uuid4().hex+'.json')
    try:
        with temp.open('x',encoding='utf-8',newline='\n') as stream:
            json.dump(value,stream,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
        os.replace(temp,final)
    finally:
        if temp.exists():temp.unlink()
    return final


def stop_reasons(directories,context):
    reasons=[]
    for directory in directories:
        if not Path(directory).exists():continue
        for path in sorted(Path(directory).glob('*.json')):
            value=json.loads(path.read_text(encoding='utf-8'))
            if not isinstance(value,dict):raise ValueError('unsupported marker object; campaign-local review required')
            legacy=False
            if value.get('version')==VERSION:
                # Explicit compatibility for our first, local-only draft marker.
                # Original bytes remain untouched; normalization is reported.
                import hashlib
                if set(value)!={'version','scope','provider','account_domain','campaign','reason','evidence','time'}:
                    raise ValueError('unsupported legacy marker fields; review required')
                legacy=True
                value=marker({'provider':'codex' if value['provider']=='openai' else value['provider'],
                    'account_domain':value['account_domain'],'campaign':value['campaign']},
                    value['reason'],'legacy/'+hashlib.sha256(path.read_bytes()).hexdigest(),value['time'])
            if blocks(value,context):reasons.append({'reason':value['reason'],'scope':value['scope'],
                 'diagnostic':diagnostic(value,context),
                 'legacy_read_only_normalization':legacy,
                 'identity_unknown':value['scope']=='provider_account' and (value['account_domain'] is None or context.get('account_domain') is None)})
    return reasons


class Budget:
    """SQLite transactions enforce cap and max1inflight across processes.

    Persistent pending reservations intentionally block further calls after a
    crash; no automatic expiry, deletion or campaign-ID reset is supported.
    """
    def __init__(self,path,cap=24):
        self.path=Path(path);self.path.parent.mkdir(parents=True,exist_ok=True)
        if type(cap) is not int or cap<1 or cap>24:raise ValueError('cap must be 1..24')
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            db.execute('CREATE TABLE IF NOT EXISTS limits(cap INTEGER NOT NULL)')
            old=db.execute('SELECT cap FROM limits').fetchone()
            if old and old[0]!=cap:raise ValueError('task budget cap cannot be reset')
            if not old:db.execute('INSERT INTO limits VALUES(?)',(cap,))
            db.execute('CREATE TABLE IF NOT EXISTS attempts(id TEXT PRIMARY KEY,campaign TEXT NOT NULL,ended TEXT,result TEXT)')
    @contextmanager
    def connect(self):
        db=sqlite3.connect(self.path,timeout=10)
        try:
            with db:yield db
        finally:db.close()
    def reserve(self,identifier,campaign):
        label(identifier);label(campaign)
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            if db.execute('SELECT 1 FROM attempts WHERE id=?',(identifier,)).fetchone():raise ValueError('attempt already reserved; no automatic retry')
            if db.execute('SELECT 1 FROM attempts WHERE ended IS NULL').fetchone():raise ValueError('inflight or interrupted reservation requires review')
            count=db.execute('SELECT COUNT(*) FROM attempts').fetchone()[0]
            cap=db.execute('SELECT cap FROM limits').fetchone()[0]
            if count>=cap:raise ValueError('absolute task-wide budget exhausted')
            db.execute('INSERT INTO attempts(id,campaign) VALUES(?,?)',(identifier,campaign))
            return count+1
    def finish(self,identifier,result):
        with self.connect() as db:
            cursor=db.execute('UPDATE attempts SET ended=?,result=? WHERE id=? AND ended IS NULL',
                 (datetime.now(timezone.utc).isoformat(),result,identifier))
            if cursor.rowcount!=1:raise ValueError('unknown/already finished reservation')
    def count(self):
        with self.connect() as db:return db.execute('SELECT COUNT(*) FROM attempts').fetchone()[0]
