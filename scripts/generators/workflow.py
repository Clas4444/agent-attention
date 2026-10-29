"""Generate/check standalone workflow setup resources and matching light illustration."""
import argparse
import json
from pathlib import Path

if __package__.startswith('scripts.'):
    from ..workflow_setup import template
else:
    from workflow_setup import template


REFERENCE = '''# Optional workflow integration bridge

Use only for an explicit integration request with a supplied graph. Ordinary
attention setup uses attention_setup.py and references/setup.md. Direct profiles remain
available without a graph. Use the bundled workflow_setup.py; it is self-contained
under isolated Python and never executes skills, tasks, shell expressions or models.

## Interview, then design

Confirm the supplied graph and preserve its work steps, skills, criteria and
status routes. Ask only for missing task/per-binding attention levels, their
conditions, tradeoffs and restoration. New graph conditions require a separately
reviewed graph revision; do not silently design a new workflow during attachment.

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

`check --file draft.json` validates graph structure. agent-workflows should also supply
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

agent-attention can reuse a graph from agent-workflows. Use `attach --file workflow.json --patch modes.json`.
A patch contains optional task attention and steps keyed by step ID, for example:

```json
{"attention":{"sync":4},"steps":{"verify":[{"binding":0,"attention":{"verify":5}}]}}
```

Binding indexes are zero-based in the displayed ordered list. The helper outputs
a new document, preserving skills, conditions, transitions and the original input.
Unknown steps/indexes or route-editing fields are rejected. Validate and export
to a new local directory. For new branch conditions, use the interview to revise
the graph explicitly; attachment does not invent extra branches or permissions.
'''


