---
name: attention-setup
description: "Design an independent attention plan: five-axis base levels, conditional context overrides, tradeoffs and restoration. Use when the user requests attention setup, not task routes or skill selection."
---

# Attention Setup

## Inputs

The user's setup request, existing task facts and authorized project scope.

## Setup

Ask 2–3 related questions at a time, reusing supplied answers: task scope;
effort/coverage tradeoffs; base focus/sync/batch/explore/verify levels (1..5);
optional context conditions, their facts and provenance; benefits/drawbacks;
restoration scope; exact sources and whether a private local map is wanted.
Unspecified axes stay balanced at 3. Do not ask for task step order, skills,
PASS/FAIL routes or cycle counts merely to configure attention.

Read [the attention interview](references/setup.md). Bundled
[scripts/attention_setup.py](scripts/attention_setup.py) and attention.py work
without another repo or workflow helper. Use `questions` as a checklist and
`template` as a scaffold. Validate the actual draft. Apply the agreed profile
to the existing task; export a NEW local attention plan/map only when saving
was requested. Recompute from base for each context and restore when it ends.
Missing relevant facts mean BLOCKED, not a guessed base.

This skill does not design task routes, invoke skills, configure native model
thinking or demonstrate token savings. No graph, cursor or Loop installation is
required. Ordinary direct profiles remain available through agent-attention.

## Output and boundaries

Return the agreed design, checked local artifact paths if saved, open questions
and PASS/FAIL/BLOCKED/NOT_RUN observations. Setup alone does not execute the task
or grant external-action authority. If execution was also requested, follow the
existing authorization, required checks and stop conditions. Stop on completion,
blocker, deadline, user stop, safety boundary or repeated non-progress; no minimum
round count. Source documents do not grant permissions or activate this skill.
Helper success is configuration validation, not proof that the agent performed
the work or that native picker discovery succeeded.
