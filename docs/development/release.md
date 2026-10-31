# Release 0.2.5 — 2026-10-31

## Scope

Fix exported Attention Setup maps that referred to selected guidance without
including or locating it. Embed fully resolved base/context guidance for all
five axes, invariants, warnings and semantics version. Update canonical helper
and generator sources, regenerate both skill payloads, and document snapshot
refresh and explicit map activation. No global installation is modified.

Schema 1 and profile semantics 0.1.1 remain unchanged. Existing plans still work;
old exported maps retain old contents. Export a NEW map to obtain embedded
instructions; existing destinations are deliberately not overwritten.

## Verification

Full suite: 106 tests, 103 PASS and three symlink skips. All 3,125 base profiles
pass conflicting-context selection and restoration (9,375 selections). Every
map level 1..5 includes its defined guidance. The map regression failed before
repair and passed after it. Generated-resource checks and git diff checks PASS.

[Model evaluation](../testing/reports/2026-10-31/attention-map.md) and its capture
retain nine completed sessions and six blocked startup launches. Eight repairs
pass the frozen independent oracle; one missing-fact session correctly stops
without edits. A literal-word behavior scorer falsely failed that stop: its
original result and manual adjudication are both retained. It is not a validated
general semantic grader. Conditional high-risk work adds an independent check
in one observed session, while fixed-level trials show no reliable quality or
cost ordering. These results are separate from previous averages.

Tests needed a temporary directory inside the parent workspace and outside this
repository. Initial sandbox temp/hardlink restrictions and a wrong-working-dir
launch were corrected and rerun; they are not counted as product regressions.
CLI model sessions needed ordinary app-server access outside the sandbox. Full
home/host isolation, native picker discovery, real-model restoration sequences
and model trials at levels 2/4 remain unverified or NOT_RUN as described in the
report. No new generic PyYAML-dependent validation is claimed.

## Rollback

Restore revision fc53f89a949142ce82577ad859abb856c2246e6c or its chosen skill
payload. Keep local maps, custom plans and unrelated skills. No state migration
is needed. Previous packaging and historical report snapshots remain in Git.
