#!/usr/bin/env python3
"""Generate/check the independent attention skill, references and illustrations."""
import argparse
import html
import json
from pathlib import Path

if __package__:
    from .workflow_assets import check as check_workflow
    from .attention_setup_assets import check as check_setup
    from .attention import AXES
    from .attention_illustrations import axis_diagram, overview
else:
    from workflow_assets import check as check_workflow
    from attention_setup_assets import check as check_setup
    from attention import AXES
    from attention_illustrations import axis_diagram, overview


def reference():
    lines = ['# Optional attention profile (experimental)', '',
        'Load this layer once for the task, then retain its profile across workflow changes.',
        'No settings or `balanced` means the existing host/workflow behavior, with all axes at 3.',
        'These are five independent behavior controls, not model reasoning effort.', '',
        'Levels 1–2 reduce discretionary effort; 3 is balanced; 4–5 increase effort.',
        'Expected token direction follows effort, not a guaranteed total-token ordering.',
        'Since 0.1.1, batch means decomposition depth, not batch size; re-select old non-default profiles.', '',
        '## How to apply', '',
        '1. Read explicit attention assignments separately from the task. Optional preview:',
        '   `python <skill-dir>/scripts/attention.py --workflow direct --attention "focus=1,sync=4"`.',
        '   Clear profiles can be applied directly; no helper execution is required.',
        '   Unknown axes, duplicate assignments or levels outside 1–5 require correction;',
        '   do not guess or silently coerce. Missing axes remain 3.',
        '2. Use the selected levels before choosing each read, change or check.',
        '   Retain dependency pointers in task context; no new state file is required.',
        '   Narrow focus reduces active detail, not access to necessary evidence.',
        '3. Apply non-default directives to the current task and any selected workflow. Keep',
        '   authorization, mandatory checks, deadlines and break conditions intact.',
        '   Warnings are tradeoffs, not permission to change requested levels.',
        '4. Reconcile before dependent work whenever a shared contract changes,',
        '   regardless of sync level. If a profile prevents safe/correct work, explain',
        '   the conflict and propose a revised profile; never silently switch modes.',
        '5. Report outcomes, material deviations with reasons, checks and',
        '   remaining gaps. Stop when complete; no minimum number of iterations.', '',
        '## Five levels per axis', '', '| Axis | Level | Guidance |', '|---|---|---|']
    for axis, levels in AXES.items():
        for level, text in enumerate(levels, 1):
            lines.append(f'| {axis} | {level}'+(' (balanced)' if level == 3 else '')+f' | {text} |')
    lines += ['', '## Task-specific interpretation', '',
        '- Code: batch controls decomposition and intermediate inspection; sync reconciles caller/schema/test contracts.',
        '- Debug: preserve hypothesis attribution even at low decomposition; required risk controls take precedence.',
        '- Review: higher decomposition separates consequential review angles; no finding quota or edit authorization.', '',
        '## Tradeoffs', '',
        'Narrow focus can reduce repeated context, but may cause stale assumptions and rework.',
        'Wide focus can improve cross-component awareness, but may increase reading and distract',
        'from the next concrete action. Frequent sync can reduce drift but adds overhead.',
        'Low decomposition can reduce handoffs but make rollback and attribution harder.',
        'More exploration and verification consume effort without guaranteeing useful findings.',
        'Token savings and task-quality effects are hypotheses until measured.', '',
        'Avoid narrow focus + low decomposition + sparse sync for shared-contract changes.',
        'Do not lower mandatory checks, widen scope, run extra agents, or wait just',
        'because a slider is high. This helper prints guidance; it never executes tasks.', '']
    return '\n'.join(lines)




