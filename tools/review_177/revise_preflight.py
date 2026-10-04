"""Retain a preflight-only failed design; shorten references before planner runs."""
import hashlib,json,shutil,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'validation/review177-20261004'
def main():
    run=OUT/'raw/frozen-v1'
    assert not (run/'results.json').exists(), 'Never edit questions after viewing planner results'
    checks=OUT/'checks'; archive=checks/'preflight-v1-inputs-tools.zip'
    audit=json.loads((run/'frozen-audit.json').read_text(encoding='utf8'))
    files=set(audit['inputs'])|set(audit['tooling'])
    with zipfile.ZipFile(str(archive),'w',zipfile.ZIP_DEFLATED) as z:
        for name in sorted(files):z.writestr(name, (ROOT/name).read_bytes())
    with zipfile.ZipFile(str(archive)) as z:
        assert z.testzip() is None
        for name in files:assert hashlib.sha256(z.read(name)).hexdigest()==(audit['inputs'].get(name) or audit['tooling'][name])
    (checks/'preflight-v1-design.json').write_text(json.dumps(dict(reason='Author reference k03a NT reached SDK 5000ms at action 12; same IT finished 16 actions in 4645ms. No planner run started. Shorten every family equally before observing planner scores.',archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),planner_runs=0),indent=2),encoding='utf8')
    old=OUT/'raw/preflight-v1';assert not old.exists();shutil.move(str(run),str(old))
    bank=ROOT/'题目/generalization_177_20261004';oldbank=OUT/'raw/preflight-v1-questions';shutil.move(str(bank),str(oldbank))
    gen=ROOT/'tools/review_177/generate_holdout.py';s=gen.read_text(encoding='utf8')
    s=s.replace("info+=['(at %d %d)'%(ids[n],loc['human']) for n in names[5:]]", "info+=['(at %d %d)'%(ids[n],loc['desk'] if n=='book' else loc['human']) for n in names[5:]]")
    s=s.replace("            move(loc['human']);plan+=[['PickUp',ids['book']]]\n            move(loc['desk']);plan+=[['PutDown',ids['book']]]\n", '')
    s=s.replace('作者动作仅验证SDK可解性。', '书初始在书桌且保持独立 inside（相应族）；其送达目标是已满足控制。作者路径缩短以适应5秒预算，只验证SDK可解性。')
    gen.write_text(s,encoding='utf8')
    runner=ROOT/'tools/review_177/run_review.py';s=runner.read_text(encoding='utf8')
    s=s.replace("    exe['src1.7.7']=helper.build(ROOT/'src1.7.7',out/'build-current',sdk)\n", "    import shutil\n    current=ROOT/'validation/review177-20261004/raw/preflight-v1/build-current'\n    cm=json.loads((current/'build.json').read_text(encoding='utf8'))\n    assert all(cm['sources'].get(k)==v for k,v in sources['src1.7.7'].items())\n    assert sha(current/'example')==cm['binary_sha256']\n    shutil.copytree(str(current),str(out/'build-current'))\n    exe['src1.7.7']=out/'build-current/example'\n")
    runner.write_text(s,encoding='utf8')
if __name__=='__main__':main()
