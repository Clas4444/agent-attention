# Results and verification scope

## Current repository: 0.2.5

This release makes exported Attention Setup maps self-contained and preserves
profile semantics 0.1.1. The [map evaluation](reports/2026-10-31/attention-map.md)
records nine completed model sessions: six fixed-profile repairs, two known-fact
repairs and one intentional stop on missing facts. Six earlier startup launches
were BLOCKED. Missing-fact stopping and high-context independent checks were
observed; general savings and reliable effort separation remain unverified.
The [release verification](../development/release.md) records current tests,
resource checks, independently copied skill execution and remaining gaps.
The [layout tests](../../tests/test_repository_layout.py) check live links,
filenames and historical report preservation.

## Earlier model evidence: 0.2.3

[Harder cases and acceptance repair](reports/2026-10-30/codex-harder.md) records
sixteen of eighteen planned attempts: fifteen completed sessions, one capacity
failure after work and two NOT_RUN trials. Both harder tasks complete six
attempts each. The data separates per-task means, missing usage and original
failures. This is a small same-home fixture comparison; full runtime isolation,
general savings and independent per-axis effects remain unverified.

The earlier [composite comparison](reports/2026-10-30/codex-composite.md) remains a
separate campaign. It is not pooled with the repaired acceptance oracle. Older
[Codex validation](reports/2026-10-28/codex-validation.md),
[behavior repair](reports/2026-10-28/behavior-repair.md) and
[effort-direction measurements](reports/2026-10-28/effort-direction.md) keep their
original pins and scope. Their old PASS counts are not fresh tests of this release.

## What current checks establish

Profile parsing/inheritance, independent setup selection/restoration, generated
resources, isolated helper packaging, benchmark acceptance controls and repository
navigation can be checked deterministically. A copied skill and a valid metadata
file do not prove native picker discovery, model adherence, cross-conversation
memory or token savings. Real-model execution is opt-in and never runs in CI.

The [testing index](README.md) lists all dated evidence. Move reports using the
[migration map](../development/path-migrations.json), preserve recorded numbers
and hashes, and keep archived JSON immutable rather than rewriting it as current data.
