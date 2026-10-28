# Standalone repository validation

Initial version: 0.1.0. Date: 2026-10-28.

This repository was extracted from a Loop attention prototype and then changed
into an independent task-wide instruction layer. The prototype's 14-gate campaign
and 352-test result belong to the original repository, not this new one.

## Current checks

Ten deterministic tests pass on the available Windows Python 3.14 runtime:

[Captured commands, results and source hashes](initial-validation.json) also
record the same ten tests passing under Python 3.12 and the generated-resource
check. These are checkout-byte pins, not independent model-execution evidence.

- Omitted settings / balanced produce no overrides.
- All 3,125 profiles preserve requested levels and the same invariant floor.
- Workflow labels can change without changing the task profile.
- Temporary overrides inherit unspecified axes and do not mutate the task profile.
- Invalid bases, duplicate/out-of-range settings and command-like labels fail.
- Risk warnings do not silently rewrite requested levels.
- Generated helper, references, HTML and SVG match source.
- Five explanatory illustrations each contain all five levels and DO/AVOID guidance.
- A single installed `agent-attention` folder runs with `-I -B` outside this repo
  and preserves unrelated files, without writing task artifacts.

The source tests are in `tests/test_attention.py`. Run:

```text
python -m unittest discover -s tests -v
python scripts/attention_assets.py
```

## Claims not established

Model adherence, cross-conversation persistence, native host picker activation,
token savings, and superiority over balanced behavior are NOT_RUN. State inheritance
is tested as data composition plus documented agent instructions; there is no
enforced scheduler or automatic interception of downstream skills.

The illustrations explain policy and tradeoffs, not performance measurements.
Compare the same tasks, model, sources and acceptance oracle before claiming
improvement, and retain failures/retries in total cost.

## Attribution

Original prototype base: agent-workflows main `6a8e60e`.
Prototype illustration revision: `e2b1b71`, retained in the original local Git
history after the remote experiment branch was deleted. MIT copyright is retained.
No old model-trial archive is republished as fresh standalone runtime evidence.
