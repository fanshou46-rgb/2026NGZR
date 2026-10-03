#include "rdfw.hpp"
#include <algorithm>
#include <limits>
#include <set>
#include <sstream>

using namespace _home;
namespace {
const std::size_t NO_PROBE = static_cast<std::size_t>(-1);
typedef std::pair<StateField, unsigned int> FactKey;
const char* fieldName(StateField f) {
    switch (f) {
    case StateField::LOCATION: return "LOCATION";
    case StateField::INSIDE: return "INSIDE";
    case StateField::CONTAINER_STATE: return "CONTAINER_STATE";
    case StateField::HOLD: return "HOLD";
    case StateField::PLATE: return "PLATE";
    }
    return "invalid";
}
std::string quoted(const std::string& s) {
    std::ostringstream o; o << '"';
    for (char c : s) {
        if (c == '"' || c == '\\') o << '\\' << c;
        else if (c == '\n') o << "\\n";
        else if (static_cast<unsigned char>(c) < 32) o << '?';
        else o << c;
    }
    o << '"'; return o.str();
}
void contextRecord(const RDFW& w, FactKey key, std::set<FactKey>& seen,
                   std::ostream& out, unsigned depth = 0) {
    if (key.second == 0 || depth > 8 || !seen.insert(key).second) return;
    const auto& p = w.Provenance(key.first, key.second);
    out << int(key.first) << ':' << key.second << ':' << w.FactValue(key.first,key.second)
        << ':' << p.resolved_value << ':' << int(p.resolved_source) << ':' << p.resolved_verified;
    for (const auto* c : {&p.received, &p.conflicting})
        out << ':' << c->present << ',' << c->value << ',' << int(c->source);
    out << ':' << w.DependenciesCurrent(key.first,key.second) << ';';
    for (unsigned i=0; i<std::min(p.dependency_count,2u); ++i)
        contextRecord(w,{p.dependencies[i].field,p.dependencies[i].id},seen,out,depth+1);
}
std::size_t factCount(const ProbeCandidate& p) {
    std::set<FactKey> keys;
    for (const auto& f : p.facts) keys.insert({f.field,f.object_id});
    return keys.size();
}
std::map<FactKey,std::string> factContexts(const RDFW& w,const ProbeCandidate& p) {
    std::map<FactKey,std::string> result;
    for (const auto& f:p.facts) {
        const FactKey key{f.field,f.object_id};
        std::set<FactKey> seen; std::ostringstream out;
        contextRecord(w,key,seen,out); result[key]=out.str();
    }
    return result;
}
std::vector<std::shared_ptr<Object>> bindings(const RDFW& w,const Condition& c,
    const std::vector<std::shared_ptr<Object>>& fallback) {
    if (c.sort.empty() && c.color.empty() && c.declared_type.empty() && !c.has_explicit_id) return fallback;
    std::vector<std::shared_ptr<Object>> result;
    for (const auto& object:w.objects) if (object && object->id>0 && c.IsObjectSatisfy(object)) result.push_back(object);
    return result;
}
std::string sourceChanges(const RDFW& w, EvidenceSource source) {
    std::ostringstream out;
    for (unsigned id=0; id<w.objects.size(); ++id) {
        if (!w.objects[id]) continue;
        for (auto field : {StateField::LOCATION,StateField::INSIDE,StateField::CONTAINER_STATE,
                           StateField::HOLD,StateField::PLATE}) {
            if ((field==StateField::HOLD || field==StateField::PLATE) && id!=0) continue;
            const auto& p=w.Provenance(field,id);
            if (p.received.source==source || p.resolved_source==source)
                out << int(field) << ':' << id << ':' << p.revision << ':' << p.received.value
                    << ':' << p.resolved_value << ':' << p.resolved_verified << ';';
        }
    }
    return out.str();
}
}

void RDFW::ResetProbeLayer() {
    probe_history.clear(); probe_feedback.clear(); active_probe=nullptr;
    total_probes=consecutive_no_progress_probes=0; pending_probe=NO_PROBE;
    probe_closed_reason.clear(); probe_stop_reason.clear();
}

