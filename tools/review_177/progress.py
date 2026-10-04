"""Compact provisional totals from completed pairs; never used to choose reruns."""
import collections,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def main():
    path=ROOT/'validation/review177-20261004/raw/frozen-v1/results.json'
    if not path.exists():print('Author preflight');return
    rows=json.loads(path.read_text(encoding='utf8'));pairs=collections.defaultdict(dict)
    for row in rows:pairs[(row['suite'],row['id'],row['mode'],row['seed'])][row['version']]=row['result']
    groups=collections.defaultdict(lambda:collections.Counter())
    for key,pair in pairs.items():
        if len(pair)!=2:continue
        a,b=pair['src1.7.6'],pair['src1.7.7'];g=groups[key[0]];g['pairs']+=1
        for k in ('base','official_score','final_goals','action_cost','platform_seconds'):
            if a.get(k) is not None and b.get(k) is not None:g[k]+=b[k]-a[k]
        g['goal_regressions']+=b.get('final_goals',0)<a.get('final_goals',0)
        g['baseline_timeouts']+=bool(a.get('platform_timed_out'))
        g['current_timeouts']+=bool(b.get('platform_timed_out'))
    print('Completed:',len(rows),'/304; provisional current minus baseline')
    for name,g in groups.items():print(name,dict(g))
if __name__=='__main__':main()
