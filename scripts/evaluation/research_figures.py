"""Numerical research figures from paired records and the full grid plan.

Profile index preserves recorded pair order. It is neither time nor a one-axis
sweep. Plot primitives use white plotting areas, labeled ticks and legends.
"""
import csv
import itertools
import math
from .integrity_report import scene, text, rect, line

BLUE='#2563eb'
ORANGE='#ea580c'
GREEN='#16a34a'
GRAY='#cbd5e1'
AXES=('focus','sync','batch','explore','verify')


def canvas(title,caption):
    result=scene(title,caption)
    result[0]['color']='#ffffff'
    return result


def dot(items,x,y,color,r=2.5):
    items.append({'type':'circle','x':x,'y':y,'r':r,'color':color})


def tick_label(value,scale=1):
    return f'{value/scale:g}'+('k' if scale==1000 else '')


def axes(items,x,y,w,h,x_ticks,y_ticks,xmax,ymax,xlabel,ylabel,token=False):
    rect(items,x,y,w,h,'#ffffff')
    for value in x_ticks:
        px=x+w*value/xmax
        line(items,px,y,px,y+h,'#e5e7eb')
        text(items,px-10,y+h+22,tick_label(value,1000 if token else 1),12)
    for value in y_ticks:
        py=y+h-h*value/ymax
        line(items,x,py,x+w,py,'#e5e7eb')
        text(items,x-49,py+4,tick_label(value,1000 if token else 1),12)
    line(items,x,y+h,x+w,y+h,'#64748b');line(items,x,y,x,y+h,'#64748b')
    text(items,x,y-14,ylabel,14);text(items,x+35,y+h+48,xlabel,14)


def grid_coverage(data):
    rows=[r for r in data['observations'] if r['dataset']=='attention-grid-20261103']
    observed={}
    for row in rows:
        key=(row['case'],tuple(row['levels']),row['arm'])
        if key in observed:raise ValueError('duplicate grid cell')
        observed[key]=row['original_status']
    output=[]
    for case in ('cents','dependencies'):
        for index,axis in enumerate(AXES):
            for level in (1,3,5):
                counts=dict(planned=0,completed=0,blocked=0,failed=0,not_run=0)
                for levels in itertools.product((1,3,5),repeat=5):
                    if levels[index]!=level:continue
                    for arm in ('baseline','attention'):
                        status=observed.get((case,levels,arm))
                        counts['planned']+=1
                        counts[{'PASS':'completed','BLOCKED':'blocked','FAIL':'failed',None:'not_run'}[status]]+=1
                output.append({'case':case,'axis':axis,'level':level,**counts})
    return output


