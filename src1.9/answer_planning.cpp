#include "rdfw.hpp"
#include <algorithm>
#include <limits>
#include <sstream>
using namespace _home;

AskObservationModel RDFW::AskModel() const {
    std::set<LocationHypothesis> replies;
    // Random SDK replies can name a container even for a big object. Observation
    // support is deliberately separate from physically possible world support.
    for (const auto& object:objects) if(object) {
        if(object->location>=0) replies.insert({'a',object->location});
        if(object->id>0 && dynamic_cast<Container*>(object.get())) replies.insert({'i',object->id});
    }
    return AskObservationModel(replies);
}

CandidatePlan RDFW::ProjectVerification(unsigned id,LocationHypothesis h,std::size_t task) {
    if (!IsValidObjectId(id) || h.first=='?') return {};
    int destination=h.second;
    auto small=dynamic_pointer_cast<SmallObject>(GetObject(id));
    auto container=h.first=='i'?dynamic_pointer_cast<Container>(GetObject(h.second)):nullptr;
    if (h.first=='i') {
        if(!small || !container || FactLocation(h.second)==UNKNOWN || FactContainerState(h.second)==UNKNOWN ||
            FactValue(StateField::HOLD)!=NONE) return {};
        destination=FactLocation(h.second);
    }
    return BuildTaskGroupPlan({task},false,0,false,UNKNOWN,0,[&,destination]() {
        if (!shadow_dry_run) throw std::logic_error("scenario requires SDK isolation");
        // The branch world is an assumption; it lives only inside this snapshot.
        StateMutation mutation(*this);
        ApplyStateValue(StateField::LOCATION,id,destination,false,EvidenceSource::ASK_ANSWER);
        if(small) {
            ClearContainerMembership(small);
            ApplyStateValue(StateField::INSIDE,id,h.first=='i'?h.second:NONE,false,EvidenceSource::ASK_ANSWER);
        }
        if (location!=destination && !Move(destination)) return false;
        if (container && container->isOpen==0 && !Open(h.second)) return false;
        RecordAction(ActionCategory::OBSERVATION,"Sense",{});
        MarkDirectLocationEvidence(id,true,EvidenceSource::SENSE);
        // A visible object next to an open container does not prove outside.
        bool ambiguous=false;
        for(const auto& object:objects) {
            auto c=dynamic_pointer_cast<Container>(object);
            if(c && c->location==destination && FactContainerState(c->id)!=0) ambiguous=true;
        }
        if (small && !container && !ambiguous) SetInsideEvidence(id,true,EvidenceSource::SENSE);
        if (container) {
            // Sense does not confirm INSIDE. A successful physical TakeOut does.
            if(!TakeOut(id,h.second)) return false;
        }
        return true;
    });
}

