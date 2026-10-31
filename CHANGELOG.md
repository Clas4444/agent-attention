# Changes

## 0.2.5 — 2026-10-31

- Make exported attention maps self-contained: embed resolved five-axis guidance
  for base and every context, semantics version, invariants and combination warnings.
  Previously maps referred to selected guidance without including or locating it.
- Test all 3,125 base combinations across conflicting contexts and restoration;
  check exported guidance at every level. Profile semantics remain 0.1.1.
- Document explicit map application and snapshot refresh requirements.

## 0.2.4 — 2026-10-30

- Publish the standalone attention-setup skill already available locally, with
  its own entry instructions, UI metadata, reference, example and isolated helpers.
  Keep the main skill's older setup request compatible.
- Group guides, development notes, playground and dated reports; standardize
  document names and update live links. Preserve historical JSON bytes and report
  bodies, retaining original paths/hashes as provenance in captured data.
- Move resource generators into scripts/generators and audit metrics into
  scripts/evaluation. Keep stable CLI/core-helper paths and illustration style.
- Add layout/link/preservation gates and expand isolated setup execution checks.
  Profile semantics remain 0.1.1; no new model measurements are claimed.
- Stop tracking machine-local root AGENTS.md without deleting the local file;
  keep public maintenance rules in the development guide.

## 0.2.3 — 2026-10-30

- Reject five reproduced evaluator false-PASS cases: early exit, forged PASS
  output, protected-file mutation during acceptance, extra source files and
  cached bytecode shadowing. Check frozen sources in a fresh oracle workspace.
- Separate trial source workspaces from private metadata; detect source aliases
  and capture evaluator/case hashes before execution. Preserve old report readers.
- Group evaluation code under scripts/evaluation, keeping existing CLI/import
  entry points. Add versioned cents, ledger and dependency benchmark fixtures,
  reference/rejection controls and a bounded eighteen-call suite with global stop.
- Keep attention instructions, generators and profile semantics 0.1.1 unchanged.
- Record CLI startup failures as environment-blocked attempts and stop the suite
  instead of exiting without trial/remaining-work records.

## 0.2.2 — 2026-10-30

- Add evaluator-only host skill exclusions without modifying global settings;
  disable plugins and multi-agent execution in controlled calls. Record exclusions
  privately and require actual discovery evidence before claiming isolation.
- Preserve profile semantics 0.1.1 and installed attention guidance unchanged.
- Stop new calls on structured usage-limit/capacity errors, including failures
  after partial work. Keep partial attempts FAIL and remaining trials NOT_RUN.
- Publish the repeated Codex fixture comparison, including unavailable usage and
  original failed attempts; these are task-specific means, not global Codex averages.

## 0.2.1 — 2026-10-29

- Separate attention setup from workflow design. Interview for task scope, base
  levels, conditional attention contexts, tradeoffs and restoration only.
- Add a standalone attention-plan helper and private ATTENTION-MAP.md export;
  require no workflow graph, cursor, Loop skill or agent-workflows installation.
- Keep the existing graph-v1 helper as an optional integration bridge. Add distinct
  attention setup guidance/illustration, preserving the existing visual style.
- Test an installed attention skill with its graph bridge deliberately omitted.

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
