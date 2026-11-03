> Delivery update: conditional commit/push is now authorized. Earlier NO_COMMIT /
> NO_PUSH text below records the original experiment contract. No more model calls,
> budget reset, release/tag, version bump, peer/global edits are authorized here.
> See the RESULTS.json checkpoint for current delivery state.

# COORD-02 — Agent Attention independence and explicit coordination

**NO_PUSH / NO_COMMIT / NO_PUBLISH / NO_RELEASE.** Internal review only.
No version increase. State: READY_FOR_REVIEW; actual results are kept in
[COORD-02-RESULTS.json](COORD-02-RESULTS.json).

## repo / goal / scope

`agent-attention`, base `0698c709243a77d40b6f7affb4b2a5ec1dfc184c`.
Agent Workflows owns sequence, conditions, route/skill choice and termination.
Agent Attention only changes within-step processing. It neither dispatches a
peer skill nor grants permissions, changes routes or removes mandatory checks.
Standalone installation must work with no peer checkout. Combined use requires
an explicit versioned artifact; the normal attention setup never creates a graph.

Only this repository is edited. The peer's fixture was read as static contract
data to align bytes; no peer code is imported or executed. Old Copilot datasets,
markers, shared recovery receipts, global skills and parent maps are untouched.

## dependencies / peer_contract_version

- Product integration: optional vendored graph-v1 artifact; attention_schema=1,
  profile semantics 0.1.1. Existing direct profiles and missing-axis balanced
  defaults remain compatible.
- Experiment wire contract: `coordination-v1`, numeric `contract_version=1`,
  lowercase fault categories, `campaign` or `provider_account` scope, portable
  nonsecret evidence references. No shared runtime dependency.
- [Common fixture](../tests/fixtures/coordination-v1.json) equals the peer fixture
  byte-for-byte when checked: SHA-256
  `4d67c53d7b2fbe13c5fc5c9630e3cd8c0b307e2112adbb061bb959b3ed424a81`.
- Marker/ledger paths are campaign configuration or repo-relative local defaults,
  never fixed user-home installation paths. Markers do not alter product semantics.

## findings (file / line / evidence)

1. `scripts/evaluation/control.py:64,73`: legacy marker handling only checked
   existence and had no provider/domain/campaign model. It is retained for old
   explicit harness compatibility, not used by the COORD-02 adapter. New
   `scripts/evaluation/coordination.py` separates local faults from provider/account
   faults; unknown account domains pause the same provider, not other providers.
2. `scripts/evaluation/control.py:7`: the real Copilot error “No authentication
   information found” was not recognized before missing-usage classification.
   It is now recognized as auth root cause; old stored MALFORMED_USAGE records
   remain unchanged. AUTH_HOME is local; AUTH_ACCOUNT is provider/domain scoped.
3. `scripts/evaluation/coordination.py:112`: reservations need serialization across
   processes and campaign IDs. SQLite BEGIN IMMEDIATE plus persistent unfinished
   rows enforces max1inflight and cap24; failures/timeouts consume the budget.
   A Windows test exposed connections not closing on context exit; explicit
   connection cleanup repaired it before model calls.
4. `scripts/attention_setup.py:94`: selection starts from base and does not mutate
   plans. Exceptions/early stop after a selection do not leak into the next
   selection. This is helper semantics, not proof of model remembering restoration.
5. `scripts/workflow_setup.py:74,215,230,289`: versioned opt-in attachment changes
   attention fields only; conditions/routes/skills/acceptance are preserved.
   Unsupported graph versions, unknown patch fields and invalid profiles fail
   explicitly. `tests/test_coord_product.py` checks standalone and no cross-write.
6. `scripts/evaluation/publication.py:29`: old release receipts pinned mutable task
   files. New work legitimately makes old source receipts STALE. The historical
   audit still requires every old report artifact to match; it reports stale
   sources instead of rewriting an old receipt or claiming fresh release PASS.
7. `scripts/evaluation/coordination.py:19`: the first COORD-02 wire draft differed from the peer's v1 field names/provider
   labels. A campaign-local schema pause allowed the in-flight call to finish;
   three completed attempts and their source snapshot were retained. The fixture
   and serialization were aligned before a suffix continuation, without changing
   task prompts, selection order, skill bytes or the absolute task-wide counter.

## axis semantics / preregistered observable signatures

Balanced 3 is default. A higher number allocates more discretionary work along
that axis; it is not a quality score or a promise of monotonic token cost.

| Axis | Low 1 | High 5 | Tradeoff and interpretation |
|---|---|---|---|
| focus | Bounded action; necessary dependency pointers retained | Relevant end-to-end contracts in view | Broader active context costs reading; narrow detail can miss interactions |
| sync | Completion reconciliation, earlier on shared-contract change | Reconcile after consequential shared-state/assumption changes | Frequent sync adds overhead; sparse sync can accumulate drift |
| batch | Group straightforward changes; required acceptance remains | Explicit reversible steps and intermediate inspection | Higher means more decomposition, not larger batches |
| explore | Supplied evidence then required dependencies | Map the authorized flow/conflicting assumptions before editing | Extra discovery may distract; return to the actual task |
| verify | Direct result plus mandatory/risk checks | Independent consequential checks/boundaries | Extra checks can be redundant; low never waives mandatory checks |

