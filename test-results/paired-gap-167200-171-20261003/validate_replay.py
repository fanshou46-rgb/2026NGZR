#!/usr/bin/env python3
"""Validate witness derivation against retained SDK final states, no reruns."""
from pathlib import Path
import sys
sys.dont_write_bytecode=True
import analyze_direct_pairs as a
import inspect_evidence as i

rows=i.load(i.DIRECT/'results.json') if (i.DIRECT/'final-audit.json').exists() else i.prior()
errors=[];checked=0
for r in rows:
    if r['stage']!=2 or r['baseline']['final_goals']<=r['current']['final_goals']:continue
    for arm in ('baseline','current'):
        run=Path(r[arm]['output']);tasks=a.ground_tasks(run);ev=a.events(run/'server.log');s,h=a.replay(Path(r['path']),ev,tasks)
        expected=set(a.values(run/'runtime/vanswer.txt')[40]);actual={gid for gid,t in tasks.items() if a.satisfies(s,t)}
        if actual!=expected:errors.append(dict(id=r['id'],mode=r['mode'],round=r['round'],arm=arm,expected=sorted(expected),actual=sorted(actual)))
        checked+=1
print(a.json.dumps(dict(checked=checked,errors=errors),ensure_ascii=False,indent=2))
assert not errors
