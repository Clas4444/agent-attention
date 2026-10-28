---
name: agent-attention
description: "Set task-wide attention behavior across workflows: focus width, reconciliation cadence, batch size, exploration breadth and verification depth. Optional independent guidance; not a model reasoning-effort control."
---

# Agent Attention

Use when the user requests an attention profile for a task or explicitly invokes
this layer. It works with direct tasks, Loop and other skills without modifying
their instructions or recursively calling them.

## Activate once

1. Read [the profile reference](references/attention.md). Parse only the user's
   explicit attention settings; missing axes stay 3 (balanced). Unknown or repeated
   assignments must be corrected, not guessed. Optional read-only helper:
   `python <skill-dir>/scripts/attention.py --attention "focus=1,sync=4"`.
2. Record requested/effective levels in the task's existing checkpoint, together
   with goal, acceptance criteria, source pointers, shared contracts and next action.
   Do not create global configuration or write files outside existing authorization.
3. Keep this profile when switching workflow/skill during the same task. Reuse the
   checkpoint instead of loading or patching all skill files. A workflow label in
   helper output is descriptive; the helper never invokes it.
4. A step-specific override inherits unnamed axes and expires when that step ends.
   Record its scope, effective levels and restoration of the task profile. Use
   `inherit(task_levels, override)` in the helper module when composing overrides;
   the CLI resolves task profiles only. On resume, confirm the saved profile still
   applies; do not silently carry it into an unrelated task or another conversation.
5. Apply attention directives within the current workflow's required rules.
   Permissions, required tests, risk-triggered checks and source identity take
   precedence. Shared-contract changes require reconciliation before dependent
   work at every sync level. Explain conflicts/deviations, not silent changes.
6. Report profile, relevant checks and remaining gaps. Stop when complete, blocked,
   at deadline or after repeated non-progress. No level requires extra iterations.

No invocation means the agent's ordinary behavior; explicit balanced adds no
override directives. This is instruction guidance, not enforced scheduling,
native host settings, model reasoning control or proven token reduction.

## Example

`Use $agent-attention with focus=2,sync=4 for this task. Keep that profile while
implementing, testing and reviewing with the tools/skills already available.`
