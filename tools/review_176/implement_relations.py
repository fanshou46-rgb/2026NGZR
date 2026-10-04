"""Apply one version's relation/feedback changes while preserving untouched bytes."""
from pathlib import Path
import difflib
ROOT = Path(__file__).resolve().parents[2] / 'src1.7.6'


def edit(name, fn):
    path = ROOT / name
    raw = path.read_bytes()
    old = raw.decode('utf8').splitlines(keepends=True)
    contents = [line.rstrip('\r\n') for line in old]
    original = '\n'.join(contents) + '\n'
    revised = fn(original).splitlines()
    newline = '\r\n' if raw.count(b'\r\n') > raw.count(b'\n') / 2 else '\n'
    result = []
    for op, a, b, c, d in difflib.SequenceMatcher(None, contents, revised, autojunk=False).get_opcodes():
        result.extend(old[a:b] if op == 'equal' else
                      [line + newline for line in revised[c:d]] if op in ('insert', 'replace') else [])
    path.write_bytes(''.join(result).encode('utf8'))


def header(s):
    s = s.replace('    struct StateProvenance {', '''    struct InsideEdge {
        int value = UNKNOWN;
        bool verified = false;
        EvidenceSource source = EvidenceSource::UNKNOWN;
        InsideEdge() = default;
        InsideEdge(int v, bool k, EvidenceSource s): value(v), verified(k), source(s) {}
    };
    struct StateProvenance {''', 1)
    s = s.replace('        unsigned int storage_exclusion = 0;', '''        unsigned int storage_exclusion = 0;
        // INSIDE only. Each SDK edge is independent; a positive edge never
        // proves another edge false. These maps participate in existing journals.
        std::map<unsigned, InsideEdge> inside_edges;
        bool inside_complete = false;''', 1)
    s = s.replace('                hold->inside = NONE;\n', '').replace('                plate->inside = NONE;\n', '')
    s = s.replace('        int FactInside(unsigned int id) const {', '''        int InsideRelation(unsigned int id, unsigned int container, bool hypothesis=false) const;
        void SetInsideRelation(unsigned int id, unsigned int container, int value,
                               bool verified, EvidenceSource source);
        int FactInside(unsigned int id) const {''', 1)
    return s


