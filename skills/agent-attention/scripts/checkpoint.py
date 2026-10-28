#!/usr/bin/env python3
"""Explicit task-local attention state. Never installs skills or executes tasks."""
import argparse
import json
import os
from pathlib import Path
import re
import stat
import tempfile

if __package__:
    from .attention import inherit, parse_attention, SEMANTICS_VERSION
else:
    # Isolated Python (-I) omits the script directory from sys.path. Load only
    # the declared sibling resource, never a same-named global module.
    import importlib.util
    spec=importlib.util.spec_from_file_location('agent_attention_profile',Path(__file__).with_name('attention.py'))
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    inherit,parse_attention=module.inherit,module.parse_attention
    SEMANTICS_VERSION=module.SEMANTICS_VERSION


def label(value):
    if not isinstance(value, str) or not re.fullmatch(r'[a-z][a-z0-9-]{0,63}', value):
        raise ValueError('task/workflow labels must be simple identifiers')
    return value


def unique(pairs):
    result={}
    for key,value in pairs:
        if key in result: raise ValueError('duplicate checkpoint key')
        result[key]=value
    return result


def plain(path):
    if path.absolute()!=path.resolve(): raise ValueError('checkpoint aliases are not supported')
    if path.exists():
        meta=path.lstat()
        if not stat.S_ISREG(meta.st_mode) or meta.st_nlink!=1:
            raise ValueError('checkpoint must be a plain non-hardlinked file')


def validate(state, task):
    label(task)
    if isinstance(state,dict) and state.get('semantics_version')!=SEMANTICS_VERSION:
        raise ValueError('checkpoint semantics changed; explicitly re-select a profile and initialize a new state file')
    if (not isinstance(state,dict) or type(state.get('version')) is not int or state.get('version')!=1 or state.get('task_id')!=task
            or state.get('status') not in ('active','finished')
            or type(state.get('override_active')) is not bool):
        raise ValueError('checkpoint is malformed or belongs to another task')
    inherit(state.get('task_levels'))
    inherit(state.get('effective_levels'))
    label(state.get('workflow'))
    history=state.get('history')
    if not isinstance(history,list) or not history: raise ValueError('checkpoint history required')
    for event in history:
        if not isinstance(event,dict): raise ValueError('invalid transition object')
        label(event.get('workflow'))
        inherit(event.get('effective_levels'))
        if type(event.get('override_active')) is not bool: raise ValueError('invalid transition')
        if event['override_active'] is False and event['effective_levels']!=state['task_levels']:
            raise ValueError('non-override transition must use task levels')
    if any(state[key]!=history[-1][key] for key in ('workflow','effective_levels','override_active')):
        raise ValueError('checkpoint and last transition disagree')
    if state['status']=='finished' and state['override_active']:
        raise ValueError('finished task cannot retain an override')
    return state


def transition(state, workflow, override=None):
    if state['status']!='active': raise ValueError('task has finished; create a new checkpoint')
    effective=inherit(state['task_levels'],override)
    event={'workflow':label(workflow),'effective_levels':effective,'override_active':override is not None}
    state.update(event)
    state['history'].append(event.copy())
    return state


def execute(action, path, task, workflow='direct', attention=None, override=None):
    path=Path(path).absolute()
    plain(path); label(task); label(workflow)
    if action=='init':
        if path.exists(): raise ValueError('refuse to overwrite an existing checkpoint')
        if override is not None: raise ValueError('init takes a task profile, not a step override')
        levels=parse_attention(attention)
        state={'version':1,'semantics_version':SEMANTICS_VERSION,'task_id':task,'status':'active','task_levels':levels,'history':[]}
        transition(state,workflow)
    else:
        state=validate(json.loads(path.read_text(encoding='utf-8'),object_pairs_hook=unique),task)
        if attention is not None: raise ValueError('task profile cannot be silently replaced')
        if action=='show':
            if override is not None: raise ValueError('show cannot apply an override')
            return state
        if action=='enter': transition(state,workflow,override)
        elif action=='finish':
            if override is not None: raise ValueError('finish cannot apply an override')
            transition(state,state['workflow'])
            state['status']='finished'
        else: raise ValueError('unknown checkpoint action')
    validate(state,task)
    # Parent must already exist: this helper does not create arbitrary directory trees.
    staged=None
    try:
        with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',dir=path.parent,
                                         prefix='.attention-',suffix='.tmp',delete=False) as stream:
            staged=Path(stream.name)
            json.dump(state,stream,indent=2); stream.write('\n')
        plain(path)
        if action=='init' and path.exists(): raise ValueError('checkpoint appeared during init')
        os.replace(staged,path)
    finally:
        if staged is not None and staged.exists(): staged.unlink()
    return state


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('init','enter','show','finish'))
    parser.add_argument('--state',type=Path,required=True)
    parser.add_argument('--task',required=True)
    parser.add_argument('--workflow',default='direct')
    parser.add_argument('--attention')
    parser.add_argument('--override')
    parser.add_argument('--quiet',action='store_true',help='Print current effective state only; full history stays in the file')
    args=parser.parse_args(argv)
    try: state=execute(args.action,args.state,args.task,args.workflow,args.attention,args.override)
    except (OSError,ValueError,KeyError,TypeError,AttributeError) as error:
        parser.exit(2,'FAIL: '+str(error)+'\n')
    result=({key:state[key] for key in ('task_id','status','workflow','effective_levels','override_active')}
            if args.quiet else state)
    print(json.dumps(result,indent=None if args.quiet else 2))
    return 0


if __name__=='__main__': raise SystemExit(main())
