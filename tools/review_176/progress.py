"""Read completed rows only; never change or replace a production run."""
import collections,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
rows=json.loads((ROOT/'validation/review176-20261004/raw/frozen-v2/results.json').read_text(encoding='utf8'))
pairs=collections.defaultdict(dict);over=collections.Counter();changes=[]
for row in rows:
    r=row['result'];pairs[(row['suite'],row['id'],row['mode'],row['seed'])][row['version']]=r
    path=ROOT/'validation/review176-20261004/raw/frozen-v2/runs'/Path(r['output']).name
    text=(path/'client.log').read_text(encoding='utf8',errors='replace')
    matches=re.findall(r'\[3A\]\[final\] goals=(\d+)',text)
    if matches and r.get('final_goals') is not None and int(matches[-1])>r['final_goals']:over[(row['suite'],row['version'])]+=1
for key,p in pairs.items():
    if len(p)==2 and p['src1.7.5'].get('final_goals')!=p['src1.7.6'].get('final_goals'):
        changes.append((key,[(v,x.get('base'),x.get('final_goals'),x.get('action_cost'),x.get('platform_timed_out')) for v,x in p.items()]))
print('Completed:',len(rows),'Goal overclaims:',dict(over),'Goal changes:',changes)