std::size_t RDFW::LegacyBlockedProposal() const {
    const auto terminal=terminal_checker.evaluateAll(*this);
    std::size_t best=NO_PROBE; double priority=std::numeric_limits<double>::max();
    for (std::size_t i=0; i<tasks.size(); ++i) {
        if (!tasks[i].IsUsable() || terminal.goals[i]==TerminalStatus::SATISFIED ||
            (i<task_attempts.size() && task_attempts[i]>=3)) continue;
        const double value=stage==2 ? (tasks[i].ask_times==0 ? tasks[i].risk/2.0 :
            (tasks[i].is_cheat ? 1000.0 : tasks[i].risk)) : tasks[i].risk;
        if (best==NO_PROBE || value<priority) { best=i; priority=value; }
    }
    return best;
}

std::vector<BlockingFact> RDFW::AnalyzeBlockingFacts(const std::vector<CandidatePlan>& candidates) const {
    std::vector<BlockingFact> result;
    const auto terminal=terminal_checker.evaluateAll(*this);
    std::vector<std::size_t> order; const auto proposal=LegacyBlockedProposal();
    if (proposal!=NO_PROBE) order.push_back(proposal);
    for (std::size_t i=0; i<tasks.size(); ++i) if (i!=proposal) order.push_back(i);
    for (auto index:order) {
        const auto& t=tasks[index];
        if (!t.IsUsable() || terminal.goals[index]==TerminalStatus::SATISFIED) continue;
        const CandidatePlan* candidate=FindCandidate(candidates,index);
        std::string reason;
        if (index<task_attempts.size() && task_attempts[index]>=3) reason="task_retry_bound";
        else if (index<failed_task_revision.size() && failed_task_revision[index]==world_revision) reason="failed_task_revision";
        else if (!candidate) reason="not_in_current_candidate_set";
        else if (!candidate->eligible) reason="risk_eligibility";
        else if (!candidate->dry_run_succeeded) reason="incomplete_projection";
        else if (candidate->marginal_score<=0) reason="nonpositive_single";
        else if (!deadline_manager.canFinish(candidate->remainingDuration(),plan_safety_margin)) reason="deadline";
        else reason="constraint_trade";
        std::ostringstream label; label << "task=" << index << ",stable_id=" << t.stable_id << ",filter=" << reason;
        LogProbe("blocked_task",nullptr,nullptr,label.str());
        if (reason=="task_retry_bound") continue;
        std::set<FactKey> seen;
        std::function<void(StateField,unsigned,unsigned)> inspect;
        inspect=[&](StateField field,unsigned id,unsigned depth) {
            if (depth>8 || !IsValidObjectId(id) || !seen.insert({field,id}).second) return;
            const auto& p=Provenance(field,id);
            if (FactValue(field,id)==UNKNOWN) {
                BlockingFact f; f.task_index=index; f.stable_task_id=t.stable_id; f.field=field; f.object_id=id;
                f.reason=HasContradictoryEvidence(field,id)?"conflict":
                    !DependenciesCurrent(field,id)?"dependency_invalid":p.resolved_value==UNKNOWN?"unknown":"unverified";
                auto addLocation=[&](int loc,const std::string& source) {
                    if (loc>=0 && loc<=MAX_LOCATION_ID) f.location_hints.emplace(loc,source);
                };
                auto locationClaims=[&](unsigned object,const std::string& relation) {
                    const int verified=FactLocation(object);
                    if (verified!=UNKNOWN) { addLocation(verified,relation+":canonical"); return; }
                    const auto& loc=Provenance(StateField::LOCATION,object);
                    for (const auto* c:{&loc.received,&loc.conflicting})
                        if (c->present && c->source!=EvidenceSource::UNKNOWN)
                            addLocation(c->value,relation+":claim_source="+std::to_string(int(c->source)));
                };
                locationClaims(id,"object_location");
                const auto& inside=Provenance(StateField::INSIDE,id);
                const int in=FactInside(id);
                if (in==UNKNOWN) for (const auto* c:{&inside.received,&inside.conflicting})
                    if (c->present && c->value>0 && dynamic_cast<Container*>(GetObject(c->value).get()))
                        locationClaims(c->value,"inside_container");
                if (in>0) locationClaims(in,"canonical_inside_container");
                // Only existing relation information supplies a location hypothesis.
                for (const auto* relations:{&infos,&notnot_infoConstrains})
                    for (const auto& r:*relations) {
                        if (r.behave!="near" && r.behave!="on" && r.behave!="inside" && r.behave!="in") continue;
                        for (const auto& x:r.X) for (const auto& y:r.Y) {
                            if (!x || !y) continue;
                            if (x->id==int(id)) locationClaims(y->id,"relation_"+r.behave);
                            else if (y->id==int(id) && r.behave=="near") locationClaims(x->id,"relation_near");
                        }
                    }
                result.push_back(f);
                std::ostringstream fact; fact << label.str() << ",fact=" << fieldName(field) << ':' << id << ",reason=" << f.reason;
                LogProbe("blocking_fact",nullptr,nullptr,fact.str());
            }
            for (unsigned i=0; i<std::min(p.dependency_count,2u); ++i)
                inspect(p.dependencies[i].field,p.dependencies[i].id,depth+1);
        };
        auto object=[&](const std::shared_ptr<Object>& o) {
            if (!o) return;
            inspect(StateField::LOCATION,o->id,0);
            if (dynamic_cast<SmallObject*>(o.get())) {
                inspect(StateField::INSIDE,o->id,0);
                const auto& p=Provenance(StateField::INSIDE,o->id);
                for (int id:{FactInside(o->id),p.received.value,p.conflicting.value})
                    if (id>0 && dynamic_cast<Container*>(GetObject(id).get())) {
                        inspect(StateField::LOCATION,id,0); inspect(StateField::CONTAINER_STATE,id,0);
                    }
            }
            if (dynamic_cast<Container*>(o.get())) inspect(StateField::CONTAINER_STATE,o->id,0);
        };
        for (const auto& x:bindings(*this,t.conditionX,t.X)) object(x);
        for (const auto& y:bindings(*this,t.conditionY,t.Y)) object(y);
        if (t.behave=="give") object(human);
    }
    return result;
}

