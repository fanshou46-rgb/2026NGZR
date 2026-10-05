"""Remove premature external-commit markers; actual gateway owns this boundary."""
from pathlib import Path
p=Path(__file__).resolve().parents[2]/'experiments/full_probability/source/rdfw.cpp'
s=p.read_text(encoding='utf8')
old='    if (!shadow_dry_run) mutation.platformSucceeded();\n'
assert s.count(old)==9,s.count(old)
s=s.replace(old,'')
s=s.replace('    score_evaluator.reset();\n','    score_evaluator.reset();\n    execution_evidence.reset(false);\n    pending_execution=0;\n',1)
p.write_text(s,encoding='utf8',newline='\n')
print('Dispatch boundary moved into gateway')
