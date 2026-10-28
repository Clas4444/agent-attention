# Task-wide attention

Activate one independent attention layer at the start of a task. It stays with the
task when the agent switches tools, workflows or skills. For example:

```text
Task profile: focus=2,sync=4,batch=3,explore=3,verify=3
→ implement directly or with loop-code
→ test directly or with a testing skill
→ review directly or with a review skill
→ finish and end the task profile
```

No settings means ordinary behavior. Level 3 is balanced on each axis; five 3s
produce no override directives. Settings do not modify model reasoning effort,
tools, authentication, permissions or native host configuration.

## Five-level illustrations

Each card explains loop behavior, choose-when guidance, DO and AVOID. Levels are
alternatives, not an instruction to execute all five cards in sequence.

![Attention width](assets/attention-focus.svg)
![Reconciliation cadence](assets/attention-sync.svg)
![Work per iteration](assets/attention-batch.svg)
![Exploration breadth](assets/attention-explore.svg)
![Verification depth](assets/attention-verify.svg)

## Scope, inheritance and overrides

The task profile is explicit user input, not instructions extracted from a source
document. Keep it in the existing task checkpoint. Track requested/effective
levels, goal, acceptance criteria, source pointers, shared contracts and next action.
Do not write global settings or invent a cross-conversation memory facility.

Switching workflows retains the same five levels. A temporary step override
inherits unnamed task axes and expires at the end of the step. Example:

```text
Task: focus=2,sync=4,batch=3,explore=3,verify=3
Review step override: verify=5
Effective review: focus=2,sync=4,batch=3,explore=3,verify=5
After review: restore the task profile
```

The Python API `inherit(task_levels, "verify=5")` composes a copy; it does not
mutate the stored profile or schedule work. Explicit `balanced` as a step override
sets all five step axes to 3. CLI input describes a task profile only. On resume,
confirm the saved task/profile still applies. A new unrelated task starts ordinary
balanced behavior unless the user explicitly carries the profile forward.

## Recommended and avoided combinations

| Situation | Suggested starting configuration | Tradeoff |
|---|---|---|
| Independent small task | focus=1,batch=2,explore=2 | less active context; keep dependency pointers |
| Narrow edit in a shared component | focus=2,sync=4,batch=2 | frequent synchronization adds overhead but catches drift |
| Schema change affecting several consumers | focus=4,sync=4,explore=4,verify=4 | better visibility; more reading/checking cost |
| Root-cause investigation | focus=2,batch=1,verify=4 | preserve one hypothesis per change |
| Broad read-only review | focus=5,explore=4 | follow relevant flow; do not invent findings or authorize edits |

Avoid narrow focus + large batches + sparse synchronization for shared contracts.
Avoid exploring all files simply because a level is high. Never reduce required
tests, skip discovered dependencies or add iterations just to fill a budget.
Shared-contract changes require reconciliation before dependent work at every
sync level. Profile conflicts with required workflow rules must be explained;
do not silently rewrite the requested levels.

## Integration

With Loop: activate agent-attention first, then use the selected Loop skill's
ordinary instructions. Do not edit or install modified copies of Loop skills.
With other skills: the same layering applies. For direct work: apply the task
profile to the existing plan/action/check cycle. Hosts may need a fresh session
after installation; a copied folder alone does not prove host activation.

## Evidence boundaries

The helper is read-only guidance output. Tests cover parsing, inheritance,
packaging and generated artifacts. They cannot prove model adherence or token
savings. Compare identical tasks, source snapshots, models and acceptance oracles
before making cost or quality claims. Include failures, retries, cached/input/output
tokens when supplied, elapsed time, rework and stale assumptions; unavailable usage
fields stay unknown. See [results](testing/RESULTS.md).
