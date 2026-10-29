# Attention setup

Design base levels, conditional contexts, tradeoffs and restoration for an
existing task. This configures attention; it does not create work steps or routes.

## Choose an entry point

Install the entire `skills/attention-setup` folder and invoke **`$attention-setup`**.
It has its own SKILL.md, UI metadata, reference, example and bundled helpers. It
runs independently of the profile skill, Agent Workflows and any workflow graph.

If `skills/agent-attention` is already installed, the older **`$agent-attention setup`**
request remains supported using the same helper/schema. That two-word request is
not a separately registered picker entry. Natural-language attention setup is
also supported; native picker discovery and syntax depend on the host.

Both paths reuse known task facts. Copying a folder does not prove host discovery;
see the [skill catalog](../../skills/README.md) for installation choices.

![Set a base, choose context overrides and restore it](../assets/attention-setup.svg)

## What this setup designs

| Attention setup in agent-attention | Workflow setup in agent-workflows |
|---|---|
| Base levels for five attention axes | Work steps and skill choices |
| Conditional temporary levels for existing contexts | Conditional task routes after observed results |
| Tradeoffs, fact provenance and restoration scope | Completion, cycle return and bounded retries |
| Optional attention.json and ATTENTION-MAP.md | Optional workflow.json, AGENT-MAP.md and diagram |

Both work independently. A context can be an existing phase such as editing or
reviewing, a known risk, or another user-defined fact. It does not create that
phase, run a skill or choose the next work step. A simple task-wide plan has no
conditional rules at all.

## Interview

The agent reuses supplied information and asks two or three related questions at
a time. Establish the task scope, desired effort/coverage tradeoff and base
levels for focus, sync, batch, explore and verify. All unspecified axes stay 3.
Then ask whether observed conditions need temporary overrides, why each helps,
its drawback, where facts come from, and when the base must be restored. Gather
0–5 exact source pointers when useful. Do not require task step order, skills,
status routes, cycle counts or another repository.

Example: base focus=2, all other axes=3. For risk=high, temporarily use verify=5
and sync=4, retaining focus=2. This adds independent checking and reconciliation
at extra effort. Narrow focus can miss interactions; preserve dependency pointers
and all required checks. When risk is no longer high, restore the base. An unknown
risk is clarified rather than silently treated as ordinary risk.

Levels 1–2 reduce discretionary effort, 3 is balanced, 4–5 increase it. Required
checks, permission boundaries and shared-contract reconciliation remain. These
are behavioral instructions; selecting a level does not prove adherence, set
native model thinking or guarantee token ordering/savings.

## Optional helper and local map

Apply clear agreed settings directly in context. Files and helper calls are
optional. From this repository:

```text
python scripts/attention_setup.py questions
python scripts/attention_setup.py template
python scripts/attention_setup.py check --file attention.json
python scripts/attention_setup.py select --file attention.json --facts-file facts.json
python scripts/attention_setup.py export --file attention.json --project C:/MyProject
```

For an installed skill, substitute its `scripts/attention_setup.py` path. The
whole skill folder includes this helper and attention.py for isolated Python use.
The template is a scaffold; replace it with the actual interview answers.

The attention_schema=1 plan stores scope, base, ordered rules, fact_sources,
sources and restore=base-after-context. Rules contain id, when, levels and reason.
Conditions are exact typed equality comparisons, not code. First matching rule
wins; unspecified axes inherit base. Every selection starts from base, so previous
overrides cannot leak. Base is the fallback only when earlier conditions are
known not to match. Missing relevant facts return BLOCKED, exit 2. Invalid input
exits 1; exit 0 means the helper succeeded, not that the task passed.

Only an explicit saving request calls for export. It creates a NEW local
`.attention/plans/<id>/` with attention.json, ATTENTION-MAP.md and an ignore file.
No workflow.json, steps, transitions, cycles, cursor or diagram is required.
The map covers scope, exact sources, condition provenance and attention choices.
Existing output is never overwritten. Path escapes, repository metadata and
output aliases are rejected; I/O errors may leave a partial new directory.
Force-add or manual sharing can publish ignored data: keep machine maps private.

## Optional integration

If you already have a compatible graph and explicitly want per-binding attention,
see [workflow integration](workflow-integration.md). That bridge preserves the existing
skills and task routes. You do not need it for attention setup or normal profiles.

## Evidence

The standalone tests verify levels, conditional choice, missing facts, restoration,
private export and each installed skill in a directory without Agent Workflows
or the other skill folder.
They are deterministic plumbing checks, not model-behavior or token benchmarks.
Earlier shared-graph measurements retain their original scope. See the
[original setup separation capture](../testing/reports/2026-10-29/setup-separation.md).
Current packaging checks are recorded in the [release verification](../development/release.md).
