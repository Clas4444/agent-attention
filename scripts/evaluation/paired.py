"""Frozen single-axis paired design and leak-free task rendering."""
import random
from ..attention import AXES


def design(seed=20261103):
    profiles = [('balanced',dict.fromkeys(AXES,3))]
    for axis in AXES:
        for level in (1,5): profiles.append((f'{axis}-{level}',dict(dict.fromkeys(AXES,3),**{axis:level})))
    rng=random.Random(seed); rng.shuffle(profiles)
    pairs=[('dependencies',label,levels) for label,levels in profiles]
    pairs.append(('cents','balanced',dict.fromkeys(AXES,3)))
    rows=[]
    for number,(case,label,levels) in enumerate(pairs,1):
        arms=['baseline','attention'] if number%2 else ['attention','baseline']
        for arm in arms:
            rows.append({'id':f'{number:02d}-{arm}', 'pair':number,'case':case,
                         'arm':arm,'profile':label,'levels':levels})
    return rows


def prompt(case, row):
    # Explicit template prefix/suffix, reject drift instead of fragile free replacement.
    prefix='Use the installed .agents/skills/agent-attention/SKILL.md explicitly with {profile} for this task. '
    suffix='Apply the profile to your working decisions. '
    task=case['task']
    if not task.startswith(prefix) or task.count(suffix)!=1: raise ValueError('unknown task template')
    task=task[len(prefix):].replace(suffix,'')
    common='Work only in the current disposable project. No network, external actions, global instructions or extra agents. '
    if row['arm']=='baseline':
        if any(word in task.casefold() for word in ('attention','profile','skill')): raise ValueError('baseline cue leakage')
        return common+task
    return common+prefix.format(profile=','.join(f'{k}={v}' for k,v in row['levels'].items()))+task+suffix
