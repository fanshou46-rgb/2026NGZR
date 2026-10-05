#include "episode_routes.hpp"
#include "physical_route_view.hpp"
#include <cassert>
#include <cmath>
#include <iostream>
#include <sstream>
using namespace _home;
namespace {
void samePolicy(const std::shared_ptr<EpisodePolicy>& a,const std::shared_ptr<EpisodePolicy>& b) {
    assert(a->stop==b->stop);
    if(a->stop)return;
    assert(a->action.kind==b->action.kind && a->action.a==b->action.a && a->action.b==b->action.b && a->action.duration==b->action.duration);
    assert(a->children.size()==b->children.size() && a->probabilities.size()==b->probabilities.size());
    for(const auto& edge:a->children) {
        assert(b->children.count(edge.first));
        assert(std::abs(a->probabilities.at(edge.first)-b->probabilities.at(edge.first))<1e-12);
        samePolicy(edge.second,b->children.at(edge.first));
    }
}
std::string bytes(const EpisodeBelief& belief) {
    std::ostringstream s;s.precision(17);
    for(const auto& state:belief.support()) {
        const auto& w=state.episode.world;
        s<<physicalEpisodeSignature(state.episode)<<'/'<<state.weight<<'/'<<w.answer_order_seed<<'/'<<w.answer_order_assumed;
        for(const auto& f:w.initial_reply_counts)s<<'/'<<f.first.first<<f.first.second<<':'<<f.second;
        s<<'|';
    }
    return s.str();
}
EpisodePlan compare(const EpisodeBelief& belief,const SdkEpisodeModel& model,const std::vector<EpisodeRoute>& routes,
    const std::vector<JointAction>& info,const AskObservationModel& ask) {
    const auto before=bytes(belief);
    const auto plain=EpisodeRouteSearch::solve(belief,model,routes,info,ask,std::chrono::milliseconds(10000),1000000,std::chrono::milliseconds(1000),false);
    const auto shared=EpisodeRouteSearch::solve(belief,model,routes,info,ask,std::chrono::milliseconds(10000),1000000,std::chrono::milliseconds(1000),true);
    assert(!plain.work_cut && !plain.wall_cut && !shared.work_cut && !shared.wall_cut);
    assert(std::abs(plain.value.lower-shared.value.lower)<1e-12 && std::abs(plain.value.upper-shared.value.upper)<1e-12);
    samePolicy(plain.policy,shared.policy);assert(bytes(belief)==before);
    return shared;
}
}
int main() {
    SdkEpisode initial;auto& w=initial.world;w.robot=1;w.locations={1,2,3};
    w.objects[2]=JointObject(false,true,1);w.objects[3]=JointObject(true,false,1);
    w.objects[4]=JointObject(false,false,2);w.objects[5]=JointObject(false,true,2);w.freezeSdkReplyDomain();
    SdkEpisodeModel model;model.goals={SdkPredicate{"puton",{{3,4}}}};
    const auto ask=AskObservationModel({{'a',1},{'a',2},{'a',3},{'i',2},{'i',5}},.6,.3,.1,0).withPersistentAnswerOrderPrior();
    const EpisodeRoute delivery={{JointActionKind::PICKUP,3},{JointActionKind::MOVE,2},{JointActionKind::SENSE},{JointActionKind::PUTDOWN,3}};
    std::vector<WeightedEpisode> copies;
    for(unsigned i=0;i<64;++i) {
        auto e=initial;e.world.answer_order_seed=i;e.world.answer_order_assumed=true;
        e.world.initial_reply_counts[{'a',1}]+=i;e.world.initial_reply_counts[{'i',2}]+=i;
        copies.push_back({e,1.0+i});
    }
    const EpisodeBelief belief(copies);const auto before=bytes(belief);
    assert(PhysicalRouteView::make(belief).physical_worlds==1);
    for(unsigned repeat=0;repeat<50;++repeat) {
        auto plan=compare(belief,model,{delivery},{},ask);
        assert(plan.transitions==4 && plan.value.lower==31 && plan.physical_view_inputs==64 && plan.physical_view_worlds==1);
        const auto plain=EpisodeRouteSearch::solve(belief,model,{delivery},{},ask,std::chrono::milliseconds(10000),1000000,std::chrono::milliseconds(1000),false);
        assert(plain.transitions==256);
    }
    // Histories and SDK map feasibility are part of physical scoring identity.
    std::vector<WeightedEpisode> variants={{initial,1}};
    auto add=[&](const SdkEpisode& e){variants.push_back({e,1});};
    auto e=initial;e.world.robot=2;add(e);e=initial;e.world.hand=3;add(e);
    e=initial;e.world.plate=3;add(e);e=initial;e.world.hand=e.world.plate=3;add(e);
    e=initial;e.world.objects[3].at=2;add(e);e=initial;e.world.objects[3].inside={2,5};add(e);
    e=initial;e.world.objects[3].inside={2};add(e);e=initial;e.world.objects[2].opened=true;add(e);
    e=initial;e.world.objects[4].container=true;add(e);e=initial;e.world.locations.insert(4);add(e);
    e=initial;e.world.initial_reply_counts.erase({'a',2});add(e);
    e=initial;e.world.initial_reply_counts[{'a',4}]=0;add(e);e=initial;e.world.initial_reply_counts.clear();add(e);
    e=initial;e.world.objects[6]=JointObject(true,false,1);add(e);e=initial;e.world.objects[3].small=false;add(e);
    e=initial;e.paid=1;add(e);
    assert(PhysicalRouteView::make(EpisodeBelief(variants)).physical_worlds==variants.size());
    compare(EpisodeBelief(variants),model,{delivery},{},ask);
    SdkEpisodeModel ledger=model;ledger.constraints={{SdkPredicate{"inside",{{3,2}}},false}};
    auto untouched=initial;untouched.credits={true};untouched.world.objects[3].inside={2};untouched.world.objects[2].opened=true;
    auto lost=untouched;lost.credits={false};
    EpisodeBelief histories({{untouched,.5},{lost,.5}});
    assert(PhysicalRouteView::make(histories).physical_worlds==2);
    // Initially forbidden inside may be removed by the first physical action.
    const EpisodeRoute remove={{JointActionKind::TAKEOUT,3,2},{JointActionKind::MOVE,2},{JointActionKind::SENSE},{JointActionKind::PUTDOWN,3}};
    auto restoration=compare(histories,ledger,{delivery,remove},{},ask);
    assert(!restoration.policy->stop && restoration.policy->action.kind==JointActionKind::TAKEOUT);
    // Preserve answer selectors/frequency mixtures: aggregation is NOT valid
    // for ASK even when every physical/ledger field matches.
    auto hidden=copies;for(auto& state:hidden)state.episode.world.objects[3].inside={2,5};
    const EpisodeBelief multiple(hidden);auto collapsed=PhysicalRouteView::make(multiple);
    assert(collapsed.physical_worlds==1);
    auto real=multiple.branches(model,{JointActionKind::ASK,3},ask);
    auto wrong=collapsed.belief.branches(model,{JointActionKind::ASK,3},ask);
    bool difference=real.size()!=wrong.size();
    for(const auto& a:real)for(const auto& b:wrong)if(!(a.observation<b.observation)&&!(b.observation<a.observation))
        difference|=std::abs(a.probability-b.probability)>1e-9;
    assert(difference); // the test would catch accidentally replacing replay
    compare(multiple,model,{delivery},{{JointActionKind::ASK,3},{JointActionKind::SENSE}},ask);
    const EpisodeRoute ask_route={{JointActionKind::ASK,3},{JointActionKind::PICKUP,3},{JointActionKind::MOVE,2},{JointActionKind::SENSE},{JointActionKind::PUTDOWN,3}};
    auto fallback=compare(multiple,model,{ask_route},{},ask);
    assert(fallback.physical_view_inputs==0 && fallback.physical_view_worlds==0);
    assert(bytes(belief)==before && belief.support().size()==64);
    bool residual_rejected=false,miss_rejected=false;
    try{PhysicalRouteView::make(EpisodeBelief({{initial,1}},.1));}catch(const std::logic_error&){residual_rejected=true;}
    EpisodeBelief missed({{initial,1}});JointObservation impossible;impossible.success=true;
    assert(missed.observe(model,{JointActionKind::MOVE,1},impossible,ask,99)==EpisodeUpdate::SUPPORT_MISS);
    try{PhysicalRouteView::make(missed);}catch(const std::logic_error&){miss_rejected=true;}
    assert(residual_rejected && miss_rejected); // aggregation cannot repair unknown support
    std::cout<<"50 full-policy/value equivalences: 64x physical work reduction; all histories/map/slot/containment counterexamples and full ASK distribution retained\n";
}
