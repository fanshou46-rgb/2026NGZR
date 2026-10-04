from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[2]
s=(ROOT/'tools/review_176/run_review.py').read_text(encoding='utf8')
s=re.sub(r'src1\.7\.[56]',lambda m:'src1.7.'+str(int(m.group()[-1])+1),s)
s=s.replace("('holdout176','generalization_176_20261004')","('seen176','generalization_176_20261004'),('holdout177','generalization_177_20261004')")
s=s.replace('groups[:3]','groups[:4]').replace("('g01a','h03a','j01a','j02a')","('g01a','h03a','j01a','k01a')")
s=s.replace("validation/review175-20261004/frozen-v2/build-current","validation/review176-20261004/raw/frozen-v2/build-current")
s=s.replace('tools/review_176/generate_holdout.py','tools/review_177/generate_holdout.py')
s=s.replace('groups[2][2]','groups[3][2]').replace("groups[2][1]/c['path']","groups[3][1]/c['path']")
s=s.replace('/416','/304').replace('len(rows)==416','len(rows)==304')
s=s.replace("        for gi,(label,folder,cases) in enumerate(groups):", "        for gi,(label,folder,cases) in enumerate(groups):\n            if si and label not in ('holdout177','competition'):continue")
s=s.replace("all 24 old + all 12 seen175 + all 8 new176 + 6 preselected competition; IT/NT x 2 seeds x 2 versions = 400; four Stage1 controls x IT/NT x 2 versions = 16; rotated serial order; all failures retained; no concurrent builds or input changes", "24 old + 12 seen175 + 8 seen176 one seed IT/NT/two versions=176; 8 holdout177 + 6 competition two seeds IT/NT/two versions=112; four Stage1 controls IT/NT/two versions=16; total304; serial rotated; frozen all bytes; no concurrent builds")
dest=ROOT/'tools/review_177/run_review.py';assert not dest.exists();dest.write_text(s,encoding='utf8')
s=(ROOT/'tools/review_176/summarize_review.py').read_text(encoding='utf8').replace('review176','review177').replace('frozen-v2','frozen-v1')
s=re.sub(r'src1\.7\.[56]',lambda m:'src1.7.'+str(int(m.group()[-1])+1),s).replace("audit['runs']==416","audit['runs']==304")
dest=ROOT/'tools/review_177/summarize_review.py';assert not dest.exists();dest.write_text(s,encoding='utf8')
