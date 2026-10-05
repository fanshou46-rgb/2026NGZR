"""Cross-check actual SDK action stream against public execution receipts."""
from pathlib import Path
import argparse,json,re,collections,hashlib,math,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2];LAB=ROOT/'experiments/full_probability'
ANSI=re.compile(r'\x1b\[[0-9;]*m')
def digest(value):
    result=14695981039346656037
    for byte in value.encode('utf8'):
        result=((result^byte)*1099511628211)&((1<<64)-1)
    return result

COSTS={'Move':4,'Sense':1,'AskLoc':2,'Open':2,'Close':2,'PickUp':2,'PutDown':2,
       'ToPlate':2,'FromPlate':2,'PutIn':2,'TakeOut':2}

def public_missing_locations(case_id):
    """Independently reconstruct only SDK Plug input, never author truth labels."""
    bank=ROOT/'题目/independent_100_20261004'
    catalogue=json.loads((bank/'catalogue.json').read_text(encoding='utf8'))
    row=next(c for c in catalogue['cases'] if c['id']==case_id)
    path=bank/row['path'];raw=path.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==row['sha256'],'question hash changed'
    root=ET.fromstring(raw);env=root.find('env')
    get=lambda name:env.findtext(name) or ''
    public=get('info')+' '+('' if env.get('mis')=='on' else get('mis'))+' '+(get('err/w') if env.get('err')=='on' else get('err/r'))
    return parse_public_missing_locations(public,root.findtext('instr') or '',row['stage'])

def parse_public_missing_locations(public,instruction,stage):
    atoms=[tuple(s.split()) for s in re.findall(r'\(([^()]*)\)',public)]
    attrs={}
    for atom in atoms:
        if len(atom)==3 and atom[0] in ('sort','size','color','type'):
            attrs.setdefault(int(atom[1]),set()).add((atom[0],atom[2]))
    supplied_at={int(t[1]) for t in atoms if len(t)==3 and t[0]=='at'}
    tokens=iter(re.findall(r'\(|\)|[^\s()]+',instruction))
    def parse(first):
        if first!='(':return first
        result=[]
        for token in tokens:
            if token==')':return result
            result.append(parse(token))
        raise ValueError('unclosed instruction')
    tree=parse(next(tokens));required=set();acquisitions=set()
    for task in tree[1:]:
        if not isinstance(task,list) or task[0]!=':task':continue
        action,conditions=task[1],task[2][1:]
        acquisition_variable=action[2] if action[0]=='give' and action[1]=='human' else action[1]
        for variable in action[1:]:
            if variable=='human':bound={id for id,a in attrs.items() if ('sort','human') in a}
            elif variable.isdigit():bound={int(variable)}
            else:
                tests={(c[0],c[2]) for c in conditions if len(c)==3 and c[1]==variable}
                assert tests and all(t[0] in ('sort','size','color','type') for t in tests),'unsupported public goal grounding'
                bound={id for id,a in attrs.items() if tests<=a}
            required.update(bound)
            if action[0] in ('pickup','give','puton','putin') and variable==acquisition_variable:acquisitions.update(bound)
    direct=set(required)
    required.update(int(t[2]) for t in atoms if len(t)==3 and t[0]=='inside' and int(t[1]) in direct)
    supplied_inside={int(t[1]) for t in atoms if len(t)==3 and t[0]=='inside'}
    supplied_stored={int(t[1]) for t in atoms if len(t)==2 and t[0] in ('hold','plate') and int(t[1])>0}
    if stage==1:return dict(big=set(),acquisition=set())
    return dict(big={id for id in required if ('size','big') in attrs.get(id,set()) and id not in supplied_at},
        acquisition={id for id in acquisitions if ('size','small') in attrs.get(id,set()) and id not in supplied_at and id not in supplied_inside and id not in supplied_stored})

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

