# Agent Attention maintenance

This repository is an independent instruction layer, not a Loop distribution.
Read docs/GUIDE.md. Core semantics live in scripts/attention.py. Generated helper,
reference, HTML and SVG come from scripts/attention_assets.py; edit sources first.
The single distributable skill is skills/agent-attention. Do not patch downstream
skills, grant permissions, change model settings or claim measured token savings.

Run `python -m unittest discover -s tests -v`,
`python scripts/attention_assets.py`, and `git diff --check`.
Keep raw/private logs under ignored .loop. Historical prototype results do not
certify this standalone repository. Record new source hashes and actual checks.
