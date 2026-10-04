#!/usr/bin/env python3
"""Copy inspectable evidence; retain every run while deduplicating SDK iclingo."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def package(source,destination):
    assert not (destination/'results.json').exists(), 'Never overwrite an evidence run'
    destination.mkdir(parents=True,exist_ok=True)
    for path in source.iterdir():
        if path.is_file() and path.suffix in ('.json','.csv','.md'):
            shutil.copy2(str(path),str(destination/path.name))
    for arm in ('baseline','current'):
        target=destination/('build-'+arm); target.mkdir()
        for name in ('build.log','build.json'):
            shutil.copy2(str(source/('build-'+arm)/name),str(target/name))
    with zipfile.ZipFile(str(destination/'binaries.zip'),'w',zipfile.ZIP_DEFLATED) as z:
        for arm in ('baseline','current'):
            z.write(str(source/('build-'+arm)/'example'),arm+'/example')
    shared=next((source/'runs').glob('*/runtime/iclingo')); digest=sha(shared)
    logs=0; files=0
    with zipfile.ZipFile(str(destination/'raw-evidence.zip'),'w',zipfile.ZIP_DEFLATED) as z:
        z.write(str(shared),'shared-sdk/iclingo')
        for path in sorted((source/'runs').rglob('*')):
            if not path.is_file(): continue
            if path.name=='iclingo': assert sha(path)==digest,path
            else:
                z.write(str(path),str(path.relative_to(source))); files+=1
                if path.name=='client.log': logs+=1
        z.writestr('shared-sdk/manifest.json',json.dumps(dict(iclingo_sha256=digest,
            runs=logs,files=files,policy='Identical SDK iclingo stored once; all run logs, inputs and ASP outputs retained.'),indent=2))
    assert logs==len(json.loads((source/'results.json').read_text()))*2
    (destination/'package-sha256.json').write_text(json.dumps(
        {p.relative_to(destination).as_posix():sha(p) for p in destination.rglob('*') if p.is_file()},indent=2))

def main():
    p=argparse.ArgumentParser(); p.add_argument('source',type=Path); p.add_argument('destination',type=Path)
    a=p.parse_args();package(a.source,a.destination)

if __name__=='__main__': main()
