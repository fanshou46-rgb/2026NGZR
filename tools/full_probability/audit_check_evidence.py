"""Independently audit real SDK CTest fixture logs, including failed checkpoints."""
from pathlib import Path
import argparse,hashlib,json,re
from latency_evidence import verify_latency_evidence
from model_time_evidence import verify_model_time_evidence
from verify_receipts import ANSI,verify_coverage_schedule,verify_policy_interruptions
ROOT=Path(__file__).resolve().parents[2];LAB=ROOT/'experiments/full_probability'

def main():
    parser=argparse.ArgumentParser();parser.add_argument('checkpoint');args=parser.parse_args();cp=args.checkpoint
    assert cp.replace('_','').isalnum()
    log=LAB/'checks'/cp/'Testing/Temporary/LastTest.log';raw=log.read_bytes();rows=[]
    requires_model_ledger=b'[FullModelTimeSpan]' in (LAB/'builds'/cp/'source/full_controller.cpp').read_bytes()
    for section in re.split(r'\n\d+/\d+ Testing: ',ANSI.sub('',raw.decode('utf8',errors='replace')))[1:]:
        if not any(k in section for k in ('[FullPhysicalEvaluation]','[FullCoverageSchedule]','[FullCoverageRefutation]','[FullPolicyInterruption]')):continue
        decisions={};catalogues={};receipts=[]
        for line in section.splitlines():
            if '[FullDecisionEvidence] ' in line:
                f=dict(re.findall(r'(\w+)=([^\s]+)',line));d=int(f['decision']);assert d not in decisions;decisions[d]=f
            if '[FullPolicyCatalogue] {' in line:
                c=json.loads(line.split('[FullPolicyCatalogue] ',1)[1]);assert c['decision'] not in catalogues;catalogues[c['decision']]=c
            if '[ExecutionEvidence] {' in line:
                r=json.loads(line.split('[ExecutionEvidence] ',1)[1])
                if r['event']=='finalized':receipts.append(r)
        timed=verify_latency_evidence(section,decisions,catalogues)
        scheduled=verify_coverage_schedule(section,decisions,receipts)
        interruptions=verify_policy_interruptions(section,receipts)
        clock=verify_model_time_evidence(section,receipts,requires_model_ledger)
        rows.append(dict(test=section.splitlines()[0],time=timed,model_time=clock,coverage_markers=len(scheduled),interruptions=len(interruptions),receipts=len(receipts)))
    assert rows,'No SDK fixture evidence found'
    target=LAB/(cp+'-check-evidence.json');assert not target.exists(),'Prior evidence is immutable'
    value=dict(checkpoint=cp,all_build_checks_passed=(LAB/'builds'/cp/'checks-passed.json').exists(),
        log_sha256=hashlib.sha256(raw).hexdigest(),fixtures=rows,
        scope='SDK CTest raw receipts, coverage proofs, selected-tree future-time arithmetic and physical metadata only; full matrices/repeats and prior calibration are separate')
    target.write_text(json.dumps(value,indent=2)+'\n')
    print(json.dumps(dict(checkpoint=cp,fixtures=len(rows),all_build_checks_passed=value['all_build_checks_passed'],
        future_time_trees=sum(r['time']['latency_trees'] for r in rows),coverage_markers=sum(r['coverage_markers'] for r in rows),interruptions=sum(r['interruptions'] for r in rows))))
if __name__=='__main__':main()
