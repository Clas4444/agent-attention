# Scoped-product delivery — unreleased source changes

Delivery authorization covers commit/push, not a new release/tag/version. Repository
version remains0.2.6; profile semantics0.1.1 and all25 directives remain unchanged.
The new compact API/format, scoped state and lazy skill entry are additive behavior
changes, not merely reports. No local rule requires a version bump for this source
delivery. A future release should choose its own scope from these unreleased notes.

See [product evidence](../testing/reports/2026-11-03/function-03/README.md),
[coordination evidence](../testing/reports/2026-11-03/coord-02/README.md) and
[delivery checkpoint](../../task/FUNCTION-03-RESULTS.json). Local gates run against
the final diff; remote CI/CodeQL must be checked on its exact pushed SHA. Original
measured source archives and source receipts remain distinct from delivery source.

# Release 0.2.6 — 2026-11-03

## Scope

Add a maintainable paired pilot runner and offline integrity audit/reproduction
scripts. Behavior changes are limited to experiment control, baseline exposure,
source pinning and stop/resume semantics; patch release is appropriate. Skills,
profile schema and semantics 0.1.1 are unchanged. No global payload was modified.

The pilot stops on first quota/rate/capacity/auth, unreliable usage or discovery,
checks a shared marker before each invocation, and reserves append-only attempt
IDs. Interrupted reservations remain unknown; they do not become NOT_RUN or an
automatic retry. Baseline carries no candidate file or prompt cue. A startup
relative-path error was repaired after its sole blocked invocation and covered
by a fake-CLI integration regression. No shared marker was cleared.

## Evidence and verification

The [integrity report](../testing/reports/2026-11-03/copilot-integrity.md) ships
364 normalized historical records, the frozen 24-call protocol, one blocked new
CLI attempt and 23 NOT_RUN, per-record hashes and five SVG/PNG figures. Published
scripts reproduce metrics and chart primitives from public files only. Original
historical statuses and frozen pre-fix pilot pins remain separate from publication
source hashes. The corrected harness has no new model-session evidence.

The same-version presentation revision adds the all-66-pair token/time lines,
profile mapping, labeled scatter and complete marginal coverage. A new authorized
campaign passes absolute-path preflight then stops on missing authentication;
it has no completed model sessions. The old marker and records are retained.

Full suite target for this snapshot is 119 tests with three platform symlink
skips; actual gate results are recorded in the task status after execution.
Run python -m unittest discover -s tests -v, python scripts/attention_assets.py,
the historical artifact audit (changed source receipts are STALE),
and git diff --check. Do not infer CI from historical runs; inspect exact SHA.

## Rollback

Restore revision 46971104b7a80723c43d35d5969de2182797424e or the selected source
payload. No profile/checkpoint state migration is required. Keep local experiment
records and the shared stop marker; rollback is not authorization to resume calls.

## Previous release 0.2.5 — 2026-10-31

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