def cpp(s):
    # Slot transitions do not change SDK containment.
    for name, end in [('SetHold', 'void RDFW::SetPlate'), ('SetPlate', 'bool RDFW::HasContradictoryEvidence')]:
        a = s.index('void RDFW::' + name); b = s.index(end, a + 1)
        block = s[a:b].replace('        ClearContainerMembership(item);\n', '').replace(
            '        SetInsideEvidence(item->id, verified, source);\n', '')
        s = s[:a] + block + s[b:]
    a = s.index('void RDFW::SetInsideEvidence'); b = s.index('void RDFW::SetContainerEvidence', a)
    s = s[:a] + '''void RDFW::SetInsideEvidence(unsigned int id, bool verified, EvidenceSource source) {
    StateMutation mutation(*this);
    if (!EnsureEvidenceCapacity(id)) return;
    const auto small = id < objects.size() ? dynamic_pointer_cast<SmallObject>(objects[id]) : nullptr;
    if (small && small->inside > 0) {
        SetInsideRelation(id, small->inside, 1, verified, source);
        return;
    }
    auto& p = MutableProvenance(StateField::INSIDE,id);
    if (small && small->inside == NONE && verified) {
        // An explicit whole-record assignment, not a slot-action inference.
        p.inside_complete = true;
        for (auto& edge:p.inside_edges) edge.second=InsideEdge(0,true,source);
    } else if (!small || small->inside == UNKNOWN) {
        p.inside_complete = false;
        for (auto& edge:p.inside_edges) edge.second.verified=false;
    }
    UpdateProvenance(StateField::INSIDE,id,small?small->inside:UNKNOWN,verified,source);
}

''' + s[b:]
    s = s.replace('    if (field == StateField::INSIDE) { objectInsideVerified[id]=false;', '''    if (field == StateField::INSIDE) {
        p.inside_complete=false;
        for(auto& edge:p.inside_edges) edge.second.verified=false;
        objectInsideVerified[id]=false;''', 1)
    # Binary task qualifications use the requested edge, never another parent.
    s = s.replace('dynamic_pointer_cast<SmallObject>(object) && FactInside(object->id)==UNKNOWN)',
                  'dynamic_pointer_cast<SmallObject>(object) && (task.Y.empty() || InsideRelation(object->id,task.Y[0]->id)==UNKNOWN))', 1)
    s = s.replace('               small->location == location &&\n               (small->inside == NONE || small->inside == UNKNOWN);',
                  '               small->location == location;')
    s = s.replace('return hold_id == NONE && small->inside == static_cast<int>(b);',
                  'return hold_id == NONE && InsideRelation(a,b,true)==1;')
    # A location observation cannot refute a persistent inside edge.
    a=s.index('void RDFW::ReconcileLocationRelation');b=s.index('// A successful container action',a)
    s=s[:a]+'''void RDFW::ReconcileLocationRelation(const shared_ptr<SmallObject>&) {
    // SDK explicit at and inside are independent, including after movement.
}

'''+s[b:]
    a=s.index('    for (const auto& item : container->smallObjectsInside)',s.index('void RDFW::ConfirmContainerLocation'))
    b=s.index('\nbool RDFW::TakeOut',a)
    s=s[:a]+'}\n'+s[b:]
    for name, next_name in [('TakeOut','PutIn'),('PutIn','Close'),('FromPlate','ToPlate'),('ToPlate','PutDown'),('PutDown','PickUp'),('PickUp','Move')]:
        a=s.index('bool RDFW::'+name+'(');b=s.index('bool RDFW::'+next_name+'(',a+1)
        block=s[a:b]
        block=block.replace('        ClearContainerMembership(small);\n','').replace('            ClearContainerMembership(small);\n','')
        block=block.replace('        StageStateValue(StateField::INSIDE,small->id,NONE);\n','').replace('            StageStateValue(StateField::INSIDE,small->id,NONE);\n','')
        block=block.replace('        StageStateValue(StateField::INSIDE,small->id,b);\n','')
        block=block.replace('        SetInsideEvidence(a, true, EvidenceSource::ACTION_SUCCESS);\n','')
        if name=='TakeOut':
            block=block.replace('        SetHold(small);', '        SetInsideRelation(a,b,0,true,EvidenceSource::ACTION_SUCCESS);\n        SetHold(small);',1)
        elif name=='PutIn':
            block=block.replace('        small->on = NONE;', '        SetInsideRelation(a,b,1,true,EvidenceSource::ACTION_SUCCESS);\n        small->on = NONE;',1)
        elif name=='FromPlate':
            block=block.replace('    const std::vector<unsigned int> arguments{a};', '''    const std::vector<unsigned int> arguments{a};
    const bool empty_hand_before = FactValue(StateField::HOLD)==NONE;''',1)
            block=block.replace('    fromplate_cons[a]=0;\n    return 0;', '''    if (empty_hand_before) {
        auto& p=MutableProvenance(StateField::INSIDE,a);
        const bool new_exclusion=!(p.storage_exclusion & 2u);
        p.storage_exclusion |= 2u;
        if (plate_id==static_cast<int>(a)) {
            active_mutation->storage(); plate.reset(); plate_id=UNKNOWN;
            UpdateProvenance(StateField::PLATE,0,UNKNOWN,false,EvidenceSource::ACTION_FAILURE);
        }
        if(new_exclusion) {++p.revision; ++world_revision;}
        LOG("[SlotFeedback] FromPlate(%u)=false with confirmed empty hand: tray!=item\\n",a);
    }
    return 0;''',1)
        s=s[:a]+block+s[b:]
    s=s.replace('        ConfirmContainerLocation(container);\n        SetContainerEvidence',
                '        SetHold(nullptr); // Successful Open/Close proves an empty hand.\n        ConfirmContainerLocation(container);\n        SetContainerEvidence')
    s=s.replace('std::chrono::milliseconds(300), plan_safety_margin)) return false;\n    if (!PickUp(a) && !FromPlate(a)) return false;\n    return PutDown(a) && IsNotStoredFact(a);', '''std::chrono::milliseconds(200), plan_safety_margin)) return false;
    if (FromPlate(a)) return PutDown(a) && IsNotStoredFact(a);
    return IsNotStoredFact(a);''',1)
    # Initial positive inside entries are additive, not conflicting scalar votes.
    a=s.index('            if (!ReceiveWeakClaim(StateField::INSIDE, index,');b=s.index('\n        }',a)
    s=s[:a]+'''            SetInsideRelation(index,container_id,1,stage==1,EvidenceSource::INITIAL);'''+s[b:]
    s=s.replace('if (!plated || plate_id == hold_id)', 'if (!plated)')
    # Do not overwrite an independent explicit initial at with a container's at.
    s=s.replace('                const int container_fact = FactLocation(p->id);',
                '                if (s->id<score_locations.size() && score_locations[s->id]!=UNKNOWN) continue;\n                const int container_fact = FactLocation(p->id);',1)
    # Complete reliable initial domain allows absent edges to be known false.
    s=s.replace('    if (valid_facts == 0) {', '''    if(stage==1) for(const auto& item:smallObjects)
        MutableProvenance(StateField::INSIDE,item->id).inside_complete=true;
    if (valid_facts == 0) {''',1)
    # Instruction info is a claim, not a physical slot/containment transition.
    a=s.index('    else if (behave == "inside" || behave == "in")',s.index('void RDFW::ParseInfo'))
    b=s.index('\n    else',a+10)
    block=s[a:b]
    begin=block.index('            ClearContainerMembership(p);')
    block=block[:begin]+'''            SetInsideRelation(p->id,cId,1,stage==1,EvidenceSource::EXPLICIT_INFO);
        }
    }'''
    s=s[:a]+block+s[b:]
    # Sense absence at an observed open container proves only this edge absent.
    s=s.replace('ApplyStateValue(StateField::INSIDE,small,UNKNOWN,false,EvidenceSource::SENSE);',
                'SetInsideRelation(small,cont,0,true,EvidenceSource::SENSE);',1)
    # Remove stale equality conflicts from the weak-reply filter.
    s=s.replace('(small && FactInside(id)!=UNKNOWN && FactInside(id)!=inside)',
                '(small && relation=="inside" && InsideRelation(id,target)==0)')
    return s


