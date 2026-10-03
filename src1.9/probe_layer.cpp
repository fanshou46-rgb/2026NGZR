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
int opportunityValue(const RDFW& w,ProbeCandidate& p) {
    std::map<std::string,std::size_t> bundles;
    for(auto index:p.task_indices) {
        if(index>=w.tasks.size()) continue;
        const auto& task=w.tasks[index]; std::ostringstream key; key<<task.behave;
        for(const auto* objects:{&task.X,&task.Y}) {
            key<<':' ; for(const auto& object:*objects) if(object) key<<object->id<<',';
        }
        ++bundles[key.str()];
    }
    std::size_t largest=0; for(const auto& b:bundles) largest=std::max(largest,b.second);
    p.continuation_bundles=std::max<std::size_t>(1,std::min<std::size_t>(3,bundles.size()));
    return 40*static_cast<int>(std::min(p.task_indices.size(),largest*p.continuation_bundles));
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
    answer_search_used=std::chrono::steady_clock::duration::zero();
    answer_route_hints.clear();
    answer_route_cache.clear();
    location_beliefs.clear(); probe_cost_spent=0; probe_authorized_constraint_risks.clear();
    probe_history.clear(); probe_feedback.clear(); active_probe=nullptr;
    total_probes=consecutive_no_progress_probes=0; pending_probe=NO_PROBE;
    probe_closed_reason.clear(); probe_stop_reason.clear();
}

LocationBelief& RDFW::BeliefFor(unsigned id) {
    auto& belief=location_beliefs[id];
    if (!belief.empty()) {
        std::vector<LocationHypothesis> absent;
        for(const auto& h:belief.distribution()) if(h.first.first=='a' && IsAbsentFromSensedLocation(id,h.first.second)) absent.push_back(h.first);
        for(auto h:absent) belief.ruleOut(h);
        const int inside=FactInside(id),loc=FactLocation(id);
        if(inside>0) belief.confirm({'i',inside});
        else if(loc!=UNKNOWN && (inside==NONE || !dynamic_pointer_cast<SmallObject>(GetObject(id))))
            belief.confirm({'a',loc});
        return belief;
    }
    std::set<LocationBelief::Hypothesis> domain;
    for (const auto& object:objects) if (object) {
        if (object->location>=0) domain.insert({'a',object->location});
        if (dynamic_pointer_cast<SmallObject>(GetObject(id)) && object->id>0 && dynamic_cast<Container*>(object.get())) domain.insert({'i',object->id});
    }
    LocationBelief::Hypothesis hint{'?',-1};
    const auto object=GetObject(id);
    if (object) {
        const auto small=dynamic_cast<SmallObject*>(object.get());
        if (small && small->inside>0) hint={'i',small->inside};
        else if (object->location>=0) hint={'a',object->location};
    }
    belief.initialize(domain,hint); return BeliefFor(id);
}

