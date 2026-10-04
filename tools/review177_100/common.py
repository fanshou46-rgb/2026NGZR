"""Independent 100-question audit. Historical sources are read-only inputs."""
import hashlib, importlib.util, json, sys, os
from pathlib import Path
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
TOOLS = Path(__file__).resolve().parent
OUT = ROOT / 'validation/review177-100-20261004'
BANK = ROOT / '题目/independent_100_20261004'
SDK = Path(os.environ.get('RDFW_AUDIT_SDK','/tmp/env-release-2026-search')) if sys.platform!='win32' else ROOT.parent/'env-release-2026'
OLD = ROOT / '题目/2026_comprehensive_200'
SEEDS = [2026100403, 2026100404, 2026100405, 2026100403]
ARMS = ['167', '167_200', '177', 'neutral', 'no_ask', 'legacy_visibility']
SOURCES = {'167':ROOT/'HistoryVersion/src1.6.7', '167_200':ROOT/'src1.6.7-200ms', '177':ROOT/'src1.7.7'}
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p, value):
    p=Path(p); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def module(name,p):
    spec=importlib.util.spec_from_file_location(name,str(p)); m=importlib.util.module_from_spec(spec)
    sys.modules[name]=m;spec.loader.exec_module(m);return m
def helpers():
    return module('audit_compare',ROOT/'src1.7.7/tests/run_probe_compare.py'), module('audit_runner',ROOT/'HistoryVersion/src1.1.2 (x)/tools/baseline.py')
def core(p):
    return {q.name:sha(q) for q in sorted(p.iterdir()) if q.suffix in ('.cpp','.hpp','.h') or q.name=='words.txt'}
