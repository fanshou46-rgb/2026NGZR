"""Freeze checkpoint source, binary, failed checks and every raw run; verify ZIP bytes."""
from pathlib import Path
import argparse,hashlib,json,zipfile

ROOT=Path(__file__).resolve().parents[2];LAB=ROOT/'experiments/full_probability'
def sha(data):return hashlib.sha256(data).hexdigest()

def main():
    parser=argparse.ArgumentParser();parser.add_argument('checkpoint');parser.add_argument('--auxiliary',action='store_true');parser.add_argument('--checks-only',action='store_true');args=parser.parse_args()
    cp=args.checkpoint
    assert cp.replace('_','').replace('-','').isalnum()
    output=LAB/'evidence';output.mkdir(exist_ok=True)
    tag=cp+'-checks' if args.checks_only else cp
    target=output/(tag+'.zip');assert not target.exists(),'Existing evidence is immutable'
    files=set()
    build=LAB/'builds'/cp
    if build.exists():files.update(p for p in build.rglob('*') if p.is_file())
    if not args.checks_only:
        files.update(p for p in LAB.glob(cp+'-*') if p.is_file())
        for folder in (LAB/'runs').glob(cp+'-*'):
            files.update(p for p in folder.rglob('*') if p.is_file())
    for folder in (LAB/'checks').glob(cp+'*'):
        if folder.is_file():files.add(folder)
        else:files.update(p for p in folder.rglob('*') if p.is_file() and (
            p.suffix in ('.log','.json','.txt') and 'CMakeFiles' not in p.parts or p.name=='receipt.json'))
    files.update((LAB/'source-receipt.json',LAB/'EXECUTION_PLAN.md',LAB/'WORK_LOG.md'))
    files.update(p for p in LAB.glob('prior-development-*.json') if p.is_file())
    if args.auxiliary:
        files.update(p for p in (LAB/'next').rglob('*') if p.is_file())
        for folder in (LAB/'checks').iterdir():
            if folder.is_dir() and folder.name.startswith(('episode-','door-failure-')):
                files.update(p for p in folder.rglob('*') if p.is_file() and p.suffix in ('.log','.json','.cpp','.hpp','.txt'))
    else:assert files and any(p.parent==build for p in files),'No checkpoint build receipt'
    manifest=[]
    with zipfile.ZipFile(str(target),'w',zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(files):
            data=path.read_bytes();name=path.relative_to(ROOT).as_posix()
            manifest.append(dict(path=name,bytes=len(data),sha256=sha(data)))
            archive.writestr(name,data)
    with zipfile.ZipFile(str(target)) as archive:
        assert archive.testzip() is None,'CRC verification failed'
        assert set(archive.namelist())=={row['path'] for row in manifest}
        for row in manifest:assert sha(archive.read(row['path']))==row['sha256']
    receipt=dict(checkpoint=cp,checks_only=args.checks_only,archive=target.name,sha256=sha(target.read_bytes()),files=manifest,
        scope='immutable development checkpoint, source and executable plus all raw runs and failed check logs; excluded test object files and SDK binaries are not robot scoring evidence',
        postprocessing_tools={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in sorted((ROOT/'tools/full_probability').glob('*.py'))})
    (output/(tag+'-manifest.json')).write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(checkpoint=cp,files=len(files),bytes=target.stat().st_size,sha256=receipt['sha256'])))
if __name__=='__main__':main()
