from implement_relations import edit

def containment(s):
    s=s.replace('    // Keep one representative for old route construction.', '''    // A new weak edge cannot demote an already qualified scalar resolution,
    // including a constraint-derived one with live dependencies.
    if(!verified && ResolvedState(StateField::INSIDE,id).present) {
        if(changed) ++p.revision;
        return;
    }
    // Keep one representative for old route construction.''')
    s=s.replace('representative==UNKNOWN || item.first==container ||\n           (item.second.verified && !representative_verified)', 'representative==UNKNOWN || (item.second.verified && !representative_verified) ||\n           (item.second.verified==representative_verified && item.first==container)')
    return s
edit('containment.cpp',containment)

def cpp(s):
    a=s.index('    if (IsInsideVerified(a)) {',s.index('bool RDFW::GetSmallObjectStatus'))
    b=s.index('    if (IsInsideVerified(a) && IsLocationVerified(a)) return true;',a)
    s=s[:a]+'''    // at and multiple inside edges can coexist. Only a confirmed negative
    // edge contradicts an inside answer; another positive parent does not.
    if(chosen_relation=="inside" && InsideRelation(a,chosen_target)==0) {
        LOG(YELLOW "AskLoc(%u) conflicts with confirmed negative edge; ignored\\n" RESET,a);
        return false;
    }
    if (chosen_relation=="at" && IsLocationVerified(a) &&
        FactLocation(a)!=static_cast<int>(chosen_target)) {
        LOG(YELLOW "AskLoc(%u) conflicts with trusted at; ignored\\n" RESET,a);
        return false;
    }
'''+s[b:]
    a=s.index('    // A noisy reply cannot remove independent containment edges.',a)
    b=s.index('    if (location_conflict) MarkUnresolved',a)
    s=s[:a]+'''    const bool trusted_inside=IsInsideVerified(a);
    const auto& inside_record=Provenance(StateField::INSIDE,a);
    const bool independent_inside=inside_record.inside_complete ||
        std::any_of(inside_record.inside_edges.begin(),inside_record.inside_edges.end(),
            [](const std::pair<const unsigned,InsideEdge>& edge){return edge.second.verified;});
    // A noisy reply supplies a route hint without overwriting independent facts.
    if (chosen_relation == "inside") {
        auto cont=dynamic_pointer_cast<Container>(objects[chosen_target]);
        if (!cont) return false;
        if (cont->location==UNKNOWN) GetBigObjectStatus(cont->id);
        if (!IsLocationVerified(a)) StageStateValue(StateField::LOCATION,a,cont->location);
        SetInsideRelation(a,cont->id,1,false,EvidenceSource::ASK_ANSWER);
    } else {
        if (!EnsureLocationCapacity(static_cast<int>(chosen_target))) return false;
        if (!IsLocationVerified(a)) StageStateValue(StateField::LOCATION,a,static_cast<int>(chosen_target));
        if (!trusted_inside) StageStateValue(StateField::INSIDE,a,NONE);
    }
    if (!IsLocationVerified(a)) MarkDirectLocationEvidence(a,false,EvidenceSource::ASK_ANSWER);
    if (!trusted_inside) SetInsideEvidence(a,false,EvidenceSource::ASK_ANSWER);
'''+s[b:]
    s=s.replace('    if (inside_conflict) MarkUnresolved(StateField::INSIDE, a);','    if (inside_conflict && !independent_inside) MarkUnresolved(StateField::INSIDE, a);',1)
    return s
edit('rdfw.cpp',cpp)
edit('tests/CMakeLists.txt',lambda s:s.replace('add_executable(state_profile state_profile.cpp)', '''add_executable(relation_evidence_tests relation_evidence_tests.cpp)
target_link_libraries(relation_evidence_tests rdfw_test_core)
target_compile_options(relation_evidence_tests PRIVATE -UNDEBUG)
foreach(case RANGE 0 3)
    add_test(NAME relation_evidence_${case} COMMAND relation_evidence_tests "${CMAKE_CURRENT_BINARY_DIR}/words.txt" ${case})
endforeach()
add_executable(state_profile state_profile.cpp)''',1))
