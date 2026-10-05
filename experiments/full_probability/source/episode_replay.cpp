#include "episode_replay.hpp"
#include <stdexcept>
using namespace _home;
namespace {
bool same(const JointObservation& a,const JointObservation& b) {return !(a<b)&&!(b<a);}
bool same(const JointAction& a,const JointAction& b) {
    return a.kind==b.kind && a.a==b.a && a.b==b.b && a.duration==b.duration;
}
}
EpisodeUpdate EpisodeReplay::observe(const SdkEpisodeModel& model,const JointAction& action,
    const JointObservation& observation,const AskObservationModel& ask,std::size_t receipt) {
    if(!receipt)throw std::invalid_argument("missing execution receipt");
    for(const auto& event:history)if(event.receipt==receipt) {
        if(!same(event.action,action)||!same(event.observation,observation))
            throw std::invalid_argument("receipt reused for different public evidence");
        return EpisodeUpdate::DUPLICATE;
    }
    if(!history.empty() && receipt<=history.back().receipt)
        throw std::invalid_argument("out-of-order execution feedback");
    if(!current.modelValid())throw std::logic_error("repair before accepting another action");
    auto result=current.observe(model,action,observation,ask,receipt);
    history.push_back({receipt,action,observation});
    return result;
}
EpisodeRepairResult EpisodeReplay::repair(const SdkEpisodeModel& model,const AskObservationModel& ask,
    const std::vector<WeightedEpisode>& initial,std::size_t cap,std::chrono::milliseconds wall) {
    if(!cap || wall.count()<=0)throw std::invalid_argument("invalid repair budget");
    EpisodeRepairResult result;
    const auto end=std::chrono::steady_clock::now()+wall;
    for(const auto& scene:initial) {
        if(scene.episode.paid!=0 || scene.episode.credits.size()!=model.constraints.size())
            throw std::invalid_argument("repair requires initial unpaid episodes");
        for(bool credit:scene.episode.credits)if(!credit)
            throw std::invalid_argument("repair cannot install a pre-damaged initial ledger");
    }
    // Work is bounded over all candidate scenes and received actions. No paid
    // command is repeated on the physical robot during this computation.
    std::vector<WeightedEpisode> survivors;
    for(const auto& scene:initial) {
        EpisodeBelief replay({scene});bool consistent=true;double mass=scene.weight;
        for(const auto& event:history) {
            if(result.transitions>=cap){result.work_cut=true;result.reason="repair_work_budget";return result;}
            if(std::chrono::steady_clock::now()>=end){result.wall_cut=true;result.reason="repair_wall_budget";return result;}
            ++result.transitions;
            double probability=0;
            try {
                probability=replay.conditionPublicFeedback(model,event.action,event.observation,ask);
            } catch(const std::logic_error&) {result.reason="unmodeled_observation_order";return result;}
            if(probability<=0){consistent=false;break;}
            // Carry likelihood of the complete public history, not just the
            // last answer. Relative weights are unnormalized until installation.
            mass*=probability;
        }
        if(!consistent)continue;
        if(replay.support().size()!=1)throw std::logic_error("singleton replay unexpectedly branched");
        if(mass>0)survivors.push_back({replay.support().front().episode,mass});
    }
    if(survivors.empty()){result.reason="no_initial_scene_explains_public_history";return result;}
    current=EpisodeBelief(std::move(survivors));result.installed=true;result.reason="replayed_all_paid_evidence";
    return result;
}
