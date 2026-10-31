# Testing and evidence

Use current commands for verification and dated reports for historical results.
Deterministic PASS does not establish native discovery or model adherence.

| Need | Read |
|---|---|
| Current verification and latest model evidence | [Results](results.md) |
| Profile comparison design and host exclusions | [Campaign protocol](campaigns.md) |
| Cases, checker controls and bounded execution | [Benchmark guide](../../benchmarks/README.md) |
| Layout, ownership and naming rules | [Repository layout](../development/repository-layout.md) |

## Reports by date

- [2026-10-31](reports/2026-10-31/): [attention map repair and behavior](reports/2026-10-31/attention-map.md), and sanitized JSON.
- [2026-10-30](reports/2026-10-30/): [harder cases](reports/2026-10-30/codex-harder.md),
  [composite profiles](reports/2026-10-30/codex-composite.md), and paired JSON.
- [2026-10-29](reports/2026-10-29/): [independent setup separation](reports/2026-10-29/setup-separation.md),
  [graph integration](reports/2026-10-29/workflow-integration.md),
  [expectation audit](reports/2026-10-29/expectation-audit.md),
  [publication checks](reports/2026-10-29/publication-checks.md),
  [archive reconciliation](reports/2026-10-29/archive-reconciliation.md), and captures.
- [2026-10-28](reports/2026-10-28/): [initial capture](reports/2026-10-28/initial-validation.json),
  [Codex validation](reports/2026-10-28/codex-validation.md),
  [behavior repair](reports/2026-10-28/behavior-repair.md),
  [effort direction](reports/2026-10-28/effort-direction.md),
  [evaluator reliability](reports/2026-10-28/evaluator-reliability.md), and
  [Windows checkpoint repair](reports/2026-10-28/windows-checkpoint-repair.md).

Reports retain their original versions, language, denominators and uncertainty.
Historical JSON is unchanged. Recorded source paths/hashes refer to the measured
snapshot; relative links now point to the reorganized files. See the
[migration map](../development/path-migrations.json) for old/new locations and
preservation hashes. Old commit permalinks retain the original layout.

Run `python -m unittest discover -s tests -v`,
`python scripts/attention_assets.py`, and `git diff --check`. Plans on evaluation
entry points make no model calls. Keep raw traces, private maps and authentication
data out of publication; never discard failed attempts or treat missing usage as zero.
