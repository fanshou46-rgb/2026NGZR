"""Rebuild ignored SDK clients for a fresh-checkout reproduction, without overwrites."""
import argparse,hashlib,importlib.util,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--sdk',type=Path,required=True);args=parser.parse_args()
    audit=json.loads((ROOT/'validation/review177-20261004/frozen-audit.json').read_text(encoding='utf8'))
    for version,files in audit['sources'].items():
        for name,value in files.items():assert hashlib.sha256((ROOT/version/name).read_bytes()).hexdigest()==value,(version,name)
    outputs={'src1.7.6':ROOT/'validation/review176-20261004/raw/frozen-v2/build-current',
             'src1.7.7':ROOT/'validation/review177-20261004/raw/preflight-v1/build-current'}
    assert all(not p.exists() for p in outputs.values()), 'Use a fresh reproduction checkout; never overwrite original evidence'
    path=ROOT/'src1.7.7/tests/run_probe_compare.py'
    spec=importlib.util.spec_from_file_location('replay_build',str(path));helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    for version,dest in outputs.items():
        helper.build(ROOT/version,dest,args.sdk.resolve())
        print('Rebuilt',version,'in',dest,flush=True)
    print('Now run tools/review_177/run_review.py with a fresh --out. These are newly built clients and a new experiment, not the original binaries or timing.')
if __name__=='__main__':main()
