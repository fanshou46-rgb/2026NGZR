#include "episode_router.hpp"
#include <cassert>
#include <iostream>
#include <sstream>
using namespace _home;
namespace {
std::vector<std::string> routes(const EpisodeProposalBatch& batch) {
    std::vector<std::string> result;
    for(const auto& route:batch.routes) {
        std::ostringstream s;int fee=0;
        for(const auto& a:route){s<<int(a.kind)<<','<<a.a<<','<<a.b<<','<<a.duration.count()<<';';fee+=a.cost();}
        s<<'/'<<fee;result.push_back(s.str());
    }
    return result;
}
std::string beliefBytes(const EpisodeBelief& belief) {
    std::ostringstream s;s.precision(17);
    for(const auto& state:belief.support()) {
        const auto& e=state.episode;const auto& w=e.world;
        s<<state.weight<<':'<<e.paid<<':'<<w.robot<<','<<w.hand<<','<<w.plate<<','<<w.answer_order_seed<<','<<w.answer_order_assumed<<';';
        for(bool c:e.credits)s<<c;s<<';';
        for(int loc:w.locations)s<<loc<<',';s<<';';
        for(const auto& item:w.objects) {
            const auto& o=item.second;s<<item.first<<':'<<o.small<<','<<o.container<<','<<o.at<<','<<o.opened<<':';
            for(unsigned parent:o.inside)s<<parent<<',';s<<';';
        }
        for(const auto& entry:w.initial_reply_counts)s<<entry.first.first<<','<<entry.first.second<<':'<<entry.second<<';';
        s<<'|';
    }
    return s.str();
}
}
int main() {
    SdkEpisode initial;auto& w=initial.world;w.robot=1;w.locations={1,2,3};
    w.objects[1]=JointObject(false,false,3);w.objects[2]=JointObject(false,true,1);
    w.objects[3]=JointObject(true,false,1);w.objects[4]=JointObject(true,false,2);
    w.objects[5]=JointObject(false,true,2);w.objects[6]=JointObject(false,false,3);
    w.objects[7]=JointObject(true,false,1);w.objects[8]=JointObject(true,false,1);w.objects[9]=JointObject(true,false,3);
    w.freezeSdkReplyDomain();
    SdkEpisodeModel model;
    model.goals={SdkPredicate{"putin",{{7,2}}},SdkPredicate{"putin",{{8,2}}},
        SdkPredicate{"puton",{{4,6}}},SdkPredicate{"puton",{{3,5}}},SdkPredicate{"close",{{2,0}}},
        SdkPredicate{"pickup",{{9,0}}},SdkPredicate{"goto",{{1,0}}}};
    model.constraints={{SdkPredicate{"inside",{{7,2}}},false},{SdkPredicate{"pickup",{{7,0}}},false}};
    initial.credits={true,true};
    std::vector<WeightedEpisode> copies;
    for(unsigned i=0;i<64;++i) {
        auto state=initial;state.world.answer_order_seed=i;state.world.answer_order_assumed=bool(i%2);
        // These differ for ASK / terminal reward, but not for Builder's
        // physical routes. Keep the first episode unchanged for the greedy
        // ledger proposal; other proposals never inspect credits or paid.
        if(i){state.paid=i;state.credits={bool(i%2),bool(i%3)};
            state.world.initial_reply_counts[{'a',1}]+=i;
            state.world.initial_reply_counts[{'i',2}]+=i;}
        copies.push_back({state,1.0+i});
    }
    EpisodeBelief many(copies),one({{initial,1}});
    const auto before=beliefBytes(many);
    for(unsigned repeat=0;repeat<50;++repeat) {
        const auto single=EpisodeRouter::propose(one,model,4096,std::chrono::milliseconds(1000));
        const auto reused=EpisodeRouter::propose(many,model,4096,std::chrono::milliseconds(1000));
        assert(!single.work_cut && !single.wall_cut && !reused.work_cut && !reused.wall_cut);
        assert(single.physical_worlds==1 && single.reused_worlds==0);
        assert(reused.physical_worlds==1 && reused.reused_worlds==63);
        assert(single.transitions==reused.transitions && routes(single)==routes(reused));
        assert(beliefBytes(many)==before && many.support().size()==64);
    }
    // Separately change every dynamic / visibility / map field. No merging
    // is permitted, even when the bounded catalogue cannot yet exploit it.
    std::vector<WeightedEpisode> variants={{initial,1}};
    auto add=[&](const SdkEpisode& e){e.world.validate();variants.push_back({e,1});};
    auto e=initial;e.world.robot=2;add(e);
    e=initial;e.world.hand=3;add(e);
    e=initial;e.world.plate=3;add(e);
    e=initial;e.world.objects[3].at=2;add(e);
    e=initial;e.world.objects[3].inside={2,5};add(e);
    e=initial;e.world.objects[3].inside={2};add(e);
    e=initial;e.world.objects[2].opened=true;add(e);
    e=initial;e.world.objects[6].container=true;add(e);
    e=initial;e.world.locations.insert(4);add(e);
    e=initial;e.world.initial_reply_counts.erase({'a',2});add(e);
    e=initial;e.world.initial_reply_counts[{'a',4}]=0;add(e); // presence defines legal Move even with count 0
    e=initial;e.world.initial_reply_counts.clear();add(e); // fallback map, no frozen reply pool
    e=initial;e.world.objects[10]=JointObject(true,false,1);add(e);
    e=initial;e.world.objects[9].small=false;add(e);
    auto distinct=EpisodeRouter::propose(EpisodeBelief(variants),model,4096,std::chrono::milliseconds(1000));
    assert(distinct.physical_worlds==variants.size() && distinct.reused_worlds==0);
    // Identical object poses but different initial loc facts must retain
    // both feasibility alternatives. This must hold after map freezing.
    SdkEpisode map;map.world.robot=0;map.world.locations={0,1};map.world.objects[3]=JointObject(true,false,1);
    map.world.freezeSdkReplyDomain();auto blocked=map;blocked.world.initial_reply_counts.erase({'a',1});
    SdkEpisodeModel pickup;pickup.goals={SdkPredicate{"pickup",{{3,0}}}};
    auto batch=EpisodeRouter::propose(EpisodeBelief({{blocked,.5},{map,.5}}),pickup,4096,std::chrono::milliseconds(1000));
    assert(batch.physical_worlds==2 && batch.reused_worlds==0);
    bool reachable=false;
    for(const auto& route:batch.routes)if(!route.empty() && route.front().kind==JointActionKind::MOVE && route.front().a==1)reachable=true;
    assert(reachable);
    std::cout<<"50 repeats: 64 selector/weight/ledger worlds reuse one physical catalogue; all belief bytes retained, 15 distinct physical/map variants separated\n";
}
