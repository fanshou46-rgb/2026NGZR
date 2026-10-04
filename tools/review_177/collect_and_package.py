"""Collect checks and publish exact evidence with CRC/SHA verification."""
import hashlib,json,re,shutil,zipfile
from pathlib import Path
TEMP=Path('/tmp') if __import__('os').name!='nt' else Path('//wsl.localhost/Ubuntu-18.04/tmp')
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'validation/review177-20261004';RUN=OUT/'raw/frozen-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
def main():
    assert json.loads((RUN/'final-audit.json').read_text(encoding='utf8'))['runs']==304
    checks=OUT/'checks';checks.mkdir(exist_ok=True);raw=OUT/'raw/checks';logs=raw/'logs';logs.mkdir(parents=True,exist_ok=False)
    for p in TEMP.glob('rdfw177*.log'):shutil.copyfile(str(p),str(logs/p.name))
    for kind,name,expected in [('unit','rdfw177-tests-8.log',320),('sanitizer','rdfw177-sanitizer-final.log',291)]:
        text=(logs/name).read_text(encoding='utf8',errors='replace');match=re.search(r'(\d+)% tests passed, (\d+) tests failed out of (\d+)',text)
        seconds=re.search(r'Total Test time \(real\) =\s*([\d.]+) sec',text)
        assert match and seconds and match.groups()==('100','0',str(expected))
        assert not any(x in text for x in ('ERROR: AddressSanitizer','runtime error:','ERROR: LeakSanitizer'))
        save(checks/(kind+'-summary.json'),dict(tests=expected,passed=expected,seconds=float(seconds.group(1)),sdk_direct_tests=29 if kind=='unit' else 0,sdk_subprocess_tests_included=kind=='unit',final_frozen_sources=True,draft_sanitizer_not_final_evidence=True,earlier_failed_logs_retained=True))
    for build in ('rdfw177-tests','rdfw177-sanitizer-nopie'):
        source=TEMP/build;dest=raw/build;dest.mkdir()
        for name in ('CMakeCache.txt','CTestTestfile.cmake','words.txt'):shutil.copyfile(str(source/name),str(dest/name))
        shutil.copytree(str(source/'Testing'),str(dest/'Testing'))
        for p in (source/'CMakeFiles').glob('*.dir/*'):
            if p.name in ('flags.make','link.txt','build.make'):
                folder=dest/'recipes'/p.parent.name;folder.mkdir(parents=True,exist_ok=True);shutil.copyfile(str(p),str(folder/p.name))
    shutil.copytree(str(TEMP/'rdfw177-tests/official-semantics'),str(raw/'official-semantics'))
    save(checks/'checked-source-hashes.json',{str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'src1.7.7').rglob('*') if p.is_file() and (p.suffix in ('.cpp','.hpp','.h','.sh') or p.name in ('words.txt','CMakeLists.txt'))})
    frozen=json.loads((checks/'pre-final-check-source-hashes.json').read_text(encoding='utf8'))
    assert all(sha(ROOT/'src1.7.7'/name)==h for name,h in frozen.items())
    audit=json.loads((RUN/'frozen-audit.json').read_text(encoding='utf8'))
    snapshot=raw/'executed-sources';snapshot.mkdir()
    for v in ('src1.7.6','src1.7.7'):
        dest=snapshot/v;dest.mkdir()
        for name,h in audit['sources'][v].items():
            assert sha(ROOT/v/name)==h;shutil.copyfile(str(ROOT/v/name),str(dest/name))
    dest=OUT/'evidence';dest.mkdir(exist_ok=False)
    manifest=dict(policy='All production, references, checks and failed attempts retained. Exact SDK resource duplicates represented once; generated binaries by hashes and build recipes.',archives=[],excluded=[])
    runtime=next((RUN/'runs').glob('*/runtime'));fixtures=raw/'sdk-fixtures';fixtures.mkdir();resources={}
    names={'iclingo','vrunact.sh','vruntask.sh'}|{Path(p).name for p in audit['sdk'] if p.startswith('res/')}
    for name in names:
        p=runtime/name
        if p.is_file():resources[name]=sha(p);shutil.copyfile(str(p),str(fixtures/name))
    def bundle(name,files):
        entries={};archive=dest/name
        with zipfile.ZipFile(str(archive),'w',zipfile.ZIP_DEFLATED) as z:
            for p in sorted(set(files)):
                h=sha(p);rel=p.relative_to(OUT).as_posix()
                duplicate='runtime' in p.parts and resources.get(p.name)==h
                binary=p.name in ('example','reference','seed.so','core') or p.name.startswith('core.') or p.suffix in ('.o','.a')
                if duplicate or binary:manifest['excluded'].append(dict(path=rel,sha256=h,reason='duplicate_sdk_resource' if duplicate else 'generated_binary'));continue
                entries[rel]=h;z.writestr(rel,p.read_bytes())
        with zipfile.ZipFile(str(archive)) as z:
            assert z.testzip() is None
            for name,h in entries.items():assert hashlib.sha256(z.read(name)).hexdigest()==h
        assert archive.stat().st_size<90*1024*1024
        manifest['archives'].append(dict(path=archive.name,sha256=sha(archive),bytes=archive.stat().st_size,entries=entries));print(archive.name,len(entries),archive.stat().st_size,flush=True)
    bundle('production-traces.zip',[p for p in (RUN/'runs').rglob('*') if p.is_file()])
    bundle('reference-traces.zip',[p for p in (RUN/'references').rglob('*') if p.is_file()])
    records=[p for p in RUN.rglob('*') if p.is_file() and 'runs' not in p.relative_to(RUN).parts and 'references' not in p.relative_to(RUN).parts]
    previous=OUT/'raw/reused-build';previous.mkdir()
    for name in ('build.log','build.json'):
        shutil.copyfile(str(ROOT/'validation/review176-20261004/raw/frozen-v2/build-current'/name),str(previous/name))
    records += [p for p in previous.iterdir() if p.is_file()]
    bundle('executed-records.zip',records)
    failed=[p for p in raw.rglob('*') if p.is_file()]
    bundle('checks-and-failures.zip',failed)
    draft=[p for p in (OUT/'raw/preflight-v1').rglob('*') if p.is_file()]
    draft += [p for p in (OUT/'raw/preflight-v1-questions').rglob('*') if p.is_file()]
    bundle('preflight-v1-failure.zip',draft)
    save(dest/'manifest.json',manifest)
if __name__=='__main__':main()