Observations must use real read/edit/check/reconciliation traces. Command counts,
token use, state writes and final self-reports alone do not prove adherence.
Signature absence on a simple fixture is reported, not fixed by manufacturing
extra loops or lowering the acceptance oracle.

## acceptance / checklist

- [x] Standalone helper works from a copied skill, isolated Python, no peer checkout.
- [x] Combined graph-v1 is opt-in; routes/skills/conditions/acceptance preserved.
- [x] Balanced defaults and invalid/missing-relevant-fact diagnostics tested.
- [x] Pure selection restoration after exception/early stop; mandatory invariants
  equal across all 3,125 profiles; portable local map/no cross-write controls.
- [x] Campaign-local vs provider/domain scope, unknown identity, other provider,
  stale markers and append-only history tested against the common fixture.
- [x] Concurrent reservation/cap and uncertain-inflight failure paths tested.
- [x] Codex host login status and model-visible baseline/candidate inventories
  checked without reading/copying credentials; Copilot is never called.
- [x] Protocol, order, cases, rubric, signature expectations and max24 cap frozen
  before model execution. Source snapshots and old attempts retained.
- [x] Finish bounded pilot or stop on a real provider/campaign prerequisite;
  preserve every invocation, original labels and missing usage.
- [x] Build internal paired effect/quality/behavior figures when data allows;
  keep historical 66-pair series separate, with ticks/units/legend/source/n.
- [x] Final deterministic gates; READY_FOR_REVIEW with actual counts and NO_PUSH.

## experiments / results / limitations

Before calls, 35 focused contract/product/adapter/oracle tests passed (one
symlink skip). A prior temp-directory choice inside the source repo was rejected
by an existing benchmark guard; rerunning with a normal permitted temp root
resolved the harness setup error. These tests are not model sessions.

Codex preflight: authenticated via supported `login status`; baseline has zero
skills, attention has exactly its one local candidate, and neither includes
parent AGENTS context. Per-command exclusions disable 177 host skills; plugins,
apps, memory and multi-agent are off. Exec is ephemeral. Authentication stays in
the host-managed cache; no token or credential file is copied into a workspace.
No model/effort override is supplied. Requested model is the configured CLI
default; actual model is null/NOT_REPORTED unless transport explicitly reports it.

This isolates visible candidate/task context, not the entire authentication home
or operating system. Debug inventory is a preflight, not an attestation of the
later runtime prompt. Account domain remains unknown. No provider/account switch
is used to evade quota. The pilot is n=1 per condition, descriptive only.

Three initial attempts completed before local wire-alignment pause. The next
protocol continues the exact unexecuted suffix; it does not restart the seed or
budget. Calls across both protocol snapshots share one persistent cap24 ledger.
Historical Copilot data/old Codex map studies remain separate from new results.

## unresolved / evidence_paths

Pilot complete:24/24 CLI,24 completed turns,24 functional PASS,24 protected-file
integrity PASS,24 audited mandatory checks,0 retry/timeout/quota stop. Budget
remaining0 and inflight0. Actual model NOT_REPORTED on all24, not inferred.

Initial3 wire-draft attempts remain explicit DRAFT_MISMATCH;21 continuation
attempts use aligned v1. All12 pairs are descriptive; the strict aligned subset
has10 complete pairs. No old attempt or marker was removed. Data is n=1 per cell.

Unresolved: focus breadth not identified on the two-file fixture; actual model
identity and runtime-prompt/full-home/OS isolation unverified; real-model combined
Workflow+Attention and cross-context restoration NOT_RUN; no causal savings or
reliability estimate. Four high-level signatures have one observed trace example,
not universal compliance. No more calls are authorized within this exhausted cap.

Raw traces, measured source snapshots, context inventory and SQLite ledger stay
under ignored `.loop/coord-02/`. Sanitized observations, protocols, source tables,
SVG/PNG and semantic review are in [internal evidence](../docs/testing/reports/2026-11-03/coord-02/README.md).
The report separates metadata/unit fixes from product/model behavior evidence.
No artifact is committed or pushed. Parent review will inspect files directly.


## changed_paths

Reviewable changes are limited to experiment coordination/Codex adapter/trace
metrics/reporting, their deterministic tests, the common fixture, historical
receipt audit handling and this task package. Canonical skill semantics,
illustrations, versions, peer/global files and old shared receipts are unchanged.
The exact current list is in COORD-02-RESULTS.json.

## tests / result summary

- Pre-model focused gate:35 tests,34 PASS,1 skip; no model calls in tests.
- Final full gate:139 tests,136 PASS,3 symlink skips; assets, task links and diff PASS.
- Both PNGs rendered/viewed. All pilot data is new; historical66 is separately
  linked, not pooled. Old artifact receipt PASS; changed source receipts STALE.
- Metadata false positive reproduced from the measured source snapshot: reading
  checks.py formerly counted as execution; corrected parser rejects it. All24 real
  mandatory executions still pass the independent trace audit.
- NO_PUSH / NO_COMMIT / NO_RELEASE. Next: parent/human review of this diff and
  explicit unresolved limitations. Do not restart pilot, change provider or reset24.
