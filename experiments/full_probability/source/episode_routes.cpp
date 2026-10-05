#include "episode_routes.hpp"
#include <algorithm>
#include <stdexcept>
using namespace _home;
namespace {
struct RouteSearch {
    const SdkEpisodeModel& model;const AskObservationModel& ask;
    const std::vector<EpisodeRoute>& routes;
    std::size_t limit,work=0;std::chrono::steady_clock::time_point end;
    bool work_cut=false,wall_cut=false,complete=true,candidate_truncated=false;
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
        if(step>=actions.size())return incumbent;
        if(actions[step].duration>left || !allowed(b)){candidate_truncated=true;return incumbent;}
        std::vector<EpisodeBranch> branches;
        try{branches=b.branches(model,actions[step],ask);}catch(const std::logic_error&){complete=false;return incumbent;}
        auto policy=std::make_shared<EpisodePolicy>();policy->stop=false;policy->action=actions[step];
        SdkRewardBounds value;
        for(const auto& branch:branches) {
            const bool physical=branch.observation.kind==JointObservation::Kind::FEEDBACK;
            auto child=physical && !branch.observation.success?stop(branch.posterior):
                route(branch.posterior,actions,step+1,left-actions[step].duration);
            policy->children.emplace(branch.observation,child.second);
            policy->probabilities.emplace(branch.observation,branch.probability);
            value.lower+=branch.probability*child.first.lower;value.upper+=branch.probability*child.first.upper;
        }
        // Compare the entire remaining tail with stopping at this PUBLIC
        // observation. Negative intermediate prefixes are allowed when their
        // completed restoration wins; a known-useless failed probe is pruned.
        const bool mandatory_sense=actions[step].kind==JointActionKind::SENSE && step>0 &&
            (actions[step-1].kind==JointActionKind::MOVE || actions[step-1].kind==JointActionKind::OPEN);
        return mandatory_sense || value.lower>incumbent.first.upper+1e-9?Value{value,policy}:incumbent;
    }
    Value bestRoute(const EpisodeBelief& b,std::chrono::milliseconds left) {
        auto best=stop(b);
        std::vector<std::size_t> order(routes.size());
        std::vector<double> priorities(routes.size(),0);
        for(std::size_t i=0;i<routes.size();++i) {
            order[i]=i;
            if(b.support().empty())continue;
            int arrival=b.support().front().episode.world.robot;int prefix=0;
            for(const auto& action:routes[i]) {
                prefix+=action.cost();if(action.kind==JointActionKind::MOVE)arrival=int(action.a);
                if(action.kind!=JointActionKind::PICKUP && action.kind!=JointActionKind::TAKEOUT && action.kind!=JointActionKind::FROMPLATE)continue;
                double available=0;
                for(const auto& state:b.support()) {
                    const auto& w=state.episode.world;bool present=false;
                    if(action.kind==JointActionKind::PICKUP)present=w.atLocation(action.a,arrival);
                    else if(action.kind==JointActionKind::FROMPLATE)present=w.plate==action.a;
                    else present=w.atLocation(action.b,arrival) && w.objects.at(action.a).inside.count(action.b);
                    if(present)available+=state.weight;
                }
                priorities[i]=available*40-prefix;break;
            }
        }
        // This is a cheap PUBLIC-posterior ordering hint only. Eligibility and
        // value still come from complete whole-belief route evaluation below.
        std::stable_sort(order.begin(),order.end(),[&](std::size_t a,std::size_t c){
            if(priorities[a]!=priorities[c])return priorities[a]>priorities[c];
            return routes[a].size()<routes[c].size();
        });
        for(auto id:order) {
            if(exhausted())break;
            candidate_truncated=false;
            auto candidate=route(b,routes[id],0,left);
            if(!candidate_truncated && candidate.first.lower>best.first.upper+1e-9)best=std::move(candidate);
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
    const auto end=std::chrono::steady_clock::now()+wall;
    // A direct-route catalogue cannot consume the observation candidates'
    // reserved work. Each observation gets a deterministic fair work slice.
    RouteSearch search(m,ask,routes,observations.empty()?cap:std::max(std::size_t(1),cap/2),observations.empty()?end:end-wall/2);
    auto best=search.bestRoute(b,left);
    std::size_t work=search.work,remaining=observations.size();
    bool work_cut=search.work_cut,wall_cut=search.wall_cut,complete=search.complete;
    for(const auto& action:observations) {
        if(work>=cap){work_cut=true;break;}
        const auto slice=std::max(std::size_t(1),(cap-work)/remaining--);
        RouteSearch information(m,ask,routes,slice,end);
        if(action.duration>left || !information.allowed(b)) {
            work_cut|=information.work_cut;wall_cut|=information.wall_cut;continue;
        }
        std::vector<EpisodeBranch> branches;
        try{branches=b.branches(m,action,ask);}catch(const std::logic_error&){complete=false;work+=information.work;continue;}
        std::stable_sort(branches.begin(),branches.end(),[](const EpisodeBranch& a,const EpisodeBranch& b){return a.probability>b.probability;});
        auto policy=std::make_shared<EpisodePolicy>();policy->stop=false;policy->action=action;
        SdkRewardBounds value;
        for(const auto& branch:branches) {
            auto child=information.bestRoute(branch.posterior,left-action.duration);
            policy->children.emplace(branch.observation,child.second);
            policy->probabilities.emplace(branch.observation,branch.probability);
            value.lower+=branch.probability*child.first.lower;value.upper+=branch.probability*child.first.upper;
        }
        if(value.lower>best.first.upper+1e-9)best={value,policy};
        work+=information.work;work_cut|=information.work_cut;wall_cut|=information.wall_cut;complete&=information.complete;
    }
    EpisodePlan result;result.policy=best.second;result.value=best.first;result.transitions=work;
    result.work_cut=work_cut;result.wall_cut=wall_cut;result.support_complete=complete;
    return result;
}
