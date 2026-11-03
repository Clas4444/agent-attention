"""FUNCTION-03 internal product/adherence evidence. No model calls or publication."""
import argparse
import csv
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
from .evaluation.function03 import executed_script,executed_full_checks
from .evaluation.control import parse_usage
from .evaluation.integrity_report import scene,text,line,rect,write_svg


def trace_audit(events,allowed):
    actions=[e['item'] for e in events if e.get('type')=='item.completed' and isinstance(e.get('item'),dict)]
    commands=[a for a in actions if a.get('type')=='command_execution']
    edits=[];read_before=set();related={'amounts.py','checkout.py','invoice.py','app.py'}
    first_edit=None
    for i,a in enumerate(actions):
        c=a.get('command','')
        if a.get('type')=='file_change' or any(t in c for t in ('Set-Content','write_text(')):
            edits.append(i)
            if first_edit is None:first_edit=i
        if first_edit is None and any(t in c for t in ('Get-Content','read_text(','cat ')):
            read_before.update(name for name in related if name in c)
    refresh=next((i for i,a in enumerate(actions) if a.get('type')=='command_execution' and executed_script([a],'source_tool.py','refresh')),None)
    source_reads=sum(len(re.findall(r'''(?:Get-Content|cat)\s+['"]?SOURCE\.json''',a.get('command',''),re.I)) for a in commands)
    subchecks=sum(bool(executed_script([a],'checks.py',mode)) for a in commands for mode in ('net','checkout','invoice'))
    additional=[a for a in commands if 'assert ' in a.get('command','') and re.search(r'\|\s*python(?: -B)? -',a.get('command','')) and a.get('exit_code')==0]
    return {'full_mandatory_check_executed':executed_full_checks(commands),
      'related_sources_before_first_edit':sorted(read_before),'related_source_count':len(read_before),
      'distractor_read_commands':sum(any(name in a.get('command','') for name in ('legacy_billing.py','reporting_archived.py','unrelated_colors.py','legacy_router.py','old_snapshot.md')) for a in commands),
      'edit_events_heuristic':len(edits),'partial_feedback_subchecks':subchecks,
      'source_refresh_executed':refresh is not None,'explicit_source_reads':source_reads,
      'additional_assert_scripts':len(additional),'model_compiler_roundtrip':any('attention.py' in a.get('command','') and 'Attention scope:' in a.get('aggregated_output','') for a in commands),
      'whole_skill_read_observed':any('SKILL.md' in a.get('command','') and a.get('exit_code')==0 for a in commands),
      'note':'Trace evidence is not active-context introspection, authority attestation or universal adherence.'}


def summarize(rows):
    if len({r['id'] for r in rows})!=len(rows):raise ValueError('duplicate invocation')
    for r in rows:
        u=r.get('usage')
        if u is not None:
            parsed=parse_usage(u)
            if u['total_tokens']!=parsed['total_tokens']:raise ValueError('invalid usage')
        if type(r.get('seconds')) not in (int,float) or not math.isfinite(r['seconds']) or r['seconds']<0:
            raise ValueError('invalid elapsed time')
    return {'CLI_attempts':len(rows),'completed_model_turns':sum(r['model_turn_completed'] for r in rows),
      'functional_PASS':sum(r['functional'] for r in rows),'file_integrity_PASS':sum(r['integrity']=='PASS' for r in rows),
      'full_mandatory_checks_audited':sum(r['trace_audit']['full_mandatory_check_executed'] for r in rows),
      'missing_usage':sum(r.get('usage') is None for r in rows),'actual_model_reported':sum(r.get('actual_model') is not None for r in rows),
      'scope':'FUNCTION-03 only; no COORD/historical pooling','n':'one invocation per condition',
      'limits':['No reliability, causal effect or general token-saving claim.','2/4 levels only compiler/unit tested, not model tested.','Compiled API entry measured; native picker/direct skill loading not measured.']}


