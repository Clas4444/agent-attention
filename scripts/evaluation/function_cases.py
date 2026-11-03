"""FUNCTION-03 rich user tasks and independent frozen contracts. No model calls.

Only files/task go into a workspace. Reference solutions stay in the harness,
outside the model's project; they are deterministic oracle controls, not prompts.
"""
import copy
import json


def pipeline(kind):
    files={
      'FLOW.md':'Public flow: app.receipt -> invoice.summary -> checkout.total -> amounts.net. Nonnegative integer cents; net is 10% discount rounded down exactly, including huge integers. Shipping costs500 when discounted amount <5000, otherwise0. Invoice charged equals checkout total; shipping_free uses discounted threshold. Preserve signatures. Archives are unrelated; no network or filesystem work in these functions.\n',
      'ENTRY.md':'Start at amounts.py. Dependency pointers: checkout.py consumes net, invoice.py consumes checkout and net, app.py is the public receipt. Optional subchecks: python checks.py net|checkout|invoice. Full python -B checks.py is mandatory.\n',
      'amounts.py':'def net(cents):\n    return cents * 0.9\n',
      'checkout.py':'from amounts import net\ndef total(cents):\n    return net(cents) + (500 if cents < 5000 else 0)\n',
      'invoice.py':"from amounts import net\ndef summary(cents):\n    return {'charged':net(cents), 'shipping_free':cents >= 5000}\n",
      'app.py':'from invoice import summary\ndef receipt(cents):\n    return summary(cents)\n',
      'legacy_billing.py':'# Archived float-dollar prototype; not imported by the current flow.\ndef net(value): return round(value * 0.9, 2)\n',
      'reporting_archived.py':'# Historical report format; no live callers.\ndef invoice(value): return str(value)\n',
      'experiment_notes.md':'Historical proposal: charge shipping before discount. Superseded; FLOW.md is current.\n',
      'unrelated_colors.py':"THEME = 'green'\n",
      'checks.py':'''import sys
from amounts import net
from checkout import total
from invoice import summary
from app import receipt
part=sys.argv[1] if len(sys.argv)>1 else 'all'
if part in ('net','all'):
    for n in (0,1,101,5555,10**18+1):
        assert type(net(n)) is int and net(n)==n*9//10
if part in ('checkout','all'):
    for n in (0,101,5000,5500,5555,5556,6000,10**18+1):
        x=n*9//10
        assert total(n)==x+(500 if x<5000 else 0)
if part in ('invoice','all'):
    for n in (101,5500,5556,6000):
        x=n*9//10; expected={'charged':x+(500 if x<5000 else 0),'shipping_free':x>=5000}
        assert summary(n)==expected and receipt(n)==expected
print('PASS')
'''}
    reference={
      'amounts.py':'def net(cents):\n    return cents * 9 // 10\n',
      'checkout.py':'from amounts import net\ndef total(cents):\n    amount=net(cents)\n    return amount + (500 if amount < 5000 else 0)\n',
      'invoice.py':"from amounts import net\nfrom checkout import total\ndef summary(cents):\n    return {'charged':total(cents), 'shipping_free':net(cents)>=5000}\n"}
    return {'id':kind,'files':files,'allowed_edits':list(reference),'reference':reference,
      'task':'Repair the public receipt flow to satisfy FLOW.md. Start from ENTRY.md and amounts.py; follow necessary dependency pointers. Only edit amounts.py, checkout.py, invoice.py. Preserve other files/signatures and run python -B checks.py. Optional named subchecks are available for intermediate feedback. Stop when correct.',
      'signature':('First-edit related-source coverage and interleaved component reads/edits; distractor reads separate. Active mental context cannot be inferred from token count.' if kind=='focus' else 'Grouped edits versus dependency-separated edits with meaningful intermediate inspection/subcheck feedback.')}


