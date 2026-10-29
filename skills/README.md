# Skill catalog

| Skill | Purpose | Entry point | Required companion |
|---|---|---|---|
| Agent Attention | Apply a five-axis task profile and scoped overrides | [agent-attention/SKILL.md](agent-attention/SKILL.md), `$agent-attention` | None |
| Attention Setup | Design base levels, conditional contexts, tradeoffs and restoration | [attention-setup/SKILL.md](attention-setup/SKILL.md), `$attention-setup` | None |

Install the entire selected folder in the host's supported skill directory. Both
folders contain the helpers/resources they need and run independently under
isolated Python. Do not install this catalog or the whole repository as a skill.

SKILL.md is maintained in each skill folder. Supporting Python, references and
examples are generated from canonical sources in `scripts/` and
`scripts/generators/`; edit those sources and regenerate rather than patching copies.
Duplicated helper files are intentional so either skill can be installed alone.
The standalone setup skill has explicit-invocation UI metadata matching its local
entry point. Native picker discovery still requires a host check.

The profile skill also retains the older two-word setup request and the optional
graph bridge. The standalone setup skill does not bundle that bridge or require
Agent Workflows. See the [setup guide](../docs/guides/attention-setup.md) and
[repository layout](../docs/development/repository-layout.md).