def picture():
    return '''<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="930" viewBox="0 0 1400 930" role="img" aria-labelledby="title desc">
<title id="title">Design a conditional workflow and a local agent map</title>
<desc id="desc">Interview, validate and export; choose skills or attention before each step, route after evidence, return for another bounded cycle or stop.</desc>
<defs><marker id="arrow" markerWidth="9" markerHeight="9" refX="7" refY="4" orient="auto"><path d="M0 0L8 4L0 8" fill="none" stroke="#126957" stroke-width="1.5"/></marker></defs>
<rect width="1400" height="930" rx="20" fill="#f2f6f4"/>
<g font-family="Arial, sans-serif" fill="#16313b">
<text x="40" y="40" font-size="15" fill="#126957" font-weight="700">OPTIONAL / WORKFLOW INTEGRATION</text>
<text x="40" y="87" font-size="35" font-weight="700">Attach attention to an existing graph</text>
<text x="40" y="122" font-size="19" fill="#415d67">Optional graph bridge only. For independent attention setup, use the attention setup guide.</text>
<g fill="white" stroke="#cddcda"><rect x="40" y="155" width="305" height="135" rx="12"/><rect x="378" y="155" width="305" height="135" rx="12"/><rect x="716" y="155" width="305" height="135" rx="12"/><rect x="1054" y="155" width="306" height="135" rx="12"/></g>
<g font-size="20" font-weight="700"><text x="60" y="190">1 / Ask and clarify</text><text x="398" y="190">2 / Design and check</text><text x="736" y="190">3 / Export local map</text><text x="1074" y="190">4 / Run when requested</text></g>
<g font-size="17" fill="#415d67"><text x="60" y="224">Outcome, steps, branches,</text><text x="60" y="251">source pointers and limits.</text><text x="398" y="224">Explicit fallback for each status.</text><text x="398" y="251">Clarify unknown condition facts.</text><text x="736" y="224">Exact files for each step.</text><text x="736" y="251">Keep the current route visible.</text><text x="1074" y="224">Setup alone does not execute.</text><text x="1074" y="251">Keep normal permissions.</text></g>
<g fill="none" stroke="#126957" stroke-width="2" marker-end="url(#arrow)"><path d="M347 224H373"/><path d="M685 224H711"/><path d="M1023 224H1049"/></g>
<text x="40" y="345" font-size="22" font-weight="700">Inside a cycle: choose before work, route after evidence</text>
<g fill="white" stroke="#cddcda"><rect x="85" y="380" width="380" height="170" rx="12"/><rect x="580" y="380" width="380" height="170" rx="12"/><rect x="1070" y="408" width="245" height="115" rx="12"/></g>
<g font-size="22" font-weight="700"><text x="107" y="417">WORK / conditional binding</text><text x="602" y="417">VERIFY / conditional binding</text><text x="1092" y="450">DONE</text></g>
<g font-size="18" fill="#415d67"><text x="107" y="452">If bug: debug skill + detailed steps.</text><text x="107" y="481">Otherwise: implementation skill.</text><text x="107" y="519">Read only this step's sources.</text><text x="602" y="452">If high risk: review + verify level 5.</text><text x="602" y="481">Otherwise: ordinary task checks.</text><text x="602" y="519">Record actual PASS / FAIL / gaps.</text><text x="1092" y="486">Criteria met: finish now.</text></g>
<g fill="none" stroke="#126957" stroke-width="2" marker-end="url(#arrow)"><path d="M465 466H574"/><path d="M960 466H1064"/><path d="M770 550V605H275V555"/><path d="M85 465H58V570H175V555"/></g>
<g font-size="16" fill="#126957"><text x="485" y="452">PASS</text><text x="975" y="449">PASS + done</text><text x="330" y="593">More work remains? Return to entry: one completed cycle.</text><text x="52" y="597">FAIL: revise</text></g>
<rect x="40" y="643" width="1320" height="65" rx="12" fill="#e0eee8"/>
<text x="60" y="669" font-size="19" font-weight="700">STOP / BLOCKED, NOT_RUN, budget, deadline, user stop or repeated non-progress.</text>
<text x="60" y="695" font-size="17">No minimum rounds. Missing facts are questions, not a guessed fallback. Routing never executes a task.</text>
<rect x="40" y="735" width="645" height="145" rx="12" fill="white" stroke="#cddcda"/><rect x="705" y="735" width="655" height="145" rx="12" fill="#fff8f5" stroke="#cddcda"/>
<text x="60" y="768" font-size="18" font-weight="700" fill="#126957">RECOMMENDED</text><text x="725" y="768" font-size="18" font-weight="700" fill="#9a4c32">AVOID</text>
<g font-size="18" fill="#415d67"><text x="60" y="802">Keep 0–5 exact source pointers per step; use the local map.</text><text x="60" y="835">Recompute attention at each step; retain honest evidence.</text><text x="725" y="802">Scan the whole repository or run every possible branch.</text><text x="725" y="835">Treat conditions as code, or setup as permission to publish.</text></g>
<text x="40" y="912" font-size="15" fill="#415d67">Graph validation and routing are deterministic checks. Native discovery and real-agent effectiveness require separate observation.</text>
</g></svg>'''


def check(repo, write=False):
    folder = repo/'.github/skills/loop'
    layer = 'skills'
    if not folder.is_dir():
        folder = repo/'skills/agent-attention'; layer = 'attention'
    outputs = {folder/'scripts/workflow_setup.py': (repo/'scripts/workflow_setup.py').read_text(encoding='utf-8'),
               folder/'references/workflow-integration.md': REFERENCE,
               folder/'assets/workflow-example.json': json.dumps(template(layer), indent=2)+'\n',
               repo/'docs/assets/workflow-setup.svg': picture()}
    errors = []
    for path, contents in outputs.items():
        if write:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(contents, encoding='utf-8', newline='\n')
        elif not path.is_file() or path.read_text(encoding='utf-8') != contents:
            errors.append('stale workflow resource: '+path.relative_to(repo).as_posix())
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args(); errors = check(args.repo.resolve(), args.write)
    print('\n'.join(errors) if errors else 'PASS: workflow setup resources and illustration')
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
