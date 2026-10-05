"""One-time scoped edits for 1.6.6; fail on an unexpected baseline."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=root/'rdfw.cpp'; s=p.read_text(encoding='utf-8')
def edit(old,new,count=1):
    global s
    assert s.count(old)==count,(old[:90],s.count(old),count)
    s=s.replace(old,new)
edit('[PlannerVersion] 1.6.5','[PlannerVersion] 1.6.6')
edit('        stage = 1;\n        const TerminalSummary initial_hypothesis = terminal_checker.evaluateAll(*this);\n        stage = 2;', '        const TerminalSummary initial_hypothesis = terminal_checker.evaluatePlanningHypothesis(*this);')
edit('    UpdateProvenance(StateField::HOLD, 0, hold_id, verified, source);\n    if (old_plate', '    UpdateProvenance(StateField::HOLD, 0, hold_id, verified, source);\n    if (item) {\n        ClearContainerMembership(item);\n        MarkDirectLocationEvidence(item->id, verified, source);\n        SetInsideEvidence(item->id, verified, source);\n    }\n    if (old_plate')
edit('    UpdateProvenance(StateField::PLATE, 0, plate_id, verified, source);\n}', '    UpdateProvenance(StateField::PLATE, 0, plate_id, verified, source);\n    if (item) {\n        ClearContainerMembership(item);\n        MarkDirectLocationEvidence(item->id, verified, source);\n        SetInsideEvidence(item->id, verified, source);\n    }\n}',2)
edit('    p.supporting_constraints.clear();\n}\n\nvoid RDFW::UpdateProvenance', '    p.supporting_constraints.clear();\n    if (field == StateField::LOCATION) { objectLocationVerified[id]=false; objectLocationSource[id]=EvidenceSource::UNKNOWN; }\n    if (field == StateField::INSIDE) { objectInsideVerified[id]=false; objectInsideSource[id]=EvidenceSource::UNKNOWN; }\n    if (field == StateField::CONTAINER_STATE) { containerStateVerified[id]=false; containerStateSource[id]=EvidenceSource::UNKNOWN; }\n}\n\nvoid RDFW::UpdateProvenance')
edit('    if (p.resolved_value != value || p.resolved_source != source ||', '''    // Historical contradictions are retained; a strong new observation resolves
    // the current state. Weak conflicting claims cannot independently resolve it.
    if (!verified && stage == 2 && !derived && HasContradictoryEvidence(field,id)) {
        value = UNKNOWN; source = EvidenceSource::UNKNOWN;
    }
    if (p.resolved_value != value || p.resolved_source != source ||''')
edit('    p.resolved_verified = verified;\n}', '''    p.resolved_verified = verified && value != UNKNOWN && source != EvidenceSource::CONSTRAINT_HEURISTIC;
    // Compatibility arrays mirror metadata; they never grant fact eligibility.
    if (field == StateField::LOCATION) { objectLocationVerified[id]=p.resolved_verified; objectLocationSource[id]=source; }
    if (field == StateField::INSIDE) { objectInsideVerified[id]=p.resolved_verified; objectInsideSource[id]=source; }
    if (field == StateField::CONTAINER_STATE) { containerStateVerified[id]=p.resolved_verified; containerStateSource[id]=source; }
}''')
edit('    const StateProvenance& p = Provenance(field, id);\n    if (!p.resolved_verified', '''    StageTimer timer(StageTiming::CANONICAL_QUERY);
    if ((field == StateField::HOLD || field == StateField::PLATE) ? id != 0 :
        (id >= objects.size() || !objects[id])) return StateClaim();
    const StateProvenance& p = Provenance(field, id);
    if (p.resolved_source == EvidenceSource::UNKNOWN ||
        p.resolved_source == EvidenceSource::CONSTRAINT_HEURISTIC) return StateClaim();
    if (!p.resolved_verified''')
edit('    const StateProvenance& p = Provenance(field, id);\n    for (const std::size_t index : p.supporting_constraints)', '    const StateProvenance& p = Provenance(field, id);\n    if (p.dependency_count > 2) return false;\n    for (const std::size_t index : p.supporting_constraints)')
edit('        if (support.revision != d.revision || support.resolved_value != d.value)', '''        if (!support.resolved_verified || support.resolved_value == UNKNOWN ||
            support.resolved_source == EvidenceSource::CONSTRAINT_HEURISTIC ||
            support.resolved_source == EvidenceSource::UNKNOWN ||
            support.revision != d.revision || support.resolved_value != d.value)''')
for name,field,array in [('Location','LOCATION','objectLocationVerified'),('Inside','INSIDE','objectInsideVerified'),('ContainerState','CONTAINER_STATE','containerStateVerified')]:
    edit(f'    return id < {array}.size() && {array}[id] &&\n        DependenciesCurrent(StateField::{field}, id);',f'    return ResolvedState(StateField::{field}, id).present;')
# Fact-completion shortcuts: value and qualification now share one source.
edit('if (IsInsideVerified(a)) return true;', 'if (FactValue(StateField::HOLD) == static_cast<int>(a)) return true;')
edit('plate_id == static_cast<int>(a) && !IsInsideVerified(a)', 'plate_id == static_cast<int>(a) && FactValue(StateField::PLATE) != static_cast<int>(a)')
edit('if(hold_id==a||plate_id==a) return true;', 'if(TaskFactSatisfied("pickup",a)) return true;')
edit('if(hold_id==a ||plate_id==a) return true;', 'if(TaskFactSatisfied("pickup",a)) return true;')
edit('if(hold_id!=a&&plate_id!=a) return true;', 'if(TaskFactSatisfied("putdown",a)) return true;')
edit('if (stage == 1 && small->inside == NONE) return true;', 'if (stage == 1 && TaskFactSatisfied("putdown",a)) return true;')
edit('if (stage == 2 && IsInsideVerified(a) && IsLocationVerified(a) && small->inside == NONE)', 'if (stage == 2 && TaskFactSatisfied("putdown",a) && FactLocation(a) != UNKNOWN)')
edit('if(location==objects[a]->location){\n        return true;', 'if(TaskFactSatisfied("goto",a)){\n        return true;')
edit('if(location==objects[a]->location && IsLocationVerified(a)) return true;', 'if(TaskFactSatisfied("goto",a)) return true;')
edit('if(cnt->isOpen && (stage == 1 || IsContainerStateVerified(a))) return true;', 'if(TaskFactSatisfied("open",a)) return true;',2)
edit('if(!cnt->isOpen && (stage == 1 || IsContainerStateVerified(a))) return true;', 'if(TaskFactSatisfied("close",a)) return true;',2)
edit('if(objects[a]->location==human->location && plate_id!=a && hold_id!=a) return true;', 'if(TaskFactSatisfied("give",a,human->id)) return true;')
edit('if(Isinside(a,b) && (stage == 1 || IsInsideVerified(a))) return true;', 'if(TaskFactSatisfied("putin",a,b)) return true;',2)
edit('if(Isinside(a,b)==0) return true;', 'if(TaskFactSatisfied("takeout",a,b)) return true;')
edit('if (stage == 1 && small->inside != target_cont->id && small->inside != UNKNOWN)', 'if (stage == 1 && TaskFactSatisfied("takeout",a,b))')
edit('if (!Isinside(a,b) && IsInsideVerified(a)) return true;', 'if (TaskFactSatisfied("takeout",a,b)) return true;')
edit('    return true; //小物体不在容器里了', '    return TaskFactSatisfied("takeout",a,b); // 未验证的非 inside 不是完成事实')
edit('if(small && small->inside==NONE && small->location==objects[b]->location &&\n       plate_id!=a && hold_id!=a &&\n       (stage == 1 || (IsInsideVerified(a) && IsLocationVerified(a) && IsLocationVerified(b))))', 'if(TaskFactSatisfied("puton",a,b))')
edit('stage == 2 && (!IsLocationVerified(b) || objects[b]->location != location)', 'stage == 2 && (FactLocation(b) == UNKNOWN || FactLocation(b) != FactLocation(0))')
edit('if (!target_cont->isOpen || !IsContainerStateVerified(cont)) return false;', 'if (FactContainerState(cont) != 1) return false;')
# Trusted reads protecting state and selecting direct anchors.
edit('if (small->inside != answer_inside)', 'if (FactInside(a) != answer_inside)')
edit('if (objects[a]->location != answer_location)', 'if (FactLocation(a) != answer_location)')
edit('if (objects[a]->location != static_cast<int>(chosen_location))', 'if (FactLocation(a) != static_cast<int>(chosen_location))')
edit('if (objectLocationVerified[id] && !objectLocationInferredByMustNear[id])', 'if (FactLocation(id) == loc && !objectLocationInferredByMustNear[id])')
edit('(direct_votes.empty() || objectLocationVerified[id])', '(direct_votes.empty() || FactLocation(id) == chosen_location)')
edit('if (objectLocationVerified[id] && !objectLocationInferredByMustNear[id] &&', 'if (FactLocation(id) != UNKNOWN && !objectLocationInferredByMustNear[id] &&')
edit('(objectLocationVerified[id] || !anchored)', '(FactLocation(id) == chosen_location || !anchored)')
edit('if (IsLocationVerified(item->id) && !IsInsideVerified(item->id) &&\n            item->location != location)', 'if (FactLocation(item->id) != UNKNOWN && FactInside(item->id) == UNKNOWN &&\n            FactLocation(item->id) != location)')
edit('if (small && small->inside > 0 && IsInsideVerified(a) &&\n            HasObjectAtLocation(location, small->inside)) {\n            small->location = location;\n            MarkDirectLocationEvidence(a, true, EvidenceSource::SENSE);', '''if (small && FactInside(a) > 0 &&
            HasObjectAtLocation(location, FactInside(a))) {
            ApplyStateValue(StateField::LOCATION,a,location,true,EvidenceSource::RELATION_DERIVED);
            DependOn(StateField::LOCATION,a,StateField::INSIDE,a);
            DependOn(StateField::LOCATION,a,StateField::LOCATION,FactInside(a));''',2)
# Sense visibility is a proof decision, not a navigation hypothesis.
edit('visible_container_is_open = visible_container && visible_container->isOpen != 0;', 'visible_container_is_open = visible_container && FactContainerState(sensed_container_id) != 0;')
edit('container_is_open = cont->isOpen == 1;', 'container_is_open = FactContainerState(sensed_container_id) == 1;')
# Missing dependencies in the second Sense pipeline; observe container first.
edit('            if (objects[id]->location != location) {', '            const bool moved = objects[id]->location != location;\n            ApplyStateValue(StateField::LOCATION,id,location,true,EvidenceSource::SENSE);\n            if (moved) {')
edit('                                         : EvidenceSource::CONSTRAINT_HEURISTIC);\n                        }', '                                         : EvidenceSource::CONSTRAINT_HEURISTIC);\n                            DependOn(StateField::LOCATION,sp->id,StateField::INSIDE,sp->id);\n                            DependOn(StateField::LOCATION,sp->id,StateField::LOCATION,id);\n                        }')
# Missing invalidation and reset.
edit('            smObj->location = UNKNOWN;\n            // 同时', '            smObj->location = UNKNOWN;\n            SetInsideEvidence(x,false,EvidenceSource::UNKNOWN);\n            MarkDirectLocationEvidence(x,false,EvidenceSource::UNKNOWN);\n            // 同时')
edit('    preflight_report = QuestionPreflightReport();\n    cout', '    preflight_report = QuestionPreflightReport();\n    holdProvenance=StateProvenance(); plateProvenance=StateProvenance();\n    cout')
edit('        if (index > 0)\n            MarkDirectLocationEvidence(index, stage == 1, EvidenceSource::INITIAL);', '        MarkDirectLocationEvidence(index, index == 0 || stage == 1, EvidenceSource::INITIAL);')
edit('    location = a;\n    if (hold)', '    ApplyStateValue(StateField::LOCATION,0,a,true,EvidenceSource::ACTION_SUCCESS);\n    if (hold)')
# Header comments are adjusted separately. Guard comparison includes canonical metadata.
edit('    out << location <<', '    out << DebugStateSnapshot() << "|canonical|";\n    out << location <<')
# Candidate evidence sources are metadata snapshots, not compatibility truth.
for array,field in [('objectLocationSource','LOCATION'),('objectInsideSource','INSIDE'),('containerStateSource','CONTAINER_STATE')]:
    edit(f'if (i < {array}.size() &&\n            {array}[i] != EvidenceSource::UNKNOWN)',f'if (Provenance(StateField::{field},i).resolved_source != EvidenceSource::UNKNOWN)')
    edit(f'fact.source = EvidenceName({array}[i]);',f'fact.source = EvidenceName(Provenance(StateField::{field},i).resolved_source);')
edit('    return evidence;\n}', '''    for (StateField f : {StateField::HOLD,StateField::PLATE}) {
        CandidateEvidence e; e.object_id=0; e.fact=f==StateField::HOLD?"hold":"plate";
        e.source=EvidenceName(Provenance(f,0).resolved_source); e.verified=ResolvedState(f,0).present;
        evidence.push_back(e);
    }
    return evidence;
}''')
p.write_text(s,encoding='utf-8')
for p in [root/'CMakeLists.txt',root/'tests/CMakeLists.txt']:
    text=p.read_text(encoding='utf-8').replace('1.6.5','1.6.6').replace('rdfw.cpp','canonical_state.cpp rdfw.cpp')
    # paths in local test target must both remain relative to tests.
    text=text.replace('../canonical_state.cpp rdfw.cpp','../canonical_state.cpp ../rdfw.cpp')
    p.write_text(text,encoding='utf-8')
for name in ['run_release_matrix.py','run_state_matrix.py']:
    p=root/'tests'/name; p.write_text(p.read_text(encoding='utf-8').replace('src1.6.5','src1.6.6'),encoding='utf-8')
