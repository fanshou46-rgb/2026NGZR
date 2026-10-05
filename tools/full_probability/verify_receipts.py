"""Cross-check actual SDK action stream against public execution receipts."""
from pathlib import Path
import argparse,json,re,collections,hashlib,math
ROOT=Path(__file__).resolve().parents[2];LAB=ROOT/'experiments/full_probability'
ANSI=re.compile(r'\x1b\[[0-9;]*m')
def digest(value):
    result=14695981039346656037
    for byte in value.encode('utf8'):
        result=((result^byte)*1099511628211)&((1<<64)-1)
    return result

COSTS={'Move':4,'Sense':1,'AskLoc':2,'Open':2,'Close':2,'PickUp':2,'PutDown':2,
       'ToPlate':2,'FromPlate':2,'PutIn':2,'TakeOut':2}

def verify_policy(node, depth=0):
    assert depth<=64,'policy recursion limit'
    if node.get('stop') is True:
        assert node=={'stop':True}
        return 0
    assert node['action'] in COSTS and node['cost']==COSTS[node['action']]
    assert node['unexpected']=={'stop':True},'missing public feedback fallback'
    children=node['children'];assert children,'non-Stop policy has no feedback branches'
    probabilities=[b['probability'] for b in children]
    assert all(math.isfinite(p) and p>0 for p in probabilities)
    assert abs(sum(probabilities)-1)<1e-8,'finite support probabilities do not sum to one'
    observations=set();nodes=1
    for b in children:
        key=(b['kind'],b['success'],tuple(b['ids']),tuple(b['reply']))
        assert key not in observations;observations.add(key)
        expected=1 if node['action']=='Sense' else 2 if node['action']=='AskLoc' else 0
        assert b['kind']==expected,'feedback kind does not match command'
        nodes+=verify_policy(b['node'],depth+1)
    return nodes

def observed_branch(root,receipt):
    for b in root['children']:
        if root['action']=='Sense':match=set(b['ids'])==set(json.loads(receipt['feedback']))
        elif root['action']=='AskLoc':
            raw=receipt['feedback'];reply=('?',-1)
            if raw=='':reply=('!',-1)
            m=re.fullmatch(r'(at|inside)\((\d+),(\d+)\)',raw)
            if m:reply=('a' if m[1]=='at' else 'i',int(m[3]))
            match=tuple(b['reply'])==reply
        else:match=b['success']==(receipt['outcome']=='succeeded')
        if match:return b['node']
    return None

def sdk_feedback(path):
    result=[]
    for line in ANSI.sub('',path.read_text(errors='replace')).splitlines():
        m=re.fullmatch(r'\s*\[(.+?)\|([^\]]*)\]\s*',line)
        if m:result.append((m[1].strip(),m[2].strip()))
    return result
