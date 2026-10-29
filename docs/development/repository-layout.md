# Repository layout and content conventions

Keep runtime helpers, installable skills, generated assets, current guides and
historical evidence separate. Do not copy machine-local maps or raw traces into
these public folders.
The workspace's root AGENTS.md and .loop maps remain local and are ignored by
Git; public maintenance conventions live here. Untracking a local instruction
file does not delete it from the working machine.

## Ownership

| Location | Canonical content | Maintenance rule |
|---|---|---|
| `skills/*/SKILL.md`, `skills/*/agents/` | Skill routing and UI metadata | Edit the intended entry point directly |
| `scripts/attention.py`, `attention_setup.py`, `checkpoint.py`, `workflow_setup.py` | Core helper behavior | Preserve independently bundled execution |
| `scripts/generators/` | Skill resource/reference and illustration sources | Regenerate with `python scripts/attention_assets.py --write` |
| `scripts/evaluation/` | Opt-in evaluator and reporting internals | No model calls in deterministic tests/CI |
| `benchmarks/cases/` | Versioned task inputs and independent controls | Keep cases and measurements separately pinned |
| `docs/guides/` | Current user instructions | Keep purpose, invocation, examples, outputs and limits consistent |
| `docs/development/` | Repository/release maintenance | Document ownership, compatibility and checks |
| `docs/testing/` | Current protocol and evidence index | Link to reports instead of duplicating old measurements |
| `docs/testing/reports/<date>/` | Historical Markdown/JSON captures | Preserve measured numbers, failures and source provenance |

The root `scripts/attention_assets.py`, `effort_campaign.py`, `evaluate_effort.py`
and `evaluate_suite.py` entry points remain available. Generator internals and
historical audit counters moved into their functional packages. The stable core
helper locations remain unchanged so bundled skills need no shared installation.

## Naming and content

Use lowercase kebab-case for guide/report/asset filenames and skill folders,
snake_case for Python modules/tests, and `YYYY-MM-DD` for report directories.
Keep standard names README.md, SKILL.md, CHANGELOG.md and LICENSE. Pair a report
and its JSON using the same stem. Use explicit product names in maintained prose.

Current guides explain when to use a capability, its actual invocation, examples,
outputs and limits. Skill entry points keep routing and essential constraints;
longer instructions go in a linked reference. Generated resources have one
canonical generator even when they are bundled in two independently installable
skills. Historical reports keep their original language and conclusions; only
relative link targets are updated when moving them.

Historical JSON bytes are unchanged by this reorganization. Embedded source
paths, hashes and versions describe the measured snapshot, not necessarily today's
layout. Do not rewrite them to make old trials appear current. The migration map
also records hashes of preserved JSON and report text with link URLs normalized.
Use current guides for executable commands and old commit permalinks for original
locations. No root-level compatibility stubs are kept for every former report.

## Verify changes

Run the full unittest suite, `python scripts/attention_assets.py`, and
`git diff --check`. Repository-layout tests check live relative links, filename
conventions and preserved report data. Independently copied skills must run with
`python -I -B` without other skill folders. These checks establish packaging and
helper behavior, not native host discovery or model adherence.

See the [path migration map](path-migrations.json), [skill catalog](../../skills/README.md)
and [testing index](../testing/README.md).