std::string RDFW::ProbeFactContext(const ProbeCandidate& probe,bool include_absence) const {
    std::set<FactKey> keys,seen; std::ostringstream out;
    for (const auto& f:probe.facts) keys.insert({f.field,f.object_id});
    for (auto key:keys) contextRecord(*this,key,seen,out);
    if (include_absence) for (auto key:keys)
        out << "absent:" << key.second << ':' << IsAbsentFromSensedLocation(key.second,probe.target_location) << ';';
    return out.str();
}

CandidatePlan RDFW::ProjectProbeMove(int target) {
    const int saved=task_index; task_index=-1;
    try {
        auto plan=BuildTaskGroupPlan({0},false,0,false,target);
        task_index=saved; return plan;
    } catch (...) { task_index=saved; throw; }
}

bool RDFW::ProbeConstraintAffected(const Instruction& c,bool& unknown_storage) const {
    std::set<FactKey> reads,visited; unknown_storage=false;
    const auto add=[&](StateField f,unsigned id) { reads.insert({f,id}); };
    const auto xs=bindings(*this,c.conditionX,c.X), ys=bindings(*this,c.conditionY,c.Y);
    for (const auto& x:xs) {
        if (!x) continue;
        if (c.behave=="goto" || c.behave=="move") { add(StateField::LOCATION,0); add(StateField::LOCATION,x->id); }
        else if (c.behave=="near" || c.behave=="nextto" || c.behave=="on" || c.behave=="puton" || c.behave=="give") {
            add(StateField::LOCATION,x->id);
            if (c.behave=="give") { if (human) add(StateField::LOCATION,human->id); }
            else for (const auto& y:ys) if (y) add(StateField::LOCATION,y->id);
        } else if (c.behave=="inside" || c.behave=="in" || c.behave=="putin" || c.behave=="takeout") add(StateField::INSIDE,x->id);
        else if (c.behave=="opened" || c.behave=="closed" || c.behave=="open" || c.behave=="close") {
            if (ys.empty()) add(StateField::CONTAINER_STATE,x->id);
            else for (const auto& y:ys) if (y) add(StateField::CONTAINER_STATE,y->id);
        }
        // Storage predicates may use observed outside location as a fallback.
        else if (c.behave=="pickup" || c.behave=="putdown" || c.behave=="hold" || c.behave=="plate") {
            add(StateField::INSIDE,x->id);
        }
    }
    std::function<bool(FactKey,unsigned)> affected=[&](FactKey k,unsigned depth) {
        if (depth>8 || !visited.insert(k).second) return false;
        bool changes=false;
        if (k.first==StateField::LOCATION) {
            if (k.second==0 || IsStoredFact(k.second)) changes=true;
            else if (IsValidObjectId(k.second) && dynamic_cast<SmallObject*>(objects[k.second].get()) && !IsNotStoredFact(k.second) &&
                     (FactValue(StateField::HOLD)==UNKNOWN || FactValue(StateField::PLATE)==UNKNOWN)) {
                unknown_storage=true; changes=true;
            }
        }
        const auto& p=Provenance(k.first,k.second);
        for (unsigned i=0; i<std::min(p.dependency_count,2u); ++i)
            changes=affected({p.dependencies[i].field,p.dependencies[i].id},depth+1) || changes;
        return changes;
    };
    bool result=false; for (auto key:reads) result=affected(key,0) || result;
    return result;
}

