"""Publish every result and failed check; omit binaries and exact SDK duplicates."""
from pathlib import Path
import hashlib,json,shutil,zipfile
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'validation/review175-20261004';RUN=OUT/'frozen-v5'
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
 assert json.loads((RUN/'final-audit.json').read_text())['runs']==432
 dest=OUT/'evidence';dest.mkdir(exist_ok=False);manifest={'archives':[],'excluded':[],'policy':'Every run retained; exact immutable SDK resource duplicates and generated binaries represented by hashes.'}
 audit=json.loads((RUN/'frozen-audit.json').read_text());resource_hashes={}
 runtime=next((RUN/'runs').glob('*/runtime'));fixtures=OUT/'checks/raw/sdk-fixtures';fixtures.mkdir(parents=True,exist_ok=False)
 names={'iclingo','vrunact.sh','vruntask.sh'}|{Path(p).name for p in audit['sdk'] if p.startswith('res/')}
 for name in names:
  p=runtime/name
  if not p.is_file():continue
  digest=sha(p.read_bytes());expected=audit['sdk'].get('res/'+name)
  if expected is not None and digest!=expected:continue
  resource_hashes[name]=digest;shutil.copyfile(str(p),str(fixtures/name))
 def bundle(name,files):
  entries={};archive=dest/name
  with zipfile.ZipFile(str(archive),'w',zipfile.ZIP_DEFLATED) as z:
   for p in sorted(set(files)):
    data=p.read_bytes();digest=sha(data);rel=p.relative_to(OUT).as_posix()
    duplicate='runtime' in p.parts and resource_hashes.get(p.name)==digest
    binary=p.name in ('example','reference','seed.so','core') or p.name.startswith('core.') or p.suffix in ('.o','.a')
    if duplicate or binary:manifest['excluded'].append(dict(path=rel,sha256=digest,reason='duplicate_sdk_resource' if duplicate else 'generated_binary'));continue
    entries[rel]=digest;z.writestr(rel,data)
  with zipfile.ZipFile(str(archive)) as z:
   assert z.testzip() is None
   for p,h in entries.items():assert sha(z.read(p))==h
  assert archive.stat().st_size<90*1024*1024
  manifest['archives'].append(dict(path=name,sha256=sha(archive.read_bytes()),bytes=archive.stat().st_size,entries=entries));print(name,len(entries),archive.stat().st_size,flush=True)
 bundle('production-traces.zip',[p for p in (RUN/'runs').rglob('*') if p.is_file()])
 bundle('reference-traces.zip',[p for p in (RUN/'reference-runs').rglob('*') if p.is_file()])
 competition=OUT/'frozen-competition'
 assert json.loads((competition/'final-audit.json').read_text())['runs']==72
 bundle('competition-sample.zip',[p for p in competition.rglob('*') if p.is_file()])
 records=[p for p in RUN.rglob('*') if p.is_file() and 'runs' not in p.relative_to(RUN).parts and 'reference-runs' not in p.relative_to(RUN).parts]
 # Reused binaries live outside the run, so include their build recipes/hashes.
 snapshots=OUT/'checks/raw/executed-sources';snapshots.mkdir(parents=True,exist_ok=False)
 for version in ('src1.7.3','src1.7.4','src1.7.5'):
  target=snapshots/version;target.mkdir()
  for p in (ROOT/version).iterdir():
   if p.is_file() and (p.suffix in ('.cpp','.hpp','.h') or p.name in ('words.txt','CMakeLists.txt')):shutil.copyfile(str(p),str(target/p.name))
  assert all(sha((target/name).read_bytes())==h for name,h in audit['sources'][version].items())
 records += [p for p in (OUT/'frozen-v2/build-current').iterdir() if p.is_file()]
 bundle('executed-records.zip',records)
 failed=[]
 for draft in ('frozen-v1','frozen-v2','frozen-v3','frozen-v4'):
  failed += [p for p in (OUT/draft).rglob('*') if p.is_file() and 'build-current' not in p.relative_to(OUT/draft).parts]
 failed += [p for p in (OUT/'checks/raw').rglob('*') if p.is_file()]
 bundle('checks-and-failures.zip',failed)
 (dest/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
 for name in ('frozen-audit.json','final-audit.json'):shutil.copyfile(str(RUN/name),str(OUT/name))
if __name__=='__main__':main()
