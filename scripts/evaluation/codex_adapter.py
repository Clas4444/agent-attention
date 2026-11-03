"""COORD-02 local-only Codex adapter. NO_PUSH; no credential/home copying.

Prepare context/auth preflight and freeze before calling run. All campaigns for
this task share ROOT/.loop/coord-02/model-budget.db, cap24 including failures.
The supported CLI retains host authentication; per-command discovery exclusions
and ephemeral runs isolate candidate/task context, not the OS authentication home.
"""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import time
from .cases import ROOT,load_case
from .acceptance import changes,check_candidate
from .paired import design,prompt
from .runner import assess_usage
from .control import failure_reason
from .coordination import Budget,marker,write_marker,stop_reasons,VERSION
from .trace_metrics import successful_mandatory_check,task_status


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(path,value):Path(path).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n')


def arguments(exclusions):
    config='skills.config=['+','.join('{path='+json.dumps(p)+',enabled=false}' for p in exclusions)+']'
    return ['--disable','apps','--disable','plugins','--disable','memories','--disable','multi_agent','-c',config]


def inventory(value,work,arm):
    text='\n'.join(c.get('text','') for row in value for c in row.get('content',[]) if isinstance(c,dict))
    roots=dict(re.findall(r'- `(r\d+)` = `([^`]+)`',text))
    paths=[]
    for raw in re.findall(r'\(file: ([^\r\n]+)\)',text):
        first,_,tail=raw.partition('/')
        paths.append((Path(roots[first])/tail).resolve() if first in roots else Path(raw).resolve())
    expected=[] if arm=='baseline' else [(work/'.agents/skills/agent-attention/SKILL.md').resolve()]
    leaked=any(s in text for s in ('AgentRepo — local workspace instructions','Agent Attention maintenance','COORD-02'))
    return {'skill_count':len(paths),'candidate_context':paths==expected,
            'parent_context':leaked,'status':'PASS' if paths==expected and not leaked else 'BLOCKED',
            'scope':'model-visible context inventory; authentication home remains host-managed'}


