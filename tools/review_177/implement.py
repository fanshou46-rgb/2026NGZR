from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[2]
p=ROOT/'src1.7.7'
assert not p.exists()
shutil.copytree(str(ROOT/'src1.7.6'),str(p),ignore=shutil.ignore_patterns('build','test-results','__pycache__','.git'))
for folder in ('tools/review_177','validation/review177-20261004'):
    (ROOT/folder).mkdir(exist_ok=True)
(ROOT/'tools/review_177/.gitignore').write_text('__pycache__/\n',encoding='utf8')
(ROOT/'tools/review_177/.gitattributes').write_text('*.py -text\n',encoding='utf8')
(ROOT/'validation/review177-20261004/.gitignore').write_text('raw/\n*.log\n',encoding='utf8')
(ROOT/'validation/review177-20261004/.gitattributes').write_text('*.json -text\n*.csv -text\n*.zip -text -diff\n*.cpp -text\n*.txt -text\n',encoding='utf8')
def edit(name,old,new):
    f=p/name;b=f.read_bytes();assert old in b,(name,old);f.write_bytes(b.replace(old,new))
edit('CMakeLists.txt',b'VERSION 1.7.6',b'VERSION 1.7.7')
edit('rdfw.cpp',b'[PlannerVersion] 1.7.6',b'[PlannerVersion] 1.7.7')
# Further source changes are recorded in repair_at.py / repair_probe.py.
