#include "rdfw.hpp"
#include "joint_world.hpp"
#include <algorithm>
using namespace _home;

ProbabilityBounds RDFW::VisibilityProbability(unsigned id,int target,unsigned opened) {
    ProbabilityBounds unknown;
    if(!IsValidObjectId(id) || target<0)return unknown;
    const bool small=bool(dynamic_pointer_cast<SmallObject>(objects[id]));
    const int at=ExplicitAt(id);
    if(at==target || (small && IsStoredFact(id))) {
        ProbabilityBounds certain;certain.lower=certain.upper=1;certain.residual=0;return certain;
    }
    if(!small && at!=UNKNOWN) {
        ProbabilityBounds certain;certain.lower=certain.upper=0;certain.residual=0;return certain;
    }
    // The legacy distribution supplies reference hypotheses, not exclusive
    // physical locations. Every scene adds all independent positive edges.
    std::map<LocationHypothesis,double> prior=BeliefFor(id).distribution();
    if(at!=UNKNOWN) {prior.clear();prior[{'a',at}]=1;}
    std::vector<std::pair<LocationHypothesis,double>> ranked(prior.begin(),prior.end());
    std::sort(ranked.begin(),ranked.end(),[](const std::pair<LocationHypothesis,double>&a,
        const std::pair<LocationHypothesis,double>&b){return a.second!=b.second?a.second>b.second:a.first<b.first;});
    std::vector<WeightedJointWorld> support;double covered=0;
    for(const auto& h:ranked) {
        if(support.size()>=32)break; // omitted mass goes to residual, never renormalized away
        if(h.second<=0 || (h.first.first!='a' && h.first.first!='i'))continue;
        if(h.first.first=='i' && (!small || InsideRelation(id,h.first.second)==0))continue;
        JointWorld scene;scene.robot=target;scene.locations.insert(target);
        scene.hand=FactValue(StateField::HOLD)>0?FactValue(StateField::HOLD):0;
        scene.plate=FactValue(StateField::PLATE)>0?FactValue(StateField::PLATE):0;
        for(unsigned j=1;j<objects.size();++j) if(objects[j]) {
            const auto c=dynamic_pointer_cast<Container>(objects[j]);
            int loc=FactLocation(j);if(loc==UNKNOWN)loc=objects[j]->location;
            if(loc>=0)scene.locations.insert(loc);
            scene.objects[j]=JointObject(bool(dynamic_pointer_cast<SmallObject>(objects[j])),bool(c),loc>=0?loc:-1,0,c && c->isOpen==1);
        }
        auto& object=scene.objects[id];
        object.at=at!=UNKNOWN?(at<0?-1:at):h.first.first=='a'?h.first.second:-1;
        if(object.at>=0)scene.locations.insert(object.at);
        if(h.first.first=='i') {
            auto c=scene.objects.find(h.first.second);
            if(c==scene.objects.end() || !c->second.container)continue;
            object.inside.insert(h.first.second);
        }
        double coverage=1;
        if(small) {
            const auto& edges=Provenance(StateField::INSIDE,id);
            for(const auto& e:edges.inside_edges)
                if(InsideRelation(id,e.first)==1)object.inside.insert(e.first);
            // Unknown coexistence and unknown target slot membership stay in
            // residual support; these are declared prior assumptions, not fits.
            if(!edges.inside_complete)coverage*=.75;
            if(FactValue(StateField::HOLD)==UNKNOWN || FactValue(StateField::PLATE)==UNKNOWN)coverage*=.75;
        }
        for(unsigned parent:object.inside) {
            auto& c=scene.objects.at(parent);
            if(FactLocation(parent)==UNKNOWN)coverage*=.5;
            if(parent!=opened && FactContainerState(parent)==UNKNOWN)coverage*=.5;
        }
        const double weight=h.second*coverage;
        try {scene.validate();}
        catch(const std::invalid_argument&) {continue;} // invalid public support remains residual
        covered+=weight;support.push_back({std::move(scene),weight});
    }
    JointBelief belief(std::move(support),std::max(0.0,1-covered));
    // Condition the finite scenes on still-current public ID observations.
    // Zero covered likelihood leaves residual=1, explicitly exposing a support
    // miss instead of manufacturing a certain posterior or a canonical fact.
    for(unsigned loc=0;loc<posSensedFlag.size();++loc) if(posSensedFlag[loc]) {
        const bool seen=HasObjectAtLocation(loc,id);
        belief.condition([&](const JointWorld& state) {
            JointWorld observed=state;observed.robot=loc;observed.locations.insert(loc);
            return (observed.visible().count(id)!=0)==seen?1.0:0.0;
        });
    }
    return belief.probabilityBounds([&](const JointWorld& state){
        JointWorld scene=state;
        if(opened && scene.objects.count(opened))scene.objects[opened].opened=true;
        return scene.visible().count(id)!=0;
    });
}
