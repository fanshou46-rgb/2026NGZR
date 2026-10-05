#include "full_controller.hpp"
#include "rdfw.hpp"
#include <algorithm>
#include <cmath>
#include <regex>
#include <stdexcept>
using namespace _home;
namespace {
SdkPredicate ground(const Instruction& instruction,const RDFW& w) {
    SdkPredicate p;p.verb=instruction.behave;
    for(const auto& x:instruction.X)if(x) {
        if(p.verb=="give"){if(w.human)p.bindings.push_back({x->id,w.human->id});}
        else if(instruction.Y.empty())p.bindings.push_back({x->id,0});
        else for(const auto& y:instruction.Y)if(y)p.bindings.push_back({x->id,y->id});
    }
    return p;
}
const char* actionName(JointActionKind kind) {
    switch(kind) {
    case JointActionKind::MOVE:return "Move";case JointActionKind::PICKUP:return "PickUp";
    case JointActionKind::PUTDOWN:return "PutDown";case JointActionKind::TOPLATE:return "ToPlate";
    case JointActionKind::FROMPLATE:return "FromPlate";case JointActionKind::OPEN:return "Open";
    case JointActionKind::CLOSE:return "Close";case JointActionKind::PUTIN:return "PutIn";
    case JointActionKind::TAKEOUT:return "TakeOut";case JointActionKind::SENSE:return "Sense";
    case JointActionKind::ASK:return "AskLoc";
    }
    throw std::invalid_argument("unknown model command");
}
std::vector<unsigned> arguments(const JointAction& a) {
    if(a.kind==JointActionKind::SENSE)return {};
    if(a.kind==JointActionKind::PUTIN || a.kind==JointActionKind::TAKEOUT)return {a.a,a.b};
    return {a.a};
}
bool strong(const RDFW& w,StateField field,unsigned id) {
    const auto& p=w.Provenance(field,id);
    if(w.FactValue(field,id)==UNKNOWN)return false;
    // Constraint votes never become a hard generative assumption here.
    return p.resolved_source!=EvidenceSource::CONSTRAINT_DERIVED &&
        p.resolved_source!=EvidenceSource::CONSTRAINT_HEURISTIC &&
        p.resolved_source!=EvidenceSource::RELATION_DERIVED;
}
}
FullModelController::FullModelController(RDFW& w):owner(w),ask({{'a',0}},.6,.3,.1,0) {}
void FullModelController::initialize() {
    auto& w=owner;
    if(w.objects.size()>64 || w.tasks.size()>16 ||
       w.not_infoConstrains.size()+w.notnot_infoConstrains.size()+w.not_taskConstrains.size()>64)
        throw std::logic_error("public scene exceeds bounded controller scope");
    for(const auto& task:w.tasks)if(task.IsUsable()) {
        auto p=ground(task,w);if(p.bindings.empty())throw std::logic_error("ungrounded public goal");model.goals.push_back(p);
    }
    const auto add=[&](const std::vector<Instruction>& items,bool must) {
        for(const auto& instruction:items)if(instruction.IsUsable()) {
            auto p=ground(instruction,w);if(p.bindings.empty())throw std::logic_error("ungrounded public constraint");
            model.constraints.push_back({p,must});
        }
    };
    add(w.not_infoConstrains,false);add(w.notnot_infoConstrains,true);add(w.not_taskConstrains,false);
    initial_template.robot=w.FactLocation(0);
    if(initial_template.robot<0)throw std::logic_error("robot position is not confirmed");
    initial_template.locations.insert(initial_template.robot);
    for(const auto& object:w.objects)if(object && object->id>0) {
        const auto& p=w.Provenance(StateField::LOCATION,object->id);
        if(p.received.present && p.received.value>=0)initial_template.locations.insert(p.received.value);
        if(w.FactLocation(object->id)>=0)initial_template.locations.insert(w.FactLocation(object->id));
    }
    // Locations are the public finite map domain. Its coverage is recorded; an
    // observed world outside it causes support repair/Stop, never a false fact.
    std::vector<unsigned> small_ids;
    for(const auto& object:w.objects)if(object && object->id>0) {
        const unsigned id=object->id;const bool small=bool(std::dynamic_pointer_cast<SmallObject>(object));
        const bool container=bool(std::dynamic_pointer_cast<Container>(object));
        const auto& position=w.Provenance(StateField::LOCATION,id);
        int at=position.received.present?position.received.value:-1;
        if(at<0)at=-1;
        if(w.stage==1 || strong(w,StateField::LOCATION,id))at=w.ExplicitAt(id);
        if(at<0)at=-1;
        if(!small && at<0)at=initial_template.robot;
        initial_template.objects[id]=JointObject(small,container,at);
        if(small)small_ids.push_back(id);
        if(container) {
            const auto& p=w.Provenance(StateField::CONTAINER_STATE,id);
            bool opened=p.received.present && p.received.value==1;
            if(strong(w,StateField::CONTAINER_STATE,id))opened=w.FactContainerState(id)==1;
            initial_template.objects[id].opened=opened;
            if(!strong(w,StateField::CONTAINER_STATE,id)) {
                PublicPriorFactor f;f.field=PriorField::DOOR;f.object=id;
                f.values={{opened?1:0,.8},{opened?0:1,.2}};factors.push_back(f);
            }
        }
        if(w.stage!=1 && !strong(w,StateField::LOCATION,id)) {
            PublicPriorFactor f;f.field=PriorField::EXPLICIT_AT;f.object=id;
            std::vector<int> alternatives;
            for(int loc:initial_template.locations)if(loc!=at)alternatives.push_back(loc);
            if(small && at!=-1)alternatives.push_back(-1);
            if(alternatives.empty())f.values={{at,1}};
            else {
                f.values.push_back({at,.8});
                for(int loc:alternatives)f.values.push_back({loc,.2/alternatives.size()});
            }
            factors.push_back(f);
        }
    }
    for(unsigned id:small_ids)for(const auto& parent:initial_template.objects)if(parent.second.container) {
        const auto& p=w.Provenance(StateField::INSIDE,id);
        auto edge=p.inside_edges.find(parent.first);
        const bool received=edge!=p.inside_edges.end() && edge->second.value==1;
        const bool known=w.InsideRelation(id,parent.first)!=UNKNOWN &&
            ((edge!=p.inside_edges.end() && edge->second.verified) || w.stage==1);
        const bool present=known?w.InsideRelation(id,parent.first)==1:received;
        if(present)initial_template.objects[id].inside.insert(parent.first);
        if(!known) {
            PublicPriorFactor f;f.field=PriorField::INSIDE_EDGE;f.object=id;f.parent=parent.first;
            f.values={{present?1:0,.98},{present?0:1,.02}};factors.push_back(f);
        }
    }
    for(auto field:{StateField::HOLD,StateField::PLATE}) {
        const bool known=strong(w,field,0);const auto& p=w.Provenance(field,0);
        unsigned hint=known?unsigned(w.FactValue(field)):p.received.present && p.received.value>0?unsigned(p.received.value):0;
        if(hint && !std::binary_search(small_ids.begin(),small_ids.end(),hint))hint=0;
        if(field==StateField::HOLD)initial_template.hand=hint;else initial_template.plate=hint;
        if(!known) {
            PublicPriorFactor f;f.field=field==StateField::HOLD?PriorField::HAND:PriorField::PLATE;
            f.values={{int(hint),.8}};
            std::vector<unsigned> alternatives={0};alternatives.insert(alternatives.end(),small_ids.begin(),small_ids.end());
            alternatives.erase(std::remove(alternatives.begin(),alternatives.end(),hint),alternatives.end());
            if(alternatives.empty())f.values.front().probability=1;
            else for(unsigned id:alternatives)f.values.push_back({int(id),.2/alternatives.size()});
            factors.push_back(f);
        }
    }
    modal=initial_template;modal.freezeSdkReplyDomain();
    auto scenes=EpisodePrior::generate(initial_template,factors,model.constraints.size(),64);
    std::set<LocationHypothesis> answers;
    for(int loc:initial_template.locations)answers.insert({'a',loc});
    for(const auto& object:initial_template.objects)if(object.second.container)answers.insert({'i',int(object.first)});
    ask=AskObservationModel(answers,.6,.3,.1,0);
    replay.reset(new EpisodeReplay(EpisodeBelief(std::move(scenes.scenes))));
    LOG("[FullModel] prior_scope=%s assignments=%zu samples=%zu variables=%zu calibrated=false\n",scenes.scope.c_str(),scenes.assignments,scenes.draws,factors.size());
}
bool FullModelController::qualify(ActionPermit& p) const {
    if(!selecting || !policy || policy->stop || p.action!=actionName(policy->action.kind) ||
       p.arguments!=arguments(policy->action) || p.state_signature!=expected_signature)return false;
    p.policy=decision;p.selection_reason="full_joint_public_feedback_policy";
    // Nonrepresented feedback has an explicit STOP fallback and support-miss
    // accounting. This is execution completeness, not certified prior coverage.
    p.branches_complete=true;
    for(auto& e:p.evidence)if(e.source==std::to_string(int(EvidenceSource::CONSTRAINT_DERIVED)) ||
        e.source==std::to_string(int(EvidenceSource::CONSTRAINT_HEURISTIC))) {
        e.confirmed=false;p.kind=PermitKind::MODELED_PROBE;
    }
    if(p.kind!=PermitKind::CONFIRMED)p.kind=PermitKind::MODELED_PROBE;
    return true;
}
bool FullModelController::dispatch(const JointAction& a) {
    auto& w=owner;w.isPass=false;
    switch(a.kind) {
    case JointActionKind::MOVE:return w.Move(a.a);case JointActionKind::PICKUP:return w.PickUp(a.a);
    case JointActionKind::PUTDOWN:return w.PutDown(a.a);case JointActionKind::TOPLATE:return w.ToPlate(a.a);
    case JointActionKind::FROMPLATE:return w.FromPlate(a.a);case JointActionKind::OPEN:return w.Open(a.a);
    case JointActionKind::CLOSE:return w.Close(a.a);case JointActionKind::PUTIN:return w.PutIn(a.a,a.b);
    case JointActionKind::TAKEOUT:return w.TakeOut(a.a,a.b);
    case JointActionKind::SENSE:w.SenseCurrentLocationOnly(true);return true;
    case JointActionKind::ASK:w.AskLoc(a.a);++asked[a.a];return true;
    }
    throw std::logic_error("unmapped model dispatch");
}
JointObservation FullModelController::feedback(const JointAction& action,const ActionReceipt& r) const {
    JointObservation o;
    if(action.kind==JointActionKind::SENSE) {
        o.kind=JointObservation::Kind::VISIBLE;
        std::regex id("[0-9]+");auto text=r.public_feedback;
        for(std::sregex_iterator i(text.begin(),text.end(),id),end;i!=end;++i)o.ids.insert(unsigned(std::stoul(i->str())));
    } else if(action.kind==JointActionKind::ASK) {
        o.kind=JointObservation::Kind::ANSWER;std::smatch match;
        if(std::regex_match(r.public_feedback,match,std::regex("(at|inside)\\(([0-9]+),([0-9]+)\\)")) && std::stoul(match[2])==action.a)
            o.reply={match[1]=="at"?'a':'i',std::stoi(match[3])};
        else if(r.public_feedback!="not_known")throw std::logic_error("unmodeled public answer format");
    } else o.success=r.outcome==ExecutionStatus::SUCCEEDED;
    return o;
}
void FullModelController::run() {
    auto& w=owner;
    auto began=std::chrono::steady_clock::now();initialize();cpu_used+=std::chrono::steady_clock::now()-began;
    w.execution_evidence.reset(true);
    for(unsigned step=0;step<96 && !w.deadline_manager.deadlineReached();++step) {
        if(w.deadline_manager.remaining()<=w.plan_safety_margin+std::chrono::milliseconds(150))break;
        if(!policy || policy->stop) {
            if(cpu_used>=std::chrono::milliseconds(250))break;
            began=std::chrono::steady_clock::now();
            SdkEpisode modal_episode;modal_episode.world=modal;modal_episode.credits.assign(model.constraints.size(),true);
            auto proposals=EpisodeRouter::propose(EpisodeBelief({{modal_episode,1}}),model,1024,std::chrono::milliseconds(10));
            auto adaptive=EpisodeRouter::propose(replay->belief(),model,2048,std::chrono::milliseconds(10));
            proposals.routes.insert(proposals.routes.end(),adaptive.routes.begin(),adaptive.routes.end());
            std::vector<JointAction> observations={{JointActionKind::SENSE}};
            for(const auto& goal:model.goals)for(const auto& binding:goal.bindings)
                if(asked[binding.first]<3)observations.push_back({JointActionKind::ASK,binding.first});
            const auto already=std::chrono::steady_clock::now()-began;
            const auto allowance=std::min(std::chrono::milliseconds(30),
                std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::milliseconds(250)-cpu_used-already));
            if(allowance.count()<=0)break;
            const auto plan=EpisodeRouteSearch::solve(replay->belief(),model,proposals.routes,observations,ask,
                w.deadline_manager.remaining()-w.plan_safety_margin,8192-proposals.transitions-adaptive.transitions,allowance);
            policy=plan.policy;++decision;cpu_used+=std::chrono::steady_clock::now()-began;
            LOG("[FullModel] decision=%zu lower=%.6f upper=%.6f routes=%zu transitions=%zu wall_cut=%s work_cut=%s model_ms=%lld\n",
                decision,plan.value.lower,plan.value.upper,proposals.routes.size(),plan.transitions+proposals.transitions+adaptive.transitions,
                plan.wall_cut?"true":"false",plan.work_cut?"true":"false",(long long)std::chrono::duration_cast<std::chrono::milliseconds>(cpu_used).count());
            if(policy->stop)break;
        }
        const auto action=policy->action;expected_signature=w.PlanStateSignature();selecting=true;
        const auto before=w.ActionReceipts().size();
        try{dispatch(action);}catch(...) {selecting=false;throw;}
        selecting=false;
        if(w.ActionReceipts().size()!=before+1)throw std::logic_error("model command has no unique committed receipt");
        const auto& receipt=w.ActionReceipts().back();
        if(receipt.outcome==ExecutionStatus::INDETERMINATE || !receipt.state_committed)break;
        const auto observation=feedback(action,receipt);
        began=std::chrono::steady_clock::now();
        const auto update=replay->observe(model,action,observation,ask,receipt.id);
        if(update==EpisodeUpdate::SUPPORT_MISS) {
            LOG("[FullModel] support_miss receipt=%zu action=%s paid_once=true fallback=stop\n",receipt.id,actionName(action.kind));
            const auto extra=EpisodePrior::generate(initial_template,factors,model.constraints.size(),128,4096+receipt.id*128);
            const auto repaired=replay->repair(model,ask,extra.scenes,8192,std::chrono::milliseconds(20));
            LOG("[FullModel] support_repair installed=%s transitions=%zu reason=%s\n",repaired.installed?"true":"false",repaired.transitions,repaired.reason.c_str());
            policy.reset();cpu_used+=std::chrono::steady_clock::now()-began;
            if(!repaired.installed)break;
            continue;
        }
        auto child=policy->children.find(observation);
        policy=child==policy->children.end()?std::make_shared<EpisodePolicy>():child->second;
        const auto& support=replay->belief().support();
        if(!support.empty())modal=std::max_element(support.begin(),support.end(),
            [](const WeightedEpisode& a,const WeightedEpisode& b){return a.weight<b.weight;})->episode.world;
        cpu_used+=std::chrono::steady_clock::now()-began;
    }
    w.normal_stop_requested=true;LOG("[FullModel] stopped receipts=%zu model_ms=%lld\n",w.ActionReceipts().size(),
        (long long)std::chrono::duration_cast<std::chrono::milliseconds>(cpu_used).count());
}
