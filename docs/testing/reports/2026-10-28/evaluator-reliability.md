# Evaluator reliability — 0.1.2 candidate

This records the internal pre-setup candidate, included in 0.2.0 without a
separate 0.1.2 publication. Current expanded counts are in
[setup validation](../2026-10-29/workflow-integration.md); the 50-test count below is historical.

This patch changes measurement reliability, not the five-axis policy. Semantic
profile version remains 0.1.1, so existing 0.1.1 checkpoints remain compatible.
Earlier model measurements retain their original hashes and denominators; no
new model performance measurement is claimed by these tests.

## Result rules

PASS requires a completed CLI turn, exit 0, unchanged protected inputs and a
passing independent acceptance script. A zero exit or self-reported success
without turn completion is insufficient. Tool-command outcomes remain available
in the per-trial action records; acceptance PASS does not certify every command.

An HTTP 429 before any recorded action, completion, protected-input change or
implementation change is BLOCKED_ENVIRONMENT. The campaign saves the attempt,
stops further model calls and writes remaining profile labels to not-run.json.
Those labels are not attempts or failures. A 429 after work started remains FAIL;
rate-limit text cannot excuse partial work or missing/deleted implementation.

Invalid usage is retained as FAIL with usage_error and unknown usage rather than
dropping the trial or inventing zero cost. An acceptance timeout/error is recorded
as FAIL with acceptance_error. Missing usage remains unknown even if correctness
otherwise passes. Cached input is still a subset of total input.

## Local checks

The pre-setup candidate suite contained 50 tests, including real disposable Git baselines and real
acceptance scripts with a deterministic CLI fixture. It verifies successful work,
forged completion, oracle tampering, invalid usage, oracle timeout, deleted work,
and stopping after a pre-action rate limit. These fixture outcomes are evaluator
tests, not model attempts; they must not inflate the real-Codex success counts.

Run `python -m unittest discover -s tests -v` and
`python scripts/attention_assets.py`. No model calls occur in these tests or CI.
The opt-in `scripts/evaluate_effort.py` still consumes account usage when run
against a real CLI; use a new output directory outside this source repository.

Windows/Linux CI for this candidate is NOT_RUN until publication. Previous
0.1.1 CI success does not certify this changed evaluator. Profile behavior and
illustrations remain unchanged; model repetition and new cost comparisons are
NOT_RUN in this maintenance patch.
