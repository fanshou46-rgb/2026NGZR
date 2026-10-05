"""Retained real SDK counterexamples against the immutable pre-fix checkpoint."""
from pathlib import Path
import hashlib, json, shutil, subprocess
ROOT=Path(__file__).resolve().parents[2]
LAB=ROOT/'experiments/full_probability'
SDK=Path('/tmp/env-release-2026-search')
out=LAB/'checks/door-failure-before-v2'
assert not out.exists(), 'Previous evidence is retained; use a new directory'
out.mkdir()
src=LAB/'builds/a02/source'
fixture=LAB/'next/door_failure_sdk_probe.cpp'
exe=out/'probe'
args=['g++','-std=c++11','-O2','-UNDEBUG','-I'+str(src/'tests/stubs'),'-I'+str(src),'-I'+str(SDK/'src'),'-I'+str(SDK/'include'),str(fixture),str(LAB/'checks/a02/librdfw_test_core.a'),str(SDK/'lib/libasp.so'),'-pthread','-Wl,-rpath,'+str(SDK/'lib'),'-o',str(exe)]
with (out/'compile.log').open('w') as log:subprocess.run(args,stdout=log,stderr=subprocess.STDOUT,check=True)
runtime=out/'runtime';runtime.mkdir()
for file in list((SDK/'res').glob('*.lp'))+[SDK/'res/iclingo',SDK/'bin/vrunact.sh',SDK/'bin/vruntask.sh']:
    shutil.copy2(str(file),str(runtime/file.name))
    if file.name in ['iclingo','vrunact.sh','vruntask.sh']:(runtime/file.name).chmod(0o755)
for test in [0,3]:
    with (out/('case-'+str(test)+'.log')).open('w') as log:
        subprocess.run([str(exe),str(LAB/'checks/a02/words.txt'),str(test),'before'],stdout=log,stderr=subprocess.STDOUT,cwd=str(runtime),check=True)
receipt=dict(scope='two real SDK counterexamples, immutable a02 planner and unit gateway',
    fixture_sha256=hashlib.sha256(fixture.read_bytes()).hexdigest(),
    binary_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),
    core_sha256=hashlib.sha256((LAB/'checks/a02/librdfw_test_core.a').read_bytes()).hexdigest())
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('REAL SDK BEFORE-FIX COUNTEREXAMPLES VERIFIED',flush=True)
