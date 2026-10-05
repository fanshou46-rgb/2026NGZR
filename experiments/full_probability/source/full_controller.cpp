#include "full_controller.hpp"
#include "rdfw.hpp"
#include "episode_conditioner.hpp"
#include "episode_proposal.hpp"
#include "public_prior_parameters.hpp"
#include <algorithm>
#include <cmath>
#include <regex>
#include <sstream>
#include <iomanip>
#include <stdexcept>
using namespace _home;
namespace {
SdkPredicate ground(const Instruction& instruction,const RDFW& w) {
    SdkPredicate p;p.verb=instruction.behave;
    auto xs=instruction.X,ys=instruction.Y;
    if(!instruction.conditionX.sort.empty() || !instruction.conditionX.color.empty()) {
        xs.clear();for(const auto& object:w.objects)if(object && object->id>0 && instruction.conditionX.IsObjectSatisfy(object))xs.push_back(object);
    }
    if(!instruction.conditionY.sort.empty() || !instruction.conditionY.color.empty()) {
        ys.clear();for(const auto& object:w.objects)if(object && object->id>0 && instruction.conditionY.IsObjectSatisfy(object))ys.push_back(object);
    }
    for(const auto& x:xs)if(x) {
        if(p.verb=="give"){if(w.human)p.bindings.push_back({x->id,w.human->id});}
        else if(ys.empty())p.bindings.push_back({x->id,0});
        else for(const auto& y:ys)if(y)p.bindings.push_back({x->id,y->id});
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
std::string policyJson(const std::shared_ptr<EpisodePolicy>& p) {
    if(!p || p->stop)return "{\"stop\":true}";
    std::ostringstream s;s<<std::setprecision(17)<<"{\"action\":"<<ExecutionEvidence::jsonString(actionName(p->action.kind))<<",\"args\":[";
    const auto args=arguments(p->action);
    for(std::size_t i=0;i<args.size();++i){if(i)s<<',';s<<args[i];}
    s<<"],\"cost\":"<<p->action.cost()<<",\"unexpected\":{\"stop\":true},\"children\":[";
    bool first=true;
    for(const auto& child:p->children) {
        if(!first)s<<',';first=false;const auto& o=child.first;
        s<<"{\"kind\":"<<int(o.kind)<<",\"success\":"<<(o.success?"true":"false")<<",\"ids\":[";
        bool id_first=true;for(unsigned id:o.ids){if(!id_first)s<<',';id_first=false;s<<id;}
        s<<"],\"reply\":["<<ExecutionEvidence::jsonString(std::string(1,o.reply.first))<<','<<o.reply.second<<"],\"probability\":";
        auto probability=p->probabilities.find(o);s<<(probability==p->probabilities.end()?0:probability->second);
        s<<",\"node\":"<<policyJson(child.second)<<'}';
    }
    s<<"]}";return s.str();
}
}
FullModelController::FullModelController(RDFW& w):owner(w),ask({{'a',0}},.6,.3,.1,0) {}
void FullModelController::initialize() {
    auto& w=owner;
    if(!w.ActionReceipts().empty())throw std::logic_error("full policy must own SDK calls from episode start");
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
    for(const auto& goal:model.goals)for(const auto& binding:goal.bindings) {
        required_objects.insert(binding.first);if(binding.second)required_objects.insert(binding.second);
    }
    const auto direct_objects=required_objects;
    for(unsigned id:direct_objects)for(const auto& edge:w.Provenance(StateField::INSIDE,id).inside_edges)
        if(edge.second.value==1)required_objects.insert(edge.first);
    LOG("[FullModel] missing_location_policy=bounded_public_input_coverage max_queries_per_object=3 canonical_at_from_answer=false\n");
    initial_template.robot=w.FactLocation(0);
    if(initial_template.robot<0)throw std::logic_error("robot position is not confirmed");
    initial_template.locations.insert(initial_template.robot);
    for(const auto& object:w.objects)if(object && object->id>0) {
        const auto& p=w.Provenance(StateField::LOCATION,object->id);
        if(p.received.present && p.received.value>=0)initial_template.locations.insert(p.received.value);
        if(w.FactLocation(object->id)>=0)initial_template.locations.insert(w.FactLocation(object->id));
    }
    // Candidate locations are not confirmed SDK loc facts. Missing big-object
    // positions need positive off-site hypotheses before the first Sense;
    // otherwise a singleton public site makes absence logically inexplicable.
    // Numeric gaps/neighbours are an explicitly finite coverage heuristic.
    bool missing_required=false;
    for(const auto& object:w.objects)if(object && object->id>0 &&
        !std::dynamic_pointer_cast<SmallObject>(object) && required_objects.count(object->id)) {
        const auto& p=w.Provenance(StateField::LOCATION,object->id);
        if(w.stage!=1 && !strong(w,StateField::LOCATION,object->id) && (!p.received.present || p.received.value<0)) {
            initial_missing_big.insert(object->id);missing_required=true;
            LOG("[InitialMissingLocation] object=%u required=true received_at=false source=public_input_absence\n",object->id);
        }
    }
    if(missing_required) {
        const auto public_sites=initial_template.locations;
        const int maximum=*public_sites.rbegin();
        if(maximum<=63)for(int site=0;site<=maximum+1;++site)initial_template.locations.insert(site);
        else for(int site:public_sites) {
            if(site>0)initial_template.locations.insert(site-1);
            if(site<4095)initial_template.locations.insert(site+1);
        }
        LOG("[FullModel] candidate_domain_refinement=public_numeric_neighbours scope=uncalibrated_finite_coverage sites=%zu\n",initial_template.locations.size());
    }
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
                const double confidence=p.received.present?DevelopmentPublicPrior::doorHint():.5;
                f.values={{opened?1:0,confidence},{opened?0:1,1-confidence}};factors.push_back(f);
            }
        }
        if(w.stage!=1 && !strong(w,StateField::LOCATION,id)) {
            PublicPriorFactor f;f.field=PriorField::EXPLICIT_AT;f.object=id;
            if(!position.received.present || position.received.value<0) {
                // Missing at and supplied inside are distinct PUBLIC patterns.
                // Inside never logically excludes independent at: both retain
                // positive prior probability and use the same SDK transitions.
                bool received_inside=false;
                for(const auto& edge:w.Provenance(StateField::INSIDE,id).inside_edges)
                    received_inside|=edge.second.value==1;
                const double absent=small?DevelopmentPublicPrior::absentAt(received_inside):0;
                for(int loc:initial_template.locations)f.values.push_back({loc,(1-absent)/initial_template.locations.size()});
                if(small)f.values.push_back({-1,absent});
                factors.push_back(f);continue;
            }
            std::vector<int> alternatives;
            for(int loc:initial_template.locations)if(loc!=at)alternatives.push_back(loc);
            if(small && at!=-1)alternatives.push_back(-1);
            if(alternatives.empty())f.values={{at,1}};
            else {
                const double confidence=DevelopmentPublicPrior::locationHint(small);
                f.values.push_back({at,confidence});
                for(int loc:alternatives)f.values.push_back({loc,(1-confidence)/alternatives.size()});
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
            const double confidence=DevelopmentPublicPrior::insideHint(present);
            f.values={{present?1:0,confidence},{present?0:1,1-confidence}};factors.push_back(f);
        }
    }
    for(auto field:{StateField::HOLD,StateField::PLATE}) {
        const bool known=strong(w,field,0);const auto& p=w.Provenance(field,0);
        unsigned hint=known?unsigned(w.FactValue(field)):p.received.present && p.received.value>0?unsigned(p.received.value):0;
        if(hint && !std::binary_search(small_ids.begin(),small_ids.end(),hint))hint=0;
        if(field==StateField::HOLD)initial_template.hand=hint;else initial_template.plate=hint;
        if(!known) {
            PublicPriorFactor f;f.field=field==StateField::HOLD?PriorField::HAND:PriorField::PLATE;
            const double confidence=p.received.present?DevelopmentPublicPrior::slotHint():.5;
            f.values={{int(hint),confidence}};
            std::vector<unsigned> alternatives={0};alternatives.insert(alternatives.end(),small_ids.begin(),small_ids.end());
            alternatives.erase(std::remove(alternatives.begin(),alternatives.end(),hint),alternatives.end());
            if(alternatives.empty())f.values.front().probability=1;
            else for(unsigned id:alternatives)f.values.push_back({int(id),(1-confidence)/alternatives.size()});
            factors.push_back(f);
        }
    }
    modal=initial_template;modal.freezeSdkReplyDomain();
    auto scenes=EpisodePrior::generate(initial_template,factors,model.constraints.size(),64,0,true);
    std::set<LocationHypothesis> answers;
    for(int loc:initial_template.locations)answers.insert({'a',loc});
    for(const auto& object:initial_template.objects)if(object.second.container)answers.insert({'i',int(object.first)});
    ask=AskObservationModel(answers,.6,.3,.1,0).withPersistentAnswerOrderPrior();
    LOG("[FullModel] truthful_answer_order=uncalibrated_persistent_rank_prior blank_answer=distinct_from_not_known\n");
    replay.reset(new EpisodeReplay(EpisodeBelief(std::move(scenes.scenes))));
    LOG("[FullModel] prior_scope=%s assignments=%zu samples=%zu variables=%zu calibration=initial_fields_development_02 feedback_calibrated=false holdout_validated=false\n",scenes.scope.c_str(),scenes.assignments,scenes.draws,factors.size());
}
bool FullModelController::selectMissingLocationObservation() {
    coverage_policy=false;
    for(unsigned id:initial_missing_big) {
        if(strong(owner,StateField::LOCATION,id) || asked[id]>=3)continue;
        bool supported_clue=false;
        auto clue=coverage_clues.find(id);
        if(clue!=coverage_clues.end() && clue->second.first=='a') {
            double mass=0;
            for(const auto& state:replay->belief().support())
                if(state.episode.world.truthfulReplies(id).count(clue->second))mass+=state.weight;
            supported_clue=mass>1e-12;
        }
        if(asked[id]>0 && supported_clue)continue;
        // Required public-domain coverage, analogous to initial perception.
        // This does not claim a profitable finite-catalogue value or confirm
        // the answer. Every modeled reply pays its fee and initially stops;
        // an actual reply can refine the prior and trigger a new decision.
        policy=std::make_shared<EpisodePolicy>();policy->stop=false;
        coverage_policy=true;
        policy->action={JointActionKind::ASK,id};++decision;
        const auto stopping=replay->belief().reward(model);SdkRewardBounds paid;
        for(const auto& branch:replay->belief().branches(model,policy->action,ask)) {
            policy->children.emplace(branch.observation,std::make_shared<EpisodePolicy>());
            policy->probabilities.emplace(branch.observation,branch.probability);
            const auto value=branch.posterior.reward(model);
            paid.lower+=branch.probability*value.lower;paid.upper+=branch.probability*value.upper;
        }
        LOG("[FullDecisionEvidence] decision=%zu stop_lower=%.9f stop_upper=%.9f selected_lower=%.9f selected_upper=%.9f support=%zu information_candidates=1 selected_stop=false scope=necessary_initial_missing_big_location target=%u attempts_before=%u initial_at_missing=true\n",
            decision,stopping.lower,stopping.upper,paid.lower,paid.upper,replay->belief().support().size(),id,asked[id]);
        return true;
    }
    return false;
}
bool FullModelController::refineLocationDomain(const JointAction& action,const JointObservation& observation,std::size_t receipt) {
    if(action.kind!=JointActionKind::ASK)return false;
    if(initial_missing_big.count(action.a))coverage_clues[action.a]=observation.reply;
    if(observation.reply.first!='a' || observation.reply.second<0 || observation.reply.second>4095 ||
        initial_template.locations.count(observation.reply.second))return false;
    const int site=observation.reply.second;initial_template.locations.insert(site);
    std::size_t variables=0;
    for(auto& factor:factors)if(factor.field==PriorField::EXPLICIT_AT) {
        // Approximate domain extension, never an object-specific hard at.
        // All unresolved initial AT variables retain their old alternatives;
        // full paid-history replay determines which world explains the reply.
        for(auto& value:factor.values)value.probability*=.95;
        factor.values.push_back({site,.05});++variables;
    }
    ask=ask.withReply(observation.reply);
    LOG("[FullDomainEvidence] receipt=%zu query=%u location=%d refined_variables=%zu added_prior_mass=0.05 canonical_at_written=false scope=approximate_prior_domain_extension\n",
        receipt,action.a,site,variables);
    return true;
}
bool FullModelController::qualify(ActionPermit& p) const {
    if(!selecting || !policy || policy->stop || p.action!=actionName(policy->action.kind) ||
       p.arguments!=arguments(policy->action) || p.state_signature!=expected_signature)return false;
    p.policy=decision;p.selection_reason=coverage_policy?"necessary_public_missing_location_coverage":"full_joint_public_feedback_policy";
    // Nonrepresented feedback has an explicit STOP fallback and support-miss
    // accounting. This is execution completeness, not certified prior coverage.
    p.branches_complete=true;
    for(auto& e:p.evidence)if(e.source==std::to_string(int(EvidenceSource::CONSTRAINT_DERIVED)) ||
        e.source==std::to_string(int(EvidenceSource::CONSTRAINT_HEURISTIC)) ||
        e.source==std::to_string(int(EvidenceSource::RELATION_DERIVED)) ||
        e.source==std::to_string(int(EvidenceSource::UNKNOWN))) {
        e.confirmed=false;p.kind=PermitKind::MODELED_PROBE;
    }
    if(p.kind!=PermitKind::CONFIRMED)p.kind=PermitKind::MODELED_PROBE;
    return true;
}
void FullModelController::logSelectedPolicy() {
    if(!policy || policy->stop)throw std::logic_error("cannot record a Stop as an actual SDK command");
    if(logged_decision!=decision) {
        logged_nodes.clear();
        // Stable preorder follows public observation edges. These IDs are
        // catalogue references only and never identify a hidden world.
        std::function<void(const std::shared_ptr<EpisodePolicy>&)> index;
        index=[&](const std::shared_ptr<EpisodePolicy>& node) {
            if(!node || node->stop)return;
            if(logged_nodes.count(node.get()))throw std::logic_error("policy catalogue must be an observation tree");
            const auto id=logged_nodes.size()+1;logged_nodes.emplace(node.get(),id);
            for(const auto& branch:node->children)index(branch.second);
        };
        index(policy);const auto json=policyJson(policy);
        logged_policy_digest=ExecutionEvidence::digest(json);
        LOG("[FullPolicyCatalogue] {\"schema\":\"full_policy_catalogue.v2\",\"decision\":%zu,\"digest\":%llu,\"root\":%s}\n",
            decision,(unsigned long long)logged_policy_digest,json.c_str());
        logged_decision=decision;
    }
    const auto node=logged_nodes.find(policy.get());
    if(node==logged_nodes.end())throw std::logic_error("selected suffix is absent from committed policy catalogue");
    LOG("[FullPolicy] {\"schema\":\"full_policy.v2\",\"decision\":%zu,\"receipt\":%zu,\"before\":%llu,\"prior_scope\":\"finite_public_domain_estimate\",\"catalogue\":%llu,\"node\":%zu}\n",
        decision,owner.ActionReceipts().size()+1,(unsigned long long)ExecutionEvidence::digest(expected_signature),
        (unsigned long long)logged_policy_digest,node->second);
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
        else if(r.public_feedback.empty())o.reply={'!',-1};
        else if(r.public_feedback!="not_known")throw std::logic_error("unmodeled public answer format");
    } else o.success=r.outcome==ExecutionStatus::SUCCEEDED;
    return o;
}
void FullModelController::run() {
    auto& w=owner;
    std::string stop_reason="step_or_deadline_limit";
    auto began=std::chrono::steady_clock::now();initialize();cpu_used+=std::chrono::steady_clock::now()-began;
    w.execution_evidence.reset(true);
    began=std::chrono::steady_clock::now();
    // Necessary initial perception is explicit and precedes profitable route
    // selection. Its fee and raw feedback enter the same persistent episode.
    policy=std::make_shared<EpisodePolicy>();policy->stop=false;policy->action={JointActionKind::SENSE};decision=1;
    for(const auto& branch:replay->belief().branches(model,policy->action,ask)) {
        policy->children.emplace(branch.observation,std::make_shared<EpisodePolicy>());
        policy->probabilities.emplace(branch.observation,branch.probability);
    }
    cpu_used+=std::chrono::steady_clock::now()-began;
    for(unsigned step=0;step<96 && !w.deadline_manager.deadlineReached();++step) {
        if(w.deadline_manager.remaining()<=w.plan_safety_margin+std::chrono::milliseconds(150)){stop_reason="remaining_time_guard";break;}
        if(!policy || policy->stop) {
            if(cpu_used>=std::chrono::milliseconds(250)){stop_reason="cumulative_model_budget";break;}
            began=std::chrono::steady_clock::now();
            const bool coverage_observation=selectMissingLocationObservation();
            if(coverage_observation) {
                cpu_used+=std::chrono::steady_clock::now()-began;
            } else {
                SdkEpisode modal_episode;modal_episode.world=modal;modal_episode.credits.assign(model.constraints.size(),true);
                auto proposals=EpisodeRouter::propose(EpisodeBelief({{modal_episode,1}}),model,1024,std::chrono::milliseconds(10));
                auto adaptive=EpisodeRouter::propose(replay->belief(),model,2048,std::chrono::milliseconds(10));
                proposals.routes.insert(proposals.routes.end(),adaptive.routes.begin(),adaptive.routes.end());
                std::vector<JointAction> observations;
                const auto& states=replay->belief().support();
                if(!states.empty()) {
                    const auto visible=states.front().episode.world.visible();bool differs=false;
                    for(const auto& state:states)differs|=state.episode.world.visible()!=visible;
                    if(differs)observations.push_back({JointActionKind::SENSE});
                }
                const auto& targets=required_objects;
                for(unsigned id:targets)if(asked[id]<3 && !states.empty()) {
                    const auto truth=states.front().episode.world.truthfulReplies(id);bool differs=false;
                    for(const auto& state:states)differs|=state.episode.world.truthfulReplies(id)!=truth;
                    if(differs)observations.push_back({JointActionKind::ASK,id});
                }
                const auto already=std::chrono::steady_clock::now()-began;
                const auto allowance=std::min(std::chrono::milliseconds(50),
                    std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::milliseconds(250)-cpu_used-already));
                if(allowance.count()<=0){stop_reason="no_remaining_search_budget";break;}
                const auto plan=EpisodeRouteSearch::solve(replay->belief(),model,proposals.routes,observations,ask,
                    w.deadline_manager.remaining()-w.plan_safety_margin,8192-proposals.transitions-adaptive.transitions,allowance);
                policy=plan.policy;++decision;
                const auto stopping=replay->belief().reward(model);
                LOG("[FullModel] decision=%zu lower=%.6f upper=%.6f routes=%zu transitions=%zu prefix_cache_hits=%zu wall_cut=%s work_cut=%s model_ms=%lld\n",
                    decision,plan.value.lower,plan.value.upper,proposals.routes.size(),plan.transitions+proposals.transitions+adaptive.transitions,
                    plan.prefix_cache_hits,
                    plan.wall_cut?"true":"false",plan.work_cut?"true":"false",(long long)std::chrono::duration_cast<std::chrono::milliseconds>(cpu_used+std::chrono::steady_clock::now()-began).count());
                LOG("[FullDecisionEvidence] decision=%zu stop_lower=%.9f stop_upper=%.9f selected_lower=%.9f selected_upper=%.9f support=%zu information_candidates=%zu selected_stop=%s scope=finite_catalogue_complete_candidates\n",
                    decision,stopping.lower,stopping.upper,plan.value.lower,plan.value.upper,replay->belief().support().size(),observations.size(),policy->stop?"true":"false");
                cpu_used+=std::chrono::steady_clock::now()-began;
                if(policy->stop){stop_reason="no_profitable_complete_candidate";break;}
            }
        }
        began=std::chrono::steady_clock::now();
        const auto action=policy->action;expected_signature=w.PlanStateSignature();selecting=true;
        logSelectedPolicy();
        cpu_used+=std::chrono::steady_clock::now()-began;
        const auto before=w.ActionReceipts().size();
        const auto dispatch_began=std::chrono::steady_clock::now();
        try{dispatch(action);}catch(const std::exception& error) {
            selecting=false;
            LOG_ERROR("[FullModel] stopped_after_dispatch_exception action=%s reason=%s receipts=%zu",actionName(action.kind),error.what(),w.ActionReceipts().size());
            stop_reason="dispatch_exception";
            break;
        }
        selecting=false;
        if(w.ActionReceipts().size()!=before+1)throw std::logic_error("model command has no unique committed receipt");
        const auto& receipt=w.ActionReceipts().back();
        sdk_ns+=std::max(0LL,receipt.sdk_ns);
        dispatch_overhead+=std::chrono::steady_clock::now()-dispatch_began-std::chrono::nanoseconds(std::max(0LL,receipt.sdk_ns));
        if(receipt.outcome==ExecutionStatus::INDETERMINATE || !receipt.state_committed){stop_reason="indeterminate_or_uncommitted_outcome";break;}
        began=std::chrono::steady_clock::now();
        const auto observation=feedback(action,receipt);
        const bool refined_domain=refineLocationDomain(action,observation,receipt.id);
        const auto update=replay->observe(model,action,observation,ask,receipt.id);
        if(update==EpisodeUpdate::SUPPORT_MISS || refined_domain) {
            LOG("[FullModel] support_miss receipt=%zu action=%s paid_once=true fallback=stop\n",receipt.id,actionName(action.kind));
            const auto conditioned=EpisodeConditioner::initial(initial_template,factors,replay->evidence());
            LOG("[FullModel] initial_conditioning consistent=%s proof_count=%zu retained_mass=%.17g\n",
                conditioned.consistent?"true":"false",conditioned.proofs.size(),conditioned.retained_prior_mass);
            for(const auto& proof:conditioned.proofs)LOG("[InitialFactorProof] field=%d object=%u parent=%u receipt=%zu predicate=%s\n",
                int(proof.field),proof.object,proof.parent,proof.receipt,proof.predicate.c_str());
            if(!conditioned.consistent){cpu_used+=std::chrono::steady_clock::now()-began;stop_reason="public_evidence_excludes_initial_domain";break;}
            const auto proposal_time=std::min(std::chrono::milliseconds(30),
                std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::milliseconds(250)-cpu_used-(std::chrono::steady_clock::now()-began)));
            if(proposal_time.count()<=0){cpu_used+=std::chrono::steady_clock::now()-began;stop_reason="no_remaining_proposal_budget";break;}
            const auto extra=EpisodeProposal::generate(initial_template,conditioned.factors,replay->evidence(),
                model.constraints.size(),32,4096+receipt.id*128,262144,proposal_time);
            LOG("[FullModel] conditional_proposal complete=%s particles=%zu checks=%zu block_cache_hits=%zu work_cut=%s wall_cut=%s scope=%s\n",
                extra.complete?"true":"false",extra.scenes.size(),extra.checks,extra.block_cache_hits,extra.work_cut?"true":"false",
                extra.wall_cut?"true":"false",extra.scope.c_str());
            if(!extra.complete || extra.scenes.empty()){cpu_used+=std::chrono::steady_clock::now()-began;stop_reason="conditional_proposal_unavailable";break;}
            const auto repair_time=std::min(std::chrono::milliseconds(20),
                std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::milliseconds(250)-cpu_used-(std::chrono::steady_clock::now()-began)));
            if(repair_time.count()<=0){cpu_used+=std::chrono::steady_clock::now()-began;stop_reason="no_remaining_replay_budget";break;}
            const auto repaired=replay->repair(model,ask,extra.scenes,8192,repair_time);
            LOG("[FullModel] support_repair installed=%s transitions=%zu reason=%s\n",repaired.installed?"true":"false",repaired.transitions,repaired.reason.c_str());
            policy.reset();cpu_used+=std::chrono::steady_clock::now()-began;
            if(!repaired.installed){stop_reason=repaired.reason;break;}
            const auto& repaired_support=replay->belief().support();
            if(!repaired_support.empty())modal=std::max_element(repaired_support.begin(),repaired_support.end(),
                [](const WeightedEpisode& a,const WeightedEpisode& b){return a.weight<b.weight;})->episode.world;
            continue;
        }
        auto child=policy->children.find(observation);
        policy=child==policy->children.end()?std::make_shared<EpisodePolicy>():child->second;
        const auto& support=replay->belief().support();
        if(!support.empty())modal=std::max_element(support.begin(),support.end(),
            [](const WeightedEpisode& a,const WeightedEpisode& b){return a.weight<b.weight;})->episode.world;
        cpu_used+=std::chrono::steady_clock::now()-began;
    }
    w.normal_stop_requested=true;LOG("[FullModel] stopped receipts=%zu model_ms=%lld sdk_ms=%.6f dispatch_overhead_ms=%lld\n",w.ActionReceipts().size(),
        (long long)std::chrono::duration_cast<std::chrono::milliseconds>(cpu_used).count(),sdk_ns/1000000.0,
        (long long)std::chrono::duration_cast<std::chrono::milliseconds>(dispatch_overhead).count());
    LOG("[FullStopEvidence] reason=%s remaining_ms=%lld model_ns=%lld prior_coverage_certified=false\n",stop_reason.c_str(),
        (long long)w.deadline_manager.remaining().count(),(long long)std::chrono::duration_cast<std::chrono::nanoseconds>(cpu_used).count());
}
