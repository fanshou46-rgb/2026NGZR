#include "joint_world.hpp"
#include <algorithm>
#include <cmath>
#include <stdexcept>
#include <tuple>
using namespace _home;

void JointWorld::freezeSdkReplyDomain() {
    if(!initial_reply_counts.empty())return;
    initial_reply_counts[{'a',robot}]+=1;
    for(const auto& item:objects) {
        if(item.second.at>=0)initial_reply_counts[{'a',item.second.at}]+=1;
        if(item.second.container)initial_reply_counts[{'i',int(item.first)}]+=1;
    }
}

void JointWorld::validate() const {
    for(int location:locations) if(location<0) throw std::invalid_argument("negative world location");
    if(!locations.count(robot)) throw std::invalid_argument("unknown robot location");
    if(hand && hand==plate) throw std::invalid_argument("same object in both slots");
    for(unsigned slot:{hand,plate}) if(slot && (!objects.count(slot) || !objects.at(slot).small))
        throw std::invalid_argument("invalid held object");
    for(const auto& item:objects) {
        const auto& o=item.second;
        if(!item.first || (o.at!=-1 && !locations.count(o.at)))
            throw std::invalid_argument("invalid object location");
        if(o.inside && (!o.small || !objects.count(o.inside) || !objects.at(o.inside).container))
            throw std::invalid_argument("invalid containment");
        if(o.container && o.small) throw std::invalid_argument("movable containers not modeled");
    }
}
bool JointWorld::atLocation(unsigned id,int loc) const {
    if(!id) return robot==loc;
    auto it=objects.find(id);if(it==objects.end()) return false;
    return it->second.at==loc || (it->second.small && (hand==id || plate==id) && robot==loc);
}
std::set<unsigned> JointWorld::visible() const {
    std::set<unsigned> result;
    for(const auto& item:objects) {
        const auto& o=item.second;
        if(atLocation(item.first,robot)) result.insert(item.first);
        if(o.inside) {
            const auto& container=objects.at(o.inside);
            if(container.opened && atLocation(o.inside,robot)) result.insert(item.first);
        }
    }
    return result;
}
std::set<LocationHypothesis> JointWorld::truthfulReplies(unsigned id) const {
    if(!id) return {{'a',robot}};
    std::set<LocationHypothesis> result;
    auto it=objects.find(id);if(it==objects.end()) return result;
    for(int loc:locations) if(atLocation(id,loc)) result.insert({'a',loc});
    if(it->second.inside) result.insert({'i',int(it->second.inside)});
    return result;
}
int JointAction::cost() const {
    switch(kind) {
    case JointActionKind::MOVE:return 4;
    case JointActionKind::SENSE:return 1;
    case JointActionKind::PICKUP:case JointActionKind::PUTDOWN:
    case JointActionKind::TOPLATE:case JointActionKind::FROMPLATE:
    case JointActionKind::OPEN:case JointActionKind::CLOSE:
    case JointActionKind::PUTIN:case JointActionKind::TAKEOUT:case JointActionKind::ASK:return 2;
    }
    throw std::invalid_argument("unsupported joint action");
}
bool JointObservation::operator<(const JointObservation& other) const {
    return std::tie(kind,success,ids,reply)<std::tie(other.kind,other.success,other.ids,other.reply);
}
JointStep JointDynamics::step(const JointWorld& original,const JointAction& action) {
    original.validate();
    action.cost(); // Validate the action vocabulary even for standalone steps.
    if(action.kind==JointActionKind::ASK) throw std::invalid_argument("ask needs noisy observation model");
    JointStep result;result.world=original;
    auto& w=result.world;
    if(action.kind==JointActionKind::SENSE) {
        result.observation.kind=JointObservation::Kind::VISIBLE;
        result.observation.ids=w.visible();return result;
    }
    auto it=w.objects.find(action.a),dest=w.objects.find(action.b);
    bool success=false;
    const bool small=it!=w.objects.end() && it->second.small;
    const bool container=it!=w.objects.end() && it->second.container;
    const bool into=dest!=w.objects.end() && dest->second.container && dest->second.opened && w.atLocation(action.b,w.robot);
    switch(action.kind) {
    case JointActionKind::MOVE:
        success=w.locations.count(int(action.a)) && w.robot!=int(action.a);
        if(success) {
            w.robot=int(action.a);
            for(unsigned slot:{w.hand,w.plate}) if(slot) w.objects.at(slot).at=w.robot;
        }break;
    case JointActionKind::PICKUP:
        success=small && !w.hand && w.plate!=action.a && w.atLocation(action.a,w.robot);
        if(success) {w.hand=action.a;it->second.at=w.robot;}break;
    case JointActionKind::PUTDOWN:
        success=small && w.hand==action.a;
        if(success) {w.hand=0;it->second.at=w.robot;}break;
    case JointActionKind::TOPLATE:
        success=small && w.hand==action.a && !w.plate;
        if(success) {w.hand=0;w.plate=action.a;it->second.at=w.robot;}break;
    case JointActionKind::FROMPLATE:
        success=small && w.plate==action.a && !w.hand;
        if(success) {w.plate=0;w.hand=action.a;it->second.at=w.robot;}break;
    case JointActionKind::OPEN:
    case JointActionKind::CLOSE: {
        const bool opening=action.kind==JointActionKind::OPEN;
        success=container && !w.hand && w.atLocation(action.a,w.robot) && it->second.opened!=opening;
        if(success) it->second.opened=opening;
        break;
    }
    case JointActionKind::PUTIN:
        success=small && into && w.hand==action.a;
        if(success) {w.hand=0;it->second.inside=action.b;if(it->second.at==w.robot)it->second.at=-1;}break;
    case JointActionKind::TAKEOUT:
        success=small && into && !w.hand && it->second.inside==action.b;
        if(success) {w.hand=action.a;it->second.inside=0;it->second.at=w.robot;}break;
    default: break;
    }
    result.observation.success=success;w.validate();return result;
}

