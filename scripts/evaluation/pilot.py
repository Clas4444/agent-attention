"""Freeze/run a bounded Copilot single-axis pilot; never run in CI.

Use --freeze before --run. Each CLI call counts, even startup/auth failures.
No credential copying or automatic retries. A pre-existing shared marker stops
all calls. Local private output must be NEW and is never a publication source.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from .paired import design, prompt
from .cases import ROOT, load_case
from .acceptance import changes, check_candidate
from .control import classify, execute_plan, failure_reason, parse_usage


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,value): path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n')


def freeze(output, command, marker):
    output=Path(output).resolve();output.mkdir(parents=True,exist_ok=False)
    files=[*sorted((ROOT/'scripts/evaluation').glob('*.py')),
           *sorted((ROOT/'skills/agent-attention').rglob('*')),
           ROOT/'benchmarks/cases/dependencies.json',ROOT/'benchmarks/cases/cents.json']
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in files if p.is_file() and '__pycache__' not in p.parts}
    protocol={'schema':1,'frozen_at':datetime.now(timezone.utc).isoformat(),
       'hypothesis':'Single-axis extremes may change discretionary work; correctness and integrity must remain.',
       'seed':20261103,'plan':design(),'cli_limit':24,'per_call_seconds':180,
       'command':command,'marker':str(marker),'pins':pins,
       'model':'configured default, no model/effort override; actual reported model recorded',
       'isolation':'New COPILOT_HOME and Git workspace per CLI; no credentials copied; trace discovery required.',
       'primary':['frozen functional oracle','protected input integrity','total input+output tokens'],
       'secondary':['wall seconds','tool starts','read/edit/check observations'],
       'stop':'first quota/rate/capacity/auth, malformed/missing usage, CLI prerequisite or discovery leak; shared exclusive marker',
       'resume':'append-only reservations/results; no auto retry, no marker removal',
       'limits':'n=1 per cell, descriptive only; concurrent other-chat pilot confounds timing; not a full factorial',
       'oracle':'fresh source-only frozen checks, completion marker, no protected/extra/alias files',
       'argv_flags':['--no-custom-instructions','--no-ask-user','--no-auto-update','--sync-session=off',
         '--disable-builtin-mcps','--no-color','--output-format','json','--stream','off','--allow-all-tools',
         '--excluded-tools','task','web_fetch','web_search']}
    save(output/'protocol-private.json',protocol)
    # Public frozen copy omits private CLI paths; hashes still identify runtime.
    public=dict(protocol);public.pop('marker');public.pop('command')
    public['runtime_sha256']={str(i):sha(Path(p)) for i,p in enumerate(command) if Path(p).is_file()}
    save(output/'protocol.json',public)
    return protocol


def run(output):
    output=Path(output).resolve();protocol=json.loads((output/'protocol-private.json').read_text())
    for name,digest in protocol['pins'].items():
        if sha(ROOT/name)!=digest: raise ValueError('frozen source changed: '+name)
    def invoke(row):
        folder=output/row['id'];folder.mkdir(exist_ok=False)
        work=folder/'workspace';work.mkdir();home=folder/'home';home.mkdir()
        case=load_case(row['case']);case=json.loads(json.dumps(case))
        # Both arms have the same neutral fixture instructions, without treatment cues.
        case['files']['AGENTS.md']='Only edit the authorized source files. FLOW.md is authoritative. No network or external actions. Run python -B checks.py.\n'
        for name,content in case['files'].items(): (work/name).write_text(content,encoding='utf-8',newline='\n')
        if row['arm']=='attention': shutil.copytree(ROOT/'skills/agent-attention',work/'.agents/skills/agent-attention',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        subprocess.run(['git','init','-q',str(work)],check=True,capture_output=True)
        pins={p.relative_to(work).as_posix():sha(p) for p in work.rglob('*') if p.is_file() and '.git' not in p.parts}
        save(folder/'pins.json',pins)
        task=prompt(case,row);(folder/'prompt.txt').write_text(task,encoding='utf-8',newline='\n')
        env=os.environ.copy();env['COPILOT_HOME']=str(home);env['USE_TGREP']='false'
        usage_path=folder/'usage.json'
        command=protocol['command']+['--prompt',task,'-C',str(work),'--usage-output-file',str(usage_path),*protocol['argv_flags']]
        start=time.monotonic();started=datetime.now(timezone.utc).isoformat()
        try:
            proc=subprocess.run(command,cwd=work,env=env,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=protocol['per_call_seconds'])
            code,out,err=proc.returncode,proc.stdout,proc.stderr
        except (OSError,subprocess.TimeoutExpired) as error:
            code=None;out=getattr(error,'stdout','') or '';err=type(error).__name__
            if isinstance(out,bytes):out=out.decode('utf-8',errors='replace')
        (folder/'events.jsonl').write_text(out,encoding='utf-8',newline='\n');(folder/'stderr.log').write_text(err,encoding='utf-8',newline='\n')
        elapsed=time.monotonic()-start
        events=[]
        for line in out.splitlines():
            try: value=json.loads(line)
            except ValueError:continue
            if isinstance(value,dict):events.append(value)
        observed_skills=[s for e in events if e.get('type')=='session.skills_loaded' for s in e.get('data',{}).get('skills',[])]
        leaked=any(s.get('source')!='builtin' and not
          (row['arm']=='attention' and s.get('source')=='project' and s.get('name')=='agent-attention') for s in observed_skills)
        builtin=any(s.get('source')=='builtin' for s in observed_skills)
        usage=None;usage_error=None;model=None
        try:
            raw=json.loads(usage_path.read_text()) if usage_path.exists() else None
            if raw:
                model=raw.get('currentModel')
                u=raw.get('modelMetrics',{}).get(model,{}).get('usage',{})
                usage=parse_usage({'input_tokens':u.get('inputTokens'),'output_tokens':u.get('outputTokens'),
                    'cached_input_tokens':u.get('cacheReadTokens'),'cache_write_tokens':u.get('cacheWriteTokens'),
                    'premium_requests':raw.get('totalPremiumRequestCost'),'api_duration_ms':raw.get('totalApiDurationMs')})
        except (ValueError,TypeError):usage_error='MALFORMED_USAGE'
        protected=changes(work,pins,case['allowed_edits'])
        edited=any(sha(work/n)!=pins[n] if (work/n).is_file() else True for n in case['allowed_edits'])
        accepted=False;oracle_error=None
        if not protected:
            proc,error,mutations=check_candidate(work,case,folder)
            accepted=proc.returncode==0 and error is None and not mutations
            oracle_error=error
        reason=failure_reason(events,err)
        if reason is None and not usage:reason=usage_error or 'USAGE_UNAVAILABLE'
        if reason is None and code is None:reason='CLI_PREREQUISITE'
        if reason is None and (leaked or not any(e.get('type')=='session.skills_loaded' for e in events)):
            reason='DISCOVERY_NOT_VERIFIED'
        # Builtins are common host tooling, documented, not the treatment skill.
        status=classify(code,events,err,accepted and not protected and not leaked,edited or bool(protected))
        if not events and code!=0 and not edited:status='BLOCKED_ENVIRONMENT'
        if reason and status=='PASS':status='FAIL'
        tool_events=[e for e in events if e.get('type')=='tool.execution_start']
        tools=[e.get('data',{}).get('toolName','unknown') for e in tool_events]
        return {**row,'status':status,'stop_reason':reason,'functional':accepted,
          'integrity':'PASS' if not protected else 'FAIL','policy':'NOT_VERIFIED: no OS external-effects attestation',
          'protected_changes':protected,'oracle_error':oracle_error,'usage':usage,'actual_model':model,
          'exit_code':code,'seconds':elapsed,'started_at':started,'tool_starts':len(tool_events),
          'tool_names':tools,'discovery':{'observed':bool(observed_skills),'foreign_skill':leaked,'builtin_skills':builtin},
          'trace_sha256':sha(folder/'events.jsonl'),'prompt_sha256':sha(folder/'prompt.txt')}
    result=execute_plan(protocol['plan'],output/'attempts.jsonl',Path(protocol['marker']),invoke,protocol['cli_limit'])
    save(output/'outcomes.json',result);print(json.dumps({'attempts':len(result['attempts']),'not_run':len(result['not_run'])}))
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--marker',type=Path)
    p.add_argument('--command',nargs='+');p.add_argument('--freeze',action='store_true');p.add_argument('--run',action='store_true')
    a=p.parse_args()
    if a.freeze:
        if not a.command or not a.marker:p.error('--freeze requires --command and --marker')
        freeze(a.output,a.command,a.marker)
    elif a.run:run(a.output)
    else:p.error('choose --freeze or --run')
