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

Optional graph setup uses scripts/workflow_setup.py and scripts/workflow_assets.py.
Graph contract v1 is vendored identically in agent-workflows; neither repo imports
the other at runtime. Edit core sources, regenerate bundled resources, and keep
the shared contract tests aligned. Profile semantics remain 0.1.1; release 0.2.0
does not silently migrate profile state. New map exports must remain local by default.

Attention setup is independent: scripts/attention_setup.py designs base levels,
conditional context overrides and restoration; scripts/attention_setup_assets.py
packages its helper/reference/example and attention-setup.svg. It never requires
a graph or imports agent-workflows. workflow_setup.py remains an optional legacy
graph integration bridge; do not route ordinary attention setup through it.
