"""Explanatory attention cards, matching the existing light bundle atlas style."""
import html
import textwrap

DETAILS = {
 'focus': ('Attention width', 'How much related work stays in active context?', [
  ('One action', 'A small isolated task', 'Keep a pointer to the shared goal.', 'Forget callers when a contract changes.'),
  ('One component', 'A local module change', 'Read its immediate contract.', 'Assume neighboring modules agree.'),
  ('Balanced', 'An ordinary scoped task', 'Expand for concrete dependencies.', 'Read every file by default.'),
  ('Direct dependents', 'An API or schema change', 'Compare affected caller assumptions.', 'Widen the authorized task.'),
  ('Relevant whole flow', 'An end-to-end contract', 'Keep cross-component constraints visible.', 'Carry irrelevant detail forever.')]),
 'sync': ('Reconciliation cadence', 'When should the loop compare local progress with shared state?', [
  ('At completion*', 'Independent work with stable inputs', 'Reconcile earlier on contract change.', 'Defer a known conflict until delivery.'),
  ('After a group', 'Related tasks with few shared edges', 'Check shared assumptions at handoff.', 'Pass stale checkpoints onward.'),
  ('Balanced', 'Normal task boundaries', 'Reconcile at important milestones.', 'Treat a saved plan as current proof.'),
  ('After shared changes', 'Several callers share a contract', 'Compare dependencies before proceeding.', 'Recheck unrelated state after every edit.'),
  ('After shared-state steps', 'Closely coupled or changing inputs', 'Keep short, explicit reconciliations.', 'Let coordination replace useful work.')]),
 'batch': ('Work per iteration', 'How much work is planned before the next loop checkpoint?', [
  ('One action', 'One hypothesis or risky operation', 'Observe the result before moving on.', 'Change several debug hypotheses together.'),
  ('Small change', 'A narrow reversible edit', 'Keep rollback and checks local.', 'Split work into meaningless fragments.'),
  ('Balanced', 'A complete bounded work item', 'Finish a useful acceptance item.', 'Require extra rounds after completion.'),
  ('Related group', 'Changes sharing one acceptance goal', 'Check each dependency boundary.', 'Bundle unrelated fixes.'),
  ('Larger stage', 'A coherent authorized stage', 'Keep reversible internal checkpoints.', 'Make one unreviewable giant change.')]),
 'explore': ('Exploration breadth', 'Where should the loop look before selecting its next action?', [
  ('Supplied sources*', 'A known target with clear inputs', 'Follow required dependencies if found.', 'Ignore evidence outside the first file.'),
  ('Immediate references', 'A localized task', 'Read direct imports and contracts.', 'Assume names prove behavior.'),
  ('Balanced', 'Ordinary uncertainty', 'Expand for a specific open question.', 'Search the whole repo repeatedly.'),
  ('Direct dependencies', 'Likely cross-component impact', 'Look proactively for conflicting assumptions.', 'Expand without a task-related reason.'),
  ('Relevant flow map', 'An unfamiliar connected system', 'Map the relevant route, then act.', 'Keep exploring after enough evidence.')]),
 'verify': ('Verification depth', 'What additional evidence should the loop seek above the required floor?', [
  ('Direct result*', 'A small low-impact outcome', 'Keep mandatory and risk-triggered checks.', 'Call untested work PASS.'),
  ('Immediate contract', 'A local behavior change', 'Check affected inputs and consumers.', 'Verify only an internal helper.'),
  ('Balanced', 'Normal risk-based verification', 'Use the original skill checks.', 'Confuse source review with execution.'),
  ('Regression + boundaries', 'A bug fix or shared contract', 'Test nearby paths and legitimate behavior.', 'Add checks with no relevant risk.'),
  ('Independent checks', 'Consequential assumptions', 'Cross-check important claims independently.', 'Treat more checks as guaranteed quality.')])}