def main():
    parser=argparse.ArgumentParser();parser.add_argument('checkpoint');parser.add_argument('--suite',default='smoke');a=parser.parse_args()
    records=[json.loads(s) for s in (LAB/(a.checkpoint+'-'+a.suite+'.jsonl')).read_text().splitlines() if s]
    totals=collections.Counter();rows=[]
    failures=[]
    for row in records:
        if row['arm']!='lab':continue
        before_totals=totals.copy()
        try:
            rawlog=(LAB/'runs'/row['key']/'client.log').read_bytes()
            text=rawlog.decode('utf8',errors='replace')
            trace=[];policies=[]
            for line in ANSI.sub('',text).splitlines():
                if '[ExecutionEvidence] {' in line:
                    trace.append(json.loads(line.split('[ExecutionEvidence] ',1)[1]))
                if '[FullPolicy] {' in line:
                    policies.append(json.loads(line.split('[FullPolicy] ',1)[1]))
            prepared=[r for r in trace if r['event']=='prepared']
            finalized=[r for r in trace if r['event']=='finalized']
            assert [r['id'] for r in prepared]==list(range(1,len(prepared)+1)),row['key']
            assert len({r['id'] for r in finalized})==len(finalized),row['key']
            sent=[r for r in finalized if r['status']=='committed']
            actions=[r['action']+(' '+ ' '.join(map(str,r['args'])) if r['args'] else '') for r in sent]
            assert actions==[s.rstrip() for s in row['result']['action_sequence']],(row['key'],actions,row['result']['action_sequence'])
            external=sdk_feedback(LAB/'runs'/row['key']/'server.log')
            assert [a for a,feedback in external]==actions,(row['key'],'raw SDK action stream mismatch')
            for r,(_,raw) in zip(sent,external):
                if r['action']=='Sense':assert list(map(int,raw.split()))==json.loads(r['feedback'])
                else:assert raw==r['feedback'],(row['key'],r['id'],'raw SDK feedback mismatch')
            if row.get('policy')=='full':
                assert len(policies)==len(prepared),row['key']
                previous=None
                for p,receipt,final in zip(policies,prepared,finalized):
                    assert p['receipt']==receipt['id'] and p['decision']==receipt['policy']
                    assert p['before']==receipt['before'] and p['root']['action']==receipt['action']
                    assert p['root']['args']==receipt['args'] and p['root']['cost']==receipt['cost']
                    assert receipt['permit']!='legacy_unqualified'
                    totals['policy_nodes_checked']+=verify_policy(p['root'])
                    if previous and previous[0]['decision']==p['decision']:
                        assert observed_branch(previous[0]['root'],previous[1])==p['root'],(row['key'],'executed suffix differs from selected policy')
                    if observed_branch(p['root'],final) is None:
                        totals['unexpected_feedback_stop']+=1
                    previous=(p,final)
                totals['policies_checked']+=len(policies)
            for r in finalized:
                assert r['id']<=len(prepared)
                p=prepared[r['id']-1]
                assert p['before']==r['before'] and p['action']==r['action'] and p['args']==r['args']
                assert p['remaining_ms']>p['reserved_ms']
                assert all(ref['event']<r['id'] for ref in p['evidence']),row['key']
                if p['permit']=='confirmed':assert p['evidence'] and all(ref['confirmed'] for ref in p['evidence'])
                if p['permit']=='modeled_probe':assert p['policy']>0
                assert r['digest']>0 and r['parent_digest']==(finalized[r['id']-2]['digest'] if r['id']>1 else 0)
                signed=dict(r,event='committed' if r['status']=='committed' else 'cancelled',digest=0)
                body=str(r['parent_digest'])+json.dumps(signed,ensure_ascii=False,separators=(',',':'))
                assert digest(body)==r['digest'],(row['key'],r['id'],'receipt digest mismatch')
                totals[p['permit']]+=1;totals['outcome_'+r['outcome']]+=1
            assert len(prepared)==len(finalized),row['key']
            timings=[r.get('sdk_ns') for r in finalized]
            timing=None
            if any(v is not None for v in timings):
                assert all(isinstance(v,int) and v>=0 for v in timings),'invalid or incomplete SDK durations'
                timing=sum(timings)
                totals['sdk_duration_receipts_checked']+=len(timings)
                totals['sdk_ns']+=timing
                if row.get('policy')=='full':
                    matches=re.findall(r'\[FullModel\] stopped receipts=(\d+) model_ms=(\d+) sdk_ms=([0-9.]+) dispatch_overhead_ms=(-?\d+)',text)
                    assert len(matches)==1,'missing unique controller timing totals'
                    count,model_ms,sdk_ms,overhead=matches[0]
                    assert int(count)==len(finalized) and int(overhead)>=0
                    assert abs(float(sdk_ms)*1e6-timing)<=1,'SDK wait total differs from receipts'
                    totals['model_ms_reported']+=int(model_ms)
                    totals['dispatch_overhead_ms_reported']+=int(overhead)
            cost=sum(r['cost'] for r in sent)
            assert cost==row['result']['action_cost'],(row['key'],cost,row['result']['action_cost'])
            totals['runs']+=1;totals['actions']+=len(sent)
            rows.append(dict(key=row['key'],actions=len(sent),cost=cost,receipt_coverage=1,sdk_ns_checked=timing,
                log_sha256=hashlib.sha256(rawlog).hexdigest()))
        except (AssertionError, ValueError, KeyError, OSError) as error:
            totals=before_totals
            failures.append(dict(key=row['key'],verified=False,reason=str(error) or 'receipt/policy audit assertion failed',client_exit=row['result'].get('client_exit'),official_score=row['result'].get('official_score')))
    result=dict(checkpoint=a.checkpoint,suite=a.suite,totals=dict(totals),runs=rows,failed_runs=failures,
        scope='actual raw SDK commands and feedback, costs, receipt chronology; full policy roots, branch mass, costs, Stop fallback and executed suffix. Finite prior coverage and candidate value calibration are not certified; legacy_unqualified is not a validated policy permit')
    (LAB/(a.checkpoint+'-'+a.suite+'-receipts.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(result['totals'],failed_runs=len(failures))))
if __name__=='__main__':main()
