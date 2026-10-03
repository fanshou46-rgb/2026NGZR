# Direct access inventory

Categories reflect owner and role; each write is reviewed with the closure report. Aliased vector erases and Robot primitive writes are explicitly covered there.

| File:line | Function | Write | Category | Code |
|---|---|---|---|---|
| src1.6.7/candidate_plan.cpp:152 | evaluate | False | read_access | if (terminal_before.constraint_eligible[i] && |
| src1.6.7/candidate_plan.cpp:153 | evaluate | False | read_access | !terminal_after.constraint_eligible[i]) |
| src1.6.7/candidate_plan.cpp:155 | evaluate | False | read_access | if (terminal_before.constraint_eligible[i] && |
| src1.6.7/candidate_plan.cpp:156 | evaluate | False | read_access | terminal_after.constraint_eligible[i]) |
| src1.6.7/canonical_state.cpp:12 | ScoreFactLocation | False | declaration | // Official Stage 1 ASP at facts intentionally exclude inside propagation. |
| src1.6.7/canonical_state.cpp:13 | ScoreFactLocation | False | declaration | // This is the scoring representation of canonical location, not a planner read. |
| src1.6.7/canonical_state.cpp:15 | ScoreFactLocation | False | read_access | return FactLocation(id)!=UNKNOWN && id < score_locations.size() ? score_locations[id] : UNKNOWN; |
| src1.6.7/canonical_state.cpp:29 | IsNotStoredFact | True | local_result | const auto inside = ResolvedState(StateField::INSIDE, id); |
| src1.6.7/canonical_state.cpp:30 | IsNotStoredFact | False | read_access | if (!inside.present) return false; |
| src1.6.7/canonical_state.cpp:31 | IsNotStoredFact | False | read_access | if (inside.value > 0) return true; |
| src1.6.7/canonical_state.cpp:35 | IsNotStoredFact | False | read_access | return loc.present && inside.value == NONE && |
| src1.6.7/canonical_state.cpp:36 | IsNotStoredFact | False | read_access | (inside.source == EvidenceSource::SENSE \|\| inside.source == EvidenceSource::ACTION_SUCCESS); |
| src1.6.7/canonical_state.cpp:55 | ApplyStateValue | False | canonical_mutation | bool verified, EvidenceSource source) { |
| src1.6.7/canonical_state.cpp:88 | AppendStateSnapshot | False | read_access | const auto& p = Provenance(field,id); |
| src1.6.7/canonical_state.cpp:89 | AppendStateSnapshot | False | read_access | out << int(field) << ':' << id << ':' << p.resolved_value << ':' |
| src1.6.7/canonical_state.cpp:90 | AppendStateSnapshot | False | read_access | << int(p.resolved_source) << ':' << p.resolved_verified << ':' << p.revision; |
| src1.6.7/canonical_state.cpp:91 | AppendStateSnapshot | False | read_access | for (const auto* claim : {&p.received,&p.conflicting}) |
| src1.6.7/canonical_state.cpp:93 | AppendStateSnapshot | False | read_access | out << ':' << p.dependency_count; |
| src1.6.7/canonical_state.cpp:94 | AppendStateSnapshot | False | read_access | for (unsigned int k=0; k<std::min(p.dependency_count,2u); ++k) { |
| src1.6.7/canonical_state.cpp:95 | AppendStateSnapshot | False | read_access | const auto& d=p.dependencies[k]; |
| src1.6.7/canonical_state.cpp:96 | AppendStateSnapshot | False | read_access | out << ':' << int(d.field) << ',' << d.id << ',' << d.value << ',' << d.revision; |
| src1.6.7/canonical_state.cpp:98 | AppendStateSnapshot | False | read_access | out << ':' << p.support_constraint_index << '['; |
| src1.6.7/canonical_state.cpp:99 | AppendStateSnapshot | False | read_access | for (auto support : p.supporting_constraints) out << support << ','; |
| src1.6.7/canonical_state.cpp:106 | AppendStateSnapshot | False | read_access | out << object->location << ':'; |
| src1.6.7/canonical_state.cpp:108 | AppendStateSnapshot | False | read_access | if (small) out << small->inside << ':' << small->on; |
| src1.6.7/canonical_state.cpp:110 | AppendStateSnapshot | False | read_access | if (cont) { out << cont->isOpen << '['; for (auto item:cont->smallObjectsInside) out << item->id << ','; out << ']'; } |
| src1.6.7/canonical_state.cpp:111 | AppendStateSnapshot | False | read_access | out << ':' << (id<objectLocationVerified.size() && objectLocationVerified[id]) |
| src1.6.7/canonical_state.cpp:112 | AppendStateSnapshot | False | read_access | << ':' << (id<objectInsideVerified.size() && objectInsideVerified[id]) |
| src1.6.7/canonical_state.cpp:113 | AppendStateSnapshot | False | read_access | << ':' << (id<containerStateVerified.size() && containerStateVerified[id]) |
| src1.6.7/canonical_state.cpp:114 | AppendStateSnapshot | False | read_access | << ':' << int(LocationSource(id)) << ':' << int(InsideSource(id)) << ':' << int(ContainerSource(id)) |
| src1.6.7/canonical_state.cpp:115 | AppendStateSnapshot | False | read_access | << ':' << (id<objectLocationInferredByMustNear.size() && objectLocationInferredByMustNear[id]) << ';'; |
| src1.6.7/canonical_state.cpp:118 | AppendStateSnapshot | False | read_access | out << location << ':' << hold_id << ':' << plate_id << ':' << (hold?hold->id:0) << ':' << (plate?plate->id:0) << ';'; |
| src1.6.7/canonical_state.cpp:119 | AppendStateSnapshot | False | read_access | for (bool b:constraint_eligible) out << b; |
| src1.6.7/canonical_state.cpp:120 | AppendStateSnapshot | False | read_access | out << ';'; for (bool b:constraint_uncertain) out << b; |
| src1.6.7/canonical_state.cpp:121 | AppendStateSnapshot | False | read_access | out << ';'; for (int v:score_locations) out << v << ','; |
| src1.6.7/canonical_state.cpp:127 | DebugStateConsistency | False | read_access | const auto check = [&](StateField f, unsigned id, int legacy, bool verified, EvidenceSource source) { |
| src1.6.7/canonical_state.cpp:128 | DebugStateConsistency | False | read_access | const auto& p=Provenance(f,id); const auto fact=ResolvedState(f,id); |
| src1.6.7/canonical_state.cpp:129 | DebugStateConsistency | False | read_access | if (p.resolved_verified != verified \|\| p.resolved_source != source) issue(id,"compatibility metadata"); |
| src1.6.7/canonical_state.cpp:130 | DebugStateConsistency | False | read_access | if (p.resolved_verified && p.resolved_value != UNKNOWN && legacy != p.resolved_value) issue(id,"resolved/legacy value"); |
| src1.6.7/canonical_state.cpp:131 | DebugStateConsistency | False | read_access | if (p.resolved_verified && p.resolved_value != UNKNOWN && !ResolutionEligible(f,id)) issue(id,"invalid resolution"); |
| src1.6.7/canonical_state.cpp:133 | DebugStateConsistency | False | read_access | if (p.dependency_count>2) issue(id,"dependency bound"); |
| src1.6.7/canonical_state.cpp:137 | DebugStateConsistency | False | read_access | check(StateField::LOCATION,id,objects[id]->location,id<objectLocationVerified.size() && objectLocationVerified[id],LocationSource(id)); |
| src1.6.7/canonical_state.cpp:139 | DebugStateConsistency | False | read_access | if (small) check(StateField::INSIDE,id,small->inside,id<objectInsideVerified.size() && objectInsideVerified[id],InsideSource(id)); |
| src1.6.7/canonical_state.cpp:141 | DebugStateConsistency | False | read_access | if (cont) check(StateField::CONTAINER_STATE,id,cont->isOpen,id<containerStateVerified.size() && containerStateVerified[id],ContainerSource(id)); |
| src1.6.7/canonical_state.cpp:147 | DebugStateConsistency | False | read_access | if (!container) issue(id,"inside target"); |
| src1.6.7/canonical_state.cpp:148 | DebugStateConsistency | False | read_access | else if (FactLocation(id)!=UNKNOWN && FactLocation(container->id)!=UNKNOWN && FactLocation(id)!=FactLocation(container->id)) issue(id,"inside location"); |
| src1.6.7/canonical_state.cpp:150 | DebugStateConsistency | False | read_access | if (cont) for (auto item:cont->smallObjectsInside) |
| src1.6.7/canonical_state.cpp:151 | DebugStateConsistency | False | read_access | if (!item \|\| item->inside!=cont->id) issue(id,"membership cache"); |
| src1.6.7/canonical_state.cpp:154 | DebugStateConsistency | False | read_access | const int legacy=f==StateField::HOLD?hold_id:plate_id; |
| src1.6.7/canonical_state.cpp:155 | DebugStateConsistency | False | read_access | const auto ptr=f==StateField::HOLD?hold:plate; |
| src1.6.7/canonical_state.cpp:157 | DebugStateConsistency | False | read_access | const auto& p=Provenance(f,0); |
| src1.6.7/canonical_state.cpp:158 | DebugStateConsistency | False | read_access | check(f,0,legacy,p.resolved_verified,p.resolved_source); |
| src1.6.7/canonical_state.cpp:160 | DebugStateConsistency | False | read_access | if (holdProvenance.resolved_verified && plateProvenance.resolved_verified && |
| src1.6.7/canonical_state.cpp:161 | DebugStateConsistency | False | read_access | holdProvenance.resolved_value>0 && holdProvenance.resolved_value==plateProvenance.resolved_value) issue(0,"exclusive storage"); |
| src1.6.7/legacy_priority.cpp:25 | isLocationKnown | False | read_access | return o && (h?o->location:w.FactLocation(o->id))!=UNKNOWN; |
| src1.6.7/legacy_priority.cpp:28 | isInsideKnown | False | read_access | return o && (h?o->inside:w.FactInside(o->id))!=UNKNOWN; |
| src1.6.7/legacy_priority.cpp:31 | isContainerStateKnown | False | read_access | return o && (h?o->isOpen:w.FactContainerState(o->id))!=UNKNOWN; |
| src1.6.7/legacy_priority.cpp:43 | evaluatePair | False | read_access | if (!hypothesis && (hypothesis?world.location:world.FactLocation(0)) != _home::UNKNOWN && |
| src1.6.7/legacy_priority.cpp:44 | evaluatePair | False | read_access | world.IsAbsentFromSensedLocation(x->id, (hypothesis?world.location:world.FactLocation(0)))) |
| src1.6.7/legacy_priority.cpp:46 | evaluatePair | False | read_access | if (!isLocationKnown(world, x, hypothesis) \|\| (hypothesis?world.location:world.FactLocation(0)) == _home::UNKNOWN) |
| src1.6.7/legacy_priority.cpp:48 | evaluatePair | False | read_access | return boolStatus((hypothesis?world.location:world.FactLocation(0)) == (hypothesis?x->location:world.FactLocation(x->id))); |
| src1.6.7/legacy_priority.cpp:58 | evaluatePair | False | read_access | return boolStatus(static_cast<bool>((hypothesis?container->isOpen:world.FactContainerState(container->id))) == expect_open); |
| src1.6.7/legacy_priority.cpp:62 | evaluatePair | False | read_access | const bool stored = (hypothesis?(world.hold_id==x->id \|\| world.plate_id==x->id):world.IsStoredFact(x->id)); |
| src1.6.7/legacy_priority.cpp:63 | evaluatePair | False | read_access | if (!hypothesis && world.stage == 2 && !world.IsInsideVerified(x->id)) |
| src1.6.7/legacy_priority.cpp:73 | evaluatePair | False | read_access | if ((hypothesis?(world.hold_id==x->id \|\| world.plate_id==x->id):world.IsStoredFact(x->id))) |
| src1.6.7/legacy_priority.cpp:75 | evaluatePair | False | read_access | if ((hypothesis?small->inside:world.FactInside(small->id)) != _home::NONE) return TerminalStatus::UNSATISFIED; |
| src1.6.7/legacy_priority.cpp:80 | evaluatePair | False | read_access | if (behave == "putin" \|\| behave == "inside" \|\| behave == "in") { |
| src1.6.7/legacy_priority.cpp:84 | evaluatePair | False | read_access | return boolStatus((hypothesis?small->inside:world.FactInside(small->id)) == y->id); |
| src1.6.7/legacy_priority.cpp:91 | evaluatePair | False | read_access | return boolStatus((hypothesis?small->inside:world.FactInside(small->id)) != y->id); |
| src1.6.7/legacy_priority.cpp:94 | evaluatePair | False | read_access | if (behave == "puton" \|\| behave == "on" \|\| behave == "near" \|\| |
| src1.6.7/legacy_priority.cpp:99 | evaluatePair | False | read_access | world.IsAbsentFromSensedLocation(target->id, (hypothesis?x->location:world.FactLocation(x->id)))) |
| src1.6.7/legacy_priority.cpp:102 | evaluatePair | False | read_access | world.IsAbsentFromSensedLocation(x->id, (hypothesis?target->location:world.FactLocation(target->id)))) |
| src1.6.7/legacy_priority.cpp:107 | evaluatePair | False | read_access | if (behave == "puton" \|\| behave == "on" \|\| behave == "give") { |
| src1.6.7/legacy_priority.cpp:111 | evaluatePair | False | read_access | if ((hypothesis?(world.hold_id==x->id \|\| world.plate_id==x->id):world.IsStoredFact(x->id))) |
| src1.6.7/legacy_priority.cpp:113 | evaluatePair | False | read_access | if ((hypothesis?small->inside:world.FactInside(small->id)) != _home::NONE) return TerminalStatus::UNSATISFIED; |
| src1.6.7/legacy_priority.cpp:115 | evaluatePair | False | read_access | return boolStatus((hypothesis?x->location:world.FactLocation(x->id)) == (hypothesis?target->location:world.FactLocation(target->id))); |
| src1.6.7/legacy_priority.cpp:118 | evaluatePair | False | read_access | if (behave == "plate") { |
| src1.6.7/legacy_priority.cpp:119 | evaluatePair | False | read_access | if (hypothesis) return boolStatus(world.plate_id==x->id); |
| src1.6.7/legacy_priority.cpp:120 | evaluatePair | False | read_access | if (!hypothesis && world.stage == 2 && !world.IsInsideVerified(x->id)) |
| src1.6.7/legacy_priority.cpp:122 | evaluatePair | False | read_access | return (hypothesis?world.plate_id:world.FactValue(StateField::PLATE))==UNKNOWN && !world.IsNotStoredFact(x->id) ? TerminalStatus::UNKNOWN : boolStatus((hypothesis?world.plate_id:world.FactValue(StateField::PLATE)) == x->id); |
| src1.6.7/legacy_priority.cpp:125 | evaluatePair | False | read_access | if (behave == "hold") { |
| src1.6.7/legacy_priority.cpp:126 | evaluatePair | False | read_access | if (hypothesis) return boolStatus(world.hold_id==x->id); |
| src1.6.7/legacy_priority.cpp:127 | evaluatePair | False | read_access | if (!hypothesis && world.stage == 2 && !world.IsInsideVerified(x->id)) |
| src1.6.7/legacy_priority.cpp:129 | evaluatePair | False | read_access | return (hypothesis?world.hold_id:world.FactValue(StateField::HOLD))==UNKNOWN && !world.IsNotStoredFact(x->id) ? TerminalStatus::UNKNOWN : boolStatus((hypothesis?world.hold_id:world.FactValue(StateField::HOLD)) == x->id); |
| src1.6.7/legacy_priority.cpp:194 | evaluateAll | False | read_access | const bool has_ledger = world.constraint_eligible.size() == |
| src1.6.7/legacy_priority.cpp:201 | evaluateAll | False | read_access | const bool eligible = !has_ledger \|\| world.constraint_eligible[result.constraints.size()-1]; |
| src1.6.7/legacy_priority.cpp:202 | evaluateAll | True | local_result | result.constraint_eligible.push_back(eligible); |
| src1.6.7/legacy_priority.cpp:212 | evaluateAll | False | read_access | const bool eligible = !has_ledger \|\| world.constraint_eligible[result.constraints.size()-1]; |
| src1.6.7/legacy_priority.cpp:213 | evaluateAll | True | local_result | result.constraint_eligible.push_back(eligible); |
| src1.6.7/legacy_priority.cpp:223 | evaluateAll | False | read_access | const bool eligible = !has_ledger \|\| world.constraint_eligible[result.constraints.size()-1]; |
| src1.6.7/legacy_priority.cpp:224 | evaluateAll | True | local_result | result.constraint_eligible.push_back(eligible); |
| src1.6.7/parser.cpp:602 | get_info_instruction | False | read_access | else if (is_match_rule(father, BE, PREP, NP))//be on the... |
| src1.6.7/parser.cpp:608 | get_info_instruction | False | read_access | else if (is_match_rule(father, BE, NOT, PREP, NP))// be not on |
| src1.6.7/parser.cpp:651 | get_info_instruction | False | read_access | if (instr.behave == "on" && instr.isUseY && instr.conditionY.sort == "plate") |
| src1.6.7/parser.cpp:653 | get_info_instruction | False | read_access | instr.behave = "plate"; |
| src1.6.7/parser.cpp:658 | get_info_instruction | False | read_access | instr.behave = "on"; |
| src1.6.7/question_preflight.cpp:30 | SemanticInstructionKey | False | declaration | // Do NOT use positions: two objects at the same location remain two goals. |
| src1.6.7/question_preflight.cpp:32 | SemanticInstructionKey | False | read_access | if (predicate == "in") predicate = "inside"; |
| src1.6.7/question_preflight.cpp:56 | RunQuestionPreflight | False | read_access | if (location < 0 \|\| location > MAX_LOCATION_ID) |
| src1.6.7/question_preflight.cpp:57 | RunQuestionPreflight | False | read_access | world_error("robot has no usable initial location"); |
| src1.6.7/question_preflight.cpp:71 | RunQuestionPreflight | False | read_access | if (object->sort.empty() && !small && !big && object->location == UNKNOWN) |
| src1.6.7/question_preflight.cpp:75 | RunQuestionPreflight | False | read_access | if (object->location < UNKNOWN \|\| object->location > MAX_LOCATION_ID) |
| src1.6.7/question_preflight.cpp:76 | RunQuestionPreflight | False | read_access | world_error("object location out of bounds: " + std::to_string(i)); |
| src1.6.7/question_preflight.cpp:82 | RunQuestionPreflight | False | declaration | // Stage 2 location descriptions can be wrong; collisions there are NOT |
| src1.6.7/question_preflight.cpp:84 | RunQuestionPreflight | False | read_access | if (stage == 1 && big && object->location != UNKNOWN && |
| src1.6.7/question_preflight.cpp:85 | RunQuestionPreflight | False | read_access | !big_locations.emplace(object->location, object->id).second) |
| src1.6.7/question_preflight.cpp:86 | RunQuestionPreflight | False | read_access | world_warning("multiple big objects at Stage 1 location " + |
| src1.6.7/question_preflight.cpp:87 | RunQuestionPreflight | False | read_access | std::to_string(object->location)); |
| src1.6.7/rdfw.cpp:178 | EvidenceName | False | read_access | const char* EvidenceName(EvidenceSource source) { |
| src1.6.7/rdfw.cpp:180 | EvidenceName | False | read_access | case EvidenceSource::UNKNOWN: return "unknown"; |
| src1.6.7/rdfw.cpp:181 | EvidenceName | False | read_access | case EvidenceSource::INITIAL: return "initial"; |
| src1.6.7/rdfw.cpp:182 | EvidenceName | False | read_access | case EvidenceSource::EXPLICIT_INFO: return "explicit_info"; |
| src1.6.7/rdfw.cpp:183 | EvidenceName | False | read_access | case EvidenceSource::CONSTRAINT_DERIVED: return "constraint_derived"; |
| src1.6.7/rdfw.cpp:184 | EvidenceName | False | read_access | case EvidenceSource::RELATION_DERIVED: return "relation_derived"; |
| src1.6.7/rdfw.cpp:185 | EvidenceName | False | read_access | case EvidenceSource::CONSTRAINT_HEURISTIC: return "constraint_heuristic"; |
| src1.6.7/rdfw.cpp:186 | EvidenceName | False | read_access | case EvidenceSource::SENSE: return "sense"; |
| src1.6.7/rdfw.cpp:187 | EvidenceName | False | read_access | case EvidenceSource::ACTION_SUCCESS: return "action_success"; |
| src1.6.7/rdfw.cpp:188 | EvidenceName | False | read_access | case EvidenceSource::ACTION_FAILURE: return "action_failure"; |
| src1.6.7/rdfw.cpp:189 | EvidenceName | False | read_access | case EvidenceSource::ASK_ANSWER: return "ask_answer"; |
| src1.6.7/rdfw.cpp:275 | CaptureCandidateEvidence | False | read_access | if (Provenance(StateField::LOCATION,i).resolved_source != EvidenceSource::UNKNOWN) { |
| src1.6.7/rdfw.cpp:278 | CaptureCandidateEvidence | False | read_access | fact.fact = "location"; |
| src1.6.7/rdfw.cpp:279 | CaptureCandidateEvidence | False | read_access | fact.source = EvidenceName(Provenance(StateField::LOCATION,i).resolved_source); |
| src1.6.7/rdfw.cpp:280 | CaptureCandidateEvidence | False | read_access | fact.verified = IsLocationVerified(static_cast<unsigned int>(i)); |
| src1.6.7/rdfw.cpp:283 | CaptureCandidateEvidence | False | read_access | if (Provenance(StateField::INSIDE,i).resolved_source != EvidenceSource::UNKNOWN) { |
| src1.6.7/rdfw.cpp:286 | CaptureCandidateEvidence | False | read_access | fact.fact = "inside"; |
| src1.6.7/rdfw.cpp:287 | CaptureCandidateEvidence | False | read_access | fact.source = EvidenceName(Provenance(StateField::INSIDE,i).resolved_source); |
| src1.6.7/rdfw.cpp:288 | CaptureCandidateEvidence | False | read_access | fact.verified = IsInsideVerified(static_cast<unsigned int>(i)); |
| src1.6.7/rdfw.cpp:291 | CaptureCandidateEvidence | False | read_access | if (Provenance(StateField::CONTAINER_STATE,i).resolved_source != EvidenceSource::UNKNOWN) { |
| src1.6.7/rdfw.cpp:295 | CaptureCandidateEvidence | False | read_access | fact.source = EvidenceName(Provenance(StateField::CONTAINER_STATE,i).resolved_source); |
| src1.6.7/rdfw.cpp:296 | CaptureCandidateEvidence | False | read_access | fact.verified = IsContainerStateVerified(static_cast<unsigned int>(i)); |
| src1.6.7/rdfw.cpp:301 | CaptureCandidateEvidence | False | read_access | CandidateEvidence e; e.object_id=0; e.fact=f==StateField::HOLD?"hold":"plate"; |
| src1.6.7/rdfw.cpp:302 | CaptureCandidateEvidence | False | read_access | e.source=EvidenceName(Provenance(f,0).resolved_source); e.verified=ResolvedState(f,0).present; |
| src1.6.7/rdfw.cpp:335 | BuildTaskGroupPlan | False | snapshot_restore | const std::vector<bool> original_constraint_eligible = constraint_eligible; |
| src1.6.7/rdfw.cpp:336 | BuildTaskGroupPlan | False | snapshot_restore | std::vector<bool> saved_constraint_uncertain = constraint_uncertain; |
| src1.6.7/rdfw.cpp:337 | BuildTaskGroupPlan | False | snapshot_restore | std::vector<int> saved_score_locations = score_locations; |
| src1.6.7/rdfw.cpp:340 | BuildTaskGroupPlan | False | snapshot_restore | int location; |
| src1.6.7/rdfw.cpp:344 | BuildTaskGroupPlan | False | snapshot_restore | int inside; |
| src1.6.7/rdfw.cpp:345 | BuildTaskGroupPlan | False | snapshot_restore | int on; |
| src1.6.7/rdfw.cpp:360 | BuildTaskGroupPlan | True | snapshot_restore | state.location = objects[i]->location; |
| src1.6.7/rdfw.cpp:367 | BuildTaskGroupPlan | True | snapshot_restore | state.inside = small->inside; |
| src1.6.7/rdfw.cpp:368 | BuildTaskGroupPlan | True | snapshot_restore | state.on = small->on; |
| src1.6.7/rdfw.cpp:374 | BuildTaskGroupPlan | False | snapshot_restore | state.is_open = container->isOpen; |
| src1.6.7/rdfw.cpp:375 | BuildTaskGroupPlan | False | snapshot_restore | state.contents = container->smallObjectsInside; |
| src1.6.7/rdfw.cpp:382 | BuildTaskGroupPlan | False | snapshot_restore | const int saved_location = location; |
| src1.6.7/rdfw.cpp:383 | BuildTaskGroupPlan | False | snapshot_restore | const int saved_hold_id = hold_id; |
| src1.6.7/rdfw.cpp:384 | BuildTaskGroupPlan | False | snapshot_restore | const int saved_plate_id = plate_id; |
| src1.6.7/rdfw.cpp:413 | BuildTaskGroupPlan | False | snapshot_restore | std::vector<bool> saved_inferred = objectLocationInferredByMustNear; |
| src1.6.7/rdfw.cpp:415 | BuildTaskGroupPlan | False | snapshot_restore | std::vector<bool> saved_pos_sensed = posSensedFlag; |
| src1.6.7/rdfw.cpp:416 | BuildTaskGroupPlan | False | snapshot_restore | std::vector<bool> saved_location_verified = objectLocationVerified; |
| src1.6.7/rdfw.cpp:417 | BuildTaskGroupPlan | False | snapshot_restore | std::vector<bool> saved_inside_verified = objectInsideVerified; |
| src1.6.7/rdfw.cpp:418 | BuildTaskGroupPlan | False | snapshot_restore | std::vector<bool> saved_container_verified = containerStateVerified; |
| src1.6.7/rdfw.cpp:419 | BuildTaskGroupPlan | False | snapshot_restore | std::vector<EvidenceSource> saved_location_source = objectLocationSource; |
| src1.6.7/rdfw.cpp:420 | BuildTaskGroupPlan | False | snapshot_restore | std::vector<EvidenceSource> saved_inside_source = objectInsideSource; |
| src1.6.7/rdfw.cpp:421 | BuildTaskGroupPlan | False | snapshot_restore | std::vector<EvidenceSource> saved_container_source = containerStateSource; |
| src1.6.7/rdfw.cpp:422 | BuildTaskGroupPlan | False | snapshot_restore | std::vector<StateProvenance> saved_location_provenance = locationProvenance; |
| src1.6.7/rdfw.cpp:423 | BuildTaskGroupPlan | False | snapshot_restore | std::vector<StateProvenance> saved_inside_provenance = insideProvenance; |
| src1.6.7/rdfw.cpp:424 | BuildTaskGroupPlan | False | snapshot_restore | std::vector<StateProvenance> saved_container_provenance = containerProvenance; |
| src1.6.7/rdfw.cpp:425 | BuildTaskGroupPlan | False | snapshot_restore | StateProvenance saved_hold_provenance = holdProvenance; |
| src1.6.7/rdfw.cpp:426 | BuildTaskGroupPlan | False | snapshot_restore | StateProvenance saved_plate_provenance = plateProvenance; |
| src1.6.7/rdfw.cpp:429 | BuildTaskGroupPlan | False | snapshot_restore | std::vector<LocationSensedInfo> saved_sensed_objects = locationSensedObjects; |
| src1.6.7/rdfw.cpp:481 | BuildTaskGroupPlan | True | snapshot_restore | objectLocationInferredByMustNear = std::move(saved_inferred); |
| src1.6.7/rdfw.cpp:483 | BuildTaskGroupPlan | True | snapshot_restore | posSensedFlag = std::move(saved_pos_sensed); |
| src1.6.7/rdfw.cpp:484 | BuildTaskGroupPlan | True | snapshot_restore | objectLocationVerified = std::move(saved_location_verified); |
| src1.6.7/rdfw.cpp:485 | BuildTaskGroupPlan | True | snapshot_restore | objectInsideVerified = std::move(saved_inside_verified); |
| src1.6.7/rdfw.cpp:486 | BuildTaskGroupPlan | True | snapshot_restore | containerStateVerified = std::move(saved_container_verified); |
| src1.6.7/rdfw.cpp:487 | BuildTaskGroupPlan | True | snapshot_restore | objectLocationSource = std::move(saved_location_source); |
| src1.6.7/rdfw.cpp:488 | BuildTaskGroupPlan | True | snapshot_restore | objectInsideSource = std::move(saved_inside_source); |
| src1.6.7/rdfw.cpp:489 | BuildTaskGroupPlan | True | snapshot_restore | containerStateSource = std::move(saved_container_source); |
| src1.6.7/rdfw.cpp:490 | BuildTaskGroupPlan | True | snapshot_restore | locationProvenance = std::move(saved_location_provenance); |
| src1.6.7/rdfw.cpp:491 | BuildTaskGroupPlan | True | snapshot_restore | insideProvenance = std::move(saved_inside_provenance); |
| src1.6.7/rdfw.cpp:492 | BuildTaskGroupPlan | True | snapshot_restore | containerProvenance = std::move(saved_container_provenance); |
| src1.6.7/rdfw.cpp:493 | BuildTaskGroupPlan | True | snapshot_restore | holdProvenance = std::move(saved_hold_provenance); |
| src1.6.7/rdfw.cpp:494 | BuildTaskGroupPlan | True | snapshot_restore | plateProvenance = std::move(saved_plate_provenance); |
| src1.6.7/rdfw.cpp:497 | BuildTaskGroupPlan | True | snapshot_restore | locationSensedObjects = std::move(saved_sensed_objects); |
| src1.6.7/rdfw.cpp:505 | BuildTaskGroupPlan | True | snapshot_restore | objects[i]->location = state.location; |
| src1.6.7/rdfw.cpp:512 | BuildTaskGroupPlan | True | snapshot_restore | small->inside = state.inside; |
| src1.6.7/rdfw.cpp:513 | BuildTaskGroupPlan | True | snapshot_restore | small->on = state.on; |
| src1.6.7/rdfw.cpp:522 | BuildTaskGroupPlan | True | snapshot_restore | container->isOpen = object_states[i].is_open; |
| src1.6.7/rdfw.cpp:523 | BuildTaskGroupPlan | True | snapshot_restore | container->smallObjectsInside.swap(object_states[i].contents); |
| src1.6.7/rdfw.cpp:526 | BuildTaskGroupPlan | True | snapshot_restore | location = std::move(saved_location); |
| src1.6.7/rdfw.cpp:527 | BuildTaskGroupPlan | True | snapshot_restore | hold_id = std::move(saved_hold_id); |
| src1.6.7/rdfw.cpp:528 | BuildTaskGroupPlan | True | snapshot_restore | plate_id = std::move(saved_plate_id); |
| src1.6.7/rdfw.cpp:529 | BuildTaskGroupPlan | True | snapshot_restore | hold = saved_hold_id > 0 && static_cast<std::size_t>(saved_hold_id) < objects.size() |
| src1.6.7/rdfw.cpp:531 | BuildTaskGroupPlan | True | snapshot_restore | plate = saved_plate_id > 0 && static_cast<std::size_t>(saved_plate_id) < objects.size() |
| src1.6.7/rdfw.cpp:546 | BuildTaskGroupPlan | True | snapshot_restore | constraint_eligible = std::move(saved_constraint_eligible); |
| src1.6.7/rdfw.cpp:547 | BuildTaskGroupPlan | True | snapshot_restore | constraint_uncertain = std::move(saved_constraint_uncertain); |
| src1.6.7/rdfw.cpp:548 | BuildTaskGroupPlan | True | snapshot_restore | score_locations = std::move(saved_score_locations); |
| src1.6.7/rdfw.cpp:655 | BuildTaskGroupPlan | False | snapshot_restore | const int projected_location = location; |
| src1.6.7/rdfw.cpp:725 | BuildSyntheticPutOnCandidate | False | read_access | terminal.constraint_eligible.begin(), terminal.constraint_eligible.end(), true)); |
| src1.6.7/rdfw.cpp:837 | EvaluateShadowCandidates | False | read_access | LOG("[TaskGroupShadow] phase=%s revision=%zu stop_score=%d " |
| src1.6.7/rdfw.cpp:871 | RefreshTaskStates | False | read_access | LOG(CYAN_BLUE "[Recovery] reactivated task=%zu behave=%s revision=%zu\n" RESET, |
| src1.6.7/rdfw.cpp:974 | CanStartPlan | False | declaration | // 100 ms output reserve; it never relies on a truncated/empty preview. |
| src1.6.7/rdfw.cpp:1035 | ShouldStartConstraintTrade | False | read_access | if (plan.legacy_before.constraint_eligible[i] && |
| src1.6.7/rdfw.cpp:1252 | PlanStateSignature | False | read_access | out << location << ',' << hold_id << ',' << plate_id << ',' |
| src1.6.7/rdfw.cpp:1257 | PlanStateSignature | False | read_access | out << object->id << ',' << object->location << ',' |
| src1.6.7/rdfw.cpp:1261 | PlanStateSignature | False | read_access | if (small) out << ',' << small->inside << ',' << small->on; |
| src1.6.7/rdfw.cpp:1265 | PlanStateSignature | False | read_access | out << ',' << container->isOpen << '['; |
| src1.6.7/rdfw.cpp:1267 | PlanStateSignature | False | read_access | container->smallObjectsInside) |
| src1.6.7/rdfw.cpp:1277 | PlanStateSignature | False | read_access | for (bool value : constraint_eligible) out << value; |
| src1.6.7/rdfw.cpp:1279 | PlanStateSignature | False | read_access | for (bool value : constraint_uncertain) out << value; |
| src1.6.7/rdfw.cpp:1280 | PlanStateSignature | False | read_access | out << ":score_locations:"; |
| src1.6.7/rdfw.cpp:1281 | PlanStateSignature | False | read_access | for (int value : score_locations) out << value << ","; |
| src1.6.7/rdfw.cpp:1284 | PlanStateSignature | False | read_access | out << (i < objectLocationVerified.size() && objectLocationVerified[i]) |
| src1.6.7/rdfw.cpp:1285 | PlanStateSignature | False | read_access | << ':' << (i < objectInsideVerified.size() && objectInsideVerified[i]) |
| src1.6.7/rdfw.cpp:1286 | PlanStateSignature | False | read_access | << ':' << (i < containerStateVerified.size() && containerStateVerified[i]) |
| src1.6.7/rdfw.cpp:1287 | PlanStateSignature | False | read_access | << ':' << (i < objectLocationSource.size() ? |
| src1.6.7/rdfw.cpp:1288 | PlanStateSignature | False | read_access | static_cast<int>(objectLocationSource[i]) : -1) |
| src1.6.7/rdfw.cpp:1289 | PlanStateSignature | False | read_access | << ':' << (i < objectInsideSource.size() ? |
| src1.6.7/rdfw.cpp:1290 | PlanStateSignature | False | read_access | static_cast<int>(objectInsideSource[i]) : -1) |
| src1.6.7/rdfw.cpp:1291 | PlanStateSignature | False | read_access | << ':' << (i < containerStateSource.size() ? |
| src1.6.7/rdfw.cpp:1292 | PlanStateSignature | False | read_access | static_cast<int>(containerStateSource[i]) : -1) << ','; |
| src1.6.7/rdfw.cpp:1361 | InitializeConstraintLedger | False | initialization | if (constraint_eligible.size() == count && constraint_uncertain.size() == count) return; |
| src1.6.7/rdfw.cpp:1364 | InitializeConstraintLedger | True | initialization | constraint_eligible.swap(e); constraint_uncertain.swap(u); |
| src1.6.7/rdfw.cpp:1373 | UpdateConstraintLedger | False | canonical_mutation | const std::vector<bool> eligibility_before = constraint_eligible; |
| src1.6.7/rdfw.cpp:1378 | UpdateConstraintLedger | True | canonical_mutation | if (score_locations.size() < objects.size()) score_locations.resize(objects.size(), UNKNOWN); |
| src1.6.7/rdfw.cpp:1380 | UpdateConstraintLedger | True | canonical_mutation | if (hold_id > 0) score_locations[hold_id] = location; |
| src1.6.7/rdfw.cpp:1381 | UpdateConstraintLedger | True | canonical_mutation | if (plate_id > 0) score_locations[plate_id] = location; |
| src1.6.7/rdfw.cpp:1382 | UpdateConstraintLedger | False | canonical_mutation | } else if (!arguments.empty() && arguments[0] < score_locations.size()) { |
| src1.6.7/rdfw.cpp:1383 | UpdateConstraintLedger | True | canonical_mutation | if (performed == "PutIn") score_locations[arguments[0]] = UNKNOWN; |
| src1.6.7/rdfw.cpp:1386 | UpdateConstraintLedger | True | canonical_mutation | performed == "FromPlate") score_locations[arguments[0]] = location; |
| src1.6.7/rdfw.cpp:1393 | UpdateConstraintLedger | True | canonical_mutation | constraint_eligible[i] = false; |
| src1.6.7/rdfw.cpp:1394 | UpdateConstraintLedger | True | canonical_mutation | constraint_uncertain[i] = false; |
| src1.6.7/rdfw.cpp:1396 | UpdateConstraintLedger | False | canonical_mutation | constraint_eligible[i]) { |
| src1.6.7/rdfw.cpp:1397 | UpdateConstraintLedger | True | canonical_mutation | constraint_uncertain[i] = true; |
| src1.6.7/rdfw.cpp:1405 | UpdateConstraintLedger | False | canonical_mutation | for (std::size_t i = 0; i < constraint_eligible.size(); ++i) |
| src1.6.7/rdfw.cpp:1406 | UpdateConstraintLedger | False | canonical_mutation | if (eligibility_before[i] && !constraint_eligible[i]) |
| src1.6.7/rdfw.cpp:1410 | UpdateConstraintLedger | False | canonical_mutation | for (std::size_t i = 0; i < constraint_eligible.size(); ++i) |
| src1.6.7/rdfw.cpp:1411 | UpdateConstraintLedger | False | canonical_mutation | if (eligibility_before[i] && !constraint_eligible[i] && |
| src1.6.7/rdfw.cpp:1434 | DryRunActionSucceeds | False | read_access | static_cast<int>(arguments[0]) != location; |
| src1.6.7/rdfw.cpp:1442 | DryRunActionSucceeds | False | read_access | return small && hold_id == NONE && plate_id != static_cast<int>(a) && |
| src1.6.7/rdfw.cpp:1443 | DryRunActionSucceeds | False | read_access | small->location == location && |
| src1.6.7/rdfw.cpp:1444 | DryRunActionSucceeds | False | read_access | (small->inside == NONE \|\| small->inside == UNKNOWN); |
| src1.6.7/rdfw.cpp:1446 | DryRunActionSucceeds | False | read_access | if (action == "PutDown") return hold_id == static_cast<int>(a); |
| src1.6.7/rdfw.cpp:1448 | DryRunActionSucceeds | False | read_access | return hold_id == static_cast<int>(a) && plate_id == NONE; |
| src1.6.7/rdfw.cpp:1450 | DryRunActionSucceeds | False | read_access | return plate_id == static_cast<int>(a) && hold_id == NONE; |
| src1.6.7/rdfw.cpp:1454 | DryRunActionSucceeds | False | read_access | return container && container->location == location && hold_id == NONE && |
| src1.6.7/rdfw.cpp:1455 | DryRunActionSucceeds | False | read_access | container->isOpen == (action == "Open" ? 0 : 1); |
| src1.6.7/rdfw.cpp:1464 | DryRunActionSucceeds | False | read_access | if (!small \|\| !container \|\| container->location != location \|\| |
| src1.6.7/rdfw.cpp:1465 | DryRunActionSucceeds | False | read_access | container->isOpen != 1) return false; |
| src1.6.7/rdfw.cpp:1466 | DryRunActionSucceeds | False | read_access | if (action == "PutIn") return hold_id == static_cast<int>(a); |
| src1.6.7/rdfw.cpp:1467 | DryRunActionSucceeds | False | read_access | return hold_id == NONE && small->inside == static_cast<int>(b); |
| src1.6.7/rdfw.cpp:1474 | DryRunSenseIds | False | read_access | if (location < 0) return; |
| src1.6.7/rdfw.cpp:1476 | DryRunSenseIds | False | read_access | if (!objects[i] \|\| objects[i]->location != location) continue; |
| src1.6.7/rdfw.cpp:1477 | DryRunSenseIds | False | read_access | if (static_cast<int>(i) == hold_id \|\| static_cast<int>(i) == plate_id) continue; |
| src1.6.7/rdfw.cpp:1480 | DryRunSenseIds | False | read_access | if (small && small->inside > 0 && |
| src1.6.7/rdfw.cpp:1481 | DryRunSenseIds | False | read_access | static_cast<std::size_t>(small->inside) < objects.size()) { |
| src1.6.7/rdfw.cpp:1483 | DryRunSenseIds | False | read_access | std::dynamic_pointer_cast<Container>(objects[small->inside]); |
| src1.6.7/rdfw.cpp:1484 | DryRunSenseIds | False | read_access | if (container && container->isOpen != 1) continue; |
| src1.6.7/rdfw.cpp:1534 | InitializeDynamicArrays | True | initialization | objectLocationVerified.assign(max_size, false); |
| src1.6.7/rdfw.cpp:1535 | InitializeDynamicArrays | True | initialization | objectLocationInferredByMustNear.assign(max_size, false); |
| src1.6.7/rdfw.cpp:1536 | InitializeDynamicArrays | True | initialization | objectInsideVerified.assign(max_size, false); |
| src1.6.7/rdfw.cpp:1537 | InitializeDynamicArrays | True | initialization | containerStateVerified.assign(max_size, false); |
| src1.6.7/rdfw.cpp:1538 | InitializeDynamicArrays | True | initialization | objectLocationSource.assign(max_size, EvidenceSource::UNKNOWN); |
| src1.6.7/rdfw.cpp:1539 | InitializeDynamicArrays | True | initialization | objectInsideSource.assign(max_size, EvidenceSource::UNKNOWN); |
| src1.6.7/rdfw.cpp:1540 | InitializeDynamicArrays | True | initialization | containerStateSource.assign(max_size, EvidenceSource::UNKNOWN); |
| src1.6.7/rdfw.cpp:1541 | InitializeDynamicArrays | True | initialization | locationProvenance.assign(max_size, StateProvenance()); |
| src1.6.7/rdfw.cpp:1542 | InitializeDynamicArrays | True | initialization | insideProvenance.assign(max_size, StateProvenance()); |
| src1.6.7/rdfw.cpp:1543 | InitializeDynamicArrays | True | initialization | containerProvenance.assign(max_size, StateProvenance()); |
| src1.6.7/rdfw.cpp:1544 | InitializeDynamicArrays | True | initialization | holdProvenance = StateProvenance(); |
| src1.6.7/rdfw.cpp:1545 | InitializeDynamicArrays | True | initialization | plateProvenance = StateProvenance(); |
| src1.6.7/rdfw.cpp:1715 | Init | True | initialization | posSensedFlag.resize(100, false);  // 为100个位置预留空间，全部标记为未感知 |
| src1.6.7/rdfw.cpp:1718 | Init | True | initialization | locationSensedObjects.resize(100);  // 为100个位置预留空间 |
| src1.6.7/rdfw.cpp:1732 | Plan | True | initialization | constraint_eligible.clear(); |
| src1.6.7/rdfw.cpp:1733 | Plan | True | initialization | constraint_uncertain.clear(); |
| src1.6.7/rdfw.cpp:1734 | Plan | True | initialization | score_locations.clear(); |
| src1.6.7/rdfw.cpp:1772 | Plan | True | initialization | location = UNKNOWN; |
| src1.6.7/rdfw.cpp:1773 | Plan | True | initialization | hold = nullptr; |
| src1.6.7/rdfw.cpp:1774 | Plan | True | initialization | hold_id = 0; |
| src1.6.7/rdfw.cpp:1777 | Plan | False | initialization | for (size_t i = 0; i < posSensedFlag.size(); i++) { |
| src1.6.7/rdfw.cpp:1778 | Plan | True | initialization | posSensedFlag[i] = false; |
| src1.6.7/rdfw.cpp:1780 | Plan | False | initialization | fill(objectLocationVerified.begin(), objectLocationVerified.end(), false); |
| src1.6.7/rdfw.cpp:1781 | Plan | False | initialization | fill(objectLocationInferredByMustNear.begin(), objectLocationInferredByMustNear.end(), false); |
| src1.6.7/rdfw.cpp:1782 | Plan | False | initialization | fill(objectInsideVerified.begin(), objectInsideVerified.end(), false); |
| src1.6.7/rdfw.cpp:1783 | Plan | False | initialization | fill(containerStateVerified.begin(), containerStateVerified.end(), false); |
| src1.6.7/rdfw.cpp:1784 | Plan | False | initialization | fill(objectLocationSource.begin(), objectLocationSource.end(), EvidenceSource::UNKNOWN); |
| src1.6.7/rdfw.cpp:1785 | Plan | False | initialization | fill(objectInsideSource.begin(), objectInsideSource.end(), EvidenceSource::UNKNOWN); |
| src1.6.7/rdfw.cpp:1786 | Plan | False | initialization | fill(containerStateSource.begin(), containerStateSource.end(), EvidenceSource::UNKNOWN); |
| src1.6.7/rdfw.cpp:1787 | Plan | False | initialization | fill(locationProvenance.begin(), locationProvenance.end(), StateProvenance()); |
| src1.6.7/rdfw.cpp:1788 | Plan | False | initialization | fill(insideProvenance.begin(), insideProvenance.end(), StateProvenance()); |
| src1.6.7/rdfw.cpp:1789 | Plan | False | initialization | fill(containerProvenance.begin(), containerProvenance.end(), StateProvenance()); |
| src1.6.7/rdfw.cpp:1790 | Plan | True | initialization | holdProvenance = StateProvenance(); |
| src1.6.7/rdfw.cpp:1791 | Plan | True | initialization | plateProvenance = StateProvenance(); |
| src1.6.7/rdfw.cpp:1794 | Plan | False | initialization | for (auto& loc_info : locationSensedObjects) { |
| src1.6.7/rdfw.cpp:1947 | Plan | False | initialization | LOG("[TradeoffEvidence] probing current location before decisions\n"); |
| src1.6.7/rdfw.cpp:2240 | ExecuteGuardedGroup | False | read_access | actual_terminal.constraint_eligible != |
| src1.6.7/rdfw.cpp:2241 | ExecuteGuardedGroup | False | read_access | group.terminal_after.constraint_eligible \|\| |
| src1.6.7/rdfw.cpp:2433 | ExecuteTerminalRecovery | False | read_access | "goals=%zu/%zu revision=%zu\n" RESET, |
| src1.6.7/rdfw.cpp:2440 | ExecuteTerminalRecovery | False | read_access | "actions=%zu revision=%zu\n" RESET, |
| src1.6.7/rdfw.cpp:2479 | Cons_plan | False | read_access | if(cons.behave=="on") { |
| src1.6.7/rdfw.cpp:2480 | Cons_plan | False | read_access | if (cons.Y.empty() \|\| !cons.Y[0] \|\| cons.Y[0]->location < 0 \|\| |
| src1.6.7/rdfw.cpp:2481 | Cons_plan | False | read_access | !EnsureLocationCapacity(cons.Y[0]->location)) continue; |
| src1.6.7/rdfw.cpp:2482 | Cons_plan | False | read_access | if(cons.X[0]->location!=cons.Y[0]->location) putdown_cons[cons.X[0]->id][cons.Y[0]->location]++; |
| src1.6.7/rdfw.cpp:2483 | Cons_plan | False | read_access | else if(cons.X[0]->id==plate_id\|\|cons.X[0]->id==hold_id) putdown_cons[cons.X[0]->id][cons.Y[0]->location]++; |
| src1.6.7/rdfw.cpp:2485 | Cons_plan | False | read_access | else if(cons.behave=="inside"\|\|cons.behave=="in") { |
| src1.6.7/rdfw.cpp:2488 | Cons_plan | False | read_access | if(small && small->inside!=cons.Y[0]->id) putin_cons[cons.X[0]->id][cons.Y[0]->id]++; |
| src1.6.7/rdfw.cpp:2492 | Cons_plan | False | read_access | if(cons.Y[0]->location!=cons.X[0]->location) //如果约束没有触犯 |
| src1.6.7/rdfw.cpp:2494 | Cons_plan | False | read_access | if(cons.Y[0]->location!=UNKNOWN) move_cons[cons.X[0]->id][cons.Y[0]->location]++; |
| src1.6.7/rdfw.cpp:2495 | Cons_plan | False | read_access | if(cons.X[0]->location!=UNKNOWN) move_cons[cons.Y[0]->id][cons.X[0]->location]++; |
| src1.6.7/rdfw.cpp:2498 | Cons_plan | False | read_access | else if(cons.behave == "plate") toplate_cons[cons.X[0]->id]++; |
| src1.6.7/rdfw.cpp:2501 | Cons_plan | False | read_access | if(cont && cont->isOpen!=1) open_cons[cons.X[0]->id]++; |
| src1.6.7/rdfw.cpp:2506 | Cons_plan | False | read_access | if(cont && cont->isOpen==1) close_cons[cons.X[0]->id]++; |
| src1.6.7/rdfw.cpp:2515 | Cons_plan | False | read_access | if(cons.behave=="on" && !cons.Y.empty() && cons.Y[0] && |
| src1.6.7/rdfw.cpp:2516 | Cons_plan | False | read_access | cons.X[0]->location==cons.Y[0]->location) { |
| src1.6.7/rdfw.cpp:2518 | Cons_plan | False | read_access | if(small && small->inside!=cons.Y[0]->id) cons.X[0]->is_keep++; |
| src1.6.7/rdfw.cpp:2527 | Cons_plan | False | read_access | if (x_obj->location != UNKNOWN && x_obj->location == y_obj->location) { |
| src1.6.7/rdfw.cpp:2534 | Cons_plan | False | read_access | else if(cons.behave=="plate"&& plate_id==cons.X[0]->id)fromplate_cons[cons.X[0]->id]++; |
| src1.6.7/rdfw.cpp:2535 | Cons_plan | False | read_access | else if(cons.behave=="inside"\|\|cons.behave=="in") |
| src1.6.7/rdfw.cpp:2539 | Cons_plan | False | read_access | if(small && small->inside==cons.Y[0]->id)  takeout_cons[cons.X[0]->id][cons.Y[0]->id]++; |
| src1.6.7/rdfw.cpp:2543 | Cons_plan | False | read_access | if(cont && cont->isOpen!=1) open_cons[cons.X[0]->id]++; |
| src1.6.7/rdfw.cpp:2547 | Cons_plan | False | read_access | if(cont && cont->isOpen!=1) close_cons[cons.X[0]->id]++; |
| src1.6.7/rdfw.cpp:2560 | Cons_plan | False | read_access | cons.Y[0]->location >= 0 && EnsureLocationCapacity(cons.Y[0]->location)) |
| src1.6.7/rdfw.cpp:2561 | Cons_plan | False | read_access | putdown_cons[cons.X[0]->id][cons.Y[0]->location]++; |
| src1.6.7/rdfw.cpp:2562 | Cons_plan | False | read_access | else if(cons.behave=="goto" && cons.X[0]->location >= 0 && |
| src1.6.7/rdfw.cpp:2563 | Cons_plan | False | read_access | EnsureLocationCapacity(cons.X[0]->location)) goto_cons[cons.X[0]->location]++; |
| src1.6.7/rdfw.cpp:2570 | Cons_plan | False | read_access | if(IsValidObjectId(hold_id) && location >= 0 && EnsureLocationCapacity(location)) { |
| src1.6.7/rdfw.cpp:2571 | Cons_plan | False | read_access | x=hold_id; |
| src1.6.7/rdfw.cpp:2572 | Cons_plan | False | read_access | if(objects[x]->is_keep>putdown1_cons[x]+putdown_cons[x][location]+fromplate_cons[x]){ |
| src1.6.7/rdfw.cpp:2573 | Cons_plan | False | read_access | cout<<"the hold object must putdown here!"<<endl; |
| src1.6.7/rdfw.cpp:2577 | Cons_plan | False | read_access | if(IsValidObjectId(plate_id) && location >= 0 && EnsureLocationCapacity(location)) |
| src1.6.7/rdfw.cpp:2579 | Cons_plan | False | read_access | x=plate_id; |
| src1.6.7/rdfw.cpp:2580 | Cons_plan | False | read_access | if(objects[x]->is_keep>putdown1_cons[x]+putdown_cons[x][location]+fromplate_cons[x]){ |
| src1.6.7/rdfw.cpp:2581 | Cons_plan | False | read_access | cout<<"the plate object must putdown here!"<<endl; |
| src1.6.7/rdfw.cpp:2582 | Cons_plan | False | read_access | if(hold_id>0) PutDown(hold_id); |
| src1.6.7/rdfw.cpp:2606 | FilterConstraintsByTaskConflicts | False | read_access | if ((task.behave == "goto" && has_x && task.X[0]->location == loc) \|\| |
| src1.6.7/rdfw.cpp:2607 | FilterConstraintsByTaskConflicts | False | read_access | (task.behave == "putin" && has_y && task.Y[0]->location == loc) \|\| |
| src1.6.7/rdfw.cpp:2608 | FilterConstraintsByTaskConflicts | False | read_access | (task.behave == "putin" && has_x && task.X[0]->location == loc)\|\| |
| src1.6.7/rdfw.cpp:2609 | FilterConstraintsByTaskConflicts | False | read_access | (task.behave == "puton" && has_y && task.Y[0]->location == loc)\|\| |
| src1.6.7/rdfw.cpp:2610 | FilterConstraintsByTaskConflicts | False | read_access | (task.behave == "puton" && has_x && task.X[0]->location == loc)\|\| |
| src1.6.7/rdfw.cpp:2611 | FilterConstraintsByTaskConflicts | False | read_access | (task.behave == "open" && has_x && task.X[0]->location == loc)\|\| |
| src1.6.7/rdfw.cpp:2612 | FilterConstraintsByTaskConflicts | False | read_access | (task.behave == "close" && has_x && task.X[0]->location == loc)\|\| |
| src1.6.7/rdfw.cpp:2613 | FilterConstraintsByTaskConflicts | False | read_access | (task.behave == "pickup" && has_x && task.X[0]->location == loc)\|\| |
| src1.6.7/rdfw.cpp:2614 | FilterConstraintsByTaskConflicts | False | read_access | (task.behave == "give" && has_x && task.X[0]->location == loc)\|\| |
| src1.6.7/rdfw.cpp:2615 | FilterConstraintsByTaskConflicts | False | read_access | (task.behave == "give" && has_y && task.Y[0]->location == loc)\|\| |
| src1.6.7/rdfw.cpp:2616 | FilterConstraintsByTaskConflicts | False | read_access | (task.behave == "takeout" && has_y && task.Y[0]->location == loc)) { |
| src1.6.7/rdfw.cpp:2618 | FilterConstraintsByTaskConflicts | False | read_access | cout << "[FilterConstraintsByTaskConflicts] Conflict found between goto_cons at location " << loc << " and task " << task.behave << endl; |
| src1.6.7/rdfw.cpp:2629 | FilterConstraintsByTaskConflicts | False | read_access | cout << "[FilterConstraintsByTaskConflicts] Conflict found between goto_cons at location " << loc << " with conflict count " << conflict_count << endl; |
| src1.6.7/rdfw.cpp:2637 | FilterConstraintsByTaskConflicts | False | read_access | cout << "[FilterConstraintsByTaskConflicts] Discarded goto_cons at location " << max_effect_loc << " due to " << max_effect << " conflicts." << endl; |
| src1.6.7/rdfw.cpp:2642 | FilterConstraintsByTaskConflicts | False | read_access | cout << "[FilterConstraintsByTaskConflicts] Discarded goto_cons at location " << it->first << " due to " << it->second << " conflicts." << endl; |
| src1.6.7/rdfw.cpp:2732 | TaskOptimization | False | declaration | // Sort tasks based on behavior evaluation and container grouping for takeout tasks |
| src1.6.7/rdfw.cpp:2820 | CalculateTaskRisk | False | read_access | if(small->inside!=t.Y[0]->id) return 0;//如果任务满足 |
| src1.6.7/rdfw.cpp:2821 | CalculateTaskRisk | False | read_access | t.risk+=takeout_cons[t.X[0]->id][t.Y[0]->id]+goto_risk(t.Y[0]->location); |
| src1.6.7/rdfw.cpp:2828 | CalculateTaskRisk | False | read_access | if(small->inside==t.Y[0]->id) return 0; |
| src1.6.7/rdfw.cpp:2830 | CalculateTaskRisk | False | read_access | if (t.Y[0]->location >= 0 && EnsureLocationCapacity(t.Y[0]->location)) |
| src1.6.7/rdfw.cpp:2831 | CalculateTaskRisk | False | read_access | t.risk += move_cons[t.X[0]->id][t.Y[0]->location]; |
| src1.6.7/rdfw.cpp:2832 | CalculateTaskRisk | False | read_access | if(t.X[0]->location!=t.Y[0]->location) t.risk+=goto_risk(t.Y[0]->location); |
| src1.6.7/rdfw.cpp:2837 | CalculateTaskRisk | False | read_access | if (t.Y[0]->location >= 0 && EnsureLocationCapacity(t.Y[0]->location)) |
| src1.6.7/rdfw.cpp:2838 | CalculateTaskRisk | False | read_access | t.risk+= putdown_cons[t.X[0]->id][t.Y[0]->location]+move_cons[t.X[0]->id][t.Y[0]->location]; |
| src1.6.7/rdfw.cpp:2840 | CalculateTaskRisk | False | read_access | if(t.X[0]->location!=t.Y[0]->location) t.risk+=goto_risk(t.Y[0]->location); |
| src1.6.7/rdfw.cpp:2844 | CalculateTaskRisk | False | read_access | int loc = t.X[0]->location; |
| src1.6.7/rdfw.cpp:2852 | CalculateTaskRisk | False | read_access | else if(t.behave=="open") t.risk+=open_cons[t.X[0]->id]+goto_risk(t.X[0]->location); |
| src1.6.7/rdfw.cpp:2853 | CalculateTaskRisk | False | read_access | else if(t.behave=="close") t.risk+=close_cons[t.X[0]->id]+goto_risk(t.X[0]->location); |
| src1.6.7/rdfw.cpp:2861 | CalculateTaskRisk | False | read_access | if (human->location >= 0 && EnsureLocationCapacity(human->location)) |
| src1.6.7/rdfw.cpp:2862 | CalculateTaskRisk | False | read_access | t.risk += move_cons[t.X[0]->id][human->location]; |
| src1.6.7/rdfw.cpp:2863 | CalculateTaskRisk | False | read_access | if(t.X[0]->location!=human->location) t.risk+=goto_risk(human->location); |
| src1.6.7/rdfw.cpp:2868 | CalculateTaskRisk | False | declaration | // goto targets an object's location; the target object itself is untouched. |
| src1.6.7/rdfw.cpp:2889 | CalculateTaskRisk | False | read_access | if (other && other->location == t.X[0]->location && t.X[0]->location != UNKNOWN) { |
| src1.6.7/rdfw.cpp:2907 | CalculateStepRisk | False | read_access | if(t.X[0]->location!=location && t.X[0]->location >= 0) { |
| src1.6.7/rdfw.cpp:2908 | CalculateStepRisk | False | read_access | if (!EnsureLocationCapacity(t.X[0]->location)) return 0; |
| src1.6.7/rdfw.cpp:2909 | CalculateStepRisk | False | read_access | t.risk+=goto_cons[t.X[0]->location]; |
| src1.6.7/rdfw.cpp:2913 | CalculateStepRisk | False | read_access | if(small->inside!=UNKNOWN&&small->inside!=NONE && |
| src1.6.7/rdfw.cpp:2914 | CalculateStepRisk | False | read_access | IsValidObjectId(small->inside)) |
| src1.6.7/rdfw.cpp:2915 | CalculateStepRisk | False | read_access | t.risk+=open_cons[small->inside]+takeout_cons[small->id][small->inside]; |
| src1.6.7/rdfw.cpp:2916 | CalculateStepRisk | False | read_access | else if(small->inside==NONE) t.risk+=pickup_cons[small->id]; |
| src1.6.7/rdfw.cpp:2937 | EnsureLocationCapacity | False | declaration | // Normal inputs stay inside the preallocated range.  Keep this hot path |
| src1.6.7/rdfw.cpp:2938 | EnsureLocationCapacity | False | declaration | // constant-time; full row scans are needed only when a new location column |
| src1.6.7/rdfw.cpp:2942 | EnsureLocationCapacity | False | initialization | required <= posSensedFlag.size() && |
| src1.6.7/rdfw.cpp:2943 | EnsureLocationCapacity | False | initialization | required <= locationSensedObjects.size() && |
| src1.6.7/rdfw.cpp:2953 | EnsureLocationCapacity | True | initialization | if (loc >= (int)posSensedFlag.size()) posSensedFlag.resize(loc + 1, false); |
| src1.6.7/rdfw.cpp:2954 | EnsureLocationCapacity | True | initialization | if (loc >= (int)locationSensedObjects.size()) locationSensedObjects.resize(loc + 1); |
| src1.6.7/rdfw.cpp:3024 | EnsureEvidenceCapacity | True | initialization | if (objectLocationVerified.capacity()<required) objectLocationVerified.reserve(required); |
| src1.6.7/rdfw.cpp:3025 | EnsureEvidenceCapacity | True | initialization | if (objectLocationInferredByMustNear.capacity()<required) objectLocationInferredByMustNear.reserve(required); |
| src1.6.7/rdfw.cpp:3026 | EnsureEvidenceCapacity | True | initialization | if (objectInsideVerified.capacity()<required) objectInsideVerified.reserve(required); |
| src1.6.7/rdfw.cpp:3027 | EnsureEvidenceCapacity | True | initialization | if (containerStateVerified.capacity()<required) containerStateVerified.reserve(required); |
| src1.6.7/rdfw.cpp:3028 | EnsureEvidenceCapacity | True | initialization | if (objectLocationSource.capacity()<required) objectLocationSource.reserve(required); |
| src1.6.7/rdfw.cpp:3029 | EnsureEvidenceCapacity | True | initialization | if (objectInsideSource.capacity()<required) objectInsideSource.reserve(required); |
| src1.6.7/rdfw.cpp:3030 | EnsureEvidenceCapacity | True | initialization | if (containerStateSource.capacity()<required) containerStateSource.reserve(required); |
| src1.6.7/rdfw.cpp:3031 | EnsureEvidenceCapacity | True | initialization | if (locationProvenance.capacity()<required) locationProvenance.reserve(required); |
| src1.6.7/rdfw.cpp:3032 | EnsureEvidenceCapacity | True | initialization | if (insideProvenance.capacity()<required) insideProvenance.reserve(required); |
| src1.6.7/rdfw.cpp:3033 | EnsureEvidenceCapacity | True | initialization | if (containerProvenance.capacity()<required) containerProvenance.reserve(required); |
| src1.6.7/rdfw.cpp:3034 | EnsureEvidenceCapacity | False | initialization | if (objectLocationVerified.size() < required) |
| src1.6.7/rdfw.cpp:3035 | EnsureEvidenceCapacity | True | initialization | objectLocationVerified.resize(required, false); |
| src1.6.7/rdfw.cpp:3036 | EnsureEvidenceCapacity | False | initialization | if (objectLocationInferredByMustNear.size() < required) |
| src1.6.7/rdfw.cpp:3037 | EnsureEvidenceCapacity | True | initialization | objectLocationInferredByMustNear.resize(required, false); |
| src1.6.7/rdfw.cpp:3038 | EnsureEvidenceCapacity | False | initialization | if (objectInsideVerified.size() < required) |
| src1.6.7/rdfw.cpp:3039 | EnsureEvidenceCapacity | True | initialization | objectInsideVerified.resize(required, false); |
| src1.6.7/rdfw.cpp:3040 | EnsureEvidenceCapacity | False | initialization | if (containerStateVerified.size() < required) |
| src1.6.7/rdfw.cpp:3041 | EnsureEvidenceCapacity | True | initialization | containerStateVerified.resize(required, false); |
| src1.6.7/rdfw.cpp:3042 | EnsureEvidenceCapacity | False | initialization | if (objectLocationSource.size() < required) |
| src1.6.7/rdfw.cpp:3043 | EnsureEvidenceCapacity | True | initialization | objectLocationSource.resize(required, EvidenceSource::UNKNOWN); |
| src1.6.7/rdfw.cpp:3044 | EnsureEvidenceCapacity | False | initialization | if (objectInsideSource.size() < required) |
| src1.6.7/rdfw.cpp:3045 | EnsureEvidenceCapacity | True | initialization | objectInsideSource.resize(required, EvidenceSource::UNKNOWN); |
| src1.6.7/rdfw.cpp:3046 | EnsureEvidenceCapacity | False | initialization | if (containerStateSource.size() < required) |
| src1.6.7/rdfw.cpp:3047 | EnsureEvidenceCapacity | True | initialization | containerStateSource.resize(required, EvidenceSource::UNKNOWN); |
| src1.6.7/rdfw.cpp:3048 | EnsureEvidenceCapacity | True | initialization | if (locationProvenance.size() < required) locationProvenance.resize(required); |
| src1.6.7/rdfw.cpp:3049 | EnsureEvidenceCapacity | True | initialization | if (insideProvenance.size() < required) insideProvenance.resize(required); |
| src1.6.7/rdfw.cpp:3050 | EnsureEvidenceCapacity | True | initialization | if (containerProvenance.size() < required) containerProvenance.resize(required); |
| src1.6.7/rdfw.cpp:3054 | MutableProvenance | False | read_access | StateProvenance& RDFW::MutableProvenance(StateField field, unsigned int id) { |
| src1.6.7/rdfw.cpp:3059 | MutableProvenance | False | read_access | if (field == StateField::HOLD) return holdProvenance; |
| src1.6.7/rdfw.cpp:3060 | MutableProvenance | False | read_access | if (field == StateField::PLATE) return plateProvenance; |
| src1.6.7/rdfw.cpp:3061 | MutableProvenance | False | read_access | if (field == StateField::LOCATION) return locationProvenance[id]; |
| src1.6.7/rdfw.cpp:3062 | MutableProvenance | False | read_access | if (field == StateField::INSIDE) return insideProvenance[id]; |
| src1.6.7/rdfw.cpp:3063 | MutableProvenance | False | read_access | return containerProvenance[id]; |
| src1.6.7/rdfw.cpp:3066 | Provenance | False | read_access | const StateProvenance& RDFW::Provenance(StateField field, unsigned int id) const { |
| src1.6.7/rdfw.cpp:3067 | Provenance | False | read_access | static const StateProvenance empty; |
| src1.6.7/rdfw.cpp:3068 | Provenance | False | read_access | if (field == StateField::HOLD) return holdProvenance; |
| src1.6.7/rdfw.cpp:3069 | Provenance | False | read_access | if (field == StateField::PLATE) return plateProvenance; |
| src1.6.7/rdfw.cpp:3070 | Provenance | False | read_access | const std::vector<StateProvenance>& records = field == StateField::LOCATION |
| src1.6.7/rdfw.cpp:3071 | Provenance | False | read_access | ? locationProvenance : field == StateField::INSIDE |
| src1.6.7/rdfw.cpp:3072 | Provenance | False | read_access | ? insideProvenance : containerProvenance; |
| src1.6.7/rdfw.cpp:3076 | SetHold | False | canonical_mutation | void RDFW::SetHold(const shared_ptr<SmallObject>& item, EvidenceSource source) { |
| src1.6.7/rdfw.cpp:3078 | SetHold | False | canonical_mutation | const int old_plate = plate_id; |
| src1.6.7/rdfw.cpp:3083 | SetHold | False | canonical_mutation | const bool verified = stage == 1 \|\| source == EvidenceSource::ACTION_SUCCESS; |
| src1.6.7/rdfw.cpp:3084 | SetHold | False | canonical_mutation | UpdateProvenance(StateField::HOLD, 0, hold_id, verified, source); |
| src1.6.7/rdfw.cpp:3090 | SetHold | False | canonical_mutation | if (old_plate != plate_id) |
| src1.6.7/rdfw.cpp:3091 | SetHold | False | canonical_mutation | UpdateProvenance(StateField::PLATE, 0, plate_id, verified, source); |
| src1.6.7/rdfw.cpp:3094 | SetPlate | False | canonical_mutation | void RDFW::SetPlate(const shared_ptr<SmallObject>& item, EvidenceSource source) { |
| src1.6.7/rdfw.cpp:3096 | SetPlate | False | canonical_mutation | const int old_hold = hold_id; |
| src1.6.7/rdfw.cpp:3101 | SetPlate | False | canonical_mutation | const bool verified = stage == 1 \|\| source == EvidenceSource::ACTION_SUCCESS; |
| src1.6.7/rdfw.cpp:3102 | SetPlate | False | canonical_mutation | if (old_hold != hold_id) |
| src1.6.7/rdfw.cpp:3103 | SetPlate | False | canonical_mutation | UpdateProvenance(StateField::HOLD, 0, hold_id, verified, source); |
| src1.6.7/rdfw.cpp:3104 | SetPlate | False | canonical_mutation | UpdateProvenance(StateField::PLATE, 0, plate_id, verified, source); |
| src1.6.7/rdfw.cpp:3113 | HasContradictoryEvidence | False | read_access | const StateProvenance& p = Provenance(field, id); |
| src1.6.7/rdfw.cpp:3114 | HasContradictoryEvidence | False | read_access | return p.received.present && p.conflicting.present && |
| src1.6.7/rdfw.cpp:3115 | HasContradictoryEvidence | False | read_access | p.received.value != p.conflicting.value; |
| src1.6.7/rdfw.cpp:3119 | ReceiveWeakClaim | False | canonical_mutation | EvidenceSource source) { |
| src1.6.7/rdfw.cpp:3122 | ReceiveWeakClaim | False | canonical_mutation | StateProvenance& p = MutableProvenance(field, id); |
| src1.6.7/rdfw.cpp:3123 | ReceiveWeakClaim | False | canonical_mutation | const bool previous_weak = p.received.present && |
| src1.6.7/rdfw.cpp:3124 | ReceiveWeakClaim | False | canonical_mutation | (p.received.source == EvidenceSource::INITIAL \|\| |
| src1.6.7/rdfw.cpp:3125 | ReceiveWeakClaim | False | canonical_mutation | p.received.source == EvidenceSource::ASK_ANSWER \|\| |
| src1.6.7/rdfw.cpp:3126 | ReceiveWeakClaim | False | canonical_mutation | p.received.source == EvidenceSource::EXPLICIT_INFO); |
| src1.6.7/rdfw.cpp:3128 | ReceiveWeakClaim | False | canonical_mutation | p.received.value != value; |
| src1.6.7/rdfw.cpp:3129 | ReceiveWeakClaim | True | canonical_mutation | if (conflict) p.conflicting = p.received; |
| src1.6.7/rdfw.cpp:3130 | ReceiveWeakClaim | True | canonical_mutation | p.received = StateClaim(value, source, true); |
| src1.6.7/rdfw.cpp:3131 | ReceiveWeakClaim | False | canonical_mutation | return !conflict && !(stage == 2 && p.conflicting.present && |
| src1.6.7/rdfw.cpp:3132 | ReceiveWeakClaim | False | canonical_mutation | p.conflicting.value != p.received.value); |
| src1.6.7/rdfw.cpp:3138 | MarkUnresolved | False | canonical_mutation | StateProvenance& p = MutableProvenance(field, id); |
| src1.6.7/rdfw.cpp:3139 | MarkUnresolved | False | canonical_mutation | if (p.resolved_value != UNKNOWN \|\| p.resolved_source != EvidenceSource::UNKNOWN) |
| src1.6.7/rdfw.cpp:3140 | MarkUnresolved | False | canonical_mutation | ++p.revision; |
| src1.6.7/rdfw.cpp:3141 | MarkUnresolved | True | canonical_mutation | p.resolved_value = UNKNOWN; |
| src1.6.7/rdfw.cpp:3142 | MarkUnresolved | True | canonical_mutation | p.resolved_source = EvidenceSource::UNKNOWN; |
| src1.6.7/rdfw.cpp:3143 | MarkUnresolved | True | canonical_mutation | p.resolved_verified = false; |
| src1.6.7/rdfw.cpp:3144 | MarkUnresolved | True | canonical_mutation | p.dependency_count = 0; |
| src1.6.7/rdfw.cpp:3145 | MarkUnresolved | True | canonical_mutation | p.support_constraint_index = UNKNOWN; |
| src1.6.7/rdfw.cpp:3146 | MarkUnresolved | True | canonical_mutation | p.supporting_constraints.clear(); |
| src1.6.7/rdfw.cpp:3147 | MarkUnresolved | True | canonical_mutation | if (field == StateField::LOCATION) { objectLocationVerified[id]=false; objectLocationSource[id]=EvidenceSource::UNKNOWN; } |
| src1.6.7/rdfw.cpp:3148 | MarkUnresolved | True | canonical_mutation | if (field == StateField::INSIDE) { objectInsideVerified[id]=false; objectInsideSource[id]=EvidenceSource::UNKNOWN; } |
| src1.6.7/rdfw.cpp:3149 | MarkUnresolved | True | canonical_mutation | if (field == StateField::CONTAINER_STATE) { containerStateVerified[id]=false; containerStateSource[id]=EvidenceSource::UNKNOWN; } |
| src1.6.7/rdfw.cpp:3152 | UpdateProvenance | False | canonical_mutation | void RDFW::UpdateProvenance(StateField field, unsigned int id, int value, |
| src1.6.7/rdfw.cpp:3153 | UpdateProvenance | False | canonical_mutation | bool verified, EvidenceSource source) { |
| src1.6.7/rdfw.cpp:3155 | UpdateProvenance | False | canonical_mutation | StateProvenance& p = MutableProvenance(field, id); |
| src1.6.7/rdfw.cpp:3156 | UpdateProvenance | False | canonical_mutation | const bool derived = source == EvidenceSource::CONSTRAINT_DERIVED \|\| |
| src1.6.7/rdfw.cpp:3157 | UpdateProvenance | False | canonical_mutation | source == EvidenceSource::RELATION_DERIVED \|\| |
| src1.6.7/rdfw.cpp:3158 | UpdateProvenance | False | canonical_mutation | source == EvidenceSource::CONSTRAINT_HEURISTIC; |
| src1.6.7/rdfw.cpp:3159 | UpdateProvenance | False | canonical_mutation | if (!derived && source != EvidenceSource::UNKNOWN) { |
| src1.6.7/rdfw.cpp:3160 | UpdateProvenance | False | canonical_mutation | if (p.received.present && p.received.value != value) |
| src1.6.7/rdfw.cpp:3161 | UpdateProvenance | True | canonical_mutation | p.conflicting = p.received; |
| src1.6.7/rdfw.cpp:3162 | UpdateProvenance | True | canonical_mutation | p.received = StateClaim{value, source, true}; |
| src1.6.7/rdfw.cpp:3164 | UpdateProvenance | False | declaration | // A new direct resolution supersedes dependencies of an old inference. |
| src1.6.7/rdfw.cpp:3165 | UpdateProvenance | True | canonical_mutation | p.dependency_count = 0; |
| src1.6.7/rdfw.cpp:3166 | UpdateProvenance | True | canonical_mutation | p.support_constraint_index = UNKNOWN; |
| src1.6.7/rdfw.cpp:3167 | UpdateProvenance | True | canonical_mutation | p.supporting_constraints.clear(); |
| src1.6.7/rdfw.cpp:3169 | UpdateProvenance | False | declaration | // the current state. Weak conflicting claims cannot independently resolve it. |
| src1.6.7/rdfw.cpp:3173 | UpdateProvenance | False | canonical_mutation | if (p.resolved_value != value \|\| p.resolved_source != source \|\| |
| src1.6.7/rdfw.cpp:3174 | UpdateProvenance | False | canonical_mutation | p.resolved_verified != verified \|\| p.revision == 0) ++p.revision; |
| src1.6.7/rdfw.cpp:3175 | UpdateProvenance | True | canonical_mutation | p.resolved_value = value; |
| src1.6.7/rdfw.cpp:3176 | UpdateProvenance | True | canonical_mutation | p.resolved_source = source; |
| src1.6.7/rdfw.cpp:3177 | UpdateProvenance | True | canonical_mutation | p.resolved_verified = verified && value != UNKNOWN && source != EvidenceSource::CONSTRAINT_HEURISTIC; |
| src1.6.7/rdfw.cpp:3179 | UpdateProvenance | True | canonical_mutation | if (field == StateField::LOCATION) { objectLocationVerified[id]=p.resolved_verified; objectLocationSource[id]=source; } |
| src1.6.7/rdfw.cpp:3180 | UpdateProvenance | True | canonical_mutation | if (field == StateField::INSIDE) { objectInsideVerified[id]=p.resolved_verified; objectInsideSource[id]=source; } |
| src1.6.7/rdfw.cpp:3181 | UpdateProvenance | True | canonical_mutation | if (field == StateField::CONTAINER_STATE) { containerStateVerified[id]=p.resolved_verified; containerStateSource[id]=source; } |
| src1.6.7/rdfw.cpp:3188 | DependOn | False | canonical_mutation | StateProvenance& p = MutableProvenance(derived_field, derived_id); |
| src1.6.7/rdfw.cpp:3189 | DependOn | False | canonical_mutation | if (p.dependency_count >= 2) return; |
| src1.6.7/rdfw.cpp:3190 | DependOn | False | canonical_mutation | const StateProvenance& support = Provenance(support_field, support_id); |
| src1.6.7/rdfw.cpp:3191 | DependOn | True | canonical_mutation | p.dependencies[p.dependency_count++] = |
| src1.6.7/rdfw.cpp:3192 | DependOn | False | canonical_mutation | StateDependency{support_field, support_id, support.resolved_value, support.revision}; |
| src1.6.7/rdfw.cpp:3198 | SetConstraintSupport | True | canonical_mutation | MutableProvenance(field, id).support_constraint_index = index; |
| src1.6.7/rdfw.cpp:3202 | RecordConstraintSupports | False | canonical_mutation | StateProvenance& p = MutableProvenance(field, id); |
| src1.6.7/rdfw.cpp:3223 | RecordConstraintSupports | True | canonical_mutation | if (relevant(not_infoConstrains[i])) p.supporting_constraints.push_back(i); |
| src1.6.7/rdfw.cpp:3226 | RecordConstraintSupports | True | canonical_mutation | p.supporting_constraints.push_back(not_infoConstrains.size() + i); |
| src1.6.7/rdfw.cpp:3233 | ResolutionEligible | False | read_access | const StateProvenance& p = Provenance(field, id); |
| src1.6.7/rdfw.cpp:3238 | ResolutionEligible | False | read_access | if (field == StateField::LOCATION && (p.resolved_value < 0 \|\| p.resolved_value > MAX_LOCATION_ID)) return false; |
| src1.6.7/rdfw.cpp:3239 | ResolutionEligible | False | read_access | if (field == StateField::CONTAINER_STATE && p.resolved_value != 0 && p.resolved_value != 1) return false; |
| src1.6.7/rdfw.cpp:3240 | ResolutionEligible | False | read_access | if (field == StateField::INSIDE && (p.resolved_value < 0 \|\| p.resolved_value > int(MAX_OBJECT_ID))) return false; |
| src1.6.7/rdfw.cpp:3241 | ResolutionEligible | False | read_access | if (field == StateField::INSIDE && p.resolved_value > 0 && |
| src1.6.7/rdfw.cpp:3242 | ResolutionEligible | False | read_access | (!IsValidObjectId(p.resolved_value) \|\| !dynamic_cast<Container*>(objects[p.resolved_value].get()))) return false; |
| src1.6.7/rdfw.cpp:3243 | ResolutionEligible | False | read_access | if ((field == StateField::HOLD \|\| field == StateField::PLATE) && (p.resolved_value < 0 \|\| p.resolved_value > int(MAX_OBJECT_ID))) return false; |
| src1.6.7/rdfw.cpp:3244 | ResolutionEligible | False | read_access | if ((field == StateField::HOLD \|\| field == StateField::PLATE) && p.resolved_value > 0 && |
| src1.6.7/rdfw.cpp:3245 | ResolutionEligible | False | read_access | (!IsValidObjectId(p.resolved_value) \|\| !dynamic_cast<SmallObject*>(objects[p.resolved_value].get()))) return false; |
| src1.6.7/rdfw.cpp:3246 | ResolutionEligible | False | read_access | if ((field == StateField::HOLD \|\| field == StateField::PLATE) && p.resolved_value > 0) { |
| src1.6.7/rdfw.cpp:3247 | ResolutionEligible | False | read_access | const auto& other = field == StateField::HOLD ? plateProvenance : holdProvenance; |
| src1.6.7/rdfw.cpp:3248 | ResolutionEligible | False | read_access | if (other.resolved_verified && other.resolved_value == p.resolved_value) return false; |
| src1.6.7/rdfw.cpp:3250 | ResolutionEligible | False | read_access | if (field == StateField::INSIDE && p.resolved_value > 0 && |
| src1.6.7/rdfw.cpp:3251 | ResolutionEligible | False | read_access | ((holdProvenance.resolved_verified && holdProvenance.resolved_value == int(id)) \|\| |
| src1.6.7/rdfw.cpp:3252 | ResolutionEligible | False | read_access | (plateProvenance.resolved_verified && plateProvenance.resolved_value == int(id)))) return false; |
| src1.6.7/rdfw.cpp:3253 | ResolutionEligible | False | read_access | if (p.resolved_source == EvidenceSource::UNKNOWN \|\| |
| src1.6.7/rdfw.cpp:3254 | ResolutionEligible | False | read_access | p.resolved_source == EvidenceSource::CONSTRAINT_HEURISTIC) return false; |
| src1.6.7/rdfw.cpp:3255 | ResolutionEligible | False | read_access | if (!p.resolved_verified \|\| p.resolved_value == UNKNOWN) return false; |
| src1.6.7/rdfw.cpp:3262 | ResolvedState | False | read_access | const auto& p=Provenance(field,id); |
| src1.6.7/rdfw.cpp:3263 | ResolvedState | False | read_access | return StateClaim(p.resolved_value,p.resolved_source,true); |
| src1.6.7/rdfw.cpp:3273 | DependenciesCurrentDepth | False | read_access | const StateProvenance& p = Provenance(field, id); |
| src1.6.7/rdfw.cpp:3274 | DependenciesCurrentDepth | False | read_access | if (p.dependency_count > 2) return false; |
| src1.6.7/rdfw.cpp:3275 | DependenciesCurrentDepth | False | read_access | if (!p.dependency_count && p.supporting_constraints.empty() && p.support_constraint_index<0) return true; |
| src1.6.7/rdfw.cpp:3277 | DependenciesCurrentDepth | False | read_access | for (const std::size_t index : p.supporting_constraints) { |
| src1.6.7/rdfw.cpp:3279 | DependenciesCurrentDepth | False | read_access | if ((index < constraint_eligible.size() && !constraint_eligible[index]) \|\| |
| src1.6.7/rdfw.cpp:3280 | DependenciesCurrentDepth | False | read_access | (index < constraint_uncertain.size() && constraint_uncertain[index])) return false; |
| src1.6.7/rdfw.cpp:3282 | DependenciesCurrentDepth | False | read_access | if (p.support_constraint_index >= 0) { |
| src1.6.7/rdfw.cpp:3283 | DependenciesCurrentDepth | False | read_access | const std::size_t index = static_cast<std::size_t>(p.support_constraint_index); |
| src1.6.7/rdfw.cpp:3285 | DependenciesCurrentDepth | False | read_access | if ((index < constraint_eligible.size() && !constraint_eligible[index]) \|\| |
| src1.6.7/rdfw.cpp:3286 | DependenciesCurrentDepth | False | read_access | (index < constraint_uncertain.size() && constraint_uncertain[index])) |
| src1.6.7/rdfw.cpp:3289 | DependenciesCurrentDepth | False | read_access | for (unsigned int i = 0; i < p.dependency_count; ++i) { |
| src1.6.7/rdfw.cpp:3290 | DependenciesCurrentDepth | False | read_access | const StateDependency& d = p.dependencies[i]; |
| src1.6.7/rdfw.cpp:3291 | DependenciesCurrentDepth | False | read_access | const StateProvenance& support = Provenance(d.field, d.id); |
| src1.6.7/rdfw.cpp:3293 | DependenciesCurrentDepth | False | read_access | support.revision != d.revision \|\| support.resolved_value != d.value) |
| src1.6.7/rdfw.cpp:3301 | MarkDirectLocationEvidence | False | canonical_mutation | EvidenceSource source) { |
| src1.6.7/rdfw.cpp:3304 | MarkDirectLocationEvidence | False | canonical_mutation | const int value = id < objects.size() && objects[id] ? objects[id]->location : UNKNOWN; |
| src1.6.7/rdfw.cpp:3305 | MarkDirectLocationEvidence | False | canonical_mutation | UpdateProvenance(StateField::LOCATION, id, value, verified, source); |
| src1.6.7/rdfw.cpp:3306 | MarkDirectLocationEvidence | False | canonical_mutation | if (source == EvidenceSource::CONSTRAINT_DERIVED \|\| source == EvidenceSource::CONSTRAINT_HEURISTIC) |
| src1.6.7/rdfw.cpp:3308 | MarkDirectLocationEvidence | True | canonical_mutation | objectLocationInferredByMustNear[id] = |
| src1.6.7/rdfw.cpp:3309 | MarkDirectLocationEvidence | False | canonical_mutation | source == EvidenceSource::CONSTRAINT_DERIVED \|\| |
| src1.6.7/rdfw.cpp:3310 | MarkDirectLocationEvidence | False | canonical_mutation | source == EvidenceSource::CONSTRAINT_HEURISTIC; |
| src1.6.7/rdfw.cpp:3313 | SetInsideEvidence | False | canonical_mutation | void RDFW::SetInsideEvidence(unsigned int id, bool verified, EvidenceSource source) { |
| src1.6.7/rdfw.cpp:3317 | SetInsideEvidence | False | canonical_mutation | UpdateProvenance(StateField::INSIDE, id, small ? small->inside : UNKNOWN, verified, source); |
| src1.6.7/rdfw.cpp:3320 | SetContainerEvidence | False | canonical_mutation | void RDFW::SetContainerEvidence(unsigned int id, bool verified, EvidenceSource source) { |
| src1.6.7/rdfw.cpp:3324 | SetContainerEvidence | False | canonical_mutation | UpdateProvenance(StateField::CONTAINER_STATE, id, |
| src1.6.7/rdfw.cpp:3325 | SetContainerEvidence | False | canonical_mutation | container ? container->isOpen : UNKNOWN, verified, source); |
| src1.6.7/rdfw.cpp:3326 | SetContainerEvidence | False | canonical_mutation | if (source == EvidenceSource::CONSTRAINT_DERIVED \|\| source == EvidenceSource::CONSTRAINT_HEURISTIC) |
| src1.6.7/rdfw.cpp:3330 | LocationSource | False | read_access | EvidenceSource RDFW::LocationSource(unsigned int id) const { |
| src1.6.7/rdfw.cpp:3331 | LocationSource | False | read_access | return id < objectLocationSource.size() ? objectLocationSource[id] : EvidenceSource::UNKNOWN; |
| src1.6.7/rdfw.cpp:3333 | InsideSource | False | read_access | EvidenceSource RDFW::InsideSource(unsigned int id) const { |
| src1.6.7/rdfw.cpp:3334 | InsideSource | False | read_access | return id < objectInsideSource.size() ? objectInsideSource[id] : EvidenceSource::UNKNOWN; |
| src1.6.7/rdfw.cpp:3336 | ContainerSource | False | read_access | EvidenceSource RDFW::ContainerSource(unsigned int id) const { |
| src1.6.7/rdfw.cpp:3337 | ContainerSource | False | read_access | return id < containerStateSource.size() ? containerStateSource[id] : EvidenceSource::UNKNOWN; |
| src1.6.7/rdfw.cpp:3345 | InvalidateSenseAtLocation | True | canonical_mutation | posSensedFlag[loc] = false; |
| src1.6.7/rdfw.cpp:3346 | InvalidateSenseAtLocation | False | canonical_mutation | locationSensedObjects[loc].object_ids.clear(); |
| src1.6.7/rdfw.cpp:3347 | InvalidateSenseAtLocation | False | canonical_mutation | locationSensedObjects[loc].container_id = NONE; |
| src1.6.7/rdfw.cpp:3348 | InvalidateSenseAtLocation | False | canonical_mutation | locationSensedObjects[loc].has_container = false; |
| src1.6.7/rdfw.cpp:3351 | IsLocationVerified | False | read_access | bool RDFW::IsLocationVerified(unsigned int id) const { |
| src1.6.7/rdfw.cpp:3355 | IsInsideVerified | False | read_access | bool RDFW::IsInsideVerified(unsigned int id) const { |
| src1.6.7/rdfw.cpp:3359 | IsContainerStateVerified | False | read_access | bool RDFW::IsContainerStateVerified(unsigned int id) const { |
| src1.6.7/rdfw.cpp:3365 | IsAbsentFromSensedLocation | False | read_access | static_cast<std::size_t>(loc) >= posSensedFlag.size() \|\| |
| src1.6.7/rdfw.cpp:3366 | IsAbsentFromSensedLocation | False | read_access | !posSensedFlag[loc] \|\| !IsValidObjectId(static_cast<int>(id)) \|\| |
| src1.6.7/rdfw.cpp:3367 | IsAbsentFromSensedLocation | False | read_access | hold_id == static_cast<int>(id) \|\| plate_id == static_cast<int>(id)) |
| src1.6.7/rdfw.cpp:3369 | IsAbsentFromSensedLocation | False | read_access | const LocationSensedInfo& sensed = locationSensedObjects[loc]; |
| src1.6.7/rdfw.cpp:3372 | IsAbsentFromSensedLocation | False | declaration | // A closed container can hide a small object at this location. |
| src1.6.7/rdfw.cpp:3495 | HoldSmallObject | False | read_access | if (plate_id == a) |
| src1.6.7/rdfw.cpp:3497 | HoldSmallObject | False | read_access | if (hold_id != NONE && !PutDown(hold_id)) return false; |
| src1.6.7/rdfw.cpp:3501 | HoldSmallObject | False | read_access | if (hold_id != NONE && !PutDown(hold_id)) return false; |
| src1.6.7/rdfw.cpp:3502 | HoldSmallObject | False | read_access | if(location!=target_small->location && !Move(target_small->location)) return false; |
| src1.6.7/rdfw.cpp:3503 | HoldSmallObject | False | read_access | if(target_small->inside==NONE) return PickUp(a); |
| src1.6.7/rdfw.cpp:3504 | HoldSmallObject | False | read_access | else if(target_small->inside!=UNKNOWN)//说明小物体在容器里面 |
| src1.6.7/rdfw.cpp:3506 | HoldSmallObject | False | read_access | if (!IsValidObjectId(target_small->inside)) return false; |
| src1.6.7/rdfw.cpp:3507 | HoldSmallObject | False | read_access | auto target_cont = dynamic_pointer_cast<Container>(objects[target_small->inside]); |
| src1.6.7/rdfw.cpp:3509 | HoldSmallObject | False | read_access | if(!target_cont->isOpen && !Open(target_cont->id)) return false; |
| src1.6.7/rdfw.cpp:3515 | HoldSmallObject | False | read_access | if (hold_id == static_cast<int>(a)) { |
| src1.6.7/rdfw.cpp:3517 | HoldSmallObject | False | declaration | // 初始 hold 事实可能是错的。用一次可观察动作建立本地事实；失败则清除猜测。 |
| src1.6.7/rdfw.cpp:3519 | HoldSmallObject | False | read_access | SetHold(nullptr, EvidenceSource::ACTION_FAILURE); |
| src1.6.7/rdfw.cpp:3521 | HoldSmallObject | False | read_access | if (plate_id == static_cast<int>(a) && FactValue(StateField::PLATE) != static_cast<int>(a)) { |
| src1.6.7/rdfw.cpp:3523 | HoldSmallObject | False | read_access | SetPlate(nullptr, EvidenceSource::ACTION_FAILURE); |
| src1.6.7/rdfw.cpp:3525 | HoldSmallObject | False | read_access | if (hold_id != a) |
| src1.6.7/rdfw.cpp:3527 | HoldSmallObject | False | read_access | if (hold_id != NONE && !PutDown(hold_id)) return false; //如果拿着物体，先放下 |
| src1.6.7/rdfw.cpp:3528 | HoldSmallObject | False | read_access | if (plate_id == a) |
| src1.6.7/rdfw.cpp:3536 | HoldSmallObject | False | read_access | if (target_small->location != UNKNOWN) |
| src1.6.7/rdfw.cpp:3538 | HoldSmallObject | False | read_access | if (location != target_small->location) |
| src1.6.7/rdfw.cpp:3539 | HoldSmallObject | False | read_access | if(Move(target_small->location)!=1) |
| src1.6.7/rdfw.cpp:3547 | HoldSmallObject | False | read_access | if(target_small->location == UNKNOWN ){ |
| src1.6.7/rdfw.cpp:3555 | HoldSmallObject | False | read_access | if (target_small->inside == NONE\|\|target_small->inside == UNKNOWN) //这里我想了想，可能不会有UNKOWN的情况 |
| src1.6.7/rdfw.cpp:3558 | HoldSmallObject | False | read_access | if (target_small->location == location && PickUp(a)) return 1; |
| src1.6.7/rdfw.cpp:3561 | HoldSmallObject | False | read_access | if (!EnsureLocationCapacity(location)) return false; |
| src1.6.7/rdfw.cpp:3564 | HoldSmallObject | False | read_access | if ( posSensedFlag[location] |
| src1.6.7/rdfw.cpp:3565 | HoldSmallObject | False | read_access | && target_small->location == location |
| src1.6.7/rdfw.cpp:3566 | HoldSmallObject | False | read_access | && HasContainerAtLocation(location) |
| src1.6.7/rdfw.cpp:3568 | HoldSmallObject | False | read_access | unsigned int cont_id = GetContainerAtLocation(location); |
| src1.6.7/rdfw.cpp:3571 | HoldSmallObject | False | read_access | return (cont && cont->isOpen); |
| src1.6.7/rdfw.cpp:3576 | HoldSmallObject | False | read_access | if (TakeOut(a, GetContainerAtLocation(location))) return 1; |
| src1.6.7/rdfw.cpp:3580 | HoldSmallObject | False | read_access | if (plate_id == UNKNOWN && FromPlate(a)) return 1; |
| src1.6.7/rdfw.cpp:3581 | HoldSmallObject | False | read_access | ApplyStateValue(StateField::LOCATION,a,UNKNOWN,false,EvidenceSource::ACTION_FAILURE); |
| src1.6.7/rdfw.cpp:3594 | HoldSmallObject | False | read_access | int initial_cont_id=target_small->inside; |
| src1.6.7/rdfw.cpp:3597 | HoldSmallObject | False | read_access | ApplyStateValue(StateField::INSIDE,target_small->id,UNKNOWN,false,EvidenceSource::UNKNOWN); |
| src1.6.7/rdfw.cpp:3600 | HoldSmallObject | False | read_access | TakeOutResult result = TakeOutLogic(a,target_small->inside); |
| src1.6.7/rdfw.cpp:3606 | HoldSmallObject | False | read_access | else if(result == TakeOutResult::NeedContainerLocation) {if (t >= 2)  return 0;GetBigObjectStatus(target_small->inside);} |
| src1.6.7/rdfw.cpp:3650 | TakeOutLogic | False | read_access | const bool absent = HasObjectAtLocation(location, cont) && |
| src1.6.7/rdfw.cpp:3651 | TakeOutLogic | False | read_access | !HasObjectAtLocation(location, small); |
| src1.6.7/rdfw.cpp:3654 | TakeOutLogic | False | read_access | if (small_object && small_object->inside == static_cast<int>(cont)) { |
| src1.6.7/rdfw.cpp:3655 | TakeOutLogic | False | read_access | ApplyStateValue(StateField::INSIDE,small,UNKNOWN,false,EvidenceSource::SENSE); |
| src1.6.7/rdfw.cpp:3661 | TakeOutLogic | False | read_access | if(target_cont->location==UNKNOWN)return TakeOutResult::NeedContainerLocation; |
| src1.6.7/rdfw.cpp:3663 | TakeOutLogic | False | read_access | if(!target_cont->isOpen) |
| src1.6.7/rdfw.cpp:3675 | TakeOutLogic | False | read_access | ApplyStateValue(StateField::CONTAINER_STATE,cont,true,true,EvidenceSource::ACTION_FAILURE); |
| src1.6.7/rdfw.cpp:3728 | SolveTask_PutDown | False | read_access | if(hold_id==a){ |
| src1.6.7/rdfw.cpp:3729 | SolveTask_PutDown | False | read_access | if (location < 0 \|\| !EnsureLocationCapacity(location)) return false; |
| src1.6.7/rdfw.cpp:3730 | SolveTask_PutDown | False | read_access | if(putdown_cons[a][location]) { |
| src1.6.7/rdfw.cpp:3736 | SolveTask_PutDown | False | read_access | else if(plate_id==a){ |
| src1.6.7/rdfw.cpp:3737 | SolveTask_PutDown | False | read_access | if (location < 0 \|\| !EnsureLocationCapacity(location)) return false; |
| src1.6.7/rdfw.cpp:3738 | SolveTask_PutDown | False | read_access | if(hold_id>0) { |
| src1.6.7/rdfw.cpp:3739 | SolveTask_PutDown | False | read_access | if (!PutDown(hold_id)) return false; |
| src1.6.7/rdfw.cpp:3740 | SolveTask_PutDown | False | read_access | if(putdown_cons[a][location]) { |
| src1.6.7/rdfw.cpp:3746 | SolveTask_PutDown | False | read_access | if(putdown_cons[a][location]) { |
| src1.6.7/rdfw.cpp:3759 | SolveTask_PutDown | False | read_access | if (location < 0) return false; |
| src1.6.7/rdfw.cpp:3760 | SolveTask_PutDown | False | read_access | if (!EnsureLocationCapacity(location)) return false; |
| src1.6.7/rdfw.cpp:3761 | SolveTask_PutDown | False | read_access | if (putdown_cons[a][location]) { |
| src1.6.7/rdfw.cpp:3778 | SolveTask_Goto | False | read_access | else return Move(objects[a]->location); |
| src1.6.7/rdfw.cpp:3784 | SolveTask_Goto | False | read_access | if(objects[a]->location==UNKNOWN) |
| src1.6.7/rdfw.cpp:3801 | SolveTask_Goto | False | read_access | if(location==objects[a]->location) { |
| src1.6.7/rdfw.cpp:3803 | SolveTask_Goto | False | read_access | if (HasObjectAtLocation(location, a)) return true; |
| src1.6.7/rdfw.cpp:3806 | SolveTask_Goto | False | read_access | HasObjectAtLocation(location, FactInside(a))) { |
| src1.6.7/rdfw.cpp:3807 | SolveTask_Goto | False | read_access | ApplyStateValue(StateField::LOCATION,a,location,true,EvidenceSource::RELATION_DERIVED); |
| src1.6.7/rdfw.cpp:3814 | SolveTask_Goto | False | read_access | else if(!Move(objects[a]->location)) |
| src1.6.7/rdfw.cpp:3822 | SolveTask_Goto | False | read_access | if (HasObjectAtLocation(location, a)) return true; |
| src1.6.7/rdfw.cpp:3825 | SolveTask_Goto | False | read_access | HasObjectAtLocation(location, FactInside(a))) { |
| src1.6.7/rdfw.cpp:3826 | SolveTask_Goto | False | read_access | ApplyStateValue(StateField::LOCATION,a,location,true,EvidenceSource::RELATION_DERIVED); |
| src1.6.7/rdfw.cpp:3852 | SolveTask_Open | False | read_access | if(hold_id!=NONE && !PutDown(hold_id)) return false; |
| src1.6.7/rdfw.cpp:3855 | SolveTask_Open | False | read_access | if (location != objects[a]->location && !Move(objects[a]->location)) return false; |
| src1.6.7/rdfw.cpp:3860 | SolveTask_Open | False | read_access | if(objects[a]->location==UNKNOWN) |
| src1.6.7/rdfw.cpp:3869 | SolveTask_Open | False | read_access | if (location != objects[a]->location) |
| src1.6.7/rdfw.cpp:3870 | SolveTask_Open | False | read_access | if(!Move(objects[a]->location)) |
| src1.6.7/rdfw.cpp:3879 | SolveTask_Open | False | read_access | ApplyStateValue(StateField::CONTAINER_STATE,a,true,true,EvidenceSource::ACTION_FAILURE); |
| src1.6.7/rdfw.cpp:3880 | SolveTask_Open | False | read_access | MarkDirectLocationEvidence(a, true, EvidenceSource::SENSE); |
| src1.6.7/rdfw.cpp:3907 | SolveTask_Close | False | read_access | if(hold_id!=NONE && !PutDown(hold_id)) return false; |
| src1.6.7/rdfw.cpp:3910 | SolveTask_Close | False | read_access | if (location != objects[a]->location && !Move(objects[a]->location)) return false; |
| src1.6.7/rdfw.cpp:3916 | SolveTask_Close | False | read_access | if(objects[a]->location==UNKNOWN) |
| src1.6.7/rdfw.cpp:3925 | SolveTask_Close | False | read_access | if (location != objects[a]->location) |
| src1.6.7/rdfw.cpp:3926 | SolveTask_Close | False | read_access | if(!Move(objects[a]->location)) |
| src1.6.7/rdfw.cpp:3935 | SolveTask_Close | False | read_access | ApplyStateValue(StateField::CONTAINER_STATE,a,false,true,EvidenceSource::ACTION_FAILURE); |
| src1.6.7/rdfw.cpp:3936 | SolveTask_Close | False | read_access | MarkDirectLocationEvidence(a, true, EvidenceSource::SENSE); |
| src1.6.7/rdfw.cpp:3954 | SolveTask_Give | False | read_access | if(human->location==UNKNOWN) |
| src1.6.7/rdfw.cpp:3990 | SolveTask_Putin | False | read_access | if(objects[a]->location==objects[b]->location) |
| src1.6.7/rdfw.cpp:3992 | SolveTask_Putin | False | read_access | if (location != target_cont->location && !Move(target_cont->location)) return false; |
| src1.6.7/rdfw.cpp:3993 | SolveTask_Putin | False | read_access | if (target_cont->isOpen != 1 && !Open(b)) return false; |
| src1.6.7/rdfw.cpp:4000 | SolveTask_Putin | False | read_access | if (location != target_cont->location && !Move(target_cont->location)) return false; |
| src1.6.7/rdfw.cpp:4001 | SolveTask_Putin | False | read_access | if (target_cont->isOpen != 1) |
| src1.6.7/rdfw.cpp:4014 | SolveTask_Putin | False | read_access | if(objects[b]->location==UNKNOWN) |
| src1.6.7/rdfw.cpp:4025 | SolveTask_Putin | False | read_access | if (location != target_cont->location) |
| src1.6.7/rdfw.cpp:4026 | SolveTask_Putin | False | read_access | if(!Move(target_cont->location)) |
| src1.6.7/rdfw.cpp:4034 | SolveTask_Putin | False | read_access | if (!target_cont->isOpen) |
| src1.6.7/rdfw.cpp:4045 | SolveTask_Putin | False | read_access | ApplyStateValue(StateField::CONTAINER_STATE,b,true,true,EvidenceSource::ACTION_FAILURE); |
| src1.6.7/rdfw.cpp:4079 | SolveTask_Putin | False | declaration | //     PutDown(hold_id); |
| src1.6.7/rdfw.cpp:4116 | SolveTask_TakeOut | False | declaration | // Stage 2 location facts and AskLoc replies may be misleading. A known |
| src1.6.7/rdfw.cpp:4128 | SolveTask_TakeOut | False | read_access | if (hold!= nullptr && !PutDown(hold->id)) return false; |
| src1.6.7/rdfw.cpp:4129 | SolveTask_TakeOut | False | read_access | if (location != target_cont->location && !Move(target_cont->location)) return false; |
| src1.6.7/rdfw.cpp:4130 | SolveTask_TakeOut | False | read_access | if (target_cont->isOpen != 1 && !Open(target_cont->id)) return false; |
| src1.6.7/rdfw.cpp:4134 | SolveTask_TakeOut | False | read_access | if(target_cont->location==UNKNOWN){GetBigObjectStatus(b);if(!IsKeepingGoing(task_index)) return false;} |
| src1.6.7/rdfw.cpp:4135 | SolveTask_TakeOut | False | read_access | if (hold!= nullptr && !PutDown(hold->id)) return false; |
| src1.6.7/rdfw.cpp:4140 | SolveTask_TakeOut | False | read_access | if (location != target_cont->location) |
| src1.6.7/rdfw.cpp:4141 | SolveTask_TakeOut | False | read_access | if(!Move(target_cont->location)) |
| src1.6.7/rdfw.cpp:4167 | SolveTask_TakeOut | False | read_access | return TaskFactSatisfied("takeout",a,b); // 未验证的非 inside 不是完成事实 |
| src1.6.7/rdfw.cpp:4186 | SolveTask_PutOn | False | read_access | if(objects[b]->location==UNKNOWN) |
| src1.6.7/rdfw.cpp:4196 | SolveTask_PutOn | False | read_access | if (location != objects[b]->location) |
| src1.6.7/rdfw.cpp:4198 | SolveTask_PutOn | False | read_access | if(!Move(objects[b]->location)) |
| src1.6.7/rdfw.cpp:4208 | SolveTask_PutOn | False | read_access | if(!HasObjectAtLocation(location, b)) { |
| src1.6.7/rdfw.cpp:4414 | remove_if | False | read_access | int loc = (objects[id] ? objects[id]->location : UNKNOWN); |
| src1.6.7/rdfw.cpp:4452 | ExecuteMultiGotoAggregation | False | read_access | int loc = (objects[id] ? objects[id]->location : UNKNOWN); |
| src1.6.7/rdfw.cpp:4481 | ExecuteMultiGotoAggregation | False | read_access | int loc = (objects[id] ? objects[id]->location : UNKNOWN); |
| src1.6.7/rdfw.cpp:4517 | ExecuteMultiGotoAggregation | False | read_access | int loc = objects[id]->location; |
| src1.6.7/rdfw.cpp:4525 | ExecuteMultiGotoAggregation | False | read_access | int loc = objects[id]->location; |
| src1.6.7/rdfw.cpp:4533 | ExecuteMultiGotoAggregation | False | read_access | int loc = objects[id]->location; |
| src1.6.7/rdfw.cpp:4597 | ExecuteMultiGotoAggregation | False | read_access | int loc = objects[id]->location; |
| src1.6.7/rdfw.cpp:4620 | ExecuteMultiGotoAggregation | False | read_access | cout << "[MultiGoto] location " << loc << " has " << count << " small objects" << endl; |
| src1.6.7/rdfw.cpp:4656 | ExecuteMultiGotoAggregation | False | read_access | int loc = objects[big_id]->location; |
| src1.6.7/rdfw.cpp:4688 | ExecuteMultiGotoAggregation | False | read_access | LOG(YELLOW "[MultiGoto] No optimal location found, using first available: %d\n" RESET, chosen_loc); |
| src1.6.7/rdfw.cpp:4696 | ExecuteMultiGotoAggregation | False | read_access | LOG(YELLOW "[MultiGoto] No optimal location found, using first available: %d\n" RESET, loc); |
| src1.6.7/rdfw.cpp:4705 | ExecuteMultiGotoAggregation | False | read_access | LOG(RED "[MultiGoto] ERROR: No valid location found! chosen_loc=%d, rightlocation[%d]=%d\n" RESET, |
| src1.6.7/rdfw.cpp:4708 | ExecuteMultiGotoAggregation | False | read_access | chosen_loc = location; |
| src1.6.7/rdfw.cpp:4709 | ExecuteMultiGotoAggregation | False | read_access | LOG(YELLOW "[MultiGoto] Using current location as fallback: %d\n" RESET, chosen_loc); |
| src1.6.7/rdfw.cpp:4714 | ExecuteMultiGotoAggregation | False | declaration | // chosen_loc is a location, while SolveTask_PutOn expects an object id |
| src1.6.7/rdfw.cpp:4715 | ExecuteMultiGotoAggregation | False | declaration | // whose location is the destination.  Keep the legacy hub selection |
| src1.6.7/rdfw.cpp:4716 | ExecuteMultiGotoAggregation | False | declaration | // unchanged and map that location to a stable representative object. |
| src1.6.7/rdfw.cpp:4719 | ExecuteMultiGotoAggregation | False | read_access | if (!objects[i] \|\| objects[i]->location != chosen_loc) continue; |
| src1.6.7/rdfw.cpp:4729 | ExecuteMultiGotoAggregation | False | read_access | LOG(GREEN "[MultiGoto] hub location=%d representative_object=%u\n" RESET, |
| src1.6.7/rdfw.cpp:4741 | ExecuteMultiGotoAggregation | False | read_access | int loc = objects[id]->location; |
| src1.6.7/rdfw.cpp:4759 | ExecuteMultiGotoAggregation | False | read_access | if (location != chosen_loc) { |
| src1.6.7/rdfw.cpp:4773 | ExecuteMultiGotoAggregation | False | declaration | // 护栏：hold/plate 不在集合且跨区会触发 move 约束时，先就地处理 |
| src1.6.7/rdfw.cpp:4774 | ExecuteMultiGotoAggregation | False | read_access | if (IsValidObjectId(hold_id) && !in_set(hold_id) && |
| src1.6.7/rdfw.cpp:4775 | ExecuteMultiGotoAggregation | False | read_access | chosen_loc >= 0 && hold_id < static_cast<int>(move_cons.size()) && |
| src1.6.7/rdfw.cpp:4776 | ExecuteMultiGotoAggregation | False | read_access | static_cast<std::size_t>(chosen_loc) < move_cons[hold_id].size() && |
| src1.6.7/rdfw.cpp:4777 | ExecuteMultiGotoAggregation | False | read_access | move_cons[hold_id][chosen_loc]) { |
| src1.6.7/rdfw.cpp:4778 | ExecuteMultiGotoAggregation | False | read_access | PutDown(hold_id); |
| src1.6.7/rdfw.cpp:4780 | ExecuteMultiGotoAggregation | False | read_access | if (IsValidObjectId(plate_id) && !in_set(plate_id) && |
| src1.6.7/rdfw.cpp:4781 | ExecuteMultiGotoAggregation | False | read_access | chosen_loc >= 0 && plate_id < static_cast<int>(move_cons.size()) && |
| src1.6.7/rdfw.cpp:4782 | ExecuteMultiGotoAggregation | False | read_access | static_cast<std::size_t>(chosen_loc) < move_cons[plate_id].size() && |
| src1.6.7/rdfw.cpp:4783 | ExecuteMultiGotoAggregation | False | read_access | move_cons[plate_id][chosen_loc]) { |
| src1.6.7/rdfw.cpp:4784 | ExecuteMultiGotoAggregation | False | read_access | if (hold_id > 0) PutDown(hold_id); |
| src1.6.7/rdfw.cpp:4785 | ExecuteMultiGotoAggregation | False | read_access | FromPlate(plate_id); |
| src1.6.7/rdfw.cpp:4786 | ExecuteMultiGotoAggregation | False | read_access | PutDown(plate_id); |
| src1.6.7/rdfw.cpp:4789 | ExecuteMultiGotoAggregation | False | declaration | // 若 hold/plate 在集合里，优先处理 |
| src1.6.7/rdfw.cpp:4794 | ExecuteMultiGotoAggregation | False | read_access | if (hold_id  > 0) promote_front(hold_id); |
| src1.6.7/rdfw.cpp:4795 | ExecuteMultiGotoAggregation | False | read_access | if (plate_id > 0) promote_front(plate_id); |
| src1.6.7/rdfw.cpp:4801 | stable_sort | False | read_access | int da = (sa && sa->location == chosen_loc) ? 0 : 1; |
| src1.6.7/rdfw.cpp:4802 | stable_sort | False | read_access | int db = (sb && sb->location == chosen_loc) ? 0 : 1; |
| src1.6.7/rdfw.cpp:4841 | ExecuteMultiGotoAggregation | False | read_access | if (location != chosen_loc) { |
| src1.6.7/rdfw.cpp:4903 | ParseAskLocationReply | False | read_access | "^\\s*(at\|inside)\\s*\\(\\s*([0-9]+)\\s*,\\s*([0-9]+)\\s*\\)\\s*$"); |
| src1.6.7/rdfw.cpp:4913 | ParseAskLocationReply | False | read_access | if (relation == "inside" && reply_target > static_cast<int>(MAX_OBJECT_ID)) |
| src1.6.7/rdfw.cpp:4939 | GetSmallObjectStatus | False | mutation_consumer | if (relation == "inside") { |
| src1.6.7/rdfw.cpp:4942 | GetSmallObjectStatus | False | mutation_consumer | } else if (target < posSensedFlag.size() && posSensedFlag[target] && |
| src1.6.7/rdfw.cpp:4956 | GetSmallObjectStatus | False | mutation_consumer | if (IsInsideVerified(a)) { |
| src1.6.7/rdfw.cpp:4957 | GetSmallObjectStatus | False | mutation_consumer | const int answer_inside = chosen_relation == "inside" |
| src1.6.7/rdfw.cpp:4960 | GetSmallObjectStatus | False | mutation_consumer | LOG(YELLOW "AskLoc(%u) conflicts with trusted inside fact; ignored\n" RESET, a); |
| src1.6.7/rdfw.cpp:4964 | GetSmallObjectStatus | False | mutation_consumer | if (IsLocationVerified(a)) { |
| src1.6.7/rdfw.cpp:4965 | GetSmallObjectStatus | False | mutation_consumer | const int answer_location = chosen_relation == "inside" |
| src1.6.7/rdfw.cpp:4966 | GetSmallObjectStatus | False | mutation_consumer | ? objects[chosen_target]->location : static_cast<int>(chosen_target); |
| src1.6.7/rdfw.cpp:4968 | GetSmallObjectStatus | False | mutation_consumer | LOG(YELLOW "AskLoc(%u) conflicts with trusted location; ignored\n" RESET, a); |
| src1.6.7/rdfw.cpp:4972 | GetSmallObjectStatus | False | mutation_consumer | if (IsInsideVerified(a) && IsLocationVerified(a)) return true; |
| src1.6.7/rdfw.cpp:4974 | GetSmallObjectStatus | False | mutation_consumer | const int answer_inside = chosen_relation == "inside" |
| src1.6.7/rdfw.cpp:4976 | GetSmallObjectStatus | False | mutation_consumer | const int answer_location = chosen_relation == "inside" |
| src1.6.7/rdfw.cpp:4977 | GetSmallObjectStatus | False | mutation_consumer | ? objects[chosen_target]->location : static_cast<int>(chosen_target); |
| src1.6.7/rdfw.cpp:4978 | GetSmallObjectStatus | False | mutation_consumer | const bool inside_conflict = !IsInsideVerified(a) && |
| src1.6.7/rdfw.cpp:4980 | GetSmallObjectStatus | False | mutation_consumer | EvidenceSource::ASK_ANSWER); |
| src1.6.7/rdfw.cpp:4981 | GetSmallObjectStatus | False | mutation_consumer | const bool location_conflict = !IsLocationVerified(a) && |
| src1.6.7/rdfw.cpp:4984 | GetSmallObjectStatus | False | mutation_consumer | EvidenceSource::ASK_ANSWER); |
| src1.6.7/rdfw.cpp:4986 | GetSmallObjectStatus | False | mutation_consumer | if (small->inside > 0 && static_cast<size_t>(small->inside) < objects.size()) { |
| src1.6.7/rdfw.cpp:4987 | GetSmallObjectStatus | False | mutation_consumer | auto old_cont = dynamic_pointer_cast<Container>(objects[small->inside]); |
| src1.6.7/rdfw.cpp:4991 | GetSmallObjectStatus | False | mutation_consumer | if (chosen_relation == "inside") { |
| src1.6.7/rdfw.cpp:4994 | GetSmallObjectStatus | False | mutation_consumer | if (cont->location == UNKNOWN) GetBigObjectStatus(cont->id); |
| src1.6.7/rdfw.cpp:4995 | GetSmallObjectStatus | False | mutation_consumer | StageStateValue(StateField::LOCATION,small->id,cont->location); |
| src1.6.7/rdfw.cpp:4998 | GetSmallObjectStatus | False | mutation_consumer | for (const auto& item : cont->smallObjectsInside) { |
| src1.6.7/rdfw.cpp:5008 | GetSmallObjectStatus | False | mutation_consumer | if (!IsLocationVerified(a)) |
| src1.6.7/rdfw.cpp:5009 | GetSmallObjectStatus | False | mutation_consumer | MarkDirectLocationEvidence(a, false, EvidenceSource::ASK_ANSWER); |
| src1.6.7/rdfw.cpp:5010 | GetSmallObjectStatus | False | mutation_consumer | if (!IsInsideVerified(a)) |
| src1.6.7/rdfw.cpp:5011 | GetSmallObjectStatus | False | mutation_consumer | SetInsideEvidence(a, false, EvidenceSource::ASK_ANSWER); |
| src1.6.7/rdfw.cpp:5014 | GetSmallObjectStatus | False | mutation_consumer | if (small->location >= 0) { |
| src1.6.7/rdfw.cpp:5015 | GetSmallObjectStatus | False | mutation_consumer | if (!EnsureLocationCapacity(small->location)) return false; |
| src1.6.7/rdfw.cpp:5016 | GetSmallObjectStatus | False | mutation_consumer | posCorrectFlag[small->location] = false; |
| src1.6.7/rdfw.cpp:5037 | GetBigObjectStatus | False | mutation_consumer | if (target < posSensedFlag.size() && posSensedFlag[target] && |
| src1.6.7/rdfw.cpp:5044 | GetBigObjectStatus | False | mutation_consumer | LOG(YELLOW "AskLoc(%u) produced no usable bounded location reply\n" RESET, a); |
| src1.6.7/rdfw.cpp:5047 | GetBigObjectStatus | False | mutation_consumer | if (IsLocationVerified(a)) { |
| src1.6.7/rdfw.cpp:5049 | GetBigObjectStatus | False | mutation_consumer | LOG(YELLOW "AskLoc(%u) conflicts with trusted location; ignored\n" RESET, a); |
| src1.6.7/rdfw.cpp:5057 | GetBigObjectStatus | False | mutation_consumer | static_cast<int>(chosen_location), EvidenceSource::ASK_ANSWER); |
| src1.6.7/rdfw.cpp:5060 | GetBigObjectStatus | False | mutation_consumer | for (const auto& item : cont->smallObjectsInside) { |
| src1.6.7/rdfw.cpp:5063 | GetBigObjectStatus | False | declaration | // observation or successful action on an individual item. |
| src1.6.7/rdfw.cpp:5064 | GetBigObjectStatus | False | mutation_consumer | if (IsLocationVerified(item->id)) continue; |
| src1.6.7/rdfw.cpp:5065 | GetBigObjectStatus | False | mutation_consumer | ApplyStateValue(StateField::LOCATION,item->id,cont->location,false,EvidenceSource::ASK_ANSWER); |
| src1.6.7/rdfw.cpp:5069 | GetBigObjectStatus | False | mutation_consumer | MarkDirectLocationEvidence(a, false, EvidenceSource::ASK_ANSWER); |
| src1.6.7/rdfw.cpp:5087 | AskLoc | False | read_access | if (small && small->inside > 0) |
| src1.6.7/rdfw.cpp:5088 | AskLoc | False | read_access | str = "inside(" + std::to_string(a) + "," + |
| src1.6.7/rdfw.cpp:5089 | AskLoc | False | read_access | std::to_string(small->inside) + ")"; |
| src1.6.7/rdfw.cpp:5090 | AskLoc | False | read_access | else if (objects[a]->location >= 0) |
| src1.6.7/rdfw.cpp:5092 | AskLoc | False | read_access | std::to_string(objects[a]->location) + ")"; |
| src1.6.7/rdfw.cpp:5109 | Sense | False | declaration | // Sense 只观察当前位置，不应把 location 当作对象 ID，也不应隐式开关门。 |
| src1.6.7/rdfw.cpp:5120 | SenseCurrentLocationOnly | False | canonical_mutation | int curr_loc = location; |
| src1.6.7/rdfw.cpp:5124 | SenseCurrentLocationOnly | False | canonical_mutation | if (curr_loc >= posSensedFlag.size()) { |
| src1.6.7/rdfw.cpp:5125 | SenseCurrentLocationOnly | True | canonical_mutation | posSensedFlag.resize(curr_loc + 1, false); |
| src1.6.7/rdfw.cpp:5126 | SenseCurrentLocationOnly | True | canonical_mutation | locationSensedObjects.resize(curr_loc + 1);  // 同时扩展物体记录数组 |
| src1.6.7/rdfw.cpp:5129 | SenseCurrentLocationOnly | False | canonical_mutation | if (!force && posSensedFlag[curr_loc]) { |
| src1.6.7/rdfw.cpp:5142 | SenseCurrentLocationOnly | False | canonical_mutation | if (curr_loc >= posSensedFlag.size()) { |
| src1.6.7/rdfw.cpp:5143 | SenseCurrentLocationOnly | True | canonical_mutation | posSensedFlag.resize(curr_loc + 1, false); |
| src1.6.7/rdfw.cpp:5144 | SenseCurrentLocationOnly | True | canonical_mutation | locationSensedObjects.resize(curr_loc + 1);  // 同时扩展物体记录数组 |
| src1.6.7/rdfw.cpp:5147 | SenseCurrentLocationOnly | True | canonical_mutation | posSensedFlag[curr_loc] = true; |
| src1.6.7/rdfw.cpp:5150 | SenseCurrentLocationOnly | False | canonical_mutation | locationSensedObjects[curr_loc].object_ids.clear(); |
| src1.6.7/rdfw.cpp:5151 | SenseCurrentLocationOnly | False | canonical_mutation | locationSensedObjects[curr_loc].container_id = 0; |
| src1.6.7/rdfw.cpp:5152 | SenseCurrentLocationOnly | False | canonical_mutation | locationSensedObjects[curr_loc].has_container = false; |
| src1.6.7/rdfw.cpp:5159 | SenseCurrentLocationOnly | False | canonical_mutation | if (objects[id]->location != curr_loc) |
| src1.6.7/rdfw.cpp:5160 | SenseCurrentLocationOnly | False | canonical_mutation | InvalidateSenseAtLocation(objects[id]->location); |
| src1.6.7/rdfw.cpp:5161 | SenseCurrentLocationOnly | False | canonical_mutation | ApplyStateValue(StateField::LOCATION,id,curr_loc,true,EvidenceSource::SENSE); |
| src1.6.7/rdfw.cpp:5165 | SenseCurrentLocationOnly | False | canonical_mutation | locationSensedObjects[curr_loc].object_ids.push_back(id); |
| src1.6.7/rdfw.cpp:5170 | SenseCurrentLocationOnly | False | canonical_mutation | locationSensedObjects[curr_loc].container_id = id; |
| src1.6.7/rdfw.cpp:5171 | SenseCurrentLocationOnly | False | canonical_mutation | locationSensedObjects[curr_loc].has_container = true; |
| src1.6.7/rdfw.cpp:5173 | SenseCurrentLocationOnly | False | canonical_mutation | LOG("[SenseCurrentLocationOnly] Container %d detected at location %d", id, curr_loc); |
| src1.6.7/rdfw.cpp:5175 | SenseCurrentLocationOnly | False | canonical_mutation | LOG("[SenseCurrentLocationOnly] Object %d detected at location %d", id, curr_loc); |
| src1.6.7/rdfw.cpp:5180 | SenseCurrentLocationOnly | False | declaration | // 让位置证据与 inside 关系保持一致。开放容器与其内容同时可见时， |
| src1.6.7/rdfw.cpp:5186 | SenseCurrentLocationOnly | False | canonical_mutation | if (!small \|\| static_cast<int>(id) == hold_id \|\| static_cast<int>(id) == plate_id) continue; |
| src1.6.7/rdfw.cpp:5198 | SenseCurrentLocationOnly | False | canonical_mutation | small->inside == static_cast<int>(sensed_container_id) && visible_container_is_open; |
| src1.6.7/rdfw.cpp:5200 | SenseCurrentLocationOnly | False | canonical_mutation | SetInsideEvidence(id, false, EvidenceSource::SENSE); |
| src1.6.7/rdfw.cpp:5204 | SenseCurrentLocationOnly | False | canonical_mutation | if (small->inside > 0 && static_cast<size_t>(small->inside) < objects.size()) { |
| src1.6.7/rdfw.cpp:5205 | SenseCurrentLocationOnly | False | canonical_mutation | auto old_container = dynamic_pointer_cast<Container>(objects[small->inside]); |
| src1.6.7/rdfw.cpp:5208 | SenseCurrentLocationOnly | False | canonical_mutation | ApplyStateValue(StateField::INSIDE,id,NONE,true,EvidenceSource::SENSE); |
| src1.6.7/rdfw.cpp:5214 | SenseCurrentLocationOnly | False | canonical_mutation | for (auto id2 : locationSensedObjects[curr_loc].object_ids) { |
| src1.6.7/rdfw.cpp:5233 | SenseCurrentLocationOnly | False | canonical_mutation | if (static_cast<int>(i) == hold_id \|\| static_cast<int>(i) == plate_id) continue; |
| src1.6.7/rdfw.cpp:5234 | SenseCurrentLocationOnly | False | canonical_mutation | if (objects[i]->location == curr_loc) { |
| src1.6.7/rdfw.cpp:5242 | SenseCurrentLocationOnly | False | canonical_mutation | ApplyStateValue(StateField::LOCATION,id,UNKNOWN,false,EvidenceSource::SENSE); |
| src1.6.7/rdfw.cpp:5244 | SenseCurrentLocationOnly | False | canonical_mutation | LOG(YELLOW "[SenseCurrentLocationOnly] Object id=%u expected at %d but not sensed, set location UNKNOWN\n" RESET, id, curr_loc); |
| src1.6.7/rdfw.cpp:5253 | SenseCurrentLocationOnly | False | canonical_mutation | if (small && small->inside == sensed_container_id) { |
| src1.6.7/rdfw.cpp:5258 | SenseCurrentLocationOnly | False | canonical_mutation | ApplyStateValue(StateField::LOCATION,id,UNKNOWN,false,EvidenceSource::SENSE); |
| src1.6.7/rdfw.cpp:5260 | SenseCurrentLocationOnly | False | canonical_mutation | LOG(YELLOW "[SenseCurrentLocationOnly] Object id=%u expected at %d but not sensed, set location UNKNOWN\n" RESET, id, curr_loc); |
| src1.6.7/rdfw.cpp:5268 | GetLocationSensedInfo | False | read_access | const RDFW::LocationSensedInfo& RDFW::GetLocationSensedInfo(int location) const { |
| src1.6.7/rdfw.cpp:5270 | GetLocationSensedInfo | False | read_access | if (location >= 0 && location < locationSensedObjects.size()) { |
| src1.6.7/rdfw.cpp:5271 | GetLocationSensedInfo | False | read_access | return locationSensedObjects[location]; |
| src1.6.7/rdfw.cpp:5276 | HasObjectAtLocation | False | read_access | bool RDFW::HasObjectAtLocation(int location, unsigned int object_id) const { |
| src1.6.7/rdfw.cpp:5277 | HasObjectAtLocation | False | read_access | if (location >= 0 && location < locationSensedObjects.size()) { |
| src1.6.7/rdfw.cpp:5278 | HasObjectAtLocation | False | read_access | const auto& info = locationSensedObjects[location]; |
| src1.6.7/rdfw.cpp:5286 | HasContainerAtLocation | False | read_access | bool RDFW::HasContainerAtLocation(int location) const { |
| src1.6.7/rdfw.cpp:5287 | HasContainerAtLocation | False | read_access | if (location >= 0 && location < locationSensedObjects.size()) { |
| src1.6.7/rdfw.cpp:5288 | HasContainerAtLocation | False | read_access | return locationSensedObjects[location].has_container; |
| src1.6.7/rdfw.cpp:5293 | GetObjectsAtLocation | False | read_access | vector<unsigned int> RDFW::GetObjectsAtLocation(int location) const { |
| src1.6.7/rdfw.cpp:5294 | GetObjectsAtLocation | False | read_access | if (location >= 0 && location < locationSensedObjects.size()) { |
| src1.6.7/rdfw.cpp:5295 | GetObjectsAtLocation | False | read_access | return locationSensedObjects[location].object_ids; |
| src1.6.7/rdfw.cpp:5300 | GetContainerAtLocation | False | read_access | unsigned int RDFW::GetContainerAtLocation(int location) const { |
| src1.6.7/rdfw.cpp:5301 | GetContainerAtLocation | False | read_access | if (location >= 0 && location < locationSensedObjects.size()) { |
| src1.6.7/rdfw.cpp:5302 | GetContainerAtLocation | False | read_access | return locationSensedObjects[location].container_id; |
| src1.6.7/rdfw.cpp:5325 | sense | False | mutation_consumer | const bool moved = objects[id]->location != location; |
| src1.6.7/rdfw.cpp:5326 | sense | False | mutation_consumer | ApplyStateValue(StateField::LOCATION,id,location,true,EvidenceSource::SENSE); |
| src1.6.7/rdfw.cpp:5328 | sense | False | mutation_consumer | StageStateValue(StateField::LOCATION,id,location); |
| src1.6.7/rdfw.cpp:5330 | sense | False | mutation_consumer | for (auto &sp : cont->smallObjectsInside) { |
| src1.6.7/rdfw.cpp:5332 | sense | False | mutation_consumer | StageStateValue(StateField::LOCATION,sp->id,location); |
| src1.6.7/rdfw.cpp:5335 | sense | False | mutation_consumer | entailed ? EvidenceSource::CONSTRAINT_DERIVED |
| src1.6.7/rdfw.cpp:5336 | sense | False | mutation_consumer | : EvidenceSource::CONSTRAINT_HEURISTIC); |
| src1.6.7/rdfw.cpp:5342 | sense | False | declaration | // 小物体分支无需强制改 inside，这里保持原有逻辑不动 |
| src1.6.7/rdfw.cpp:5344 | sense | False | mutation_consumer | MarkDirectLocationEvidence(id, true, EvidenceSource::SENSE); |
| src1.6.7/rdfw.cpp:5345 | sense | False | mutation_consumer | if (objects[id]->unable_site == location) objects[id]->unable_site = UNKNOWN; |
| src1.6.7/rdfw.cpp:5376 | Isinside | False | read_access | if(small->inside==objects[b]->id) return true; |
| src1.6.7/rdfw.cpp:5396 | IsKeepingGoing | False | read_access | if(small->inside==t.Y[0]->id){ //如果任务没有满足 |
| src1.6.7/rdfw.cpp:5397 | IsKeepingGoing | False | read_access | const int target_location = t.Y[0]->location; |
| src1.6.7/rdfw.cpp:5408 | IsKeepingGoing | False | read_access | if(small->inside!=t.Y[0]->id) //如果任务没有满足 |
| src1.6.7/rdfw.cpp:5410 | IsKeepingGoing | False | read_access | const int target_location = t.Y[0]->location; |
| src1.6.7/rdfw.cpp:5415 | IsKeepingGoing | False | read_access | if(t.X[0]->location!=target_location) t.risk+=goto_cons[target_location]; |
| src1.6.7/rdfw.cpp:5421 | IsKeepingGoing | False | read_access | const int target_location = t.Y[0]->location; |
| src1.6.7/rdfw.cpp:5426 | IsKeepingGoing | False | read_access | if(t.X[0]->location!=target_location) t.risk+=goto_cons[target_location]; |
| src1.6.7/rdfw.cpp:5430 | IsKeepingGoing | False | read_access | else if(t.behave=="goto" && t.X[0]->location >= 0 && |
| src1.6.7/rdfw.cpp:5431 | IsKeepingGoing | False | read_access | EnsureLocationCapacity(t.X[0]->location)) t.risk+=goto_cons[t.X[0]->location]; |
| src1.6.7/rdfw.cpp:5434 | IsKeepingGoing | False | read_access | if (t.X[0]->location >= 0 && EnsureLocationCapacity(t.X[0]->location)) |
| src1.6.7/rdfw.cpp:5435 | IsKeepingGoing | False | read_access | t.risk+=goto_cons[t.X[0]->location]; |
| src1.6.7/rdfw.cpp:5439 | IsKeepingGoing | False | read_access | if (t.X[0]->location >= 0 && EnsureLocationCapacity(t.X[0]->location)) |
| src1.6.7/rdfw.cpp:5440 | IsKeepingGoing | False | read_access | t.risk+=goto_cons[t.X[0]->location]; |
| src1.6.7/rdfw.cpp:5448 | IsKeepingGoing | False | read_access | if (human && human->location >= 0) { |
| src1.6.7/rdfw.cpp:5449 | IsKeepingGoing | False | read_access | if (!EnsureLocationCapacity(human->location)) return false; |
| src1.6.7/rdfw.cpp:5450 | IsKeepingGoing | False | read_access | t.risk+=move_cons[t.X[0]->id][human->location]; |
| src1.6.7/rdfw.cpp:5451 | IsKeepingGoing | False | read_access | if(t.X[0]->location!=human->location) t.risk+=goto_cons[human->location]; |
| src1.6.7/rdfw.cpp:5545 | ClearContainerMembership | False | canonical_mutation | auto& items = container->smallObjectsInside; |
| src1.6.7/rdfw.cpp:5557 | ReconcileLocationRelation | False | read_access | if (!small \|\| small->inside <= 0) return; |
| src1.6.7/rdfw.cpp:5558 | ReconcileLocationRelation | False | read_access | auto container = dynamic_pointer_cast<Container>(GetObject(small->inside)); |
| src1.6.7/rdfw.cpp:5559 | ReconcileLocationRelation | False | read_access | if (container && container->location != UNKNOWN && small->location != UNKNOWN && |
| src1.6.7/rdfw.cpp:5560 | ReconcileLocationRelation | False | read_access | container->location != small->location) { |
| src1.6.7/rdfw.cpp:5562 | ReconcileLocationRelation | False | read_access | ApplyStateValue(StateField::INSIDE,small->id,UNKNOWN,false,EvidenceSource::EXPLICIT_INFO); |
| src1.6.7/rdfw.cpp:5566 | declaration/inline | False | declaration | // A successful container action proves co-location even when the initial |
| src1.6.7/rdfw.cpp:5567 | declaration/inline | False | declaration | // location was misleading. Its contents inherit that location only with the |
| src1.6.7/rdfw.cpp:5568 | declaration/inline | False | declaration | // strength of their own inside evidence. |
| src1.6.7/rdfw.cpp:5571 | ConfirmContainerLocation | False | read_access | if (container->location != location) |
| src1.6.7/rdfw.cpp:5572 | ConfirmContainerLocation | False | read_access | InvalidateSenseAtLocation(container->location); |
| src1.6.7/rdfw.cpp:5573 | ConfirmContainerLocation | False | read_access | StageStateValue(StateField::LOCATION,container->id,location); |
| src1.6.7/rdfw.cpp:5575 | ConfirmContainerLocation | False | read_access | for (const auto& item : container->smallObjectsInside) { |
| src1.6.7/rdfw.cpp:5576 | ConfirmContainerLocation | False | read_access | if (!item \|\| item->inside != container->id) continue; |
| src1.6.7/rdfw.cpp:5578 | ConfirmContainerLocation | False | read_access | FactLocation(item->id) != location) continue; |
| src1.6.7/rdfw.cpp:5579 | ConfirmContainerLocation | False | read_access | StageStateValue(StateField::LOCATION,item->id,location); |
| src1.6.7/rdfw.cpp:5581 | ConfirmContainerLocation | False | declaration | // The action verifies the container, not an inside relation that was |
| src1.6.7/rdfw.cpp:5584 | ConfirmContainerLocation | False | read_access | const EvidenceSource source = |
| src1.6.7/rdfw.cpp:5585 | ConfirmContainerLocation | False | read_access | InsideSource(item->id) == EvidenceSource::CONSTRAINT_DERIVED |
| src1.6.7/rdfw.cpp:5586 | ConfirmContainerLocation | False | read_access | ? EvidenceSource::CONSTRAINT_DERIVED |
| src1.6.7/rdfw.cpp:5587 | ConfirmContainerLocation | False | read_access | : EvidenceSource::RELATION_DERIVED; |
| src1.6.7/rdfw.cpp:5615 | TakeOut | False | read_access | StageStateValue(StateField::LOCATION,small->id,location); |
| src1.6.7/rdfw.cpp:5623 | TakeOut | False | read_access | SetInsideEvidence(a, true, EvidenceSource::ACTION_SUCCESS); |
| src1.6.7/rdfw.cpp:5625 | TakeOut | False | read_access | SetContainerEvidence(b, true, EvidenceSource::ACTION_SUCCESS); |
| src1.6.7/rdfw.cpp:5626 | TakeOut | False | read_access | InvalidateSenseAtLocation(location); |
| src1.6.7/rdfw.cpp:5658 | PutIn | True | planning_cache | small->on = NONE; |
| src1.6.7/rdfw.cpp:5659 | PutIn | False | read_access | StageStateValue(StateField::LOCATION,small->id,location); |
| src1.6.7/rdfw.cpp:5662 | PutIn | False | read_access | for (const auto& item : cont->smallObjectsInside) { |
| src1.6.7/rdfw.cpp:5670 | PutIn | False | read_access | SetInsideEvidence(a, true, EvidenceSource::ACTION_SUCCESS); |
| src1.6.7/rdfw.cpp:5672 | PutIn | False | read_access | SetContainerEvidence(b, true, EvidenceSource::ACTION_SUCCESS); |
| src1.6.7/rdfw.cpp:5673 | PutIn | False | read_access | InvalidateSenseAtLocation(location); |
| src1.6.7/rdfw.cpp:5702 | Close | False | read_access | SetContainerEvidence(a, true, EvidenceSource::ACTION_SUCCESS); |
| src1.6.7/rdfw.cpp:5703 | Close | False | read_access | InvalidateSenseAtLocation(location); |
| src1.6.7/rdfw.cpp:5732 | Open | False | read_access | SetContainerEvidence(a, true, EvidenceSource::ACTION_SUCCESS); |
| src1.6.7/rdfw.cpp:5733 | Open | False | read_access | InvalidateSenseAtLocation(location); |
| src1.6.7/rdfw.cpp:5763 | FromPlate | False | read_access | SetInsideEvidence(a, true, EvidenceSource::ACTION_SUCCESS); |
| src1.6.7/rdfw.cpp:5764 | FromPlate | False | read_access | InvalidateSenseAtLocation(location); |
| src1.6.7/rdfw.cpp:5792 | ToPlate | False | read_access | SetInsideEvidence(a, true, EvidenceSource::ACTION_SUCCESS); |
| src1.6.7/rdfw.cpp:5793 | ToPlate | False | read_access | InvalidateSenseAtLocation(location); |
| src1.6.7/rdfw.cpp:5821 | PutDown | False | read_access | StageStateValue(StateField::LOCATION,small->id,location); |
| src1.6.7/rdfw.cpp:5823 | PutDown | True | planning_cache | small->on = NONE; |
| src1.6.7/rdfw.cpp:5826 | PutDown | False | read_access | SetInsideEvidence(a, true, EvidenceSource::ACTION_SUCCESS); |
| src1.6.7/rdfw.cpp:5827 | PutDown | False | read_access | InvalidateSenseAtLocation(location); |
| src1.6.7/rdfw.cpp:5830 | PutDown | False | read_access | if (location >= 0 && EnsureLocationCapacity(location)) |
| src1.6.7/rdfw.cpp:5831 | PutDown | False | read_access | putdown_cons[a][location]=0; |
| src1.6.7/rdfw.cpp:5857 | PickUp | False | read_access | StageStateValue(StateField::LOCATION,small->id,location); |
| src1.6.7/rdfw.cpp:5860 | PickUp | False | read_access | SetInsideEvidence(a, true, EvidenceSource::ACTION_SUCCESS); |
| src1.6.7/rdfw.cpp:5861 | PickUp | False | read_access | InvalidateSenseAtLocation(location); |
| src1.6.7/rdfw.cpp:5903 | Move | False | read_access | if (hold_id > 0 && hit_move_cons(hold_id, a)) { |
| src1.6.7/rdfw.cpp:5904 | Move | False | read_access | if (!has_taskX0 \|\| tasks[task_index].X[0]->id != hold_id) { |
| src1.6.7/rdfw.cpp:5905 | Move | False | read_access | PutDown(hold_id); |
| src1.6.7/rdfw.cpp:5908 | Move | False | read_access | if (plate_id > 0 && hit_move_cons(plate_id, a)) { |
| src1.6.7/rdfw.cpp:5909 | Move | False | read_access | if (hold_id > 0) PutDown(hold_id); |
| src1.6.7/rdfw.cpp:5910 | Move | False | read_access | FromPlate(plate_id); |
| src1.6.7/rdfw.cpp:5911 | Move | False | read_access | if (hold_id > 0) PutDown(hold_id); |
| src1.6.7/rdfw.cpp:5915 | Move | False | read_access | const int previous_location = location; |
| src1.6.7/rdfw.cpp:5931 | Move | False | read_access | ApplyStateValue(StateField::LOCATION,0,a,true,EvidenceSource::ACTION_SUCCESS); |
| src1.6.7/rdfw.cpp:5932 | Move | False | read_access | if (hold)  StageStateValue(StateField::LOCATION,hold->id,a); |
| src1.6.7/rdfw.cpp:5933 | Move | False | read_access | if (plate) StageStateValue(StateField::LOCATION,plate->id,a); |
| src1.6.7/rdfw.cpp:5936 | Move | False | read_access | if (hold_id > 0) { |
| src1.6.7/rdfw.cpp:5937 | Move | False | read_access | MarkDirectLocationEvidence(hold_id, FactValue(StateField::HOLD)==hold_id, |
| src1.6.7/rdfw.cpp:5938 | Move | False | read_access | EvidenceSource::RELATION_DERIVED); |
| src1.6.7/rdfw.cpp:5939 | Move | False | read_access | DependOn(StateField::LOCATION,hold_id,StateField::HOLD,0); |
| src1.6.7/rdfw.cpp:5940 | Move | False | read_access | DependOn(StateField::LOCATION,hold_id,StateField::LOCATION,0); |
| src1.6.7/rdfw.cpp:5942 | Move | False | read_access | if (plate_id > 0) { |
| src1.6.7/rdfw.cpp:5943 | Move | False | read_access | MarkDirectLocationEvidence(plate_id, FactValue(StateField::PLATE)==plate_id, |
| src1.6.7/rdfw.cpp:5944 | Move | False | read_access | EvidenceSource::RELATION_DERIVED); |
| src1.6.7/rdfw.cpp:5945 | Move | False | read_access | DependOn(StateField::LOCATION,plate_id,StateField::PLATE,0); |
| src1.6.7/rdfw.cpp:5946 | Move | False | read_access | DependOn(StateField::LOCATION,plate_id,StateField::LOCATION,0); |
| src1.6.7/rdfw.cpp:5961 | Move | False | read_access | if (hold_id > 0 && safe_idx(hold_id)) { |
| src1.6.7/rdfw.cpp:5962 | Move | False | read_access | move_cons[hold_id][a] = 0; |
| src1.6.7/rdfw.cpp:5963 | Move | False | read_access | objects[hold_id]->is_keep = 0; |
| src1.6.7/rdfw.cpp:5994 | PrintEnv | False | read_access | if (v->location == UNKNOWN) |
| src1.6.7/rdfw.cpp:5999 | PrintEnv | False | read_access | if (v->location < 0 \|\| v->location > MAX_LOCATION_ID) { |
| src1.6.7/rdfw.cpp:6003 | PrintEnv | False | read_access | if (static_cast<std::size_t>(v->location) >= objPos.size()) |
| src1.6.7/rdfw.cpp:6004 | PrintEnv | False | read_access | objPos.resize(v->location + 1); // expand objPos |
| src1.6.7/rdfw.cpp:6005 | PrintEnv | False | read_access | objPos[v->location].push_back(v); |
| src1.6.7/rdfw.cpp:6021 | PrintEnv | False | declaration | // print robot info (green) (hold, plate) |
| src1.6.7/rdfw.cpp:6023 | PrintEnv | False | read_access | cout << GREEN << "(" << v->sort << " hold:" << hold_id << " plate:" << plate_id << ")" << RESET; |
| src1.6.7/rdfw.cpp:6034 | PrintEnv | False | read_access | cout << " inside:["; |
| src1.6.7/rdfw.cpp:6035 | PrintEnv | False | read_access | for (int c = 0; c < p->smallObjectsInside.size(); c++) |
| src1.6.7/rdfw.cpp:6036 | PrintEnv | False | read_access | cout << (c == 0 ? "" : ",") << p->smallObjectsInside[c]->id; |
| src1.6.7/rdfw.cpp:6037 | PrintEnv | False | read_access | cout << "] " << (p->isOpen ? "Open" : "Closed"); |
| src1.6.7/rdfw.cpp:6295 | ValidateInstruction | False | read_access | else if (behave == "plate") |
| src1.6.7/rdfw.cpp:6297 | ValidateInstruction | False | read_access | else if (behave == "inside" \|\| behave == "in") |
| src1.6.7/rdfw.cpp:6299 | ValidateInstruction | False | read_access | else if (behave == "on") |
| src1.6.7/rdfw.cpp:6308 | ValidateInstruction | False | instruction_metadata | if (schema.give_form && !instruction.structuredSource && |
| src1.6.7/rdfw.cpp:6322 | ValidateInstruction | False | instruction_metadata | if (instruction.structuredSource) { |
| src1.6.7/rdfw.cpp:6413 | ValidateInstruction | False | declaration | // synchronous per-item success logging inside the real-time budget. |
| src1.6.7/rdfw.cpp:6566 | ParseEnvSentence | False | initialization | const bool unary = firstToken == "hold" \|\| firstToken == "plate" \|\| |
| src1.6.7/rdfw.cpp:6570 | ParseEnvSentence | False | initialization | firstToken == "inside" \|\| firstToken == "type"; |
| src1.6.7/rdfw.cpp:6585 | ParseEnvSentence | False | initialization | if (firstToken == "hold") |
| src1.6.7/rdfw.cpp:6588 | ParseEnvSentence | True | initialization | this->hold_id = index; |
| src1.6.7/rdfw.cpp:6591 | ParseEnvSentence | False | initialization | else if (firstToken == "plate") |
| src1.6.7/rdfw.cpp:6593 | ParseEnvSentence | True | initialization | this->plate_id = index; |
| src1.6.7/rdfw.cpp:6621 | ParseEnvSentence | False | initialization | ApplyStateValue(StateField::CONTAINER_STATE,index,(firstToken == "opened"),stage == 1,EvidenceSource::INITIAL); |
| src1.6.7/rdfw.cpp:6626 | ParseEnvSentence | False | initialization | LOG_ERROR("Env sentence has an invalid location: %s", sentence.c_str()); |
| src1.6.7/rdfw.cpp:6630 | ParseEnvSentence | False | initialization | location_id, EvidenceSource::INITIAL)) { |
| src1.6.7/rdfw.cpp:6631 | ParseEnvSentence | False | initialization | ApplyStateValue(StateField::LOCATION,index,UNKNOWN,false,EvidenceSource::UNKNOWN); |
| src1.6.7/rdfw.cpp:6632 | ParseEnvSentence | False | initialization | if (score_locations.size() <= static_cast<std::size_t>(index)) |
| src1.6.7/rdfw.cpp:6633 | ParseEnvSentence | True | initialization | score_locations.resize(index + 1, UNKNOWN); |
| src1.6.7/rdfw.cpp:6634 | ParseEnvSentence | True | initialization | score_locations[index] = UNKNOWN; |
| src1.6.7/rdfw.cpp:6637 | ParseEnvSentence | True | initialization | obj->location = location_id; |
| src1.6.7/rdfw.cpp:6638 | ParseEnvSentence | False | initialization | if (score_locations.size() <= static_cast<std::size_t>(index)) |
| src1.6.7/rdfw.cpp:6639 | ParseEnvSentence | True | initialization | score_locations.resize(index + 1, UNKNOWN); |
| src1.6.7/rdfw.cpp:6640 | ParseEnvSentence | True | initialization | score_locations[index] = location_id; |
| src1.6.7/rdfw.cpp:6641 | ParseEnvSentence | False | initialization | MarkDirectLocationEvidence(index, index == 0 \|\| stage == 1, EvidenceSource::INITIAL); |
| src1.6.7/rdfw.cpp:6661 | ParseEnvSentence | False | initialization | } else if (firstToken == "color" \|\| firstToken == "inside") { |
| src1.6.7/rdfw.cpp:6675 | ParseEnvSentence | False | initialization | LOG_ERROR("Env sentence has an invalid inside reference: %s", |
| src1.6.7/rdfw.cpp:6680 | ParseEnvSentence | False | initialization | container_id, EvidenceSource::INITIAL)) { |
| src1.6.7/rdfw.cpp:6681 | ParseEnvSentence | False | initialization | ApplyStateValue(StateField::INSIDE,index,UNKNOWN,false,EvidenceSource::UNKNOWN); |
| src1.6.7/rdfw.cpp:6684 | ParseEnvSentence | False | initialization | ApplyStateValue(StateField::INSIDE,index,container_id,stage == 1,EvidenceSource::INITIAL); |
| src1.6.7/rdfw.cpp:6733 | ParseEnv | False | declaration | // Preserve explicit ASP locations before inside propagates planner locations. |
| src1.6.7/rdfw.cpp:6734 | ParseEnv | True | initialization | if (score_locations.size() < objects.size()) score_locations.resize(objects.size(), UNKNOWN); |
| src1.6.7/rdfw.cpp:6736 | ParseEnv | False | initialization | if (hold_id > 0) |
| src1.6.7/rdfw.cpp:6738 | ParseEnv | False | initialization | auto held = std::dynamic_pointer_cast<SmallObject>(GetObject(hold_id)); |
| src1.6.7/rdfw.cpp:6740 | ParseEnv | False | initialization | LOG_ERROR("Ignoring invalid hold reference %d", hold_id); |
| src1.6.7/rdfw.cpp:6741 | ParseEnv | True | initialization | hold_id = NONE; |
| src1.6.7/rdfw.cpp:6742 | ParseEnv | False | initialization | SetHold(nullptr, EvidenceSource::INITIAL); |
| src1.6.7/rdfw.cpp:6744 | ParseEnv | False | initialization | SetHold(held, EvidenceSource::INITIAL); |
| src1.6.7/rdfw.cpp:6745 | ParseEnv | True | initialization | score_locations[hold_id] = location; |
| src1.6.7/rdfw.cpp:6746 | ParseEnv | False | initialization | MarkDirectLocationEvidence(hold_id, stage == 1, EvidenceSource::INITIAL); |
| src1.6.7/rdfw.cpp:6747 | ParseEnv | False | initialization | SetInsideEvidence(hold_id, stage == 1, EvidenceSource::INITIAL); |
| src1.6.7/rdfw.cpp:6750 | ParseEnv | False | initialization | if (plate_id > 0) |
| src1.6.7/rdfw.cpp:6752 | ParseEnv | False | initialization | auto plated = std::dynamic_pointer_cast<SmallObject>(GetObject(plate_id)); |
| src1.6.7/rdfw.cpp:6753 | ParseEnv | False | initialization | if (!plated \|\| plate_id == hold_id) { |
| src1.6.7/rdfw.cpp:6754 | ParseEnv | False | initialization | LOG_ERROR("Ignoring invalid plate reference %d", plate_id); |
| src1.6.7/rdfw.cpp:6755 | ParseEnv | True | initialization | plate_id = NONE; |
| src1.6.7/rdfw.cpp:6756 | ParseEnv | False | initialization | SetPlate(nullptr, EvidenceSource::INITIAL); |
| src1.6.7/rdfw.cpp:6758 | ParseEnv | False | initialization | SetPlate(plated, EvidenceSource::INITIAL); |
| src1.6.7/rdfw.cpp:6759 | ParseEnv | True | initialization | score_locations[plate_id] = location; |
| src1.6.7/rdfw.cpp:6760 | ParseEnv | False | initialization | MarkDirectLocationEvidence(plate_id, stage == 1, EvidenceSource::INITIAL); |
| src1.6.7/rdfw.cpp:6761 | ParseEnv | False | initialization | SetInsideEvidence(plate_id, stage == 1, EvidenceSource::INITIAL); |
| src1.6.7/rdfw.cpp:6764 | ParseEnv | False | initialization | if (!holdProvenance.received.present) |
| src1.6.7/rdfw.cpp:6765 | ParseEnv | False | initialization | UpdateProvenance(StateField::HOLD, 0, hold_id, |
| src1.6.7/rdfw.cpp:6766 | ParseEnv | False | initialization | stage == 1, EvidenceSource::INITIAL); |
| src1.6.7/rdfw.cpp:6767 | ParseEnv | False | initialization | if (!plateProvenance.received.present) |
| src1.6.7/rdfw.cpp:6768 | ParseEnv | False | initialization | UpdateProvenance(StateField::PLATE, 0, plate_id, |
| src1.6.7/rdfw.cpp:6769 | ParseEnv | False | initialization | stage == 1, EvidenceSource::INITIAL); |
| src1.6.7/rdfw.cpp:6773 | ParseEnv | False | initialization | if (s == plate \|\| s == hold) |
| src1.6.7/rdfw.cpp:6775 | ParseEnv | False | initialization | if (s->inside != UNKNOWN && s->inside != NONE) |
| src1.6.7/rdfw.cpp:6777 | ParseEnv | False | initialization | auto p = dynamic_pointer_cast<Container>(GetObject(s->inside)); |
| src1.6.7/rdfw.cpp:6781 | ParseEnv | False | initialization | for (auto item:p->smallObjectsInside) if(item && item->id==s->id) listed=true; |
| src1.6.7/rdfw.cpp:6782 | ParseEnv | True | initialization | if (!listed) p->smallObjectsInside.push_back(s); |
| src1.6.7/rdfw.cpp:6784 | ParseEnv | False | initialization | ApplyStateValue(StateField::LOCATION,s->id,container_fact!=UNKNOWN?container_fact:p->location, |
| src1.6.7/rdfw.cpp:6786 | ParseEnv | False | initialization | EvidenceSource::INITIAL); |
| src1.6.7/rdfw.cpp:6792 | ParseEnv | True | initialization | s->location = UNKNOWN; |
| src1.6.7/rdfw.cpp:6793 | ParseEnv | True | initialization | s->inside = UNKNOWN; |
| src1.6.7/rdfw.cpp:6794 | ParseEnv | False | initialization | MarkDirectLocationEvidence(s->id,false,EvidenceSource::UNKNOWN); |
| src1.6.7/rdfw.cpp:6795 | ParseEnv | False | initialization | SetInsideEvidence(s->id,false,EvidenceSource::UNKNOWN); |
| src1.6.7/rdfw.cpp:6798 | ParseEnv | False | initialization | else if (s->location != UNKNOWN && |
| src1.6.7/rdfw.cpp:6800 | ParseEnv | True | initialization | s->inside = NONE; |
| src1.6.7/rdfw.cpp:6801 | ParseEnv | False | initialization | if (s->inside != UNKNOWN && s != plate && s != hold && |
| src1.6.7/rdfw.cpp:6802 | ParseEnv | False | initialization | Provenance(StateField::INSIDE,s->id).resolved_value!=s->inside) |
| src1.6.7/rdfw.cpp:6803 | ParseEnv | False | initialization | SetInsideEvidence(s->id, stage == 1, EvidenceSource::INITIAL); |
| src1.6.7/rdfw.cpp:6804 | ParseEnv | False | initialization | if (s->location != UNKNOWN && LocationSource(s->id) == EvidenceSource::UNKNOWN) |
| src1.6.7/rdfw.cpp:6805 | ParseEnv | False | initialization | MarkDirectLocationEvidence(s->id, stage == 1, EvidenceSource::INITIAL); |
| src1.6.7/rdfw.cpp:6829 | ParseInfo | False | canonical_mutation | if (behave == "on") |
| src1.6.7/rdfw.cpp:6832 | ParseInfo | False | canonical_mutation | int thelocation = yFact!=UNKNOWN ? yFact : info.Y[0]->location; |
| src1.6.7/rdfw.cpp:6835 | ParseInfo | False | canonical_mutation | ApplyStateValue(StateField::LOCATION,v->id,thelocation,stage == 1 && IsLocationVerified(info.Y[0]->id),EvidenceSource::EXPLICIT_INFO); |
| src1.6.7/rdfw.cpp:6839 | ParseInfo | False | declaration | // Official on/near mean co-location; neither proves outside. |
| src1.6.7/rdfw.cpp:6841 | ParseInfo | True | planning_cache | small->on = info.Y[0]->id; |
| src1.6.7/rdfw.cpp:6849 | ParseInfo | False | canonical_mutation | int yLocation = yFact!=UNKNOWN ? yFact : info.Y[0]->location; |
| src1.6.7/rdfw.cpp:6850 | ParseInfo | False | canonical_mutation | int xLocation = xFact!=UNKNOWN ? xFact : info.X[0]->location; |
| src1.6.7/rdfw.cpp:6856 | ParseInfo | False | canonical_mutation | ApplyStateValue(StateField::LOCATION,v->id,yLocation,stage == 1 && IsLocationVerified(info.Y[0]->id),EvidenceSource::EXPLICIT_INFO); |
| src1.6.7/rdfw.cpp:6869 | ParseInfo | False | canonical_mutation | ApplyStateValue(StateField::LOCATION,v->id,xLocation,stage == 1 && IsLocationVerified(info.X[0]->id),EvidenceSource::EXPLICIT_INFO); |
| src1.6.7/rdfw.cpp:6878 | ParseInfo | False | canonical_mutation | else if (behave == "plate") |
| src1.6.7/rdfw.cpp:6880 | ParseInfo | False | canonical_mutation | if (plate == nullptr) |
| src1.6.7/rdfw.cpp:6885 | ParseInfo | False | canonical_mutation | if (hold_id == small->id) SetHold(nullptr, EvidenceSource::EXPLICIT_INFO); |
| src1.6.7/rdfw.cpp:6886 | ParseInfo | False | canonical_mutation | SetPlate(small, EvidenceSource::EXPLICIT_INFO); |
| src1.6.7/rdfw.cpp:6887 | ParseInfo | False | canonical_mutation | SetInsideEvidence(small->id, stage == 1, EvidenceSource::EXPLICIT_INFO); |
| src1.6.7/rdfw.cpp:6891 | ParseInfo | False | canonical_mutation | LOG_ERROR("The plate already has a small object (%d %s)", plate->id, plate->sort.c_str()); |
| src1.6.7/rdfw.cpp:6894 | ParseInfo | False | canonical_mutation | else if (behave == "inside" \|\| behave == "in") |
| src1.6.7/rdfw.cpp:6905 | ParseInfo | False | canonical_mutation | if (hold_id == p->id) SetHold(nullptr, EvidenceSource::EXPLICIT_INFO); |
| src1.6.7/rdfw.cpp:6906 | ParseInfo | False | canonical_mutation | if (plate_id == p->id) SetPlate(nullptr, EvidenceSource::EXPLICIT_INFO); |
| src1.6.7/rdfw.cpp:6907 | ParseInfo | True | planning_cache | p->on = NONE; |
| src1.6.7/rdfw.cpp:6910 | ParseInfo | False | canonical_mutation | StageStateValue(StateField::LOCATION,p->id,containerFact!=UNKNOWN ? containerFact : c->location); |
| src1.6.7/rdfw.cpp:6911 | ParseInfo | False | canonical_mutation | SetInsideEvidence(p->id, stage == 1, EvidenceSource::EXPLICIT_INFO); |
| src1.6.7/rdfw.cpp:6912 | ParseInfo | False | canonical_mutation | MarkDirectLocationEvidence(p->id, stage == 1 && IsLocationVerified(cId), |
| src1.6.7/rdfw.cpp:6913 | ParseInfo | False | canonical_mutation | EvidenceSource::EXPLICIT_INFO); |
| src1.6.7/rdfw.cpp:6925 | ParseInfo | False | canonical_mutation | ApplyStateValue(StateField::CONTAINER_STATE,p->id,true,stage == 1,EvidenceSource::EXPLICIT_INFO); |
| src1.6.7/rdfw.cpp:6934 | ParseInfo | False | canonical_mutation | ApplyStateValue(StateField::CONTAINER_STATE,p->id,false,stage == 1,EvidenceSource::EXPLICIT_INFO); |
| src1.6.7/rdfw.cpp:7053 | Fini | True | initialization | holdProvenance=StateProvenance(); plateProvenance=StateProvenance(); |
| src1.6.7/rdfw.cpp:7057 | Fini | True | initialization | location = UNKNOWN; |
| src1.6.7/rdfw.cpp:7058 | Fini | True | initialization | hold = nullptr; |
| src1.6.7/rdfw.cpp:7059 | Fini | True | initialization | hold_id = 0; |
| src1.6.7/rdfw.cpp:7063 | Fini | True | initialization | plate = nullptr; |
| src1.6.7/rdfw.cpp:7064 | Fini | True | initialization | plate_id = 0; |
| src1.6.7/rdfw.cpp:7085 | Fini | True | initialization | posSensedFlag.clear(); |
| src1.6.7/rdfw.cpp:7086 | Fini | True | initialization | objectLocationVerified.clear(); |
| src1.6.7/rdfw.cpp:7087 | Fini | True | initialization | objectLocationInferredByMustNear.clear(); |
| src1.6.7/rdfw.cpp:7088 | Fini | True | initialization | objectInsideVerified.clear(); |
| src1.6.7/rdfw.cpp:7089 | Fini | True | initialization | containerStateVerified.clear(); |
| src1.6.7/rdfw.cpp:7090 | Fini | True | initialization | objectLocationSource.clear(); |
| src1.6.7/rdfw.cpp:7091 | Fini | True | initialization | locationProvenance.clear(); |
| src1.6.7/rdfw.cpp:7092 | Fini | True | initialization | insideProvenance.clear(); |
| src1.6.7/rdfw.cpp:7093 | Fini | True | initialization | containerProvenance.clear(); |
| src1.6.7/rdfw.cpp:7094 | Fini | True | initialization | objectInsideSource.clear(); |
| src1.6.7/rdfw.cpp:7095 | Fini | True | initialization | containerStateSource.clear(); |
| src1.6.7/rdfw.cpp:7113 | Fini | False | initialization | posSensedFlag.shrink_to_fit(); |
| src1.6.7/rdfw.cpp:7114 | Fini | False | initialization | objectLocationVerified.shrink_to_fit(); |
| src1.6.7/rdfw.cpp:7115 | Fini | False | initialization | objectLocationInferredByMustNear.shrink_to_fit(); |
| src1.6.7/rdfw.cpp:7116 | Fini | False | initialization | objectInsideVerified.shrink_to_fit(); |
| src1.6.7/rdfw.cpp:7117 | Fini | False | initialization | containerStateVerified.shrink_to_fit(); |
| src1.6.7/rdfw.cpp:7153 | Fini | True | initialization | posSensedFlag.resize(100, false); |
| src1.6.7/rdfw.cpp:7154 | Fini | True | initialization | objectLocationVerified.resize(100, false); |
| src1.6.7/rdfw.cpp:7155 | Fini | True | initialization | objectLocationInferredByMustNear.resize(100, false); |
| src1.6.7/rdfw.cpp:7156 | Fini | True | initialization | objectInsideVerified.resize(100, false); |
| src1.6.7/rdfw.cpp:7157 | Fini | True | initialization | containerStateVerified.resize(100, false); |
| src1.6.7/rdfw.cpp:7158 | Fini | True | initialization | locationSensedObjects.resize(100); |
| src1.6.7/rdfw.cpp:7161 | Fini | False | initialization | for (auto& loc_info : locationSensedObjects) { |
| src1.6.7/rdfw.cpp:7199 | OptimizeMemoryUsage | False | mutation_consumer | posSensedFlag.shrink_to_fit(); |
| src1.6.7/rdfw.cpp:7200 | OptimizeMemoryUsage | False | mutation_consumer | objectLocationVerified.shrink_to_fit(); |
| src1.6.7/rdfw.cpp:7201 | OptimizeMemoryUsage | False | mutation_consumer | objectLocationInferredByMustNear.shrink_to_fit(); |
| src1.6.7/rdfw.cpp:7202 | OptimizeMemoryUsage | False | mutation_consumer | objectInsideVerified.shrink_to_fit(); |
| src1.6.7/rdfw.cpp:7203 | OptimizeMemoryUsage | False | mutation_consumer | containerStateVerified.shrink_to_fit(); |
| src1.6.7/rdfw.cpp:7227 | OptimizeMemoryUsage | False | mutation_consumer | for (auto& loc_info : locationSensedObjects) { |
| src1.6.7/rdfw.cpp:7230 | OptimizeMemoryUsage | False | mutation_consumer | locationSensedObjects.shrink_to_fit(); |
| src1.6.7/rdfw.cpp:7272 | Instruction | True | instruction_metadata | structuredSource = true; |
| src1.6.7/rdfw.cpp:7325 | Instruction | False | read_access | invalidate("conflicting color conditions"); |
| src1.6.7/rdfw.cpp:7331 | Instruction | False | read_access | invalidate("conflicting sort conditions"); |
| src1.6.7/rdfw.cpp:7343 | Instruction | False | read_access | invalidate("conflicting type conditions"); |
| src1.6.7/rdfw.cpp:7355 | Instruction | False | read_access | invalidate("conflicting id conditions"); |
| src1.6.7/rdfw.cpp:7487 | BuildMustNearRelations | False | mutation_consumer | hold_mustnear = hold_id > 0 && static_cast<size_t>(hold_id) < mustNearComponent.size() && |
| src1.6.7/rdfw.cpp:7488 | BuildMustNearRelations | False | mutation_consumer | mustNearComponent[hold_id] != UNKNOWN; |
| src1.6.7/rdfw.cpp:7489 | BuildMustNearRelations | False | mutation_consumer | plate_mustnear = plate_id > 0 && static_cast<size_t>(plate_id) < mustNearComponent.size() && |
| src1.6.7/rdfw.cpp:7490 | BuildMustNearRelations | False | mutation_consumer | mustNearComponent[plate_id] != UNKNOWN; |
| src1.6.7/rdfw.cpp:7513 | RefreshMustNearConstraintState | False | canonical_mutation | const int loc = objects[id]->location; |
| src1.6.7/rdfw.cpp:7515 | RefreshMustNearConstraintState | False | canonical_mutation | if (FactLocation(id) == loc && !objectLocationInferredByMustNear[id]) |
| src1.6.7/rdfw.cpp:7517 | RefreshMustNearConstraintState | False | canonical_mutation | if (!objectLocationInferredByMustNear[id]) ++candidate_votes[loc]; |
| src1.6.7/rdfw.cpp:7537 | RefreshMustNearConstraintState | False | canonical_mutation | if (objects[id]->location == chosen_location && |
| src1.6.7/rdfw.cpp:7538 | RefreshMustNearConstraintState | False | canonical_mutation | !objectLocationInferredByMustNear[id] && |
| src1.6.7/rdfw.cpp:7555 | RefreshMustNearConstraintState | False | canonical_mutation | if (FactLocation(id) != UNKNOWN && !objectLocationInferredByMustNear[id] && |
| src1.6.7/rdfw.cpp:7556 | RefreshMustNearConstraintState | False | canonical_mutation | objects[id]->location != UNKNOWN && objects[id]->location != chosen_location) { |
| src1.6.7/rdfw.cpp:7567 | RefreshMustNearConstraintState | False | canonical_mutation | if (!objectLocationInferredByMustNear[id]) continue; |
| src1.6.7/rdfw.cpp:7569 | RefreshMustNearConstraintState | False | canonical_mutation | objects[id]->location != chosen_location) { |
| src1.6.7/rdfw.cpp:7570 | RefreshMustNearConstraintState | False | canonical_mutation | ApplyStateValue(StateField::LOCATION,id,UNKNOWN,false,EvidenceSource::UNKNOWN); |
| src1.6.7/rdfw.cpp:7574 | RefreshMustNearConstraintState | False | canonical_mutation | anchored ? EvidenceSource::CONSTRAINT_DERIVED |
| src1.6.7/rdfw.cpp:7575 | RefreshMustNearConstraintState | False | canonical_mutation | : EvidenceSource::CONSTRAINT_HEURISTIC); |
| src1.6.7/rdfw.cpp:7584 | RefreshMustNearConstraintState | False | canonical_mutation | if (objects[id]->location == chosen_location && |
| src1.6.7/rdfw.cpp:7585 | RefreshMustNearConstraintState | False | canonical_mutation | !objectLocationInferredByMustNear[id] && |
| src1.6.7/rdfw.cpp:7590 | RefreshMustNearConstraintState | False | canonical_mutation | anchored ? EvidenceSource::CONSTRAINT_DERIVED |
| src1.6.7/rdfw.cpp:7591 | RefreshMustNearConstraintState | False | canonical_mutation | : EvidenceSource::CONSTRAINT_HEURISTIC); |
| src1.6.7/rdfw.cpp:7596 | RefreshMustNearConstraintState | False | declaration | // SmallObject::inside/on，near 本身不代表包含或承载关系。 |
| src1.6.7/rdfw.cpp:7599 | RefreshMustNearConstraintState | False | canonical_mutation | for (const auto& item : container->smallObjectsInside) { |
| src1.6.7/rdfw.cpp:7600 | RefreshMustNearConstraintState | False | canonical_mutation | if (!item \|\| item->inside != container->id) continue; |
| src1.6.7/rdfw.cpp:7604 | RefreshMustNearConstraintState | False | canonical_mutation | location_entailed ? EvidenceSource::CONSTRAINT_DERIVED |
| src1.6.7/rdfw.cpp:7605 | RefreshMustNearConstraintState | False | canonical_mutation | : EvidenceSource::CONSTRAINT_HEURISTIC); |
| src1.6.7/rdfw.cpp:7610 | RefreshMustNearConstraintState | False | canonical_mutation | LOG(GREEN "[MustNear] inferred obj %u at location %d\n" RESET, |
| src1.6.7/rdfw.cpp:7618 | RefreshMustNearConstraintState | False | canonical_mutation | const int loc = objects[id]->location; |
| src1.6.7/rdfw.cpp:7633 | RefreshMustNearConstraintState | False | canonical_mutation | LOG(YELLOW "[MustNear] component %d has conflicting/insufficient evidence; not propagated\n" RESET, |
| src1.6.7/rdfw.cpp:7660 | ApplyMustInConstraintCorrection | False | canonical_mutation | if (cons.IsUsable() && (cons.behave == "inside" \|\| cons.behave == "in") && |
| src1.6.7/rdfw.cpp:7675 | ApplyMustInConstraintCorrection | False | canonical_mutation | cout<<"sm->inside: "<<sm->inside<<endl; |
| src1.6.7/rdfw.cpp:7677 | ApplyMustInConstraintCorrection | False | canonical_mutation | if (sm->inside != UNKNOWN && sm->inside != y) { |
| src1.6.7/rdfw.cpp:7678 | ApplyMustInConstraintCorrection | False | canonical_mutation | if (sm->inside >= 0 && sm->inside < numObjs) { |
| src1.6.7/rdfw.cpp:7679 | ApplyMustInConstraintCorrection | False | canonical_mutation | if (auto old_cont = std::dynamic_pointer_cast<Container>(objects[sm->inside])) { |
| src1.6.7/rdfw.cpp:7681 | ApplyMustInConstraintCorrection | False | canonical_mutation | auto& vec = old_cont->smallObjectsInside; |
| src1.6.7/rdfw.cpp:7689 | ApplyMustInConstraintCorrection | False | canonical_mutation | ApplyStateValue(StateField::INSIDE,x,y,true,EvidenceSource::CONSTRAINT_DERIVED); |
| src1.6.7/rdfw.cpp:7696 | ApplyMustInConstraintCorrection | False | canonical_mutation | for (auto&& v : cont->smallObjectsInside) { |
| src1.6.7/rdfw.cpp:7708 | ApplyMustInConstraintCorrection | False | canonical_mutation | int y_loc = y_fact!=UNKNOWN ? y_fact : objects[y]->location; |
| src1.6.7/rdfw.cpp:7713 | ApplyMustInConstraintCorrection | False | canonical_mutation | location_entailed ? EvidenceSource::CONSTRAINT_DERIVED |
| src1.6.7/rdfw.cpp:7714 | ApplyMustInConstraintCorrection | False | canonical_mutation | : EvidenceSource::CONSTRAINT_HEURISTIC); |
| src1.6.7/rdfw.cpp:7727 | ApplyMustInConstraintCorrection | False | canonical_mutation | if (cons.behave != "inside"&&cons.behave != "in") continue; |
| src1.6.7/rdfw.cpp:7736 | ApplyMustInConstraintCorrection | False | canonical_mutation | if (smObj->inside == y) { |
| src1.6.7/rdfw.cpp:7739 | ApplyMustInConstraintCorrection | False | canonical_mutation | int old_loc = smObj->location; |
| src1.6.7/rdfw.cpp:7741 | ApplyMustInConstraintCorrection | False | canonical_mutation | SetInsideEvidence(x,false,EvidenceSource::UNKNOWN); |
| src1.6.7/rdfw.cpp:7742 | ApplyMustInConstraintCorrection | False | canonical_mutation | MarkDirectLocationEvidence(x,false,EvidenceSource::UNKNOWN); |
| src1.6.7/rdfw.cpp:7747 | ApplyMustInConstraintCorrection | False | canonical_mutation | auto& vec = cont->smallObjectsInside; |
| src1.6.7/rdfw.cpp:7795 | ApplyOpenCloseCorrection | False | read_access | if (cont->isOpen != 1) { |
| src1.6.7/rdfw.cpp:7802 | ApplyOpenCloseCorrection | False | read_access | if (cont->isOpen) { |
| src1.6.7/rdfw.cpp:7809 | ApplyOpenCloseCorrection | False | read_access | if (cont->isOpen) { |
| src1.6.7/rdfw.cpp:7816 | ApplyOpenCloseCorrection | False | read_access | if (cont->isOpen != 1) { |
| src1.6.7/rdfw.cpp:7832 | ApplyOpenCloseCorrection | False | read_access | contradictory ? EvidenceSource::CONSTRAINT_HEURISTIC |
| src1.6.7/rdfw.cpp:7833 | ApplyOpenCloseCorrection | False | read_access | : EvidenceSource::CONSTRAINT_DERIVED); |
| src1.6.7/rdfw.hpp:36 | declaration/inline | False | declaration | // Source of the current fact, separate from whether it is reliable enough |
| src1.6.7/rdfw.hpp:38 | declaration/inline | False | declaration | enum class EvidenceSource { |
| src1.6.7/rdfw.hpp:43 | declaration/inline | False | declaration | // Evidence is a received claim. Object fields are planning hypotheses/cache; |
| src1.6.7/rdfw.hpp:44 | declaration/inline | False | declaration | // StateProvenance plus canonical queries alone qualify current facts. |
| src1.6.7/rdfw.hpp:48 | declaration/inline | False | declaration | EvidenceSource source = EvidenceSource::UNKNOWN; |
| src1.6.7/rdfw.hpp:51 | StateClaim | False | read_access | StateClaim(int v, EvidenceSource s, bool p) : value(v), source(s), present(p) {} |
| src1.6.7/rdfw.hpp:57 | declaration/inline | True | declaration | std::size_t revision = 0; |
| src1.6.7/rdfw.hpp:60 | StateDependency | False | read_access | : field(f), id(object), value(v), revision(r) {} |
| src1.6.7/rdfw.hpp:62 | declaration/inline | False | declaration | struct StateProvenance { |
| src1.6.7/rdfw.hpp:63 | declaration/inline | False | declaration | StateClaim received; |
| src1.6.7/rdfw.hpp:64 | declaration/inline | False | declaration | StateClaim conflicting; |
| src1.6.7/rdfw.hpp:65 | declaration/inline | True | declaration | int resolved_value = UNKNOWN; |
| src1.6.7/rdfw.hpp:66 | declaration/inline | True | declaration | EvidenceSource resolved_source = EvidenceSource::UNKNOWN; |
| src1.6.7/rdfw.hpp:67 | declaration/inline | True | declaration | bool resolved_verified = false; |
| src1.6.7/rdfw.hpp:68 | declaration/inline | True | declaration | std::size_t revision = 0; |
| src1.6.7/rdfw.hpp:69 | declaration/inline | False | declaration | StateDependency dependencies[2]; |
| src1.6.7/rdfw.hpp:70 | declaration/inline | True | declaration | unsigned int dependency_count = 0; |
| src1.6.7/rdfw.hpp:71 | declaration/inline | True | declaration | int support_constraint_index = UNKNOWN; |
| src1.6.7/rdfw.hpp:72 | declaration/inline | False | declaration | std::vector<std::size_t> supporting_constraints; |
| src1.6.7/rdfw.hpp:107 | declaration/inline | False | declaration | *      location    (int)   : ... |
| src1.6.7/rdfw.hpp:113 | declaration/inline | False | declaration | *      Object (Init)       : Initialize id, sort and location (id must be known) |
| src1.6.7/rdfw.hpp:119 | declaration/inline | False | declaration | int location; |
| src1.6.7/rdfw.hpp:125 | Object | True | initialization | Object(int id, const string &sort = "", int location = UNKNOWN) |
| src1.6.7/rdfw.hpp:126 | Object | False | initialization | : sort(sort), location(location), id(id) {}   // Initialize id, sort and location (id must be known) |
| src1.6.7/rdfw.hpp:131 | ToString | False | read_access | return "id:" + to_string(id) + "    at:" + to_string(location) + "     sort:" + sort + "\n"; |
| src1.6.7/rdfw.hpp:142 | declaration/inline | False | declaration | *      inside      (int)   : the big object id which small object inside |
| src1.6.7/rdfw.hpp:145 | declaration/inline | False | declaration | *      Object (Init)       : Initialize id, sort and location (id must be known) |
| src1.6.7/rdfw.hpp:152 | declaration/inline | True | declaration | int inside = UNKNOWN;  // the big object id which small object inside |
| src1.6.7/rdfw.hpp:153 | declaration/inline | True | declaration | int on = UNKNOWN;      // the big object id which small object on |
| src1.6.7/rdfw.hpp:156 | SmallObject | True | initialization | SmallObject(int id, int location = UNKNOWN, const string &sort = "", const string &color = "") |
| src1.6.7/rdfw.hpp:157 | SmallObject | False | initialization | : Object(id, sort, location), color(color) {} |
| src1.6.7/rdfw.hpp:166 | ToString | False | read_access | return Object::ToString() + "color:" + color + "    inside:" + to_string(inside) + "    on:" + to_string(on) + "\n"; |
| src1.6.7/rdfw.hpp:176 | declaration/inline | False | declaration | *      inside      (int)   : the big object id which small object inside |
| src1.6.7/rdfw.hpp:183 | BigObject | True | initialization | BigObject(int id, int location = UNKNOWN, string sort = "") |
| src1.6.7/rdfw.hpp:184 | BigObject | False | initialization | : Object(id, sort, location) {} |
| src1.6.7/rdfw.hpp:197 | declaration/inline | False | declaration | *      smallObjectsInside  (vector<shared_ptr<SmallObject>>) |
| src1.6.7/rdfw.hpp:198 | declaration/inline | False | declaration | *      isOpen      (int)   : 0(closed)  1(open) |
| src1.6.7/rdfw.hpp:200 | declaration/inline | False | declaration | *      inside      (int)   : the big object id which small object inside |
| src1.6.7/rdfw.hpp:209 | declaration/inline | False | declaration | vector<shared_ptr<SmallObject>> smallObjectsInside; |
| src1.6.7/rdfw.hpp:210 | declaration/inline | True | declaration | int isOpen = 0; |
| src1.6.7/rdfw.hpp:212 | Container | True | initialization | Container(int id, int location = UNKNOWN, bool isOpen = true, string sort = "") |
| src1.6.7/rdfw.hpp:213 | Container | False | initialization | : BigObject(id, location, sort), isOpen(isOpen) {} |
| src1.6.7/rdfw.hpp:217 | Container | False | initialization | : BigObject(obj), isOpen(UNKNOWN) {} |
| src1.6.7/rdfw.hpp:221 | Container | False | initialization | : BigObject(*obj), isOpen(UNKNOWN) {} |
| src1.6.7/rdfw.hpp:226 | DeleteObjectInside | False | membership_primitive | for (int i = 0; i < smallObjectsInside.size(); i++) |
| src1.6.7/rdfw.hpp:228 | DeleteObjectInside | False | membership_primitive | if (smallObjectsInside[i]->id == target->id) { |
| src1.6.7/rdfw.hpp:229 | DeleteObjectInside | True | membership_primitive | smallObjectsInside.erase(smallObjectsInside.begin() + i); |
| src1.6.7/rdfw.hpp:237 | ToString | False | read_access | for (int i = 0; i < smallObjectsInside.size(); i++) |
| src1.6.7/rdfw.hpp:239 | ToString | False | read_access | out += to_string(i) + " " + smallObjectsInside[i]->ToString(); |
| src1.6.7/rdfw.hpp:251 | declaration/inline | False | declaration | *      hold        (shared_ptr<SmallObject>)   : ... |
| src1.6.7/rdfw.hpp:252 | declaration/inline | False | declaration | *      plate       (shared_ptr<SmallObject>)   : ... |
| src1.6.7/rdfw.hpp:253 | declaration/inline | False | declaration | *      hold_id     (int)   : ... |
| src1.6.7/rdfw.hpp:254 | declaration/inline | False | declaration | *      plate_id    (int)   : ... |
| src1.6.7/rdfw.hpp:264 | declaration/inline | False | declaration | shared_ptr<SmallObject> hold; |
| src1.6.7/rdfw.hpp:265 | declaration/inline | False | declaration | shared_ptr<SmallObject> plate; |
| src1.6.7/rdfw.hpp:267 | declaration/inline | True | declaration | int hold_id = NONE, plate_id = UNKNOWN; |
| src1.6.7/rdfw.hpp:269 | Robot | True | initialization | Robot(int id, int location = UNKNOWN) |
| src1.6.7/rdfw.hpp:270 | Robot | False | initialization | : Object(id, "robot", location) {} |
| src1.6.7/rdfw.hpp:274 | SetHold | False | canonical_mutation | void SetHold(const shared_ptr<SmallObject> &hold) { |
| src1.6.7/rdfw.hpp:275 | SetHold | True | canonical_mutation | this->hold = hold; |
| src1.6.7/rdfw.hpp:276 | SetHold | False | canonical_mutation | if (hold != nullptr) { |
| src1.6.7/rdfw.hpp:277 | SetHold | True | canonical_mutation | this->hold->location = location; |
| src1.6.7/rdfw.hpp:278 | SetHold | True | canonical_mutation | hold_id = hold->id; |
| src1.6.7/rdfw.hpp:279 | SetHold | True | canonical_mutation | hold->inside = NONE; |
| src1.6.7/rdfw.hpp:280 | SetHold | True | planning_cache | hold->on = NONE; |
| src1.6.7/rdfw.hpp:281 | SetHold | False | canonical_mutation | if (plate_id == hold_id) { |
| src1.6.7/rdfw.hpp:282 | SetHold | False | canonical_mutation | plate.reset(); |
| src1.6.7/rdfw.hpp:283 | SetHold | True | canonical_mutation | plate_id = NONE; |
| src1.6.7/rdfw.hpp:287 | SetHold | True | canonical_mutation | hold_id = NONE; |
| src1.6.7/rdfw.hpp:290 | SetPlate | False | canonical_mutation | void SetPlate(const shared_ptr<SmallObject> &plate) { |
| src1.6.7/rdfw.hpp:291 | SetPlate | True | canonical_mutation | this->plate = plate; |
| src1.6.7/rdfw.hpp:292 | SetPlate | False | canonical_mutation | if (plate != nullptr) { |
| src1.6.7/rdfw.hpp:293 | SetPlate | True | canonical_mutation | this->plate->location = location; |
| src1.6.7/rdfw.hpp:294 | SetPlate | True | canonical_mutation | plate_id = plate->id; |
| src1.6.7/rdfw.hpp:295 | SetPlate | True | canonical_mutation | plate->inside = NONE; |
| src1.6.7/rdfw.hpp:296 | SetPlate | True | planning_cache | plate->on = NONE; |
| src1.6.7/rdfw.hpp:297 | SetPlate | False | canonical_mutation | if (hold_id == plate_id) { |
| src1.6.7/rdfw.hpp:298 | SetPlate | False | canonical_mutation | hold.reset(); |
| src1.6.7/rdfw.hpp:299 | SetPlate | True | canonical_mutation | hold_id = NONE; |
| src1.6.7/rdfw.hpp:303 | SetPlate | True | canonical_mutation | plate_id = NONE; |
| src1.6.7/rdfw.hpp:307 | ToString | False | read_access | return Object::ToString() + "hold:\n" + (hold != nullptr ? hold->ToString() : "") + "plate:\n" + (plate != nullptr ? plate->ToString() : ""); |
| src1.6.7/rdfw.hpp:439 | declaration/inline | False | declaration | vector<bool> constraint_eligible; |
| src1.6.7/rdfw.hpp:442 | declaration/inline | False | declaration | vector<bool> constraint_uncertain; |
| src1.6.7/rdfw.hpp:443 | declaration/inline | False | declaration | // Stage 1 ASP at facts, separate from planner locations inferred from inside. |
| src1.6.7/rdfw.hpp:444 | declaration/inline | False | declaration | vector<int> score_locations; |
| src1.6.7/rdfw.hpp:475 | declaration/inline | False | declaration | vector<vector<int>> putin_cons;      //not_info   inside   + not_task   putin |
| src1.6.7/rdfw.hpp:476 | declaration/inline | False | declaration | vector<vector<int>> takeout_cons;    // ontnot_infor  inside   + not_task   takeout |
| src1.6.7/rdfw.hpp:477 | declaration/inline | False | declaration | vector<vector<int>> putdown_cons;    //not_info   on   + not_task   puton |
| src1.6.7/rdfw.hpp:478 | declaration/inline | False | declaration | vector<int> putdown1_cons;        //not_task   putdown  + hold  + plate |
| src1.6.7/rdfw.hpp:482 | declaration/inline | False | declaration | vector<int> pickup_cons;         //not_info   plate   + not_task   pickup |
| src1.6.7/rdfw.hpp:485 | declaration/inline | False | declaration | vector<int> fromplate_cons;      //hold |
| src1.6.7/rdfw.hpp:486 | declaration/inline | False | declaration | vector<int> toplate_cons;        //plate |
| src1.6.7/rdfw.hpp:499 | declaration/inline | False | declaration | // objectLocationInferredByMustNear 用来区分直接证据和约束推导证据， |
| src1.6.7/rdfw.hpp:502 | declaration/inline | False | declaration | std::vector<bool> objectLocationInferredByMustNear; |
| src1.6.7/rdfw.hpp:526 | declaration/inline | False | declaration | vector<bool> posSensedFlag;   // 位置感知记录标识，避免重复感知 |
| src1.6.7/rdfw.hpp:529 | declaration/inline | False | declaration | vector<bool> objectLocationVerified; |
| src1.6.7/rdfw.hpp:530 | declaration/inline | False | declaration | vector<bool> objectInsideVerified; |
| src1.6.7/rdfw.hpp:531 | declaration/inline | False | declaration | vector<bool> containerStateVerified; |
| src1.6.7/rdfw.hpp:532 | declaration/inline | False | declaration | vector<EvidenceSource> objectLocationSource; |
| src1.6.7/rdfw.hpp:533 | declaration/inline | False | declaration | vector<EvidenceSource> objectInsideSource; |
| src1.6.7/rdfw.hpp:534 | declaration/inline | False | declaration | vector<EvidenceSource> containerStateSource; |
| src1.6.7/rdfw.hpp:536 | declaration/inline | False | declaration | vector<StateProvenance> locationProvenance; |
| src1.6.7/rdfw.hpp:537 | declaration/inline | False | declaration | vector<StateProvenance> insideProvenance; |
| src1.6.7/rdfw.hpp:538 | declaration/inline | False | declaration | vector<StateProvenance> containerProvenance; |
| src1.6.7/rdfw.hpp:539 | declaration/inline | False | declaration | StateProvenance holdProvenance; |
| src1.6.7/rdfw.hpp:540 | declaration/inline | False | declaration | StateProvenance plateProvenance; |
| src1.6.7/rdfw.hpp:541 | declaration/inline | False | declaration | const StateProvenance& Provenance(StateField field, unsigned int id) const; |
| src1.6.7/rdfw.hpp:548 | declaration/inline | False | declaration | // Source/Verified arrays or Object planning hypotheses for qualification. |
| src1.6.7/rdfw.hpp:556 | declaration/inline | False | declaration | // One value mutation entry point; received contradictions retain a |
| src1.6.7/rdfw.hpp:559 | declaration/inline | False | declaration | bool verified, EvidenceSource source); |
| src1.6.7/rdfw.hpp:568 | declaration/inline | False | declaration | EvidenceSource source); |
| src1.6.7/rdfw.hpp:578 | declaration/inline | False | declaration | vector<LocationSensedInfo> locationSensedObjects;  // 每个位置的感知物体记录 |
| src1.6.7/rdfw.hpp:581 | declaration/inline | False | declaration | const LocationSensedInfo& GetLocationSensedInfo(int location) const; |
| src1.6.7/rdfw.hpp:582 | declaration/inline | False | declaration | bool HasObjectAtLocation(int location, unsigned int object_id) const; |
| src1.6.7/rdfw.hpp:583 | declaration/inline | False | declaration | bool HasContainerAtLocation(int location) const; |
| src1.6.7/rdfw.hpp:584 | declaration/inline | False | declaration | vector<unsigned int> GetObjectsAtLocation(int location) const; |
| src1.6.7/rdfw.hpp:585 | declaration/inline | False | declaration | unsigned int GetContainerAtLocation(int location) const; |
| src1.6.7/rdfw.hpp:586 | declaration/inline | False | declaration | int CountObjectsAtLocation(int location) const; |
| src1.6.7/rdfw.hpp:731 | declaration/inline | False | declaration | EvidenceSource source = EvidenceSource::ACTION_SUCCESS); |
| src1.6.7/rdfw.hpp:732 | declaration/inline | False | declaration | void SetInsideEvidence(unsigned int id, bool verified, EvidenceSource source); |
| src1.6.7/rdfw.hpp:733 | declaration/inline | False | declaration | void SetContainerEvidence(unsigned int id, bool verified, EvidenceSource source); |
| src1.6.7/rdfw.hpp:734 | declaration/inline | False | declaration | EvidenceSource LocationSource(unsigned int id) const; |
| src1.6.7/rdfw.hpp:735 | declaration/inline | False | declaration | EvidenceSource InsideSource(unsigned int id) const; |
| src1.6.7/rdfw.hpp:736 | declaration/inline | False | declaration | EvidenceSource ContainerSource(unsigned int id) const; |
| src1.6.7/rdfw.hpp:751 | declaration/inline | False | declaration | bool IsLocationVerified(unsigned int id) const; |
| src1.6.7/rdfw.hpp:752 | declaration/inline | False | declaration | bool IsInsideVerified(unsigned int id) const; |
| src1.6.7/rdfw.hpp:753 | declaration/inline | False | declaration | bool IsContainerStateVerified(unsigned int id) const; |
| src1.6.7/rdfw.hpp:756 | declaration/inline | False | declaration | EvidenceSource source = EvidenceSource::ACTION_SUCCESS); |
| src1.6.7/rdfw.hpp:758 | declaration/inline | False | declaration | EvidenceSource source = EvidenceSource::ACTION_SUCCESS); |
| src1.6.7/rdfw.hpp:855 | declaration/inline | False | declaration | // Compatibility staging is private and must finish inside this scope. |
| src1.6.7/rdfw.hpp:859 | declaration/inline | False | declaration | int location, inside, on, open; |
| src1.6.7/rdfw.hpp:860 | declaration/inline | False | declaration | StateProvenance loc, in, cont; |
| src1.6.7/rdfw.hpp:862 | declaration/inline | False | declaration | EvidenceSource ls, is, cs; |
| src1.6.7/rdfw.hpp:874 | declaration/inline | False | declaration | StateProvenance hp, pp; |
| src1.6.7/rdfw.hpp:877 | declaration/inline | True | declaration | std::size_t revision=0; |
| src1.6.7/rdfw.hpp:899 | declaration/inline | False | declaration | StateProvenance& MutableProvenance(StateField field, unsigned int id); |
| src1.6.7/rdfw.hpp:900 | declaration/inline | False | declaration | void UpdateProvenance(StateField field, unsigned int id, int value, |
| src1.6.7/rdfw.hpp:901 | declaration/inline | False | declaration | bool verified, EvidenceSource source); |
| src1.6.7/rdfw.hpp:1007 | declaration/inline | True | declaration | bool structuredSource = false; |
| src1.6.7/score_evaluator.cpp:63 | snapshot | False | read_access | if (terminal.constraint_eligible[i] && |
| src1.6.7/state_mutation.cpp:7 | declaration/inline | False | mutation_journal | static_assert(std::is_nothrow_move_constructible<StateProvenance>::value && |
| src1.6.7/state_mutation.cpp:8 | declaration/inline | False | mutation_journal | std::is_nothrow_move_assignable<StateProvenance>::value, |
| src1.6.7/state_mutation.cpp:26 | touch | True | mutation_journal | row.id=id; row.location=w.objects[id]->location; |
| src1.6.7/state_mutation.cpp:27 | touch | True | mutation_journal | row.inside=small?small->inside:UNKNOWN; row.on=small?small->on:UNKNOWN; |
| src1.6.7/state_mutation.cpp:28 | touch | False | mutation_journal | row.open=container?container->isOpen:UNKNOWN; |
| src1.6.7/state_mutation.cpp:29 | touch | False | mutation_journal | row.loc=w.Provenance(StateField::LOCATION,id); |
| src1.6.7/state_mutation.cpp:30 | touch | False | mutation_journal | row.in=w.Provenance(StateField::INSIDE,id); |
| src1.6.7/state_mutation.cpp:31 | touch | False | mutation_journal | row.cont=w.Provenance(StateField::CONTAINER_STATE,id); |
| src1.6.7/state_mutation.cpp:32 | touch | False | mutation_journal | row.lv=w.objectLocationVerified[id]; row.iv=w.objectInsideVerified[id]; |
| src1.6.7/state_mutation.cpp:33 | touch | False | mutation_journal | row.cv=w.containerStateVerified[id]; row.inferred=w.objectLocationInferredByMustNear[id]; |
| src1.6.7/state_mutation.cpp:34 | touch | False | mutation_journal | row.ls=w.objectLocationSource[id]; row.is=w.objectInsideSource[id]; row.cs=w.containerStateSource[id]; |
| src1.6.7/state_mutation.cpp:35 | touch | False | mutation_journal | if (container) row.members=container->smallObjectsInside; |
| src1.6.7/state_mutation.cpp:42 | storage | False | mutation_journal | StateProvenance h=w.holdProvenance, p=w.plateProvenance; |
| src1.6.7/state_mutation.cpp:44 | storage | False | mutation_journal | hand=w.hold; tray=w.plate; hand_id=w.hold_id; tray_id=w.plate_id; |
| src1.6.7/state_mutation.cpp:49 | sensed | False | mutation_journal | if (loc<0 \|\| std::size_t(loc)>=w.locationSensedObjects.size()) return; |
| src1.6.7/state_mutation.cpp:51 | sensed | False | mutation_journal | SensedRow row{loc,w.posSensedFlag[loc],w.locationSensedObjects[loc]}; |
| src1.6.7/state_mutation.cpp:57 | ledger | False | mutation_journal | auto e=w.constraint_eligible, u=w.constraint_uncertain; |
| src1.6.7/state_mutation.cpp:58 | ledger | False | mutation_journal | auto s=w.score_locations; |
| src1.6.7/state_mutation.cpp:60 | ledger | True | mutation_journal | revision=w.world_revision; ledger_saved=true; |
| src1.6.7/state_mutation.cpp:67 | rollback | True | mutation_journal | object->location=r.location; |
| src1.6.7/state_mutation.cpp:68 | rollback | True | mutation_journal | if (auto small=dynamic_pointer_cast<SmallObject>(object)) { small->inside=r.inside; small->on=r.on; } |
| src1.6.7/state_mutation.cpp:70 | rollback | True | mutation_journal | container->isOpen=r.open; container->smallObjectsInside.swap(r.members); |
| src1.6.7/state_mutation.cpp:72 | rollback | False | mutation_journal | std::swap(w.locationProvenance[r.id],r.loc); |
| src1.6.7/state_mutation.cpp:73 | rollback | False | mutation_journal | std::swap(w.insideProvenance[r.id],r.in); |
| src1.6.7/state_mutation.cpp:74 | rollback | False | mutation_journal | std::swap(w.containerProvenance[r.id],r.cont); |
| src1.6.7/state_mutation.cpp:75 | rollback | True | mutation_journal | w.objectLocationVerified[r.id]=r.lv; w.objectInsideVerified[r.id]=r.iv; |
| src1.6.7/state_mutation.cpp:76 | rollback | True | mutation_journal | w.containerStateVerified[r.id]=r.cv; w.objectLocationInferredByMustNear[r.id]=r.inferred; |
| src1.6.7/state_mutation.cpp:77 | rollback | True | mutation_journal | w.objectLocationSource[r.id]=r.ls; w.objectInsideSource[r.id]=r.is; w.containerStateSource[r.id]=r.cs; |
| src1.6.7/state_mutation.cpp:80 | rollback | True | mutation_journal | w.hold=hand; w.plate=tray; w.hold_id=hand_id; w.plate_id=tray_id; |
| src1.6.7/state_mutation.cpp:81 | rollback | False | mutation_journal | std::swap(w.holdProvenance,hp); std::swap(w.plateProvenance,pp); |
| src1.6.7/state_mutation.cpp:84 | rollback | True | mutation_journal | w.posSensedFlag[row.loc]=row.sensed; |
| src1.6.7/state_mutation.cpp:85 | rollback | False | mutation_journal | std::swap(w.locationSensedObjects[row.loc],row.info); |
| src1.6.7/state_mutation.cpp:88 | rollback | True | mutation_journal | w.constraint_eligible.swap(eligible); w.constraint_uncertain.swap(uncertain); |
| src1.6.7/state_mutation.cpp:89 | rollback | True | mutation_journal | w.score_locations.swap(score); w.world_revision=revision; |
| src1.6.7/state_mutation.cpp:95 | rollback | False | mutation_journal | const auto withdraw=[](StateProvenance& p) { |
| src1.6.7/state_mutation.cpp:96 | rollback | True | mutation_journal | ++p.revision;p.resolved_value=UNKNOWN;p.resolved_source=EvidenceSource::UNKNOWN; |
| src1.6.7/state_mutation.cpp:97 | rollback | True | mutation_journal | p.resolved_verified=false;p.dependency_count=0;p.support_constraint_index=UNKNOWN; |
| src1.6.7/state_mutation.cpp:98 | rollback | True | mutation_journal | p.supporting_constraints.clear(); |
| src1.6.7/state_mutation.cpp:101 | rollback | False | mutation_journal | withdraw(w.locationProvenance[r.id]);withdraw(w.insideProvenance[r.id]);withdraw(w.containerProvenance[r.id]); |
| src1.6.7/state_mutation.cpp:102 | rollback | True | mutation_journal | w.objectLocationVerified[r.id]=w.objectInsideVerified[r.id]=w.containerStateVerified[r.id]=false; |
| src1.6.7/state_mutation.cpp:103 | rollback | True | mutation_journal | w.objectLocationSource[r.id]=w.objectInsideSource[r.id]=w.containerStateSource[r.id]=EvidenceSource::UNKNOWN; |
| src1.6.7/state_mutation.cpp:104 | rollback | True | mutation_journal | w.objectLocationInferredByMustNear[r.id]=false; |
| src1.6.7/state_mutation.cpp:106 | rollback | False | mutation_journal | withdraw(w.holdProvenance);withdraw(w.plateProvenance); |
| src1.6.7/state_mutation.cpp:108 | rollback | True | mutation_journal | w.posSensedFlag[r.loc]=false; |
| src1.6.7/state_mutation.cpp:109 | rollback | False | mutation_journal | w.locationSensedObjects[r.loc].object_ids.clear(); |
| src1.6.7/state_mutation.cpp:110 | rollback | False | mutation_journal | w.locationSensedObjects[r.loc].has_container=false; |
| src1.6.7/state_mutation.cpp:111 | rollback | False | mutation_journal | w.locationSensedObjects[r.loc].container_id=NONE; |
| src1.6.7/state_mutation.cpp:116 | rollback | True | mutation_journal | if(w.constraint_eligible.size()!=count && eligible.size()==count) w.constraint_eligible.swap(eligible); |
| src1.6.7/state_mutation.cpp:117 | rollback | True | mutation_journal | if(w.constraint_uncertain.size()!=count && uncertain.size()==count) w.constraint_uncertain.swap(uncertain); |
| src1.6.7/state_mutation.cpp:118 | rollback | False | mutation_journal | std::fill(w.constraint_uncertain.begin(),w.constraint_uncertain.end(),true); |
| src1.6.7/state_mutation.cpp:124 | PrepareActionState | False | mutation_journal | active_mutation->touch(0);active_mutation->sensed(location); |
| src1.6.7/state_mutation.cpp:126 | PrepareActionState | False | mutation_journal | if(hold) active_mutation->touch(hold->id); |
| src1.6.7/state_mutation.cpp:127 | PrepareActionState | False | mutation_journal | if(plate) active_mutation->touch(plate->id); |
| src1.6.7/state_mutation.cpp:132 | PrepareActionState | False | mutation_journal | active_mutation->sensed(objects[id]->location); |
| src1.6.7/state_mutation.cpp:134 | PrepareActionState | False | mutation_journal | for(const auto& item:c->smallObjectsInside) if(item) active_mutation->touch(item->id); |
| src1.6.7/state_mutation.cpp:141 | StageStateValue | True | mutation_journal | if (field==StateField::LOCATION) objects[id]->location=value; |
| src1.6.7/state_mutation.cpp:143 | StageStateValue | True | mutation_journal | if (auto s=dynamic_pointer_cast<SmallObject>(objects[id])) s->inside=value; |
| src1.6.7/state_mutation.cpp:145 | StageStateValue | True | mutation_journal | if (auto c=dynamic_pointer_cast<Container>(objects[id])) c->isOpen=value; |
| src1.6.7/state_mutation.cpp:152 | AddContainerMembership | True | mutation_journal | container->smallObjectsInside.push_back(item); |
| src1.6.7/terminal_checker.cpp:26 | declaration/inline | False | declaration | // revision shortcut, or change to recursive qualification is involved. |
| src1.6.7/terminal_checker.cpp:69 | evaluatePair | False | read_access | const auto robot_location = [&]() { return hypothesis?world.location:facts.value(StateField::LOCATION,0); }; |
| src1.6.7/terminal_checker.cpp:70 | evaluatePair | False | read_access | const auto hand = [&]() { return hypothesis?world.hold_id:facts.value(StateField::HOLD,0); }; |
| src1.6.7/terminal_checker.cpp:71 | evaluatePair | False | read_access | const auto tray = [&]() { return hypothesis?world.plate_id:facts.value(StateField::PLATE,0); }; |
| src1.6.7/terminal_checker.cpp:82 | evaluatePair | False | read_access | (in.source==EvidenceSource::SENSE \|\| in.source==EvidenceSource::ACTION_SUCCESS); |
| src1.6.7/terminal_checker.cpp:84 | evaluatePair | False | read_access | const auto locationValue = [&](const std::shared_ptr<Object>& o) { return !o?UNKNOWN:hypothesis?o->location:facts.value(StateField::LOCATION,o->id); }; |
| src1.6.7/terminal_checker.cpp:85 | evaluatePair | False | read_access | const auto insideValue = [&](const std::shared_ptr<SmallObject>& o) { return !o?UNKNOWN:hypothesis?o->inside:facts.value(StateField::INSIDE,o->id); }; |
| src1.6.7/terminal_checker.cpp:86 | evaluatePair | False | read_access | const auto containerValue = [&](const std::shared_ptr<Container>& o) { return !o?UNKNOWN:hypothesis?o->isOpen:facts.value(StateField::CONTAINER_STATE,o->id); }; |
| src1.6.7/terminal_checker.cpp:89 | evaluatePair | False | read_access | if(hypothesis) { if(o->id==0) return world.location; |
| src1.6.7/terminal_checker.cpp:90 | evaluatePair | False | read_access | return o->id<world.score_locations.size()?world.score_locations[o->id]:o->location; } |
| src1.6.7/terminal_checker.cpp:92 | evaluatePair | False | read_access | if(world.stage==1 && o->id>0) return loc!=UNKNOWN && o->id<world.score_locations.size()?world.score_locations[o->id]:UNKNOWN; |
| src1.6.7/terminal_checker.cpp:136 | evaluatePair | False | read_access | if (behave == "putin" \|\| behave == "inside" \|\| behave == "in") { |
| src1.6.7/terminal_checker.cpp:150 | evaluatePair | False | read_access | if (behave == "puton" \|\| behave == "on" \|\| behave == "near" \|\| |
| src1.6.7/terminal_checker.cpp:177 | evaluatePair | False | read_access | if (behave == "plate") { |
| src1.6.7/terminal_checker.cpp:184 | evaluatePair | False | read_access | if (behave == "hold") { |
| src1.6.7/terminal_checker.cpp:247 | evaluateConstraint | False | declaration | // Each grounded constraint must hold; negate BEFORE combining bindings. |
| src1.6.7/terminal_checker.cpp:301 | evaluateConstraints | True | local_result | result.constraint_eligible.reserve(constraint_count); |
| src1.6.7/terminal_checker.cpp:306 | evaluateConstraints | False | read_access | const bool has_ledger = world.constraint_eligible.size() == |
| src1.6.7/terminal_checker.cpp:313 | evaluateConstraints | False | read_access | const bool eligible = !has_ledger \|\| world.constraint_eligible[result.constraints.size()-1]; |
| src1.6.7/terminal_checker.cpp:314 | evaluateConstraints | True | local_result | result.constraint_eligible.push_back(eligible); |
| src1.6.7/terminal_checker.cpp:315 | evaluateConstraints | False | read_access | const bool certain = !has_ledger \|\| world.constraint_uncertain.size() != world.constraint_eligible.size() \|\| |
| src1.6.7/terminal_checker.cpp:316 | evaluateConstraints | False | read_access | !world.constraint_uncertain[result.constraints.size()-1]; |
| src1.6.7/terminal_checker.cpp:326 | evaluateConstraints | False | read_access | const bool eligible = !has_ledger \|\| world.constraint_eligible[result.constraints.size()-1]; |
| src1.6.7/terminal_checker.cpp:327 | evaluateConstraints | True | local_result | result.constraint_eligible.push_back(eligible); |
| src1.6.7/terminal_checker.cpp:328 | evaluateConstraints | False | read_access | const bool certain = !has_ledger \|\| world.constraint_uncertain.size() != world.constraint_eligible.size() \|\| |
| src1.6.7/terminal_checker.cpp:329 | evaluateConstraints | False | read_access | !world.constraint_uncertain[result.constraints.size()-1]; |
| src1.6.7/terminal_checker.cpp:339 | evaluateConstraints | False | read_access | const bool eligible = !has_ledger \|\| world.constraint_eligible[result.constraints.size()-1]; |
| src1.6.7/terminal_checker.cpp:340 | evaluateConstraints | True | local_result | result.constraint_eligible.push_back(eligible); |
| src1.6.7/terminal_checker.cpp:341 | evaluateConstraints | False | read_access | const bool certain = !has_ledger \|\| world.constraint_uncertain.size() != world.constraint_eligible.size() \|\| |
| src1.6.7/terminal_checker.cpp:342 | evaluateConstraints | False | read_access | !world.constraint_uncertain[result.constraints.size()-1]; |
| src1.6.7/terminal_checker.hpp:29 | declaration/inline | False | declaration | std::vector<bool> constraint_eligible; |
| src1.6.7/tests/canonical_baseline_probe.cpp:17 | main | False | test_fixture | assert(w->ParseEnv("(hold 0) (plate 0) (at 0 1) (sort 1 human) (size 1 big) (at 1 1) " |
| src1.6.7/tests/canonical_baseline_probe.cpp:23 | main | False | test_fixture | w->MarkDirectLocationEvidence(2,true,EvidenceSource::SENSE);w->MarkUnresolved(StateField::LOCATION,2); |
| src1.6.7/tests/canonical_baseline_probe.cpp:24 | main | False | test_fixture | assert(!w->IsLocationVerified(2)); |
| src1.6.7/tests/canonical_baseline_probe.cpp:26 | main | True | test_fixture | w->MarkDirectLocationEvidence(2,true,EvidenceSource::SENSE);c->location=1; |
| src1.6.7/tests/canonical_baseline_probe.cpp:37 | main | False | test_fixture | w->notnot_infoConstrains={T("inside",s,c)};w->ApplyMustInConstraintCorrection(); |
| src1.6.7/tests/canonical_baseline_probe.cpp:38 | main | False | test_fixture | w->not_infoConstrains={T("inside",s,c)};w->ApplyMustInConstraintCorrection(); |
| src1.6.7/tests/canonical_baseline_probe.cpp:39 | main | False | test_fixture | assert(!w->IsInsideVerified(3)); |
| src1.6.7/tests/canonical_baseline_probe.cpp:41 | main | False | test_fixture | w->notnot_infoConstrains={T("inside",s,c)};w->ApplyMustInConstraintCorrection(); |
| src1.6.7/tests/canonical_baseline_probe.cpp:42 | main | True | test_fixture | c->location=5;w->MarkDirectLocationEvidence(2,true,EvidenceSource::SENSE); |
| src1.6.7/tests/canonical_baseline_probe.cpp:44 | main | True | test_fixture | w->constraint_uncertain={true};assert(!w->ResolvedState(StateField::LOCATION,3).present); |
| src1.6.7/tests/canonical_baseline_probe.cpp:48 | main | False | test_fixture | w->SetHold(s,EvidenceSource::INITIAL);assert(ScoreSemanticsTestAccess::Move(*w)); |
| src1.6.7/tests/canonical_baseline_probe.cpp:51 | main | False | test_fixture | w->MarkDirectLocationEvidence(2,true,EvidenceSource::CONSTRAINT_HEURISTIC); |
| src1.6.7/tests/canonical_baseline_probe.cpp:54 | main | True | test_fixture | w->MarkDirectLocationEvidence(2,true,EvidenceSource::SENSE);c->location=1; |
| src1.6.7/tests/canonical_baseline_probe.cpp:55 | main | False | test_fixture | w->notnot_infoConstrains={T("inside",s,c)};w->ApplyMustInConstraintCorrection(); |
| src1.6.7/tests/canonical_baseline_probe.cpp:58 | main | True | test_fixture | w->stage=1;w->MarkDirectLocationEvidence(2,true,EvidenceSource::SENSE);c->location=1; |
| src1.6.7/tests/canonical_baseline_probe.cpp:59 | main | False | test_fixture | w->ParseInfo(T("on",s,c));assert(w->ResolvedState(StateField::LOCATION,3).value==5); |
| src1.6.7/tests/canonical_baseline_probe.cpp:61 | main | True | test_fixture | s->inside=NONE;w->SetInsideEvidence(3,true,EvidenceSource::SENSE); |
| src1.6.7/tests/canonical_baseline_probe.cpp:62 | main | True | test_fixture | s->inside=2;c->smallObjectsInside.push_back(s); |
| src1.6.7/tests/canonical_baseline_probe.cpp:66 | main | True | test_fixture | s->inside=1;w->SetInsideEvidence(3,true,EvidenceSource::SENSE); |
| src1.6.7/tests/canonical_state_tests.cpp:29 | World | False | test_fixture | assert(w->ParseEnv("(hold 0) (plate 0) (at 0 1) (sort 1 human) (size 1 big) (at 1 1) " |
| src1.6.7/tests/canonical_state_tests.cpp:31 | World | False | test_fixture | "(sort 3 cup) (size 3 small) (inside 3 2) (sort 4 table) (size 4 big) (at 4 5)")); |
| src1.6.7/tests/canonical_state_tests.cpp:38 | main | False | test_fixture | const auto fact=[&](StateField f,unsigned id,int value,EvidenceSource source=EvidenceSource::SENSE) {w->ApplyStateValue(f,id,value,true,source);}; |
| src1.6.7/tests/canonical_state_tests.cpp:41 | main | True | test_fixture | w->objectLocationVerified[2]=true; // deliberate stale compatibility |
| src1.6.7/tests/canonical_state_tests.cpp:42 | main | False | test_fixture | assert(c->location==1 && w->FactLocation(2)==UNKNOWN && !w->IsLocationVerified(2)); |
| src1.6.7/tests/canonical_state_tests.cpp:44 | main | True | test_fixture | fact(StateField::LOCATION,2,1);w->objects[4]->location=UNKNOWN; |
| src1.6.7/tests/canonical_state_tests.cpp:46 | main | True | test_fixture | assert(w->FactLocation(4)==1);w->constraint_eligible={test!=2};w->constraint_uncertain={test!=2}; |
| src1.6.7/tests/canonical_state_tests.cpp:48 | main | False | test_fixture | assert(w->objects[4]->location==1 && w->FactLocation(4)==UNKNOWN); |
| src1.6.7/tests/canonical_state_tests.cpp:55 | main | False | test_fixture | w->tasks={Task("goto",c)};assert(c->location==w->location); |
| src1.6.7/tests/canonical_state_tests.cpp:59 | main | True | test_fixture | if(test==12) { fact(StateField::LOCATION,2,5);c->location=1; |
| src1.6.7/tests/canonical_state_tests.cpp:63 | main | False | test_fixture | assert(c->location==5 && s->inside==NONE && c->isOpen==1); |
| src1.6.7/tests/canonical_state_tests.cpp:67 | main | True | test_fixture | fact(StateField::LOCATION,2,5);c->location=1; |
| src1.6.7/tests/canonical_state_tests.cpp:68 | main | True | test_fixture | assert(w->FactLocation(2)==5);w->objectLocationVerified[2]=false; |
| src1.6.7/tests/canonical_state_tests.cpp:73 | main | False | test_fixture | assert(w->plate==s && !w->hold && w->DebugStateConsistency().empty()); |
| src1.6.7/tests/canonical_state_tests.cpp:75 | main | True | test_fixture | c->isOpen=1;w->containerStateVerified[2]=true; |
| src1.6.7/tests/canonical_state_tests.cpp:80 | main | False | test_fixture | w->ApplyStateValue(StateField::LOCATION,2,5,false,EvidenceSource::ASK_ANSWER); |
| src1.6.7/tests/canonical_state_tests.cpp:81 | main | False | test_fixture | assert(c->location==5 && w->HasContradictoryEvidence(StateField::LOCATION,2)); |
| src1.6.7/tests/canonical_state_tests.cpp:94 | main | True | test_fixture | fact(StateField::LOCATION,2,1);w->objects[4]->location=UNKNOWN; |
| src1.6.7/tests/canonical_state_tests.cpp:96 | main | True | test_fixture | w->constraint_eligible={true};w->constraint_uncertain={false}; |
| src1.6.7/tests/canonical_state_tests.cpp:102 | main | False | test_fixture | w->SetPlate(s,EvidenceSource::INITIAL);w->tasks={Task("pickup",s)}; |
| src1.6.7/tests/canonical_state_tests.cpp:106 | main | True | test_fixture | fact(StateField::LOCATION,2,1);c->location=5; |
| src1.6.7/tests/canonical_state_tests.cpp:108 | main | False | test_fixture | w->ApplyStateValue(StateField::LOCATION,2,1,true,EvidenceSource::SENSE); |
| src1.6.7/tests/canonical_state_tests.cpp:111 | main | True | test_fixture | s->location=1;s->inside=NONE;w->tasks={Task("give",s)};w->SetActionResults({false,false,false,false}); |
| src1.6.7/tests/canonical_state_tests.cpp:114 | main | True | test_fixture | s->inside=NONE;w->tasks={Task("putin",s,c)}; |
| src1.6.7/tests/canonical_state_tests.cpp:117 | main | False | test_fixture | w->notnot_infoConstrains={Task("inside",s,c)};w->ApplyMustInConstraintCorrection(); |
| src1.6.7/tests/canonical_state_tests.cpp:119 | main | False | test_fixture | assert(w->FactLocation(3)==1 && w->Provenance(StateField::LOCATION,3).dependency_count==2); |
| src1.6.7/tests/canonical_state_tests.cpp:120 | main | True | test_fixture | w->constraint_uncertain={true};assert(w->FactLocation(3)==UNKNOWN); |
| src1.6.7/tests/canonical_state_tests.cpp:122 | main | False | test_fixture | w->notnot_infoConstrains={Task("inside",s,c)};w->ApplyMustInConstraintCorrection(); |
| src1.6.7/tests/canonical_state_tests.cpp:123 | main | False | test_fixture | w->not_infoConstrains={Task("inside",s,c)};w->ApplyMustInConstraintCorrection(); |
| src1.6.7/tests/canonical_state_tests.cpp:124 | main | False | test_fixture | assert(s->inside==UNKNOWN && w->FactInside(3)==UNKNOWN && !w->IsInsideVerified(3)); |
| src1.6.7/tests/canonical_state_tests.cpp:130 | main | False | test_fixture | assert(!w->ResolvedState(StateField::LOCATION,2).present); // weak support revision matches, but is not fact |
| src1.6.7/tests/canonical_state_tests.cpp:132 | main | False | test_fixture | w->ApplyStateValue(StateField::LOCATION,2,1,true,EvidenceSource::CONSTRAINT_HEURISTIC); |
| src1.6.7/tests/canonical_state_tests.cpp:139 | main | False | test_fixture | fact(StateField::INSIDE,3,2,EvidenceSource::CONSTRAINT_DERIVED); |
| src1.6.7/tests/canonical_state_tests.cpp:142 | main | False | test_fixture | w->SetHold(s,EvidenceSource::INITIAL); |
| src1.6.7/tests/canonical_state_tests.cpp:144 | main | False | test_fixture | assert(s->location==5 && w->FactLocation(3)==UNKNOWN); |
| src1.6.7/tests/canonical_state_tests.cpp:148 | main | True | test_fixture | w->SetHold(s);w->plateProvenance=w->holdProvenance;w->plate_id=3;w->plate=s; |
| src1.6.7/tests/canonical_state_tests.cpp:154 | main | False | test_fixture | assert(w->FactLocation(3)==UNKNOWN); // matching revision of an invalid state is no support |
| src1.6.7/tests/canonical_state_tests.cpp:157 | main | False | test_fixture | assert(w->score_locations[2]==1 && w->ScoreFactLocation(2)==UNKNOWN); |
| src1.6.7/tests/canonical_state_tests.cpp:161 | main | True | test_fixture | fact(StateField::LOCATION,2,5);c->location=1; |
| src1.6.7/tests/canonical_state_tests.cpp:162 | main | False | test_fixture | w->notnot_infoConstrains={Task("inside",s,c)};w->ApplyMustInConstraintCorrection(); |
| src1.6.7/tests/canonical_state_tests.cpp:163 | main | False | test_fixture | assert(w->FactLocation(3)==5 && s->location==5); |
| src1.6.7/tests/canonical_state_tests.cpp:166 | main | True | test_fixture | w->stage=1;fact(StateField::LOCATION,2,5);c->location=1; |
| src1.6.7/tests/canonical_state_tests.cpp:167 | main | False | test_fixture | w->ParseInfo(Task("on",s,c));assert(w->FactLocation(3)==5); |
| src1.6.7/tests/canonical_state_tests.cpp:169 | main | False | test_fixture | w->ParseInfo(Task("inside",s,c));assert(w->FactLocation(3)==5); |
| src1.6.7/tests/canonical_state_tests.cpp:171 | main | True | test_fixture | fact(StateField::INSIDE,3,NONE);s->inside=2;c->smallObjectsInside.push_back(s); |
| src1.6.7/tests/canonical_state_tests.cpp:174 | main | False | test_fixture | assert(w->FactLocation(3)==UNKNOWN); // cache membership cannot prove inside |
| src1.6.7/tests/deadline_sensitivity_tests.cpp:14 | main | False | test_fixture | assert(w->ParseEnv("(hold 0) (plate 0) (at 0 1) (sort 1 cupboard) (size 1 big) (type 1 container) (at 1 1) (opened 1)")); |
| src1.6.7/tests/guarded_decision_tests.cpp:19 | Run | False | test_fixture | "(hold 0) (plate 0) (at 0 1) " |
| src1.6.7/tests/guarded_decision_tests.cpp:39 | declaration/inline | False | test_fixture | "(hold 0) (plate 0) (at 0 1) " |
| src1.6.7/tests/input_safety_tests.cpp:54 | main | False | test_fixture | assert(world->ParseEnv("(inside 2 99) (at 0 1)")); |
| src1.6.7/tests/input_safety_tests.cpp:55 | main | False | test_fixture | assert(std::dynamic_pointer_cast<SmallObject>(world->objects[2])->inside == UNKNOWN); |
| src1.6.7/tests/input_safety_tests.cpp:56 | main | False | test_fixture | assert(world->ParseEnv("(hold 3) (at 0 1)")); |
| src1.6.7/tests/input_safety_tests.cpp:57 | main | False | test_fixture | assert(world->hold_id == NONE && !world->hold); |
| src1.6.7/tests/input_safety_tests.cpp:62 | main | False | test_fixture | "(:domain (hold 0) (sort 5 bowl) (size 5 small) (at 5 5))")); |
| src1.6.7/tests/input_safety_tests.cpp:64 | main | False | test_fixture | assert(world->objects[5]->sort == "bowl" && world->objects[5]->location == 5); |
| src1.6.7/tests/input_safety_tests.cpp:66 | main | False | test_fixture | // The largest supported sparse id is bounded and all object/location |
| src1.6.7/tests/interval_gate_tests.cpp:27 | main | False | test_fixture | assert(w->ParseEnv("(hold 0) (plate 0) (at 0 1) (sort 1 cupboard) " |
| src1.6.7/tests/interval_gate_tests.cpp:32 | main | True | test_fixture | w->constraint_uncertain[0] = true; |
| src1.6.7/tests/interval_gate_tests.cpp:95 | main | False | test_fixture | w->ApplyStateValue(StateField::CONTAINER_STATE,1,1,true,EvidenceSource::SENSE); |
| src1.6.7/tests/legal_preservation_tests.cpp:19 | main | False | test_fixture | assert(std::dynamic_pointer_cast<Container>(w->objects[3])->isOpen == 0); |
| src1.6.7/tests/mutation_failure_tests.cpp:35 | World | False | test_fixture | assert(w->ParseEnv("(hold 0) (plate 0) (at 0 1) (sort 1 human) (size 1 big) (at 1 1) " |
| src1.6.7/tests/mutation_failure_tests.cpp:37 | World | False | test_fixture | "(sort 3 cup) (size 3 small) (inside 3 2) " |
| src1.6.7/tests/mutation_failure_tests.cpp:67 | main | False | test_fixture | if(test==0) w->ApplyStateValue(StateField::INSIDE,3,4,true,EvidenceSource::SENSE); |
| src1.6.7/tests/mutation_failure_tests.cpp:68 | main | False | test_fixture | else if(test==1) w->MarkDirectLocationEvidence(2,true,EvidenceSource::CONSTRAINT_DERIVED); |
| src1.6.7/tests/mutation_failure_tests.cpp:69 | main | False | test_fixture | else if(test==2) w->ParseInfo(T("inside",small,w->objects[4])); |
| src1.6.7/tests/mutation_failure_tests.cpp:74 | main | False | test_fixture | else if(test==17) {w->notnot_infoConstrains={T("inside",small,w->objects[4])};w->ApplyMustInConstraintCorrection();} |
| src1.6.7/tests/mutation_failure_tests.cpp:75 | main | False | test_fixture | else if(test==18) {w->ApplyStateValue(StateField::LOCATION,2,5,true,EvidenceSource::SENSE);} |
| src1.6.7/tests/parse_snapshot.cpp:9 | snapshot | False | test_fixture | std::cout << "SNAP " << phase << " robot=" << w.location << ',' << w.hold_id << ',' << w.plate_id << '\n'; |
| src1.6.7/tests/parse_snapshot.cpp:11 | snapshot | False | test_fixture | std::cout<<"SNAP object "<<o->id<<' '<<o->sort<<' '<<o->location; |
| src1.6.7/tests/parse_snapshot.cpp:15 | snapshot | False | test_fixture | if(s) std::cout<<" small "<<s->color<<' '<<s->inside<<' '<<s->on; |
| src1.6.7/tests/parse_snapshot.cpp:16 | snapshot | False | test_fixture | else if(c) std::cout<<" container "<<c->isOpen; |
| src1.6.7/tests/question_preflight_tests.cpp:12 | declaration/inline | False | test_fixture | "(hold 0) (plate 0) (at 0 1) " |
| src1.6.7/tests/question_preflight_tests.cpp:91 | GotoAndConflicts | False | test_fixture | // Different IDs at the SAME location must not be merged. |
| src1.6.7/tests/question_preflight_tests.cpp:115 | CanonicalRelationsAndSets | False | test_fixture | Not(Info("inside X Y", "(id X 2) (id Y 3)")) + |
| src1.6.7/tests/question_preflight_tests.cpp:146 | MalformedConstraintRecovery | False | test_fixture | "(:cons_not (:info (inside X) (:cond (id X 2))))"}) { |
| src1.6.7/tests/question_preflight_tests.cpp:166 | WorldSafetyAndStage2Unknowns | True | test_fixture | w->objects[2]->location = UNKNOWN; |
| src1.6.7/tests/question_preflight_tests.cpp:167 | WorldSafetyAndStage2Unknowns | True | test_fixture | w->objects[3]->location = UNKNOWN; |
| src1.6.7/tests/question_preflight_tests.cpp:168 | WorldSafetyAndStage2Unknowns | True | test_fixture | std::dynamic_pointer_cast<Container>(w->objects[3])->isOpen = UNKNOWN; |
| src1.6.7/tests/question_preflight_tests.cpp:170 | WorldSafetyAndStage2Unknowns | True | test_fixture | w->objects[3]->location = 1; // Stage 2 err may collide with human |
| src1.6.7/tests/question_preflight_tests.cpp:222 | RealPlanGate | False | test_fixture | assert(w->TestPlatformCalls() == 0); // no correction/Cons_plan/action on unsafe world |
| src1.6.7/tests/recovery_evidence_tests.cpp:30 | declaration/inline | False | test_fixture | "(hold 0) (plate 0) (at 0 2) " |
| src1.6.7/tests/recovery_evidence_tests.cpp:40 | main | False | test_fixture | // A: a guaranteed initial must-inside repairs inside, but the cupboard's |
| src1.6.7/tests/recovery_evidence_tests.cpp:41 | main | False | test_fixture | // unverified initial location does not become a Sense-quality book location. |
| src1.6.7/tests/recovery_evidence_tests.cpp:42 | main | True | test_fixture | auto inside = World(argv[1], 2, kitchen); |
| src1.6.7/tests/recovery_evidence_tests.cpp:43 | main | False | test_fixture | Instruction must_in = Unary("inside", inside->objects[3]); |
| src1.6.7/tests/recovery_evidence_tests.cpp:44 | main | False | test_fixture | must_in.Y.push_back(inside->objects[2]); |
| src1.6.7/tests/recovery_evidence_tests.cpp:45 | main | False | test_fixture | inside->notnot_infoConstrains.push_back(must_in); |
| src1.6.7/tests/recovery_evidence_tests.cpp:46 | main | False | test_fixture | inside->ApplyMustInConstraintCorrection(); |
| src1.6.7/tests/recovery_evidence_tests.cpp:47 | main | False | test_fixture | assert(inside->IsInsideVerified(3)); |
| src1.6.7/tests/recovery_evidence_tests.cpp:48 | main | False | test_fixture | assert(inside->InsideSource(3) == EvidenceSource::CONSTRAINT_DERIVED); |
| src1.6.7/tests/recovery_evidence_tests.cpp:49 | main | False | test_fixture | assert(!inside->IsLocationVerified(3)); |
| src1.6.7/tests/recovery_evidence_tests.cpp:50 | main | False | test_fixture | assert(inside->LocationSource(3) == EvidenceSource::CONSTRAINT_HEURISTIC); |
| src1.6.7/tests/recovery_evidence_tests.cpp:51 | main | False | test_fixture | Instruction putin = Unary("putin", inside->objects[3]); |
| src1.6.7/tests/recovery_evidence_tests.cpp:52 | main | False | test_fixture | putin.Y.push_back(inside->objects[2]); |
| src1.6.7/tests/recovery_evidence_tests.cpp:53 | main | False | test_fixture | assert(inside->ZeroActionPreCheck(putin)); |
| src1.6.7/tests/recovery_evidence_tests.cpp:58 | main | False | test_fixture | assert(closed->ContainerSource(2) == EvidenceSource::INITIAL); |
| src1.6.7/tests/recovery_evidence_tests.cpp:59 | main | False | test_fixture | assert(!closed->IsContainerStateVerified(2)); |
| src1.6.7/tests/recovery_evidence_tests.cpp:62 | main | False | test_fixture | assert(closed->IsContainerStateVerified(2)); |
| src1.6.7/tests/recovery_evidence_tests.cpp:63 | main | False | test_fixture | assert(closed->ContainerSource(2) == EvidenceSource::CONSTRAINT_DERIVED); |
| src1.6.7/tests/recovery_evidence_tests.cpp:71 | main | False | test_fixture | assert(explicit_info->ContainerSource(2) == EvidenceSource::EXPLICIT_INFO); |
| src1.6.7/tests/recovery_evidence_tests.cpp:72 | main | False | test_fixture | // Stage 2 :info is a received claim; the SDK does not verify its truth. |
| src1.6.7/tests/recovery_evidence_tests.cpp:73 | main | False | test_fixture | assert(!explicit_info->IsContainerStateVerified(2)); |
| src1.6.7/tests/recovery_evidence_tests.cpp:77 | main | False | test_fixture | // C: conflicting initial locations do not give either endpoint a trusted |
| src1.6.7/tests/recovery_evidence_tests.cpp:78 | main | False | test_fixture | // must-near inference, even if the robot stands at one reported location. |
| src1.6.7/tests/recovery_evidence_tests.cpp:80 | main | False | test_fixture | "(hold 0) (plate 0) (at 0 4) " |
| src1.6.7/tests/recovery_evidence_tests.cpp:88 | main | False | test_fixture | assert(!conflict->IsLocationVerified(3)); |
| src1.6.7/tests/recovery_evidence_tests.cpp:92 | main | False | test_fixture | "(hold 0) (plate 0) (at 0 2) " |
| src1.6.7/tests/recovery_evidence_tests.cpp:100 | main | False | test_fixture | assert(weak->objects[3]->location == 2); |
| src1.6.7/tests/recovery_evidence_tests.cpp:101 | main | False | test_fixture | assert(weak->LocationSource(3) == EvidenceSource::CONSTRAINT_HEURISTIC); |
| src1.6.7/tests/recovery_evidence_tests.cpp:102 | main | False | test_fixture | assert(!weak->IsLocationVerified(3)); |
| src1.6.7/tests/recovery_evidence_tests.cpp:108 | main | False | test_fixture | "(hold 0) (plate 0) (at 0 2) " |
| src1.6.7/tests/recovery_evidence_tests.cpp:114 | main | False | test_fixture | changed->ApplyStateValue(StateField::LOCATION,2,4,true,EvidenceSource::SENSE); |
| src1.6.7/tests/recovery_evidence_tests.cpp:115 | main | True | test_fixture | changed->score_locations[2] = 4; // fixture changes the authoritative at fact |
| src1.6.7/tests/recovery_evidence_tests.cpp:126 | main | False | test_fixture | assert(changed->location == 2 && changed->objects[2]->location == 4); |
| src1.6.7/tests/recovery_evidence_tests.cpp:142 | main | False | test_fixture | // E: an ineligible task cannot make Stop depend on the first stale list. |
| src1.6.7/tests/recovery_evidence_tests.cpp:145 | main | False | test_fixture | "(hold 0) (plate 0) (at 0 2) " |
| src1.6.7/tests/recovery_evidence_tests.cpp:149 | main | False | test_fixture | "(hold 0) (plate 0) (at 0 2) (sort 1 human) (size 1 big) (at 1 1) " |
| src1.6.7/tests/score_semantics_tests.cpp:28 | declaration/inline | False | test_fixture | "(hold 0) (plate 0) (at 0 1) " |
| src1.6.7/tests/score_semantics_tests.cpp:31 | declaration/inline | False | test_fixture | "(sort 3 cup) (size 3 small) (color 3 red) (inside 3 2) (at 3 1) " |
| src1.6.7/tests/score_semantics_tests.cpp:124 | main | False | test_fixture | carried.replace(carried.find("(hold 0)"), 8, "(hold 3)"); |
| src1.6.7/tests/score_semantics_tests.cpp:125 | main | False | test_fixture | carried.replace(carried.find("(inside 3 2)"), 12, ""); |
| src1.6.7/tests/score_semantics_tests.cpp:127 | main | False | test_fixture | "(:cons_notnot (:info (on X Y) (:cond (sort X cup) (color X red) (sort Y table))))", "m", 56, 56); |
| src1.6.7/tests/score_semantics_tests.cpp:146 | main | False | test_fixture | assert(w->constraint_uncertain[0]); |
| src1.6.7/tests/score_semantics_tests.cpp:147 | main | False | test_fixture | w->ApplyStateValue(StateField::CONTAINER_STATE,2,1,true,EvidenceSource::SENSE); |
| src1.6.7/tests/score_semantics_tests.cpp:149 | main | False | test_fixture | assert(w->constraint_uncertain[0]); // recovery cannot prove past truth |
| src1.6.7/tests/score_semantics_tests.cpp:151 | main | False | test_fixture | const auto saved = w->constraint_uncertain; |
| src1.6.7/tests/score_semantics_tests.cpp:153 | main | False | test_fixture | assert(w->constraint_uncertain == saved); |
| src1.6.7/tests/score_semantics_tests.cpp:154 | main | True | test_fixture | w->constraint_eligible[0] = false; |
| src1.6.7/tests/score_semantics_tests.cpp:155 | main | True | test_fixture | w->constraint_uncertain[0] = false; |
| src1.6.7/tests/score_semantics_tests.cpp:156 | main | False | test_fixture | w->ApplyStateValue(StateField::CONTAINER_STATE,2,0,true,EvidenceSource::CONSTRAINT_DERIVED); |
| src1.6.7/tests/state_invariant_tests.cpp:42 | main | False | test_fixture | assert(w->ParseEnv("(hold 0) (plate 0) (at 0 1) " |
| src1.6.7/tests/state_invariant_tests.cpp:45 | main | False | test_fixture | "(sort 3 cup) (size 3 small) (color 3 red) (inside 3 2) " |
| src1.6.7/tests/state_invariant_tests.cpp:51 | main | False | test_fixture | assert(a.id==7 && a.location==11 && b.id==8 && b.location==12); |
| src1.6.7/tests/state_invariant_tests.cpp:52 | main | False | test_fixture | assert(d.id==9 && d.location==13); |
| src1.6.7/tests/state_invariant_tests.cpp:55 | main | False | test_fixture | assert(c->location==w->location && w->IsLocationVerified(2)); |
| src1.6.7/tests/state_invariant_tests.cpp:56 | main | False | test_fixture | assert(s->location==c->location && !w->IsLocationVerified(3)); |
| src1.6.7/tests/state_invariant_tests.cpp:59 | main | False | test_fixture | assert(s->inside==NONE && c->smallObjectsInside.empty()); |
| src1.6.7/tests/state_invariant_tests.cpp:60 | main | False | test_fixture | assert(w->hold==s && w->hold_id==3); |
| src1.6.7/tests/state_invariant_tests.cpp:62 | main | False | test_fixture | assert(!w->hold && w->plate==s); |
| src1.6.7/tests/state_invariant_tests.cpp:64 | main | False | test_fixture | assert(s->location==5); |
| src1.6.7/tests/state_invariant_tests.cpp:66 | main | False | test_fixture | assert(!w->plate && w->hold==s); |
| src1.6.7/tests/state_invariant_tests.cpp:68 | main | False | test_fixture | assert(!w->hold && s->inside==NONE); |
| src1.6.7/tests/state_invariant_tests.cpp:70 | main | False | test_fixture | w->ParseInfo(Task("inside",s,w->objects[4])); |
| src1.6.7/tests/state_invariant_tests.cpp:71 | main | False | test_fixture | w->ParseInfo(Task("inside",s,w->objects[4])); |
| src1.6.7/tests/state_invariant_tests.cpp:73 | main | False | test_fixture | assert(c->smallObjectsInside.empty() && d->smallObjectsInside.size()==1); |
| src1.6.7/tests/state_invariant_tests.cpp:74 | main | False | test_fixture | w->ParseInfo(Task("on",s,w->objects[1])); |
| src1.6.7/tests/state_invariant_tests.cpp:75 | main | False | test_fixture | assert(d->smallObjectsInside.empty()); |
| src1.6.7/tests/state_invariant_tests.cpp:77 | main | False | test_fixture | assert(s->on==UNKNOWN \|\| s->on==NONE); |
| src1.6.7/tests/state_invariant_tests.cpp:79 | main | True | test_fixture | c->isOpen=UNKNOWN; c->location=w->location; w->SetHold(s); |
| src1.6.7/tests/state_invariant_tests.cpp:86 | main | False | test_fixture | int loc=w->location, sloc=s->location, in=s->inside, op=c->isOpen; |
| src1.6.7/tests/state_invariant_tests.cpp:87 | main | False | test_fixture | auto contents=c->smallObjectsInside; |
| src1.6.7/tests/state_invariant_tests.cpp:89 | main | False | test_fixture | assert(w->location==loc && s->location==sloc && s->inside==in); |
| src1.6.7/tests/state_invariant_tests.cpp:90 | main | False | test_fixture | assert(c->isOpen==op && c->smallObjectsInside==contents); |
| src1.6.7/tests/state_invariant_tests.cpp:93 | main | True | test_fixture | w->stage=1; c->location=w->location; s->location=w->location; |
| src1.6.7/tests/state_invariant_tests.cpp:94 | main | True | test_fixture | c->isOpen=1; w->tasks.push_back(Task("takeout",s,c)); |
| src1.6.7/tests/state_invariant_tests.cpp:95 | main | False | test_fixture | const auto before=c->smallObjectsInside; |
| src1.6.7/tests/state_invariant_tests.cpp:97 | main | False | test_fixture | assert(p.dry_run_succeeded && w->hold_id==NONE && s->inside==2); |
| src1.6.7/tests/state_invariant_tests.cpp:98 | main | False | test_fixture | assert(c->smallObjectsInside==before && w->TestPlatformCalls()==0); |
| src1.6.7/tests/state_invariant_tests.cpp:104 | main | True | test_fixture | c->location=1; s->location=1; w->SetSenseResult({2}); |
| src1.6.7/tests/state_invariant_tests.cpp:107 | main | False | test_fixture | assert(!w->IsLocationVerified(3)); |
| src1.6.7/tests/state_invariant_tests.cpp:111 | main | True | test_fixture | w->objects[4]->location=UNKNOWN; |
| src1.6.7/tests/state_invariant_tests.cpp:113 | main | False | test_fixture | assert(w->objects[4]->location==4); |
| src1.6.7/tests/state_invariant_tests.cpp:114 | main | True | test_fixture | c->location=1; w->objectLocationVerified[2]=true; |
| src1.6.7/tests/state_invariant_tests.cpp:115 | main | True | test_fixture | w->objectLocationInferredByMustNear[2]=false; |
| src1.6.7/tests/state_invariant_tests.cpp:116 | main | True | test_fixture | w->objectLocationSource[2]=EvidenceSource::SENSE; |
| src1.6.7/tests/state_invariant_tests.cpp:118 | main | False | test_fixture | assert(w->objects[4]->location==UNKNOWN); |
| src1.6.7/tests/state_invariant_tests.cpp:119 | main | False | test_fixture | assert(!w->IsLocationVerified(4)); |
| src1.6.7/tests/state_invariant_tests.cpp:121 | main | True | test_fixture | s->inside=UNKNOWN; s->location=UNKNOWN; |
| src1.6.7/tests/state_invariant_tests.cpp:122 | main | False | test_fixture | w->SetAskResult("inside(3,4)"); |
| src1.6.7/tests/state_invariant_tests.cpp:125 | main | False | test_fixture | assert(!w->IsInsideVerified(3) && !w->IsLocationVerified(3)); |
| src1.6.7/tests/state_invariant_tests.cpp:128 | main | True | test_fixture | c->location=1; s->location=1; c->isOpen=UNKNOWN; |
| src1.6.7/tests/state_invariant_tests.cpp:130 | main | False | test_fixture | assert(s->inside==2 && !w->IsInsideVerified(3)); |
| src1.6.7/tests/state_invariant_tests.cpp:136 | main | False | test_fixture | assert(w->hold==s && s->inside==NONE && c->smallObjectsInside.empty()); |
| src1.6.7/tests/state_invariant_tests.cpp:138 | main | False | test_fixture | assert(!w->hold && s->inside==2 && c->smallObjectsInside.size()==1); |
| src1.6.7/tests/state_invariant_tests.cpp:139 | main | False | test_fixture | assert(c->location==s->location && c->isOpen==1); |
| src1.6.7/tests/state_invariant_tests.cpp:149 | main | False | test_fixture | auto goal=Task("inside",s,c); w->notnot_infoConstrains.push_back(goal); |
| src1.6.7/tests/state_invariant_tests.cpp:159 | main | False | test_fixture | assert(!summary.constraint_eligible[0]); |
| src1.6.7/tests/state_invariant_tests.cpp:161 | main | False | test_fixture | w->SetHold(s,EvidenceSource::INITIAL); w->SetInsideEvidence(3,true,EvidenceSource::SENSE); |
| src1.6.7/tests/state_invariant_tests.cpp:164 | main | False | test_fixture | assert(w->location==1 && !w->IsLocationVerified(3)); |
| src1.6.7/tests/state_invariant_tests.cpp:169 | main | False | test_fixture | w->SetInsideEvidence(3,true,EvidenceSource::SENSE); |
| src1.6.7/tests/state_invariant_tests.cpp:170 | main | False | test_fixture | w->ParseInfo(Task("on",s,c)); |
| src1.6.7/tests/state_invariant_tests.cpp:171 | main | False | test_fixture | assert(s->inside==2 && c->smallObjectsInside.size()==1); |
| src1.6.7/tests/state_invariant_tests.cpp:173 | main | False | test_fixture | assert(s->inside==2 && w->IsInsideVerified(3)); |
| src1.6.7/tests/state_invariant_tests.cpp:174 | main | False | test_fixture | w->ApplyStateValue(StateField::INSIDE,3,UNKNOWN,false,EvidenceSource::UNKNOWN); |
| src1.6.7/tests/state_invariant_tests.cpp:176 | main | False | test_fixture | assert(s->inside==UNKNOWN && !w->IsInsideVerified(3)); |
| src1.6.7/tests/state_invariant_tests.cpp:178 | main | True | test_fixture | w->posSensedFlag[4]=true; |
| src1.6.7/tests/state_invariant_tests.cpp:179 | main | False | test_fixture | w->locationSensedObjects[4].object_ids={2}; |
| src1.6.7/tests/state_invariant_tests.cpp:181 | main | False | test_fixture | assert(!w->posSensedFlag[4] && !w->HasObjectAtLocation(4,2)); |
| src1.6.7/tests/state_invariant_tests.cpp:184 | main | False | test_fixture | assert(w->hold_id==3 && w->plate_id==NONE && !w->plate); |
| src1.6.7/tests/state_invariant_tests.cpp:187 | main | True | test_fixture | w->objects[4]->location=UNKNOWN; |
| src1.6.7/tests/state_invariant_tests.cpp:189 | main | False | test_fixture | assert(w->LocationSource(2)==EvidenceSource::INITIAL); |
| src1.6.7/tests/state_invariant_tests.cpp:190 | main | False | test_fixture | assert(w->LocationSource(4)==EvidenceSource::CONSTRAINT_HEURISTIC); |
| src1.6.7/tests/state_invariant_tests.cpp:192 | main | False | test_fixture | assert(w->objects[2]->location==4 && w->objects[4]->location==4); |
| src1.6.7/tests/state_invariant_tests.cpp:193 | main | False | test_fixture | assert(!w->IsLocationVerified(4)); |
| src1.6.7/tests/state_invariant_tests.cpp:194 | main | True | test_fixture | c->location=UNKNOWN; w->objectLocationVerified[2]=false; |
| src1.6.7/tests/state_invariant_tests.cpp:196 | main | False | test_fixture | assert(w->objects[4]->location==UNKNOWN); |
| src1.6.7/tests/state_invariant_tests.cpp:198 | main | False | test_fixture | w->notnot_infoConstrains.push_back(Task("inside",s,c)); |
| src1.6.7/tests/state_invariant_tests.cpp:200 | main | False | test_fixture | assert(w->InsideSource(3)==EvidenceSource::CONSTRAINT_DERIVED); |
| src1.6.7/tests/state_invariant_tests.cpp:203 | main | False | test_fixture | assert(s->location==1); |
| src1.6.7/tests/state_invariant_tests.cpp:204 | main | False | test_fixture | assert(w->LocationSource(3)==EvidenceSource::CONSTRAINT_DERIVED); |
| src1.6.7/tests/state_invariant_tests.cpp:205 | main | True | test_fixture | w->constraint_eligible.assign(1,false); |
| src1.6.7/tests/state_invariant_tests.cpp:206 | main | True | test_fixture | w->constraint_uncertain.assign(1,false); |
| src1.6.7/tests/state_invariant_tests.cpp:209 | main | True | test_fixture | c->location=1; s->location=1; c->isOpen=UNKNOWN; |
| src1.6.7/tests/state_invariant_tests.cpp:211 | main | False | test_fixture | assert(s->inside==2 && s->location==1); |
| src1.6.7/tests/state_invariant_tests.cpp:212 | main | False | test_fixture | assert(!w->IsLocationVerified(3)); |
| src1.6.7/tests/state_invariant_tests.cpp:214 | main | True | test_fixture | c->isOpen=UNKNOWN; |
| src1.6.7/tests/state_invariant_tests.cpp:217 | main | False | test_fixture | assert(c->isOpen==1 && w->IsContainerStateVerified(2)); |
| src1.6.7/tests/state_layer_tests.cpp:24 | main | False | test_fixture | assert(w->ParseEnv("(hold 0) (plate 0) (at 0 1) " |
| src1.6.7/tests/state_layer_tests.cpp:27 | main | False | test_fixture | "(sort 3 cup) (size 3 small) (inside 3 2)")); |
| src1.6.7/tests/state_layer_tests.cpp:31 | main | False | test_fixture | const auto& p=w->Provenance(StateField::LOCATION,2); |
| src1.6.7/tests/state_layer_tests.cpp:32 | main | False | test_fixture | assert(p.received.present && p.received.value==4); |
| src1.6.7/tests/state_layer_tests.cpp:33 | main | False | test_fixture | assert(p.received.source==EvidenceSource::INITIAL); |
| src1.6.7/tests/state_layer_tests.cpp:34 | main | False | test_fixture | assert(p.resolved_value==4 && !w->IsLocationVerified(2)); |
| src1.6.7/tests/state_layer_tests.cpp:38 | main | False | test_fixture | assert(c->location==5 && !w->IsLocationVerified(2)); |
| src1.6.7/tests/state_layer_tests.cpp:39 | main | False | test_fixture | assert(w->Provenance(StateField::LOCATION,2).resolved_value==UNKNOWN); |
| src1.6.7/tests/state_layer_tests.cpp:40 | main | False | test_fixture | assert(w->Provenance(StateField::LOCATION,2).received.source==EvidenceSource::ASK_ANSWER); |
| src1.6.7/tests/state_layer_tests.cpp:43 | main | False | test_fixture | const auto& p=w->Provenance(StateField::CONTAINER_STATE,2); |
| src1.6.7/tests/state_layer_tests.cpp:44 | main | False | test_fixture | assert(c->isOpen==1 && p.resolved_value==1); |
| src1.6.7/tests/state_layer_tests.cpp:45 | main | False | test_fixture | assert(p.received.source==EvidenceSource::ACTION_SUCCESS && w->IsContainerStateVerified(2)); |
| src1.6.7/tests/state_layer_tests.cpp:48 | main | False | test_fixture | assert(c->isOpen==0 && !w->IsContainerStateVerified(2)); |
| src1.6.7/tests/state_layer_tests.cpp:49 | main | False | test_fixture | assert(w->Provenance(StateField::CONTAINER_STATE,2).received.source==EvidenceSource::INITIAL); |
| src1.6.7/tests/state_layer_tests.cpp:52 | main | False | test_fixture | assert(c->location==UNKNOWN && w->HasContradictoryEvidence(StateField::LOCATION,2)); |
| src1.6.7/tests/state_layer_tests.cpp:53 | main | False | test_fixture | assert(!w->IsLocationVerified(2)); |
| src1.6.7/tests/state_layer_tests.cpp:57 | main | True | test_fixture | w->objects[1]->location=UNKNOWN; |
| src1.6.7/tests/state_layer_tests.cpp:58 | main | True | test_fixture | c->location=1; w->MarkDirectLocationEvidence(2,true,EvidenceSource::SENSE); |
| src1.6.7/tests/state_layer_tests.cpp:60 | main | False | test_fixture | assert(w->objects[1]->location==1); |
| src1.6.7/tests/state_layer_tests.cpp:61 | main | False | test_fixture | assert(w->Provenance(StateField::LOCATION,1).dependency_count>0); |
| src1.6.7/tests/state_layer_tests.cpp:66 | main | True | test_fixture | c->location=5; w->MarkDirectLocationEvidence(2,true,EvidenceSource::SENSE); |
| src1.6.7/tests/state_layer_tests.cpp:68 | main | False | test_fixture | assert(!w->IsLocationVerified(1)); |
| src1.6.7/tests/state_layer_tests.cpp:73 | main | True | test_fixture | c->location=1; w->MarkDirectLocationEvidence(2,true,EvidenceSource::SENSE); |
| src1.6.7/tests/state_layer_tests.cpp:74 | main | True | test_fixture | w->objects[1]->location=UNKNOWN; |
| src1.6.7/tests/state_layer_tests.cpp:78 | main | True | test_fixture | w->constraint_eligible.assign(1,true); |
| src1.6.7/tests/state_layer_tests.cpp:79 | main | True | test_fixture | w->constraint_uncertain.assign(1,false); |
| src1.6.7/tests/state_layer_tests.cpp:80 | main | False | test_fixture | const auto derived_before=w->Provenance(StateField::LOCATION,1); |
| src1.6.7/tests/state_layer_tests.cpp:81 | main | False | test_fixture | assert(derived_before.dependency_count==1); |
| src1.6.7/tests/state_layer_tests.cpp:82 | main | False | test_fixture | assert(derived_before.supporting_constraints.size()==1); |
| src1.6.7/tests/state_layer_tests.cpp:83 | main | False | test_fixture | auto before=w->Provenance(StateField::LOCATION,2); |
| src1.6.7/tests/state_layer_tests.cpp:86 | main | False | test_fixture | const auto& after=w->Provenance(StateField::LOCATION,2); |
| src1.6.7/tests/state_layer_tests.cpp:87 | main | False | test_fixture | assert(after.revision==before.revision && after.resolved_value==before.resolved_value); |
| src1.6.7/tests/state_layer_tests.cpp:88 | main | False | test_fixture | assert(after.received.source==before.received.source); |
| src1.6.7/tests/state_layer_tests.cpp:89 | main | False | test_fixture | const auto& derived_after=w->Provenance(StateField::LOCATION,1); |
| src1.6.7/tests/state_layer_tests.cpp:90 | main | False | test_fixture | assert(derived_after.revision==derived_before.revision); |
| src1.6.7/tests/state_layer_tests.cpp:91 | main | False | test_fixture | assert(derived_after.resolved_value==derived_before.resolved_value); |
| src1.6.7/tests/state_layer_tests.cpp:92 | main | False | test_fixture | assert(derived_after.resolved_source==derived_before.resolved_source); |
| src1.6.7/tests/state_layer_tests.cpp:93 | main | False | test_fixture | assert(derived_after.resolved_verified==derived_before.resolved_verified); |
| src1.6.7/tests/state_layer_tests.cpp:94 | main | False | test_fixture | assert(derived_after.dependency_count==derived_before.dependency_count); |
| src1.6.7/tests/state_layer_tests.cpp:95 | main | False | test_fixture | assert(derived_after.dependencies[0].field==derived_before.dependencies[0].field); |
| src1.6.7/tests/state_layer_tests.cpp:96 | main | False | test_fixture | assert(derived_after.dependencies[0].id==derived_before.dependencies[0].id); |
| src1.6.7/tests/state_layer_tests.cpp:97 | main | False | test_fixture | assert(derived_after.dependencies[0].value==derived_before.dependencies[0].value); |
| src1.6.7/tests/state_layer_tests.cpp:98 | main | False | test_fixture | assert(derived_after.dependencies[0].revision==derived_before.dependencies[0].revision); |
| src1.6.7/tests/state_layer_tests.cpp:99 | main | False | test_fixture | assert(derived_after.supporting_constraints==derived_before.supporting_constraints); |
| src1.6.7/tests/state_layer_tests.cpp:102 | main | True | test_fixture | w->stage=1; c->location=1; |
| src1.6.7/tests/state_layer_tests.cpp:113 | main | False | test_fixture | assert(w->Provenance(StateField::CONTAINER_STATE,2).resolved_value==1); |
| src1.6.7/tests/state_layer_tests.cpp:114 | main | False | test_fixture | assert(w->ContainerSource(2)==EvidenceSource::ACTION_SUCCESS); |
| src1.6.7/tests/state_layer_tests.cpp:117 | main | True | test_fixture | s->inside=UNKNOWN; w->SetInsideEvidence(3,false,EvidenceSource::UNKNOWN); |
| src1.6.7/tests/state_layer_tests.cpp:123 | main | False | test_fixture | assert(w->Provenance(StateField::CONTAINER_STATE,2).received.source==EvidenceSource::EXPLICIT_INFO); |
| src1.6.7/tests/state_layer_tests.cpp:124 | main | False | test_fixture | assert(!w->IsContainerStateVerified(2)); |
| src1.6.7/tests/state_layer_tests.cpp:128 | main | False | test_fixture | assert(w->location==5); |
| src1.6.7/tests/state_layer_tests.cpp:129 | main | False | test_fixture | assert(!w->IsInsideVerified(3)); |
| src1.6.7/tests/state_layer_tests.cpp:133 | main | False | test_fixture | assert(s->inside==NONE && s->location==5); |
| src1.6.7/tests/state_layer_tests.cpp:134 | main | False | test_fixture | assert(w->Provenance(StateField::INSIDE,3).resolved_value==UNKNOWN); |
| src1.6.7/tests/state_layer_tests.cpp:135 | main | False | test_fixture | assert(w->Provenance(StateField::LOCATION,3).resolved_value==UNKNOWN); |
| src1.6.7/tests/state_layer_tests.cpp:139 | main | False | test_fixture | assert(w->ParseEnvSentence("(inside 3 1)")); |
| src1.6.7/tests/state_layer_tests.cpp:140 | main | False | test_fixture | assert(s->inside==UNKNOWN); |
| src1.6.7/tests/state_layer_tests.cpp:143 | main | False | test_fixture | Instruction must=Goal("inside",s); must.Y.push_back(c); |
| src1.6.7/tests/state_layer_tests.cpp:146 | main | False | test_fixture | assert(w->IsInsideVerified(3)); |
| src1.6.7/tests/state_layer_tests.cpp:147 | main | False | test_fixture | assert(w->Provenance(StateField::INSIDE,3).support_constraint_index==0); |
| src1.6.7/tests/state_layer_tests.cpp:148 | main | True | test_fixture | w->constraint_eligible.assign(1,false); |
| src1.6.7/tests/state_layer_tests.cpp:149 | main | False | test_fixture | assert(!w->IsInsideVerified(3)); |
| src1.6.7/tests/state_layer_tests.cpp:151 | main | False | test_fixture | assert(w->Provenance(StateField::HOLD,0).received.source==EvidenceSource::INITIAL); |
| src1.6.7/tests/state_layer_tests.cpp:152 | main | False | test_fixture | assert(w->Provenance(StateField::PLATE,0).resolved_value==NONE); |
| src1.6.7/tests/state_layer_tests.cpp:154 | main | False | test_fixture | assert(w->Provenance(StateField::HOLD,0).resolved_value==3); |
| src1.6.7/tests/state_layer_tests.cpp:155 | main | False | test_fixture | assert(w->Provenance(StateField::HOLD,0).resolved_verified); |
| src1.6.7/tests/state_layer_tests.cpp:156 | main | False | test_fixture | assert(w->Provenance(StateField::HOLD,0).received.source==EvidenceSource::ACTION_SUCCESS); |
| src1.6.7/tests/state_layer_tests.cpp:161 | main | False | test_fixture | assert(w->Provenance(StateField::CONTAINER_STATE,2).supporting_constraints.size()==1); |
| src1.6.7/tests/state_layer_tests.cpp:162 | main | True | test_fixture | w->constraint_eligible.assign(1,false); |
| src1.6.7/tests/state_layer_tests.cpp:165 | main | False | test_fixture | assert(!w->IsContainerStateVerified(2)); |
| src1.6.7/tests/state_layer_tests.cpp:167 | main | True | test_fixture | c->location=1; w->MarkDirectLocationEvidence(2,true,EvidenceSource::SENSE); |
| src1.6.7/tests/state_layer_tests.cpp:168 | main | True | test_fixture | w->objects[1]->location=UNKNOWN; |
| src1.6.7/tests/state_layer_tests.cpp:173 | main | False | test_fixture | assert(w->Provenance(StateField::LOCATION,1).supporting_constraints.size()==1); |
| src1.6.7/tests/state_layer_tests.cpp:174 | main | True | test_fixture | w->constraint_uncertain.assign(1,true); |
| src1.6.7/tests/state_profile.cpp:25 | main | False | test_fixture | std::string env="(at 0 1) (hold 0) (plate 0) (sort 1 human) (size 1 big) (at 1 1)"; |
| src1.6.7/tests/state_profile.cpp:28 | main | False | test_fixture | for(unsigned id=1;id<=size;++id) w->ApplyStateValue(StateField::LOCATION,id,1,true,EvidenceSource::SENSE); |
| src1.6.7/tests/state_profile.cpp:30 | main | True | test_fixture | w->constraint_eligible.assign(size-1,true);w->constraint_uncertain.assign(size-1,false); |
| src1.6.7/tests/state_profile.cpp:33 | main | False | test_fixture | auto& p=w->locationProvenance[id]; |
| src1.6.7/tests/state_profile.cpp:34 | main | True | test_fixture | for(unsigned k=0;k<size-1;++k)p.supporting_constraints.push_back(k); |
| src1.6.7/tests/task_group_projection_tests.cpp:24 | main | False | test_fixture | "(hold 0) (plate 0) (at 0 1) " |
| src1.6.7/tests/task_group_projection_tests.cpp:31 | main | False | test_fixture | const int initial_location = world.location; |
| src1.6.7/tests/task_group_projection_tests.cpp:39 | main | False | test_fixture | assert(world.location == initial_location); |
| src1.6.7/tests/task_group_projection_tests.cpp:41 | main | False | test_fixture | assert(world.constraint_eligible.empty()); |
| src1.6.7/tests/task_group_projection_tests.cpp:46 | main | False | test_fixture | assert(world.location == initial_location); |
| src1.6.7/tests/task_group_projection_tests.cpp:58 | main | False | test_fixture | assert(world.location == initial_location); |
| src1.6.7/tests/task_group_projection_tests.cpp:67 | main | False | test_fixture | "(hold 0) (plate 0) (at 0 1) " |
| src1.6.7/tests/task_group_projection_tests.cpp:83 | main | False | test_fixture | assert(constrained->constraint_eligible.empty()); |
| src1.6.7/tests/three_a_tests.cpp:28 | main | False | test_fixture | " (hold 0) (plate 0) (at 0 4) " |
| src1.6.7/tests/three_a_tests.cpp:36 | main | False | test_fixture | close_goal.isEnable = false; // terminal truth must not depend on execution flags |
| src1.6.7/tests/three_a_tests.cpp:70 | main | False | test_fixture | world->ApplyStateValue(StateField::CONTAINER_STATE,2,0,true,EvidenceSource::SENSE); |
| src1.6.7/tests/three_a_tests.cpp:82 | main | True | test_fixture | std::dynamic_pointer_cast<Container>(world->objects[2])->isOpen = false; |
| src1.6.7/tests/three_a_tests.cpp:83 | main | False | test_fixture | const int location_before_preview = world->location; |
| src1.6.7/tests/three_a_tests.cpp:104 | main | False | test_fixture | assert(world->location == location_before_preview); |
| src1.6.7/tests/three_a_tests.cpp:105 | main | False | test_fixture | assert(!std::dynamic_pointer_cast<Container>(world->objects[2])->isOpen); |
| src1.6.7/tests/three_a_tests.cpp:114 | main | False | test_fixture | world->ApplyStateValue(StateField::LOCATION,0,3,true,EvidenceSource::ACTION_SUCCESS); |
| src1.6.7/tests/three_a_tests.cpp:120 | main | False | test_fixture | assert(world->location == 3 && world->objects[2]->location == 4); |
