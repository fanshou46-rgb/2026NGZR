#!/usr/bin/env python3
import hashlib,json,shutil,zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
RAW=Path('/tmp/rdfw-direct-167200-171-20261003')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    audit=json.loads((RAW/'input-audit.json').read_text())
    counts={}
    for arm,dirname in [('baseline','src1.6.7-200ms'),('current','src1.7.1')]:
        for rel,digest in audit['products'][arm].items():assert sha(ROOT/dirname/rel)==digest,rel
        counts[arm]=len(audit['products'][arm])
    for case in audit['cases']:assert sha(Path(case['path']))==case['sha256']
    metadata=HERE/'raw-metadata';metadata.mkdir(exist_ok=False)
    for name in ('input-audit.json','final-audit.json','results.json','summary.json','regressions.json','stage1-differences.json'):
        shutil.copyfile(str(RAW/name),str(metadata/name))
    for arm in ('baseline','current'):
        dest=metadata/('build-'+arm);dest.mkdir()
        for name in ('build.json','build.log'):shutil.copyfile(str(RAW/('build-'+arm)/name),str(dest/name))
    shutil.copyfile('/tmp/rdfw-direct-167200-171-progress.log',str(HERE/'direct-run.log'))
    with zipfile.ZipFile(str(HERE/'raw-evidence.zip')) as z:
        assert z.testzip() is None
        entries=len(z.namelist());assert len([n for n in z.namelist() if n.endswith('/server.log')])==568
        archived_final=json.loads(z.read('final-audit.json'));assert archived_final==json.loads((RAW/'final-audit.json').read_text())
    payload=dict(pairs=284,runs=568,seed=20260924,rounds=2,modes=['it','nt'],deadline_ms=5000,products_still_unchanged=True,inputs_still_unchanged=True,
        frozen_file_counts=counts,archive=dict(path='raw-evidence.zip',sha256=sha(HERE/'raw-evidence.zip'),bytes=(HERE/'raw-evidence.zip').stat().st_size,entries=entries,crc_verified=True),
        deliverables={p.relative_to(HERE).as_posix():sha(p) for p in sorted((HERE/'analysis').rglob('*')) if p.is_file()},
        scripts={p.name:sha(p) for p in sorted(HERE.glob('*.py'))},metadata={p.relative_to(HERE).as_posix():sha(p) for p in sorted(metadata.rglob('*')) if p.is_file()},
        policy='All direct runs retained; no original or product files deleted or modified. Analysis files only.')
    with (HERE/'delivery-manifest.json').open('x',encoding='utf-8') as f:json.dump(payload,f,ensure_ascii=False,indent=2)
    print(json.dumps({k:v for k,v in payload.items() if k not in ('deliverables','metadata','scripts')},indent=2))
if __name__=='__main__':main()
