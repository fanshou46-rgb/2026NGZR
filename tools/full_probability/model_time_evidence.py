"""Verify reported model intervals and receipt-stable segment accounting."""
import re
PHASES={'initialize','initial_forecast','candidate_selection','deferred_coverage','policy_catalogue','feedback_replay'}
def verify_model_time_evidence(text,receipts,required=False):
    spans=[]
    for line in text.splitlines():
        if '[FullModelTimeSpan] ' not in line:continue
        f=dict(re.findall(r'(\w+)=([^\s]+)',line));assert int(f['id'])==len(spans)+1
        assert f['phase'] in PHASES and f['scope']=='model_only_receipt_watermark_unchanged'
        start,end,duration,mark=[int(f[k]) for k in ('begin_ns','end_ns','duration_ns','receipt_mark')]
        assert duration==end-start and duration>=0 and 0<=mark<=len(receipts)
        if spans:assert start>=spans[-1]['end'] and mark>=spans[-1]['mark']
        spans.append(dict(phase=f['phase'],start=start,end=end,duration=duration,mark=mark))
    if required:assert spans,'missing required model-time ledger'
    if not spans:return dict(segments=0,ns=0)
    assert sum(s['phase']=='initialize' for s in spans)==1 and spans[0]['phase']=='initialize' and spans[0]['mark']==0
    assert sum(s['phase']=='initial_forecast' for s in spans)==1
    assert [s['mark'] for s in spans if s['phase']=='policy_catalogue']==list(range(len(receipts))),'missing or duplicate policy preparation interval'
    stops=re.findall(r'\[FullStopEvidence\].*?model_ns=(\d+)',text);assert len(stops)==1
    total=sum(s['duration'] for s in spans);assert total==int(stops[0]),'model total omitted or double charged a segment'
    reported=re.findall(r'\[FullModel\] stopped receipts=(\d+) model_ms=(\d+)',text);assert len(reported)==1
    assert int(reported[0][0])==len(receipts) and int(reported[0][1])==total//1000000
    return dict(segments=len(spans),ns=total)
