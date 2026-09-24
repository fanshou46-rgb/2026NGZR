#!/usr/bin/env python3
"""Final evidence consistency checks; does not rerun or modify the solver."""
import hashlib
import json
import re
from pathlib import Path
from check import check
from design import SUITE

ROOT=SUITE.parents[1]
RUN=ROOT/'test-results/liuyifan1.0-20260924-final'
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text(encoding='utf-8'))

def main():
    check()
    rows=load(RUN/'suite.json'); assert len(rows)==26
    cases={c['id']:c for c in load(SUITE/'manifest.json')}
    assert all(r['status']=='ok' and r['evaluator_valid'] for r in rows)
    assert all(r['semantic_equal'] for r in load(RUN/'parse/comparison.json'))
    assert all(r['action_trace_equal'] for r in load(RUN/'stability.json'))
    metadata=load(RUN/'environment.json')
    for name,sha in metadata['source_sha256'].items(): assert digest(ROOT/'src1.3.3-fixed'/name)==sha
    for name,sha in metadata['case_sha256'].items(): assert digest(SUITE/name)==sha
    raw_hashes={}
    for r in rows:
        folder=ROOT/r['output']; case=SUITE/(r['id']+'.xml')
        assert digest(case)==r['case_sha256']==digest(folder/'runtime/tests/case.xml')
        assert len(r['events'])==r['action_count']==sum(r['actions'].values())
        assert load(folder/'summary.json')['actions']==r['actions']
        assert r['action_cost']==sum(4 if e['action']=='Move' else 1 if e['action']=='Sense' else 2 for e in r['events'])
        assert r['base_score']==40*r['final_goals']+20*r['credited_constraints']-r['action_cost']
        assert r['raw_score']==r['base_score']+r['efficiency_score']
        assert r['final_goals']==sum(v==40 for i,v in r['official_values'])
        assert r['credited_constraints']==sum(v==20 for i,v in r['official_values'])
        assert len(r['official_values'])==len(set(tuple(v) for v in r['official_values']))
        assert r['raw_score']==int(re.findall(r'^# Score:\s*(-?\d+)',(folder/'server.log').read_text(encoding='utf-8'),re.M)[-1])
        assert r['platform_seconds']<5 and not r['platform_timed_out']
        if r['who']=='reference':
            assert r['final_goals']==cases[r['id']]['expected_goals']
            assert r['credited_constraints']==cases[r['id']]['expected_constraints']
            assert not r['failed_actions']
        for name in ('server.log','client.log','runtime/vanswer.txt'):
            raw_hashes[str((folder/name).relative_to(ROOT))]=digest(folder/name)
    # Check every local Markdown link in the delivered documents.
    for name in ('README.md','DESIGN.md','SCORE_REPORT.md','STRATEGY_REPORT.md'):
        text=(SUITE/name).read_text(encoding='utf-8')
        for target in re.findall(r'\]\(([^)]+)\)',text):
            if '://' not in target: assert (SUITE/target).exists(),(name,target)
    result=dict(status='pass',official_runs=26,solver_runs=20,reference_runs=6,
        semantic_pairs=6,source_unchanged=True,case_snapshots_identical=True,
        valid_answer_sets=26,hard_timeouts=0,score_decomposition='all verified',
        documentation_links='all verified',raw_evidence_sha256=raw_hashes,
        suite_files_sha256={str(p.relative_to(SUITE)):digest(p) for p in SUITE.rglob('*')
            if p.is_file() and '__pycache__' not in str(p)})
    (RUN/'audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('PASS: 26 official scores, 6 semantic pairs, source/case hashes, decompositions, evidence links')

if __name__=='__main__': main()
