"""SDK-backed fixture migration; preserves untouched line bytes."""
from implement_relations import edit

def main():
    def cpp(s):
        s=s.replace('// location was misleading. Its contents inherit that location only with the\n// strength of their own inside evidence.', '// location was misleading. Contents receive a route hint only; this does not\n// prove their independent SDK at relation.')
        at='    MarkDirectLocationEvidence(container->id, true);\n}'
        s=s.replace(at,'''    MarkDirectLocationEvidence(container->id, true);
    for(const auto& object:objects) {
        const auto small=dynamic_pointer_cast<SmallObject>(object);
        if(!small || InsideRelation(small->id,container->id,true)!=1 ||
           FactLocation(small->id)!=UNKNOWN || score_locations[small->id]!=UNKNOWN) continue;
        const auto source=LocationSource(small->id);
        StageStateValue(StateField::LOCATION,small->id,location);
        MarkDirectLocationEvidence(small->id,false,source);
    }
}''',1)
        s=s.replace('            ClearContainerMembership(small);\n            if (hold_id == small->id) SetHold(nullptr, EvidenceSource::EXPLICIT_INFO);\n            SetPlate(small, EvidenceSource::EXPLICIT_INFO);\n            SetInsideEvidence(small->id, stage == 1, EvidenceSource::EXPLICIT_INFO);','            SetPlate(small, EvidenceSource::EXPLICIT_INFO);')
        return s
    edit('rdfw.cpp',cpp)
    def answer(s):
        a=s.index('        // A visible object next to an open container');b=s.index('        if (container) {',a)
        s=s[:a]+'        // ID visibility cannot prove any negative containment edge.\n'+s[b:]
        anchor='    for(std::size_t i=0;i<tasks.size();++i) key'
        a=s.index(anchor)
        s=s[:a]+'''    for(unsigned id=1;id<objects.size();++id) if(objects[id]) {
        const auto& p=Provenance(StateField::INSIDE,id);
        key<<":edges:"<<id<<':'<<p.inside_complete<<':'<<p.storage_exclusion;
        for(const auto& e:p.inside_edges)
            key<<':'<<e.first<<','<<e.second.value<<','<<e.second.verified<<','<<int(e.second.source);
    }
'''+s[a:];return s
    edit('answer_planning.cpp',answer)
    edit('probe_layer.cpp',lambda s:s.replace("    out << ':' << w.DependenciesCurrent(key.first,key.second) << ';';",'''    out << ':' << w.DependenciesCurrent(key.first,key.second) << ';';
    if(key.first==StateField::INSIDE) {
        out<<"edges:"<<p.inside_complete<<':'<<p.storage_exclusion;
        for(const auto& e:p.inside_edges)
            out<<':'<<e.first<<','<<e.second.value<<','<<e.second.verified<<','<<int(e.second.source);
        out<<';';
    }'''))
    edit('tests/official_relation_feedback_tests.cpp',lambda s:s.replace('    static bool act(', '    static std::size_t revision(const RDFW& w) {return w.world_revision;}\n    static bool act(').replace('w->DebugCaptureProjection(true)','w->debug_capture_projection=true').replace('w->StateVersion()','ScoreSemanticsTestAccess::revision(*w)'))
    edit('tests/CMakeLists.txt',lambda s:s.replace('\nendif()\n\nadd_executable(canonical_state_tests', '''
    add_executable(official_relation_feedback_tests official_relation_feedback_tests.cpp)
    target_compile_options(official_relation_feedback_tests PRIVATE -UNDEBUG)
    target_include_directories(official_relation_feedback_tests BEFORE PRIVATE stubs "${SOURCE_DIR}" "${OFFICIAL_SDK}/src" "${OFFICIAL_SDK}/include")
    target_link_libraries(official_relation_feedback_tests rdfw_test_core "${OFFICIAL_SDK}/lib/libasp.so")
    foreach(case RANGE 0 5)
        add_test(NAME official_relation_feedback_${case} COMMAND official_relation_feedback_tests "${CMAKE_CURRENT_BINARY_DIR}/words.txt" ${case})
        set_tests_properties(official_relation_feedback_${case} PROPERTIES WORKING_DIRECTORY "${SDK_TEST_WORK}" RUN_SERIAL TRUE)
    endforeach()
endif()

add_executable(canonical_state_tests''',1))
    edit('tests/official_placement_recovery_tests.cpp',lambda s:s.replace('    std::vector<bool> feedback;ok=sdk.EvaluatePickUp(3);feedback.push_back(ok);\n    if(!ok) {ok=sdk.EvaluateFromPlate(3);feedback.push_back(ok);assert(ok);}\n    ok=sdk.EvaluatePutDown(3);feedback.push_back(ok);assert(ok);','    std::vector<bool> feedback;ok=sdk.EvaluateFromPlate(3);feedback.push_back(ok);\n    if(ok) {ok=sdk.EvaluatePutDown(3);feedback.push_back(ok);assert(ok);}'))
    edit('tests/canonical_state_tests.cpp',lambda s:s.replace('w->FactInside(3)==NONE && w->FactLocation(3)==1','w->InsideRelation(3,2)==UNKNOWN && s->inside==2 && w->FactLocation(3)==1').replace('        fact(StateField::INSIDE,3,1); // human is not a container\n        assert(w->FactInside(3)==UNKNOWN && !w->DebugStateConsistency().empty());','        const auto before=w->DebugStateSnapshot();\n        fact(StateField::INSIDE,3,1); // reject invalid target rather than corrupt state\n        assert(w->InsideRelation(3,1)==UNKNOWN && w->DebugStateSnapshot()==before);\n        assert(w->DebugStateConsistency().empty());'))
    edit('tests/canonical_baseline_probe.cpp',lambda s:s.replace('w->SetHold(s);assert(w->ResolvedState(StateField::INSIDE,3).present);','w->SetHold(s);assert(!w->ResolvedState(StateField::INSIDE,3).present);\n        assert(w->InsideRelation(3,2)==UNKNOWN && s->inside==2);'))
    edit('tests/state_layer_tests.cpp',lambda s:s.replace('        assert(s->inside==UNKNOWN);\n        assert(w->HasContradictoryEvidence(StateField::INSIDE,3));\n    } else if (test == 14)', '        assert(w->InsideRelation(3,1)==UNKNOWN); // human cannot qualify an edge\n        assert(w->InsideRelation(3,2,true)==1); // unrelated hint survives\n    } else if (test == 14)'))
    def invariant(s):
        s=s.replace('assert(s->inside==NONE && c->smallObjectsInside.empty());','assert(s->inside==2 && c->smallObjectsInside.size()==1);\n        assert(w->InsideRelation(3,2)==UNKNOWN);',1)
        s=s.replace('assert(!w->hold && s->inside==NONE);','assert(!w->hold && s->inside==2 && c->smallObjectsInside.size()==1);',1)
        s=s.replace('assert(c->smallObjectsInside.empty() && d->smallObjectsInside.size()==1);','assert(c->smallObjectsInside.size()==1 && d->smallObjectsInside.size()==1);',1)
        s=s.replace('assert(d->smallObjectsInside.empty());','assert(c->smallObjectsInside.size()==1 && d->smallObjectsInside.size()==1);',1)
        return s
    edit('tests/state_invariant_tests.cpp',invariant)
    def mutation(s):
        a=s.index('        // Failed platform returns never');b=s.index('\n    unsigned failures=',a)
        return s[:a]+'''        // A negative public response can teach a precondition, without changing
        // physical state or the constraint ledger. Empty hand isolates tray!=3.
        auto w=World(argv[1]);w->SetActionResults({false});auto before=w->DebugStateSnapshot();
        assert(!ScoreSemanticsTestAccess::Action(*w,test-5));
        if(test==9) {
            assert(w->FactValue(StateField::HOLD)==NONE && w->FactValue(StateField::PLATE)==NONE);
            assert(w->InsideRelation(3,2)==1 && w->IsNotStoredFact(3));
            assert(w->location==1 && w->constraint_eligible.empty());
        } else assert(w->DebugStateSnapshot()==before);
        return 0;
    }
'''+s[b:]
    edit('tests/mutation_failure_tests.cpp',mutation)

if __name__=='__main__':main()
