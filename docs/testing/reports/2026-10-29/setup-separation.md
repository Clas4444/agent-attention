# Setup separation — 2026-10-29

This correction supersedes the combined setup presentation in the preceding
1.11.0 / 0.2.0 release. Historical capture JSON and model measurements keep
their original source hashes and must not certify changed instructions.

| Product | Default setup | Local artifact | Companion required? |
|---|---|---|---|
| agent-workflows | Work steps, conditional skills, result routes, bounded cycles | workflow.json and AGENT-MAP.md | No |
| agent-attention | Task scope, five-axis base, conditional contexts, tradeoffs, restoration | attention.json and ATTENTION-MAP.md | No |

The existing graph-v1 bridge remains available only for explicit integration.
Independent attention setup never calls it. An installed-skill regression removes
the workflow helper and graph example before checking questions, template,
validation, selection and export under isolated Python. A base-only plan needs
no rules or facts. Conditional tests check inheritance/restoration, first-match
priority, missing facts and invalid levels/fields; private exports have no graph
or cursor. Helpers never execute the task or configure native thinking.

The new attention illustration and the revised skill-specific workflow figure
use the established light background, white cards, green routes and pale stop
band. Public prose uses product names instead of conversational repository numbers.
Raw/private maps remain ignored. Deterministic and real-model results are separate;
new real-model setup interviews, adherence and token comparisons are NOT_RUN.

## Final local verification

- agent-workflows 1.11.1: 14/14 fixed gates PASS; 372 tests discovered,
  370 pass and two Windows symlink skips. Session separated-1111-final-20261029,
  input fingerprint `667002a48dcacd6bf7149876279503627216a8eb3d3d1059e368f6164d03812a`.
- agent-attention 0.2.1: 84 tests discovered, 82 pass and two directory-symlink
  skips under each available Python 3.14 and 3.12 runtime. The installed-skill
  regression runs without the optional graph helper/example present.
- Generated resources, local links, compilation and whitespace checks pass.
  Both setup figures were rendered and visually inspected; style is preserved.

[Product-specific capture and hashes](setup-separation.json) records exact local
checks. Skips do not certify unavailable symlink paths. No new model calls or
native-picker trials were performed. Prior CI was green for 1.11.0/0.2.0; it is
not evidence for these changed sources. Remote CI must use the new commit IDs.
