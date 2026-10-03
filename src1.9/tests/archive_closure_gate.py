"""Verify and archive complete closure evidence; no raw run is discarded."""
import collections,difflib,hashlib,json,re,shutil,statistics,subprocess,sys,zipfile
from pathlib import Path
sys.dont_write_bytecode=True
GATE=Path(sys.argv[1]);SOURCE=Path(__file__).resolve().parents[1];ROOT=SOURCE.parent
OUT=SOURCE/'test-results/validation-20260928';OUT.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,obj): (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2))
def load(p):return json.loads(p.read_text())
def main():
    initial=load(GATE/'input-audit.json');release=GATE/'official';build=load(release/'build-release/build.json')
    validated=load(ROOT/'src1.6.6/test-results/validation-20260928/build.json')
    current=Path(build['command'][build['command'].index('-o')+1])
    protected=load(SOURCE/'docs/BASELINE_SHA256.json')
    sdk=Path('/home/yifan/env-release-2026')
    audit=dict(source_matches_input=all(sha(SOURCE/p)==v for p,v in initial['source'].items()),
        source_matches_build=all(sha(SOURCE/p)==v for p,v in build['source_sha256'].items()),
        baseline_tree_unchanged=all(sha(ROOT/p)==v for p,v in protected.items()),
        baseline_matches_validated_release=initial['baseline_sha256']==validated['executable_sha256'],
        sdk_matches_baseline=initial['sdk']==validated['sdk_sha256']==build['sdk_sha256'],
        sdk_full_tree_unchanged=all(sha(sdk/p)==v for p,v in initial['sdk_all_files'].items()),
        current_binary_matches_build=sha(current)==build['executable_sha256'],
        words_lf=b'\r' not in (SOURCE/'words.txt').read_bytes())
    suites=['full-release','target-release-r1','target-release-r2','target-release-r3','off-release']
    summaries=[];all_rows=[]
    for suite in suites:
        rows=load(release/suite/'results.json');summary=load(release/suite/'summary.json');summaries.append(summary)
        all_rows.extend(dict(suite=suite,**row) for row in rows)
        shutil.copy2(str(release/suite/'results.json'),str(OUT/(suite+'-results.json')))
        shutil.copy2(str(release/suite/'summary.json'),str(OUT/(suite+'-summary.json')))
    controls=load(release/'timing-controls.json')
    audit['problem_hashes_valid']=all(sha(Path(row['case']))==row['case_sha256'] for row in all_rows+controls)
    audit['seed_confirmed']=all(row[label]['seed_confirmed'] for row in all_rows+controls for label in ['baseline','current'])
    audit['official_runs_valid']=all(row[label]['status']=='ok' and not row[label]['timed_out'] for row in all_rows+controls for label in ['baseline','current'])
    audit['action_cost_checks']=all(s['action_cost_mismatches']==0 and s['action_cost_checks']==2*s['pairs'] for s in summaries)
    audit['official_matrix_complete']=len(all_rows)==118
    audit['controls_complete']=len(controls)==36
    audit['controls_binaries_match']=all(sha(a)==v for a,v in [(Path('/tmp/rdfw-166-final/build-release/example'),initial['baseline_sha256']),(current,build['executable_sha256'])])
    subprocess.run([sys.executable,str(SOURCE/'tests/audit_mutation_closure.py')],check=True)
    audit['no_unclassified_writes']=not load(SOURCE/'docs/mutation-audit.json')['unclassified']
    def ctest(path):
        text=path.read_text();m=re.search(r'100% tests passed, 0 tests failed out of (\d+)',text);assert m,path
        return int(m[1])
    audit['ctest_passed']=ctest(GATE/'unit-ctest.log')==126
    audit['asan_ubsan_passed']=ctest(GATE/'asan-ctest.log')==125
    audit['before_probes_reproduced']=len(load(GATE/'before-probes.json'))==4 and all(r['code']!=0 for r in load(GATE/'before-probes.json'))
    write('audit.json',audit)
    assert all(audit.values()),audit
    combined={k:sum(s[k] for s in summaries) for k in ['pairs','identical_base','identical_actions','identical_goals','identical_constraints','official_score_differences','hard_timeouts','invalid','action_cost_checks','action_cost_mismatches']}
    write('summary.json',combined)
    # Quantization classification is exact. Behavior changes require reviewed
    # log evidence; never label them semantic/timing solely from a score delta.
    review_path=SOURCE/'docs/DIFFERENCE_REVIEW.json'
    reviewed=load(review_path) if review_path.exists() else {}
    differences=[]
    for row in all_rows:
        b,c=row['baseline'],row['current']
        behavior=any(b[k]!=c[k] for k in ['base','goals','constraints','action_sequence'])
        if not behavior and b['official']==c['official']:continue
        key='{}:{}:s{}:{}'.format(row['suite'],Path(row['case']).stem,row['stage'],row['mode'])
        bonus=[2*int((5-side['platform_seconds'])*10) for side in [b,c]]
        if not behavior:
            assert all(side['official']==side['base']+value for side,value in zip([b,c],bonus)),row
            explanation=dict(classification='score_quantization',evidence='Same base/goals/constraints/action sequence; exact SDK 2*int((5-platform_seconds)*10)',time_bonus=bonus)
        else:explanation=reviewed.get(key,dict(classification='REVIEW_REQUIRED',evidence='Inspect preserved first divergence, deadline gate, and same-binary controls'))
        differences.append(dict(key=key,behavior_changed=behavior,**explanation,**row))
    write('difference-classification.json',differences)
    control_diffs=[dict(classification='baseline_nondeterminism' if r['binary']=='baseline' else 'timing',**r) for r in controls if any(r['baseline'][k]!=r['current'][k] for k in ['base','goals','constraints','action_sequence'])]
    write('control-behavior-differences.json',control_diffs)
    metrics=load(GATE/'micro-profile.json');perf=[]
    for size in [8,64,192]:
        for phase in range(3):
            entry=dict(size=size,phase=['canonical_query','terminal','projection'][phase])
            for label in ['baseline','current']:
                selected=[r for r in metrics if r['size']==size and r['phase']==phase and r['label']==label]
                entry[label]=dict(median_ns=statistics.median(r['nanos']/r['calls'] for r in selected),
                    min_ns=min(r['nanos']/r['calls'] for r in selected),max_ns=max(r['nanos']/r['calls'] for r in selected),
                    allocations_per_call=statistics.median(r['allocations']/r['calls'] for r in selected))
            entry['after_before']=entry['current']['median_ns']/entry['baseline']['median_ns'];perf.append(entry)
    write('micro-performance-summary.json',perf)
    shutil.copy2(str(GATE/'micro-profile.json'),str(OUT/'micro-profile.json'))
    shutil.copy2(str(release/'perf-target/performance-summary.json'),str(OUT/'official-performance-summary.json'))
    # Same-binary timing distribution records all samples, not just matching pairs.
    distributions=[]
    for binary in ['baseline','current']:
        groups=collections.defaultdict(list)
        for row in controls:
            if row['binary']!=binary:continue
            for label in ['baseline','current']:groups[(row['case'],row['mode'])].append(row[label])
        for (case,mode),samples in groups.items():
            seconds=[s['platform_seconds'] for s in samples]
            distributions.append(dict(binary=binary,case=case,mode=mode,samples=len(samples),
                min_seconds=min(seconds),max_seconds=max(seconds),median_seconds=statistics.median(seconds),
                stdev_seconds=statistics.pstdev(seconds),base_values=sorted(set(s['base'] for s in samples))))
    write('timing-distribution.json',distributions)
    # Whole log trees, all metadata and answer sets. Shared SDK executable copies
    # are identified by hashes rather than redundantly embedding them per run.
    for label,tree in [('official',release),('local',GATE)]:
        with zipfile.ZipFile(str(OUT/(label+'-raw-evidence.zip')),'w',compression=zipfile.ZIP_DEFLATED) as z:
            for p in sorted(tree.rglob('*')):
                if not p.is_file():continue
                if label=='local' and release in p.parents:continue
                keep=(label=='official' and p.name not in ('iclingo','example')) or p.suffix in ('.log','.json') or p.name in ('CMakeCache.txt','vanswer.txt','LastTestsFailed.log','CTestTestfile.cmake')
                if keep:
                    z.write(str(p),p.relative_to(tree).as_posix())
    for p in GATE.glob('*.log'):shutil.copy2(str(p),str(OUT/p.name))
    for name in ['input-audit.json','commands.json','before-probes.json']:shutil.copy2(str(GATE/name),str(OUT/name))
    shutil.copy2(str(release/'timing-controls.json'),str(OUT/'timing-controls.json'))
    shutil.copy2(str(release/'build-release/build.json'),str(OUT/'build.json'))
    shutil.copy2(str(release/'build-release/build.log'),str(OUT/'official-build.log'))
    shutil.copy2(str(current),str(OUT/'example-1.6.7'))
    product=[p for p in SOURCE.iterdir() if p.suffix in ('.cpp','.hpp') or p.name in ('CMakeLists.txt','words.txt')]
    diff=[];changed=[]
    for p in sorted(product):
        old=ROOT/'src1.6.6'/p.name
        if old.exists() and sha(old)==sha(p):continue
        changed.append(p.name)
        diff.extend(difflib.unified_diff(old.read_text(encoding='utf-8-sig').splitlines(True) if old.exists() else [],p.read_text().splitlines(True),fromfile='src1.6.6/'+p.name,tofile='src1.6.7/'+p.name))
    (OUT/'source.diff').write_text(''.join(diff))
    unchanged_policy=['score_evaluator.cpp','score_evaluator.hpp','task_group_search.cpp','task_group_search.hpp','deadline_manager.cpp','deadline_manager.hpp','candidate_plan.cpp','candidate_plan.hpp','legacy_priority.cpp','legacy_priority.hpp','parser.cpp','parser.hpp','question_preflight.cpp','question_preflight.hpp']
    manifest=dict(baseline='src1.6.6',current='src1.6.7',changed_product_files=changed,
        preserved_policy_sha256={p:sha(SOURCE/p) for p in unchanged_policy},
        product_sha256={p.name:sha(p) for p in product},
        test_sha256={p.relative_to(SOURCE).as_posix():sha(p) for p in (SOURCE/'tests').rglob('*') if p.is_file()},
        ctest=126,asan_ubsan=125,before_expected_failures=4,official_pairs=118,profile_pairs=6,self_pairs=36,
        difference_review_complete=all(r['classification']!='REVIEW_REQUIRED' for r in differences))
    assert all(sha(SOURCE/p)==sha(ROOT/'src1.6.6'/p) for p in unchanged_policy)
    write('manifest.json',manifest)
    print(json.dumps(dict(audit=audit,summary=combined,difference_review_complete=manifest['difference_review_complete']),ensure_ascii=False))
    assert manifest['difference_review_complete'],'Behavior differences require preserved-log review before the release gate can pass'
if __name__=='__main__':main()
