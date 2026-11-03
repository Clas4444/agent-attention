"""Rebuild published metrics and figures from portable inputs only; no model.

python -m scripts.evaluation.integrity_report --directory docs/testing/reports/2026-11-03
SVG needs only Python. PNG uses Windows PowerShell/System.Drawing when available.
"""
import argparse
from collections import Counter
import hashlib
import html
import json
import math
from pathlib import Path
import shutil
import statistics
import subprocess
from .control import parse_usage


def mean(values): return statistics.mean(values) if values else None


def summarize(data, pilot):
    rows=data['observations']; seen=set()
    for row in rows:
        key=(row['dataset'],row['index'])
        if key in seen:raise ValueError('duplicate observation')
        seen.add(key)
        if row['original_status'] not in ('PASS','FAIL','BLOCKED'):raise ValueError('invalid status')
        if not row['calls']:raise ValueError('missing CLI records')
        for call in row['calls']:
            parse_usage(call['usage'])
            if type(call['seconds']) not in (int,float) or not math.isfinite(call['seconds']) or call['seconds']<0:
                raise ValueError('invalid duration')
    datasets={}
    for name in sorted({r['dataset'] for r in rows}):
        subset=[r for r in rows if r['dataset']==name]
        datasets[name]={'packages':len(subset),'cli_invocations':sum(len(r['calls']) for r in subset),
          'original_status':dict(Counter(r['original_status'] for r in subset)),
          'functional_cents_pass':sum(r['functional_cents'] is True for r in subset),
          'functional_cents_evaluated':sum(r['functional_cents'] is not None for r in subset),
          'stored_independent_pass':sum(r.get('stored_independent_acceptance') is True for r in subset),
          'per_arm':{arm:{'n':sum(r['arm']==arm for r in subset),
                         'functional_cents_pass':sum(r['arm']==arm and r['functional_cents'] is True for r in subset),
                         'original_pass':sum(r['arm']==arm and r['original_status']=='PASS' for r in subset)}
                     for arm in sorted({r['arm'] for r in subset})}}
    grid=[r for r in rows if r['dataset']=='attention-grid-20261103']
    pairs={}
    for row in grid:
        key=(row['case'],tuple(row['levels']))
        if row['arm'] in pairs.setdefault(key,{}):raise ValueError('duplicate grid arm')
        pairs[key][row['arm']]=row
    paired=[]
    for (case,levels),arms in pairs.items():
        if set(arms)!= {'baseline','attention'}:continue
        if any(r['original_status']!='PASS' or r['functional_cents'] is not True for r in arms.values()):continue
        baseline,attention=[arms[a]['calls'][0] for a in ('baseline','attention')]
        if not baseline['usage'] or not attention['usage']:continue
        bt,at=[c['usage']['input_tokens']+c['usage']['output_tokens'] for c in (baseline,attention)]
        if bt<=0 or baseline['seconds']<=0:raise ValueError('invalid pair denominator')
        paired.append({'case':case,'levels':levels,'baseline_tokens':bt,'attention_tokens':at,
          'delta_tokens_percent':100*(at/bt-1),'baseline_seconds':baseline['seconds'],
          'attention_seconds':attention['seconds'],'delta_seconds_percent':100*(attention['seconds']/baseline['seconds']-1)})
    coverage={axis:{str(level):sum(r['original_status']=='PASS' and r['arm']=='attention' and r['levels'][i]==level for r in grid) for level in (1,3,5)}
              for i,axis in enumerate(('focus','sync','batch','explore','verify'))}
    not_run=972-len(grid)
    if not_run<0:raise ValueError('grid exceeds frozen plan')
    metrics={'n':len(paired),'mean_pair_token_delta_percent':mean([p['delta_tokens_percent'] for p in paired]),
      'mean_pair_time_delta_percent':mean([p['delta_seconds_percent'] for p in paired]),
      'ratio_means_token_delta_percent':100*(sum(p['attention_tokens'] for p in paired)/sum(p['baseline_tokens'] for p in paired)-1) if paired else None,
      'ratio_means_time_delta_percent':100*(sum(p['attention_seconds'] for p in paired)/sum(p['baseline_seconds'] for p in paired)-1) if paired else None,
      'attention_token_wins':sum(p['attention_tokens']<p['baseline_tokens'] for p in paired)}
    attempts=pilot['attempts'];ids=[r['id'] for r in attempts]
    if len(ids)!=len(set(ids)):raise ValueError('duplicate pilot attempt')
    if set(ids)&set(pilot['not_run']):raise ValueError('observed also NOT_RUN')
    if len(ids)+len(pilot['not_run'])!=24:raise ValueError('missing pilot cells')
    for row in attempts:parse_usage(row['usage'])
    return {'schema':1,'historical':datasets,'grid':{'planned':972,'recorded':len(grid),
       'status':dict(Counter(r['original_status'] for r in grid)),'not_run':not_run,
       'quota_records':sum(r['quota_event'] for r in grid),
       'quota_after_tool_start':sum(r['quota_event'] and r['tool_starts']>0 for r in grid),
       'quota_without_tool_start':sum(r['quota_event'] and r['tool_starts']==0 for r in grid),
       'successful_attention_coverage':coverage,'pairs':paired,'paired_metrics':metrics},
       'pilot':{'planned':24,'attempted':len(attempts),'not_run':len(pilot['not_run']),
         'completed_model_sessions':sum(r['actual_model'] is not None for r in attempts),
         'status':dict(Counter(r['status'] for r in attempts)),
         'per_axis_effect':'NOT_RUN: no complete matched pair; unknown values are not zero'},
       'limits':['Historical fixed-order truncated grid; all successful focus=1',
          'Historical skill discovery contamination; no causal skill-vs-no-skill effect',
          'Revision functional regrade retained as historical, not revalidated sorted_ids semantics',
          'No sample uncertainty interval; descriptive pairs are not independent replicates']}


