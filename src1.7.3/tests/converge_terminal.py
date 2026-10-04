from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=root/'terminal_checker.cpp'; s=p.read_text(encoding='utf-8')
start=s.index('bool constraintEvidenceUsable('); end=s.index('TerminalStatus boolStatus',start)
s=s[:start]+'''// The optional hypothesis view is only used by evaluatePlanningHypothesis.
// All terminal, constraint and score callers use canonical values.
int locationValue(const RDFW& w, const std::shared_ptr<Object>& o, bool hypothesis=false) {
    if (!o) return UNKNOWN;
    return hypothesis ? o->location : w.FactLocation(o->id);
}
int insideValue(const RDFW& w, const std::shared_ptr<SmallObject>& o, bool hypothesis=false) {
    if (!o) return UNKNOWN;
    return hypothesis ? o->inside : w.FactInside(o->id);
}
int containerValue(const RDFW& w, const std::shared_ptr<Container>& o, bool hypothesis=false) {
    if (!o) return UNKNOWN;
    return hypothesis ? o->isOpen : w.FactContainerState(o->id);
}
bool isLocationKnown(const RDFW& w, const std::shared_ptr<Object>& o, bool h=false) {
    return locationValue(w,o,h)!=UNKNOWN;
}
int scoreLocation(const RDFW& w, const std::shared_ptr<Object>& o, bool h=false) {
    if (!o) return UNKNOWN;
    if (h) {
        if (o->id==0) return w.location;
        return o->id < w.score_locations.size() ? w.score_locations[o->id] : o->location;
    }
    return w.ScoreFactLocation(o->id);
}
bool isInsideKnown(const RDFW& w, const std::shared_ptr<SmallObject>& o, bool h=false) {
    return insideValue(w,o,h)!=UNKNOWN;
}
bool isContainerStateKnown(const RDFW& w, const std::shared_ptr<Container>& o, bool h=false) {
    const int state=containerValue(w,o,h); return state==0 || state==1;
}
''' +s[end:]
s=s.replace('const std::shared_ptr<Object>& y) {','const std::shared_ptr<Object>& y, bool hypothesis=false) {')
s=s.replace('    if (!x) return TerminalStatus::UNKNOWN;','''    if (!x) return TerminalStatus::UNKNOWN;
    const int robot_location=hypothesis?world.location:world.FactLocation(0);
    const int hand=hypothesis?world.hold_id:world.FactValue(StateField::HOLD);
    const int tray=hypothesis?world.plate_id:world.FactValue(StateField::PLATE);
    const bool stored=hand==x->id || tray==x->id;
    const bool not_stored=hypothesis?(hand!=x->id && tray!=x->id):world.IsNotStoredFact(x->id);''')
s=s.replace('if (world.stage == 1)', 'if (world.stage == 1 || hypothesis)')
s=s.replace('world.location', 'robot_location')
# Undo local declaration and helper scope substitutions.
s=s.replace('const int robot_location=hypothesis?robot_location:', 'const int robot_location=hypothesis?world.location:')
s=s.replace('return w.location','return w.location')
for name in ['scoreLocation','isLocationKnown','isInsideKnown','isContainerStateKnown']:
    import re
    s=re.sub(r'\b'+name+r'\(world, ([\w]+)\)',name+r'(world, \1, hypothesis)',s)
s=s.replace('x->location','locationValue(world,x,hypothesis)').replace('target->location','locationValue(world,target,hypothesis)')
s=s.replace('static_cast<bool>(container->isOpen)','static_cast<bool>(containerValue(world,container,hypothesis))')
s=s.replace('small->inside == y->id','insideValue(world,small,hypothesis) == y->id').replace('small->inside != y->id','insideValue(world,small,hypothesis) != y->id')
s=s.replace('        const bool stored = world.hold_id == x->id || world.plate_id == x->id;\n','')
s=s.replace('if (world.stage == 2 && !world.IsInsideVerified(x->id))','if (!hypothesis && world.stage == 2 && !world.IsInsideVerified(x->id))')
s=s.replace('        return boolStatus(stored);','        if (!stored && !not_stored) return TerminalStatus::UNKNOWN;\n        return boolStatus(stored);')
s=s.replace('if (world.hold_id == x->id || world.plate_id == x->id)','if (stored)')
s=s.replace('        return TerminalStatus::SATISFIED;\n    }\n\n    if (behave == "putin"', '        return not_stored ? TerminalStatus::SATISFIED : TerminalStatus::UNKNOWN;\n    }\n\n    if (behave == "putin"')
s=s.replace('            if (stored)\n                return TerminalStatus::UNSATISFIED;', '            if (stored) return TerminalStatus::UNSATISFIED;\n            if (!not_stored) return TerminalStatus::UNKNOWN;')
s=s.replace('return boolStatus(world.plate_id == x->id);','if (tray==UNKNOWN && !not_stored) return TerminalStatus::UNKNOWN;\n        return boolStatus(tray == x->id);')
s=s.replace('return boolStatus(world.hold_id == x->id);','if (hand==UNKNOWN && !not_stored) return TerminalStatus::UNKNOWN;\n        return boolStatus(hand == x->id);')
# These declarations must read compatibility only in the explicitly labeled A view.
s=s.replace('const int hand=hypothesis?world.hold_id:', 'const int hand=hypothesis?world.hold_id:')
pos=s.index('TerminalSummary TerminalChecker::evaluateAll(')
s=s[:pos]+'''TerminalSummary TerminalChecker::evaluatePlanningHypothesis(const RDFW& world) const {
    TerminalSummary result;
    for (const auto& task:world.tasks) {
        TerminalStatus status=TerminalStatus::UNKNOWN;
        bool first=true;
        if (task.IsUsable()) for (auto x:scoreBindings(world,task.conditionX,task.X)) {
            const auto ys=scoreBindings(world,task.conditionY,task.Y);
            for (std::size_t i=0; i<(ys.empty()?1:ys.size()); ++i) {
                const auto next=evaluatePair(world,task.behave,x,ys.empty()?nullptr:ys[i],true);
                if (!first && status!=next) { status=TerminalStatus::UNKNOWN; break; }
                status=next; first=false;
            }
        }
        result.goals.push_back(status);
    }
    return result;
}

'''+s[pos:]
p.write_text(s,encoding='utf-8')
