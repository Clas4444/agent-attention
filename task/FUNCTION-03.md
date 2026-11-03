> Delivery update: conditional commit/push is now authorized. Earlier NO_COMMIT /
> NO_PUSH text below records the original experiment contract. No more model calls,
> budget reset, release/tag, version bump, peer/global edits are authorized here.
> See the RESULTS.json checkpoint for current delivery state.

# FUNCTION-03 â€” usable scoped Attention, not a benchmark-only redesign

**NO_COMMIT / NO_PUSH / NO_RELEASE.** Base HEAD remains0698c70; COORD-02 diff
and evidence are retained. State: PARTIAL; ready for review. New task budget is at most12
Codex CLI invocations including failures/timeouts, max1inflight, append-only
under `.loop/function-03/`; the exhausted COORD-02 counter is not reused/reset.

## Product contract before implementation

- **Who/when:** a user/agent already has an authorized task or workflow step and
  explicitly wants a different HOW: active context width, reconciliation cadence,
  decomposition, discovery or verification. Useful for consequential dependencies,
  changing sources, competing explanations or costly uncertainty.
- **When not:** a trivial action with no meaningful tradeoff, an unrequested
  profile, native model effort/budget control, route/permission changes, or a
  general token-saving claim. Balanced defaults avoid unnecessary overrides.
- **Input:** existing axis=1..5 strings, balanced, or an explicitly opted-in
  attention contract1 artifact with full levels and a bounded scope identifier.
- **Observable behavior:** selected axes compile into a short, focused handoff;
  read/edit/reconcile/check decisions change within the authorized step. Focus
  controls active breadth, explore controls gathering; sync reconciles changed
  inputs/contracts, verify checks correctness; batch controls decomposition.
- **Output:** legacy JSON remains the default; new `--format prompt` emits only
  relevant non-balanced directives plus compact invariants. No scheduler/file
  write. Full references/setup/graph bridge load only on demand.
- **Default:** all five axes3, no override. No implicit skill or peer execution.
- **Boundary:** Workflow owns WHAT/NEXT/STOP. Attention never adds steps, changes
  routes/authority or waives mandatory/risk-triggered checks. Unknown formats or
  conflicts fail explicitly, never silently rewrite intent.
- **Scope/failure/stop:** temporary overrides inherit the task base and expire on
  normal exit, return or exception; explicit finish restores base and prevents
  re-entry. Missing required facts BLOCKED; malformed profile FAIL. Runtime
  process kill is not magically recoverable. Stop on completion/prerequisite or
  a task/provider-scoped experiment fault; never manufacture rounds.

## Acceptance preregistered before repair

- [x] Negative controls show absent compact compiler/scope restoration API and
  bloated eager entry; add backwards-compatible implementation, not renamed axes.
- [x] Compiler covers25 axis-level cells, omits other axes, preserves invariants
  and rejects route/authority/unsupported-version fields. JSON compatibility.
- [x] Enter/exit, nested inheritance, exception/early return/finish restore base;
  combined contract is opt-in and no peer checkout/import is required.
- [x] Skill entry, setup, generator source and user guide agree; images unchanged.
- [x] Rich cases preregister signatures, same task/tool/authority at both extremes;
  independent artifact/trace check before model, then freeze sources/order/budget.
- [x] Prioritize focus with related files+distractors; changing-source sync,
  intermediate-feedback batch, hypothesis explore, independent-bug verify.
- [x] At most12 real Codex CLI, separate FUNCTION-03 cap, host auth/context
  preflight. No Copilot, quota retry, provider switch, or old-grid resume.
- [x] Report product fixes vs tests vs actual adherence, all counters/wall time,
  failures/limits, before/after table and internal source data/figures/hashes.
- [x] Final gates and READY_FOR_REVIEW or honest PARTIAL/BLOCKED. No commit/push.

## Checkpoint

12/12 new model calls completed; budget zero remaining. All functional/integrity/
full-check gates PASS. Product repairs ready for review; five-axis behavioral proof
remains PARTIAL (focus and verify contrast not demonstrated). No further calls.
See ../docs/testing/reports/2026-11-03/function-03/README.md, manual-review.json and gates.json. Final local
suite 150 tests:147 PASS,3 skips. No commit/push/release/global install.
