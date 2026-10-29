# Repeated Codex composite-profile comparison

Report date: 2026-10-30. Model attempts ran on 2026-10-29 (UTC).
These are means for one small repair fixture, not average token consumption for
Codex in general. See the [machine-readable record](CODEX-COMPOSITE-2026-10-30.json).

## Frozen comparison

Twelve planned attempts: four each with all five axes at 1 (low), 3 (balanced)
and 5 (high). Order: low/balanced/high/high/balanced/low, repeated twice. Every
attempt uses a fresh Git fixture and a frozen copy of the same Agent Attention
skill. The task fixes integer-cent discount rounding and applies shipping to the
discounted amount. The unchanged acceptance script checks large integers and
shipping thresholds; protected source and skill hashes must remain unchanged.
Correct, original-broken, wrong-content and missing-file controls were checked
before model execution. Only the correct control passed.

Codex CLI 0.165.0-alpha.1.2 requested GPT-6.1 Sol (`gpt-6.1-sol`) with native
reasoning effort fixed at medium. This identifies the request, not an independently
attested backend. Windows Python 3.14.7 runs the external acceptance oracle.
Source base: `8fa035134a05008821471893c6f1ba72430ed2f6`; the JSON pins the actual
skill and fixture bytes. Unrelated local setup-packaging edits are excluded from
publication. The exact launch-time evaluator hash was not captured; the published
evaluator includes the subsequent quota repair and is hashed separately.

## Observed tokens

| All five axes | Planned / attempted | Completed PASS | Usage samples | Mean input | Mean cached input | Mean uncached input | Mean output | Mean total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Low: 1 | 4 / 4 | 3 | 3 | 56,656.3 | 52,138.7 | 4,517.7 | 344.7 | 57,001 |
| Balanced: 3 | 4 / 4 | 3 | 3 | 56,702.7 | 52,224 | 4,478.7 | 406.3 | 57,109 |
| High: 5 | 4 / 4 | 2 | 2 | 70,872 | 63,808 | 7,064 | 663.5 | 71,535.5 |

Means use every attempt with reported usage, including failures if usage is
available. Here all four failed sessions omitted usage, so only eight completed
sessions contribute. Missing usage is unknown, never zero. The full campaign
cost cannot be computed. Total means input plus output; cache is part of input
and reasoning is part of output, so neither is added again. No monetary-price
conversion was made.

| Profile | Individual known totals | Median | Sample standard deviation |
|---|---|---:|---:|
| Low | 62,429; 62,425; 46,149 | 62,425 | 9,398.1 |
| Balanced | 62,266; 46,352; 62,709 | 62,266 | 9,318.5 |
| High | 63,112; 79,959 | 71,535.5 | 11,912.6 |

Low's observed mean is only 0.19% below balanced, much smaller than the observed
spread. High's mean is 25.26% above balanced, with only two known-usage samples.
These are descriptive statistics, not significant effects, independent samples
or evidence of general savings. Failed-session missingness is not assumed random.
Individual totals are not strictly ordered by level. Do not tune instructions
merely to force low < balanced < high on this fixture.

## Every attempt, including failures

| Trial | Profile | Original recorded result | Independent acceptance | Total tokens | Audit explanation |
|---:|---|---|---|---:|---|
| 1 | Low | PASS | PASS | 62,429 | Completed |
| 2 | Balanced | PASS | PASS | 62,266 | Completed |
| 3 | High | PASS | PASS | 63,112 | Completed |
| 4 | High | FAIL | PASS | Unknown | Model capacity error after work |
| 5 | Balanced | PASS | PASS | 46,352 | Completed |
| 6 | Low | PASS | PASS | 62,425 | Completed |
| 7 | Low | PASS | PASS | 46,149 | Completed |
| 8 | Balanced | PASS | PASS | 62,709 | Completed |
| 9 | High | PASS | PASS | 79,959 | Completed |
| 10 | High | FAIL | FAIL | Unknown | Usage limit after a read action |
| 11 | Balanced | FAIL | FAIL | Unknown | Pre-action usage block; audited BLOCKED_ENVIRONMENT |
| 12 | Low | FAIL | FAIL | Unknown | Pre-action usage block; audited BLOCKED_ENVIRONMENT |

