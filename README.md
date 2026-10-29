# Agent Attention

Five attention axes, five levels each, balanced by default. Apply a profile to an
existing task, or design a reusable attention plan with the independent setup skill.

Version: **0.2.4**. Profiles are behavioral guidance, not native model reasoning
settings or a scheduler. General token savings remain unproven.

![Five attention axes](docs/assets/attention-controls.svg)

## Choose a skill

| Need | Install the whole folder | Invoke |
|---|---|---|
| Apply task-wide levels and temporary overrides | `skills/agent-attention` | `$agent-attention` |
| Design base levels, conditional contexts and restoration | `skills/attention-setup` | `$attention-setup` |

Either skill works independently. Install one or both in your host's skill root;
for a Codex project, use `.agents/skills/<skill-name>`. Preserve local customization,
open a fresh session and verify host discovery. Copying a folder does not prove
native picker activation. See the [skill catalog](skills/README.md).

```text
Use $agent-attention with focus=2,sync=4 for this task.
Keep the profile across implementation, review and testing.
```

```text
Use $attention-setup to design attention settings for my task.
Keep the plan in context; save a private local map only if I ask.
```

The earlier `$agent-attention setup` request remains supported by the profile
skill. It is not a separately registered picker alias. The independent setup skill
has its own SKILL.md, UI metadata, reference, example and isolated Python helpers.
It needs no workflow graph, routing cursor, Loop skill or other repository.

## Attention levels

| Axis | Controls |
|---|---|
| `focus` | Width of the relevant context kept active |
| `sync` | Reconciliation of dependent work and assumptions |
| `batch` | Decomposition and intermediate inspection depth |
| `explore` | Breadth of relevant discovery |
| `verify` | Additional verification depth |

Levels 1–2 reduce discretionary work, 3 keeps ordinary behavior and 4–5 increase
attention work. Unspecified axes stay 3. Permissions, mandatory checks and
shared-contract reconciliation remain at every level. Total tokens need not be
monotonic because of required work, retries and caching.

Read the [profile guide](docs/guides/attention-profiles.md),
[setup guide](docs/guides/attention-setup.md) or
[offline playground](docs/playground/index.html). Graph integration is
[optional and separate](docs/guides/workflow-integration.md).

## Repository layout

| Location | Contents |
|---|---|
| `skills/` | Self-contained installable skills; bundled helpers are generated copies |
| `scripts/` | Canonical helpers and stable CLI entry points |
| `scripts/generators/` | Resource, reference and illustration generators |
| `scripts/evaluation/` | Opt-in benchmark execution and acceptance checks |
| `benchmarks/cases/` | Versioned repair tasks and checker controls |
| `tests/` | Deterministic tests; no real model calls |
| `docs/guides/` | Current user guides |
| `docs/development/` | Layout rules, path migration and release maintenance |
| `docs/testing/reports/<date>/` | Historical reports and paired JSON captures |

See the [documentation index](docs/README.md) and
[layout/naming rules](docs/development/repository-layout.md).

## Develop and verify

Python 3.11+, standard library only:

```text
python -m unittest discover -s tests -v
python scripts/attention_assets.py
```

Edit generator sources before generated resources, then run
`python scripts/attention_assets.py --write`. Keep raw traces and machine-local
maps private. The [benchmark guide](benchmarks/README.md) explains opt-in model
calls; [results](docs/testing/results.md) separate executed checks from limitations.
This organization/packaging release adds no new model measurements.

Profile semantics remain 0.1.1. For migration from 0.1.0, reselect `batch`: it now
means decomposition depth rather than batch size. See the profile guide and
[release notes](docs/development/release.md).

## Origin and license

Extracted from the [Agent Workflows](https://github.com/Clas4444/agent-workflows)
attention prototype, based on commit `e2b1b717b1e751a9218fa6ad22381c6fd7f55cbb`.
This repository has independent history and checks; it does not include the 53
Loop skills or inherit their historical runtime results. MIT license; original
copyright retained. See [CHANGELOG.md](CHANGELOG.md).