def scene(title,subtitle):
    return [{'type':'rect','x':0,'y':0,'w':1000,'h':620,'color':'#f2f6f4'},
      {'type':'text','x':32,'y':40,'size':25,'text':title,'color':'#16313b'},
      {'type':'text','x':32,'y':70,'size':14,'text':subtitle,'color':'#415d67'}]


def text(items,x,y,label,size=14): items.append({'type':'text','x':x,'y':y,'size':size,'text':str(label),'color':'#16313b'})
def rect(items,x,y,w,h,color): items.append({'type':'rect','x':x,'y':y,'w':w,'h':h,'color':color})
def line(items,x,y,x2,y2,color='#94a6a1'):items.append({'type':'line','x':x,'y':y,'x2':x2,'y2':y2,'color':color})


def figures(summary,protocol):
    g=summary['grid'];m=g['paired_metrics']; pairs=g['pairs']
    a=scene('Historical grid: progress and coverage','HISTORICAL | 972 planned CLI cells; partial fixed-order traversal, not full factorial')
    counts=[g['status'].get('PASS',0),g['status'].get('BLOCKED',0),g['not_run']]
    x=40
    for label,n,c in zip(['PASS','BLOCKED','NOT_RUN'],counts,['#126957','#bc7640','#cddcda']):
        w=920*n/972;rect(a,x,115,w,60,c);text(a,x+3,205,f'{label}: {n}',13);x+=w
    text(a,40,255,'Completed attention profiles per axis level (n='+str(m['n'])+')',19)
    for i,(axis,levels) in enumerate(g['successful_attention_coverage'].items()):
        y=295+i*48;text(a,40,y+16,axis)
        for j,level in enumerate(('1','3','5')):
            x=180+j*260;n=levels[level];rect(a,x,y,200*n/max(m['n'],1),24,['#94bfb0','#126957','#16313b'][j]);text(a,x+204,y+17,f'L{level}: {n}',12)
    text(a,40,585,'Focus 3/5 absent. Dependencies absent. Quota: one partial attempt + 151 without tool starts.',13)
    b=scene('Historical paired tokens and time','HISTORICAL | valid cents pairs only; n='+str(m['n'])+' | no causal or general savings claim')
    for x,label,key in [(55,'Total tokens','tokens'),(535,'Wall seconds','seconds')]:
        text(b,x,113,label,19)
        xs=[p['baseline_'+key] for p in pairs];ys=[p['attention_'+key] for p in pairs]
        maximum=max(xs+ys,default=1)*1.05
        line(b,x,470,x+390,470);line(b,x,470,x,145);line(b,x,470,x+390,145)
        for vx,vy in zip(xs,ys): b.append({'type':'circle','x':x+390*vx/maximum,'y':470-325*vy/maximum,'r':3,'color':'#126957'})
        text(b,x,505,'Baseline -> x; Attention -> y; diagonal = equal',12)
        text(b,x,530,'axis max: '+f'{maximum:,.1f}',12)
    text(b,40,570,'Token delta: mean(pair %) '+f"{m['mean_pair_token_delta_percent']:.2f}%"+'; ratio(means) '+f"{m['ratio_means_token_delta_percent']:.2f}%",15)
    text(b,40,598,'Time delta: mean(pair %) '+f"{m['mean_pair_time_delta_percent']:.2f}%"+'; ratio(means) '+f"{m['ratio_means_time_delta_percent']:.2f}%",15)
    c=scene('Single-axis pilot: missingness, not a zero effect','NEW | 24 CLI planned; 1 startup blocked; 23 NOT_RUN; no completed model sessions')
    text(c,40,120,'Other four axes = 3 | dependencies main case | balanced pair on cents',17)
    for i,axis in enumerate(('focus','sync','batch','explore','verify')):
        y=175+i*65;text(c,40,y+20,axis,18)
        for j,level in enumerate((1,3,5)):
            x=210+j*240;rect(c,x,y,210,40,'#dce5e1');text(c,x+8,y+25,f'{level}: NOT_RUN',15)
    text(c,40,545,'N=0 complete matched pairs. Costs and quality effects are unknown, not zero.',17)
    text(c,40,578,'Blocked baseline reservation belongs to explore=1; baseline receives no profile cue.',13)
    d=scene('Quality, policy and integrity alongside cost','Original statuses retained; functional rechecks are separate; no external-effects attestation')
    y=135
    for name,info in summary['historical'].items():
        text(d,40,y,name,17);text(d,40,y+30,'Original: '+str(info['original_status']),14)
        text(d,40,y+56,f"Frozen cents functional: {info['functional_cents_pass']}/{info['functional_cents_evaluated']}; historical policy/integrity NOT_VERIFIED",13);y+=110
    text(d,40,490,'New pilot: protected inputs intact; no model/action; task acceptance not evaluated.',16)
    text(d,40,530,'Harness controls: stop-first, append-only retry, cue-free baseline, functional/mutation rejection.',14)
    text(d,40,570,'Do not interpret cheaper tokens as adherence or higher quality. Targets are not measurements.',14)
    e=scene('Historical paired deltas: every valid pair','HISTORICAL | n='+str(m['n'])+' | attention / baseline - 1; ordered by recorded profile')
    for top,key,label in [(150,'delta_tokens_percent','Total token delta (%)'),(370,'delta_seconds_percent','Wall-time delta (%)')]:
        text(e,40,top-30,label,18)
        values=[p[key] for p in pairs];bound=max([abs(v) for v in values]+[1])
        line(e,75,top+60,930,top+60)
        for i,value in enumerate(values):
            x=80+840*i/max(len(values)-1,1);y=top+60-65*value/bound
            line(e,x,top+60,x,y,'#126957' if value<0 else '#bc7640')
            e.append({'type':'circle','x':x,'y':y,'r':3,'color':'#126957' if value<0 else '#bc7640'})
        text(e,40,top+145,f'Y extent +/- {bound:.2f}%; horizontal line = zero; x = recorded pair 1..{len(values)}',13)
    text(e,40,585,'Truncation, cache and fixed baseline-first order confound these descriptive differences.',14)
    return {'grid-progress':a,'paired-scatter':b,'paired-deltas':e,'single-axis-pilot':c,'quality-integrity':d}


