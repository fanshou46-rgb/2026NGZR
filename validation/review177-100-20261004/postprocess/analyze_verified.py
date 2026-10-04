"""Run the frozen analyzer with an explicit missing-terminal reporting repair.

The frozen source is retained byte-for-byte. SDK score 0 can exist without a
SAT terminal answer; that is not a label of G=0 and cannot be compared to int.
"""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parents[1]
original=ROOT/'tools/review177_100/analyze.py'
frozen=json.loads((OUT/'frozen-audit.json').read_text())
expected=frozen['tools'][original.relative_to(ROOT).as_posix()]
assert hashlib.sha256(original.read_bytes()).hexdigest()==expected
source=original.read_text(encoding='utf8')
old="category='goal_overcount' if g>value['final_goals'] else 'goal_undercount' if g<value['final_goals'] else 'other_difference' if (c!=value['credited_constraints'] or base!=value['base'] or cost!=value['action_cost']) else 'equal'"
new="category='sdk_terminal_missing' if value.get('final_goals') is None else 'goal_overcount' if g>value['final_goals'] else 'goal_undercount' if g<value['final_goals'] else 'other_difference' if (c!=value['credited_constraints'] or base!=value['base'] or cost!=value['action_cost']) else 'equal'"
assert source.count(old)==1
source=source.replace(old,new)
(OUT/'POSTPROCESS_REPAIR.json').write_text(json.dumps(dict(frozen_analyzer_sha256=expected,
    executed_analyzer_sha256=hashlib.sha256(source.encode('utf8')).hexdigest(),
    old=old,new=new,reason='preserve missing SDK terminal labels when raw score is zero; no run data changed'),indent=2)+'\n')
sys.path.insert(0,str(original.parent))
exec(compile(source,str(original),'exec'),dict(__file__=str(original),__name__='__main__'))
