# Testing and evidence index

Start with current checks; historical reports retain their original versions and
limits. PASS of deterministic plumbing is not PASS of real-model behavior.

| Need | Source |
|---|---|
| Current measurements and evidence limits | [RESULTS.md](RESULTS.md) |
| Current harder-case campaign and false-PASS repairs | [CODEX-HARDER-2026-10-30.md](CODEX-HARDER-2026-10-30.md) |
| Harder cases and model-call planning | [Benchmark guide](../../benchmarks/README.md) |
| Profile comparison, host skill exclusions and missing usage | [AXIS-CAMPAIGNS.md](AXIS-CAMPAIGNS.md) |
| Twelve-attempt 0.2.2 composite study | [CODEX-COMPOSITE-2026-10-30.md](CODEX-COMPOSITE-2026-10-30.md) |
| Independent attention setup | [SETUP-SEPARATION.md](SETUP-SEPARATION.md) |
| Historical evaluator repairs | [EVALUATOR-RELIABILITY.md](EVALUATOR-RELIABILITY.md) |
| Historical experiment reconciliation | [ARCHIVE-RECONCILIATION.md](ARCHIVE-RECONCILIATION.md) |

Use `python -m unittest discover -s tests -v` for deterministic checks and
`python scripts/attention_assets.py` for bundled-resource consistency.
`--plan` on either evaluation entry point never calls a model. Keep raw traces,
prompt inventories, private paths and authentication data out of publication.
Publish sanitized outcomes with denominators and the exact source/case hashes.

Do not move or rename old evidence simply to make it look current. New protocols
and acceptance oracles require a separately named report; old failures remain
available in their original records.
