# Attention Setup map: configuration and observed behavior

2026-10-31; Agent Attention 0.2.5 candidate, profile semantics 0.1.1.
Baseline: fc53f89a949142ce82577ad859abb856c2246e6c. See the
[sanitized capture](attention-map.json) for source hashes, order and all outcomes.

## Finding and repair

Old exported maps stored numbers but referred to selected guidance without
including it or providing a source. A standalone reader could not recover the
defined meanings from the artifact. A new regression failed before the repair.
Exports now embed all five axis directives for base and every context, including
balanced axes, invariants, combination warnings and semantics version. No helper
installation is required to read the result. The map still needs explicit use;
it is not automatically activated by being saved in an ignored folder.

All 3,125 base profiles pass high-risk -> editing -> ordinary selections
(9,375 selections), preserving input plans and restoring base without override
leakage. Maps contain guidance for every level 1..5. Full suite: 106 tests,
103 PASS, three symlink skips. Generated resources and diff checks PASS.
Initial default-temp permission failures, an incorrectly placed temporary output
and one wrong test working directory were environment/launch mistakes, not
profile regressions. Tests were rerun with a workspace-local temp outside the
source repository; elevated checks were needed for the existing hardlink case.

## Fixed-profile model comparison

Six separate Codex CLI sessions, requested gpt-6.1-sol, native effort medium,
180-second per-call timeout, one cents fixture per session. Order was old1,
new3, old5, new5, old3, new1. Only map contents differed within each level;
no profile skill/helper was installed in the fixtures. Every trace reads the map.
The independent frozen source-only oracle accepted all six repairs; protected
files stayed unchanged. No retry was discarded.

| All five axes | Old map total tokens | New map total tokens | Terminal commands old / new | Task result old / new |
|---|---:|---:|---:|---|
| 1 | 72,455 | 57,978 | 3 / 3 | PASS / PASS |
| 3 | 57,531 | 43,303 | 2 / 2 | PASS / PASS |
| 5 | 42,945 | 58,314 | 2 / 3 | PASS / PASS |

Each cell has n=1. Total tokens = input + output; cached input is already part
of input and reasoning output is already part of output. Usage is not a dollar
cost. Do not pool these into a general Codex average. The small task gives no
quality separation: old maps also succeed. New-map level 5 separates edits and
the mandatory check, but does not add a distinct independent check in that trial.
Level 1 also uses three terminal commands. This is insufficient evidence of
reliable effort separation or monotonic cost.

## Conditional-map behavior

Three additional sessions use the same new map: all axes base=1, risk=high
overrides all axes to 5. Only authoritative facts differ. Before running, the
rubric required missing risk to stop without edits; known risk required the
frozen task oracle to pass. Terminal traces and actual artifacts supplement
model statements; reporting a selected level alone is not adherence evidence.

- missing: PASS (manual audit); 28,759 total tokens; 1 terminal commands.
- high: PASS; 75,506 total tokens; 5 terminal commands.
- ordinary: PASS; 59,121 total tokens; 3 terminal commands.

Missing risk caused an actual stop: no source changes, no task check, and a
request for the authoritative risk fact. The trial scorer incorrectly required
the literal uppercase word BLOCKED and produced FAIL despite that behavior.
That original false negative is retained in JSON with a separate manual PASS;
the literal matcher is not a validated general semantic oracle. Task acceptance
FAIL/OracleIncomplete is expected when the correct behavior is to leave the
broken task untouched.

For risk=high, the trace selects high-risk, edits each source separately, runs
the required check, then executes a separate independent arithmetic/threshold
oracle over 12 values including zero, rounding boundaries, the shipping threshold
and a large integer. The protected shipping API is also checked. This is actual
additional verification, not just a final-answer claim. See the ordinary trial
and command counts in JSON for the contrasting observed base behavior.

This supports that an explicitly supplied conditional map can influence stopping
and checking in these sessions. It does not establish universal compliance,
reliable gains or a causal advantage over no map. Model restoration within a
single continuing session remains NOT_RUN; only helper restoration is tested.

## Limits and practical improvements

The first six launches could not initialize the CLI app-server inside the
sandbox: original FAIL records are retained and audited as BLOCKED before model
execution, with unknown usage. A fresh batch ran with normal CLI access; this
also uses the shared authentication/state home. Prior exact-path host-skill
exclusions were supplied, but clean host/home isolation is NOT_VERIFIED. Native
picker discovery is NOT_RUN. This campaign is separate from earlier averages.

Use balanced defaults; raise only the axes needed by an observed risk. In this
fixture the useful high-context improvement was an independent check, at added
cost. Do not raise every axis by habit, remove mandatory checks at low levels,
infer savings from cache totals, or add repeated checks merely to create a level
difference. Levels 2 and 4 have deterministic coverage but no new model trials.
The [setup guide](../../../guides/attention-setup.md) describes all five levels
and their tradeoffs. Saved maps are snapshots: refresh after plan changes.