def figures(rows):
    colors={'neutral':'#94a3b8','balanced':'#16a34a'}
    a=scene('FUNCTION-03: actual cost alongside product acceptance','NEW compiled-API entry | one CLI per condition | input+output total; cache/reasoning not added twice')
    a[0]['color']='#ffffff'
    for x,key,title,step in [(150,'tokens','Total tokens (k)',25000),(650,'seconds','CLI wall seconds',10)]:
        vals=[r['usage']['total_tokens'] if key=='tokens' and r.get('usage') else r['seconds'] if key=='seconds' else 0 for r in rows]
        maximum=max(step,math.ceil(max(vals,default=step)/step)*step)
        for tick in range(0,maximum+1,step):
            px=x+290*tick/maximum;line(a,px,145,px,500,'#e5e7eb');text(a,px-9,523,f'{tick/1000:g}' if key=='tokens' else tick,12)
        text(a,x,126,title,18)
        for i,(r,value) in enumerate(zip(rows,vals)):
            y=158+i*28
            text(a,x-123,y+13,r['profile'],12)
            color=colors.get(r['profile'],'#2563eb' if r['profile'].endswith('-1') else '#ea580c')
            if key=='tokens' and r.get('usage') is None:text(a,x+5,y+13,'UNKNOWN',12)
            else:rect(a,x,y,290*value/maximum,16,color)
    for i,(label,color) in enumerate([('neutral','#94a3b8'),('balanced','#16a34a'),('level1','#2563eb'),('level5','#ea580c')]):
        rect(a,40+i*230,93,14,14,color);text(a,62+i*230,106,label,13)
    text(a,36,560,'Same case inputs per comparison. Focus includes neutral/balanced controls; other cases only extremes.',13)
    text(a,36,588,'n=1, no confidence interval or causal ranking. Source counters: source-table.csv. Model name unreported.',12)
    b=scene('FUNCTION-03: artifact acceptance and observed behavior','Evidence from actual commands/artifacts, not profile announcements or token proxies')
    b[0]['color']='#ffffff'
    headings=[(25,'Condition'),(190,'Functional'),(300,'Integrity'),(400,'Full check'),(530,'Subchecks'),(655,'Source reads'),(810,'Extra scripts')]
    for x,label in headings:text(b,x,125,label,13)
    for i,r in enumerate(rows):
        y=157+i*28;review=r['trace_audit']
        for x,label in [(25,r['profile']),(210,'PASS' if r['functional'] else 'FAIL'),(310,r['integrity']),
            (430,int(review['full_mandatory_check_executed'])),(565,review['partial_feedback_subchecks']),
            (690,review['explicit_source_reads']),(855,review['additional_assert_scripts'])]:text(b,x,y,label,12)
        line(b,25,y+8,960,y+8,'#e5e7eb')
    text(b,25,545,'Subchecks = net/checkout intermediate feedback. Source reads relate to sync revision changes.',13)
    text(b,25,574,'Both verify levels may add risk-triggered scripts. Focus active breadth is not inferred from read counts.',13)
    text(b,25,602,'See manual-review.json for distinctions and unresolved cases; all helper/contract tests are separate.',12)
    return {'actual-costs':a,'acceptance-behavior':b}


def build(directory,png=False):
    directory=Path(directory);rows=json.loads((directory/'observations.json').read_text())['attempts']
    summary=summarize(rows);scenes=figures(rows)
    for name,value in [('summary.json',summary),('chart-data.json',scenes)]:
        (directory/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n')
    for name,value in scenes.items():write_svg(directory/(name+'.svg'),value)
    with (directory/'source-table.csv').open('w',encoding='utf-8',newline='') as stream:
        writer=csv.writer(stream,lineterminator='\n');writer.writerow(['id','case','profile','input_tokens','cached_input_tokens','cache_write_input_tokens','output_tokens','reasoning_output_tokens','total_tokens','wall_seconds','functional','integrity','actual_model_status'])
        for r in rows:
            u=r.get('usage') or {};writer.writerow([r['id'],r['case'],r['profile'],*[u.get(k) for k in ('input_tokens','cached_input_tokens','cache_write_input_tokens','output_tokens','reasoning_output_tokens','total_tokens')],r['seconds'],r['functional'],r['integrity'],r['actual_model_status']])
    if png:subprocess.run([shutil.which('pwsh') or 'powershell','-NoProfile','-File',str(Path(__file__).parent/'evaluation/render_figures.ps1'),'-Directory',str(directory.resolve())],check=True)
    return summary


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--directory',type=Path,required=True);p.add_argument('--png',action='store_true')
    args=p.parse_args();print(json.dumps(build(args.directory,args.png),indent=2))
