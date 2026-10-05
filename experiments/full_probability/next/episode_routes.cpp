#include "episode_routes.hpp"
#include <stdexcept>
using namespace _home;
namespace {
struct RouteSearch {
    const SdkEpisodeModel& model;const AskObservationModel& ask;
    const std::vector<EpisodeRoute>& routes;
    std::size_t limit,work=0;std::chrono::steady_clock::time_point end;
    bool work_cut=false,wall_cut=false,complete=true;
    using Value=std::pair<SdkRewardBounds,std::shared_ptr<EpisodePolicy>>;
    RouteSearch(const SdkEpisodeModel& m,const AskObservationModel& a,
        const std::vector<EpisodeRoute>& r,std::size_t cap,std::chrono::steady_clock::time_point deadline)
        :model(m),ask(a),routes(r),limit(cap),end(deadline) {}
    bool exhausted() {
        if(work>=limit)work_cut=true;
        if(std::chrono::steady_clock::now()>=end)wall_cut=true;
        return work_cut||wall_cut;
    }
    Value stop(const EpisodeBelief& b) {return {b.reward(model),std::make_shared<EpisodePolicy>()};}
    bool allowed(const EpisodeBelief& b) {
        if(exhausted())return false;
        if(b.support().size()>limit-work){work_cut=true;return false;}
        work+=b.support().size();return true;
    }
    Value route(const EpisodeBelief& b,const EpisodeRoute& actions,std::size_t step,std::chrono::milliseconds left) {
        auto incumbent=stop(b);
        if(step>=actions.size() || actions[step].duration>left || !allowed(b))return incumbent;
        std::vector<EpisodeBranch> branches;
        try{branches=b.branches(model,actions[step],ask);}catch(const std::logic_error&){complete=false;return incumbent;}
        auto policy=std::make_shared<EpisodePolicy>();policy->stop=false;policy->action=actions[step];
        SdkRewardBounds value;
        for(const auto& branch:branches) {
            const bool physical=branch.observation.kind==JointObservation::Kind::FEEDBACK;
            auto child=physical && !branch.observation.success?stop(branch.posterior):
                route(branch.posterior,actions,step+1,left-actions[step].duration);
            policy->children.emplace(branch.observation,child.second);
            value.lower+=branch.probability*child.first.lower;value.upper+=branch.probability*child.first.upper;
        }
        // Compare the entire remaining tail with stopping at this PUBLIC
        // observation. Negative intermediate prefixes are allowed when their
        // completed restoration wins; a known-useless failed probe is pruned.
        return value.lower>incumbent.first.upper+1e-9?Value{value,policy}:incumbent;
    }
    Value bestRoute(const EpisodeBelief& b,std::chrono::milliseconds left) {
        auto best=stop(b);
        for(const auto& actions:routes) {
            if(exhausted())break;
            auto candidate=route(b,actions,0,left);
            if(candidate.first.lower>best.first.upper+1e-9)best=std::move(candidate);
        }
        return best;
    }
};
}
EpisodePlan EpisodeRouteSearch::solve(const EpisodeBelief& b,const SdkEpisodeModel& m,
    const std::vector<EpisodeRoute>& routes,const std::vector<JointAction>& observations,
    const AskObservationModel& ask,std::chrono::milliseconds left,std::size_t cap,std::chrono::milliseconds wall) {
    if(!cap || wall.count()<=0 || left.count()<0)throw std::invalid_argument("invalid route budget");
    for(const auto& route:routes) {
        if(route.size()>64)throw std::invalid_argument("route exceeds bounded stack");
        for(const auto& action:route)if(action.duration.count()<0)throw std::invalid_argument("negative action duration");
    }
    for(const auto& action:observations)if((action.kind!=JointActionKind::SENSE && action.kind!=JointActionKind::ASK)||action.duration.count()<0)
        throw std::invalid_argument("invalid information catalogue");
    RouteSearch search(m,ask,routes,cap,std::chrono::steady_clock::now()+wall);
    auto best=search.bestRoute(b,left);
    for(const auto& action:observations) {
        if(action.duration>left || !search.allowed(b))continue;
        std::vector<EpisodeBranch> branches;
        try{branches=b.branches(m,action,ask);}catch(const std::logic_error&){search.complete=false;continue;}
        auto policy=std::make_shared<EpisodePolicy>();policy->stop=false;policy->action=action;
        SdkRewardBounds value;
        for(const auto& branch:branches) {
            auto child=search.bestRoute(branch.posterior,left-action.duration);
            policy->children.emplace(branch.observation,child.second);
            value.lower+=branch.probability*child.first.lower;value.upper+=branch.probability*child.first.upper;
        }
        if(value.lower>best.first.upper+1e-9)best={value,policy};
    }
    EpisodePlan result;result.policy=best.second;result.value=best.first;result.transitions=search.work;
    result.work_cut=search.work_cut;result.wall_cut=search.wall_cut;result.support_complete=search.complete;
    return result;
}
