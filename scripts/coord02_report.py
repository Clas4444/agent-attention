"""COORD-02 internal-only summary/figures from sanitized observations. NO_PUSH.

python -m scripts.coord02_report --directory task/coord-02-evidence --png
No model calls; old historical66 datasets are never pooled with this pilot.
"""
import argparse
import csv
import json
import math
from pathlib import Path
import shutil
import subprocess
from .evaluation.control import parse_usage
from .evaluation.integrity_report import scene,text,rect,line,write_svg
from .evaluation.trace_metrics import successful_mandatory_check

AXES=('focus','sync','batch','explore','verify')


def review_trace(events):
    actions=[e['item'] for e in events if e.get('type')=='item.completed' and isinstance(e.get('item'),dict)]
    commands=[a for a in actions if a.get('type')=='command_execution']
    edits=[];inspections=[]
    for index,action in enumerate(actions):
        cmd=action.get('command','')
        if action.get('type')=='file_change' or any(t in cmd for t in ('Set-Content','write_text(','apply_patch')):edits.append(index)
        elif action.get('type')=='command_execution' and any(t in cmd for t in ('Get-Content','read_text(','cat ')):inspections.append(index)
    return {'mandatory_check_executed':successful_mandatory_check(actions),
        'candidate_instruction_read':any('.agents/skills/agent-attention/SKILL.md' in a.get('command','') and a.get('exit_code')==0 for a in commands),
        'edit_events_heuristic':len(edits),
        'inspection_between_edit_events':bool(edits and any(edits[0]<i<edits[-1] for i in inspections)),
        'additional_assert_command_heuristic':any('assert ' in a.get('command','') and a.get('exit_code')==0 and not successful_mandatory_check([a]) for a in commands),
        'signature_verdict':'NOT_VERIFIED: heuristics locate evidence; do not grade five-axis adherence from counts',
        'reconciliation_verdict':'NOT_VERIFIED: no independently measured shared-contract transition in this fixture'}


def summarize(attempts):
    seen=set();groups={};normalized={}
    for row in attempts:
        if row['id'] in seen:raise ValueError('duplicate attempted cell')
        seen.add(row['id']);usage=parse_usage(row['usage']);normalized[row['id']]=usage
        if usage is not None and 'total_tokens' in row['usage'] and row['usage']['total_tokens']!=usage['total_tokens']:
            raise ValueError('inconsistent total_tokens; never trust a precomputed total')
        if row['arm'] not in ('baseline','attention'):raise ValueError('unknown arm')
        if row.get('seconds') is not None and (type(row['seconds']) not in (int,float) or not math.isfinite(row['seconds']) or row['seconds']<0):
            raise ValueError('invalid elapsed time')
        groups.setdefault((row['case'],row['profile']),{})[row['arm']]=row
    pairs=[]
    for (case,profile),arms in groups.items():
        if set(arms)!= {'baseline','attention'}:continue
        a,b=arms['attention'],arms['baseline']
        ua,ub=normalized[a['id']],normalized[b['id']]
        if not ua or not ub or ub['total_tokens']<=0 or b['seconds'] is None or a['seconds'] is None or b['seconds']<=0:continue
        pairs.append({'case':case,'profile':profile,'n':1,
           'baseline_tokens':ub['total_tokens'],'attention_tokens':ua['total_tokens'],
           'token_delta_percent':100*(ua['total_tokens']/ub['total_tokens']-1),
           'baseline_seconds':b['seconds'],'attention_seconds':a['seconds'],
           'seconds_delta_percent':100*(a['seconds']/b['seconds']-1),
           'baseline_status':b['status'],'attention_status':a['status'],
           'quality_matched':a['functional']==b['functional'],'both_functional':a['functional'] and b['functional'],
           'both_integrity':a['integrity']=='PASS' and b['integrity']=='PASS'})
        pairs[-1]['wire_v1_pair']=a.get('coordination_wire_integrity')=='V1_ALIGNED' and b.get('coordination_wire_integrity')=='V1_ALIGNED'
    return {'attempted_cli':len(attempts),'completed_model_sessions':sum(r.get('model_turn_completed') is True for r in attempts),
       'functional_pass':sum(r['functional'] is True for r in attempts),
       'integrity_pass':sum(r['integrity']=='PASS' for r in attempts),
       'status_counts':{s:sum(r['status']==s for r in attempts) for s in sorted({r['status'] for r in attempts})},
       'usage_missing':sum(r['usage'] is None for r in attempts),
       'actual_model_reported':sum(r['actual_model'] is not None for r in attempts),
       'audited_mandatory_checks':sum(r.get('behavior_review',{}).get('mandatory_check_executed') is True for r in attempts),
       'mandatory_check_audit_samples':sum('behavior_review' in r for r in attempts),
       'initial_wire_draft_attempts':sum(r.get('coordination_wire_integrity')=='DRAFT_MISMATCH' for r in attempts),
       'strict_v1_complete_pairs':sum(p['wire_v1_pair'] for p in pairs),
       'pairs':pairs,'limits':['n=1 per cell; no effect confidence interval or causal claim',
        'Balanced dependencies control is reused graphically, not independently replicated per axis',
        'Command counts and tokens alone do not demonstrate signature adherence',
        'Historical66 remain a separate confounded campaign, never included here']}


