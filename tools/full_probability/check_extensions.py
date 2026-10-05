"""Verify replay/route extensions without changing the frozen SDK checkpoint."""
from pathlib import Path
import subprocess,json,hashlib
ROOT=Path(__file__).resolve().parents[2];LAB=ROOT/'experiments/full_probability'
out=LAB/'checks/episode-extensions-03'
assert not out.exists(),'Do not replace earlier evidence'
out.mkdir()
source=LAB/'source';draft=LAB/'next'
shared=[draft/'sdk_episode.cpp',source/'joint_world.cpp',source/'observation_model.cpp']+[draft/('episode_'+name+'.cpp') for name in ['replay','routes','prior','router']]
files=shared+[draft/'sdk_episode.hpp']+[draft/('episode_'+name+suffix) for name in ['replay','routes','prior','router'] for suffix in ['.hpp','_tests.cpp']]
hashes={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
for name in ['replay','routes','prior','router']:
    exe=out/name
    args=['g++','-std=c++11','-O2','-Wall','-I'+str(source),str(draft/('episode_'+name+'_tests.cpp'))]+[str(p) for p in shared]+['-o',str(exe)]
    with (out/(name+'-compile.log')).open('w') as f:subprocess.run(args,stdout=f,stderr=subprocess.STDOUT,check=True)
    with (out/(name+'.log')).open('w') as f:subprocess.run([str(exe)],stdout=f,stderr=subprocess.STDOUT,check=True)
assert hashes=={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
(out/'receipt.json').write_text(json.dumps(dict(sources=hashes,replay=True,routes=True,prior=True,router=True,scope='bounded finite-model kernels, production prior mapping/controller not connected'),indent=2)+'\n')
print('REPLAY, ROUTE, PRIOR AND ROUTER EXTENSIONS PASS',flush=True)
