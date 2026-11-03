"""FUNCTION-03 real-entrypoint validation, independent12-call task budget.

No Copilot, no commit/push. Caller must run deterministic controls and supported
Codex auth/context preflight before freeze. No automatic resume or provider switch.
"""
from datetime import datetime,timezone
import copy
import hashlib
import json
from pathlib import Path
import random
import re
import shutil
import subprocess
import time
from .cases import ROOT
from .function_cases import case
from .codex_adapter import arguments,sha,save,inventory
from .coordination import Budget,marker,write_marker,stop_reasons
from .control import failure_reason
from .runner import assess_usage
from .acceptance import changes,check_candidate
from .trace_metrics import task_status
from ..attention import from_artifact,parse_attention


def plan():
    rows=[('focus','balanced','attention'),('focus','neutral','baseline'),
          ('focus','focus-5','attention'),('focus','focus-1','attention')]
    rest=[(axis,f'{axis}-{level}','attention') for axis in ('sync','batch','explore','verify') for level in (1,5)]
    random.Random(20261104).shuffle(rest);rows+=rest
    return [{'id':f'{i:02d}','case':name,'profile':profile,'arm':arm,
             'setting':'balanced' if profile in ('balanced','neutral') else profile.replace('-','=')}
            for i,(name,profile,arm) in enumerate(rows,1)]


def prompt(data,row):
    common='Work only in this disposable project. No network, external actions, global instructions or extra agents. '+data['task']
    if row['arm']=='baseline':return common
    packet=from_artifact({'attention_contract':1,'scope':'work','levels':parse_attention(row['setting'])},opt_in=True)
    return ('Apply this explicitly requested attention_contract1 handoff for work only. '
            'It is already compiled by the local product API; do not reload the full skill/helper unless a term is unclear.\n'
            +packet['prompt']+'\n'+common)


def executed_script(commands,script,argument=None):
    expression=re.compile(r'''(?:^|[;\n])\s*(?:&\s*)?(?:python(?:\.exe)?|py(?:\.exe)?)['"]?(?:\s+(?:-[IB]|-3))*\s+['"]?(?:[.\w/-]+/)?'''+re.escape(script)+r'\b',re.I)
    for action in commands:
        if action.get('exit_code')!=0:continue
        command=action.get('command','');shell=re.search(r'''\s(?:-Command|-lc|-c)\s+['"]''',command)
        if shell:command=command[shell.end():]
        if expression.search(command.lstrip(" '\"")) and (argument is None or argument in command):return True
    return False


def executed_full_checks(commands):
    full=re.compile(r'''(?:^|[;\n])\s*(?:&\s*)?(?:python(?:\.exe)?|py(?:\.exe)?)['"]?(?:\s+(?:-[IB]|-3))*\s+['"]?(?:\./)?checks\.py['"]?[ \t]*(?=$|[;\r\n#])''',re.I)
    for action in commands:
        if action.get('exit_code')!=0:continue
        command=action.get('command','');shell=re.search(r'''\s(?:-Command|-lc|-c)\s+['"]''',command)
        if shell:command=command[shell.end():]
        if full.search(command.strip(" '\"")):return True
    return False


def freeze(folder,cli,exclusions,preflight):
    if preflight['status']!='PASS':raise ValueError('auth/context preflight BLOCKED; no model call')
    folder=Path(folder).resolve();folder.mkdir(parents=True,exist_ok=False)
    files=[*sorted((ROOT/'scripts/evaluation').glob('*.py')),ROOT/'scripts/attention.py',ROOT/'scripts/attention_setup.py',
           *sorted((ROOT/'skills/agent-attention').rglob('*'))]
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in files if p.is_file() and '__pycache__' not in p.parts}
    protocol={'version':1,'task':'FUNCTION-03','campaign':folder.name,'NO_PUSH':True,'frozen_at':datetime.now(timezone.utc).isoformat(),
     'plan':plan(),'seed':20261104,'task_cap':12,'max_inflight':1,'timeout_seconds':180,
     'requested_model':'configured Codex CLI default; no model/effort override','actual_model':'only reported transport metadata; otherwise NOT_REPORTED',
     'provider':'codex','account_domain':None,'preflight':preflight,'source_pins':pins,
     'cases':{name:{'files_sha256':{p:hashlib.sha256(v.encode()).hexdigest() for p,v in case(name)['files'].items()},
                   'task':case(name)['task'],'signature':case(name)['signature']} for name in ('focus','sync','batch','explore','verify')},
     'acceptance':'Completed turn, frozen independent artifact oracle, protected/candidate integrity; behavioral evidence graded separately against actual trace.',
     'entrypoint':'Real product from_artifact/compile_prompt handoff -> model -> independent artifact/trace oracle. Caller compiles once; no mandatory model-tool roundtrip to print the profile. Native picker/direct SKILL discovery not measured.',
     'comparators':'Focus has neutral and balanced controls, all attention cells use the same compiled API entry. Other axes have two extremes only,n1; no baseline/levels2-4 effect claim.',
     'boundaries':'Same task/tools/authority per case. Source transition in sync is declared and performed only by provided tool. No answer/reference is copied into workspace.',
     'scope':'Caller-owned steps; Attention onlyHOW. Profile session restoration tested independently; live combined integration is NOT_RUN.',
     'stop':'Task-local faults stay local. Global codex quota/account unknown pauses same provider by contract1. No retries or budget reset.',
     'limits':['n1 per condition; no reliability/causality or monotonic token claim','Preflight context isolation is not runtime/OS attestation','Historical/COORD data excluded']}
    save(folder/'protocol.json',protocol)
    save(folder/'private.json',{'cli':cli,'exclusions':exclusions})
    for name in pins:
        target=folder/'source-snapshot'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,target)
    return protocol