def write_svg(path,items):
    parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="620" viewBox="0 0 1000 620" role="img">']
    for item in items:
        i=dict(item);kind=i.pop('type');color=i.pop('color')
        if kind=='text':
            label=html.escape(i.pop('text'));size=i.pop('size')
            parts.append(f'<text x="{i["x"]}" y="{i["y"]}" font-family="Arial,sans-serif" font-size="{size}" fill="{color}">{label}</text>')
        elif kind=='rect':parts.append(f'<rect x="{i["x"]}" y="{i["y"]}" width="{i["w"]}" height="{i["h"]}" fill="{color}"/>')
        elif kind=='circle':parts.append(f'<circle cx="{i["x"]}" cy="{i["y"]}" r="{i["r"]}" fill="{color}"/>')
        else:
            dash=' stroke-dasharray="6 4"' if i.get('dash') else ''
            parts.append(f'<line x1="{i["x"]}" y1="{i["y"]}" x2="{i["x2"]}" y2="{i["y2"]}" stroke="{color}"{dash}/>')
    path.write_text('\n'.join(parts+['</svg>'])+'\n',encoding='utf-8',newline='\n')


def build(directory,png=False):
    directory=Path(directory)
    data=json.loads((directory/'historical.json').read_text(encoding='utf-8'))
    pilot=json.loads((directory/'pilot.json').read_text(encoding='utf-8'))
    protocol=json.loads((directory/'protocol.json').read_text(encoding='utf-8'))
    summary=summarize(data,pilot)
    (directory/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8',newline='\n')
    scenes=figures(summary,protocol)
    from .research_figures import plots,source_tables
    research,coverage=plots(summary,data)
    scenes.update(research)
    source_tables(directory,summary['grid']['pairs'],coverage)
    for name,items in scenes.items():write_svg(directory/(name+'.svg'),items)
    (directory/'chart-data.json').write_text(json.dumps(scenes,indent=2)+'\n',encoding='utf-8',newline='\n')
    if png:
        subprocess.run([shutil.which('pwsh') or 'powershell','-NoProfile','-File',str(Path(__file__).with_name('render_figures.ps1')),
                        '-Directory',str(directory.resolve())],check=True)
    return summary


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--directory',type=Path,required=True);p.add_argument('--png',action='store_true')
    a=p.parse_args();print(json.dumps(build(a.directory,a.png)['grid']['paired_metrics'],indent=2))
