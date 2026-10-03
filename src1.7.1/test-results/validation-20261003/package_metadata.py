#!/usr/bin/env python3
"""Copy inspectable metadata and verify archives without deleting originals."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

def main():
    p=argparse.ArgumentParser()
    p.add_argument('source',type=Path)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--archives',type=Path,nargs='*',default=[])
    a=p.parse_args()
    a.output.mkdir(exist_ok=False)
    copied=[]
    for f in sorted(a.source.rglob('*')):
        if not f.is_file():continue
        rel=f.relative_to(a.source)
        if rel.parts[0]=='runs':continue
        if f.name not in ('build.log','build.json','audit.json','final-audit.json',
            'input-audit.json','results.json','summary.json','manifest.json'):continue
        target=a.output/rel
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(str(f),str(target))
        copied.append({'path':rel.as_posix(),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
    archives=[]
    for zpath in a.archives:
        with zipfile.ZipFile(str(zpath)) as z:
            assert z.testzip() is None,'corrupt archive '+str(zpath)
            count=len(z.namelist())
        archives.append({'path':str(zpath),'bytes':zpath.stat().st_size,'entries':count,
            'sha256':hashlib.sha256(zpath.read_bytes()).hexdigest(),'crc_verified':True})
    (a.output/'delivery-manifest.json').write_text(json.dumps({'original_root':str(a.source),
        'metadata':copied,'archives':archives,'policy':'All originals retained; no file deletion.'},
        ensure_ascii=False,indent=2),encoding='utf-8')
    print('PACKAGED',len(copied),'metadata files;',len(archives),'verified archives')

if __name__=='__main__':main()
