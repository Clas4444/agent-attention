"""Small audit counters: model attempts are distinct from scorer controls."""


def summarize(records):
    seen=set();counts={'PASS':0,'FAIL':0,'BLOCKED_ENVIRONMENT':0}
    for row in records:
        trial=row.get('trial_id')
        if not isinstance(trial,str) or not trial or trial in seen:
            raise ValueError('every model attempt needs a unique trial_id')
        if row.get('kind')!='model_trial':
            raise ValueError('scorer controls are not model attempts')
        status=row.get('classification')
        if status not in counts: raise ValueError('unknown classification')
        seen.add(trial);counts[status]+=1
    evaluated=counts['PASS']+counts['FAIL']
    return {'attempts':len(seen),'successes':counts['PASS'],'failures':counts['FAIL'],
            'environment_blocked':counts['BLOCKED_ENVIRONMENT'],'evaluated_attempts':evaluated,
            'success_rate':counts['PASS']/evaluated if evaluated else None,
            'status':'MEASURED' if evaluated else 'NOT_RUN'}