def playground():
    data = json.dumps(AXES, ensure_ascii=True).replace('<', '\\u003c')
    return '''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Agent attention playground</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#f2f6f4;color:#16313b;font:17px/1.5 system-ui,sans-serif}
main{max-width:1040px;margin:auto;padding:40px 24px}h1{font-size:36px;margin-bottom:8px}p{color:#415d67}
.layout{display:grid;grid-template-columns:1.1fr 1fr;gap:24px}.panel{padding:24px;background:#ffffff;border:1px solid #cddcda;border-radius:16px}
.control{margin:0 0 25px}label{display:flex;justify-content:space-between;font-weight:650}input{width:100%;accent-color:#5de2b3;margin:16px 0 5px}
.ends{display:flex;justify-content:space-between;font-size:13px;color:#415d67}small{display:block;color:#415d67;margin-top:6px}
button{border:0;border-radius:8px;padding:12px 18px;background:#5de2b3;color:#101827;font-weight:700;cursor:pointer}
pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#e0eee8;padding:16px;border-radius:8px;font-size:14px}
li{margin:10px 0}#warnings{color:#9a4c32}a{color:#126957}select{font:inherit;padding:6px;background:#ffffff;color:#16313b}
@media(max-width:750px){.layout{grid-template-columns:1fr}h1{font-size:28px}}
</style><main>
<h1>Agent attention / experiment</h1>
<p>Five independent controls. Level 3 keeps the ordinary balanced policy. This offline page previews guidance; it does not change Codex or run a task.</p>
<div class="layout"><section class="panel" aria-label="Attention controls"><div id="controls"></div>
<button id="reset" type="button">Reset to balanced</button></section>
<section class="panel" aria-label="Resolved guidance"><label for="skill">Example workflow label</label>
<select id="skill"><option>direct</option><option>loop-code</option><option>research</option></select>
<h2 id="mode">Balanced</h2><pre id="command"></pre><ul id="guidance" aria-live="polite"></ul><ul id="warnings" aria-live="polite"></ul>
<p>Required checks, permissions and task scope stay in force. Shared-contract changes always trigger reconciliation before dependent work. No minimum iteration count. Token savings are unmeasured.</p>
<p><a href="GUIDE.md">Guide and tradeoffs</a></p></section></div>
<p>Request → bounded action → check → reconcile when needed → next action or stop.</p>
</main><script>
const axes = '''+data+''';
const labels = {focus:'Attention width',sync:'Reconciliation cadence',batch:'Decomposition depth',explore:'Exploration breadth',verify:'Verification depth'};
const ends = {focus:['One action','Relevant flow'],sync:['At completion*','Shared-state steps'],batch:['Minimal decomposition','Detailed reversible steps'],explore:['Supplied sources*','Map relevant flow'],verify:['Direct result*','Independent checks']};
const inputs = {};
for (const key of Object.keys(axes)) {
  const box = document.createElement('div'); box.className='control';
  const label = document.createElement('label'); label.htmlFor=key;
  label.append(document.createTextNode(labels[key]));
  const value = document.createElement('output'); value.id=key+'-value'; label.append(value);
  const input = document.createElement('input'); input.id=key; input.type='range'; input.min='1'; input.max='5'; input.step='1'; input.value='3';
  const edge = document.createElement('div'); edge.className='ends';
  for (const text of ends[key]) { const span=document.createElement('span');span.textContent=text;edge.append(span); }
  const note = document.createElement('small'); note.id=key+'-note'; input.setAttribute('aria-describedby',note.id);
  box.append(label,input,edge,note);document.getElementById('controls').append(box);inputs[key]=input;
  input.addEventListener('input',render);
}
function items(id, values) {
  const list=document.getElementById(id);list.replaceChildren();
  for(const text of values){const item=document.createElement('li');item.textContent=text;list.append(item);}
}
function render() {
  const levels={};const directives=[];const warnings=[];
  for(const [key,input] of Object.entries(inputs)) {
    const n=Number(input.value);levels[key]=n;
    document.getElementById(key+'-value').textContent=n===3?'3 · balanced':String(n);
    document.getElementById(key+'-note').textContent=axes[key][n-1];
    if(n!==3)directives.push(key+': '+axes[key][n-1]);
  }
  if(levels.focus<=2&&levels.batch>=4)warnings.push('Narrow focus with detailed decomposition can lose the shared goal; retain dependency pointers without repeated summaries.');
  if(levels.sync<=2&&(levels.focus<=2||levels.batch>=4))warnings.push('Sparse reconciliation can accumulate drift; reconcile immediately on shared-contract changes.');
  if(levels.explore>=4&&levels.focus<=2)warnings.push('Broad exploration may dominate a narrow task; record findings, then return to the selected action.');
  const changed=Object.entries(levels).filter(([key,n])=>n!==3).map(([key,n])=>key+'='+n);
  const setting=changed.length?changed.join(','):'balanced';
  document.getElementById('mode').textContent=changed.length?'Custom profile':'Balanced';
  document.getElementById('command').textContent='python scripts/attention.py --workflow '+document.getElementById('skill').value+' --attention "'+setting+'"';
  items('guidance',directives.length?directives:['No overrides: use the existing skill workflow.']);items('warnings',warnings);
  window.attentionPreview={levels,directives,warnings,setting};
}
document.getElementById('reset').addEventListener('click',()=>{for(const input of Object.values(inputs))input.value='3';render();});
document.getElementById('skill').addEventListener('change',render);render();
</script></html>
'''


def check(repo, write=False):
    outputs = {repo/'docs/assets/attention-controls.svg': overview(),
               repo/'docs/attention-playground.html': playground()}
    outputs.update({repo/f'docs/assets/attention-{axis}.svg': axis_diagram(axis, levels)
                    for axis, levels in AXES.items()})
    helper = (repo/'scripts/attention.py').read_text(encoding='utf-8')
    folder = repo/'skills/agent-attention'
    outputs[folder/'references/attention.md'] = reference()
    outputs[folder/'scripts/attention.py'] = helper
    outputs[folder/'scripts/checkpoint.py'] = (repo/'scripts/checkpoint.py').read_text(encoding='utf-8')
    errors = []
    for path, content in outputs.items():
        if write:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8', newline='\n')
        elif not path.is_file() or path.read_text(encoding='utf-8') != content:
            errors.append('stale attention resource: '+path.relative_to(repo).as_posix())
    return errors + check_workflow(repo, write) + check_setup(repo, write)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    errors = check(args.repo.resolve(), args.write)
    print('\n'.join(errors) if errors else 'PASS: attention resources and diagram')
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