void RDFW::QualifyProbe(ProbeCandidate& p) {
    p.eligible=false;
    if (!probe_closed_reason.empty()) { p.rejection=probe_closed_reason; return; }
    if (FactLocation(0)==UNKNOWN || FactLocation(0)!=location || p.target_location<0 || p.target_location>MAX_LOCATION_ID) { p.rejection="invalid_canonical_location"; return; }
    if (!deadline_manager.canFinish(p.estimated_duration,plan_safety_margin)) { p.rejection="deadline"; return; }
    const auto history=probe_history.find(p.signature);
    if (history!=probe_history.end()) {
        const auto& h=history->second;
        if (h.attempts>=probe_policy.max_same_probe) { p.rejection="same_probe_bound"; return; }
        if (h.world_revision==world_revision || h.context_after==p.fact_context) { p.rejection="duplicate_related_revision"; return; }
        if (!h.related_new_evidence) { p.rejection="previous_probe_no_information"; return; }
        bool changed_shared_fact=false;
        for (const auto& current:factContexts(*this,p)) {
            const auto old=h.fact_contexts_after.find(current.first);
            if (old!=h.fact_contexts_after.end() && old->second!=current.second) changed_shared_fact=true;
        }
        // Regrouping tasks or target facts does not create a new observation opportunity.
        if (!changed_shared_fact) { p.rejection="duplicate_related_revision"; return; }
    }
    if (p.kind==ProbeKind::MOVE_AND_SENSE) {
        if ((FactValue(StateField::HOLD)!=UNKNOWN && FactValue(StateField::HOLD)!=hold_id) ||
            (FactValue(StateField::PLATE)!=UNKNOWN && FactValue(StateField::PLATE)!=plate_id)) {
            p.constraint_result="constraint_safety_unknown"; p.rejection=p.constraint_result; return;
        }
        const auto projection=ProjectProbeMove(p.target_location);
        if (!projection.dry_run_succeeded) { p.rejection="incomplete_move_projection"; return; }
        if (projection.actions.size()!=1 || projection.actions[0].name!="Move" ||
            projection.actions[0].arguments!=std::vector<unsigned>{static_cast<unsigned>(p.target_location)}) {
            p.rejection="extra_physical_actions"; return;
        }
        if (!projection.broken_constraints.empty()) {
            p.constraint_result="constraint_known_loss"; p.rejection=p.constraint_result; return;
        }
        std::size_t index=0; bool unknown=false;
        for (const auto* group:{&not_infoConstrains,&notnot_infoConstrains,&not_taskConstrains})
            for (const auto& c:*group) {
                bool unknown_storage=false;
                const bool relevant=ProbeConstraintAffected(c,unknown_storage);
                if (index<projection.terminal_before.constraint_eligible.size() && projection.terminal_before.constraint_eligible[index] && relevant &&
                    (unknown_storage || index>=projection.terminal_after.constraints.size() ||
                     projection.terminal_after.constraints[index]!=TerminalStatus::SATISFIED)) unknown=true;
                ++index;
            }
        if (unknown) { p.constraint_result="constraint_safety_unknown"; p.rejection=p.constraint_result; return; }
    }
    p.eligible=true; p.rejection.clear();
}

