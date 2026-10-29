# Setup validation — 1.11.0 / 0.2.0 candidates

Repo 1 supplies conditional skills; Repo 2 supplies conditional per-step attention.
Both vendor the same self-contained workflow graph contract v1. Their runtime
modules do not import one another. The release/profile-semantic versions and
workflow schema version are separate concepts.

## What is tested

The shared contract suite covers optional skills/attention/both layers; typed
fact comparisons and explicit ordered fallbacks; skill/profile choice before
work; routing after evidenced PASS/FAIL/BLOCKED/NOT_RUN; cycle return and early
completion; maximum steps/cycles; per-step attention restoration; changed graph
hashes and invalid cursors; malformed graphs, unknown fields and skill catalogs;
attachment preserving skills/conditions/routes; bounded input; local map export,
no overwrite, no project escape and alias rejection; Git ignore behavior;
isolated-Python installed resources; and fact files avoiding shell interpolation.

The output-symlink test is skipped where directory symlink creation is unavailable;
this is not a passing alias test on that environment. Record skips separately.
Source and bundled helpers, reference, sample graph and illustration are checked
against their generators, then all native skill roots are synchronized.

## Final local candidate observations — 2026-10-29

| Candidate | Recorded checks | Explicit limits |
|---|---|---|
| Repo 1, 1.11.0 | 14/14 fixed gates PASS; 372 tests, 370 pass and two skips, Windows Python 3.14.7 | File- and directory-symlink creation tests are skipped for this Windows account; no fresh Linux/3.11 CI |
| Repo 1 changed-area check | 62 tests, 61 pass and one directory-symlink skip on Python 3.12 | Focused changed-area check, not a second full campaign |
| Repo 2, 0.2.0 | 73 tests, 72 pass and one directory-symlink skip on both available Python runtimes | Local deterministic tests, not new model or native-discovery trials |

Each repository has its own [captured candidate checks](SETUP-CANDIDATE-CHECKS.json).
Repo 1's final session is setup-1110-20261029-hardened, input fingerprint
`9b1bd72842c6d009656d88f52ae4677e6aecec932504928c6e7ffe6c3b084b55`.
The earlier failed routing campaign and pre-hardening PASS are retained as separate
records, not relabeled. Repo 1's base Git HEAD is still the prior published commit;
the dirty working-tree input fingerprint identifies this local candidate.

## Cross-repository integration

[Recorded fixture observations](WORKFLOW-SETUP.json) use actual local Python
assertions and two targeted fixture edits. The original Repo 1 graph is exported,
Repo 2 attaches modes without changing skills/routes, and shared helpers select
and advance the same cursor. Selected instruction paths are present in a real
disposable installation. The trace is:

1. Addition assertion fails; work FAIL routes back to work.
2. Addition is repaired and checked; work PASS routes to verify.
3. Addition boundaries pass but the global goal still fails on multiplication;
   verify PASS with done=false returns to entry, completing cycle 1.
4. Multiplication is repaired and checked; work PASS routes to verify.
5. Multiplication boundaries and global checks pass; done=true returns DONE after
   cycle 2 and five observed steps. No extra cycle is run.

This is a deterministic integration harness, with zero model calls. It verifies
graph/attachment/routing plumbing and actual fixture checks. It does not measure
a model's attention, prove a skill's instructions were followed or establish an
independent agent's ability to interview a user. Caller evidence is an observation,
not an authenticated execution log. The source hash pins the helper, not a new
published Git commit.

## Limits and publication

See the [current expectation audit](EXPECTATION-AUDIT.md) for observed deviations,
unsupported assumptions and pending checks; implementation is not host evidence.

Native skill-picker discovery, real-model setup interview quality, arbitrary
business workflow effectiveness and remote CI on these candidates are NOT_RUN.
Existing model evidence retains its old input pins; changing the loop gateway
or attention instructions does not renew those observations. Local validation
and installed script tests must not be relabeled as native discovery or model
runtime PASS. CodeQL repair validation in Repo 1 also remains a separate claim.

Run the focused contract suite and generator check, then the repository's full
gates before publication. Keep raw maps, interview answers and private paths in
ignored local directories. Publish only reviewed summaries. Schema validation,
route calculation and setup export never execute tasks or infer permission.