Original records remain eight PASS and four FAIL. Applying the corrected
classifier to the retained events gives eight PASS, two FAIL and two
BLOCKED_ENVIRONMENT. This replay is deterministic classification, not new model
execution. Nine final workspaces pass acceptance, including the capacity-failed
session; this does not make nine sessions successful. Protected inputs remain
unchanged in all twelve attempts and no completed shell command reports failure.
The original faulty runner made two further calls after the first quota error;
these attempts remain visible rather than being replaced with successful retries.

Completed low/balanced traces group related work; high traces add intermediate
or boundary checks. Trial 1 also repeats acceptance verification. These limited
observations support a strategy distinction, not guaranteed adherence to every
axis or a quality advantage. One small task cannot establish broader correctness.

## Verified evaluator defects and repairs

1. Ignoring user config did not remove installed host skills. A no-model prompt
   probe still exposed 177 unrelated skills; the discovery-skip feature probe did
   not remove them. The evaluator now accepts a private exact-path exclusion list
   as per-invocation configuration and disables plugins/multi-agent execution.
   No global installation or settings were modified. After exclusions, a fixture
   prompt probe contains just its Agent Attention candidate and fixture instructions,
   with no parent project instructions. Full home/runtime isolation remains
   NOT_VERIFIED: authentication home and service cache are shared. This is a
   controlled same-home comparison, not a certified clean A/B.
2. The runner only detected HTTP 429 text in stderr. Real quota errors arrived in
   JSON events, so it incorrectly continued. It now inspects structured error and
   turn-failure events as well as stderr for quota, rate-limit and capacity errors.
   It stops new calls even after partial work, retaining partial attempts as FAIL
   and remaining labels as NOT_RUN. Ordinary model prose and command output cannot
   spoof an environment block.

The initial sandbox prompt probe failed startup permissions. A proposed temporary
credential-copy method was rejected by automatic review before execution and was
abandoned. No credentials were copied. The accepted approach uses CLI-local
exclusions, documented in [campaign preparation](AXIS-CAMPAIGNS.md).
The host-exclusion regression initially failed with an unsupported argument, then
passed after implementation. Structured-quota regressions initially produced four
failures across fourteen tests, then passed after repair. These failed attempts
are preserved in the JSON record and private logs.

Final working-tree validation: 89 tests, 87 PASS and two symlink tests skipped
because creation was unavailable. Generated resources and `git diff --check`
PASS. The working-tree suite includes unrelated setup packaging; publication-scope
checks also PASS: 88 tests, 86 PASS and two symlink skips on a staged snapshot
excluding unrelated setup packaging; its generated resources PASS. Profile instructions and
semantics 0.1.1 are unchanged. A fresh real-model campaign after the quota repair
is BLOCKED by account usage; deterministic replay/regressions do not replace it.
Historical measurements are not pooled with this campaign.

## What to do and avoid

- Keep balanced as the ordinary starting point. For a narrow, well-understood
  repair, lower discretionary work while retaining all mandatory checks; this
  sample does not demonstrate a material low-versus-balanced token saving.
- Increase relevant axes when consequential boundaries or dependencies justify
  extra checks. High added checking here but did not demonstrate a broader quality
  improvement, so avoid setting every axis to 5 routinely just to appear thorough.
- Compare identical task/model/skill snapshots, vary execution order, inspect real
  discovery and traces, and report sample counts, failures, cache and unknown usage.
  Next research should include more task types and controlled individual axes.
- Avoid counting unavailable usage as zero, counting cache/reasoning twice,
  selecting only passing retries, treating quota failures as reasoning failures,
  inferring money saved from token totals, or publishing these means as a universal
  Codex average. Do not alter mandatory correctness checks to manufacture savings.

Private traces and prompt inventories remain local. Published hashes identify
retained files, not independent attestation. Reproduce the design with
`python scripts/evaluate_effort.py --repeats 4 --plan`, verify the acceptance
controls and actual discovery, then execute only when account prerequisites allow.
