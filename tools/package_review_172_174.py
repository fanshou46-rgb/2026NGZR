"""Archive every review result, with explicit duplicate/runtime exclusions."""
from pathlib import Path
import hashlib,json,zipfile,shutil
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'validation/review-20261004'
RUN=OUT/'frozen-comparison-v3'
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
 dest=OUT/'evidence';dest.mkdir(exist_ok=False)
 audit=json.loads((RUN/'frozen-audit.json').read_text(encoding='utf8'))
 assert json.loads((RUN/'final-audit.json').read_text(encoding='utf8'))['runs']==384
 copied_names={'iclingo','vrunact.sh','vruntask.sh'}|{Path(p).name for p in audit['sdk'] if p.startswith('res/')}
 # Names alone are insufficient: a copied template may become a dynamic state.
 # Keep one exact runtime resource bundle and omit only byte-identical copies.
 resource_hashes={}
 first_runtime=next(p for p in sorted((RUN/'runs').glob('*/runtime')))
 fixtures=RUN/'sdk-runtime-fixtures';fixtures.mkdir(exist_ok=False)
 for name in sorted(copied_names):
  source=first_runtime/name
  if not source.is_file():continue
  digest=sha(source.read_bytes());expected=audit['sdk'].get('res/'+name)
  if expected is not None and digest!=expected:continue
  resource_hashes[name]=digest;shutil.copyfile(source,fixtures/name)
 manifest={'policy':'No run excluded. Repeated SDK resources and generated binaries are represented by hashes; dynamic ASP states, traces and failures are retained.',
           'archives':[],'excluded':[]}
 def bundle(name,files):
  entries={};archive=dest/name
  with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
   for path in sorted(files):
    relative=path.relative_to(OUT).as_posix()
    data=path.read_bytes();digest=sha(data)
    duplicate='runtime' in path.parts and resource_hashes.get(path.name)==digest
    binary=path.name in ('reproduce','reproduce-v2','reproduce-multi','reference-client','seed.so','core') or path.name.startswith('core.') or path.suffix in ('.a','.o')
    if duplicate or binary:
     manifest['excluded'].append({'path':relative,'sha256':digest,'reason':'duplicate_sdk_resource' if duplicate else 'generated_binary'})
     continue
    entries[relative]=digest;z.writestr(relative,data)
  with zipfile.ZipFile(archive) as z:
   assert z.testzip() is None
   assert set(z.namelist())==set(entries)
   for n,h in entries.items():assert sha(z.read(n))==h
  manifest['archives'].append({'path':name,'sha256':sha(archive.read_bytes()),'bytes':archive.stat().st_size,'entries':entries})
  assert archive.stat().st_size<90*1024*1024
  print(name,len(entries),'entries',archive.stat().st_size,'bytes',flush=True)
 bundle('production-traces.zip',[p for p in (RUN/'runs').rglob('*') if p.is_file()])
 bundle('reference-traces.zip',[p for p in (RUN/'reference-runs').rglob('*') if p.is_file()])
 bundle('executed-sources-and-records.zip',[p for p in RUN.rglob('*') if p.is_file() and 'runs' not in p.relative_to(RUN).parts and 'reference-runs' not in p.relative_to(RUN).parts])
 extra=[p for p in (OUT/'semantics').rglob('*') if p.is_file()]
 if (OUT/'checks').exists():extra.extend(p for p in (OUT/'checks').rglob('*') if p.is_file())
 extra.extend(OUT.glob('*.log'))
 bundle('semantics-and-checks.zip',extra)
 (dest/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
 for name in ('frozen-audit.json','final-audit.json'):shutil.copyfile(RUN/name,OUT/name)
 print('All ZIP CRC and per-entry SHA verified.')
if __name__=='__main__':main()
