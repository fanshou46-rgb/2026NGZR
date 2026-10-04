from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]/'src1.7.7'
def change(name,old,new):
    p=ROOT/name;b=p.read_bytes();ending='\r\n' if b.count(b'\r\n')>b.count(b'\n')/2 else '\n'
    s=b.decode('utf8').replace('\r\n','\n');assert old in s,(name,old[:70]);s=s.replace(old,new)
    p.write_bytes(s.replace('\n',ending).encode('utf8'))
change('tests/sanitize_probe.sh','rdfw176-sanitizer-nopie','rdfw177-sanitizer-nopie')
change('tests/run_probe_compare.py',"BASELINE = ROOT / 'src1.7.5'","BASELINE = ROOT / 'src1.7.6'")
change('state_mutation.cpp','p.supporting_constraints.clear();p.inside_complete=false;',
       'p.supporting_constraints.clear();p.inside_complete=false;p.explicit_at=UNKNOWN;')
change('canonical_state.cpp','int RDFW::ScoreFactLocation(unsigned int id) const {','''int RDFW::ExplicitAt(unsigned int id) const {
    if(!IsValidObjectId(id))return UNKNOWN;
    if(!dynamic_cast<SmallObject*>(objects[id].get()))return FactLocation(id);
    return Provenance(StateField::LOCATION,id).explicit_at;
}

int RDFW::ScoreFactLocation(unsigned int id) const {''')
change('canonical_state.cpp','out << "];" << p.inside_complete << \'{\';',
       'out << "];" << p.explicit_at << ":" << p.inside_complete << \'{\';')
change('rdfw.cpp','    if (stage == 1) {\n        if (score_locations.size() < objects.size())',
       '    if (stage == 1 || stage == 2) {\n        if (score_locations.size() < objects.size())')
change('rdfw.cpp','    if (performed != "Sense" && performed != "AskLoc") {','''    const auto explicit_at=[&](unsigned id,int at) {
        if(!IsValidObjectId(id))return;
        active_mutation->touch(id);
        auto& p=MutableProvenance(StateField::LOCATION,id);
        if(p.explicit_at!=at) {p.explicit_at=at;++p.revision;}
    };
    if(performed=="Move") {
        if(hold_id>0)explicit_at(hold_id,location);
        if(plate_id>0)explicit_at(plate_id,location);
    } else if(!arguments.empty()) {
        if(performed=="PutIn")explicit_at(arguments[0],NONE);
        else if(performed=="PickUp" || performed=="TakeOut" || performed=="PutDown" ||
                performed=="ToPlate" || performed=="FromPlate" || performed=="Open" || performed=="Close")
            explicit_at(arguments[0],location);
    }
    if (performed != "Sense" && performed != "AskLoc") {''')
start=(ROOT/'rdfw.cpp').read_text(encoding='utf8').index('void RDFW::DryRunSenseIds(')
s=(ROOT/'rdfw.cpp').read_text(encoding='utf8');end=s.index('\n/**',start)
change('rdfw.cpp',s[start:end],'''void RDFW::DryRunSenseIds(std::vector<unsigned int>& sensed_ids) const {
    sensed_ids.clear();if(location<0)return;
    for(unsigned id=1;id<objects.size();++id) {
        if(!objects[id])continue;
        const auto small=dynamic_pointer_cast<SmallObject>(objects[id]);
        if(!small) {if(objects[id]->location==location)sensed_ids.push_back(id);continue;}
        const int at=ExplicitAt(id);
        bool visible=(at!=UNKNOWN?at==location:
            small->inside<=0 && objects[id]->location==location);
        visible|=hold_id==int(id) || plate_id==int(id);
        for(unsigned parent=1;parent<objects.size() && !visible;++parent) {
            const auto c=dynamic_pointer_cast<Container>(objects[parent]);
            if(c && InsideRelation(id,parent,true)==1 && c->isOpen==1 && c->location==location)visible=true;
        }
        if(visible)sensed_ids.push_back(id);
    }
}
''')
change('rdfw.cpp','    if (valid_facts == 0) {','''    if(stage==1) for(unsigned id=1;id<objects.size();++id) if(objects[id]) {
        auto& p=MutableProvenance(StateField::LOCATION,id);
        p.explicit_at=id<score_locations.size() && score_locations[id]!=UNKNOWN?score_locations[id]:NONE;
    }
    if (valid_facts == 0) {''')
change('rdfw.cpp','out << ":score_locations:";', '''out << ":explicit_at:";
    for(unsigned id=1;id<objects.size();++id) if(objects[id])out << id << ',' << ExplicitAt(id) << ';';
    out << ":score_locations:";''')
change('answer_planning.cpp','        if(small) {\n            if(h.first==\'i\')', '''        if(small) {
            // Scenario-only explicit at. Public answers never write this fact.
            MutableProvenance(StateField::LOCATION,id).explicit_at=h.first=='a'?destination:NONE;
            if(h.first=='i')''')
change('answer_planning.cpp','key<<":edges:"<<id', 'key<<":explicit_at:"<<ExplicitAt(id);\n        key<<":edges:"<<id')
