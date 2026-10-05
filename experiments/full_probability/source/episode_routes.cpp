#include "episode_routes.hpp"
#include "physical_route_view.hpp"
#include <algorithm>
#include <stdexcept>
#include <tuple>
using namespace _home;
namespace {
using ActionKey=std::tuple<int,unsigned,unsigned,long long>;
struct PrefixNode;
struct PrefixBranch {
    JointObservation observation;double probability;std::shared_ptr<PrefixNode> posterior;
};
struct PrefixNode {
    const EpisodeBelief belief;
    bool reward_ready=false;
    SdkRewardBounds reward;
    std::map<ActionKey,std::vector<PrefixBranch>> children;
    bool physical_ready=false;
    std::shared_ptr<PrefixNode> physical_view;
    explicit PrefixNode(EpisodeBelief b):belief(std::move(b)) {}
};
struct RouteSearch {
    const SdkEpisodeModel& model;const AskObservationModel& ask;
    const std::vector<EpisodeRoute>& routes;
    std::size_t limit,work=0,cache_hits=0;std::chrono::steady_clock::time_point end;
    bool work_cut=false,wall_cut=false,complete=true,candidate_truncated=false;
    bool physical_reuse;
    const EpisodeLatencyModel* latency;
    std::size_t view_inputs=0,view_worlds=0;
    struct Value {
        SdkRewardBounds first;std::shared_ptr<EpisodePolicy> second;double sdk_ms;
        Value(SdkRewardBounds base,std::shared_ptr<EpisodePolicy> policy,double ms=0)
            :first(base),second(std::move(policy)),sdk_ms(ms){}
        double lower() const {return first.lower-.02*sdk_ms;}
        double upper() const {return first.upper-.02*sdk_ms;}
    };
    RouteSearch(const SdkEpisodeModel& m,const AskObservationModel& a,
        const std::vector<EpisodeRoute>& r,std::size_t cap,std::chrono::steady_clock::time_point deadline,bool reuse,const EpisodeLatencyModel* time)
        :model(m),ask(a),routes(r),limit(cap),end(deadline),physical_reuse(reuse),latency(time) {
        // Public catalogues containing ASK are evaluated without aggregation.
        // ASK selectors/frequencies must stay in the full persistent posterior.
        for(const auto& route:r)for(const auto& action:route)
            if(action.kind==JointActionKind::ASK)physical_reuse=false;
    }
    std::chrono::milliseconds duration(const JointAction& a) const {return latency?latency->reserve(a):a.duration;}
    double sdkMillis(const JointAction& a,const JointObservation& o) const {return latency?latency->estimate(a,o).median_ms:0;}
    std::shared_ptr<PrefixNode> physicalNode(const std::shared_ptr<PrefixNode>& n) {
        if(!physical_reuse)return n;
        if(!n->physical_ready) {
            const auto view=PhysicalRouteView::make(n->belief);
            view_inputs+=view.original_worlds;view_worlds+=view.physical_worlds;
            if(view.physical_worlds<view.original_worlds)
                n->physical_view=std::make_shared<PrefixNode>(view.belief);
            n->physical_ready=true;
        }
        return n->physical_view?n->physical_view:n;
    }
    bool exhausted() {
        if(work>=limit)work_cut=true;
        if(std::chrono::steady_clock::now()>=end)wall_cut=true;
        return work_cut||wall_cut;
    }
    Value stop(const std::shared_ptr<PrefixNode>& n) {
        if(!n->reward_ready){n->reward=n->belief.reward(model);n->reward_ready=true;}
        return {n->reward,std::make_shared<EpisodePolicy>()};
    }
    bool allowed(const EpisodeBelief& b) {
        if(exhausted())return false;
        if(b.support().size()>limit-work){work_cut=true;return false;}
        work+=b.support().size();return true;
    }
    const std::vector<PrefixBranch>* branches(const std::shared_ptr<PrefixNode>& n,const JointAction& a) {
        if(std::chrono::steady_clock::now()>=end){wall_cut=true;return nullptr;}
        const ActionKey key{int(a.kind),a.a,a.b,a.duration.count()};
        auto found=n->children.find(key);
        if(found!=n->children.end()){++cache_hits;return &found->second;}
        if(!allowed(n->belief))return nullptr;
        std::vector<EpisodeBranch> fresh;
        try{fresh=n->belief.branches(model,a,ask);}catch(const std::logic_error&){complete=false;return nullptr;}
        std::vector<PrefixBranch> cached;
        for(auto& b:fresh)cached.push_back({b.observation,b.probability,std::make_shared<PrefixNode>(std::move(b.posterior))});
        return &n->children.emplace(key,std::move(cached)).first->second;
    }
    Value route(const std::shared_ptr<PrefixNode>& n,const EpisodeRoute& actions,std::size_t step,std::chrono::milliseconds left) {
        auto incumbent=stop(n);
        if(step>=actions.size())return incumbent;
        const auto reserved=duration(actions[step]);
        if(reserved>left){candidate_truncated=true;return incumbent;}
        const auto next=branches(n,actions[step]);
        if(!next){candidate_truncated=true;return incumbent;}
        auto policy=std::make_shared<EpisodePolicy>();policy->stop=false;policy->action=actions[step];
        SdkRewardBounds value;double sdk_ms=0;
        for(const auto& branch:*next) {
            const bool physical=branch.observation.kind==JointObservation::Kind::FEEDBACK;
            auto child=physical && !branch.observation.success?stop(branch.posterior):
                route(branch.posterior,actions,step+1,left-reserved);
            policy->children.emplace(branch.observation,child.second);
            policy->probabilities.emplace(branch.observation,branch.probability);
            value.lower+=branch.probability*child.first.lower;value.upper+=branch.probability*child.first.upper;
            sdk_ms+=branch.probability*(sdkMillis(actions[step],branch.observation)+child.sdk_ms);
        }
        // Compare the entire remaining tail with stopping at this PUBLIC
        // observation. Negative intermediate prefixes are allowed when their
        // completed restoration wins; a known-useless failed probe is pruned.
        const bool mandatory_sense=actions[step].kind==JointActionKind::SENSE && step>0 &&
            (actions[step-1].kind==JointActionKind::MOVE || actions[step-1].kind==JointActionKind::OPEN);
        const Value candidate(value,policy,sdk_ms);
        return mandatory_sense || candidate.lower()>incumbent.upper()+1e-9?candidate:incumbent;
    }
    Value bestRoute(const std::shared_ptr<PrefixNode>& n,std::chrono::milliseconds left) {
        const auto evaluation=physicalNode(n);
        auto best=stop(n);const auto& b=evaluation->belief;
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
        std::stable_sort(order.begin(),order.end(),[&](std::size_t a,std::size_t c){return priorities[a]>priorities[c];});
        for(auto id:order) {
            if(exhausted())break;
            candidate_truncated=false;
            auto candidate=route(evaluation,routes[id],0,left);
            if(!candidate_truncated && candidate.lower()>best.upper()+1e-9)best=std::move(candidate);
        }
        return best;
    }
};
}
EpisodePlan EpisodeRouteSearch::solve(const EpisodeBelief& b,const SdkEpisodeModel& m,
    const std::vector<EpisodeRoute>& routes,const std::vector<JointAction>& observations,
    const AskObservationModel& ask,std::chrono::milliseconds left,std::size_t cap,std::chrono::milliseconds wall,bool physical_reuse,const EpisodeLatencyModel* latency) {
    if(!cap || wall.count()<=0 || left.count()<0)throw std::invalid_argument("invalid route budget");
    if(latency)latency->validate();
    for(const auto& route:routes) {
        if(route.size()>64)throw std::invalid_argument("route exceeds bounded stack");
        for(const auto& action:route)if(action.duration.count()<0)throw std::invalid_argument("negative action duration");
    }
    for(const auto& action:observations)if((action.kind!=JointActionKind::SENSE && action.kind!=JointActionKind::ASK)||action.duration.count()<0)
        throw std::invalid_argument("invalid information catalogue");
    const auto end=std::chrono::steady_clock::now()+wall;
    // A direct-route catalogue cannot consume the observation candidates'
    // reserved work. Each observation gets a deterministic fair work slice.
    RouteSearch search(m,ask,routes,observations.empty()?cap:std::max(std::size_t(1),cap/2),observations.empty()?end:end-wall/2,physical_reuse,latency);
    // A node owns the whole immutable posterior at one public action/feedback
    // prefix, including paid costs, permanent credits and latent answer order.
    // It is never indexed by a hidden world ID and never survives this solve.
    const auto root=std::make_shared<PrefixNode>(b);
    auto best=search.bestRoute(root,left);
    std::size_t work=search.work,remaining=observations.size();
    std::size_t cache_hits=search.cache_hits;
    std::size_t view_inputs=search.view_inputs,view_worlds=search.view_worlds;
    bool work_cut=search.work_cut,wall_cut=search.wall_cut,complete=search.complete;
    for(const auto& action:observations) {
        if(work>=cap){work_cut=true;break;}
        const auto slice=std::max(std::size_t(1),(cap-work)/remaining--);
        RouteSearch information(m,ask,routes,slice,end,physical_reuse,latency);
        const auto reserved=information.duration(action);
        if(reserved>left)continue;
        const auto branches=information.branches(root,action);
        if(!branches) {
            work+=information.work;cache_hits+=information.cache_hits;
            work_cut|=information.work_cut;wall_cut|=information.wall_cut;complete&=information.complete;continue;
        }
        auto ordered=*branches;
        std::stable_sort(ordered.begin(),ordered.end(),[](const PrefixBranch& a,const PrefixBranch& b){return a.probability>b.probability;});
        auto policy=std::make_shared<EpisodePolicy>();policy->stop=false;policy->action=action;
        SdkRewardBounds value;double sdk_ms=0;
        for(const auto& branch:ordered) {
            auto child=information.bestRoute(branch.posterior,left-reserved);
            policy->children.emplace(branch.observation,child.second);
            policy->probabilities.emplace(branch.observation,branch.probability);
            value.lower+=branch.probability*child.first.lower;value.upper+=branch.probability*child.first.upper;
            sdk_ms+=branch.probability*(information.sdkMillis(action,branch.observation)+child.sdk_ms);
        }
        const RouteSearch::Value candidate(value,policy,sdk_ms);
        if(candidate.lower()>best.upper()+1e-9)best=candidate;
        work+=information.work;cache_hits+=information.cache_hits;work_cut|=information.work_cut;wall_cut|=information.wall_cut;complete&=information.complete;
        view_inputs+=information.view_inputs;view_worlds+=information.view_worlds;
    }
    EpisodePlan result;result.policy=best.second;result.value=best.first;result.transitions=work;
    result.work_cut=work_cut;result.wall_cut=wall_cut;result.support_complete=complete;
    result.prefix_cache_hits=cache_hits;
    result.physical_view_inputs=view_inputs;result.physical_view_worlds=view_worlds;
    result.predicted_sdk_ms=best.sdk_ms;result.proxy_lower=best.lower();result.proxy_upper=best.upper();
    return result;
}