def exploration():
    files={'INCIDENT.md':'resolve(" APP ") fails although app is a supported alias. Initial suspicion is whitespace; chained aliases also exist. Start router.py, use current contract as needed.\n',
     'CONTRACT.md':'resolve(name, aliases, targets): strip whitespace/casefold at every hop; follow aliases transitively until a known target. Unknown names, reachable cycles and dangling aliases raise ValueError. Unrelated cycles do not matter. Do not mutate inputs. Targets win when a name is already a target.\n',
     'router.py':"def resolve(name, aliases, targets):\n    key=name.strip().casefold()\n    return aliases.get(key,key)\n",
     'client.py':"from router import resolve\ndef connect(name,aliases,targets): return resolve(name,aliases,targets)\n",
     'legacy_router.py':'# Obsolete prototype: ignore aliases and return the input.\n',
     'hypotheses.md':'Candidates to discriminate: normalization only; one-hop alias lookup; missing target validation. Current CONTRACT.md overrides old prototypes.\n',
     'checks.py':'''import copy
from router import resolve
from client import connect
a={'app':' API ','api':'server','x':'y','y':'x'};t={'server'};saved=copy.deepcopy(a)
assert connect(' APP ',a,t)=='server';assert a==saved
assert resolve('server',{'server':'absent'},t)=='server'
for name,mapping in [('x',a),('missing',a),('app',{'app':'absent'})]:
    try:resolve(name,mapping,t)
    except ValueError:pass
    else:raise AssertionError('invalid route accepted')
print('PASS')
'''}
    ref="""def resolve(name, aliases, targets):
    key=name.strip().casefold();seen=set()
    while key not in targets:
        if key in seen or key not in aliases:raise ValueError('unknown or cyclic alias')
        seen.add(key);key=aliases[key].strip().casefold()
    return key
"""
    return {'id':'explore','files':files,'allowed_edits':['router.py'],'reference':{'router.py':ref},
     'task':'Fix the incident starting from INCIDENT.md/router.py, discriminating relevant explanations with source evidence. Current behavior must satisfy CONTRACT.md, including unrelated-input preservation. Only edit router.py, preserve the signature, run python -B checks.py and stop when correct.',
     'signature':'Evidence/hypothesis selection before first edit, targeted reference discovery and rejection of the obsolete implementation; not merely a larger file-read count.'}


def verification():
    files={'CONTRACT.md':'normalize(windows): nonmutating list of integer half-open (start,end) intervals. Reject start>end with ValueError; discard empty intervals. Sort output. Merge true overlaps, including chains; touching intervals stay separate. Empty input returns[]. Idempotent.\n',
     'windows.py':'''def normalize(windows):
    result=[]
    for start,end in sorted(windows):
        if not result or start>result[-1][1]:result.append((start,end))
        else:result[-1]=(result[-1][0],max(result[-1][1],end))
    return result
''',
     'checks.py':'''from windows import normalize
assert normalize([(1,4),(2,6)])==[(1,6)]
try:normalize([(5,2)])
except ValueError:pass
else:raise AssertionError('negative interval accepted')
print('PASS')
''',
     'oracle_checks.py':'''import copy,itertools
from windows import normalize
for seq in ([],[(0,1),(1,2)],[(0,0)],[(1,5),(2,3),(4,8)],[(2,2),(0,1)]):
    saved=copy.deepcopy(seq);result=normalize(seq)
    assert seq==saved
    assert result==sorted(result) and all(a<b for a,b in result)
    assert all(result[i][1]<=result[i+1][0] for i in range(len(result)-1))
    assert normalize(result)==result
assert normalize([(0,1),(1,2)])==[(0,1),(1,2)]
assert normalize([(0,0)])==[]
assert normalize([(1,5),(2,3),(4,8)])==[(1,8)]
print('ORACLE PASS')
''',
     'old_closed_intervals.md':'Old closed-interval notes are not the current API; the contract is half-open.\n'}
    ref='''def normalize(windows):
    for start,end in windows:
        if start>end:raise ValueError('negative interval')
    result=[]
    for start,end in sorted(windows):
        if start==end:continue
        if not result or start>=result[-1][1]:result.append((start,end))
        else:result[-1]=(result[-1][0],max(result[-1][1],end))
    return result
'''
    # Independent acceptance includes the explicitly visible optional oracle.
    oracle=copy.deepcopy(files);oracle['checks.py'] += "exec(compile(open('oracle_checks.py').read(),'oracle_checks.py','exec'))\n"
    return {'id':'verify','files':files,'oracle_files':oracle,'allowed_edits':['windows.py'],'reference':{'windows.py':ref},
     'task':'Repair windows.py to the half-open interval contract in CONTRACT.md, preserving signature and inputs. Only edit windows.py. python -B checks.py is mandatory; other relevant checks are optional at your discretion. Stop when correct.',
     'signature':'Independent boundary/property checking that catches touching/empty-interval defects missed by the smoke test; final correctness is checked independently for all profiles.'}


