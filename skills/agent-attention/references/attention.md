# Optional attention profile (experimental)

Load this layer once for the task, then retain its profile across workflow changes.
No settings or `balanced` means the existing host/workflow behavior, with all axes at 3.
These are five independent behavior controls, not model reasoning effort.

Levels 1–2 reduce discretionary effort; 3 is balanced; 4–5 increase effort.
Expected token direction follows effort, not a guaranteed total-token ordering.
Since 0.1.1, batch means decomposition depth, not batch size; re-select old non-default profiles.

## How to apply

1. Read explicit attention assignments separately from the task. Optional preview:
   `python <skill-dir>/scripts/attention.py --workflow direct --attention "focus=1,sync=4"`.
   Clear profiles can be applied directly; no helper execution is required.
   Unknown axes, duplicate assignments or levels outside 1–5 require correction;
   do not guess or silently coerce. Missing axes remain 3.
2. Use the selected levels before choosing each read, change or check.
   Retain dependency pointers in task context; no new state file is required.
   Narrow focus reduces active detail, not access to necessary evidence.
3. Apply non-default directives to the current task and any selected workflow. Keep
   authorization, mandatory checks, deadlines and break conditions intact.
   Warnings are tradeoffs, not permission to change requested levels.
4. Reconcile before dependent work whenever a shared contract changes,
   regardless of sync level. If a profile prevents safe/correct work, explain
   the conflict and propose a revised profile; never silently switch modes.
5. Report outcomes, material deviations with reasons, checks and
   remaining gaps. Stop when complete; no minimum number of iterations.

## Five levels per axis

| Axis | Level | Guidance |
|---|---|---|
| focus | 1 | One bounded action; retain pointers to relevant dependencies in task context. |
| focus | 2 | One component and its immediate contract. |
| focus | 3 (balanced) | Use the existing skill task scope; expand context when needed. |
| focus | 4 | Keep the changed component and its direct dependents in view. |
| focus | 5 | Keep the authorized end-to-end flow and cross-component contracts in view. |
| sync | 1 | Reconcile at task completion; reconcile earlier if a shared contract changes. |
| sync | 2 | Reconcile after each completed group of related work. |
| sync | 3 (balanced) | Use the existing skill checkpoints and reconcile at important boundaries. |
| sync | 4 | Reconcile after each change that affects another component. |
| sync | 5 | Reconcile after each step that changes shared state or assumptions. |
| batch | 1 | Group straightforward related changes; use one acceptance check without optional intermediate decomposition. |
| batch | 2 | Use a few coherent work items; inspect only consequential intermediate boundaries. |
| batch | 3 (balanced) | Use the existing skill batch size for a complete bounded work item. |
| batch | 4 | Split related changes at dependency boundaries and inspect each meaningful intermediate result. |
| batch | 5 | Decompose consequential work into explicit reversible steps; inspect each result before the next dependent change. |
| explore | 1 | Start from supplied sources; follow required dependencies when discovered. |
| explore | 2 | Inspect the target and immediate references first. |
| explore | 3 (balanced) | Use the existing skill discovery strategy; expand for concrete unknowns. |
| explore | 4 | Proactively inspect direct dependencies and conflicting assumptions. |
| explore | 5 | Map the relevant authorized flow before selecting the first action. |
| verify | 1 | Check the direct result plus all mandatory and risk-triggered checks. |
| verify | 2 | Check the changed area and its immediate contract. |
| verify | 3 (balanced) | Use the existing skill risk-based verification. |
| verify | 4 | Add nearby regressions and relevant boundary cases. |
| verify | 5 | Add independent checks of consequential assumptions and affected contracts. |

## Task-specific interpretation

- Code: batch controls decomposition and intermediate inspection; sync reconciles caller/schema/test contracts.
- Debug: preserve hypothesis attribution even at low decomposition; required risk controls take precedence.
- Review: higher decomposition separates consequential review angles; no finding quota or edit authorization.

## Tradeoffs

Narrow focus can reduce repeated context, but may cause stale assumptions and rework.
Wide focus can improve cross-component awareness, but may increase reading and distract
from the next concrete action. Frequent sync can reduce drift but adds overhead.
Low decomposition can reduce handoffs but make rollback and attribution harder.
More exploration and verification consume effort without guaranteeing useful findings.
Token savings and task-quality effects are hypotheses until measured.

Avoid narrow focus + low decomposition + sparse sync for shared-contract changes.
Do not lower mandatory checks, widen scope, run extra agents, or wait just
because a slider is high. This helper prints guidance; it never executes tasks.
