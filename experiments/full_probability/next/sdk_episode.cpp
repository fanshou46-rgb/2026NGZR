#include "sdk_episode.hpp"
#include <algorithm>
#include <cmath>
#include <stdexcept>
using namespace _home;
bool SdkEpisodeModel::predicate(const JointWorld& w,const std::string& verb,unsigned a,unsigned b) const {
    const auto x=w.objects.find(a),y=w.objects.find(b);
    const bool small=x!=w.objects.end()&&x->second.small;
    const bool stored=small&&(w.hand==a || w.plate==a);
    const auto same=[&]() {
        if(x==w.objects.end() || y==w.objects.end())return false;
        for(int loc:w.locations)if(w.atLocation(a,loc)&&w.atLocation(b,loc))return true;
        return false;
    };
    if(verb=="goto" || verb=="move")return x!=w.objects.end()&&w.atLocation(a,w.robot);
    if(verb=="open" || verb=="opened")return x!=w.objects.end()&&x->second.container&&x->second.opened;
    if(verb=="close" || verb=="closed")return x!=w.objects.end()&&x->second.container&&!x->second.opened;
    if(verb=="pickup")return small&&stored;
    if(verb=="putdown")return small&&!stored;
    if(verb=="putin" || verb=="inside" || verb=="in")return small&&y!=w.objects.end()&&y->second.container&&x->second.inside.count(b);
    if(verb=="takeout")return small&&y!=w.objects.end()&&y->second.container&&!x->second.inside.count(b);
    if(verb=="puton" || verb=="give")return small&&!stored&&same();
    if(verb=="on" || verb=="near" || verb=="nextto")return same();
    if(verb=="plate")return w.plate==a;
    if(verb=="hold")return w.hand==a;
    if(verb=="at")return w.atLocation(a,int(b));
    throw std::invalid_argument("unsupported SDK predicate: "+verb);
}
bool SdkEpisodeModel::constraint(const JointWorld& w,const SdkConstraint& c) const {
    if(c.predicate.bindings.empty())throw std::invalid_argument("constraint without public grounding");
    for(const auto& pair:c.predicate.bindings)
        if(predicate(w,c.predicate.verb,pair.first,pair.second)!=c.must_hold)return false;
    return true;
}
SdkRewardBounds SdkEpisodeModel::reward(const SdkEpisode& e) const {
    if(e.credits.size()!=constraints.size())throw std::invalid_argument("missing irreversible SDK ledger");
    SdkRewardBounds r;
    for(const auto& goal:goals) {
        if(goal.bindings.empty())throw std::invalid_argument("task without public grounding");
        bool all=true,any=false;
        for(const auto& pair:goal.bindings) {bool truth=predicate(e.world,goal.verb,pair.first,pair.second);all&=truth;any|=truth;}
        r.goals_lower+=all;r.goals_upper+=any;
    }
    r.credits=std::count(e.credits.begin(),e.credits.end(),true);
    r.lower=40.0*r.goals_lower+(r.goals_lower?20.0*r.credits:0)-e.paid;
    r.upper=40.0*r.goals_upper+(r.goals_upper?20.0*r.credits:0)-e.paid;
    return r;
}
SdkEpisode SdkEpisodeModel::next(const SdkEpisode& old,const JointAction& action,const JointWorld& world,bool success) const {
    SdkEpisode e=old;e.world=world;e.paid+=action.cost();
    if(success && action.kind!=JointActionKind::SENSE && action.kind!=JointActionKind::ASK) {
        if(e.credits.size()!=constraints.size())throw std::invalid_argument("missing SDK ledger");
        for(std::size_t i=0;i<constraints.size();++i)if(e.credits[i]&&!constraint(world,constraints[i]))e.credits[i]=false;
    }
    return e;
}
EpisodeBelief::EpisodeBelief(std::vector<WeightedEpisode> input,double residual)
    :states(std::move(input)),outside(residual) {
    if(!std::isfinite(outside)||outside<0)throw std::invalid_argument("invalid residual");
    double total=outside;
    for(const auto& s:states) {
        s.episode.world.validate();
        if(!std::isfinite(s.weight)||s.weight<0)throw std::invalid_argument("invalid scenario weight");
        total+=s.weight;
    }
    if(!std::isfinite(total)||total<=0)throw std::invalid_argument("empty episode support");
    outside/=total;for(auto& s:states)s.weight/=total;
}
SdkRewardBounds EpisodeBelief::reward(const SdkEpisodeModel& model) const {
    if(!valid)throw std::logic_error("repair required after support miss");
    if(outside>0)throw std::logic_error("unmodeled residual terminal reward");
    SdkRewardBounds r;
    for(const auto& s:states) {const auto v=model.reward(s.episode);r.lower+=s.weight*v.lower;r.upper+=s.weight*v.upper;}
    return r;
}
std::vector<EpisodeBranch> EpisodeBelief::branches(const SdkEpisodeModel& model,const JointAction& action,const AskObservationModel& ask) const {
    if(!valid)throw std::logic_error("repair required after support miss");
    if(outside>0)throw std::logic_error("unmodeled residual action feedback");
    std::map<JointObservation,std::vector<WeightedEpisode>> groups;
    for(const auto& s:states)if(s.weight>0) {
        const JointBelief one({{s.episode.world,1}});
        for(const auto& branch:one.branches(action,ask))for(const auto& posterior:branch.posterior.support()) {
            auto episode=model.next(s.episode,action,posterior.world,branch.observation.success);
            groups[branch.observation].push_back({std::move(episode),s.weight*branch.probability*posterior.weight});
        }
    }
    std::vector<EpisodeBranch> result;
    for(auto& group:groups) {
        double mass=0;for(const auto& s:group.second)mass+=s.weight;
        result.push_back({group.first,mass,EpisodeBelief(std::move(group.second))});
    }
    return result;
}
EpisodeUpdate EpisodeBelief::observe(const SdkEpisodeModel& model,const JointAction& action,const JointObservation& observation,const AskObservationModel& ask,std::size_t event) {
    if(!event)throw std::invalid_argument("actual feedback requires receipt ID");
    if(events.count(event))return EpisodeUpdate::DUPLICATE;
    const auto next=branches(model,action,ask);
    events.insert(event);
    for(const auto& branch:next)if(!(branch.observation<observation)&&!(observation<branch.observation)) {
        states=branch.posterior.states;outside=branch.posterior.outside;
        return EpisodeUpdate::APPLIED;
    }
    // A support miss is a model failure, never a confirmation or permission
    // to send the paid action again. Preserve support and require repair.
    for(auto& state:states)state.episode.paid+=action.cost();
    valid=false;
    return EpisodeUpdate::SUPPORT_MISS;
}
namespace {
struct EpisodeSearch {
    const SdkEpisodeModel& model;const std::vector<JointAction>& actions;const AskObservationModel& ask;
    std::size_t limit,work=0;std::chrono::steady_clock::time_point deadline;
    bool work_cut=false,wall_cut=false,support_complete=true;
    EpisodeSearch(const SdkEpisodeModel& m,const std::vector<JointAction>& a,
        const AskObservationModel& o,std::size_t cap,std::chrono::steady_clock::time_point end)
        :model(m),actions(a),ask(o),limit(cap),deadline(end) {}
    bool exhausted() {
        if(work>=limit)work_cut=true;
        if(std::chrono::steady_clock::now()>=deadline)wall_cut=true;
        return work_cut||wall_cut;
    }
    std::pair<SdkRewardBounds,std::shared_ptr<EpisodePolicy>> run(const EpisodeBelief& belief,unsigned depth,std::chrono::milliseconds left) {
        auto best=belief.reward(model);auto policy=std::make_shared<EpisodePolicy>();
        if(!depth || exhausted())return {best,policy};
        for(const auto& action:actions) {
            if(exhausted())break;
            if(action.duration>left)continue;
            const auto transitions=belief.support().size();
            if(transitions>limit-work){work_cut=true;break;}
            work+=transitions;
            std::vector<EpisodeBranch> branches;
            try{branches=belief.branches(model,action,ask);}
            catch(const std::logic_error&){support_complete=false;continue;}
            auto candidate=std::make_shared<EpisodePolicy>();candidate->stop=false;candidate->action=action;
            SdkRewardBounds value;
            for(const auto& branch:branches) {
                auto child=run(branch.posterior,depth-1,left-action.duration);
                candidate->children[branch.observation]=child.second;
                value.lower+=branch.probability*child.first.lower;value.upper+=branch.probability*child.first.upper;
            }
            // Terminal reward already includes every paid action. No second
            // subtraction of costs, including failed commands and observations.
            if(value.lower>best.upper+1e-9){best=value;policy=candidate;}
        }
        return {best,policy};
    }
};
}
EpisodePlan EpisodePolicySearch::solve(const EpisodeBelief& b,const SdkEpisodeModel& m,const std::vector<JointAction>& a,const AskObservationModel& o,unsigned depth,std::chrono::milliseconds time,std::size_t cap,std::chrono::milliseconds wall) {
    if(depth>32 || !cap || wall.count()<=0 || time.count()<0)throw std::invalid_argument("invalid policy budget");
    EpisodeSearch search(m,a,o,cap,std::chrono::steady_clock::now()+wall);
    const auto solution=search.run(b,depth,time);EpisodePlan r;r.policy=solution.second;r.value=solution.first;
    r.transitions=search.work;r.work_cut=search.work_cut;r.wall_cut=search.wall_cut;r.support_complete=search.support_complete;
    return r;
}