def source_tables(directory,pairs,coverage):
    table=['# Historical profile-index table','',
           'All 66 complete cents pairs, in recorded order. Index is not time or a single-axis sweep.',
           'Token totals include input + output; time unit is CLI wall seconds.','',
           '| Index | Focus | Sync | Batch | Explore | Verify | Baseline tokens | Attention tokens | Baseline seconds | Attention seconds |',
           '|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    with (directory/'profile-index.csv').open('w',encoding='utf-8',newline='') as stream:
        writer=csv.writer(stream,lineterminator='\n')
        writer.writerow(['profile_index','case',*AXES,'baseline_tokens','attention_tokens','baseline_seconds','attention_seconds'])
        for i,pair in enumerate(pairs,1):
            writer.writerow([i,pair['case'],*pair['levels'],*[pair[k] for k in ('baseline_tokens','attention_tokens','baseline_seconds','attention_seconds')]])
            table.append('| '+' | '.join(map(str,[i,*pair['levels'],pair['baseline_tokens'],pair['attention_tokens'],
                                                  round(pair['baseline_seconds'],4),round(pair['attention_seconds'],4)]))+' |')
    (directory/'profile-index.md').write_text('\n'.join(table)+'\n',encoding='utf-8',newline='\n')
    with (directory/'grid-coverage.csv').open('w',encoding='utf-8',newline='') as stream:
        fields=['case','axis','level','planned','completed','blocked','failed','not_run']
        writer=csv.DictWriter(stream,fieldnames=fields,lineterminator='\n');writer.writeheader();writer.writerows(coverage)


def plots(summary,data):
    pairs=summary['grid']['pairs'];n=len(pairs)
    result={}
    a=canvas('Historical paired costs across all profiles',f'HISTORICAL | cents | n={n} complete pairs | index preserves recorded profile order')
    # Shared numeric x indexing, independently labeled y units.
    for x,key,label,step in [(95,'tokens','Total tokens',50000),(575,'seconds','Wall time (seconds)',10)]:
        w,h,y=345,320,145
        values=[p[arm+'_'+key] for p in pairs for arm in ('baseline','attention')]
        maximum=max(step,math.ceil(max(values,default=step)/step)*step)
        axes(a,x,y,w,h,[1,10,20,30,40,50,60,66],list(range(0,maximum+1,step)),66,maximum,
             'Profile index (1..66)',label)
        for arm,color in [('baseline',BLUE),('attention',ORANGE)]:
            points=[(x+w*(i+1)/66,y+h-h*p[arm+'_'+key]/maximum) for i,p in enumerate(pairs)]
            for before,after in zip(points,points[1:]):line(a,*before,*after,color)
            for px,py in points:dot(a,px,py,color,2)
    line(a,70,102,100,102,BLUE);text(a,110,108,'Baseline',14)
    line(a,265,102,295,102,ORANGE);text(a,305,108,'Attention',14)
    text(a,40,558,'Index is not elapsed time or a one-axis sweep. Five-level mapping: profile-index.csv.',14)
    text(a,40,588,'Both arms pass frozen checks in all 66 pairs; fixed order, cache and truncation confound cost.',13)
    result['historical-lines']=a

    b=canvas('Historical paired scatter with equal-usage reference',f'HISTORICAL | cents | n={n} pairs | same numeric scale on x and y in each panel')
    for x,key,label,step in [(95,'tokens','tokens',50000),(575,'seconds','seconds',10)]:
        w,h,y=345,310,150
        values=[p[arm+'_'+key] for p in pairs for arm in ('baseline','attention')]
        maximum=max(step,math.ceil(max(values,default=step)/step)*step)
        ticks=list(range(0,maximum+1,step))
        axes(b,x,y,w,h,ticks,ticks,maximum,maximum,f'Baseline ({label})',f'Attention ({label})',token=key=='tokens')
        line(b,x,y+h,x+w,y,'#64748b');b[-1]['dash']=True
        for p in pairs:dot(b,x+w*p['baseline_'+key]/maximum,y+h-h*p['attention_'+key]/maximum,GREEN,3)
    dot(b,70,104,GREEN,4);text(b,85,109,'Observed pair',14)
    line(b,300,104,335,104,'#64748b');b[-1]['dash']=True;text(b,345,109,'Equal usage (y=x)',14)
    text(b,40,555,'k = 1,000 tokens. Above diagonal: Attention consumes more; below: less.',14)
    text(b,40,585,'Descriptive matched subset; not clean causal skill effects or full factorial coverage.',14)
    result['paired-scatter']=b

    c=canvas('Historical full-plan coverage by case and axis level','972 planned CLI cells | counts include both arms | each axis-level/case denominator = 162')
    coverage=grid_coverage(data)
    colors=[GREEN,ORANGE,'#dc2626',GRAY]
    labels=['completed','blocked','failed','not_run']
    for i,(label,color) in enumerate(zip(labels,colors)):
        rect(c,40+i*225,92,15,15,color);text(c,61+i*225,106,label.upper(),13)
    for x,case in [(95,'cents'),(565,'dependencies')]:
        text(c,x,140,case+' (planned=486)',19)
        totals={label:sum(r[label] for r in coverage if r['case']==case and r['axis']=='focus') for label in labels}
        text(c,x-10,159,f"{totals['completed']} completed / {totals['blocked']} blocked / {totals['not_run']} not run",11)
        for i,row in enumerate(r for r in coverage if r['case']==case):
            y=178+i*22
            text(c,x-68,y+13,row['axis']+' '+str(row['level']),11)
            cursor=x
            for label,color in zip(labels,colors):
                width=245*row[label]/row['planned'];rect(c,cursor,y,width,14,color);cursor+=width
            text(c,x+254,y+12,f"{row['completed']}/{row['blocked']}/{row['not_run']}",11)
        text(c,x,533,'Completed / blocked / not run',12)
    text(c,40,568,'Each panel marginalizes other axes; rows overlap and must not be summed across axes.',13)
    text(c,40,596,'Complete source counts, including planned and failed: grid-coverage.csv. Successful focus only 1.',13)
    result['grid-coverage']=c
    return result,coverage
