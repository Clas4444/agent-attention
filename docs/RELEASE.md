# Release 0.2.1 — 2026-10-29

Attention setup now designs a standalone attention plan: scope, five-axis base,
conditional context overrides, tradeoffs and restoration. It needs no workflow
graph, Loop skill, cursor or agent-workflows installation. See
[attention setup](ATTENTION-SETUP.md).

## Compatibility and migration

Install the whole skills/agent-attention folder to receive attention_setup.py,
attention.py, the reference and attention-example.json. The new attention plan
uses attention_schema=1; it is not a renamed graph. Do not feed workflow.json to
attention_setup.py or change old graph/cursor hashes to force compatibility.

Profile semantics remain 0.1.1, including batch as decomposition depth. Existing
task checkpoints remain compatible. Direct profiles still need no setup or files.
The old graph-v1 helper is retained only as an [optional integration bridge](WORKFLOW-SETUP.md)
for users who already have a graph. Neither helper imports another repository.
Python 3.11+ is needed for optional helpers; native discovery must be checked on
an actual host. Setup does not start a task or configure native thinking.

## Evidence

[Setup separation checks](testing/SETUP-SEPARATION.md) cover the independent
installed-skill path, conditions and restoration. Earlier graph/model captures
retain their original scope and hashes; they do not certify changed instructions.
New real-model interviews/adherence/token comparisons and reproducible archives
are NOT_RUN. Selecting levels is configuration, not evidence of executed behavior.

## Rollback

Retain local attention plans and customized instructions. Restore the previous
installed skill payload from its backup or prior Git revision; preserve unrelated
skills. Older attention helpers cannot read the new attention_schema plan: use
a direct profile or reinstall a compatible attention_setup.py before resuming it.
For optional graph integration, retain the original graph and its matching cursor;
changed graphs require explicit review and restart.