double RDFW::ProbeProbability(const ProbeCandidate& p) {
    if (p.kind==ProbeKind::ASK_LOCATION) return 0.6;
    // Correlated fields of the same object are one event. A probe may expose
    // a container dependency even while its contents remain hidden. The maximum
    // event probability is a lower bound for learning at least one related fact;
    // it is not the probability of completing every downstream task.
    std::set<unsigned> ids;
    for(const auto& f:p.facts) ids.insert(f.object_id);
    double result=0;
    for(auto id:ids) {
        auto& belief=BeliefFor(id);
        if (IsAbsentFromSensedLocation(id,p.target_location)) belief.ruleOut({'a',p.target_location});
        double probability=0;
        if (FactLocation(id)!=UNKNOWN) probability=FactLocation(id)==p.target_location?1:0;
        else for(const auto& h:belief.distribution()) {
            if(h.first.first=='a' && h.first.second==p.target_location &&
               !IsAbsentFromSensedLocation(id,p.target_location)) probability+=h.second;
            if(h.first.first=='i' && (p.kind==ProbeKind::OPEN_AND_SENSE || FactContainerState(h.first.second)==1) &&
               (FactLocation(h.first.second)==p.target_location)) probability+=h.second;
        }
        result=std::max(result,probability);
    }
    return result;
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
                auto preferred=answer_route_hints.find(id);
                if(preferred!=answer_route_hints.end()) {
                    auto h=preferred->second;
                    addLocation(h.first=='a'?h.second:FactLocation(h.second),"answer_posterior_route");
                }
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

CandidatePlan RDFW::ProjectProbeMove(int target,unsigned open_container) {
    const int saved=task_index; task_index=-1;
    try {
        auto plan=BuildTaskGroupPlan({0},false,0,false,target,open_container);
        task_index=saved; return plan;
    } catch (...) { task_index=saved; throw; }
}

bool RDFW::ProbeConstraintAffected(const Instruction& c,bool& unknown_storage,unsigned open_container) const {
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
        bool changes=k.first==StateField::CONTAINER_STATE && k.second==open_container && open_container!=0;
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

void RDFW::QualifyProbe(ProbeCandidate& p,bool after_new_answer,int reserved_probe_cost) {
    p.eligible=false; p.constraint_risks.clear(); p.constraint_result="constraint_safe";
    if (!probe_closed_reason.empty()) { p.rejection=probe_closed_reason; return; }
    if (probe_cost_spent+p.action_cost+reserved_probe_cost>probe_policy.max_total_probe_cost) { p.rejection="probe_cost_bound"; return; }
    if (FactLocation(0)==UNKNOWN || FactLocation(0)!=location ||
        (p.kind!=ProbeKind::ASK_LOCATION && (p.target_location<0 || p.target_location>MAX_LOCATION_ID))) { p.rejection="invalid_canonical_location"; return; }
    if (!deadline_manager.canFinish(p.estimated_duration+p.continuation_duration,plan_safety_margin)) { p.rejection="deadline"; return; }
    const auto history=probe_history.find(p.signature);
    if (history!=probe_history.end()) {
        const auto& h=history->second;
        if (h.attempts>=(p.kind==ProbeKind::ASK_LOCATION?probe_policy.max_same_ask:probe_policy.max_same_probe)) { p.rejection="same_probe_bound"; return; }
        if (p.kind==ProbeKind::ASK_LOCATION && h.answer_usable && h.context_after==p.fact_context) {
            p.rejection="answer_requires_verification"; return;
        }
        if (p.kind!=ProbeKind::ASK_LOCATION) {
        if (!after_new_answer && (h.world_revision==world_revision || h.context_after==p.fact_context)) { p.rejection="duplicate_related_revision"; return; }
        if (!h.related_new_evidence) { p.rejection="previous_probe_no_information"; return; }
        bool changed_shared_fact=false;
        for (const auto& current:factContexts(*this,p)) {
            const auto old=h.fact_contexts_after.find(current.first);
            if (old!=h.fact_contexts_after.end() && old->second!=current.second) changed_shared_fact=true;
        }
        // Regrouping tasks or target facts does not create a new observation opportunity.
        if (!after_new_answer && !changed_shared_fact) { p.rejection="duplicate_related_revision"; return; }
        } // Fresh stochastic AskLoc calls have their own bounded retry allowance.
    }
    if (p.kind==ProbeKind::ASK_LOCATION) {
        if (!IsValidObjectId(p.target_object) || p.target_object==0) { p.rejection="invalid_ask_target"; return; }
    }
    if (p.kind==ProbeKind::OPEN_AND_SENSE) {
        if (!IsValidObjectId(p.target_object) || !dynamic_pointer_cast<Container>(GetObject(p.target_object)) ||
            FactLocation(p.target_object)!=p.target_location || FactContainerState(p.target_object)!=0 ||
            FactValue(StateField::HOLD)!=NONE) { p.rejection="unverified_open_preconditions"; return; }
    }
    if (p.kind==ProbeKind::MOVE_AND_SENSE || p.kind==ProbeKind::OPEN_AND_SENSE) {
        if ((FactValue(StateField::HOLD)!=UNKNOWN && FactValue(StateField::HOLD)!=hold_id) ||
            (FactValue(StateField::PLATE)!=UNKNOWN && FactValue(StateField::PLATE)!=plate_id)) {
            p.constraint_result="constraint_safety_unknown"; p.rejection=p.constraint_result; return;
        }
        const auto projection=ProjectProbeMove(p.target_location,p.kind==ProbeKind::OPEN_AND_SENSE?p.target_object:0);
        if (!projection.dry_run_succeeded) { p.rejection="incomplete_move_projection"; return; }
        std::vector<CandidateAction> physical;
        for (const auto& action:p.actions) if(action.name!="Sense") physical.push_back(action);
        bool exact=projection.actions.size()==physical.size();
        for(std::size_t i=0; exact && i<physical.size(); ++i)
            exact=projection.actions[i].name==physical[i].name && projection.actions[i].arguments==physical[i].arguments;
        if (!exact) { p.rejection="extra_physical_actions"; return; }
        if (p.kind==ProbeKind::OPEN_AND_SENSE && !projection.lost_goals.empty()) { p.rejection="probe_goal_loss"; return; }
        std::set<std::size_t> risks(projection.broken_constraints.begin(),projection.broken_constraints.end());
        std::size_t index=0; bool unknown=false;
        for (const auto* group:{&not_infoConstrains,&notnot_infoConstrains,&not_taskConstrains})
            for (const auto& c:*group) {
                bool unknown_storage=false;
                const bool relevant=ProbeConstraintAffected(c,unknown_storage,p.kind==ProbeKind::OPEN_AND_SENSE?p.target_object:0);
                if (index<projection.terminal_before.constraint_eligible.size() && projection.terminal_before.constraint_eligible[index] && relevant &&
                    (unknown_storage || index>=projection.terminal_after.constraints.size() ||
                     projection.terminal_after.constraints[index]!=TerminalStatus::SATISFIED)) {unknown=true;risks.insert(index);}
                ++index;
            }
        if (!risks.empty()) {
            p.constraint_risks.assign(risks.begin(),risks.end());
            auto total=probe_authorized_constraint_risks; total.insert(risks.begin(),risks.end());
            const double benefit=ProbeProbability(p)*p.potential_goal_value-p.action_cost-20*risks.size();
            // A bounded score trade is possible only for a substantial task
            // opportunity. Opening containers keeps the stricter no-loss gate.
            if (p.kind==ProbeKind::MOVE_AND_SENSE && p.potential_goal_value>=200 &&
                total.size()<=probe_policy.max_probe_constraint_risks && benefit>0) {
                p.constraint_result="bounded_score_trade";
            } else {
                p.constraint_result=projection.broken_constraints.empty() && unknown?"constraint_safety_unknown":"constraint_known_loss";
                p.rejection=p.constraint_result; return;
            }
        }
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
        p.potential_goal_value=opportunityValue(*this,p);
        if (p.kind==ProbeKind::MOVE_AND_SENSE) p.actions.emplace_back("Move",std::vector<unsigned>{static_cast<unsigned>(p.target_location)},ActionCategory::MOVE);
        p.actions.emplace_back("Sense",std::vector<unsigned>(),ActionCategory::OBSERVATION);
        for (const auto& a:p.actions) { p.action_cost+=a.cost; p.estimated_duration+=a.estimated_duration; }
        p.fact_context=ProbeFactContext(p); p.state_before=PlanStateSignature();
        QualifyProbe(p); probes.push_back(std::move(p));
    }
    std::map<unsigned,ProbeCandidate> asks, opens;
    for (const auto& f:facts) {
        if (f.field!=StateField::LOCATION && f.field!=StateField::INSIDE) continue;
        const auto* blocked=FindCandidate(candidates,f.task_index);
        // An observation does not solve an already projected negative trade.
        // Keep physical sensing available for evidence repair, but do not spend
        // AskLoc calls on a pure goal-ordering/restoration problem.
        if (!blocked || !blocked->dry_run_succeeded || blocked->marginal_score>0) {
            auto& ask=asks[f.object_id]; ask.kind=ProbeKind::ASK_LOCATION; ask.target_object=f.object_id;
            ask.facts.push_back(f); ask.task_indices.push_back(f.task_index);
        }
        if (f.field==StateField::INSIDE) {
            const auto& in=Provenance(StateField::INSIDE,f.object_id);
            for (int id:{in.received.value,in.conflicting.value}) {
                if (id<=0 || !dynamic_pointer_cast<Container>(GetObject(id)) || FactContainerState(id)!=0 || FactLocation(id)==UNKNOWN) continue;
                auto& open=opens[id]; open.kind=ProbeKind::OPEN_AND_SENSE; open.target_object=id;
                open.target_location=FactLocation(id); open.facts.push_back(f); open.task_indices.push_back(f.task_index);
            }
        }
    }
    for (auto* group:{&asks,&opens}) for (auto& entry:*group) {
        auto& p=entry.second; p.world_revision=world_revision; p.stable_id=NO_PROBE;
        std::sort(p.task_indices.begin(),p.task_indices.end());
        p.task_indices.erase(std::unique(p.task_indices.begin(),p.task_indices.end()),p.task_indices.end());
        for (auto i:p.task_indices) p.stable_id=std::min(p.stable_id,tasks[i].stable_id);
        p.potential_goal_value=opportunityValue(*this,p);
        if (p.kind==ProbeKind::ASK_LOCATION) {
            p.signature="ask:"+std::to_string(p.target_object);
            p.actions.emplace_back("AskLoc",std::vector<unsigned>{p.target_object},ActionCategory::HUMAN_INTERACTION);
        } else {
            p.signature="open_sense:"+std::to_string(p.target_object);
            if (p.target_location!=FactLocation(0)) p.actions.emplace_back("Move",std::vector<unsigned>{unsigned(p.target_location)},ActionCategory::MOVE);
            p.actions.emplace_back("Open",std::vector<unsigned>{p.target_object},ActionCategory::PHYSICAL);
            p.actions.emplace_back("Sense",std::vector<unsigned>(),ActionCategory::OBSERVATION);
        }
        for (const auto& a:p.actions) {p.action_cost+=a.cost; p.estimated_duration+=a.estimated_duration;}
        p.fact_context=ProbeFactContext(p); p.state_before=PlanStateSignature(); QualifyProbe(p); probes.push_back(p);
    }
    for (auto& p:probes) {
        for(const auto& f:p.facts) {
            auto hint=answer_route_hints.find(f.object_id);
            if(hint!=answer_route_hints.end() && p.kind!=ProbeKind::ASK_LOCATION) {
                auto h=hint->second;
                p.policy_preferred |= h.first=='i'?(p.kind==ProbeKind::OPEN_AND_SENSE && p.target_object==unsigned(h.second)) ||
                    (FactContainerState(h.second)==1 && p.kind!=ProbeKind::OPEN_AND_SENSE && p.target_location==FactLocation(h.second)):
                    p.kind!=ProbeKind::OPEN_AND_SENSE && p.target_location==h.second;
            }
        }
        if(p.kind==ProbeKind::ASK_LOCATION) {
            if(p.eligible) EvaluateAskBranches(p);
            continue; // actual branch plans replace the fixed heuristic reserve
        }
        p.information_estimate=ProbeProbability(p);
        int cost=0; std::chrono::milliseconds next(0);
        // Use the cheapest complete targeted continuation; missing projections incur
        // an explicit reserve instead of treating discovery as a completed goal.
        bool projected=false;
        for (auto i:p.task_indices) {
            const auto* plan=FindCandidate(candidates,i);
            if (plan && plan->dry_run_succeeded && (!projected || plan->action_cost<cost)) {
                projected=true; cost=plan->action_cost; next=plan->estimated_duration;
            }
        }
        if (!projected) {cost=8; next=std::chrono::milliseconds(400);}
        cost*=static_cast<int>(p.continuation_bundles);
        next*=static_cast<int>(p.continuation_bundles);
        if (p.kind==ProbeKind::ASK_LOCATION) {cost+=5;next+=std::chrono::milliseconds(220);}
        int unrecoverable_goal_loss=0, constraint_loss=0;
        if (p.kind==ProbeKind::MOVE_AND_SENSE || p.kind==ProbeKind::OPEN_AND_SENSE) {
            const auto physical=ProjectProbeMove(p.target_location,p.kind==ProbeKind::OPEN_AND_SENSE?p.target_object:0);
            constraint_loss=20*static_cast<int>(p.constraint_risks.size());
            for(auto id:physical.lost_goals) {
                if (id<tasks.size() && tasks[id].behave=="goto" && !tasks[id].X.empty() &&
                    FactLocation(tasks[id].X[0]->id)!=UNKNOWN) {
                    cost+=4; next+=std::chrono::milliseconds(120);
                } else unrecoverable_goal_loss+=40;
            }
        }
        p.continuation_duration=next;
        p.continuation_cost=cost;
        p.expected_gain=p.information_estimate*std::max(0,p.potential_goal_value-cost)-p.action_cost-unrecoverable_goal_loss-constraint_loss;
        if (p.eligible && (!deadline_manager.canFinish(p.estimated_duration+next,plan_safety_margin) || p.expected_gain<=0)) {
            p.eligible=false; p.rejection=p.expected_gain<=0?"nonpositive_expected_gain":"continuation_deadline";
        }
    }
    std::sort(probes.begin(),probes.end(),[](const ProbeCandidate& a,const ProbeCandidate& b) {
        if(a.policy_preferred!=b.policy_preferred) return a.policy_preferred>b.policy_preferred;
        const auto priority=[](ProbeKind k) {return k==ProbeKind::ASK_LOCATION?2:k==ProbeKind::OPEN_AND_SENSE?1:0;};
        if (priority(a.kind)!=priority(b.kind)) return priority(a.kind)<priority(b.kind);
        // Keep the measured Sense ordering, including ties, until the downstream
        // model is calibrated. A cheap hypothesis must not delay a useful route.
        if (a.kind!=ProbeKind::ASK_LOCATION && factCount(a)!=factCount(b)) return factCount(a)>factCount(b);
        if (a.kind==ProbeKind::ASK_LOCATION && a.expected_gain!=b.expected_gain) return a.expected_gain>b.expected_gain;
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
    if ((action.name!="AskLoc" && FactLocation(0)!=(action.name=="Move"?FactLocation(0):p.target_location)) || FactLocation(0)==UNKNOWN)
        throw std::runtime_error("probe canonical location changed");
    if (action.name=="Move" && (world_revision!=p.world_revision || PlanStateSignature()!=p.state_before || ProbeFactContext(p)!=p.fact_context))
        throw std::runtime_error("probe state changed before move");
    if (action.name=="Open" && (FactLocation(p.target_object)!=p.target_location ||
        FactContainerState(p.target_object)!=0 || FactValue(StateField::HOLD)!=NONE))
        throw std::runtime_error("probe open preconditions changed");
    probe_cost_spent+=action.cost;
    ++active_probe->issued_actions;
    if (action.name=="Sense") active_probe->sense_attempted=true;
}

void RDFW::ExecuteProbe(const ProbeCandidate& candidate) {
    if (stage!=2 || shadow_dry_run) { LogProbe("execution_rejected",&candidate,nullptr,"unsupported_stage_or_projection"); return; }
    if (!candidate.eligible) { LogProbe("execution_rejected",&candidate,nullptr,candidate.rejection); return; }
    ProbeCandidate checked=candidate;
    QualifyProbe(checked);
    if (!checked.eligible || PlanStateSignature()!=candidate.state_before || ProbeFactContext(candidate)!=candidate.fact_context) {
        LogProbe("execution_rejected",&checked,nullptr,checked.rejection.empty()?"stale_state":checked.rejection); return;
    }
    ProbeExecutionRecord record; record.candidate=candidate; record.revision_before=world_revision;
    auto& history=probe_history[candidate.signature]; ++history.attempts; ++total_probes;
    history.world_revision=world_revision;
    probe_authorized_constraint_risks.insert(checked.constraint_risks.begin(),checked.constraint_risks.end());
    LogProbe("execute",&candidate,&record);
    const int saved_task=task_index; task_index=-1; active_probe=&record;
    const std::string success_before=sourceChanges(*this,EvidenceSource::ACTION_SUCCESS);
    const std::string failure_before=sourceChanges(*this,EvidenceSource::ACTION_FAILURE);
    try {
        bool moved=true;
        if (candidate.kind==ProbeKind::ASK_LOCATION) {
            const auto before=ProbeFactContext(candidate,true);
            const auto reply=AskLoc(candidate.target_object); record.ask_reply=reply;
            record.received_feedback=true;
            history.answer_usable=AcceptProbeAnswer(candidate.target_object,reply);
            answer_route_hints.erase(candidate.target_object);
            if(candidate.answer_branches_evaluated) {
                auto observation=ProbeReplyHypothesis(reply,candidate.target_object);
                const AnswerBranch* selected=nullptr;
                for(const auto& branch:candidate.answer_value.branches) if(branch.observation==observation) selected=&branch;
                if(!selected && observation.first!='?') for(const auto& branch:candidate.answer_value.branches)
                    if(branch.observation.first=='*') selected=&branch;
                if(selected && selected->selected_route.first!='?')
                    answer_route_hints[candidate.target_object]=selected->selected_route;
            }
            record.related_new_evidence=before!=ProbeFactContext(candidate,true);
        } else {
        if (candidate.target_location!=FactLocation(0)) moved=Move(candidate.target_location);
        if (!moved) record.move_failed=true;
        else {
            if (candidate.kind==ProbeKind::OPEN_AND_SENSE && !Open(candidate.target_object))
                throw std::runtime_error("probe open failed");
            const auto sense_before=sourceChanges(*this,EvidenceSource::SENSE);
            const auto related_before=ProbeFactContext(candidate,true);
            SenseCurrentLocationOnly(true); record.received_feedback=true;
            record.sense_evidence_changes=sense_before!=sourceChanges(*this,EvidenceSource::SENSE);
            record.related_new_evidence=related_before!=ProbeFactContext(candidate,true);
            for(const auto& fact:candidate.facts) answer_route_hints.erase(fact.object_id);
        }
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
    else if (probe_cost_spent>=probe_policy.max_total_probe_cost) probe_closed_reason="probe_cost_bound";
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
    // No-information and per-signature retry bans are local, not layer shutdown.
    LogProbe("replan",&r.candidate,&r); pending_probe=NO_PROBE;
}

void RDFW::RecordProbeTaskCompletion(std::size_t index) {
    for (auto& r:probe_feedback) if (std::find(r.restored_tasks.begin(),r.restored_tasks.end(),index)!=r.restored_tasks.end() &&
        std::find(r.completed_tasks.begin(),r.completed_tasks.end(),index)==r.completed_tasks.end()) {
        r.completed_tasks.push_back(index); LogProbe("task_completed",&r.candidate,&r);
    }
}

void RDFW::LogProbe(const char* event,const ProbeCandidate* p,const ProbeExecutionRecord* r,const std::string& reason) const {
    std::ostringstream out; out << "{\"schema\":\"probe.v2\",\"event\":" << quoted(event)
        << ",\"world_revision\":" << world_revision << ",\"total_probes\":" << total_probes
        << ",\"probe_cost_spent\":" << probe_cost_spent << ",\"max_same_ask\":" << probe_policy.max_same_ask
        << ",\"authorized_constraint_risk_count\":" << probe_authorized_constraint_risks.size()
        << ",\"consecutive_no_progress\":" << consecutive_no_progress_probes
        << ",\"policy\":[" << probe_policy.max_total_probes_per_problem << ',' << probe_policy.max_same_probe << ',' << probe_policy.max_total_probe_cost << ']'
        << ",\"reason\":" << quoted(reason) << ",\"closed_reason\":" << quoted(probe_closed_reason);
    if (p) {
        out << ",\"signature\":" << quoted(p->signature) << ",\"kind\":" << quoted(p->kind==ProbeKind::ASK_LOCATION?"AskLoc":p->kind==ProbeKind::OPEN_AND_SENSE?"OpenSense":p->kind==ProbeKind::MOVE_AND_SENSE?"MoveSense":"SenseCurrentLocationOnly")
            << ",\"target_location\":" << p->target_location << ",\"eligible\":" << (p->eligible?"true":"false")
            << ",\"information_estimate\":" << p->information_estimate << ",\"expected_gain\":" << p->expected_gain
            << ",\"answer_branches_evaluated\":" << (p->answer_branches_evaluated?"true":"false")
            << ",\"answer_cache_hit\":" << (p->answer_cache_hit?"true":"false")
            << ",\"answer_direct_value\":" << p->answer_value.direct_value
            << ",\"answer_after_value\":" << p->answer_value.after_answer_value
            << ",\"answer_net_value\":" << p->answer_value.net_value
            << ",\"answer_branch_count\":" << p->answer_value.branches.size()
            << ",\"continuation_cost\":" << p->continuation_cost << ",\"constraint_risk_count\":" << p->constraint_risks.size()
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
        out << ",\"answer_branches\":[";
        bool branch_first=true;
        for(const auto& branch:p->answer_value.branches) {
            if(!branch_first) out<<',';branch_first=false;
            out<<"{\"reply\":["<<quoted(std::string(1,branch.observation.first))<<','<<branch.observation.second
               <<"],\"probability\":"<<branch.probability<<",\"route\":["<<quoted(std::string(1,branch.selected_route.first))
               <<','<<branch.selected_route.second<<"],\"posterior_match\":"<<branch.posterior_match<<",\"value\":"<<branch.value<<'}';
        }
        out << "],\"verification_routes\":[";bool route_first=true;
        for(const auto& route:p->verification_routes) {
            if(!route_first) out<<',';route_first=false;
            out<<"{\"hypothesis\":["<<quoted(std::string(1,route.hypothesis.first))<<','<<route.hypothesis.second
               <<"],\"success_value\":"<<route.success_value<<",\"failure_value\":"<<route.failure_value
               <<",\"success_cost\":"<<route.success_cost<<",\"duration_ms\":"<<route.worst_duration.count()
               <<",\"feasible\":"<<(route.feasible?"true":"false")<<",\"requires_new_answer\":"<<(route.requires_new_answer?"true":"false")
               <<",\"reason\":"<<quoted(route.reason)<<'}';
        }
        out << ']';
    }
    if (r) {
        out << ",\"revision_before\":" << r->revision_before << ",\"revision_after\":" << r->revision_after
            << ",\"ask_reply\":" << quoted(r->ask_reply)
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
