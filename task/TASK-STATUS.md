# Task status — 2026-11-03, presentation/recovery revision

- State: OFFLINE_COMPLETE_AUTH_BLOCKED.
- Historical audit unchanged: 364 package records / 409 experimental CLI;
  original statuses preserved. Fresh frozen cents acceptance remains 20/20
  standalone, 30/30 combined and 132/132 completed grid. Revision semantics
  remain HISTORICAL_NOT_REVALIDATED.
- Historical grid: planned972, original132 PASS +152 BLOCKED, absent688;
  66 complete cents pairs, all successful attention focus=1. No old-grid resume.
- Original pilot preserved: one startup-blocked CLI, zero model sessions,
  23 NOT_RUN. Diagnosis HARNESS_RELATIVE_CWD, fixed in 0.2.6.
- New recovery authorized by user: new campaign/marker, old marker retained;
  shared RECOVERY decision published locally for peer coordination.
- New preflight: two non-model CLI checks (--version/--help), absolute cwd/-C,
  both exit0. Model/effort settings unchanged; credentials not copied.
- New recovery pilot: 1 of24 experimental CLI invoked; 0 model sessions,
  0 tool starts; 23 NOT_RUN. Original stop MALFORMED_USAGE retained; stderr
  independently diagnoses AUTH_FAILURE (no authentication in isolated home).
  New shared marker retained; no call after auth/accounting failure.
- Pilot experimental CLI total across both campaigns: 2. Preflight checks are
  separately reported; no missing usage is counted as zero tokens.
- New per-axis effects/quality/behavior: NOT_RUN, no complete matched pair.
- Figures revised: white plot areas, light grids, legends, numeric ticks/units,
  all66-pair token/time lines, scatter y=x, full planned/completed/blocked/notrun
  coverage by case/axis/level. Primary skill illustrations unchanged.
- Source tables: all66 index-to-five-level rows in CSV+Markdown; 30 full coverage
  rows in CSV. Recorded index is not time or a one-axis sweep.
- Publication bundle: 48 SHA-256 entries for inputs, outputs, scripts, tests and
  public task/docs; old pilot/protocol and normalized historical records retained.
- Final local verification: 119 tests, 116 PASS and three platform symlink skips;
  assets, links, diff and 48 publication hashes PASS. Exact-SHA CI is checked
  during delivery. Earlier ad66dec had all
  four OS/Python jobs and both CodeQL analyses PASS; not reused for this update.
- Release remains 0.2.6: presentation/evidence only, no skill behavior change,
  global skill update, peer repository or parent map edit.
- Next prerequisite: authentication compatible with isolated campaign plus a
  reviewed new stop-state decision. No contaminated-home fallback or auto retry.

[Revised figures and recovery report](../docs/testing/reports/2026-11-03/recovery-and-figures.md)
includes actual counts, failures, limitations and links to all public datasets.
