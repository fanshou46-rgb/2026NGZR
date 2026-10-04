from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]/'src1.7.7'
def change(name,old,new):
    p=ROOT/name;b=p.read_bytes();ending='\r\n' if b.count(b'\r\n')>b.count(b'\n')/2 else '\n'
    s=b.decode('utf8').replace('\r\n','\n');assert old in s,(name,old[:70]);p.write_bytes(s.replace(old,new).replace('\n',ending).encode('utf8'))
s=(ROOT/'probe_layer.cpp').read_text(encoding='utf8');start=s.index('double RDFW::ProbeProbability(');end=s.index('\nstd::size_t RDFW::LegacyBlockedProposal',start)
change('probe_layer.cpp',s[start:end],'''double RDFW::ProbeProbability(const ProbeCandidate& p) {
    if(p.kind==ProbeKind::ASK_LOCATION)return .6;
    std::set<unsigned> ids;for(const auto& f:p.facts)ids.insert(f.object_id);
    double result=0;
    for(unsigned id:ids)result=std::max(result,VisibilityProbability(id,p.target_location,
        p.kind==ProbeKind::OPEN_AND_SENSE?p.target_object:0).lower);
    return result;
}
''')
change('probe_layer.cpp',"        if(inside>0) belief.confirm({'i',inside});\n        else if(loc!=UNKNOWN", "        if(inside<=0 && loc!=UNKNOWN")
change('probe_layer.cpp','p.information_estimate=ProbeProbability(p);','''p.information_estimate=ProbeProbability(p);
        p.probability_upper=0;p.residual_mass=0;
        std::set<unsigned> forecast_ids;
        for(const auto& f:p.facts)forecast_ids.insert(f.object_id);
        for(unsigned id:forecast_ids) {
            const auto bound=VisibilityProbability(id,p.target_location,p.kind==ProbeKind::OPEN_AND_SENSE?p.target_object:0);
            p.probability_upper=std::min(1.0,p.probability_upper+bound.upper);
            p.residual_mass=std::max(p.residual_mass,bound.residual);
        }''')
old='''            for(auto id:physical.lost_goals) {
                if (id<tasks.size() && tasks[id].behave=="goto" && !tasks[id].X.empty() &&
                    FactLocation(tasks[id].X[0]->id)!=UNKNOWN) {
                    cost+=4; next+=std::chrono::milliseconds(120);
                } else unrecoverable_goal_loss+=40;
            }'''
new='''            // Returning later is not an executable policy here. Price every
            // certain lost goal now; do not replace -40 by an optimistic Move4.
            unrecoverable_goal_loss=40*static_cast<int>(physical.lost_goals.size());
            p.terminal_goal_loss=unrecoverable_goal_loss;'''
change('probe_layer.cpp',old,new)
change('probe_layer.cpp','<< ",\\\"answer_branches_evaluated\\\":"', '''<< ",\\\"probability_upper\\\":" << p->probability_upper
            << ",\\\"residual_mass\\\":" << p->residual_mass
            << ",\\\"terminal_goal_loss\\\":" << p->terminal_goal_loss
            << ",\\\"answer_branches_evaluated\\\":"''')
# Public ID visibility is a union of explicit at, slots, and ALL opened parents.
# Keep route alternatives compatible with coexistence. Absence can still rule
# out an explicit at or an opened-parent witness, irrespective of other edges.
change('belief_state.hpp','const std::map<int,std::pair<int,int>>& containers);','const std::map<int,std::pair<int,int>>& containers, bool coexistence=false);')
change('belief_state.cpp','const std::map<int,std::pair<int,int>>& containers) {','const std::map<int,std::pair<int,int>>& containers, bool coexistence) {')
change('belief_state.cpp',"if(h.first=='a') contradicted=visible!=(h.second==location);", "if(h.first=='a') contradicted=visible?(!coexistence && h.second!=location):h.second==location;")
change('belief_state.cpp','if(visible) contradicted=(at>=0 && at!=location) || opened==0;', 'if(visible) contradicted=!coexistence && ((at>=0 && at!=location) || opened==0);')
change('rdfw.cpp','std::find(sensed_ids.begin(),sensed_ids.end(),id)!=sensed_ids.end(),containers);','std::find(sensed_ids.begin(),sensed_ids.end(),id)!=sensed_ids.end(),containers,true);')
