"""Preserve exact executed bytes, including historical Windows newline forms."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'validation/review177-20261004'
def main():
    audit=json.loads((OUT/'raw/frozen-v1/frozen-audit.json').read_text(encoding='utf8'))
    expected=dict(audit['inputs']);expected.update(audit['tooling'])
    archive=OUT/'checks/executed-input-tooling.zip'
    with zipfile.ZipFile(str(archive),'w',zipfile.ZIP_DEFLATED) as z:
        for name,h in sorted(expected.items()):
            data=(ROOT/name).read_bytes();assert hashlib.sha256(data).hexdigest()==h
            z.writestr(name,data)
    with zipfile.ZipFile(str(archive)) as z:
        assert z.testzip() is None
        for name,h in expected.items():assert hashlib.sha256(z.read(name)).hexdigest()==h
    (OUT/'checks/executed-input-tooling.json').write_text(json.dumps(dict(files=len(expected),archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),expected_sha256=expected),ensure_ascii=False,indent=2),encoding='utf8')
    print('Archived exact frozen input/tool bytes:',len(expected))
if __name__=='__main__':main()
