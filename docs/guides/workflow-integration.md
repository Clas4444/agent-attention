# Workflow integration

For independent **`$agent-attention setup`**, use the
[attention setup guide](attention-setup.md). It requires no workflow graph,
agent-workflows installation, skills or routing cursor.

This page describes the separate, explicit request to attach attention to an
existing compatible graph. The self-contained workflow_setup.py bridge is retained
for graph-v1 compatibility; it is not the attention setup entry point. Existing
skills and routes are supplied by that graph and remain unchanged.

![Optional graph integration](../assets/workflow-setup.svg)

## When integrating with a supplied graph

The agent asks two or three related questions at a time and reuses known answers.
It gathers the outcome, step list, criteria, exact source pointers, condition
facts and their provenance, profiles for each branch, result routes, cycle end,
limits and project/output location. Missing facts are clarified rather than
treated as false. Show ordered branch priorities; fallback is explicit and last.

For example, the same verify step can select verify=5 when risk=high, and ordinary
verify=3 otherwise. The work step can use focus=2,batch=4 for a bug and focus=3
otherwise. Task settings are inherited by every branch; unnamed axes stay at
their task levels. A branch override expires when that step ends. The next
selection recomputes effective levels instead of carrying the previous override.

Profiles affect work choices described in the attention guide; they do not set
native model effort, permissions or a token budget. Higher levels allocate more
discretionary attention, without guaranteed per-run token ordering.

## Attach to an existing agent-workflows graph

Use the shared schema_version=1 graph. It has steps, ordered pre-work bindings,
post-observation transitions, exact sources, criteria, condition fact names,
provenance and bounded cycle/step limits. A closing cycle_end route explicitly
returns to entry. DONE finishes immediately; STOP ends or pauses the workflow.

The attachment helper changes attention fields only. Example modes.json:

```json
{"attention":{"sync":4},"steps":{"verify":[{"binding":0,"attention":{"verify":5}},{"binding":1,"attention":{"verify":3}}]}}
```

```text
python scripts/workflow_setup.py attach --file workflow.json --patch modes.json
```

The returned document preserves skill names, when conditions and transitions,
and leaves the input file unchanged. Indexes are zero-based in the displayed
binding list. Unknown/duplicate indexes and route-editing fields are rejected.
Review and save the result as a new draft, then validate/export. To add conditions
that do not exist in the graph, explicitly revise the ordered graph in the setup
interview; attach does not invent branches. The two repos need no runtime import
of one another and remain independently installable.

## No existing graph?

Use [independent attention setup](attention-setup.md). Do not manufacture a graph
just to configure attention. To design task steps and skill choices, use
agent-workflows workflow setup, or another separately selected workflow designer.
The bridge retains its older graph template/check/export CLI for compatibility;
those graph tools are optional and are not required to install or use this skill.

## Follow the current route

The map names the project root, 0–5 exact sources per step, candidate installed
instruction paths, acceptance criteria, branch facts and their provenance. Load
only the current step and selected binding; do not scan every file or skill.

```text
python scripts/workflow_setup.py start --file workflow.json --facts-file facts.json
python scripts/workflow_setup.py select --file workflow.json --state cursor.json
python scripts/workflow_setup.py advance --file workflow.json --state cursor.json --status PASS --evidence "required checks passed" --facts-file observed-facts.json
```

start/advance print state; retain it in existing context or an explicitly chosen
local cursor file. They do not write that file or execute work. The agent actually
does and checks the authorized step, then reports PASS/FAIL/BLOCKED/NOT_RUN with
real evidence. The helper routes a supplied observation; it cannot judge task
success or authenticate a manually edited cursor.

Returning from cycle_end to entry counts one cycle. Maximum cycles/steps return
STOP; DONE ends immediately. Also stop on user request, deadline, safety boundary
or repeated non-progress. The helper does not observe those host conditions by
itself. Changed graph hashes reject old cursors; review the design and restart
explicitly. Required checks and external-action boundaries always remain.

Missing condition facts print JSON BLOCKED and exit 2 without changing state.
Invalid configuration exits 1; exit 0 means a helper operation succeeded, not
that every routed step or stopped business task passed.

## Compatibility and evidence

Graph integration introduced in 0.2.0 retains axis semantics version 0.1.1. Existing task-profile checkpoint
files remain compatible; workflow cursors are a separate graph-bound format and
are not interchangeable with checkpoint.py state. Ordinary profile use still
requires no graph or cursor. Setup does not alter installed downstream skills.

Graph/attachment/private-export/installed-Python checks are deterministic tests,
not new model attempts or native-discovery proof. Existing 0.1.1 model measurements
retain their old pins. New real-agent graph interviews/loop effectiveness are
NOT_RUN. See the [historical graph capture](../testing/reports/2026-10-29/workflow-integration.md)
and [current repository checks](../development/release.md); neither configures native reasoning.