def prepare(folder,row):
    work=(folder/'workspace').resolve();work.mkdir(parents=True,exist_ok=False)
    case=load_case(row['case']);case=json.loads(json.dumps(case))
    case['files']['AGENTS.md']='Only edit the authorized source files. FLOW.md is authoritative. No network or external actions. Run python -B checks.py.\n'
    for name,source in case['files'].items():(work/name).write_text(source,encoding='utf-8',newline='\n')
    if row['arm']=='attention':shutil.copytree(ROOT/'skills/agent-attention',work/'.agents/skills/agent-attention',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    subprocess.run(['git','init','-q',str(work)],check=True,capture_output=True)
    return work,case


def preflight(folder,cli,exclusions):
    folder=Path(folder).resolve();folder.mkdir(parents=True,exist_ok=False)
    status=subprocess.run([cli,'login','status'],capture_output=True,text=True,timeout=30)
    authenticated=status.returncode==0 and 'logged in' in (status.stdout+status.stderr).casefold()
    # Store only boolean/hash, never login cache contents or account identifiers.
    result={'authenticated':authenticated,'auth_status_sha256':hashlib.sha256((status.stdout+status.stderr).encode()).hexdigest(),
            'credential_copy':False,'provider':'codex','account_domain':None,'arms':[]}
    for arm in ('baseline','attention'):
        row={'case':'dependencies','arm':arm,'levels':dict.fromkeys(('focus','sync','batch','explore','verify'),3)}
        work,case=prepare(folder/arm,row)
        proc=subprocess.run([cli,'-C',str(work),*arguments(exclusions),'debug','prompt-input',prompt(case,row)],
                            capture_output=True,text=True,encoding='utf-8',timeout=45)
        (folder/(arm+'-prompt.json')).write_text(proc.stdout,encoding='utf-8',newline='\n')
        if proc.returncode:receipt={'status':'BLOCKED','reason':'debug prompt unavailable'}
        else:receipt=inventory(json.loads(proc.stdout),work,arm)
        result['arms'].append(dict(arm=arm,**receipt))
    result['status']='PASS' if authenticated and all(r['status']=='PASS' for r in result['arms']) else 'BLOCKED'
    result['limitations']=['Shared supported authentication cache; not full-home or OS isolation.',
                          'debug inventory is preflight evidence, not an attestation of the later runtime prompt.',
                          'Account/quota domain unknown; provider stops require identity review.']
    save(folder/'receipt.json',result);return result


SIGNATURES={
 'focus':{'low':'bounded changed component, retain required dependency pointers','high':'authorized end-to-end contract kept in view','tradeoff':'broader context may cost more; narrow scope can miss interactions'},
 'sync':{'low':'reconcile at completion or immediately on shared-contract change','high':'reconcile after consequential shared-state/assumption change','tradeoff':'frequent reconciliation adds overhead; sparse sync risks drift'},
 'batch':{'low':'group straightforward changes, mandatory acceptance retained','high':'reversible dependency steps and intermediate inspection','tradeoff':'more decomposition, not larger batches or guaranteed savings'},
 'explore':{'low':'supplied sources then required dependencies','high':'map relevant authorized flow and conflicting assumptions','tradeoff':'broader discovery costs effort; must return to task'},
 'verify':{'low':'direct result plus mandatory/risk-triggered checks','high':'independent consequential assumptions and boundary checks','tradeoff':'additional checking may be redundant; required checks never removed'}}


def freeze(folder,cli,exclusions,receipt,peer_marker_dirs=(),continuation_from=None):
    if receipt['status']!='PASS':raise ValueError('auth/context preflight prerequisite BLOCKED')
    folder=Path(folder).resolve();folder.mkdir(parents=True,exist_ok=False)
    campaign=folder.name
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in [*sorted((ROOT/'scripts/evaluation').glob('*.py')),
          ROOT/'benchmarks/cases/dependencies.json',ROOT/'benchmarks/cases/cents.json',
          ROOT/'tests/fixtures/coordination-v1.json',
          *sorted((ROOT/'skills/agent-attention').rglob('*'))] if p.is_file() and '__pycache__' not in p.parts}
    public={'version':1,'contract':VERSION,'campaign':campaign,'NO_PUSH':True,'frozen_at':datetime.now(timezone.utc).isoformat(),
       'plan':design(),'seed':20261103,'maximum_task_cli':24,'max_inflight':1,'timeout_seconds':180,
       'hypothesis':'Single-axis low/high may change discretionary behavior/cost; correctness and mandatory checks must remain.',
       'requested_model':'configured CLI default; no model or effort override','actual_model':'record only if transport explicitly reports it',
       'preflight':receipt,'provider':'codex','account_domain':None,'pins':pins,'signatures':SIGNATURES,
       'primary':['frozen functional acceptance','protected/candidate integrity','input+output tokens'],
       'secondary':['CLI wall seconds','read/edit/check/reconcile trace evidence'],
       'rubric':'Task PASS requires completed turn, frozen oracle and integrity; signature observations are descriptive and cannot be inferred from tokens or state-file writes.',
       'stop':'Local fault stops own campaign. QUOTA/RATE_LIMIT/CAPACITY/AUTH_ACCOUNT pauses same-provider matching/unknown domain; no provider switching.',
       'limits':['n=1 per cell; no confidence intervals or causal/general savings claim','Historical66 are separate, confounded focus1 observations','Concurrent peer calls may affect wall time']}
    if continuation_from:
        previous=Path(continuation_from)
        done=json.loads((previous/'results.json').read_text())
        if [r['id'] for r in done]!=[r['id'] for r in public['plan'][:len(done)]]:
            raise ValueError('continuation must preserve the exact preregistered order')
        if any(r.get('stop_reason') in ('QUOTA','RATE_LIMIT','CAPACITY','AUTH_ACCOUNT') for r in done):
            raise ValueError('provider fault cannot be bypassed by a new campaign')
        public['full_original_plan']=public['plan']
        public['plan']=public['plan'][len(done):]
        public['continuation']={'reason':'wire-contract alignment only; no outcome-based selection',
                                'previous_attempts':len(done),'previous_results_sha256':sha(previous/'results.json')}
    for name,digest in pins.items():
        target=folder/'source-snapshot'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,target)
    save(folder/'protocol.json',public)
    save(folder/'private.json',{'cli':cli,'exclusions':exclusions,'peer_markers':[str(Path(p).resolve()) for p in peer_marker_dirs]})
    return public


