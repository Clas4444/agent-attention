# Optional attention setup

Use `$attention-setup` from its independent skill, or `$agent-attention setup`
from the profile skill, to design an attention plan for an existing task.
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
The map includes scope, exact sources, condition provenance, fully resolved
guidance for base and each context, invariants and combination warnings. It can
be read without an installed helper; it does not activate itself. Re-export a
new map after changing the plan or semantics; saved maps are snapshots.
Keep it private; force-add/manual sharing bypasses ignore rules. Existing
output is never overwritten; an I/O error can leave a partial new directory.

Stop/finish according to the existing task. Mandatory checks, authorization,
shared-contract reconciliation and risk-triggered checks remain at every level.
Levels 1–2 reduce discretionary effort; 3 balanced; 4–5 increase effort. They do
not configure native model thinking or guarantee token ordering or savings.

Only if the user explicitly wants graph integration, use the optional bridge
bundled with agent-attention to attach attention to an existing graph. The
standalone attention-setup skill does not bundle workflow_setup.py. Preserve
the graph's skills and routes; integration is separate from attention setup.
