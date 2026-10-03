"""Development transform: query reuse within one immutable predicate call."""
from pathlib import Path
import re
p=Path(__file__).resolve().parents[1]/'terminal_checker.cpp'
s=p.read_text()
start=s.index('// The optional hypothesis view');end=s.index('TerminalStatus boolStatus',start)
s=s[:start]+'''// Cache lasts for one predicate evaluation. No mutation, persistent cache,
// revision shortcut, or change to recursive qualification is involved.
struct PairFacts {
    const RDFW& world;
    unsigned ids[4] = {};
    unsigned used=0;
    StateClaim values[4][5];
    bool seen[4][5] = {};
    explicit PairFacts(const RDFW& w):world(w) {}
    StateClaim get(StateField field,unsigned id) {
        unsigned row=0;
        while(row<used && ids[row]!=id) ++row;
        if(row==4) return world.ResolvedState(field,id);
        if(row==used) ids[used++]=id;
        const unsigned f=unsigned(field);
        if(!seen[row][f]) { values[row][f]=world.ResolvedState(field,id); seen[row][f]=true; }
        return values[row][f];
    }
    int value(StateField field,unsigned id) { const auto c=get(field,id); return c.present?c.value:UNKNOWN; }
};
''' +s[end:]
start=s.index('    const int robot_location=');end=s.index('\n    if (behave == "goto"',start)
s=s[:start]+'''    PairFacts facts(world);
    const auto robot_location = [&]() { return hypothesis?world.location:facts.value(StateField::LOCATION,0); };
    const auto hand = [&]() { return hypothesis?world.hold_id:facts.value(StateField::HOLD,0); };
    const auto tray = [&]() { return hypothesis?world.plate_id:facts.value(StateField::PLATE,0); };
    const auto stored = [&]() { return hand()==x->id || tray()==x->id; };
    const auto not_stored = [&]() {
        if(hypothesis) return hand()!=x->id && tray()!=x->id;
        if(!world.IsValidObjectId(x->id) || stored()) return false;
        const int h=hand(), t=tray();
        if(h!=UNKNOWN && t!=UNKNOWN) return h!=x->id && t!=x->id;
        const auto in=facts.get(StateField::INSIDE,x->id);
        if(!in.present) return false;
        if(in.value>0) return true;
        return facts.get(StateField::LOCATION,x->id).present && in.value==NONE &&
            (in.source==EvidenceSource::SENSE || in.source==EvidenceSource::ACTION_SUCCESS);
    };
    const auto locationValue = [&](const std::shared_ptr<Object>& o) { return !o?UNKNOWN:hypothesis?o->location:facts.value(StateField::LOCATION,o->id); };
    const auto insideValue = [&](const std::shared_ptr<SmallObject>& o) { return !o?UNKNOWN:hypothesis?o->inside:facts.value(StateField::INSIDE,o->id); };
    const auto containerValue = [&](const std::shared_ptr<Container>& o) { return !o?UNKNOWN:hypothesis?o->isOpen:facts.value(StateField::CONTAINER_STATE,o->id); };
    const auto scoreLocation = [&](const std::shared_ptr<Object>& o) {
        if(!o) return UNKNOWN;
        if(hypothesis) { if(o->id==0) return world.location;
            return o->id<world.score_locations.size()?world.score_locations[o->id]:o->location; }
        const int loc=locationValue(o);
        if(world.stage==1 && o->id>0) return loc!=UNKNOWN && o->id<world.score_locations.size()?world.score_locations[o->id]:UNKNOWN;
        return loc;
    };
''' +s[end:]
start=s.index('TerminalStatus evaluatePair');end=s.index('\nvoid countStatus',start)
part=s[start:end]
for name in ['scoreLocation','locationValue','insideValue','containerValue']:
    part=re.sub(name+r'\(world,\s*(\w+),\s*hypothesis\)',name+r'(\1)',part)
for name,func in [('isLocationKnown','locationValue'),('isInsideKnown','insideValue')]:
    part=re.sub(name+r'\(world,\s*(\w+),\s*hypothesis\)',r'('+func+r'(\1)!=UNKNOWN)',part)
part=part.replace('isContainerStateKnown(world, container, hypothesis)','(containerValue(container)==0 || containerValue(container)==1)')
part=re.sub(r'world.IsInsideVerified\(x->id\)',r'facts.get(StateField::INSIDE,x->id).present',part)
# Bare variables only, outside lambda definitions.
pos=part.index('    if (behave == "goto"')
tail=part[pos:]
for name in ['robot_location','hand','tray','stored','not_stored']:
    tail=re.sub(r'\b'+name+r'\b(?!\s*\()',name+'()',tail)
part=part[:pos]+tail
s=s[:start]+part+s[end:]
# Capacity reservations change allocation only, not grounding/ordering.
s=s.replace('    std::vector<std::shared_ptr<Object>> result;\n    for','    std::vector<std::shared_ptr<Object>> result;\n    result.reserve(world.objects.size());\n    for')
s=s.replace('    result.constraints.reserve(world.not_infoConstrains.size() +','    const std::size_t constraint_count=world.not_infoConstrains.size()+world.notnot_infoConstrains.size()+world.not_taskConstrains.size();\n    result.constraint_eligible.reserve(constraint_count);\n    result.constraint_credited.reserve(constraint_count);\n    result.constraints.reserve(world.not_infoConstrains.size() +')
p.write_text(s)
