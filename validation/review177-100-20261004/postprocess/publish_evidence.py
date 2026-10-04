"""Package every audit receipt after scoring; all archive entries are verified."""
from pathlib import Path
import json,hashlib,zipfile,zlib,shutil,subprocess
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parents[1]
BANK=ROOT/'题目/independent_100_20261004'
TARGET=35*1024*1024
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    audit=json.loads((OUT/'final-audit.json').read_text(encoding='utf8'));assert audit['runs']==6726
    frozen=json.loads((OUT/'frozen-audit.json').read_text(encoding='utf8'))
    publish=OUT/'evidence';publish.mkdir(exist_ok=True)
    assert not list(publish.glob('*.zip')),'Archives already exist; inspect rather than overwrite'
    manifest={'policy':'all raw run/preflight/equivalence receipts and failed author drafts retained; immutable vendor SDK omitted and hash-referenced. Compiled binaries and CMake object/cache files are local only; binary hashes/build recipes published.', 'archives':[],'frozen':frozen['source_commit'],'matrix_runs':audit['runs']}
    def pack(stem,files):
        files=sorted(set(files),key=lambda p:p.relative_to(ROOT).as_posix());number=0;z=None;entries=[];name=None
        def close():
            nonlocal z,entries
            if z is None:return
            z.writestr('CONTENTS.json',json.dumps(entries,ensure_ascii=False,indent=2)+'\n');z.close()
            with zipfile.ZipFile(name) as check:
                assert check.testzip() is None
                for e in entries:
                    data=check.read(e['path']);assert len(data)==e['bytes'] and sha(data)==e['sha256'] and check.getinfo(e['path']).CRC==e['crc32'],e['path']
            data=name.read_bytes();manifest['archives'].append(dict(path=name.relative_to(OUT).as_posix(),bytes=len(data),sha256=sha(data),payload_files=len(entries)))
            print(name.name,len(entries),len(data),flush=True);z=None;entries=[]
        for p in files:
            if z is None:
                number+=1;name=publish/(stem+'-%02d.zip'%number);z=zipfile.ZipFile(name,'x',zipfile.ZIP_DEFLATED,compresslevel=6)
            data=p.read_bytes();relative=p.relative_to(ROOT).as_posix();z.writestr(relative,data)
            entries.append(dict(path=relative,bytes=len(data),sha256=sha(data),crc32=zlib.crc32(data)&0xffffffff))
            if z.fp.tell()>=TARGET:close()
        close()
    runs=[p for p in (OUT/'runs').rglob('*') if p.is_file()]
    assert len(list((OUT/'runs').iterdir()))==6726
    pack('matrix-raw',runs+[OUT/'results.jsonl'])
    support=[]
    for folder in [OUT/'preflight',OUT/'checks']+list(OUT.glob('author-draft-*'))+[OUT/'builds']:
        for p in folder.rglob('*'):
            if p.is_file() and (p.suffix in ('.log','.json','.jsonl','.xml','.md','.py','.cpp','.h','.hpp','.txt','.plan','.zip') or p.name=='CMakeLists.txt') and not any(x in p.parts for x in ('CMakeFiles','__pycache__')):
                support.append(p)
    support += list((OUT/'postprocess').glob('*.log'))
    pack('reference-checks-drafts',support)
    snapshots=[ROOT/p for p in frozen['inputs']]+[ROOT/p for p in frozen['tools']]
    for key,core in frozen['original_sources'].items():
        folder={'167':ROOT/'HistoryVersion/src1.6.7','167_200':ROOT/'src1.6.7-200ms','177':ROOT/'src1.7.7'}[key]
        snapshots += [folder/name for name in core]
        if(folder/'CMakeLists.txt').exists():snapshots.append(folder/'CMakeLists.txt')
    snapshots += [p for p in (OUT/'experiment/source').rglob('*') if p.is_file() and p.suffix in ('.cpp','.hpp','.h','.py','.txt','.md','.json')]
    snapshots += [ROOT/'src1.7.7/tests/seed_rng.cpp']
    snapshots += [p for p in (ROOT/'题目/2026_comprehensive_200').glob('*.py')]
    # Source bytes are checked before archiving, including historical CRLF inputs.
    for relative,h in {**frozen['inputs'],**frozen['tools']}.items():assert sha((ROOT/relative).read_bytes())==h,relative
    pack('executed-input-source-tools',snapshots)
    pack('trace-evidence',[p for p in (OUT/'pair-evidence').glob('*.md')])
    pack('independent-100',[p for p in BANK.rglob('*') if p.is_file()]+[p for p in (OUT/'中文题卡').glob('*.md')])
    shutil.copy2(OUT/'preflight/audit.json',OUT/'preflight-audit.json')
    (OUT/'EVIDENCE_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('ARCHIVES VERIFIED',len(manifest['archives']),flush=True)
if __name__=='__main__':main()