std::vector<ProbeCandidate> RDFW::GenerateProbeCandidates(const std::vector<CandidatePlan>& candidates) {
    const auto facts=AnalyzeBlockingFacts(candidates); std::map<int,ProbeCandidate> grouped;
    for (const auto& f:facts) {
        if (f.field!=StateField::LOCATION && f.field!=StateField::INSIDE) {
            LogProbe("unsupported_fact",nullptr,nullptr,std::string(fieldName(f.field))+":"+std::to_string(f.object_id)); continue;
        }
        for (const auto& hint:f.location_hints) {
            const int loc=hint.first;
            if (IsAbsentFromSensedLocation(f.object_id,loc)) continue;
            if (loc==FactLocation(0) && std::size_t(loc)<posSensedFlag.size() && posSensedFlag[loc]) continue;
            // Observing a visible container cannot distinguish its exposed contents from adjacent objects.
            if (f.field==StateField::INSIDE) {
                const auto& in=Provenance(StateField::INSIDE,f.object_id);
                bool ambiguous=false;
                for (int id:{FactInside(f.object_id),in.received.value,in.conflicting.value})
                    if (id>0 && dynamic_cast<Container*>(GetObject(id).get()) && FactContainerState(id)!=0 &&
                        (FactLocation(id)==loc || Provenance(StateField::LOCATION,id).received.value==loc)) ambiguous=true;
                if (ambiguous) { LogProbe("unsupported_fact",nullptr,nullptr,"inside_container_ambiguity:"+std::to_string(f.object_id)); continue; }
            }
            auto& p=grouped[loc]; p.target_location=loc; p.facts.push_back(f);
            if (std::find(p.task_indices.begin(),p.task_indices.end(),f.task_index)==p.task_indices.end()) p.task_indices.push_back(f.task_index);
        }
    }
    std::vector<ProbeCandidate> probes;
    for (auto& entry:grouped) {
        auto& p=entry.second; p.world_revision=world_revision;
        p.signature="sense_at:"+std::to_string(p.target_location);
        p.kind=p.target_location==FactLocation(0)?ProbeKind::SENSE_CURRENT_LOCATION_ONLY:ProbeKind::MOVE_AND_SENSE;
        p.stable_id=NO_PROBE;
        for (auto index:p.task_indices) p.stable_id=std::min(p.stable_id,tasks[index].stable_id);
        p.potential_goal_value=40*static_cast<int>(p.task_indices.size());
        if (p.kind==ProbeKind::MOVE_AND_SENSE) p.actions.emplace_back("Move",std::vector<unsigned>{static_cast<unsigned>(p.target_location)},ActionCategory::MOVE);
        p.actions.emplace_back("Sense",std::vector<unsigned>(),ActionCategory::OBSERVATION);
        for (const auto& a:p.actions) { p.action_cost+=a.cost; p.estimated_duration+=a.estimated_duration; }
        p.fact_context=ProbeFactContext(p); p.state_before=PlanStateSignature();
        QualifyProbe(p); probes.push_back(std::move(p));
    }
    std::sort(probes.begin(),probes.end(),[](const ProbeCandidate& a,const ProbeCandidate& b) {
        if (factCount(a)!=factCount(b)) return factCount(a)>factCount(b);
        if (a.potential_goal_value!=b.potential_goal_value) return a.potential_goal_value>b.potential_goal_value;
        if (a.action_cost!=b.action_cost) return a.action_cost<b.action_cost;
        if (a.estimated_duration!=b.estimated_duration) return a.estimated_duration<b.estimated_duration;
        if (a.stable_id!=b.stable_id) return a.stable_id<b.stable_id;
        return a.signature<b.signature;
    });
    for (const auto& p:probes) LogProbe("candidate",&p,nullptr,p.rejection);
    return probes;
}