def figures(summary,attempts):
    pairs=summary['pairs'];case_pairs={p['profile']:p for p in pairs if p['case']=='dependencies'}
    a=scene('COORD-02 paired pilot: cost differences within each axis',
       f"NEW Codex CLI | {len(case_pairs)} dependencies pairs ({sum(p['wire_v1_pair'] for p in case_pairs.values())} V1-aligned) | n=1/cell | Attention / baseline - 1")
    a[0]['color']='#ffffff'
    values=[p[k] for p in case_pairs.values() for k in ('token_delta_percent','seconds_delta_percent')]
    bound=max(25,math.ceil(max([abs(v) for v in values]+[1])/25)*25)
    line(a,45,105,75,105,'#2563eb');text(a,85,110,'Total tokens delta (%)',14)
    line(a,400,105,430,105,'#ea580c');text(a,440,110,'CLI wall-time delta (%)',14)
    line(a,765,100,775,110,'#374151');line(a,765,110,775,100,'#374151');text(a,785,110,'draft/mixed wire',13)
    for index,axis in enumerate(AXES):
        x=70+index*185;y=175;w=135;h=270
        text(a,x+25,150,axis,18)
        for tick in (-bound,-bound/2,0,bound/2,bound):
            py=y+h/2-h*tick/(2*bound);line(a,x,py,x+w,py,'#e5e7eb');text(a,x-34,py+4,f'{tick:g}',11)
        line(a,x,y+h/2,x+w,y+h/2,'#64748b')
        for key,color in [('token_delta_percent','#2563eb'),('seconds_delta_percent','#ea580c')]:
            previous=None
            for level in (1,3,5):
                pair=case_pairs.get('balanced' if level==3 else f'{axis}-{level}')
                px=x+w*(level-1)/4
                if pair:
                    py=y+h/2-h*pair[key]/(2*bound)
                    if previous:line(a,*previous,px,py,color)
                    a.append({'type':'circle','x':px,'y':py,'r':3.5,'color':color});previous=(px,py)
                    if not pair['wire_v1_pair']:
                        line(a,px-4,py-4,px+4,py+4,'#374151');line(a,px-4,py+4,px+4,py-4,'#374151')
                else:previous=None
        for level in (1,3,5):text(a,x+w*(level-1)/4-3,y+h+22,str(level),13)
        text(a,x+10,y+h+49,'Selected level',13)
    text(a,40,541,'Other four axes remain 3. Balanced dependencies pair is shared across panels (one control).',13)
    text(a,40,570,'Lines connect measured levels for readability, not interpolation or monotonic-effect claims.',13)
    text(a,40,598,'Positive = Attention costs more. No confidence interval: one attempt per condition; no general savings.',13)
    b=scene('COORD-02 functional, integrity and trace observations',
        f"NEW pilot | {summary['attempted_cli']} attempted CLI | cost is interpreted alongside actual acceptance")
    b[0]['color']='#ffffff'
    pairs_order=sorted(pairs,key=lambda p:(p['case'],p['profile']))
    text(b,32,112,'Case / profile',13);text(b,295,112,'Functional B/A',13);text(b,455,112,'Integrity both',13)
    text(b,610,112,'Mandatory check B/A',13);text(b,820,112,'Commands B/A',13)
    for i,p in enumerate(pairs_order):
        y=145+i*29
        subset={r['arm']:r for r in attempts if r['case']==p['case'] and r['profile']==p['profile']}
        text(b,32,y,p['case']+'/'+p['profile'],12)
        text(b,310,y,f"{int(subset['baseline']['functional'])}/{int(subset['attention']['functional'])}",13)
        text(b,475,y,'PASS' if p['both_integrity'] else 'FAIL',13)
        checks=[subset[arm].get('behavior_review',{}).get('mandatory_check_executed') for arm in ('baseline','attention')]
        text(b,665,y,'/'.join('?' if v is None else str(int(v)) for v in checks),13)
        text(b,860,y,'/'.join(str(subset[arm]['behavior']['terminal_commands']) for arm in ('baseline','attention')),13)
        line(b,32,y+9,960,y+9,'#e5e7eb')
    text(b,32,550,'B/A = baseline/attention. 1 = observed PASS/check; 0 = absent. Each row is one paired case.',13)
    text(b,32,578,'Counts are trace observations, not proof of five-axis adherence; see semantic-review.json.',13)
    text(b,32,606,'No actual model name is inferred when transport does not report one. Historical data is separate.',12)
    return {'axis-paired-effects':a,'quality-behavior':b}


def build(directory,png=False):
    directory=Path(directory);data=json.loads((directory/'observations.json').read_text(encoding='utf-8'))
    summary=summarize(data['attempts'])
    for name,value in [('summary.json',summary),('chart-data.json',figures(summary,data['attempts']))]:
        (directory/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n')
    for name,items in figures(summary,data['attempts']).items():write_svg(directory/(name+'.svg'),items)
    with (directory/'paired-effects.csv').open('w',encoding='utf-8',newline='') as stream:
        fields=list(summary['pairs'][0]) if summary['pairs'] else ['case','profile','n']
        writer=csv.DictWriter(stream,fields,lineterminator='\n');writer.writeheader();writer.writerows(summary['pairs'])
    if png:subprocess.run([shutil.which('pwsh') or 'powershell','-NoProfile','-File',
         str(Path(__file__).parent/'evaluation/render_figures.ps1'),'-Directory',str(directory.resolve())],check=True)
    return summary


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--directory',type=Path,required=True);p.add_argument('--png',action='store_true')
    args=p.parse_args();print(json.dumps(build(args.directory,args.png),indent=2))
