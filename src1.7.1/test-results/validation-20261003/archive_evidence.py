#!/usr/bin/env python3
"""Archive every run's evidence; retain originals and one shared SDK executable."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args(); files=[]; binaries=[]; sdk=[]
    for f in sorted(a.root.rglob('*')):
        if not f.is_file():continue
        if f.name=='iclingo':sdk.append(f);continue
        if f.name=='example':binaries.append(f);continue
        files.append(f)
    common=sha(sdk[0]) if sdk else None
    assert all(sha(f)==common for f in sdk),'different SDK runtime binary'
    with zipfile.ZipFile(a.output,'x',compression=zipfile.ZIP_DEFLATED) as z:
        for f in files+binaries:z.write(f,f.relative_to(a.root).as_posix())
        if sdk:z.write(sdk[0],'sdk-common/iclingo')
        z.writestr('archive-manifest.json',json.dumps({'root':str(a.root),'files':len(files),
            'product_binaries':{f.relative_to(a.root).as_posix():sha(f) for f in binaries},
            'sdk_runtime_copies':len(sdk),'sdk_runtime_sha256':common,
            'policy':'All logs, summaries, XML inputs, ASP states/results, build metadata, seed and product binaries retained. Identical SDK iclingo copies represented once. No originals deleted.'},indent=2))
    print('ARCHIVED',a.output,a.output.stat().st_size,'bytes')

if __name__=='__main__':main()