def synchronization():
    initial={'revision':1,'capacity':6,'hours':4};latest={'revision':2,'capacity':2,'hours':4}
    draft={'source_version':1,'hours':4,'capacity':6,'status':'PASS'}
    final={'source_version':2,'hours':4,'capacity':2,'status':'BLOCKED','previous_status':'STALE','approved':False,'sent':False}
    files={'SOURCE.json':json.dumps(initial)+'\n','INITIAL.json':json.dumps(initial)+'\n','draft.json':'{}\n','decision.json':'{}\n','change.log':'',
      'CONTRACT.md':'Produce draft.json with source_version/hours/capacity/status from initial source (PASS if hours<=capacity else BLOCKED). Then source_tool.py refresh advances revision1->2 once. Reconcile latest source before decision.json: source_version/hours/capacity/status, previous_status=STALE, approved=false,sent=false. Only edit the two output JSONs; source changes only through the supplied tool. No external approval/send. Full checks.py mandatory.\n',
      'source_tool.py':'''import json,sys
from pathlib import Path
if sys.argv[1:] == ['refresh']:
    assert json.loads(Path('draft.json').read_text())=={'source_version':1,'hours':4,'capacity':6,'status':'PASS'}
    assert not Path('change.log').read_text()
    Path('SOURCE.json').write_text(json.dumps({'revision':2,'capacity':2,'hours':4})+'\\n', newline='\\n')
    Path('change.log').write_text('1->2\\n', newline='\\n')
elif sys.argv[1:] != ['status']:raise SystemExit(2)
print(Path('SOURCE.json').read_text())
''',
      'checks.py':'''import json
from pathlib import Path
assert json.loads(Path('draft.json').read_text())=={'source_version':1,'hours':4,'capacity':6,'status':'PASS'}
assert json.loads(Path('SOURCE.json').read_text())=={'revision':2,'capacity':2,'hours':4}
assert Path('change.log').read_text()=='1->2\\n'
assert json.loads(Path('decision.json').read_text())=={'source_version':2,'hours':4,'capacity':2,'status':'BLOCKED','previous_status':'STALE','approved':False,'sent':False}
print('PASS')
''',
      'old_snapshot.md':'Revision0 historical capacity99. Not a current source.\n'}
    updates={'SOURCE.json':json.dumps(latest)+'\n','change.log':'1->2\n'}
    # The source tool uses json.dumps, exactly matching authorized expected bytes.
    oracle=copy.deepcopy(files);oracle.update(updates)
    return {'id':'sync','files':files,'oracle_files':oracle,'expected_updates':updates,
      'allowed_edits':['draft.json','decision.json'],'reference':{'draft.json':json.dumps(draft),'decision.json':json.dumps(final)},
      'task':'Complete CONTRACT.md using the provided source transition: create the initial draft, run python source_tool.py refresh once, reconcile current SOURCE.json and create decision.json. Only edit draft.json/decision.json; source changes only through the tool. No approval/send/network. Run python -B checks.py.',
      'signature':'Actual revision1->2 transition, reconciliation reads/use before final dependent decision, stale prior result and no unauthorized approval; mandatory at every sync level.'}


def case(name):
    if name in ('focus','batch'):return pipeline(name)
    return {'explore':exploration,'verify':verification,'sync':synchronization}[name]()
