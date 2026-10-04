"""Recover and verify the two pre-repair files; archive only exact frozen bytes."""
from pathlib import Path
import hashlib,json
from implement_relations import edit
import implement_relations
ROOT=Path(__file__).resolve().parents[2];RUN=ROOT/'validation/review176-20261004/raw/frozen-v1'
audit=json.loads((RUN/'frozen-audit.json').read_text(encoding='utf8'))
dest=RUN/'executed-sources/src1.7.6';dest.mkdir(parents=True,exist_ok=False)
for name in audit['sources']['src1.7.6']:(dest/name).write_bytes((ROOT/'src1.7.6'/name).read_bytes())
implement_relations.ROOT=dest
def old_containment(s):
    a=s.index('    // A new weak edge cannot demote');b=s.index('    // Keep one representative',a)
    s=s[:a]+s[b:]
    return s.replace('representative==UNKNOWN || (item.second.verified && !representative_verified) ||\n           (item.second.verified==representative_verified && item.first==container)','representative==UNKNOWN || item.first==container ||\n           (item.second.verified && !representative_verified)')
edit('containment.cpp',old_containment)
old=(ROOT/'src1.7.5/rdfw.cpp').read_bytes()
start=old.index(b'bool RDFW::GetSmallObjectStatus(');end=old.index(b'bool RDFW::GetBigObjectStatus(',start)
block=old[start:end]
a=block.index(b'    if (small->inside > 0 && static_cast<size_t>(small->inside) < objects.size()) {')
b=block.index(b'    if (chosen_relation == "inside") {',a)
block=block[:a]+b'    // A noisy reply cannot remove independent containment edges.\r\n\r\n'+block[b:]
raw=(dest/'rdfw.cpp').read_bytes();a=raw.index(b'bool RDFW::GetSmallObjectStatus(');b=raw.index(b'bool RDFW::GetBigObjectStatus(',a)
(dest/'rdfw.cpp').write_bytes(raw[:a]+block+raw[b:])
for name,h in audit['sources']['src1.7.6'].items():
    actual=hashlib.sha256((dest/name).read_bytes()).hexdigest();assert actual==h,(name,actual,h)
print('Rejected source snapshot: all frozen hashes verified')
