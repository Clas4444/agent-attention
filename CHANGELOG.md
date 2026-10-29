# Changes

## 0.2.0 — 2026-10-29

- Add optional `$agent-attention setup`: interview for per-step conditional
  profiles, status branches, completion/cycle bounds and exact agent source maps.
- Share workflow graph contract v1 with agent-workflows 1.11.0. Attach attention
  to existing bindings while preserving skill choices, conditions and routes.
- Ship a self-contained validator/router, private export, example, reference and
  matching light illustration. Setup alone never starts execution.
- Preserve 0.1.1 axis semantics and task-checkpoint compatibility. Workflow cursors
  are separate graph-hash-bound state; they do not configure native reasoning.
- Include the internal 0.1.2 candidate below; that candidate was not pushed.

## 0.1.2 — prepared, 2026-10-28

- Add controlled single-axis campaigns, selectable levels/repeats, no-call preview,
  and automatic reports separating correctness, tool failures, cache and tokens.
- Read saved or legacy composite campaign results without invoking a model; reject
  duplicated/mislabeled results and preserve unknown usage and unrun trials.

- Require a completed turn and independent acceptance check before evaluator PASS.
- Retain malformed usage as a failed result with unknown cost, rather than losing
  the trial to an exception. Preserve input pins and private raw traces.
- Classify pre-action HTTP 429 as environment-blocked and stop remaining trials;
  partially executed or changed work cannot use this classification.
- Exercise the evaluator with deterministic CLI fixtures, real Git baselines and
  real acceptance checks, without consuming model usage in tests or CI.
- Preserve 0.1.1 profile semantics and checkpoint compatibility; no new model
  performance claims are inferred from these evaluator tests.

## 0.1.1 — 2026-10-28

- Align all five axes: lower levels reduce discretionary effort; higher levels
  increase it, with level 3 preserving ordinary balanced behavior.
- Change `batch` from batch size to decomposition depth. Re-select non-default
  batch values when migrating. Optional checkpoints reject unversioned or
  mismatched semantic profiles instead of silently reinterpreting them.
- Apply profiles directly to reads, edits and checks. Persistence is explicitly
  optional; no state file or helper call is needed for activation.
- Add real-Codex behavioral and effort-direction measurements, retaining failed
  attempts and limitations. Token ordering is an expectation, not a guarantee.
- Repair the isolated-Python optional helper and validate usage accounting.
- Accept legitimate Windows 8.3 temporary paths while retaining link rejection.

## 0.1.0 — 2026-10-28

Initial independent attention-layer prototype extracted from agent-workflows.