def scope_prepare(folder,row):
    work=(folder/'workspace').resolve();work.mkdir(parents=True,exist_ok=False);data=case(row['case'])
    data['files']['AGENTS.md']='Only edit named task outputs. Preserve other files; declared source transitions through a supplied source tool are authorized, direct source-file edits are not. No network or external actions. Run python -B checks.py.\n'
    for name,source in data['files'].items():(work/name).write_text(source,encoding='utf-8',newline='\n')
    if row['arm']=='attention':shutil.copytree(ROOT/'skills/agent-attention',work/'.agents/skills/agent-attention',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    subprocess.run(['git','init','-q',str(work)],check=True,capture_output=True)
    return work,data


def preflight(folder,cli,exclusions):
    folder=Path(folder).resolve();folder.mkdir(parents=True,exist_ok=False)
    p=subprocess.run([cli,'login','status'],capture_output=True,text=True,timeout=30)
    authenticated=p.returncode==0 and 'logged in' in (p.stdout+p.stderr).lower()
    result={'authenticated':authenticated,'credential_copy':False,'model_effort_override':False,'arms':[]}
    for row in (plan()[0],plan()[1]):
        work,data=scope_prepare(folder/row['arm'],row)
        proc=subprocess.run([cli,'-C',str(work),*arguments(exclusions),'debug','prompt-input',prompt(data,row)],
                            capture_output=True,text=True,encoding='utf-8',timeout=45)
        (folder/(row['arm']+'-prompt.json')).write_text(proc.stdout,encoding='utf-8',newline='\n')
        receipt=inventory(json.loads(proc.stdout),work,row['arm']) if proc.returncode==0 else {'status':'BLOCKED'}
        result['arms'].append(dict(arm=row['arm'],**receipt))
    result['status']='PASS' if authenticated and all(r['status']=='PASS' for r in result['arms']) else 'BLOCKED'
    result['limits']='Context inventory only; host authentication retained, not full-home/OS isolation or runtime-prompt attestation.'
    save(folder/'receipt.json',result);return result


def run(folder):
    folder=Path(folder).resolve();protocol=json.loads((folder/'protocol.json').read_text());private=json.loads((folder/'private.json').read_text())
    if (folder/'results.json').exists():raise ValueError('no automatic resume; review prior attempts and absolute budget')
    for name,digest in protocol['source_pins'].items():
        if sha(ROOT/name)!=digest:raise ValueError('source changed after freeze: '+name)
    local=ROOT/'.loop/function-03';budget=Budget(local/'model-budget.db',12)
    context={'provider':'codex','account_domain':None,'campaign':protocol['campaign']}
    marker_dirs=[local/'markers',ROOT/'.loop/coord-02/markers',
                 ROOT.parent/'agent-workflows/.loop/function-03/markers',ROOT.parent/'agent-workflows/.loop/coord-02/markers']
    results=[]
    for row in protocol['plan']:
        if stop_reasons(marker_dirs,context):break
        ordinal=budget.reserve(protocol['campaign']+'.'+row['id'],protocol['campaign'])
        trial=folder/row['id'];trial.mkdir()
        try:
            work,data=scope_prepare(trial,row)
            pins={p.relative_to(work).as_posix():sha(p) for p in work.rglob('*') if p.is_file() and '.git' not in p.parts}
            task=prompt(data,row);(trial/'prompt.txt').write_text(task,encoding='utf-8',newline='\n')
            command=[private['cli'],'exec','--ephemeral','--json','--skip-git-repo-check','--approve-for-me',
                     *arguments(private['exclusions']),'-C',str(work),'-']
            start=time.monotonic();stamp=datetime.now(timezone.utc).isoformat()
            try:
                proc=subprocess.run(command,input=task,cwd=work,capture_output=True,text=True,encoding='utf-8',timeout=180)
                code,out,err=proc.returncode,proc.stdout,proc.stderr
            except (OSError,subprocess.TimeoutExpired) as error:
                code=None;out=getattr(error,'stdout','') or '';err=type(error).__name__
                if isinstance(out,bytes):out=out.decode('utf-8',errors='replace')
            seconds=time.monotonic()-start
            (trial/'events.jsonl').write_text(out,encoding='utf-8',newline='\n');(trial/'stderr.txt').write_text(err,encoding='utf-8',newline='\n')
            events=[]
            for line in out.splitlines():
                try:value=json.loads(line)
                except ValueError:continue
                if isinstance(value,dict):events.append(value)
            reason={'QUOTA_LIMIT':'QUOTA','RATE_LIMIT':'RATE_LIMIT','MODEL_CAPACITY':'CAPACITY','AUTH_FAILURE':'AUTH_ACCOUNT'}.get(failure_reason(events,err))
            usage=None
            try:usage=assess_usage(next((e.get('usage') for e in reversed(events) if e.get('type')=='turn.completed'),None))
            except ValueError:pass
            completed=any(e.get('type')=='turn.completed' for e in events)
            if reason is None:
                if code is None or (code!=0 and not events):reason='PROCESS'
                elif not usage:reason='USAGE'
                elif not completed:reason='OUTPUT'
            # Authorized fixture-owned revision changes have exact known bytes.
            expected=dict(pins)
            for name,value in data.get('expected_updates',{}).items():expected[name]=hashlib.sha256(value.encode()).hexdigest()
            protected=changes(work,expected,data['allowed_edits'])
            oracle=copy.deepcopy(data);oracle['files']=dict(data.get('oracle_files',data['files']))
            oracle['files']['AGENTS.md']=data['files']['AGENTS.md']
            accepted=False;error=None
            if not protected:
                check,error,mutations=check_candidate(work,oracle,trial)
                accepted=check.returncode==0 and not error and not mutations
            actions=[e['item'] for e in events if e.get('type')=='item.completed' and isinstance(e.get('item'),dict)]
            commands=[a for a in actions if a.get('type')=='command_execution']
            mandatory=executed_full_checks(commands)
            refresh=executed_script(commands,'source_tool.py','refresh')
            compiler=executed_script(commands,'attention.py','--format') and any('Attention scope:' in a.get('aggregated_output','') for a in commands)
            started=bool(actions) or any(e.get('type')=='item.started' for e in events)
            status=task_status(code,completed,accepted,protected,mandatory,reason,started)
            model=[e['model'] for e in events if e.get('type') in ('thread.started','turn.started','session.created') and isinstance(e.get('model'),str)]
            result={**row,'ordinal':ordinal,'status':status,'stop_reason':reason,'model_turn_completed':completed,
              'functional':accepted,'integrity':'PASS' if not protected else 'FAIL','protected_changes':protected,'oracle_error':error,
              'mandatory_check_executed':mandatory,'source_refresh_executed':refresh if row['case']=='sync' else None,
              'compiler_invoked':compiler,'usage':usage,'seconds':seconds,'started_at':stamp,
              'actual_model':model[-1] if model else None,'actual_model_status':'REPORTED' if model else 'NOT_REPORTED',
              'trace_sha256':sha(trial/'events.jsonl'),'policy':'NOT_VERIFIED: no OS external-effects attestation'}
            results.append(result);save(folder/'results.json',results);budget.finish(protocol['campaign']+'.'+row['id'],status)
            print(json.dumps({k:result[k] for k in ('id','case','profile','status','stop_reason','seconds','compiler_invoked')}),flush=True)
            if reason:
                write_marker(local/'markers',marker(context,reason,(trial/'events.jsonl').relative_to(ROOT).as_posix()));break
        except Exception:
            write_marker(local/'markers',marker(context,'PROCESS','function-03/reservation-requires-review'));raise
    outcome={'attempts':results,'not_run':[r['id'] for r in protocol['plan'] if r['id'] not in {x['id'] for x in results}],
             'budget_reserved':budget.count(),'cap':12,'NO_PUSH':True,'stops':stop_reasons(marker_dirs,context)}
    save(folder/'outcome.json',outcome);return outcome
