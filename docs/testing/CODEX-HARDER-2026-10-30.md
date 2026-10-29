# Harder Codex cases and acceptance repair

Report date: 2026-10-30; model attempts ran on 2026-10-29 UTC (2026-10-30 in
Asia/Bangkok). Source base: `262f0595c22478809591dad6d49352d1613bc4ab`.
See the [sanitized trial data and frozen hashes](CODEX-HARDER-2026-10-30.json).

## Outcome

Sixteen of eighteen planned Codex attempts ran: fifteen completed PASS, one
capacity-failed session remains FAIL, and two remaining attempts are NOT_RUN.
The suite stopped immediately on the capacity error and made no replacement calls.
Both harder cases completed all six attempts with independent acceptance PASS.
The interrupted cents attempt also passes acceptance, but that does not make its
session successful. Its token usage is unavailable, not zero. All sixteen
attempts retain protected sources and have no failed completed shell commands.

| Case | Low mean total | Balanced mean total | High mean total | Known-usage samples per profile |
|---|---:|---:|---:|---|
| Ledger transfer | 56,912.5 | 56,994.5 | 130,003.5 | 2 / 2 / 2 |
| Dependency planning | 47,870 | 65,203.5 | 83,831.5 | 2 / 2 / 2 |
| Integer cents, interrupted | 46,286 | 62,596 | 63,103 | 1 / 1 / 1 |

On ledger, low and balanced differ by about 0.14%; high uses about 2.28 times the
balanced total with the same acceptance outcome. On dependency planning, low's
mean is about 26.6% below balanced and high's about 28.6% above it. These are
descriptive within-task observations from two samples per profile, not significant
effects or a general Codex average. Do not pool heterogeneous task means. The
interrupted cents block has only one usage sample per profile and is not a
completed repeated comparison.

Input includes cached input; output includes reported reasoning. Total is input
plus output, with neither subset added twice. The JSON includes input/cache/output
breakdowns, individual samples, median, range and sample standard deviation when
at least two samples exist. Missing usage prevents computing the full campaign
cost. Token totals do not establish monetary savings or broad quality superiority.

## Design and checker controls

Three versioned cases are stored under `benchmarks/cases/`:

- `ledger`: exact positive-integer validation, unsuccessful transfers without
  state mutation, overdrafts, idempotent replay and conflicting requests, receipt
  aliasing, arbitrary-size balances and conservation across repeated transfers.
- `dependencies`: transitive closure, deterministic lexicographic topological
  ordering, unknown names, reachable/unrelated cycles, duplicate requests,
  non-mutation, independently enumerated orders on twenty seeded small DAGs, and
  a 1,500-node chain without recursive-stack failure.
- `cents`: the original integer rounding and discounted-shipping repair, retained
  as a separately labeled control task rather than pooled with harder tasks.

Each case plans low/balanced/high/high/balanced/low, setting all five axes to 1,
3 or 5. Case blocks run ledger, dependencies, cents, sequentially. This alternating
order is not randomization and observations need not be independent. Every trial
starts a fresh Git workspace with the same frozen skill and case bytes. Reference
implementations are checker controls only and are not copied into model workspaces.
Before model calls, all three references pass; original-broken, wrong-content,
missing-file, early-exit and forged-output controls are rejected for each case.

Codex CLI 0.165.0-alpha.1.2 requested GPT-6.1 Sol (`gpt-6.1-sol`), keeping native
reasoning effort fixed at medium on Windows. The Python oracle uses 3.14.7.
Requested model identity is not independent backend attestation. Actual prompt
inspection after excluding 177 external host skills shows one fixture-local Agent
Attention candidate and no parent project instructions. Plugins/apps/memories and
multi-agent execution are disabled. Full home/runtime isolation is NOT_VERIFIED:
authentication home, host implementation and service cache remain shared.

## Five reproduced false-PASS cases

New regressions were executed against an untouched archive of 0.2.2 (`262f059`)
using real local Git and Python processes with a deterministic CLI fixture, not a
real model. Sixteen tests ran; five adversarial subcases failed because the old
runner incorrectly returned PASS. No user data or global installations were used.

| Adversarial input | Old result | Repaired result and reason |
|---|---|---|
| Import exits with `SystemExit(0)` before assertions | False PASS | FAIL: no completed-oracle marker |
| Import prints PASS then exits early | False PASS | FAIL: fixed output is not completed acceptance |
| Allowed source rewrites protected FLOW.md during acceptance | False PASS | FAIL: oracle/source integrity checked after execution |
| Correct repair adds an unrelated source file | False PASS | FAIL: source inventory enforces allowed edits |
| Correct cached bytecode shadows incorrect checked source | False PASS | FAIL: fresh oracle copies source only, excluding bytecode |

The first cause was trusting process exit without establishing that assertions
ran. The second was checking only existing protected files before acceptance,
missing later mutations and new files. The third was validating one source
snapshot while importing behavior from ambient cached bytecode. These are
evaluator defects, not evidence that attention levels require different wording.

