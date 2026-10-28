# Effort direction — 0.1.1

The intended direction is **less discretionary work at levels 1–2, ordinary work
at 3, more work at 4–5** on each axis. This aims to move token consumption in the
same direction. It does not claim that all settings save tokens, or guarantee a
strict ordering of measured totals on every task.

`batch` now means decomposition depth, not batch size. Higher levels split work
more carefully and inspect intermediate results. The skill, resolver, guide,
illustration and browser preview use this meaning. Re-select old non-default
batch settings; the optional state helper rejects old or mismatched semantics.

## Fixed comparison

Six fresh Codex CLI trials request GPT-6.1 Sol, medium native reasoning effort,
in order low/balanced/high/high/balanced/low. Each composite profile sets all five
axes to 1, 3 or 5. The same task repairs integer-cent discount rounding and the
discounted shipping threshold. Only two implementation files may change.
Protected source/skill hashes and an unchanged acceptance script check results.
The instruction snapshot is frozen before running; prompts differ only in profile.

| Profile | Acceptance | Mean input, including cache | Mean cached input | Mean uncached input | Mean output | Mean input + output |
|---|---|---:|---:|---:|---:|---:|
| Low | 2/2 PASS | 85,277 | 60,032 | 25,245 | 318.5 | 85,595.5 |
| Balanced | 2/2 PASS | 97,924.5 | 78,592 | 19,332.5 | 317 | 98,241.5 |
| High | 2/2 PASS | 124,073 | 110,528 | 13,545 | 751 | 124,824 |

Mean total is about 13% below balanced for low, and 27% above for high. This
matches the expected direction **for these means**. One low run totals 98,360,
slightly above the second balanced run's 98,341: individual runs are not strictly
ordered. Uncached input runs in the opposite direction because cache reuse
differs. These figures are not evidence of the same ordering in monetary cost.

Input is cumulative across agent tool turns, including repeated host context.
Cached input is a subset of input and must not be added to it. Output includes
reported reasoning tokens; do not add those again. No API price conversion is
used. Mean elapsed times are 23.635 s / 29.984 s / 104.983 s; latency is not an
isolated measurement of thinking effort.

Traces show low grouping related changes with acceptance verification, while
high inspects dependencies and separates edits with intermediate assertions.
All six preserve protected inputs and call no profile/checkpoint helper or JSON
state file. They demonstrate a limited strategy distinction, not native model
thinking control or independently established effects of every axis.

## Tool failures and fixture correction

Acceptance succeeds in all six attempts, but three tool commands return nonzero.
The two high trials run git status outside a Git repository. Git diff there
compares the two supplied file paths, rather than showing a change diff. One
balanced trial receives exit 1 from that file comparison. The actual Python
assertions pass; these tool errors remain recorded separately from acceptance.

The evaluator now creates a real local Git baseline. Targeted high and balanced
regression attempts validate this correction separately; they are excluded from
the six-trial means. See the machine-readable record for their outcomes.

The high regression passes acceptance with all five shell commands exiting 0.
The balanced regression times out after 180 seconds before any task action;
stderr reports HTTP 429 Too Many Requests and retry backoff. It is classified
BLOCKED_ENVIRONMENT, not a passing regression or an attention task failure.
Raw harness status is FAIL/timeout and is retained alongside that classification.
No further model calls were made during the rate limit. Across these eight new
attempts: seven acceptance successes, zero observed task-execution failures,
one environment block. This is not eight successful runs or proof of stability
across tasks; the corrected-fixture balanced regression remains blocked.

## Reproduce and inspect

Run the opt-in evaluator with a working Codex CLI and a new output directory
outside this repo. It invokes the model six times and consumes account usage;
it is not part of unit tests or CI:

```text
python scripts/evaluate_effort.py --output <new-external-directory> --cli <codex-executable>
```

The output includes frozen skill resources, fixed protocol, raw JSONL traces,
protected-input pins and per-trial outcomes. Local raw runs for this report are
at `C:/Code/attention-effort-20261028` and its regression sibling. Published
[measurements and hashes](EFFORT-DIRECTION-2026-10-28.json) exclude raw host output.

## Scope and release checks

This is one task with two samples per composite profile and a fixed reversed
order, not a five-axis causal study or a claim that every level is independently
calibrated. No evaluation against 10–18 manual prompts was performed. Host
metadata, cache, service latency and required correctness work remain confounds.
Model identity is the explicit CLI request, not independent backend attestation.
Behavioral instructions were unchanged after freezing; optional-helper semantic
version guards were added afterward and are covered by unit tests.

29/29 unit tests pass on Python 3.14 and 3.12. Generated assets and documentation
links pass. Chrome preview matches the Python resolver at all five levels across
all five axes, and reset restores balanced. The first browser checker incorrectly
assumed a label lacked the displayed balanced suffix; correcting the checker
passed without a product change. The updated batch SVG was rendered and visually
checked for clipping and readable guidance. No guaranteed token saving or broad
production reliability is claimed.
