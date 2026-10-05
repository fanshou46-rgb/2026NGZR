#include "episode_router.hpp"
#include <algorithm>
#include <numeric>
#include <sstream>
#include <stdexcept>
using namespace _home;
namespace {
struct Builder {
    JointWorld world;EpisodeRoute route;bool tray,sense,preopen,preopen_opportunity=false;
    std::size_t& work;std::size_t cap;std::chrono::steady_clock::time_point end;
    Builder(const JointWorld& w,bool use_tray,bool observation,std::size_t& used,std::size_t limit,std::chrono::steady_clock::time_point deadline,bool early=false)
        :world(w),tray(use_tray),sense(observation),preopen(early),work(used),cap(limit),end(deadline) {}
    void emit(JointActionKind kind,unsigned a=0,unsigned b=0) {
        if(work>=cap || std::chrono::steady_clock::now()>=end)throw std::runtime_error("proposal budget");
        if(route.size()>=64)throw std::runtime_error("proposal horizon");
        ++work;JointAction action(kind,a,b);auto next=JointDynamics::step(world,action);
        if(next.observation.kind==JointObservation::Kind::FEEDBACK && !next.observation.success)
            throw std::logic_error("infeasible hypothetical route");
        world=std::move(next.world);route.push_back(action);
    }
    int position(unsigned id) const {
        if(!id)return world.robot;
        const auto item=world.objects.find(id);if(item==world.objects.end())throw std::logic_error("missing public object");
        if(item->second.small && (world.hand==id || world.plate==id))return world.robot;
        if(item->second.at>=0)return item->second.at;
        for(unsigned parent:item->second.inside)if(world.objects.at(parent).at>=0)return world.objects.at(parent).at;
        throw std::logic_error("no route position in scenario");
    }
    void go(int location) {
        if(world.robot!=location){emit(JointActionKind::MOVE,unsigned(location));if(sense)emit(JointActionKind::SENSE);}
    }
    void freeHand() {
        if(!world.hand)return;
        if(tray && !world.plate)emit(JointActionKind::TOPLATE,world.hand);
        else emit(JointActionKind::PUTDOWN,world.hand);
    }
    void open(unsigned id) {
        if(world.objects.at(id).opened)return;
        freeHand();go(position(id));emit(JointActionKind::OPEN,id);
        // Door feedback does not identify its contents. Required perception
        // after opening remains part of every proposed acquisition route.
        if(sense)emit(JointActionKind::SENSE);
    }
    void acquire(unsigned id) {
        if(world.hand==id)return;
        freeHand();
        if(world.plate==id){emit(JointActionKind::FROMPLATE,id);return;}
        const auto item=world.objects.at(id);
        if(item.at>=0){go(item.at);emit(JointActionKind::PICKUP,id);return;}
        if(!item.inside.empty()) {
            const unsigned parent=*item.inside.begin();go(position(parent));open(parent);
            emit(JointActionKind::TAKEOUT,id,parent);return;
        }
        throw std::logic_error("unlocated scenario item");
    }
    void task(const SdkEpisodeModel& m,const SdkPredicate& goal) {
        if(goal.bindings.empty())return;
        const auto pair=goal.bindings.front();const unsigned a=pair.first,b=pair.second;
        // Choosing one public binding proposes a route only. The full-model
        // reward still retains the interval across all SDK binding choices.
        if(m.predicate(world,goal.verb,a,b))return;
        if(goal.verb=="goto" || goal.verb=="move")go(position(a));
        else if(goal.verb=="pickup")acquire(a);
        else if(goal.verb=="putdown") {
            if(world.hand==a)emit(JointActionKind::PUTDOWN,a);
            if(world.plate==a){freeHand();emit(JointActionKind::FROMPLATE,a);emit(JointActionKind::PUTDOWN,a);}
        } else if(goal.verb=="give" || goal.verb=="puton") {
            acquire(a);go(position(b));emit(JointActionKind::PUTDOWN,a);
            if(world.plate==a){emit(JointActionKind::FROMPLATE,a);emit(JointActionKind::PUTDOWN,a);}
        } else if(goal.verb=="open")open(a);
        else if(goal.verb=="close"){freeHand();go(position(a));emit(JointActionKind::CLOSE,a);}
        else if(goal.verb=="takeout"){freeHand();go(position(b));open(b);emit(JointActionKind::TAKEOUT,a,b);}
        else if(goal.verb=="putin") {
            const bool local_empty=!world.hand && !world.objects.at(b).opened && position(a)==position(b);
            preopen_opportunity|=local_empty;
            if(preopen && local_empty){go(position(b));open(b);}
            acquire(a);go(position(b));open(b);acquire(a);emit(JointActionKind::PUTIN,a,b);
        } else throw std::logic_error("unsupported task route");
    }
    bool batchDelivery(const SdkEpisodeModel& m,const SdkPredicate& left,const SdkPredicate& right) {
        const auto delivery=[](const SdkPredicate& g){return g.verb=="give" || g.verb=="puton";};
        if(!tray || world.plate || !delivery(left) || !delivery(right) ||
           left.bindings.empty() || right.bindings.empty())return false;
        auto a=left.bindings.front(),b=right.bindings.front();
        if(a.first==b.first || !a.second || !b.second ||
           (world.hand && world.hand!=a.first && world.hand!=b.first))return false;
        if(m.predicate(world,left.verb,a.first,a.second) || m.predicate(world,right.verb,b.first,b.second))return false;
        if(position(a.first)!=position(b.first) || position(a.second)!=position(b.second))return false;
        if(world.hand==b.first)std::swap(a,b);
        // This only proposes a capacity-feasible hypothetical route. Both
        // stored items and all permanent constraints are scored on the whole
        // belief; a tray prohibition can reject it in favour of serial delivery.
        acquire(a.first);emit(JointActionKind::TOPLATE,a.first);acquire(b.first);
        go(position(a.second));emit(JointActionKind::PUTDOWN,b.first);
        emit(JointActionKind::FROMPLATE,a.first);emit(JointActionKind::PUTDOWN,a.first);
        return true;
    }
};
std::string key(const EpisodeRoute& route) {
    std::ostringstream s;for(const auto& a:route)s<<int(a.kind)<<','<<a.a<<','<<a.b<<';';return s.str();
}
}
EpisodeProposalBatch EpisodeRouter::propose(const EpisodeBelief& belief,const SdkEpisodeModel& model,
    std::size_t cap,std::chrono::milliseconds wall,bool sense) {
    if(!cap || wall.count()<=0)throw std::invalid_argument("invalid proposal budget");
    EpisodeProposalBatch result;const auto end=std::chrono::steady_clock::now()+wall;
    std::vector<std::size_t> order(model.goals.size());std::iota(order.begin(),order.end(),0);
    const auto rank=[&](std::size_t id){const auto& v=model.goals[id].verb;return v=="goto"?3:v=="pickup"?2:v=="close"?1:0;};
    std::stable_sort(order.begin(),order.end(),[&](std::size_t a,std::size_t b){return rank(a)<rank(b);});
    std::vector<std::vector<std::size_t>> orders={order};
    // Separate terminal endpoints; each route is priced by all final goals.
    for(auto endpoint:order)if(model.goals[endpoint].verb=="goto") {
        std::vector<std::size_t> one;
        for(auto id:order)if(model.goals[id].verb!="goto")one.push_back(id);
        one.push_back(endpoint);orders.push_back(std::move(one));
    }
    if(order.size()<=16)for(std::size_t omit=0;omit<order.size();++omit) {
        auto subset=order;subset.erase(subset.begin()+omit);orders.push_back(std::move(subset));
    }
    for(auto id:order)orders.push_back({id});
    std::set<std::string> seen;
    // Offer the same complete order across different public hypotheses before
    // spending work on many variants of the first sampled world.
    for(const auto& task_order:orders)for(const auto& state:belief.support())for(bool tray:{false,true}) {
        if(result.transitions>=cap || std::chrono::steady_clock::now()>=end) {
            result.work_cut=result.transitions>=cap;result.wall_cut=std::chrono::steady_clock::now()>=end;return result;
        }
        Builder builder(state.episode.world,tray,sense,result.transitions,cap,end);
        try{for(std::size_t i=0;i<task_order.size();++i) {
            if(i+1<task_order.size() && builder.batchDelivery(model,model.goals[task_order[i]],model.goals[task_order[i+1]]))++i;
            else builder.task(model,model.goals[task_order[i]]);
        }}
        catch(const std::exception&){continue;}
        if(!builder.route.empty() && seen.insert(key(builder.route)).second)result.routes.push_back(std::move(builder.route));
        if(builder.preopen_opportunity) {
            // Add a cheaper local opening order, retaining the original. The
            // earlier successful Open can damage a permanent constraint that
            // the original first TakeOut would restore, so it is not assumed
            // dominant and receives no execution privilege.
            Builder early(state.episode.world,tray,sense,result.transitions,cap,end,true);
            try{for(std::size_t i=0;i<task_order.size();++i) {
                if(i+1<task_order.size() && early.batchDelivery(model,model.goals[task_order[i]],model.goals[task_order[i+1]]))++i;
                else early.task(model,model.goals[task_order[i]]);
            }}catch(const std::exception&){continue;}
            if(!early.route.empty() && seen.insert(key(early.route)).second)result.routes.push_back(std::move(early.route));
        }
    }
    return result;
}
