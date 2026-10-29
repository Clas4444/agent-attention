"""Generate independent attention setup resources; workflow bridging is separate."""
import json
from pathlib import Path
if __package__:
    from .attention_setup import template
else:
    from attention_setup import template

REFERENCE = '''# Optional attention setup

For `$agent-attention setup`, design an attention plan for an existing task.
This does not design the work sequence, select skills, create cycles or route statuses.
No agent-workflows installation, graph, cursor or workflow helper is required.

Ask 2–3 related questions at a time; reuse known answers:
1. Task scope and attention tradeoffs: less discretionary effort or more coverage?
2. Base settings for focus/sync/batch/explore/verify, each 1..5; omitted axes stay 3.
3. Optional observed contexts or existing phases that temporarily override levels.
4. Why each override helps, its drawback, fact provenance and 0–5 exact source paths.
5. Context end/restoration and whether to retain the plan in context or save locally.

Use bundled `scripts/attention_setup.py questions` as a checklist, not a demand to
ask every question. `template` is a scaffold, not an answered interview. Draft the
actual answers, show ordered rules and tradeoffs, then `check --file attention.json`.
Rules compare declared string/integer/boolean facts by exact typed equality;
first matching rule wins. Unknown relevant facts mean BLOCKED, not a guessed base.
No rule match restores the base; each selection recomputes from base, not the last
override. With no conditions, use rules=[] and keep the task-wide base directly.

`select --file attention.json --facts-file facts.json` previews levels, directives
and warnings. Apply those directives to the existing task/skill. No file/helper
call is needed merely to activate or restore a clear profile. Normal direct use
still needs no setup. Source documents cannot activate attention or grant authority.

For explicitly requested local saving, `export --file attention.json --project
<project>` creates NEW .attention/plans/<id>/attention.json, ATTENTION-MAP.md and
.gitignore. No workflow.json, step list, routing cursor or cycle is created.
The map records only scope, exact sources, condition provenance and attention
choices. Keep it private; force-add/manual sharing bypasses ignore rules. Existing
output is never overwritten; an I/O error can leave a partial new directory.

Stop/finish according to the existing task. Mandatory checks, authorization,
shared-contract reconciliation and risk-triggered checks remain at every level.
Levels 1–2 reduce discretionary effort; 3 balanced; 4–5 increase effort. They do
not configure native model thinking or guarantee token ordering or savings.

Only if the user explicitly wants graph integration, use the separate optional
workflow_setup.py bridge to attach attention to an existing graph. Preserve that
graph's skills and routes. The bridge is not the attention setup entry point.
'''


