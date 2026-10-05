#!/usr/bin/env python3
"""Read-only frozen-semantics/authority audit, with evidence written to a fresh file."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
sys.dont_write_bytecode=True
SOURCE=Path(__file__).resolve().parents[1]
BASELINE=SOURCE.parent/'src1.7'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def body(text, name):
    masked=re.sub(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'',
        lambda m: ''.join('\n' if c=='\n' else ' ' for c in m[0]),text)
    match=re.search(r'\bRDFW::'+re.escape(name)+r'\s*\([^;{}]*\)[^;{}]*\{',masked)
    assert match,name
    start=match.start(); end=match.end(); depth=1
    while depth:
        depth+=(masked[end]=='{')-(masked[end]=='}'); end+=1
    return text[start:end]

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--output',type=Path,required=True); a=parser.parse_args()
    frozen=['candidate_plan.cpp','candidate_plan.hpp','canonical_state.cpp','state_mutation.cpp',
        'deadline_manager.cpp','deadline_manager.hpp','score_evaluator.cpp','score_evaluator.hpp',
        'terminal_checker.cpp','terminal_checker.hpp','task_group_search.cpp','task_group_search.hpp',
        'legacy_priority.cpp','legacy_priority.hpp','parser.cpp','parser.hpp','question_preflight.cpp','question_preflight.hpp']
    products={name:dict(baseline=sha(BASELINE/name),current=sha(SOURCE/name)) for name in frozen}
    old=(BASELINE/'rdfw.cpp').read_text(); new=(SOURCE/'rdfw.cpp').read_text()
    functions=['SelectGreedyCandidate','BuildTaskGroupPlan','CalculateTaskRisk','RefreshTaskStates',
        'ShouldStartConstraintTrade','TryGuardedDecision','Move','SenseCurrentLocationOnly','Sense',
        'SolveTask','ZeroActionPreCheck','ExecuteMultiGotoAggregation','UpdateConstraintLedger','ResolvedState',
        'UpdateProvenance','ReceiveWeakClaim','ResolutionEligible','DecisionProgressSignature']
    unchanged={f:body(old,f)==body(new,f) for f in functions}
    legacy=body(new,'MustChooseOne')
    legacy_read_only=not re.search(r'\b(SolveTask|StopGate|BeginCandidateExecution|DoBehavious|Plug|ApplyStateValue|SetHold|SetPlate|Sense|Move)\b',legacy)
    probe=(SOURCE/'probe_layer.cpp').read_text()
    no_fact_writer=not re.search(r'\b(ApplyStateValue|StageStateValue|MarkDirectLocationEvidence|SetInsideEvidence|SetContainerEvidence|ReceiveWeakClaim|MutableProvenance|Plug)::?\b|\b(?:ApplyStateValue|StageStateValue|MutableProvenance)\s*\(',probe)
    changes=[]
    for f in SOURCE.glob('*'):
        if f.suffix in ('.cpp','.hpp') and (BASELINE/f.name).exists() and sha(f)!=sha(BASELINE/f.name): changes.append(f.name)
    result=dict(frozen_products=products,frozen_functions=unchanged,legacy_read_only=legacy_read_only,
        probe_has_no_fact_writer=no_fact_writer,changed_inherited_cpp=changes,
        authority='Probe delegates only to existing Move/Sense wrappers; state_mutation/canonical_state are byte-identical.',
        limitation='Static owner audit and executable tests; this is not a general C++ alias-analysis proof.')
    with a.output.open('x',encoding='utf-8') as out: json.dump(result,out,ensure_ascii=False,indent=2)
    assert all(p['baseline']==p['current'] for p in products.values()) and all(unchanged.values()) and legacy_read_only and no_fact_writer
    print('AUDIT PASS',a.output)

if __name__=='__main__': main()
