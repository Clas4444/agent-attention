"""Shared transport stopping and append-only campaign state; no model calls."""
import json
import math
from pathlib import Path


def failure_reason(events, stderr):
    messages = [stderr]
    for event in events:
        if event.get('type') in ('error', 'session.error', 'turn.failed'):
            data = event.get('data', event.get('error', event))
            messages.append(json.dumps(data))
    text = '\n'.join(messages).casefold()
    for label, needles in [
        ('QUOTA_LIMIT', ('monthly quota', 'usage limit', 'quota exceeded')),
        ('RATE_LIMIT', ('http 429', '429 too many', 'rate limit')),
        ('MODEL_CAPACITY', ('at capacity', 'capacity exceeded')),
        ('AUTH_FAILURE', ('authentication failed', 'not authenticated', 'unauthorized', 'login required'))]:
        if any(n in text for n in needles): return label
    return None


def classify(code, events, stderr, accepted, changed=False):
    actions = any(e.get('type') in ('tool.execution_start', 'tool.execution_complete',
                                  'item.started', 'item.completed') and
                  (e.get('type').startswith('tool.') or e.get('item', {}).get('type') in
                   ('command_execution', 'file_change', 'mcp_tool_call')) for e in events)
    if failure_reason(events, stderr):
        return 'FAIL' if actions or changed else 'BLOCKED_ENVIRONMENT'
    return 'PASS' if code == 0 and accepted else 'FAIL'


def parse_usage(value):
    if value is None: return None
    fields = ('input_tokens', 'output_tokens', 'cached_input_tokens')
    if not isinstance(value, dict) or any(type(value.get(k)) is not int or value[k] < 0 for k in fields):
        raise ValueError('missing/invalid usage fields')
    if value['cached_input_tokens'] > value['input_tokens']: raise ValueError('cache exceeds input')
    for key in ('cache_write_tokens', 'reasoning_tokens', 'premium_requests', 'api_duration_ms'):
        if key in value and (type(value[key]) not in (int, float) or not math.isfinite(value[key]) or value[key] < 0):
            raise ValueError('invalid usage: '+key)
    return dict(value, total_tokens=value['input_tokens']+value['output_tokens'])


def pending(plan, attempts):
    ids = [row['id'] for row in plan]
    if len(ids) != len(set(ids)): raise ValueError('duplicate planned id')
    if any(r['id'] not in ids for r in attempts): raise ValueError('unplanned attempt')
    return [key for key in ids if key not in {r['id'] for r in attempts}]


def append_attempt(path, row):
    path = Path(path)
    rows = [json.loads(s) for s in path.read_text(encoding='utf-8').splitlines()] if path.exists() else []
    prior = [r for r in rows if r['id'] == row['id']]
    expected = len(prior)+1
    if row.get('attempt') != expected or (prior and row.get('retry_of') != expected-1):
        raise ValueError('attempt must append a linked retry; never overwrite')
    with path.open('a', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(row, allow_nan=False)+'\n')


def stop(marker, reason, attempt):
    """Exclusive creation keeps the first chat's stop reason; never clears it."""
    marker = Path(marker); marker.parent.mkdir(parents=True, exist_ok=True)
    try:
        with marker.open('x', encoding='utf-8') as stream:
            json.dump({'reason':reason, 'owner':'agent-attention', 'attempt':attempt}, stream)
    except FileExistsError: pass


def execute_plan(plan, ledger, marker, invoke, max_calls=24):
    """One callback in flight; reserve attempts before CLI to survive interruption.

    Pending reservations are never automatically retried. Explicit retries use
    append_attempt separately after new authorization and a reviewed stop marker.
    """
    ledger=Path(ledger); marker=Path(marker)
    existing=[json.loads(s) for s in ledger.read_text().splitlines()] if ledger.exists() else []
    reserved=ledger.with_suffix('.reserved.jsonl')
    prior=[json.loads(s) for s in reserved.read_text().splitlines()] if reserved.exists() else []
    seen={r['id'] for r in existing+prior}
    count=max(len(prior),len(existing))
    reservations=list(prior)
    for row in plan:
        if row['id'] in seen: continue
        if marker.exists() or count>=max_calls: break
        with reserved.open('a',encoding='utf-8') as stream:
            stream.write(json.dumps({'id':row['id'],'attempt':1})+'\n')
        reservations.append({'id':row['id'],'attempt':1})
        count+=1
        try: result=invoke(row)
        except Exception as error:
            stop(marker,'HARNESS_ERROR',row['id'])
            raise RuntimeError('attempt reserved; inspect private evidence before any retry') from error
        result.update(id=row['id'],attempt=1)
        append_attempt(ledger,result);existing.append(result)
        if result.get('stop_reason'):
            stop(marker,result['stop_reason'],row['id']);break
    return {'attempts':existing,'not_run':pending(plan,existing+reservations),
            'reserved_without_result':[r['id'] for r in reservations if r['id'] not in {a['id'] for a in existing}]}
