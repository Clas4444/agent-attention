# Archive reconciliation — 2026-10-29

Version remains **0.2.1**. The private archive was checked against its manifests:
**3,321 retained files in 77 logical groups** across the two projects and their
old demo folders. This audit makes no new model calls. It does not republish raw
prompts, commands, private machine paths, fixture Git metadata or backups.

## Reconciliation of model evidence

The initial [Codex campaign](../2026-10-28/codex-validation.md) already reports
**12 attempts: 8 PASS, 1 FAIL and 3 environment blocks**. All 12 original result
statuses match the published records; those observations are not rerun here.

Four [behavior-repair traces](../2026-10-28/behavior-repair.md) and eight
[effort-direction traces](../2026-10-28/effort-direction.md) also already appear in
published reports. Their **12 unique trace hashes match** the original archived
bytes. Duplicate result/array representations were collapsed, not counted twice.
The four behavior cases passed; the effort campaign had seven acceptance successes
and one pre-action environment block. The blocked regression keeps raw status
FAIL alongside its published BLOCKED_ENVIRONMENT classification. Three nonzero
tool commands in the original six trials remain documented. Composite effort
ordering does not establish per-axis effects or monetary savings; cache behavior
and the small fixture limit the result. These historical datasets are separate;
do not sum them as a product-wide success rate.

## Deterministic setup evidence

Three local candidate captures are now indexed together, including the earlier
intermediate snapshot and final LF-normalized capture. The final independent
attention setup suite has 84 tests: 82 pass, two Windows directory-symlink skips
on each recorded Python runtime. The installed-skill test omits the optional
workflow bridge. These checks validate configuration plumbing, not real-model
interview quality, native discovery or per-context attention behavior.

See [independent setup checks](setup-separation.md),
[earlier graph setup evidence](workflow-integration.md),
[evaluator reliability](../2026-10-28/evaluator-reliability.md) and
[axis campaign protocol](../../campaigns.md). Six injected grader controls are
negative/positive deterministic checks; they are not additional model trials.

## Retention and reproducibility limits

[Machine-readable reconciliation](archive-reconciliation.json) retains the archive
SHA-256, group inventory digests, relevant record/trace hashes and original
observations. Hashes identify data; they do not reconstruct it or independently
attest model execution. At the user's request, the local raw archive is to be
deleted after this report is pushed and the remote bytes are verified. It is not
uploaded to GitHub. Thereafter, only the already-published sanitized evidence and
this reconciliation remain; full raw-trace replay is no longer possible.
No new model effectiveness, token-saving or archive reproducibility claim is made.
