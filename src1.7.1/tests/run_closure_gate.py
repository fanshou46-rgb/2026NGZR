#!/usr/bin/env python3
"""Unified State Model Closure gate. Fresh output, serial official server runs.
No deletion. Fail closed on local validation, identity audit or invalid replay.
Behavior differences are preserved for explicit classification, never rerun away.
"""
import argparse, hashlib, json, os, re, subprocess, sys, time, zipfile
from pathlib import Path
sys.dont_write_bytecode=True
SOURCE=Path(__file__).resolve().parents[1];ROOT=SOURCE.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--baseline',type=Path,required=True)
    parser.add_argument('--seed-library',type=Path,required=True)
    parser.add_argument('--sdk',type=Path,default=Path('/home/yifan/env-release-2026'))
    a=parser.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    commands=[]
    def run(name,cmd,env=None,expected=0):
        start=time.time()
        with (a.output/(name+'.log')).open('w') as log:
            p=subprocess.run([str(x) for x in cmd],stdout=log,stderr=subprocess.STDOUT,env=env)
        commands.append(dict(name=name,command=[str(x) for x in cmd],code=p.returncode,seconds=time.time()-start))
        (a.output/'commands.json').write_text(json.dumps(commands,indent=2))
        assert p.returncode==expected,(name,p.returncode)
    base=ROOT/'src1.6.6'
    validated=json.loads((base/'test-results/validation-20260928/build.json').read_text())
    assert sha(a.baseline)==validated['executable_sha256']
    assert all(sha(base/k)==v for k,v in validated['source_sha256'].items())
    assert all(sha(a.sdk/k)==v for k,v in validated['sdk_sha256'].items())
    protected=json.loads((SOURCE/'docs/BASELINE_SHA256.json').read_text())
    snapshot=dict(source={p.name:sha(p) for p in SOURCE.iterdir() if p.is_file()},
        tests={p.relative_to(SOURCE).as_posix():sha(p) for p in (SOURCE/'tests').rglob('*') if p.is_file()},
        baseline_sha256=sha(a.baseline),seed_sha256=sha(a.seed_library),sdk=validated['sdk_sha256'],
        platform=subprocess.check_output(['uname','-a']).decode(),
        compiler=subprocess.check_output(['g++','--version']).decode(),
        policy=dict(deadline_ms=5000,seed=20260924,official_serial=True,profiling_separate=True))
    snapshot['sdk_all_files']={p.relative_to(a.sdk).as_posix():sha(p) for p in a.sdk.rglob('*') if p.is_file()}
    (a.output/'input-audit.json').write_text(json.dumps(snapshot,indent=2))
    unit=a.output/'unit';asan=a.output/'asan';before=a.output/'before'
    for path,configuration,extra in [(unit,'Release',['-DOFFICIAL_SDK='+str(a.sdk)]),
            (asan,'Debug',['-DCMAKE_CXX_FLAGS=-fsanitize=address,undefined -fno-omit-frame-pointer -fno-pie','-DCMAKE_EXE_LINKER_FLAGS=-fsanitize=address,undefined -no-pie']),
            (before,'Release',[])]:
        src=SOURCE/'tests/hardening_baseline_probe' if path==before else SOURCE/'tests'
        path.mkdir()
        # CMake 3.10 does not support -S/-B.
        run(path.name+'-config',['cmake','-H'+str(src),'-B'+str(path),'-DCMAKE_BUILD_TYPE='+configuration]+extra)
        run(path.name+'-build',['cmake','--build',path,'--','-j3'])
    for path in [unit,asan]:
        env=dict(os.environ);env.update(ASAN_OPTIONS='detect_leaks=1',UBSAN_OPTIONS='halt_on_error=1')
        run(path.name+'-ctest',['bash','-c','cd "$1" && ctest --output-on-failure','gate',path],env)
    probe_results=[]
    for case in range(4):
        cmd=[str(before/'mutation_failure_tests'),str(before/'words.txt'),str(case)]
        with (a.output/('before-probe-'+str(case)+'.log')).open('w') as log:
            p=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
        assert p.returncode!=0,('missing before regression',case)
        probe_results.append(dict(case=case,code=p.returncode,expected_failure=True))
    (a.output/'before-probes.json').write_text(json.dumps(probe_results,indent=2))
    for path in [before,unit]:run(path.name+'-deadline',[path/'deadline_sensitivity_tests',path/'words.txt'])
    metrics=[]
    for round_id in range(7):
        # Alternate AB/BA to expose drift; CPU measurements finish before server.
        for size in [8,64,192]:
            for label,path in ([('baseline',before),('current',unit)] if round_id%2==0 else [('current',unit),('baseline',before)]):
                name='profile-r{}-{}-{}'.format(round_id,size,label)
                run(name,[path/'state_profile',path/'words.txt',str(size)])
                for item in re.findall(r'PROFILE (\{[^\n]+\})',(a.output/(name+'.log')).read_text()):
                    row=json.loads(item);row.update(round=round_id,label=label);metrics.append(row)
    (a.output/'micro-profile.json').write_text(json.dumps(metrics,indent=2))
    for size in [8,64,192]:
        for phase in range(3):
            checks=[r['checksum'] for r in metrics if r['size']==size and r['phase']==phase]
            assert len(checks)==14 and len(set(checks))==1,(size,phase,'semantic checksum')
    release=a.output/'official'
    run('release-matrix',[sys.executable,SOURCE/'tests/run_release_matrix.py','--output',release,'--baseline',a.baseline,'--seed-library',a.seed_library])
    run('timing-controls',[sys.executable,SOURCE/'tests/run_timing_controls.py','--runs',release,'--baseline',a.baseline,'--current',release/'build-release/example','--seed-library',a.seed_library])
    assert all(sha(ROOT/p)==v for p,v in protected.items()),'baseline changed'
    assert all(sha(SOURCE/p)==v for p,v in snapshot['source'].items()),'source changed during gate'
    run('archive',[sys.executable,SOURCE/'tests/archive_closure_gate.py',a.output])
    print('Closure gate evidence:',a.output,flush=True)
if __name__=='__main__':main()