void RDFW::EvaluateAskBranches(ProbeCandidate& probe) {
    if(probe.kind!=ProbeKind::ASK_LOCATION) return;
    probe.answer_branches_evaluated=true;
    const auto belief=BeliefFor(probe.target_object);
    std::vector<std::pair<LocationHypothesis,double>> support(belief.distribution().begin(),belief.distribution().end());
    std::sort(support.begin(),support.end(),[](const std::pair<LocationHypothesis,double>& a,
                                            const std::pair<LocationHypothesis,double>& b) {
        return a.second!=b.second?a.second>b.second:a.first<b.first;
    });
    // Past action cost cancels in every marginal score. Using the full execution
    // signature would invalidate the cache after every not_known answer.
    std::ostringstream key;key<<probe.target_object<<':'<<DecisionProgressSignature()<<':'<<ProbeFactContext(probe);
    key<<':'<<solved_task_num<<':'<<isPass<<':'<<isKeepConstrain<<':'<<isMultiGotoMode
       <<':'<<isAutoConstrain<<':'<<isAskTwice<<':'<<isErrorCorrection;
    for(unsigned id=0;id<objects.size();++id) if(objects[id]) {
        key<<":object:"<<id<<':'<<objects[id]->is_keep<<':'<<objects[id]->unable_site;
        for(auto field:{StateField::LOCATION,StateField::INSIDE,StateField::CONTAINER_STATE,StateField::HOLD,StateField::PLATE})
            key<<':'<<FactValue(field,id)<<':'<<DependenciesCurrent(field,id)<<':'<<HasContradictoryEvidence(field,id);
    }
    for(std::size_t i=0;i<tasks.size();++i) key<<":taskstate:"<<tasks[i].isEnable<<tasks[i].isfalse<<tasks[i].isMultiPuton
        <<':'<<tasks[i].ask_times<<':'<<(i<task_attempts.size()?task_attempts[i]:0)
        <<':'<<(i<failed_task_revision.size() && failed_task_revision[i]==world_revision);
    for(auto loc:score_locations) key<<":scoreloc:"<<loc;
    for(auto task:probe.task_indices) key<<":task:"<<task;
    for(const auto& history:probe_history) if(history.first.find("ask:")!=0)
        key<<":history:"<<history.first<<':'<<history.second.attempts<<':'<<history.second.world_revision
           <<':'<<history.second.related_new_evidence<<':'<<history.second.context_after;
    for(auto risk:probe_authorized_constraint_risks) key<<":risk:"<<risk;
    const auto cache_key=key.str();auto cached=answer_route_cache.find(cache_key);
    if(cached!=answer_route_cache.end()) {
        for(const auto& route:cached->second) if(route.feasible) {
            auto reusable=route;
            const int destination=route.hypothesis.first=='i'?FactLocation(route.hypothesis.second):route.hypothesis.second;
            const int prefix_cost=1+(destination!=location?4:0)+
                (route.hypothesis.first=='i' && FactContainerState(route.hypothesis.second)==0?2:0);
            // Old action cost cancels in reward, but remaining authorization
            // budget changes after an Ask. Reuse the proof, recheck this limit.
            if(!probe_closed_reason.empty() || probe_cost_spent+probe.action_cost+prefix_cost>probe_policy.max_total_probe_cost) {
                reusable.feasible=false;reusable.reason=probe_closed_reason.empty()?"probe_cost_bound":probe_closed_reason;
            }
            probe.verification_routes.push_back(reusable);probe.answer_cache_hit=true;
            support.erase(std::remove_if(support.begin(),support.end(),[&](const std::pair<LocationHypothesis,double>& h) {
                return h.first==route.hypothesis;
            }),support.end());
        }
    }
    const auto start=std::chrono::steady_clock::now();
    const auto allowance=std::min<std::chrono::steady_clock::duration>(std::chrono::milliseconds(10),
        std::max(std::chrono::steady_clock::duration::zero(),std::chrono::milliseconds(100)-answer_search_used));
    const auto end=start+allowance;
    const bool previous_budget=shadow_search_budget_enabled;
    const auto previous_deadline=shadow_search_deadline;
    shadow_search_budget_enabled=true; shadow_search_deadline=end;
    try {
        for(const auto& world:support) {
            VerificationRoute route;route.hypothesis=world.first;
            if(world.first.first=='?' || world.second<=0) continue;
            if(std::chrono::steady_clock::now()>=end) {
                route.reason="branch_search_budget";probe.verification_routes.push_back(route);continue;
            }
            ProbeCandidate verification;
            verification.kind=world.first.first=='i'?ProbeKind::OPEN_AND_SENSE:ProbeKind::MOVE_AND_SENSE;
            verification.target_object=world.first.first=='i'?world.first.second:0;
            verification.target_location=world.first.first=='i'?FactLocation(world.first.second):world.first.second;
            if(verification.kind==ProbeKind::OPEN_AND_SENSE && FactContainerState(world.first.second)==1)
                verification.kind=ProbeKind::MOVE_AND_SENSE;
            if(verification.target_location==location && verification.kind==ProbeKind::MOVE_AND_SENSE)
                verification.kind=ProbeKind::SENSE_CURRENT_LOCATION_ONLY;
            verification.signature=verification.kind==ProbeKind::OPEN_AND_SENSE?
                "open_sense:"+std::to_string(verification.target_object):"sense_at:"+std::to_string(verification.target_location);
            verification.facts=probe.facts;verification.fact_context=ProbeFactContext(verification);
            verification.potential_goal_value=probe.potential_goal_value;
            if(verification.target_location!=location && verification.target_location>=0)
                verification.actions.emplace_back("Move",std::vector<unsigned>{unsigned(verification.target_location)},ActionCategory::MOVE);
            if(verification.kind==ProbeKind::OPEN_AND_SENSE)
                verification.actions.emplace_back("Open",std::vector<unsigned>{verification.target_object},ActionCategory::PHYSICAL);
            verification.actions.emplace_back("Sense",std::vector<unsigned>{},ActionCategory::OBSERVATION);
            if(world.first.first=='i') verification.actions.emplace_back("TakeOut",
                std::vector<unsigned>{probe.target_object,unsigned(world.first.second)},ActionCategory::PHYSICAL);
            for(const auto& action:verification.actions) {
                verification.action_cost+=action.cost;verification.estimated_duration+=action.estimated_duration;
            }
            // Qualify only the Move/Open/Sense prefix; TakeOut is checked by the
            // existing task projection and feedback model, not by Probe execution.
            auto prefix=verification;
            if(world.first.first=='i') prefix.actions.pop_back();
            QualifyProbe(prefix,false,probe.action_cost);
            if(!prefix.eligible && prefix.rejection=="duplicate_related_revision") {
                QualifyProbe(prefix,true,probe.action_cost);route.requires_new_answer=prefix.eligible;
            }
            route.failure_value=-double(verification.action_cost)-20.0*prefix.constraint_risks.size();
            if(!prefix.eligible) {route.reason=prefix.rejection;probe.verification_routes.push_back(route);continue;}
            auto moved=ProjectProbeMove(verification.target_location,
                verification.kind==ProbeKind::OPEN_AND_SENSE?verification.target_object:0);
            route.failure_value-=40*moved.lost_goals.size();
            for(auto task:probe.task_indices) {
                if(std::chrono::steady_clock::now()>=end) break;
                auto plan=ProjectVerification(probe.target_object,world.first,task);
                const auto prefix_size=verification.actions.size();
                bool supported=plan.dry_run_succeeded && plan.actions.size()>=prefix_size;
                for(std::size_t i=0;supported && i<plan.actions.size();++i) {
                    if(i<prefix_size) supported=plan.actions[i].name==verification.actions[i].name &&
                        plan.actions[i].arguments==verification.actions[i].arguments;
                    else if(plan.actions[i].name=="AskLoc" || plan.actions[i].name=="Sense") supported=false;
                }
                if(!supported || !plan.eligible || !deadline_manager.canFinish(plan.estimated_duration+probe.estimated_duration,plan_safety_margin)) continue;
                if(!route.feasible || plan.marginal_score>route.success_value) {
                    route.feasible=true;route.success_value=plan.marginal_score;
                    route.success_cost=plan.action_cost;
                    route.worst_duration=plan.estimated_duration;route.reason="complete_verified_continuation";
                }
            }
            if(!route.feasible) route.reason="incomplete_or_unverified_continuation";
            probe.verification_routes.push_back(route);
        }
    } catch (...) {
        shadow_search_budget_enabled=previous_budget;shadow_search_deadline=previous_deadline;throw;
    }
    shadow_search_budget_enabled=previous_budget;shadow_search_deadline=previous_deadline;
    if(!support.empty()) {
        answer_search_used+=std::chrono::steady_clock::now()-start;
    }
    std::vector<VerificationRoute> successful;
    for(const auto& route:probe.verification_routes) if(route.feasible) successful.push_back(route);
    if(!successful.empty()) answer_route_cache[cache_key]=std::move(successful);
    auto remaining=deadline_manager.remaining()-plan_safety_margin;
    probe.answer_value=InformationPlanner::ask(belief,AskModel(),probe.verification_routes,
        probe.action_cost,remaining,probe.estimated_duration);
    probe.expected_gain=probe.answer_value.net_value;
    probe.information_estimate=0;probe.continuation_cost=0;probe.continuation_duration=std::chrono::milliseconds(0);
    for(const auto& branch:probe.answer_value.branches) {
        probe.information_estimate+=branch.probability*branch.posterior_match;
        for(const auto& route:probe.verification_routes) if(route.hypothesis==branch.selected_route) {
            probe.continuation_cost=std::max(probe.continuation_cost,route.success_cost);
            probe.continuation_duration=std::max(probe.continuation_duration,route.worst_duration);
        }
    }
    if(probe.eligible && probe.expected_gain<=0) {
        probe.eligible=false;probe.rejection="nonpositive_answer_branch_value";
    }
}
