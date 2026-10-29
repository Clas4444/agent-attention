# Controlled Codex benchmarks

These versioned fixtures evaluate observable repair outcomes and token usage.
They are separate from the distributable Agent Attention skill and never run a
model in CI. They do not establish general token savings or model adherence.

| Case | Contract under test | Allowed implementation edits |
|---|---|---|
| `cents` | Exact integer rounding and discounted shipping boundaries | `discount.py`, `checkout.py` |
| `ledger` | Validation, rollback, idempotent replay, receipt aliasing, large integers | `ledger.py`, `validation.py` |
| `dependencies` | Transitive closure, lexicographic topological order, relevant cycles, deep chains | `graph.py`, `planner.py` |

Each `cases/<id>.json` contains original source, a task, an allowed-edit list,
unchanged acceptance checks and a reference implementation used only for checker
controls. References are never copied into model workspaces. The cases remain
separate datasets; do not combine heterogeneous token means into a Codex average.
The dependency checker enumerates small-graph permutations independently and also
checks a 1,500-node chain. The ledger checker tests unsuccessful operations without
state mutation, replay conflicts and references returned to callers.

## Plan and run

```text
python scripts/evaluate_suite.py --plan
python scripts/evaluate_effort.py --case dependencies --repeats 2 --plan
python scripts/evaluate_suite.py --cases ledger dependencies cents --repeats 2 --disabled-skills-file <private-exclusions.json> --output <new-directory-outside-source-repository>
```

The default suite plans eighteen calls: three cases, three composite profiles and
two repetitions. Each case runs low/balanced/high/high/balanced/low. Plans make no
calls or writes. Real execution consumes account usage, requires working CLI
authentication and stops the entire suite on quota, rate-limit or capacity errors.
It never replaces failed attempts. Source drift between cases also stops execution.
Inspect actual skill discovery first; see [campaign preparation](../docs/testing/campaigns.md).
Exclusions do not certify full home/runtime isolation.

## Acceptance boundary

Protocol schema 2 separates each trial's `workspace/` from raw traces and harness
metadata. A source guard checks protected files, deleted files, aliases and new
files outside the allowed list. Git internals and ordinary Python bytecode cache
artifacts are excluded from the source inventory. Cached bytecode is never copied
into the acceptance workspace.

The external checker copies expected source files into a fresh temporary directory.
It takes protected sources and `checks.py` from the frozen case, runs isolated
Python with bytecode writing disabled, and requires a fresh completion marker after
all assertions. Zero exit or a printed PASS alone cannot establish success. It
checks source integrity again after acceptance, including the temporary copy.
This prevents the tested early-exit, fixed-output, mutation and cache-shadowing
bypasses. It is not a sandbox for arbitrary hostile Python or a proof against all
possible checker introspection. Use only authorized local fixtures.

Source, skill and case hashes are captured before execution. Per-case summaries
separate PASS, FAIL, BLOCKED_ENVIRONMENT, missing usage and NOT_RUN trials.
Historical schema-1 reports remain readable; their original classifications are
not silently rewritten or pooled with the new oracle's results.

## Maintenance

Evaluation code lives in `scripts/evaluation/`; public entry points remain
`scripts/evaluate_effort.py`, `scripts/evaluate_suite.py` and
`scripts/effort_campaign.py`. Deterministic acceptance controls and orchestration
tests live in `tests/test_benchmark_*.py` and `tests/test_effort_runner.py`.
Run those plus the required full suite and asset check after changes. A passing
reference alone is insufficient: broken, wrong-content, missing and early-exit
controls must also be rejected before real calls.
