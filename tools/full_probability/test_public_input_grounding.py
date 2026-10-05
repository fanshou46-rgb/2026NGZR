"""Independent semantic fixtures for public goal grounding, no author truth."""
import sys
sys.dont_write_bytecode=True
from verify_receipts import parse_public_missing_locations

public='(hold 0) (plate 0) (at 0 1) (sort 1 human) (size 1 big) (at 1 1) '
public+='(sort 2 cupboard) (size 2 big) (type 2 container) (at 2 2) '
public+='(sort 4 book) (size 4 small) (color 4 blue)'
task='(:ins (:task (give human X) (:cond (sort X book) (color X blue))))'
expected=dict(big=set(),acquisition={4})
assert parse_public_missing_locations(public,task,2)==expected
for supplied in ('(at 4 2)','(inside 4 2)'):
    assert parse_public_missing_locations(public+' '+supplied,task,2)==dict(big=set(),acquisition=set())
for field in ('hold','plate'):
    assert parse_public_missing_locations(public.replace('(%s 0)'%field,'(%s 4)'%field),task,2)==dict(big=set(),acquisition=set())
assert parse_public_missing_locations(public,task,1)==dict(big=set(),acquisition=set())
numeric='(:ins (:task (pickup 4) (:cond (sort 4 book))))'
assert parse_public_missing_locations(public,numeric,2)==expected
putdown='(:ins (:task (putdown X) (:cond (sort X book) (color X blue))))'
assert parse_public_missing_locations(public,putdown,2)==dict(big=set(),acquisition=set())
parent='(:ins (:task (putin X Y) (:cond (sort X book) (color X blue) (sort Y cupboard) (type Y container))))'
assert parse_public_missing_locations(public.replace('(at 2 2)',''),parent,2)==dict(big={2},acquisition={4})
print('9 public input fixtures: give recipient/object order, numeric binding, AT, inside, hand/tray, Stage1 and goal dependencies passed')
