"""Audit modeled future SDK time from policy edges, not unexecuted labels."""
from pathlib import Path
import json,math,re

ROOT=Path(__file__).resolve().parents[2]
PARAMETERS=ROOT/'experiments/full_probability/f19-smoke2-full-sdk-latency.json'

def future_millis(node,parameters,depth=0):
    assert depth<=128,'latency policy exceeds bounded depth'
    if node.get('stop') is True:return 0.0
    action=node['action'];total=0.0
    for edge in node['children']:
        label=action+'/failed'
        estimate=parameters['outcomes'].get(label) if edge['kind']==0 and not edge['success'] else None
        if not estimate or not estimate['count']:estimate=parameters['actions'][action]
        median=float(estimate['median_ms']);assert math.isfinite(median) and median>0
        total+=edge['probability']*(median+future_millis(edge['node'],parameters,depth+1))
    return total

def verify_latency_evidence(text,decisions,catalogues,parameters=None):
    parameters=parameters or json.loads(PARAMETERS.read_text())
    ordinary={d for d,f in decisions.items() if f['scope']=='finite_catalogue_complete_candidates'}
    latencies={};physical={};trees=0;unexecuted=0
    for line in text.splitlines():
        kind='latency' if '[FullLatencyEvidence] ' in line else 'physical' if '[FullPhysicalEvaluation] ' in line else None
        if kind is None:continue
        f=dict(re.findall(r'(\w+)=([^\s]+)',line));d=int(f['decision']);assert d in ordinary
        if kind=='physical':
            assert d not in physical and f['scope']=='pure_physical_candidate_evaluation'
            assert f['canonical_answer_authority']=='false'
            inputs,retained=int(f['inputs']),int(f['retained'])
            assert 0<=retained<=inputs and (inputs==0 or retained>0)
            assert int(f['replay_support'])==int(decisions[d]['support'])
            physical[d]=f;continue
        assert d not in latencies and f['scope']=='descriptive_future_sdk_continuous_proxy'
        assert f['hard_bound']=='false' and f['past_time_constant']=='true' and float(f['rate_per_ms'])==.02
        keys=('predicted_sdk_ms','proxy_lower','proxy_upper','base_lower','base_upper')
        ms,lo,hi,base_lo,base_hi=[float(f[k]) for k in keys]
        assert all(math.isfinite(float(f[k])) for k in keys) and ms>=0 and base_lo<=base_hi+1e-7
        assert abs(base_lo-float(decisions[d]['selected_lower']))<2e-7 and abs(base_hi-float(decisions[d]['selected_upper']))<2e-7
        assert abs(lo-(base_lo-.02*ms))<2e-7 and abs(hi-(base_hi-.02*ms))<2e-7
        if decisions[d]['selected_stop']=='true':assert ms==0
        elif d in catalogues:
            assert abs(ms-future_millis(catalogues[d]['root'],parameters))<1e-6,'future SDK time does not match whole selected feedback tree'
            trees+=1
        else:unexecuted+=1 # Deadline may prevent sending a selected candidate.
        latencies[d]=f
    if 'latency_scope=f19_actual_repeat0_sdk_median_proxy' in text:assert set(latencies)==ordinary,'missing latency decisions'
    if 'physical_eval_scope=ledger_exact_view' in text or physical:assert set(physical)==ordinary,'missing physical evaluation decisions'
    return dict(latency_decisions=len(latencies),latency_trees=trees,unexecuted_selected=unexecuted,physical_views=len(physical),
        physical_input_worlds=sum(int(f['inputs']) for f in physical.values()),physical_retained_worlds=sum(int(f['retained']) for f in physical.values()))
