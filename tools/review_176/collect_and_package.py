"""Collect checks and publish exact evidence with CRC/SHA verification."""
import hashlib,json,re,shutil,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'validation/review176-20261004';RUN=OUT/'raw/frozen-v2'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
def main():
    assert json.loads((RUN/'final-audit.json').read_text(encoding='utf8'))['runs']==416
    checks=OUT/'checks';checks.mkdir(exist_ok=True);raw=OUT/'raw/checks';logs=raw/'logs';logs.mkdir(parents=True,exist_ok=False)
    for p in Path('/tmp').glob('rdfw176*.log'):shutil.copyfile(str(p),str(logs/p.name))
    for kind,name,expected in [('unit','rdfw176-tests-5.log',304),('sanitizer','rdfw176-sanitizer.log',275)]:
        text=(logs/name).read_text(encoding='utf8',errors='replace');match=re.search(r'(\d+)% tests passed, (\d+) tests failed out of (\d+)',text)
        seconds=re.search(r'Total Test time \(real\) =\s*([\d.]+) sec',text)
        assert match and seconds and match.groups()==('100','0',str(expected))
        assert not any(x in text for x in ('ERROR: AddressSanitizer','runtime error:','ERROR: LeakSanitizer'))
        save(checks/(kind+'-summary.json'),dict(tests=expected,passed=expected,seconds=float(seconds.group(1)),sdk_direct_tests=29 if kind=='unit' else 0,sdk_subprocess_tests_included=kind=='unit',first_run_passed=kind=='sanitizer',earlier_failed_logs_retained=True))
    for build in ('rdfw176-tests','rdfw176-sanitizer-nopie'):
        source=Path('/tmp')/build;dest=raw/build;dest.mkdir()
        for name in ('CMakeCache.txt','CTestTestfile.cmake','words.txt'):shutil.copyfile(str(source/name),str(dest/name))
        shutil.copytree(str(source/'Testing'),str(dest/'Testing'))
        for p in (source/'CMakeFiles').glob('*.dir/*'):
            if p.name in ('flags.make','link.txt','build.make'):
                folder=dest/'recipes'/p.parent.name;folder.mkdir(parents=True,exist_ok=True);shutil.copyfile(str(p),str(folder/p.name))
    shutil.copytree('/tmp/rdfw176-tests/official-semantics',str(raw/'official-semantics'))
    save(checks/'checked-source-hashes.json',{str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'src1.7.6').rglob('*') if p.is_file() and (p.suffix in ('.cpp','.hpp','.h','.sh') or p.name in ('words.txt','CMakeLists.txt'))})
    audit=json.loads((RUN/'frozen-audit.json').read_text(encoding='utf8'))
    snapshot=raw/'executed-sources';snapshot.mkdir()
    for v in ('src1.7.5','src1.7.6'):
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
        shutil.copyfile(str(ROOT/'validation/review175-20261004/frozen-v2/build-current'/name),str(previous/name))
    records += [p for p in previous.iterdir() if p.is_file()]
    bundle('executed-records.zip',records)
    failed=[p for p in raw.rglob('*') if p.is_file()]
    failed += [p for p in (OUT/'raw/frozen-v1').rglob('*') if p.is_file()]
    failed += [p for p in (OUT/'raw/counterexamples').rglob('*') if p.is_file()]
    bundle('checks-and-failures.zip',failed)
    save(dest/'manifest.json',manifest)
if __name__=='__main__':main()
