from implement_relations import edit

def cpp(s):
    s=s.replace('    // Reserve the longer feedback branch: PickUp fails on tray=A, then\n    // FromPlate succeeds. Both branches end with PutDown at this location.', '    // Reserve the longer branch: tray=A uses FromPlate+PutDown; otherwise\n    // confirmed empty hand makes FromPlate=false an item-specific exclusion.')
    s=s.replace('    if(stage==1) for(const auto& item:smallObjects)\n        MutableProvenance(StateField::INSIDE,item->id).inside_complete=true;', '''    // Build every cache edge after all forward type declarations, including
    // stored objects. Cache membership never upgrades evidence.
    for(const auto& item:smallObjects) {
        const auto& edges=Provenance(StateField::INSIDE,item->id).inside_edges;
        for(const auto& edge:edges) if(edge.second.value==1) {
            const auto c=dynamic_pointer_cast<Container>(GetObject(edge.first));
            if(c && std::none_of(c->smallObjectsInside.begin(),c->smallObjectsInside.end(),
                    [&](const shared_ptr<SmallObject>& v){return v && v->id==item->id;}))
                AddContainerMembership(c,item);
        }
        if(stage==1) MutableProvenance(StateField::INSIDE,item->id).inside_complete=true;
    }''')
    # The reply supplies a weak routing representative, not exclusive membership.
    a=s.index('    if (small->inside > 0 && static_cast<size_t>(small->inside) < objects.size()) {',s.index('bool RDFW::GetSmallObjectStatus'))
    b=s.index('    if (chosen_relation == "inside") {',a)
    s=s[:a]+'    // A noisy reply cannot remove independent containment edges.\n\n'+s[b:]
    return s

edit('rdfw.cpp',cpp)
edit('tests/official_relation_feedback_tests.cpp',lambda s:s.replace('    assert(w->ParseEnv((test<=1?slots:', '    std::string input_common=common;\n    if(test==1) input_common.erase(input_common.find("(type 4 container) "),19);\n    assert(w->ParseEnv((test<=1?slots:').replace('+common+door+edges));','+input_common+door+edges+(test==1?"(type 4 container) ":"")));',1))
