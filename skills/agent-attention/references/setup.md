# Optional workflow setup

Use only for an explicit setup/design request. Existing direct workflows remain
available without a graph. Use the bundled workflow_setup.py; it is self-contained
under isolated Python and never executes skills, tasks, shell expressions or models.

## Interview, then design

Ask two or three related questions at a time, reusing known answers. Start with
outcome/completion criteria and desired steps. Then ask about exact source pointers,
PASS/FAIL/BLOCKED/NOT_RUN routes, conditional skill/profile choices, fact provenance,
cycle end, limits, project root and output location. `questions --layer skills`
or `questions --layer attention` prints the checklist. Do not manufacture answers.

Show the ordered graph and branch priorities in the conversation. Clarify missing
conditions before dependent work; use existing authorization instead of asking for
permission again. Default remains no execution: setting up a loop does not start it.
If the user also requests execution, proceed only within that authorized scope.

## Shared graph contract v1

`template --layer skills|attention|both` prints an editable two-step example.
Replace its sample goal, criteria, sources, facts and bindings with the user's
answers; the scaffold itself is not a completed interview.

- schema_version=1, id, goal, entry, limits.max_cycles and limits.max_steps.
- fact_keys declares the allowed condition names. Conditions are exact typed
  JSON equality maps, never expressions. Missing relevant facts stop selection;
  they are not false. Earlier known-false conditions do not block later routes.
  Optional fact_sources records their provenance; boundaries records constraints.
- Each step has id/title, 0–5 exact project-relative sources and acceptance criteria.
- bindings are chosen BEFORE work using ordered `when` conditions. The final
  binding has when={} as fallback. A binding can name several skills as a toolkit
  and a partial attention profile. Read only instructions needed for that step.
- transitions are chosen AFTER an evidenced status. Every status needs a final
  unconditional route. Targets are another step, DONE or STOP. Mark cycle_end
  explicitly on the closing step and give it a return route to entry.
- Optional task-level attention is inherited; binding attention lasts one step.
  Omitted axes are balanced. The next selection recomputes from task levels.
- skill_root defaults to .agents/skills; choose the actual project layout.

First-match order is deliberate and must be explained to the user. BLOCKED and
NOT_RUN should normally pause via STOP. Never interpret an absent check as PASS.
Always allow completion and stop conditions; budgets are maxima, not quotas.
Missing-fact routing prints status=BLOCKED and exits 2 without changing state.
Invalid configuration exits 1. Exit 0 means the helper operation succeeded;
it does not turn a routed STOP or an unexecuted task into PASS.

## Check and export a local map

`check --file draft.json` validates graph structure. Repo 1 should also supply
`--catalog <skill-dir>/assets/catalog.json` to check canonical registered skills.
This does not establish that instructions are installed or native picker discovery.
Inspect selected instruction paths before execution; missing ones are BLOCKED.

`export --file draft.json --project <authorized-project>` creates a NEW directory
at .loop/workflows/<id> with workflow.json, AGENT-MAP.md, diagram.mmd and a local
.gitignore ignoring all its contents. It never edits project-wide ignore settings
or overwrites an existing design. Source pointers are relative to the project,
not to the map. The map lists per-step sources and candidate instruction paths;
read only the current step and selected binding, not the whole repository.

Explicit --output accepts a normalized relative directory inside that project.
Internal output aliases/reparse points are rejected. Export validates before
creating files; an I/O failure may leave a partial new directory, so inspect it
before retrying. Ignore rules do not prevent deliberate force-add or manual sharing.

## Select and advance; no hidden scheduler

`start --file workflow.json --facts <JSON>` prints the initial cursor.
Use --facts-file facts.json for a UTF-8 JSON object without shell quoting.
Save it in existing task context or an explicitly selected local cursor file.
`select --file workflow.json --state cursor.json` prints the exact selected skills,
instruction paths, effective attention, source pointers and criteria.

After doing and checking the authorized step, use
`advance --file workflow.json --state cursor.json --status PASS --evidence <observed-result> --facts <JSON>`.
Retain the returned cursor before the next selection. FAIL/BLOCKED/NOT_RUN are
also valid observations. This command records supplied evidence; it does not
independently verify task success or write the cursor file. Keep raw evidence
separately when needed. A manually edited cursor is not an authenticated log.

Returning from cycle_end to entry increments the cycle count. Reaching limits
returns STOP. DONE ends immediately; never run extra rounds to fill a budget.
Changed graph hashes invalidate old cursors; review the revision and start a new
cursor rather than resetting counters secretly. Also stop on user request,
deadline, safety boundary or repeated non-progress; these host-level facts are
not autonomously observed by this read-only routing helper.

## Attach attention to an existing skills graph

Repo 2 can reuse Repo 1's graph. Use `attach --file workflow.json --patch modes.json`.
A patch contains optional task attention and steps keyed by step ID, for example:

```json
{"attention":{"sync":4},"steps":{"verify":[{"binding":0,"attention":{"verify":5}}]}}
```

Binding indexes are zero-based in the displayed ordered list. The helper outputs
a new document, preserving skills, conditions, transitions and the original input.
Unknown steps/indexes or route-editing fields are rejected. Validate and export
to a new local directory. For new branch conditions, use the interview to revise
the graph explicitly; attachment does not invent extra branches or permissions.