def run(folder):
    folder=Path(folder).resolve();protocol=json.loads((folder/'protocol.json').read_text());private=json.loads((folder/'private.json').read_text())
    for name,digest in protocol['pins'].items():
        if sha(ROOT/name)!=digest:raise ValueError('frozen source changed; no call: '+name)
    task=ROOT/'.loop/coord-02';budget=Budget(task/'model-budget.db',24)
    context={'provider':protocol['provider'],'account_domain':protocol['account_domain'],'campaign':protocol['campaign']}
    markers=task/'markers';reader=[markers,*private['peer_markers']]
    if (folder/'results.json').exists():raise ValueError('campaign already attempted; no automatic resume')
    rows=[]
    for row in protocol['plan']:
        stops=stop_reasons(reader,context)
        if stops:break
        identifier=protocol['campaign']+'.'+row['id']
        try:ordinal=budget.reserve(identifier,protocol['campaign'])
        except ValueError:break
        trial=folder/row['id'];trial.mkdir()
        try:
            work,case=prepare(trial,row)
            pins={p.relative_to(work).as_posix():sha(p) for p in work.rglob('*') if p.is_file() and '.git' not in p.parts}
            task_prompt=prompt(case,row);(trial/'prompt.txt').write_text(task_prompt,encoding='utf-8',newline='\n')
            command=[private['cli'],'exec','--ephemeral','--json','--skip-git-repo-check','--approve-for-me',
                     *arguments(private['exclusions']),'-C',str(work),'-']
            start=time.monotonic();stamp=datetime.now(timezone.utc).isoformat()
            try:
                proc=subprocess.run(command,input=task_prompt,cwd=work,capture_output=True,text=True,encoding='utf-8',timeout=protocol['timeout_seconds'])
                code,out,err=proc.returncode,proc.stdout,proc.stderr
            except (OSError,subprocess.TimeoutExpired) as error:
                code=None;out=getattr(error,'stdout','') or '';err=type(error).__name__
                if isinstance(out,bytes):out=out.decode('utf-8',errors='replace')
            seconds=time.monotonic()-start
            (trial/'events.jsonl').write_text(out,encoding='utf-8',newline='\n');(trial/'stderr.txt').write_text(err,encoding='utf-8',newline='\n')
            events=[]
            for line in out.splitlines():
                try:event=json.loads(line)
                except ValueError:continue
                if isinstance(event,dict):events.append(event)
            transport=failure_reason(events,err)
            reason={'QUOTA_LIMIT':'QUOTA','RATE_LIMIT':'RATE_LIMIT','MODEL_CAPACITY':'CAPACITY','AUTH_FAILURE':'AUTH_ACCOUNT'}.get(transport)
            usage=None
            try:usage=assess_usage(next((e.get('usage') for e in reversed(events) if e.get('type')=='turn.completed'),None))
            except ValueError:pass
            complete=any(e.get('type')=='turn.completed' for e in events)
            if reason is None:
                if code is None or (code!=0 and not events):reason='PROCESS'
                elif not usage:reason='USAGE'
                elif not complete:reason='OUTPUT'
            protected=changes(work,pins,case['allowed_edits']);accepted=False;oracle_error=None
            if not protected:
                check,error,mutations=check_candidate(work,case,trial)
                accepted=check.returncode==0 and not error and not mutations;oracle_error=error
            actions=[e['item'] for e in events if e.get('type')=='item.completed' and e.get('item',{}).get('type') in ('command_execution','file_change')]
            started_actions=any(e.get('type')=='item.started' and e.get('item',{}).get('type') in ('command_execution','file_change','mcp_tool_call') for e in events)
            status=task_status(code,complete,accepted,protected,successful_mandatory_check(actions),
                               reason,started_actions or bool(actions))
            reported=[e.get('model') for e in events if e.get('type') in ('thread.started','turn.started','session.created') and isinstance(e.get('model'),str)]
            commands=[a.get('command','') for a in actions if a.get('type')=='command_execution']
            result={**row,'ordinal':ordinal,'status':status,'stop_reason':reason,'usage':usage,'seconds':seconds,
                'actual_model':reported[-1] if reported else None,'actual_model_status':'REPORTED' if reported else 'NOT_REPORTED',
                'started_at':stamp,'functional':accepted,'integrity':'PASS' if not protected else 'FAIL','protected_changes':protected,'oracle_error':oracle_error,
                'model_turn_completed':complete,
                'behavior':{'terminal_commands':len(commands),'file_changes':sum(a.get('type')=='file_change' for a in actions),
                 'mandatory_check_command':successful_mandatory_check(actions),
                 'read_commands':sum(any(k in c for k in ('Get-Content','cat ','rg ','read_text')) for c in commands),
                 'independent_assert_command':any('assert ' in c and 'checks.py' not in c for c in commands),
                 'signature_adherence':'NOT_VERIFIED: requires semantic review of read/edit/check/reconciliation traces'},
                'trace_sha256':sha(trial/'events.jsonl'),'policy':'NOT_VERIFIED: no OS external-effects attestation'}
            rows.append(result);save(folder/'results.json',rows);budget.finish(identifier,status)
            print(json.dumps({k:result[k] for k in ('id','profile','arm','status','stop_reason','seconds','actual_model_status')}),flush=True)
            if reason:
                write_marker(markers,marker(context,reason,(trial/'events.jsonl').relative_to(ROOT).as_posix()));break
        except Exception:
            write_marker(markers,marker(context,'PROCESS','coord-02/reserved-attempt-requires-review'))
            raise
    outcome={'campaign':protocol['campaign'],'attempts':rows,'not_run':[r['id'] for r in protocol['plan'] if r['id'] not in {a['id'] for a in rows}],
             'absolute_task_cli_reserved':budget.count(),'NO_PUSH':True,'stops':stop_reasons(reader,context)}
    save(folder/'outcome.json',outcome);return outcome
