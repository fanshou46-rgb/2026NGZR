#!/usr/bin/env python3
"""Real SDK sanitizer smoke, run after paired timing validation."""
import argparse
import hashlib
import importlib.util
import json
import os
import shlex
from pathlib import Path
import subprocess
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'src1.7.1'
SDK=Path('/home/yifan/env-release-2026')

def save(p,data):p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')

def main():
    p=argparse.ArgumentParser();p.add_argument('--comparison',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(exist_ok=False)
    exe=a.output/'example'
    command=['g++','-std=c++11','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie',
        '-I'+str(SOURCE),'-I'+str(SDK/'include'),'-I'+str(SDK/'src')]
    command += [str(f) for f in sorted(SOURCE.glob('*.cpp'))]
    command += ['-L'+str(SDK/'lib'),'-lframe','-lutility','-lboost_thread','-lboost_system','-lboost_chrono',
        '-lboost_date_time','-lboost_regex','-lpthread','-ldl','-o',str(exe)]
    with (a.output/'build.log').open('w') as out:subprocess.run(command,stdout=out,stderr=subprocess.STDOUT,check=True)
    asan=subprocess.check_output(['g++','-print-file-name=libasan.so']).decode().strip()
    seed=a.comparison/'seed.so'
    os.environ.update(LD_PRELOAD=str(seed),RDFW_TEST_SEED='20260924',RDFW_STAGE_TIMING='0')
    launcher=a.output/'sanitized-client.sh'
    launcher.write_text('#!/bin/bash\nexport LD_PRELOAD='+shlex.quote(asan+':'+str(seed))+
        '\nexport ASAN_OPTIONS=detect_leaks=1\nexport UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1\nexec '+
        shlex.quote(str(exe))+' "$@"\n')
    launcher.chmod(0o755)
    os.environ.pop('RDFW_TASK_GROUP_MODE',None)
    spec=importlib.util.spec_from_file_location('runner',str(ROOT/'HistoryVersion/src1.1.2 (x)/tools/baseline.py'))
    runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
    cases=json.loads((a.comparison/'input-audit.json').read_text())['cases']
    selected=[c for c in cases if c['id'] in ('c032','c069','c070','A01-01-s1')]
    assert len(selected)==4
    save(a.output/'build.json',{'command':command,'binary_sha256':hashlib.sha256(exe.read_bytes()).hexdigest(),
        'asan_library':asan,'seed':str(seed),'cases':selected,'policy':'Client instrumented; SDK libraries are prebuilt. Not a performance comparison.'})
    rows=[]
    for case in selected:
        for mode in ('it','nt'):
            run=a.output/'runs'/(case['id']+'-'+mode)
            value=runner.run_case(SDK,a.comparison/'assets',launcher,Path(case['path']),case['stage'],mode,run,5000,None)
            text=(run/'client.log').read_text(errors='replace')
            value.update(id=case['id'],sanitizer_error=any(s in text for s in
                ('ERROR: AddressSanitizer','runtime error:','LeakSanitizer')),probes=sum('"event":"feedback"' in line for line in text.splitlines()),
                seed_confirmed='[RDFW_TEST_SEED] 20260924' in (run/'server.log').read_text(errors='replace'))
            rows.append(value);save(a.output/'results.json',rows)
            print(case['id'],mode,value['status'],'probes',value['probes'],'sanitizer',value['sanitizer_error'],flush=True)
    save(a.output/'audit.json',{'runs':len(rows),'errors':[r['id']+'/'+r['mode'] for r in rows if
        r['sanitizer_error'] or r['client_exit']!=0 or not r['seed_confirmed'] or r['status']!='ok'],
        'stage1_probes':sum(r['probes'] for r in rows if r['stage']==1),'stage2_probes':sum(r['probes'] for r in rows if r['stage']==2)})
    assert all(not r['sanitizer_error'] and r['client_exit']==0 and r['seed_confirmed'] and r['status']=='ok' for r in rows)

if __name__=='__main__':main()