The repaired pipeline separates `workspace/` from harness metadata, rejects source
aliases/hardlinks and unexpected files, and runs the frozen checker on a fresh
source-only copy with isolated Python and bytecode writing disabled. A fresh
completion marker must appear after assertions. Integrity is checked again after
acceptance, including the oracle copy. Git internals and ordinary generated cache
artifacts are ignored by the source inventory, but caches are never imported into
the fresh oracle. This is acceptance hardening for the tested cases, not an OS
sandbox against arbitrary hostile Python or a proof against all introspection.

Both the original false-PASS regressions and legitimate references pass after
repair. A fresh recheck of the previous campaign's saved workspaces also accepts
all eight formerly completed sessions; nine of twelve saved workspaces pass the
new oracle overall, including the earlier capacity-failed session. This is an
acceptance replay, not new model execution or replacement of historical results.
The old reports and their original classifications remain unchanged.

A final prerequisite regression also proved that a missing CLI raised OSError
before any trial result/remaining-work record was saved. This startup path now
records BLOCKED_ENVIRONMENT and stops. Its seventeen-test baseline had one error;
the repaired tests PASS. This change followed the model campaign and used a
deterministic local CLI fixture only, with no additional real-model retry. The
JSON therefore separates measured source hashes from published source hashes;
acceptance, case and suite code did not change after the real calls.

## Every model attempt

| Case | Trial | Profile | Session | Acceptance | Total tokens |
|---|---:|---|---|---|---:|
| Ledger | 1 | Low | PASS | PASS | 48,168 |
| Ledger | 2 | Balanced | PASS | PASS | 65,565 |
| Ledger | 3 | High | PASS | PASS | 121,470 |
| Ledger | 4 | High | PASS | PASS | 138,537 |
| Ledger | 5 | Balanced | PASS | PASS | 48,424 |
| Ledger | 6 | Low | PASS | PASS | 65,657 |
| Dependencies | 1 | Low | PASS | PASS | 47,847 |
| Dependencies | 2 | Balanced | PASS | PASS | 65,031 |
| Dependencies | 3 | High | PASS | PASS | 83,507 |
| Dependencies | 4 | High | PASS | PASS | 84,156 |
| Dependencies | 5 | Balanced | PASS | PASS | 65,376 |
| Dependencies | 6 | Low | PASS | PASS | 47,893 |
| Cents | 1 | Low | PASS | PASS | 46,286 |
| Cents | 2 | Balanced | PASS | PASS | 62,596 |
| Cents | 3 | High | PASS | PASS | 63,103 |
| Cents | 4 | High | FAIL: capacity after work | PASS | Unknown |
| Cents | 5 | Balanced | NOT_RUN | NOT_RUN | Unknown |
| Cents | 6 | Low | NOT_RUN | NOT_RUN | Unknown |

## Repository organization and verification

Evaluation internals now live in `scripts/evaluation/`: versioned case loading,
source/acceptance checks, the runner and suite orchestration. Existing
`scripts/evaluate_effort.py` CLI/import names and offline campaign readers remain
compatible. `scripts/evaluate_suite.py` adds bounded multi-case execution with a
global environment stop. Source/case/skill hashes are recorded before calls;
source drift between case blocks also stops execution. Real model calls remain
opt-in and are never part of CI.

The [benchmark guide](../../benchmarks/README.md), [testing index](README.md) and
[documentation map](../README.md) distinguish evaluation machinery, installable
helpers and historical evidence. Old files were not renamed or moved, preserving
existing report links. Unrelated setup-packaging edits are excluded from publication.
Attention instructions, generated skill resources and semantics 0.1.1 are unchanged.

Working-tree validation: 100 tests, 97 PASS and three symlink skips; generated
resources and diff checks PASS. The working tree includes an unrelated setup test,
so publication-snapshot results are recorded separately in the JSON/release
evidence: 99 tests, 96 PASS and three symlink skips, with generated resources PASS.
That source/fixture snapshot is commit `94c05ab23e312ff3126ac2b51904eb3f17150d61`;
only documentation changes follow it. Local Python 3.11/3.12 and Linux were NOT_RUN: only Python 3.14 is
installed; no runtime was installed for this task. New remote CI is NOT_VERIFIED
until its own result is observed. Private raw traces and failed baseline logs
remain local; published hashes identify retained bytes, not independent attestation.

## Practical guidance

Use balanced as a starting point. Low can reduce work on a well-bounded repair,
but the ledger difference here is negligible and broader regression behavior is
unknown. Increase relevant axes temporarily when dependencies or consequence
justify extra inspection; avoid raising every axis routinely just to appear
thorough. High's extra token use did not improve acceptance on these two harder
fixtures, but that does not prove it never helps on other tasks.

Keep acceptance independent, version cases, record all attempts, separate cache
from uncached input, and stop on unavailable prerequisites. Avoid forcing strict
token ordering, treating capacity errors as correctness failures, hiding retries,
calling missing usage zero, weakening mandatory checks or advertising these
per-task means as universal Codex savings. A larger randomized multi-task study
with separate axis controls is future work, not a result of this campaign.