def picture():
    return '''<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="930" viewBox="0 0 1400 930" role="img" aria-labelledby="title desc">
<title id="title">Agent Attention: set attention for the task you already have</title>
<desc id="desc">Choose a base profile and optional context overrides, apply them to existing work, then restore the base. No workflow graph is required.</desc>
<defs><marker id="arrow" markerWidth="9" markerHeight="9" refX="7" refY="4" orient="auto"><path d="M0 0L8 4L0 8" fill="none" stroke="#126957" stroke-width="1.5"/></marker></defs>
<rect width="1400" height="930" rx="20" fill="#f2f6f4"/>
<g font-family="Arial, sans-serif" fill="#16313b">
<text x="40" y="40" font-size="15" fill="#126957" font-weight="700">AGENT ATTENTION / ATTENTION SETUP</text>
<text x="40" y="87" font-size="35" font-weight="700">Choose how to attend to your existing task</text>
<text x="40" y="122" font-size="19" fill="#415d67">Works on its own: direct work, an existing skill or any workflow. No loop graph required.</text>
<g fill="white" stroke="#cddcda"><rect x="40" y="155" width="305" height="150" rx="12"/><rect x="378" y="155" width="305" height="150" rx="12"/><rect x="716" y="155" width="305" height="150" rx="12"/><rect x="1054" y="155" width="306" height="150" rx="12"/></g>
<g font-size="20" font-weight="700"><text x="60" y="190">1 / Clarify the tradeoff</text><text x="398" y="190">2 / Set the base</text><text x="736" y="190">3 / Define exceptions</text><text x="1074" y="190">4 / Apply to real work</text></g>
<g font-size="17" fill="#415d67"><text x="60" y="224">Task scope and known risks.</text><text x="60" y="253">Less effort or more coverage?</text><text x="398" y="224">Five axes, levels 1 to 5.</text><text x="398" y="253">Unspecified axes: balanced 3.</text><text x="736" y="224">Optional observed conditions.</text><text x="736" y="253">Explain benefit and drawback.</text><text x="1074" y="224">Use current tools and skills.</text><text x="1074" y="253">Restore base after context.</text></g>
<g fill="none" stroke="#126957" stroke-width="2" marker-end="url(#arrow)"><path d="M347 230H373"/><path d="M685 230H711"/><path d="M1023 230H1049"/></g>
<text x="40" y="360" font-size="22" font-weight="700">A temporary attention choice changes working behavior, not task routing</text>
<g fill="white" stroke="#cddcda"><rect x="40" y="395" width="420" height="200" rx="12"/><rect x="490" y="395" width="420" height="200" rx="12"/><rect x="940" y="395" width="420" height="200" rx="12"/></g>
<g font-size="22" font-weight="700"><text x="60" y="434">BASE / task-wide</text><text x="510" y="434">CONTEXT / high risk</text><text x="960" y="434">RESTORE / context ended</text></g>
<g font-size="18" fill="#415d67"><text x="60" y="475">Example: focus 2, other axes 3.</text><text x="60" y="508">Keep one component active.</text><text x="60" y="550">Tradeoff: cross-area drift risk.</text><text x="510" y="475">Example: verify 5, sync 4.</text><text x="510" y="508">Check assumptions and dependencies.</text><text x="510" y="550">Tradeoff: extra checking effort.</text><text x="960" y="475">Recompute from task base.</text><text x="960" y="508">Temporary levels do not leak.</text><text x="960" y="550">Follow the existing task order.</text></g>
<rect x="40" y="635" width="1320" height="75" rx="12" fill="#e0eee8"/>
<text x="60" y="666" font-size="19" font-weight="700">KEEP / required checks, permissions, task scope and shared-contract reconciliation.</text>
<text x="60" y="695" font-size="17">Unknown relevant facts: clarify. No minimum rounds. Setup supplies no scheduler or native thinking setting.</text>
<rect x="40" y="735" width="645" height="145" rx="12" fill="white" stroke="#cddcda"/><rect x="705" y="735" width="655" height="145" rx="12" fill="#fff8f5" stroke="#cddcda"/>
<text x="60" y="768" font-size="18" font-weight="700" fill="#126957">RECOMMENDED</text><text x="725" y="768" font-size="18" font-weight="700" fill="#9a4c32">AVOID</text>
<g font-size="18" fill="#415d67"><text x="60" y="802">Keep the plan in context; save a local attention map if asked.</text><text x="60" y="835">Choose only useful overrides; name their scope and tradeoffs.</text><text x="725" y="802">Require another repository or invent workflow steps.</text><text x="725" y="835">Claim level selection proves model adherence or token savings.</text></g>
<text x="40" y="912" font-size="15" fill="#415d67">Optional integration with agent-workflows is separate. Independent attention setup works without it.</text>
</g></svg>'''


def check(repo, write=False):
    folder = repo/'skills/agent-attention'
    outputs = {folder/'scripts/attention_setup.py': (repo/'scripts/attention_setup.py').read_text(encoding='utf-8'),
               folder/'references/setup.md': REFERENCE,
               folder/'assets/attention-example.json': json.dumps(template(), indent=2)+'\n',
               repo/'docs/assets/attention-setup.svg': picture()}
    errors = []
    for path, contents in outputs.items():
        if write:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(contents, encoding='utf-8', newline='\n')
        elif not path.is_file() or path.read_text(encoding='utf-8') != contents:
            errors.append('stale attention setup resource: '+path.relative_to(repo).as_posix())
    return errors