bool RDFW::TryProbe(const std::vector<CandidatePlan>& candidates,bool defer_multi_goto) {
    if (stage!=2 || shadow_dry_run) return false;
    if (!probe_closed_reason.empty()) { probe_stop_reason=probe_closed_reason; LogProbe("stop",nullptr,nullptr,probe_stop_reason); return false; }
    if (!deadline_manager.canFinish(CandidateAction("Sense",{},ActionCategory::OBSERVATION).estimated_duration,plan_safety_margin)) {
        probe_stop_reason="deadline"; LogProbe("stop",nullptr,nullptr,probe_stop_reason); return false;
    }
    if (defer_multi_goto) {
        const auto all=EvaluateShadowCandidates("probe-tail-check",true,NO_PROBE);
        if (SelectGreedyCandidate(all)) { probe_stop_reason="qualified_goto_tail"; LogProbe("stop",nullptr,nullptr,probe_stop_reason); return false; }
        const auto tail=ProjectGreedyContinuation(0,true);
        if (tail.eligible && tail.dry_run_succeeded && tail.marginal_score>0 &&
            CanStartPlan(tail,"multi-goto-relocation") &&
            ShouldStartConstraintTrade(tail,all,"probe-tail-check")) {
            probe_stop_reason="qualified_goto_tail";
            LogProbe("stop",nullptr,nullptr,probe_stop_reason); return false;
        }
    }
    MustChooseOne();
    const auto probes=GenerateProbeCandidates(candidates);
    for (const auto& p:probes) if (p.eligible) {
        const auto before=probe_feedback.size(); ExecuteProbe(p);
        return probe_feedback.size()!=before;
    }
    probe_stop_reason="no_task_and_no_legal_probe";
    if (!probes.empty()) {
        if (std::all_of(probes.begin(),probes.end(),[](const ProbeCandidate& p){return p.rejection=="deadline";})) probe_stop_reason="deadline";
        else if (std::all_of(probes.begin(),probes.end(),[](const ProbeCandidate& p){return p.rejection.find("constraint_")==0;})) probe_stop_reason="constraint_rejected";
        else if (std::all_of(probes.begin(),probes.end(),[](const ProbeCandidate& p){return p.rejection=="duplicate_related_revision" || p.rejection=="previous_probe_no_information";})) probe_stop_reason="duplicate_or_no_information";
    }
    LogProbe("stop",nullptr,nullptr,probe_stop_reason); return false;
}

void RDFW::RecordProbeAction(const CandidateAction& action) {
    const auto& p=active_probe->candidate; const auto i=active_probe->issued_actions;
    if (i>=p.actions.size() || p.actions[i].name!=action.name || p.actions[i].arguments!=action.arguments)
        throw std::runtime_error("probe action differs from authorized sequence");
    std::chrono::milliseconds remaining(0);
    for (std::size_t j=i; j<p.actions.size(); ++j) remaining+=p.actions[j].estimated_duration;
    if (!deadline_manager.canFinish(remaining,plan_safety_margin)) throw std::runtime_error("probe deadline changed");
    if (FactLocation(0)!=(action.name=="Move"?FactLocation(0):p.target_location) || FactLocation(0)==UNKNOWN)
        throw std::runtime_error("probe canonical location changed");
    if (action.name=="Move" && (world_revision!=p.world_revision || PlanStateSignature()!=p.state_before || ProbeFactContext(p)!=p.fact_context))
        throw std::runtime_error("probe state changed before move");
    ++active_probe->issued_actions;
    if (action.name=="Sense") active_probe->sense_attempted=true;
}

