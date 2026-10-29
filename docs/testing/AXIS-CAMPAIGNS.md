# Controlled attention campaigns

The original trial changed all five axes together. It could not establish which
axis caused a difference. The new planner can vary one axis and keep the other
four at balanced (3), with any unique set of levels from 1 through 5.

## Preview before consuming model usage

```text
python scripts/evaluate_effort.py --axis focus --levels 1 2 3 4 5 --repeats 2 --plan
```

This prints five explicit profiles and ten planned calls, with levels in forward
then reverse order. It does not invoke Codex or create an output directory, even
if --output is supplied. Repeats supports 1–10; it repeats the chosen level list
with alternating direction. This reduces some order bias but is not randomization.

Omit --axis to preview the existing composite low/balanced/high comparison.
Use --axis for level selection; --levels without --axis is rejected. --profiles
selects a custom order of composite labels and cannot be combined with --axis.

## Execute an explicitly selected design

Execution consumes account usage. Choose a new directory outside the source repo:

```text
python scripts/evaluate_effort.py --axis focus --levels 1 3 5 --repeats 2 --output C:/Experiments/focus-study --cli codex
```

The frozen protocol includes profile settings, planned order, source hashes and
acceptance criteria. Each trial retains input pins, prompt, raw trace and outcome.
The evaluator updates summary.json after each recorded trial. HTTP 429, structured
usage-limit errors and model-capacity errors stop the campaign and record remaining
labels as not run. Pre-action environment failures are BLOCKED_ENVIRONMENT;
failures after actions or source changes remain FAIL but still stop new calls. Interrupted or failed
attempts are not replaced with passing retries in the original record.

## Keep host skills out of the comparison

`--ignore-user-config` skips the user configuration file, not the installed
skill catalog. An unrelated global skill can add context or instructions to all
profiles. Do not infer isolation from this flag or from a model's claim.

Inspect actual discovery using the installed CLI's no-model prompt inspector
when available (`codex debug prompt-input`). Prepare a private JSON array of
exact external `SKILL.md` paths observed in that catalog, then pass
`--disabled-skills-file <private-json-file>` to the evaluator. These become
per-invocation `skills.config` exclusions; installed files and global settings
are unchanged. The local candidate skill must remain enabled. Plugins and
multi-agent execution are disabled for evaluator calls as well as apps/memories.
See the official [skill configuration documentation](https://learn.chatgpt.com/docs/build-skills).

Reinspect the fixture's actual catalog after exclusions. It should contain only
the fixture candidate, with the fixture's own instructions and no parent project
instructions. Keep discovery evidence and machine paths private. The protocol
records the exclusions but deliberately does not certify isolation. A shared
authentication home, service cache and unverified runtime context still limit
the comparison; label full isolation NOT_VERIFIED when it was not established.
No credential copying is required by this option.

## Read a saved report without running the model

```text
python scripts/effort_campaign.py --report C:/Experiments/focus-study
```

The report separates planned, observed, not-run, passing, failing and blocked
trials. Success rates exclude environment blocks; token means include all recorded
attempts with available usage, including failures. Unknown usage remains unknown,
with a separate missing-sample count. Input, cached input, uncached input, output
and total means are separate. Failed tool commands are also counted; a passing
acceptance check does not erase them. Duplicate or mislabeled trial numbers and
impossible usage are rejected instead of silently skewing the denominator.

Older composite protocol files with order/profiles remain readable and are labeled
legacy-composite. Report reading never changes a saved design, writes files or
starts a model. It does not combine unrelated campaigns or compare tasks with
different input snapshots.

## What is and is not verified

Tests cover all five axes at five levels, profile isolation, reversed order,
invalid designs, duplicate results, missing usage, failed-attempt accounting,
read-only CLI operation and execution with deterministic CLI fixtures plus real
Git/acceptance checks. These are harness tests, not model attempts.

New real-model single-axis campaigns are NOT_RUN for this candidate. Existing
composite measurements remain unchanged. A controlled design on one fixture does
not prove general causal effects, strict token ordering or monetary savings.
Use multiple task types and inspect action traces and quality alongside tokens
before drawing conclusions about an axis.
