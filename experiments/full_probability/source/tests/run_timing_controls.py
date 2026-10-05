"""Broad self-pairs: same binary for both labels; all server runs serial."""
import argparse, json, os, subprocess, sys
from pathlib import Path
sys.dont_write_bytecode=True
def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,required=True)
    p.add_argument('--baseline',type=Path,required=True);p.add_argument('--current',type=Path,required=True)
    p.add_argument('--seed-library',type=Path,required=True);a=p.parse_args()
    tests=Path(__file__).resolve().parent;os.environ['RDFW_STAGE_TIMING']='0'
    controls=[]
    for label,binary in [('baseline',a.baseline),('current',a.current)]:
        for round_id in range(1,4):
            folder=a.runs/('self-'+label+'-r'+str(round_id))
            subprocess.run([sys.executable,str(tests/'run_state_matrix.py'),'target','--repeat','1','--baseline',str(binary),'--current',str(binary),'--output',str(folder),'--seed-library',str(a.seed_library)],check=True)
            subprocess.run([sys.executable,str(tests/'summarize_state_matrix.py'),str(folder)],check=True)
            rows=json.loads((folder/'results.json').read_text())
            controls.extend(dict(binary=label,round=round_id,**row) for row in rows)
    (a.runs/'timing-controls.json').write_text(json.dumps(controls,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
