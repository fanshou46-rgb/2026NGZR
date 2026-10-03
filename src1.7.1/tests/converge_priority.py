"""Keep legacy predicate policy; use canonical values and qualifications."""
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'legacy_priority.cpp'
s=p.read_text(encoding='utf-8')
start=s.index('bool isLocationKnown'); end=s.index('TerminalStatus boolStatus',start)
s=s[:start]+'''bool isLocationKnown(const RDFW& w, const std::shared_ptr<Object>& o) {
    return o && w.FactLocation(o->id)!=UNKNOWN;
}
bool isInsideKnown(const RDFW& w, const std::shared_ptr<SmallObject>& o) {
    return o && w.FactInside(o->id)!=UNKNOWN;
}
bool isContainerStateKnown(const RDFW& w, const std::shared_ptr<Container>& o) {
    return o && w.FactContainerState(o->id)!=UNKNOWN;
}
''' +s[end:]
s=s.replace('x->location','world.FactLocation(x->id)').replace('target->location','world.FactLocation(target->id)').replace('small->inside','world.FactInside(small->id)').replace('container->isOpen','world.FactContainerState(container->id)').replace('world.location','world.FactLocation(0)')
s=s.replace('world.hold_id == x->id || world.plate_id == x->id','world.IsStoredFact(x->id)')
s=s.replace('        return boolStatus(stored);','        if (!stored && !world.IsNotStoredFact(x->id)) return TerminalStatus::UNKNOWN;\n        return boolStatus(stored);')
s=s.replace('return boolStatus(world.plate_id == x->id);','return world.FactValue(StateField::PLATE)==UNKNOWN && !world.IsNotStoredFact(x->id) ? TerminalStatus::UNKNOWN : boolStatus(world.FactValue(StateField::PLATE) == x->id);')
s=s.replace('return boolStatus(world.hold_id == x->id);','return world.FactValue(StateField::HOLD)==UNKNOWN && !world.IsNotStoredFact(x->id) ? TerminalStatus::UNKNOWN : boolStatus(world.FactValue(StateField::HOLD) == x->id);')
p.write_text(s,encoding='utf-8')