JointBelief::JointBelief(std::vector<WeightedJointWorld> input,double outside)
    :worlds(std::move(input)),residual(outside) {
    if(!std::isfinite(residual) || residual<0) throw std::invalid_argument("invalid residual mass");
    double total=residual;
    for(const auto& state:worlds) {
        state.world.validate();
        if(!std::isfinite(state.weight) || state.weight<0) throw std::invalid_argument("invalid world weight");
        total+=state.weight;
    }
    if(!std::isfinite(total) || total<=0) throw std::invalid_argument("empty joint support");
    residual/=total;for(auto& state:worlds) state.weight/=total;
}
double JointBelief::expectation(const std::function<double(const JointWorld&)>& value) const {
    if(residual>0) throw std::logic_error("unmodeled residual reward");
    double result=0;
    for(const auto& state:worlds) if(state.weight>0) {
        double score=value(state.world);
        if(!std::isfinite(score)) throw std::invalid_argument("invalid terminal reward");
        result+=state.weight*score;
    }
    return result;
}
std::vector<JointBranch> JointBelief::branches(const JointAction& action,const AskObservationModel& model) const {
    if(residual>0) throw std::logic_error("unmodeled residual observation");
    std::map<JointObservation,std::vector<WeightedJointWorld>> groups;
    for(const auto& state:worlds) {
        if(state.weight<=0)continue;
        if(action.kind==JointActionKind::ASK) {
            const auto replies=state.world.truthfulReplies(action.a);
            // The SDK returns the first matching answer atom, whose ordering is
            // not specified when both at and inside exist. Do not invent it.
            if(replies.size()!=1) throw std::logic_error("nonunique truthful SDK answer");
            const auto observation_model=state.world.initial_reply_counts.empty()?model:
                model.reweighted(state.world.initial_reply_counts,0);
            for(auto reply:observation_model.observations()) {
                double mass=state.weight*observation_model.likelihood(reply,*replies.begin());
                if(mass<=0)continue;
                JointObservation observation;observation.kind=JointObservation::Kind::ANSWER;observation.reply=reply;
                groups[observation].push_back({state.world,mass});
            }
        } else {
            auto next=JointDynamics::step(state.world,action);
            groups[next.observation].push_back({std::move(next.world),state.weight});
        }
    }
    std::vector<JointBranch> result;
    for(auto& group:groups) {
        double mass=0;for(const auto& state:group.second)mass+=state.weight;
        result.push_back({group.first,mass,JointBelief(std::move(group.second))});
    }
    return result;
}
bool JointBelief::observe(const JointAction& action,const JointObservation& observation,
    const AskObservationModel& model,std::size_t event) {
    if(event && received_events.count(event))return false;
    const auto next=branches(action,model);
    for(const auto& branch:next) if(!(branch.observation<observation) && !(observation<branch.observation)) {
        worlds=branch.posterior.worlds;
        if(event)received_events.insert(event);
        return true;
    }
    return false;
}

