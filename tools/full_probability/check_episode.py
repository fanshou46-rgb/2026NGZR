"""Standalone real SDK verification of the next episode kernel, before integration."""
from pathlib import Path
import subprocess,json,hashlib
ROOT=Path(__file__).resolve().parents[2];LAB=ROOT/'experiments/full_probability';SDK=Path('/tmp/env-release-2026-search')
OUT=LAB/'checks/episode-kernel';OUT.mkdir(parents=True,exist_ok=True)
def run(command,log,cwd=None):
    with (OUT/log).open('w') as f:subprocess.run([str(v) for v in command],cwd=cwd,stdout=f,stderr=subprocess.STDOUT,check=True)
def main():
    src=LAB/'source';draft=LAB/'next'
    common=[draft/'sdk_episode.cpp',src/'joint_world.cpp',src/'observation_model.cpp']
    files=common+[draft/'sdk_episode.hpp',draft/'sdk_episode_tests.cpp',draft/'official_sdk_episode_tests.cpp']
    hashes={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    run(['g++','-std=c++11','-O2','-Wall','-I'+str(src),draft/'sdk_episode_tests.cpp']+common+['-o',OUT/'unit'],'unit-build.log')
    run([OUT/'unit'],'unit.log')
    run(['g++','-std=c++11','-O2','-Wall','-I'+str(src),'-I'+str(SDK/'src'),'-I'+str(SDK/'include'),draft/'official_sdk_episode_tests.cpp']+common+[SDK/'lib/libasp.so','-Wl,-rpath,'+str(SDK/'lib'),'-o',OUT/'official'],'official-build.log')
    work=OUT/'runtime';work.mkdir(exist_ok=True)
    import shutil
    for p in list((SDK/'res').glob('*.lp'))+[SDK/'res/iclingo',SDK/'bin/vrunact.sh',SDK/'bin/vruntask.sh']:
        q=work/p.name;shutil.copy2(str(p),str(q));q.chmod(q.stat().st_mode|0o111)
    for case in range(8):run([OUT/'official',str(case)],'official-'+str(case)+'.log',str(work))
    assert hashes=={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    result=dict(unit=True,official_cases=8,sources=hashes,scope='finite episode scoring and observation policy; not yet production prior or controller')
    (OUT/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');print('EPISODE KERNEL AND 8 REAL SDK CASES PASS',flush=True)
if __name__=='__main__':main()
