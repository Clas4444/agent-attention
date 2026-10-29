# Release 0.2.4 — 2026-10-30

## Scope

Publish `skills/attention-setup` as an independently installable skill with its
own SKILL.md, UI metadata, reference, example and two bundled Python helpers.
Its entry point is `$attention-setup`; it requires neither Agent Attention nor
Agent Workflows. The older `$agent-attention setup` request remains supported.
The entry instructions, metadata and helper bytes match the existing local setup
installation; reference text now describes both entry points accurately.

Group current user guides, maintenance notes, playground and dated evidence into
separate directories. Use lowercase kebab-case for documents, snake_case for
Python and standard README.md/SKILL.md entry names. Generator implementations live
in `scripts/generators/`; audit counters join `scripts/evaluation/`. Stable CLI
entry points and core/bundled helper paths remain unchanged. See the
[repository layout](repository-layout.md) and [migration map](path-migrations.json).

Historical JSON stays byte-for-byte equal to the previously published snapshots.
Historical Markdown bodies are unchanged except link targets. Source paths and
hashes inside captures retain their original meaning; they are not rewritten to
match today's tree. Old commit permalinks preserve original locations; current
relative links follow the new layout without dozens of root-level redirect stubs.
The machine-local root AGENTS.md is no longer tracked; it remains on the local
filesystem, while public maintenance guidance lives in the development guide.

## Compatibility and installation

Install the whole chosen skill folder. Both skills can be copied and run on their
own under isolated Python. No global installation or settings are modified by this
release. The setup skill's existing explicit-invocation policy is preserved.

Profile semantics remain 0.1.1; task checkpoints remain compatible. Attention
plans still use attention_schema=1 and require no graph. The optional graph-v1
bridge remains in the profile skill, separate from attention setup. Core Python
helpers still require Python 3.11+. Generator output retains the illustration style.

## Verification

Run the full unittest suite, `python scripts/attention_assets.py`, and
`git diff --check`. Test standalone setup commands questions/template/check/select/
export from a temporary copy without the primary skill or workflow helper. Layout
checks verify current relative links, naming, migration destinations and preserved
historical JSON/report-body hashes. The full suite runs 104 tests: 101 PASS and
three symlink skips. The staged publication snapshot also passes all 104 tests
with the same three skips and generated-resource PASS, without local AGENTS/maps.
Diff and live-link checks PASS.

The first move attempt stopped on Windows' case-only RESULTS.md/results.md
collision. A temporary-name rename completed the move safely; the fresh snapshot
and preserved-data gates then passed. No historical values were changed.

The generic skill-creator validator is BLOCKED by unavailable PyYAML; it was tried
and failed during import. No dependency was installed. Repository metadata checks
and actual isolated helper execution are separate checks, not a replacement claim
for that validator. Native picker UI and new model trials are NOT_RUN. Historical
model results remain under the [results index](../testing/results.md).

## Rollback

Restore the previous Git revision or chosen skill payload while retaining local
attention plans, custom instructions and unrelated skills. Use the migration map
or an old commit permalink to locate previous documents. Do not rewrite historical
captures or silently migrate graph/cursor state to force compatibility.