namespace {
struct Search {
    const std::vector<JointAction>& actions;
    const AskObservationModel& model;
    const std::function<double(const JointWorld&)>& value;
    std::size_t limit,nodes=0;
    std::chrono::steady_clock::time_point deadline;
    bool complete=true,covered=true;
    Search(const std::vector<JointAction>& a,const AskObservationModel& m,
        const std::function<double(const JointWorld&)>& v,std::size_t n,
        std::chrono::steady_clock::time_point end)
        :actions(a),model(m),value(v),limit(n),deadline(end) {}
    bool exhausted() const {return nodes>=limit || std::chrono::steady_clock::now()>=deadline;}
    std::pair<double,std::shared_ptr<JointPolicy>> run(const JointBelief& b,unsigned depth,
        std::chrono::milliseconds remaining) {
        const double stop=b.expectation(value);
        auto policy=std::make_shared<JointPolicy>();double best=stop;
        if(!depth) return {best,policy};
        if(exhausted()) {complete=false;return {best,policy};}
        ++nodes;
        for(const auto& action:actions) {
            if(action.duration>remaining)continue;
            if(exhausted()) {complete=false;break;}
            std::vector<JointBranch> branches;
            try {branches=b.branches(action,model);}
            catch(const std::logic_error&) {covered=false;continue;}
            auto candidate=std::make_shared<JointPolicy>();candidate->stop=false;candidate->action=action;
            double expected=-action.cost();
            // Even when search runs out, each child has an explicit stop policy.
            // It remains a valid lower bound, never an oracle upper bound.
            for(const auto& branch:branches) {
                auto child=run(branch.posterior,depth-1,remaining-action.duration);
                expected+=branch.probability*child.first;
                candidate->children.emplace(branch.observation,child.second);
            }
            if(expected>best+1e-12) {best=expected;policy=std::move(candidate);}
        }
        return {best,policy};
    }
};
}
JointPlan JointPolicySearch::solve(const JointBelief& belief,const std::vector<JointAction>& actions,
    const AskObservationModel& model,const std::function<double(const JointWorld&)>& value,
    unsigned depth,std::chrono::milliseconds remaining,std::size_t nodes,std::chrono::milliseconds time) {
    if(depth>32)throw std::invalid_argument("joint horizon exceeds bounded stack");
    if(remaining.count()<0 || time.count()<0)throw std::invalid_argument("negative search time");
    for(const auto& action:actions) if(action.duration.count()<0)throw std::invalid_argument("negative action time");
    JointPlan result;result.policy=std::make_shared<JointPolicy>();
    if(belief.residualMass()>0) {result.support_complete=false;result.reason="residual_support";return result;}
    Search search(actions,model,value,nodes,std::chrono::steady_clock::now()+time);
    result.stop_value=belief.expectation(value);
    auto best=search.run(belief,depth,remaining);
    result.value=best.first;result.policy=std::move(best.second);result.nodes=search.nodes;
    result.search_complete=search.complete;result.support_complete=search.covered;
    if(!search.covered)result.reason="unmodeled_answer_order";
    else if(!search.complete)result.reason="search_budget";
    return result;
}