def canonical(s):
    s=s.replace('return FactInside(x) != UNKNOWN && FactInside(x) == static_cast<int>(y);','return InsideRelation(x,y)==1;')
    s=s.replace('return FactInside(x) != UNKNOWN && FactInside(x) != static_cast<int>(y);','return InsideRelation(x,y)==0;')
    s=s.replace('        ClearContainerMembership(item);\n        StageStateValue(field,id,value);','''        if (value>0) {
            SetInsideRelation(id,value,1,verified,source);
            return;
        }
        ClearContainerMembership(item);
        StageStateValue(field,id,value);''',1)
    s=s.replace('        out << "];";', '''        out << "];" << p.inside_complete << '{';
        for(const auto& edge:p.inside_edges)
            out << edge.first << ':' << edge.second.value << ':' << edge.second.verified
                << ':' << int(edge.second.source) << ',';
        out << "};";''',1)
    a=s.index('        if (IsStoredFact(id)) {');b=s.index('\n    }\n    for (StateField',a)
    s=s[:a]+'''        if (IsStoredFact(id) && (!small || FactLocation(id)!=FactLocation(0)))
            issue(id,"stored location");
        if (cont) for (auto item:cont->smallObjectsInside)
            if (!item || InsideRelation(item->id,cont->id,true)!=1) issue(id,"membership cache");'''+s[b:]
    return s


def terminal(s):
    s=s.replace('if (!small || !y || !(insideValue(small)!=UNKNOWN)) return TerminalStatus::UNKNOWN;\n        return boolStatus(insideValue(small) == y->id);', '''if (!small || !y) return TerminalStatus::UNKNOWN;
        const int edge=world.InsideRelation(small->id,y->id,hypothesis);
        return edge==UNKNOWN?TerminalStatus::UNKNOWN:boolStatus(edge==1);''')
    s=s.replace('if (!small || !y || !(insideValue(small)!=UNKNOWN)) return TerminalStatus::UNKNOWN;\n        return boolStatus(insideValue(small) != y->id);', '''if (!small || !y) return TerminalStatus::UNKNOWN;
        const int edge=world.InsideRelation(small->id,y->id,hypothesis);
        return edge==UNKNOWN?TerminalStatus::UNKNOWN:boolStatus(edge==0);''')
    return s


def journal(s):
    s=s.replace('            p.supporting_constraints.clear();', '''            p.supporting_constraints.clear();p.inside_complete=false;
            for(auto& edge:p.inside_edges) edge.second.verified=false;''',1)
    return s


def legacy(s):
    marker='    if (!instruction.IsUsable() || instruction.X.empty())'
    s=s.replace(marker,'    if (!hypothesis) return TerminalChecker().evaluateTask(world,instruction);\n'+marker,1)
    s=s.replace('if (!small || !y || !isInsideKnown(world, small, hypothesis)) return TerminalStatus::UNKNOWN;\n        return boolStatus((hypothesis?small->inside:world.FactInside(small->id)) == y->id);', '''if (!small || !y) return TerminalStatus::UNKNOWN;
        const int edge=world.InsideRelation(small->id,y->id,hypothesis);
        return edge==UNKNOWN?TerminalStatus::UNKNOWN:boolStatus(edge==1);''')
    s=s.replace('if (!small || !y || !isInsideKnown(world, small, hypothesis)) return TerminalStatus::UNKNOWN;\n        return boolStatus((hypothesis?small->inside:world.FactInside(small->id)) != y->id);', '''if (!small || !y) return TerminalStatus::UNKNOWN;
        const int edge=world.InsideRelation(small->id,y->id,hypothesis);
        return edge==UNKNOWN?TerminalStatus::UNKNOWN:boolStatus(edge==0);''')
    return s


if __name__ == '__main__':
    for name,fn in [('rdfw.hpp',header),('rdfw.cpp',cpp),('canonical_state.cpp',canonical),
                    ('terminal_checker.cpp',terminal),('state_mutation.cpp',journal),('legacy_priority.cpp',legacy)]:
        edit(name,fn)