void RDFW::ExecuteProbe(const ProbeCandidate& candidate) {
    if (stage!=2 || shadow_dry_run) { LogProbe("execution_rejected",&candidate,nullptr,"unsupported_stage_or_projection"); return; }
    ProbeCandidate checked=candidate;
    QualifyProbe(checked);
    if (!checked.eligible || PlanStateSignature()!=candidate.state_before || ProbeFactContext(candidate)!=candidate.fact_context) {
        LogProbe("execution_rejected",&checked,nullptr,checked.rejection.empty()?"stale_state":checked.rejection); return;
    }
    ProbeExecutionRecord record; record.candidate=candidate; record.revision_before=world_revision;
    auto& history=probe_history[candidate.signature]; ++history.attempts; ++total_probes;
    history.world_revision=world_revision;
    LogProbe("execute",&candidate,&record);
    const int saved_task=task_index; task_index=-1; active_probe=&record;
    const std::string success_before=sourceChanges(*this,EvidenceSource::ACTION_SUCCESS);
    const std::string failure_before=sourceChanges(*this,EvidenceSource::ACTION_FAILURE);
    try {
        bool moved=true;
        if (candidate.kind==ProbeKind::MOVE_AND_SENSE) moved=Move(candidate.target_location);
        if (!moved) record.move_failed=true;
        else {
            const auto sense_before=sourceChanges(*this,EvidenceSource::SENSE);
            const auto related_before=ProbeFactContext(candidate,true);
            SenseCurrentLocationOnly(true); record.received_feedback=true;
            record.sense_evidence_changes=sense_before!=sourceChanges(*this,EvidenceSource::SENSE);
            record.related_new_evidence=related_before!=ProbeFactContext(candidate,true);
        }
    } catch (const std::exception& e) { record.failure=e.what(); }
      catch (...) { record.failure="unknown_exception"; }
    active_probe=nullptr; task_index=saved_task;
    record.action_success_evidence_changes=success_before!=sourceChanges(*this,EvidenceSource::ACTION_SUCCESS);
    record.action_failure_evidence_changes=failure_before!=sourceChanges(*this,EvidenceSource::ACTION_FAILURE);
    record.revision_after=world_revision; record.context_after=ProbeFactContext(candidate);
    record.effective=record.related_new_evidence;
    history.context_after=record.context_after; history.related_new_evidence=record.related_new_evidence;
    history.fact_contexts_after=factContexts(*this,candidate);
    if (total_probes>=probe_policy.max_total_probes_per_problem) probe_closed_reason="total_probe_bound";
    else if (history.attempts>=probe_policy.max_same_probe) probe_closed_reason="same_probe_bound";
    LogProbe("feedback",&candidate,&record);
    probe_feedback.push_back(std::move(record)); pending_probe=probe_feedback.size()-1;
}

void RDFW::FinalizeProbeReplan(const std::vector<CandidatePlan>& candidates,const CandidatePlan* best) {
    if (pending_probe==NO_PROBE) return;
    auto& r=probe_feedback[pending_probe];
    if (best) {
        r.restored_tasks.push_back(best->task_index);
        r.effective=true;
        // Record every restored targeted task using unchanged production qualification.
        for (const auto& p:candidates) {
            if (p.task_index==best->task_index || std::find(r.candidate.task_indices.begin(),r.candidate.task_indices.end(),p.task_index)==r.candidate.task_indices.end()) continue;
            if (p.eligible && p.dry_run_succeeded && p.marginal_score>0 && CanStartPlan(p,"probe-replan") && ShouldStartConstraintTrade(p,candidates,"probe-replan")) r.restored_tasks.push_back(p.task_index);
        }
    }
    consecutive_no_progress_probes=r.effective?0:consecutive_no_progress_probes+1;
    if (consecutive_no_progress_probes>=probe_policy.max_consecutive_no_progress && probe_closed_reason.empty()) probe_closed_reason="probe_no_progress";
    LogProbe("replan",&r.candidate,&r); pending_probe=NO_PROBE;
}

