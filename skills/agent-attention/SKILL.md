---
name: agent-attention
description: "Apply an explicit five-axis attention profile within an authorized task or step; balanced by default. Optional attention setup is separate. No routing, permissions or native reasoning settings."
---

# Agent Attention

Use for an explicit profile request. The existing task/workflow owns WHAT,
NEXT and STOP; Attention only adjusts HOW within its scope. Do not select routes,
widen authority, waive checks or promise lower tokens. Trivial actions usually
need no profile.

## Compact activation

Missing axes stay3. Levels1/2 allocate less and4/5 more of the selected quantity:
focus = active context width; sync = reconciliation cadence; batch = decomposition;
explore = evidence discovery; verify = independent correctness checks. Higher
batch means smaller inspected units, not larger batches. More work adds overhead
and may not improve quality or produce monotonic token cost.

For non-balanced settings, compile the explicit user profile with the bundled
helper (no second repository needed):

```text
python <skill-dir>/scripts/attention.py --attention "focus=1,verify=5" --format prompt --scope work
```

If the caller already supplied an explicitly requested compiled contract1
handoff, apply it directly; do not add a model/tool roundtrip to reload this
skill or recompile the same profile. Unknown artifact versions require correction.

Apply this short output before reads, edits and checks. Load only an unclear axis:
[focus](references/axes/focus.md), [sync](references/axes/sync.md),
[batch](references/axes/batch.md), [explore](references/axes/explore.md),
[verify](references/axes/verify.md). Without Python, use selected references directly.
Balanced adds no override; do not load extra references/helpers merely as proof.
Unknown/duplicate axes or invalid levels require correction, not guessing.

Keep authority, mandatory/risk-triggered checks and source identity unchanged.
Every sync level reconciles changed contracts before dependent work. Focus does
not order extra searches; explore need not keep all evidence active. Sync compares
current sources/callers; verify independently tests correctness. No axis sets native
model effort or requires extra rounds, logs or state files.

## Scope and lazy optional paths

Retain the task base. A step override inherits its unnamed axes and expires on
exit/exception/early stop. Python callers use ProfileSession.scope; other callers
explicitly restore task context. Reconfirm on resume. No helper cleans a killed
host process or enforces model memory.

Only setup requests load [the interview](references/setup.md) and
scripts/attention_setup.py; standalone $attention-setup and legacy
$agent-attention setup remain available. Only explicit combined requests load
[graph-v1 integration](references/workflow-integration.md) / workflow_setup.py.
The supplied workflow retains routes/skills/stopping. Attention contract1 accepts
scope+levels only, requires opt-in and rejects routing/authority fields.

JSON CLI output stays compatible. [Full semantics](references/attention.md) and
scripts/checkpoint.py are on-demand. Save local maps/checkpoints only when asked.
Report outcomes, checks and material deviations, not repeated profile claims.
Stop with the existing task's conditions; no minimum iteration count.
