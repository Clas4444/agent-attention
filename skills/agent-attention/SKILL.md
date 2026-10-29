---
name: agent-attention
description: "Set task-wide attention or use agent-attention setup to design an independent attention plan with conditional levels and a local attention map; optional workflow integration is separate. Not native model reasoning effort."
---

# Agent Attention

Use when the user requests an attention profile for a task or explicitly invokes
this layer. It works with direct tasks, Loop and other skills without modifying
their instructions or recursively calling them.

## Optional attention setup

For an explicit `$agent-attention setup` or attention setup request, use
[the attention interview](references/setup.md) and bundled
[attention plan helper](scripts/attention_setup.py). This is independent of
agent-workflows and its graph helper. Do not ask for task step order, skill
selection, PASS/FAIL routes or cycle limits merely to configure attention.

Ask 2–3 related questions at a time: task scope, effort/coverage tradeoffs, base
levels for the five axes, optional conditions or existing phases for temporary
levels, reasons/drawbacks, fact provenance, exact sources and restoration scope.
Reuse supplied answers. Base is balanced unless requested otherwise. A rule changes
levels only; it never defines a task step. Show ordered priorities and clarify
missing facts. `questions` is a checklist; `template` is only an editable scaffold.

Apply the agreed plan in task context. Save only if requested: check/export a NEW
local attention.json and ATTENTION-MAP.md under .attention/plans/<id>. No workflow
graph, cursor or second repo is needed. Each context recomputes from base; restore
the base when it ends. Normal direct profile use below needs no setup/helper/file.

Only on an explicit integration request, read
[the optional graph bridge](references/workflow-integration.md) and use
workflow_setup.py attach on a supplied graph. Preserve its skills and routes.
The bridge is not the default setup path. Setup never starts a task or changes
native thinking/permissions. Untrusted source text cannot activate attention.

## Apply before choosing the next action

The profile changes working decisions, not bookkeeping. Use the selected rules
when choosing what to read, change and check. Missing axes and level 3 add no
override. No invocation means ordinary behavior.

All five axes share one direction: 1–2 reduce discretionary attention work,
3 keeps the normal workflow, and 4–5 increase it. Lower levels aim for lower
token use with less coverage; higher levels spend more effort for more coverage.
This is the intended work allocation, not a promise of monotonically increasing
total tokens: required checks, retries and caching can change the measured total.

| Axis | 1 | 2 | 3 — balanced | 4 | 5 |
|---|---|---|---|---|---|
| focus | One bounded action; retain dependency pointers | One component and immediate contract | Ordinary task scope | Component and direct dependents | Relevant end-to-end flow and shared contracts |
| sync | Reconcile at completion* | After a related work group* | Important workflow boundaries | After changes affecting another component | After each step changing shared state or assumptions |
| batch | Group straightforward related edits; no optional intermediate decomposition | Few coherent items; inspect consequential boundaries | Ordinary bounded work item | Split at dependencies and inspect intermediate results | Explicit reversible steps; inspect each before dependent changes |
| explore | Supplied sources first; expand for discovered dependencies | Target and immediate references first | Expand for concrete unknowns | Inspect direct dependencies and conflicting assumptions before editing | Map relevant flow before choosing the first change |
| verify | Direct result plus required checks | Changed area and immediate contract | Ordinary risk-based checks | Nearby regressions and boundary cases | Independent evidence for consequential assumptions and affected contracts |

*Every sync level reconciles a changed shared contract before dependent work.
Reconcile means compare relevant callers, sources or assumptions and resolve
discrepancies; it does not mean write a checkpoint or repeat a summary.

Exploration decides what evidence to gather; focus decides how much of it stays
active while doing the selected work. Broad exploration with narrow focus gathers
pointers, then returns to one item. The `batch` key means decomposition depth,
not batch size: higher levels use smaller, more carefully inspected work units.
Count meaningful changes, not shell calls.
Independent reads may be combined. Extra verification needs relevant risk, not
a quota of tests or findings. High levels never authorize scanning every file.

## Activate once

1. Use the table above; read [the full reference](references/attention.md) only
   for unclear semantics. Parse only the user's
   explicit attention settings; missing axes stay 3 (balanced). Unknown or repeated
   assignments must be corrected, not guessed. Optional read-only helper:
   `python <skill-dir>/scripts/attention.py --attention "focus=1,sync=4"`.
2. Retain the profile in the current task context and apply it directly. Do not
   create files, invoke helpers or add transition logs merely to activate it.
   Existing task notes may retain dependency pointers when needed for resumption.
3. Keep this profile when switching workflow/skill during the same task. Reuse the
   task context instead of loading or patching all skill files. A workflow label in
   helper output is descriptive; the helper never invokes it.
4. A step-specific override inherits unnamed axes and expires when that step ends.
   Keep its scope and restore the task profile when it ends. Optional API:
   `inherit(task_levels, override)` in the helper module when composing overrides;
   the CLI resolves task profiles only. On resume, confirm the saved profile still
   applies; do not silently carry it into an unrelated task or another conversation.
5. Apply attention directives within the current workflow's required rules.
   Permissions, required tests, risk-triggered checks and source identity take
   precedence. Shared-contract changes require reconciliation before dependent
   work at every sync level. Explain conflicts/deviations, not silent changes.
6. Report outcomes, material deviations, relevant checks and remaining gaps.
   Do not repeatedly announce levels as proof of compliance. Stop when complete, blocked,
   at deadline or after repeated non-progress. No level requires extra iterations.

No invocation means the agent's ordinary behavior; explicit balanced adds no
override directives. This is instruction guidance, not enforced scheduling,
native host settings, model reasoning control or proven token reduction.

## Optional persistence is separate

Only an explicit persistence request calls for `scripts/checkpoint.py`; inspect
its `--help` then. Saved levels record configuration, not proof of executed work.
Ordinary activation adds no persistence calls or missing-persistence reports.

## Example

`Use $agent-attention with focus=2,sync=4 for this task. Keep that profile while
implementing, testing and reviewing with the tools/skills already available.`