void RDFW::RecordProbeTaskCompletion(std::size_t index) {
    for (auto& r:probe_feedback) if (std::find(r.restored_tasks.begin(),r.restored_tasks.end(),index)!=r.restored_tasks.end() &&
        std::find(r.completed_tasks.begin(),r.completed_tasks.end(),index)==r.completed_tasks.end()) {
        r.completed_tasks.push_back(index); LogProbe("task_completed",&r.candidate,&r);
    }
}

void RDFW::LogProbe(const char* event,const ProbeCandidate* p,const ProbeExecutionRecord* r,const std::string& reason) const {
    std::ostringstream out; out << "{\"schema\":\"probe.v1\",\"event\":" << quoted(event)
        << ",\"world_revision\":" << world_revision << ",\"total_probes\":" << total_probes
        << ",\"consecutive_no_progress\":" << consecutive_no_progress_probes
        << ",\"policy\":[" << probe_policy.max_total_probes_per_problem << ',' << probe_policy.max_same_probe << ',' << probe_policy.max_consecutive_no_progress << ']'
        << ",\"reason\":" << quoted(reason) << ",\"closed_reason\":" << quoted(probe_closed_reason);
    if (p) {
        out << ",\"signature\":" << quoted(p->signature) << ",\"kind\":" << quoted(p->kind==ProbeKind::MOVE_AND_SENSE?"MoveSense":"SenseCurrentLocationOnly")
            << ",\"target_location\":" << p->target_location << ",\"eligible\":" << (p->eligible?"true":"false")
            << ",\"cost\":" << p->action_cost << ",\"duration_ms\":" << p->estimated_duration.count()
            << ",\"fact_count\":" << factCount(*p) << ",\"potential_goal_value\":" << p->potential_goal_value
            << ",\"stable_id\":" << p->stable_id << ",\"constraint_result\":" << quoted(p->constraint_result) << ",\"facts\":[";
        bool first=true;
        for (const auto& f:p->facts) {
            if (!first) out << ',';
            first=false;
            out << "{\"field\":" << quoted(fieldName(f.field)) << ",\"id\":" << f.object_id << ",\"task\":" << f.task_index
                << ",\"stable_task_id\":" << f.stable_task_id << ",\"reason\":" << quoted(f.reason) << ",\"location_hints\":[";
            bool hint_first=true; for (const auto& hint:f.location_hints) {
                if (!hint_first) out << ',';
                hint_first=false;
                out << "{\"location\":" << hint.first << ",\"source\":" << quoted(hint.second) << '}';
            }
            out << "]}";
        }
        out << ']';
    }
    if (r) {
        out << ",\"revision_before\":" << r->revision_before << ",\"revision_after\":" << r->revision_after
            << ",\"related_context_before\":" << quoted(p->fact_context) << ",\"related_context_after\":" << quoted(r->context_after)
            << ",\"issued_actions\":" << r->issued_actions << ",\"received_feedback\":" << (r->received_feedback?"true":"false")
            << ",\"sense_attempted\":" << (r->sense_attempted?"true":"false") << ",\"move_failed\":" << (r->move_failed?"true":"false")
            << ",\"related_new_evidence\":" << (r->related_new_evidence?"true":"false") << ",\"effective\":" << (r->effective?"true":"false")
            << ",\"sense_evidence_changes\":" << r->sense_evidence_changes << ",\"action_success_evidence_changes\":" << r->action_success_evidence_changes
            << ",\"action_failure_evidence_changes\":" << r->action_failure_evidence_changes << ",\"failure\":" << quoted(r->failure);
        for (const auto& list:{std::make_pair("restored_tasks",&r->restored_tasks),std::make_pair("completed_tasks",&r->completed_tasks)}) {
            out << ",\"" << list.first << "\":["; bool first=true;
            for (auto id:*list.second) { if (!first) out << ','; first=false; out << id; } out << ']';
        }
    }
    out << '}'; LOG("[Probe] %s\n",out.str().c_str());
}