def verify_coverage_schedule(text,decisions):
    schedules={}
    for line in text.splitlines():
        if '[FullCoverageSchedule] ' not in line:continue
        f=dict(re.findall(r'(\w+)=([^\s]+)',line));d=int(f['decision']);source=int(f['source_decision'])
        assert d not in schedules and source==d-1,'ambiguous coverage predecessor'
        assert f['trigger']=='ordinary_finite_candidate_stop' and f['acquisitions']=='deferred'
        assert f['canonical_answer_authority']=='false' and int(f['before'])>=0
        assert decisions[source]['scope']=='finite_catalogue_complete_candidates' and decisions[source]['selected_stop']=='true'
        assert decisions[d]['scope'] in ('necessary_initial_missing_acquisition_location','necessary_initial_missing_big_location')
        assert decisions[source]['support']==decisions[d]['support'],'coverage predecessor belief differs'
        schedules[d]=f
    if 'acquisition_schedule=after_ordinary_stop' in text:
        assert {d for d,f in decisions.items() if f['scope']=='necessary_initial_missing_acquisition_location'}<=set(schedules),'acquisition coverage precedes ordinary Stop'
    return schedules
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
            trace=[];policies=[];catalogues={}
            for line in ANSI.sub('',text).splitlines():
                if '[ExecutionEvidence] {' in line:
                    trace.append(json.loads(line.split('[ExecutionEvidence] ',1)[1]))
                if '[FullPolicy] {' in line:
                    p=json.loads(line.split('[FullPolicy] ',1)[1])
                    if p['schema']=='full_policy.v2':
                        c=catalogues[p['decision']]
                        assert p['catalogue']==c['digest'] and p['node'] in c['nodes']
                        if not c['used']:assert p['node']==1,'first action is not the catalogue root'
                        c['used']=True;p['root']=c['nodes'][p['node']]
                        totals['actual_policy_references_checked']+=1
                    else:assert p['schema']=='full_policy.v1'
                    policies.append(p)
                if '[FullPolicyCatalogue] {' in line:
                    payload=line.split('[FullPolicyCatalogue] ',1)[1].rstrip();c=json.loads(payload)
                    assert c['schema']=='full_policy_catalogue.v2' and c['decision'] not in catalogues
                    rawroot=payload.split('"root":',1)[1][:-1]
                    assert json.loads(rawroot)==c['root'] and digest(rawroot)==c['digest']
                    assert c['root'].get('stop') is not True
                    nodes={}
                    def index(node):
                        if node.get('stop') is True:return
                        nodes[len(nodes)+1]=node
                        for b in node['children']:index(b['node'])
                    totals['catalogue_nodes_checked']+=verify_policy(c['root'])
                    index(c['root']);c.update(nodes=nodes,node_ids={id(node):number for number,node in nodes.items()},used=False);catalogues[c['decision']]=c
            assert all(c['used'] for c in catalogues.values()),'unused selected catalogue'
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
                decisions={}
                missing_logs=set();acquisition_logs=set()
                for line in text.splitlines():
                    if '[InitialMissingLocation] ' in line:
                        f=dict(re.findall(r'(\w+)=([^\s]+)',line))
                        assert f['required']=='true' and f['received_at']=='false' and f['source']=='public_input_absence'
                        missing_logs.add(int(f['object']))
                    if '[InitialMissingAcquisitionLocation] ' in line:
                        f=dict(re.findall(r'(\w+)=([^\s]+)',line))
                        assert f['required_acquisition']=='true' and f['received_at']=='false' and f['received_inside']=='false' and f['source']=='public_input_absence'
                        acquisition_logs.add(int(f['object']))
                if missing_logs or 'missing_location_policy=bounded_public_input_coverage' in text:
                    public_missing=public_missing_locations(row['id'])
                    assert missing_logs==public_missing['big'],'initial absence/goal dependency differs from immutable public input'
                    if acquisition_logs or 'acquisition_coverage=bounded_public_input_absence' in text:
                        assert acquisition_logs==public_missing['acquisition'],'initial acquisition absence differs from immutable public input'
                for line in text.splitlines():
                    if '[FullDecisionEvidence] ' not in line:continue
                    fields=dict(re.findall(r'(\w+)=([^\s]+)',line))
                    decision_id=int(fields['decision']);assert decision_id not in decisions
                    values=[float(fields[k]) for k in ('stop_lower','stop_upper','selected_lower','selected_upper')]
                    assert all(math.isfinite(v) for v in values)
                    sl,su,vl,vu=values;assert sl<=su+1e-7 and vl<=vu+1e-7
                    coverage=fields['scope'] in ('necessary_initial_missing_big_location','necessary_initial_missing_acquisition_location')
                    if coverage:
                        allowed=acquisition_logs if fields['scope']=='necessary_initial_missing_acquisition_location' else missing_logs
                        assert fields['selected_stop']=='false' and int(fields['target']) in allowed
                        assert fields['initial_at_missing']=='true' and 0<=int(fields['attempts_before'])<3
                        assert abs(vl-(sl-COSTS['AskLoc']))<1e-7 and abs(vu-(su-COSTS['AskLoc']))<1e-7
                        totals['required_location_observations_checked']+=1
                    elif fields['selected_stop']=='true':assert abs(sl-vl)<1e-7 and abs(su-vu)<1e-7
                    else:assert fields['selected_stop']=='false' and vl>su-1e-7
                    assert int(fields['support'])>0 and int(fields['information_candidates'])>=0
                    assert fields['scope'] in ('finite_catalogue_complete_candidates','necessary_initial_missing_big_location','necessary_initial_missing_acquisition_location')
                    decisions[decision_id]=fields;totals['decision_values_checked']+=1
                schedules=verify_coverage_schedule(text,decisions)
                totals['deferred_coverage_predecessors_checked']+=len(schedules)
                stops=[line for line in text.splitlines() if '[FullStopEvidence] ' in line]
                if decisions:
                    assert len(stops)==1,'missing unique termination evidence'
                    for p in policies:
                        if p['decision']>1:assert p['decision'] in decisions and decisions[p['decision']]['selected_stop']=='false'
                    fields=dict(re.findall(r'(\w+)=([^\s]+)',stops[0]))
                    assert fields['reason'] and int(fields['model_ns'])>=0
                    assert fields['prior_coverage_certified']=='false'
                    totals['termination_reasons_checked']+=1
                previous=None
                domain_receipts=set()
                for line in text.splitlines():
                    if '[FullDomainEvidence] ' not in line:continue
                    f=dict(re.findall(r'(\w+)=([^\s]+)',line));rid=int(f['receipt'])
                    assert rid not in domain_receipts and 1<=rid<=len(finalized)
                    domain_receipts.add(rid);r=finalized[rid-1]
                    assert r['action']=='AskLoc' and r['args']==[int(f['query'])]
                    assert r['feedback']=='at({},{})'.format(f['query'],f['location'])
                    assert 0<=int(f['location'])<=4095 and int(f['refined_variables'])>=0
                    assert float(f['added_prior_mass'])==.05 and f['canonical_at_written']=='false'
                    assert f['scope']=='approximate_prior_domain_extension'
                    totals['actual_answer_domain_extensions_checked']+=1
                for p,receipt,final in zip(policies,prepared,finalized):
                    assert p['receipt']==receipt['id'] and p['decision']==receipt['policy']
                    assert p['before']==receipt['before'] and p['root']['action']==receipt['action']
                    assert p['root']['args']==receipt['args'] and p['root']['cost']==receipt['cost']
                    assert receipt['permit']!='legacy_unqualified'
                    f=decisions.get(p['decision'],{})
                    if f.get('scope') in ('necessary_initial_missing_big_location','necessary_initial_missing_acquisition_location'):
                        assert receipt['action']=='AskLoc' and receipt['args']==[int(f['target'])]
                        assert receipt['reason']=='necessary_public_missing_location_coverage'
                        assert all(b['node']=={'stop':True} for b in p['root']['children'])
                        prior_queries=sum(r['action']=='AskLoc' and r['args']==receipt['args'] for r in finalized if r['id']<receipt['id'])
                        assert prior_queries==int(f['attempts_before']) and prior_queries<3
                        if p['decision'] in schedules:assert int(schedules[p['decision']]['before'])==receipt['before'],'coverage changed canonical state after Stop'
                    totals['policy_nodes_checked']+=verify_policy(p['root'])
                    if previous and previous[0]['decision']==p['decision']:
                        expected=observed_branch(previous[0]['root'],previous[1])
                        assert expected==p['root'],(row['key'],'executed suffix differs from selected policy')
                        if p['schema']=='full_policy.v2':
                            c=catalogues[p['decision']]
                            assert previous[0]['schema']=='full_policy.v2' and previous[0]['catalogue']==p['catalogue']
                            assert p['node']==c['node_ids'].get(id(expected)),(row['key'],'node reference does not follow actual public feedback')
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