def text(x, y, value, size=19, color='#415d67', width=24, bold=False):
    weight = ' font-weight="700"' if bold else ''
    lines = textwrap.wrap(value, width=width, break_long_words=False, break_on_hyphens=False)
    return '\n'.join(f'<text x="{x}" y="{y+i*(size+8)}" font-size="{size}" fill="{color}"{weight}>{html.escape(line)}</text>' for i,line in enumerate(lines))


def frame(title, desc, height=1040):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="{height}" viewBox="0 0 1440 {height}" role="img" aria-labelledby="title desc">',
      f'<title id="title">{html.escape(title)}</title><desc id="desc">{html.escape(desc)}</desc>',
      f'<rect width="1440" height="{height}" rx="20" fill="#f2f6f4"/>',
      '<g font-family="Arial, Helvetica, sans-serif" fill="#16313b">']


def axis_diagram(axis, directives):
    title, why, levels = DETAILS[axis]
    out = frame(title+' — five loop behaviors', why)
    out += [text(40,38,'AGENT ATTENTION / '+axis.upper(),15,'#126957',100,True),
            text(40,90,title,36,'#16313b',65,True),
            text(40,140,why,21,width=110),
            text(40,185,'Choose the behavior that fits the task. Level 3 keeps the ordinary skill policy.',19,width=120)]
    for i, (name, when, do, avoid) in enumerate(levels):
        x=40+i*276
        border='#126957' if i==2 else '#cddcda'
        out += [f'<rect x="{x}" y="225" width="256" height="680" rx="12" fill="#ffffff" stroke="{border}" stroke-width="{2 if i==2 else 1}"/>',
          text(x+18,257,f'{i+1:02} / '+('BALANCED' if i==2 else axis.upper()),15,'#126957',25,True),
          text(x+18,296,name,22,'#16313b',18,True),
          text(x+18,382,'LOOP BEHAVIOR',14,'#126957',25,True),
          text(x+18,413,directives[i],17,width=25),
          text(x+18,595,'CHOOSE WHEN',14,'#126957',25,True),
          text(x+18,623,when,17,width=24),
          text(x+18,711,'DO',14,'#126957',25,True),
          text(x+18,739,do,17,width=25),
          text(x+18,816,'AVOID',14,'#9a4c32',25,True),
          text(x+18,844,avoid,16,'#6d4940',27)]
    out += ['<rect x="40" y="930" width="1360" height="76" rx="12" fill="#e0eee8"/>',
      text(60,960,'Always: preserve permissions, required checks and task scope. Stop when complete or blocked.',18,'#16313b',140,True),
      text(60,987,'* Required dependencies and shared-contract reconciliation override sparse timing. Token savings remain unmeasured.',16,width=150),'</g></svg>\n']
    return '\n'.join(out)


def overview():
    out=frame('How attention settings change a loop','Five behavior choices, each with five levels. No requested setting means balanced.',900)
    out += [text(40,38,'AGENT ATTENTION / EXPERIMENT',15,'#126957',100,True),text(40,90,'One task. Five independent behavior choices.',34,'#16313b',90,True),
            text(40,135,'No requested setting: use the ordinary balanced workflow. Numbers are positions, not quality scores.',19,width=125)]
    for i,(axis,(title,why,levels)) in enumerate(DETAILS.items()):
        y=175+i*112
        out += [f'<rect x="40" y="{y}" width="1360" height="96" rx="10" fill="#ffffff" stroke="#cddcda"/>',
                text(58,y+30,title,20,'#16313b',30,True),text(58,y+58,axis,15,'#126957',25)]
        for j,(name,*_) in enumerate(levels):
            out += [text(365+j*204,y+30,f'{j+1} / '+name,17,'#126957' if j==2 else '#415d67',21,j==2)]
    out += ['<rect x="40" y="755" width="1360" height="105" rx="12" fill="#e0eee8"/>',
      text(60,788,'Select useful action → act → check → reconcile when needed → next action or STOP',22,'#16313b',120,True),
      text(60,824,'Narrow focus can reduce active context but increase rework. Wider context adds cost and cross-component awareness.',18,width=145),'</g></svg>\n']
    return '\n'.join(out)
