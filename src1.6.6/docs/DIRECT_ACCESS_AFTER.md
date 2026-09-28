# Direct access inventory AFTER

A hypothesis; B fact query; C mutation; D serialization/restore/debug.
Functions are tracked by definition/body scope; mixed-function classifications are completed in CANONICAL_AUDIT_REVIEW.md / CANONICAL_AUDIT_FINAL.md.
Safe/Modify are review triage; each JSON row also records its semantic reason.

| File:line | Function | Fields | Type | Safe | Modify | Code |
|---|---|---|---|---|---|---|
| src1.6.6/canonical_state.cpp:6 | FactValue | FactValue | B | True | False | int RDFW::FactValue(StateField field, unsigned int id) const { |
| src1.6.6/canonical_state.cpp:7 | FactValue | ResolvedState | B | True | False | const StateClaim claim = ResolvedState(field, id); |
| src1.6.6/canonical_state.cpp:12 | ScoreFactLocation | inside | D | True | False | // Official Stage 1 ASP at facts intentionally exclude inside propagation. |
| src1.6.6/canonical_state.cpp:13 | ScoreFactLocation | location | D | True | False | // This is the scoring representation of canonical location, not a planner read. |
| src1.6.6/canonical_state.cpp:15 | ScoreFactLocation | FactLocation | B | True | False | return FactLocation(id)!=UNKNOWN && id < score_locations.size() ? score_locations[id] : UNKNOWN; |
| src1.6.6/canonical_state.cpp:16 | ScoreFactLocation | FactLocation | B | True | False | return FactLocation(id); |
| src1.6.6/canonical_state.cpp:19 | IsStoredFact | IsStoredFact | B | True | False | bool RDFW::IsStoredFact(unsigned int id) const { |
| src1.6.6/canonical_state.cpp:20 | IsStoredFact | FactValue | B | True | False | return id > 0 && (FactValue(StateField::HOLD) == static_cast<int>(id) \|\| |
| src1.6.6/canonical_state.cpp:21 | IsStoredFact | FactValue | B | True | False | FactValue(StateField::PLATE) == static_cast<int>(id)); |
| src1.6.6/canonical_state.cpp:24 | IsNotStoredFact | IsNotStoredFact | B | True | False | bool RDFW::IsNotStoredFact(unsigned int id) const { |
| src1.6.6/canonical_state.cpp:25 | IsNotStoredFact | IsStoredFact | B | True | False | if (!IsValidObjectId(id) \|\| IsStoredFact(id)) return false; |
| src1.6.6/canonical_state.cpp:26 | IsNotStoredFact | FactValue | B | True | False | const int hand = FactValue(StateField::HOLD), tray = FactValue(StateField::PLATE); |
| src1.6.6/canonical_state.cpp:29 | IsNotStoredFact | ResolvedState,inside | C | True | False | const auto inside = ResolvedState(StateField::INSIDE, id); |
| src1.6.6/canonical_state.cpp:30 | IsNotStoredFact | inside | B | True | False | if (!inside.present) return false; |
| src1.6.6/canonical_state.cpp:31 | IsNotStoredFact | inside | B | True | False | if (inside.value > 0) return true; |
| src1.6.6/canonical_state.cpp:34 | IsNotStoredFact | ResolvedState | B | True | False | const auto loc = ResolvedState(StateField::LOCATION, id); |
| src1.6.6/canonical_state.cpp:35 | IsNotStoredFact | inside | B | True | False | return loc.present && inside.value == NONE && |
| src1.6.6/canonical_state.cpp:36 | IsNotStoredFact | EvidenceSource,inside | B | True | False | (inside.source == EvidenceSource::SENSE \|\| inside.source == EvidenceSource::ACTION_SUCCESS); |
| src1.6.6/canonical_state.cpp:39 | TaskFactSatisfied | TaskFactSatisfied | B | True | False | bool RDFW::TaskFactSatisfied(const std::string& behave, unsigned int x, unsigned int y) const { |
| src1.6.6/canonical_state.cpp:41 | TaskFactSatisfied | FactLocation | B | True | False | if (behave == "goto") return FactLocation(0) != UNKNOWN && FactLocation(0) == FactLocation(x); |
| src1.6.6/canonical_state.cpp:42 | TaskFactSatisfied | IsStoredFact | B | True | False | if (behave == "pickup") return IsStoredFact(x); |
| src1.6.6/canonical_state.cpp:43 | TaskFactSatisfied | FactInside,IsNotStoredFact | B | True | False | if (behave == "putdown") return FactInside(x) != UNKNOWN && IsNotStoredFact(x); |
| src1.6.6/canonical_state.cpp:44 | TaskFactSatisfied | FactContainerState | B | True | False | if (behave == "open") return FactContainerState(x) == 1; |
| src1.6.6/canonical_state.cpp:45 | TaskFactSatisfied | FactContainerState | B | True | False | if (behave == "close") return FactContainerState(x) == 0; |
| src1.6.6/canonical_state.cpp:46 | TaskFactSatisfied | FactInside | B | True | False | if (behave == "putin") return FactInside(x) != UNKNOWN && FactInside(x) == static_cast<int>(y); |
| src1.6.6/canonical_state.cpp:47 | TaskFactSatisfied | FactInside | B | True | False | if (behave == "takeout") return FactInside(x) != UNKNOWN && FactInside(x) != static_cast<int>(y); |
| src1.6.6/canonical_state.cpp:49 | TaskFactSatisfied | FactInside,IsNotStoredFact | B | True | False | return y && FactInside(x) == NONE && IsNotStoredFact(x) && |
| src1.6.6/canonical_state.cpp:50 | TaskFactSatisfied | FactLocation | B | True | False | FactLocation(x) != UNKNOWN && FactLocation(x) == FactLocation(y); |
| src1.6.6/canonical_state.cpp:55 | ApplyStateValue | EvidenceSource | C | True | False | bool verified, EvidenceSource source) { |
| src1.6.6/canonical_state.cpp:58 | ApplyStateValue | location | C | True | False | objects[id]->location = value; |
| src1.6.6/canonical_state.cpp:64 | ApplyStateValue | inside | C | True | False | item->inside = value; |
| src1.6.6/canonical_state.cpp:73 | ApplyStateValue | isOpen | C | True | False | container->isOpen = value; |
| src1.6.6/canonical_state.cpp:81 | DebugStateSnapshot | Provenance | D | True | False | const auto& p = Provenance(field,id); |
| src1.6.6/canonical_state.cpp:99 | DebugStateSnapshot | location | D | True | False | out << object->location << ':'; |
| src1.6.6/canonical_state.cpp:101 | DebugStateSnapshot | inside | D | True | False | if (small) out << small->inside << ':' << small->on; |
| src1.6.6/canonical_state.cpp:103 | DebugStateSnapshot | isOpen | D | True | False | if (cont) { out << cont->isOpen << '['; for (auto item:cont->smallObjectsInside) out << item->id << ','; out << ']'; } |
| src1.6.6/canonical_state.cpp:104 | DebugStateSnapshot | objectLocationVerified | D | True | False | out << ':' << (id<objectLocationVerified.size() && objectLocationVerified[id]) |
| src1.6.6/canonical_state.cpp:105 | DebugStateSnapshot | objectInsideVerified | D | True | False | << ':' << (id<objectInsideVerified.size() && objectInsideVerified[id]) |
| src1.6.6/canonical_state.cpp:106 | DebugStateSnapshot | containerStateVerified | D | True | False | << ':' << (id<containerStateVerified.size() && containerStateVerified[id]) |
| src1.6.6/canonical_state.cpp:107 | DebugStateSnapshot | ContainerSource,InsideSource,LocationSource | D | True | False | << ':' << int(LocationSource(id)) << ':' << int(InsideSource(id)) << ':' << int(ContainerSource(id)) |
| src1.6.6/canonical_state.cpp:108 | DebugStateSnapshot | objectLocationInferredByMustNear | D | True | False | << ':' << (id<objectLocationInferredByMustNear.size() && objectLocationInferredByMustNear[id]) << ';'; |
| src1.6.6/canonical_state.cpp:111 | DebugStateSnapshot | hold,hold_id,location,plate,plate_id | D | True | False | out << location << ':' << hold_id << ':' << plate_id << ':' << (hold?hold->id:0) << ':' << (plate?plate->id:0) << ';'; |
| src1.6.6/canonical_state.cpp:121 | DebugStateConsistency | EvidenceSource | D | True | False | const auto check = [&](StateField f, unsigned id, int legacy, bool verified, EvidenceSource source) { |
| src1.6.6/canonical_state.cpp:122 | DebugStateConsistency | Provenance,ResolvedState | D | True | False | const auto& p=Provenance(f,id); const auto fact=ResolvedState(f,id); |
| src1.6.6/canonical_state.cpp:126 | DebugStateConsistency | DependenciesCurrent | D | True | False | if (fact.present && (fact.value==UNKNOWN \|\| !DependenciesCurrent(f,id))) issue(id,"invalid fact"); |
| src1.6.6/canonical_state.cpp:131 | DebugStateConsistency | LocationSource,location,objectLocationVerified | D | True | False | check(StateField::LOCATION,id,objects[id]->location,id<objectLocationVerified.size() && objectLocationVerified[id],LocationSource(id)); |
| src1.6.6/canonical_state.cpp:133 | DebugStateConsistency | InsideSource,inside,objectInsideVerified | D | True | False | if (small) check(StateField::INSIDE,id,small->inside,id<objectInsideVerified.size() && objectInsideVerified[id],InsideSource(id)); |
| src1.6.6/canonical_state.cpp:135 | DebugStateConsistency | ContainerSource,containerStateVerified,isOpen | D | True | False | if (cont) check(StateField::CONTAINER_STATE,id,cont->isOpen,id<containerStateVerified.size() && containerStateVerified[id],ContainerSource(id)); |
| src1.6.6/canonical_state.cpp:136 | DebugStateConsistency | IsStoredFact | D | True | False | if (IsStoredFact(id)) { |
| src1.6.6/canonical_state.cpp:137 | DebugStateConsistency | FactInside,FactLocation | D | True | False | if (!small \|\| FactInside(id)!=NONE \|\| FactLocation(id)!=FactLocation(0)) issue(id,"stored relation"); |
| src1.6.6/canonical_state.cpp:139 | DebugStateConsistency | FactInside | D | True | False | if (small && FactInside(id)>0) { |
| src1.6.6/canonical_state.cpp:140 | DebugStateConsistency | FactInside | D | True | False | auto container=std::dynamic_pointer_cast<Container>(GetObject(FactInside(id))); |
| src1.6.6/canonical_state.cpp:141 | DebugStateConsistency | inside | D | True | False | if (!container) issue(id,"inside target"); |
| src1.6.6/canonical_state.cpp:142 | DebugStateConsistency | FactLocation,inside,location | D | True | False | else if (FactLocation(id)!=UNKNOWN && FactLocation(container->id)!=UNKNOWN && FactLocation(id)!=FactLocation(container->id)) issue(id,"inside location"); |
| src1.6.6/canonical_state.cpp:145 | DebugStateConsistency | inside | D | True | False | if (!item \|\| item->inside!=cont->id) issue(id,"membership cache"); |
| src1.6.6/canonical_state.cpp:148 | DebugStateConsistency | hold_id,plate_id | D | True | False | const int legacy=f==StateField::HOLD?hold_id:plate_id; |
| src1.6.6/canonical_state.cpp:149 | DebugStateConsistency | hold,plate | D | True | False | const auto ptr=f==StateField::HOLD?hold:plate; |
| src1.6.6/canonical_state.cpp:151 | DebugStateConsistency | Provenance | D | True | False | const auto& p=Provenance(f,0); |
| src1.6.6/canonical_state.cpp:154 | DebugStateConsistency | holdProvenance,plateProvenance | D | True | False | if (holdProvenance.resolved_verified && plateProvenance.resolved_verified && |
| src1.6.6/canonical_state.cpp:155 | DebugStateConsistency | holdProvenance,plateProvenance | D | True | False | holdProvenance.resolved_value>0 && holdProvenance.resolved_value==plateProvenance.resolved_value) issue(0,"exclusive storage"); |
| src1.6.6/legacy_priority.cpp:25 | isLocationKnown | FactLocation,location | A | True | False | return o && (h?o->location:w.FactLocation(o->id))!=UNKNOWN; |
| src1.6.6/legacy_priority.cpp:28 | isInsideKnown | FactInside,inside | A | True | False | return o && (h?o->inside:w.FactInside(o->id))!=UNKNOWN; |
| src1.6.6/legacy_priority.cpp:31 | isContainerStateKnown | FactContainerState,isOpen | A | True | False | return o && (h?o->isOpen:w.FactContainerState(o->id))!=UNKNOWN; |
| src1.6.6/legacy_priority.cpp:43 | evaluatePair | FactLocation,location | A | True | False | if (!hypothesis && (hypothesis?world.location:world.FactLocation(0)) != _home::UNKNOWN && |
| src1.6.6/legacy_priority.cpp:44 | evaluatePair | FactLocation,location | A | True | False | world.IsAbsentFromSensedLocation(x->id, (hypothesis?world.location:world.FactLocation(0)))) |
| src1.6.6/legacy_priority.cpp:46 | evaluatePair | FactLocation,location | A | True | False | if (!isLocationKnown(world, x, hypothesis) \|\| (hypothesis?world.location:world.FactLocation(0)) == _home::UNKNOWN) |
| src1.6.6/legacy_priority.cpp:48 | evaluatePair | FactLocation,location | A | True | False | return boolStatus((hypothesis?world.location:world.FactLocation(0)) == (hypothesis?x->location:world.FactLocation(x->id))); |
| src1.6.6/legacy_priority.cpp:58 | evaluatePair | FactContainerState,isOpen | A | True | False | return boolStatus(static_cast<bool>((hypothesis?container->isOpen:world.FactContainerState(container->id))) == expect_open); |
| src1.6.6/legacy_priority.cpp:62 | evaluatePair | IsStoredFact,hold_id,plate_id | A | True | False | const bool stored = (hypothesis?(world.hold_id==x->id \|\| world.plate_id==x->id):world.IsStoredFact(x->id)); |
| src1.6.6/legacy_priority.cpp:63 | evaluatePair | IsInsideVerified | B | True | False | if (!hypothesis && world.stage == 2 && !world.IsInsideVerified(x->id)) |
| src1.6.6/legacy_priority.cpp:65 | evaluatePair | IsNotStoredFact | B | True | False | if (!hypothesis && !stored && !world.IsNotStoredFact(x->id)) return TerminalStatus::UNKNOWN; |
| src1.6.6/legacy_priority.cpp:73 | evaluatePair | IsStoredFact,hold_id,plate_id | A | True | False | if ((hypothesis?(world.hold_id==x->id \|\| world.plate_id==x->id):world.IsStoredFact(x->id))) |
| src1.6.6/legacy_priority.cpp:75 | evaluatePair | FactInside,inside | A | True | False | if ((hypothesis?small->inside:world.FactInside(small->id)) != _home::NONE) return TerminalStatus::UNSATISFIED; |
| src1.6.6/legacy_priority.cpp:80 | evaluatePair | inside | B | True | False | if (behave == "putin" \|\| behave == "inside" \|\| behave == "in") { |
| src1.6.6/legacy_priority.cpp:84 | evaluatePair | FactInside,inside | A | True | False | return boolStatus((hypothesis?small->inside:world.FactInside(small->id)) == y->id); |
| src1.6.6/legacy_priority.cpp:91 | evaluatePair | FactInside,inside | A | True | False | return boolStatus((hypothesis?small->inside:world.FactInside(small->id)) != y->id); |
| src1.6.6/legacy_priority.cpp:99 | evaluatePair | FactLocation,location | A | True | False | world.IsAbsentFromSensedLocation(target->id, (hypothesis?x->location:world.FactLocation(x->id)))) |
| src1.6.6/legacy_priority.cpp:102 | evaluatePair | FactLocation,location | A | True | False | world.IsAbsentFromSensedLocation(x->id, (hypothesis?target->location:world.FactLocation(target->id)))) |
| src1.6.6/legacy_priority.cpp:111 | evaluatePair | IsStoredFact,hold_id,plate_id | A | True | False | if ((hypothesis?(world.hold_id==x->id \|\| world.plate_id==x->id):world.IsStoredFact(x->id))) |
| src1.6.6/legacy_priority.cpp:113 | evaluatePair | FactInside,inside | A | True | False | if ((hypothesis?small->inside:world.FactInside(small->id)) != _home::NONE) return TerminalStatus::UNSATISFIED; |
| src1.6.6/legacy_priority.cpp:115 | evaluatePair | FactLocation,location | A | True | False | return boolStatus((hypothesis?x->location:world.FactLocation(x->id)) == (hypothesis?target->location:world.FactLocation(target->id))); |
| src1.6.6/legacy_priority.cpp:118 | evaluatePair | plate | B | True | False | if (behave == "plate") { |
| src1.6.6/legacy_priority.cpp:119 | evaluatePair | plate_id | A | True | False | if (hypothesis) return boolStatus(world.plate_id==x->id); |
| src1.6.6/legacy_priority.cpp:120 | evaluatePair | IsInsideVerified | B | True | False | if (!hypothesis && world.stage == 2 && !world.IsInsideVerified(x->id)) |
| src1.6.6/legacy_priority.cpp:122 | evaluatePair | FactValue,IsNotStoredFact,plate_id | A | True | False | return (hypothesis?world.plate_id:world.FactValue(StateField::PLATE))==UNKNOWN && !world.IsNotStoredFact(x->id) ? TerminalStatus::UNKNOWN : boolStatus((hypothesis?world.plate_id:world.FactValue(StateField::PLATE)) == x->id); |
| src1.6.6/legacy_priority.cpp:125 | evaluatePair | hold | B | True | False | if (behave == "hold") { |
| src1.6.6/legacy_priority.cpp:126 | evaluatePair | hold_id | A | True | False | if (hypothesis) return boolStatus(world.hold_id==x->id); |
| src1.6.6/legacy_priority.cpp:127 | evaluatePair | IsInsideVerified | B | True | False | if (!hypothesis && world.stage == 2 && !world.IsInsideVerified(x->id)) |
| src1.6.6/legacy_priority.cpp:129 | evaluatePair | FactValue,IsNotStoredFact,hold_id | A | True | False | return (hypothesis?world.hold_id:world.FactValue(StateField::HOLD))==UNKNOWN && !world.IsNotStoredFact(x->id) ? TerminalStatus::UNKNOWN : boolStatus((hypothesis?world.hold_id:world.FactValue(StateField::HOLD)) == x->id); |
| src1.6.6/parser.cpp:651 | get_info_instruction | plate | A | True | False | if (instr.behave == "on" && instr.isUseY && instr.conditionY.sort == "plate") |
| src1.6.6/parser.cpp:653 | get_info_instruction | plate | A | True | False | instr.behave = "plate"; |
| src1.6.6/question_preflight.cpp:30 | SemanticInstructionKey | location | D | True | False | // Do NOT use positions: two objects at the same location remain two goals. |
| src1.6.6/question_preflight.cpp:32 | SemanticInstructionKey | inside | A | True | False | if (predicate == "in") predicate = "inside"; |
| src1.6.6/question_preflight.cpp:56 | RunQuestionPreflight | location | A | True | False | if (location < 0 \|\| location > MAX_LOCATION_ID) |
| src1.6.6/question_preflight.cpp:57 | RunQuestionPreflight | location | A | True | False | world_error("robot has no usable initial location"); |
| src1.6.6/question_preflight.cpp:71 | RunQuestionPreflight | location | A | True | False | if (object->sort.empty() && !small && !big && object->location == UNKNOWN) |
| src1.6.6/question_preflight.cpp:75 | RunQuestionPreflight | location | A | True | False | if (object->location < UNKNOWN \|\| object->location > MAX_LOCATION_ID) |
| src1.6.6/question_preflight.cpp:76 | RunQuestionPreflight | location | A | True | False | world_error("object location out of bounds: " + std::to_string(i)); |
| src1.6.6/question_preflight.cpp:82 | RunQuestionPreflight | location | D | True | False | // Stage 2 location descriptions can be wrong; collisions there are NOT |
| src1.6.6/question_preflight.cpp:84 | RunQuestionPreflight | location | A | True | False | if (stage == 1 && big && object->location != UNKNOWN && |
| src1.6.6/question_preflight.cpp:85 | RunQuestionPreflight | location | A | True | False | !big_locations.emplace(object->location, object->id).second) |
| src1.6.6/question_preflight.cpp:86 | RunQuestionPreflight | location | A | True | False | world_warning("multiple big objects at Stage 1 location " + |
| src1.6.6/question_preflight.cpp:87 | RunQuestionPreflight | location | A | True | False | std::to_string(object->location)); |
| src1.6.6/rdfw.cpp:178 | EvidenceName | EvidenceSource | A | True | False | const char* EvidenceName(EvidenceSource source) { |
| src1.6.6/rdfw.cpp:180 | EvidenceName | EvidenceSource | A | True | False | case EvidenceSource::UNKNOWN: return "unknown"; |
| src1.6.6/rdfw.cpp:181 | EvidenceName | EvidenceSource | A | True | False | case EvidenceSource::INITIAL: return "initial"; |
| src1.6.6/rdfw.cpp:182 | EvidenceName | EvidenceSource | A | True | False | case EvidenceSource::EXPLICIT_INFO: return "explicit_info"; |
| src1.6.6/rdfw.cpp:183 | EvidenceName | EvidenceSource | A | True | False | case EvidenceSource::CONSTRAINT_DERIVED: return "constraint_derived"; |
| src1.6.6/rdfw.cpp:184 | EvidenceName | EvidenceSource | A | True | False | case EvidenceSource::RELATION_DERIVED: return "relation_derived"; |
| src1.6.6/rdfw.cpp:185 | EvidenceName | EvidenceSource | A | True | False | case EvidenceSource::CONSTRAINT_HEURISTIC: return "constraint_heuristic"; |
| src1.6.6/rdfw.cpp:186 | EvidenceName | EvidenceSource | A | True | False | case EvidenceSource::SENSE: return "sense"; |
| src1.6.6/rdfw.cpp:187 | EvidenceName | EvidenceSource | A | True | False | case EvidenceSource::ACTION_SUCCESS: return "action_success"; |
| src1.6.6/rdfw.cpp:188 | EvidenceName | EvidenceSource | A | True | False | case EvidenceSource::ACTION_FAILURE: return "action_failure"; |
| src1.6.6/rdfw.cpp:189 | EvidenceName | EvidenceSource | A | True | False | case EvidenceSource::ASK_ANSWER: return "ask_answer"; |
| src1.6.6/rdfw.cpp:275 | CaptureCandidateEvidence | EvidenceSource,Provenance | B | True | False | if (Provenance(StateField::LOCATION,i).resolved_source != EvidenceSource::UNKNOWN) { |
| src1.6.6/rdfw.cpp:278 | CaptureCandidateEvidence | location | B | True | False | fact.fact = "location"; |
| src1.6.6/rdfw.cpp:279 | CaptureCandidateEvidence | Provenance | B | True | False | fact.source = EvidenceName(Provenance(StateField::LOCATION,i).resolved_source); |
| src1.6.6/rdfw.cpp:280 | CaptureCandidateEvidence | IsLocationVerified | B | True | False | fact.verified = IsLocationVerified(static_cast<unsigned int>(i)); |
| src1.6.6/rdfw.cpp:283 | CaptureCandidateEvidence | EvidenceSource,Provenance | B | True | False | if (Provenance(StateField::INSIDE,i).resolved_source != EvidenceSource::UNKNOWN) { |
| src1.6.6/rdfw.cpp:286 | CaptureCandidateEvidence | inside | B | True | False | fact.fact = "inside"; |
| src1.6.6/rdfw.cpp:287 | CaptureCandidateEvidence | Provenance | B | True | False | fact.source = EvidenceName(Provenance(StateField::INSIDE,i).resolved_source); |
| src1.6.6/rdfw.cpp:288 | CaptureCandidateEvidence | IsInsideVerified | B | True | False | fact.verified = IsInsideVerified(static_cast<unsigned int>(i)); |
| src1.6.6/rdfw.cpp:291 | CaptureCandidateEvidence | EvidenceSource,Provenance | B | True | False | if (Provenance(StateField::CONTAINER_STATE,i).resolved_source != EvidenceSource::UNKNOWN) { |
| src1.6.6/rdfw.cpp:295 | CaptureCandidateEvidence | Provenance | B | True | False | fact.source = EvidenceName(Provenance(StateField::CONTAINER_STATE,i).resolved_source); |
| src1.6.6/rdfw.cpp:296 | CaptureCandidateEvidence | IsContainerStateVerified | B | True | False | fact.verified = IsContainerStateVerified(static_cast<unsigned int>(i)); |
| src1.6.6/rdfw.cpp:301 | CaptureCandidateEvidence | hold,plate | B | True | False | CandidateEvidence e; e.object_id=0; e.fact=f==StateField::HOLD?"hold":"plate"; |
| src1.6.6/rdfw.cpp:302 | CaptureCandidateEvidence | Provenance,ResolvedState | B | True | False | e.source=EvidenceName(Provenance(f,0).resolved_source); e.verified=ResolvedState(f,0).present; |
| src1.6.6/rdfw.cpp:341 | BuildTaskGroupPlan | location | D | True | False | int location; |
| src1.6.6/rdfw.cpp:345 | BuildTaskGroupPlan | inside | D | True | False | int inside; |
| src1.6.6/rdfw.cpp:361 | BuildTaskGroupPlan | location | D | True | False | state.location = objects[i]->location; |
| src1.6.6/rdfw.cpp:368 | BuildTaskGroupPlan | inside | D | True | False | state.inside = small->inside; |
| src1.6.6/rdfw.cpp:375 | BuildTaskGroupPlan | isOpen | D | True | False | state.is_open = container->isOpen; |
| src1.6.6/rdfw.cpp:385 | BuildTaskGroupPlan | location | D | True | False | const int saved_location = location; |
| src1.6.6/rdfw.cpp:386 | BuildTaskGroupPlan | hold_id | D | True | False | const int saved_hold_id = hold_id; |
| src1.6.6/rdfw.cpp:387 | BuildTaskGroupPlan | plate_id | D | True | False | const int saved_plate_id = plate_id; |
| src1.6.6/rdfw.cpp:416 | BuildTaskGroupPlan | objectLocationInferredByMustNear | D | True | False | const std::vector<bool> saved_inferred = objectLocationInferredByMustNear; |
| src1.6.6/rdfw.cpp:419 | BuildTaskGroupPlan | objectLocationVerified | D | True | False | const std::vector<bool> saved_location_verified = objectLocationVerified; |
| src1.6.6/rdfw.cpp:420 | BuildTaskGroupPlan | objectInsideVerified | D | True | False | const std::vector<bool> saved_inside_verified = objectInsideVerified; |
| src1.6.6/rdfw.cpp:421 | BuildTaskGroupPlan | containerStateVerified | D | True | False | const std::vector<bool> saved_container_verified = containerStateVerified; |
| src1.6.6/rdfw.cpp:422 | BuildTaskGroupPlan | EvidenceSource,objectLocationSource | D | True | False | const std::vector<EvidenceSource> saved_location_source = objectLocationSource; |
| src1.6.6/rdfw.cpp:423 | BuildTaskGroupPlan | EvidenceSource,objectInsideSource | D | True | False | const std::vector<EvidenceSource> saved_inside_source = objectInsideSource; |
| src1.6.6/rdfw.cpp:424 | BuildTaskGroupPlan | EvidenceSource,containerStateSource | D | True | False | const std::vector<EvidenceSource> saved_container_source = containerStateSource; |
| src1.6.6/rdfw.cpp:425 | BuildTaskGroupPlan | StateProvenance,locationProvenance | D | True | False | const std::vector<StateProvenance> saved_location_provenance = locationProvenance; |
| src1.6.6/rdfw.cpp:426 | BuildTaskGroupPlan | StateProvenance,insideProvenance | D | True | False | const std::vector<StateProvenance> saved_inside_provenance = insideProvenance; |
| src1.6.6/rdfw.cpp:427 | BuildTaskGroupPlan | StateProvenance,containerProvenance | D | True | False | const std::vector<StateProvenance> saved_container_provenance = containerProvenance; |
| src1.6.6/rdfw.cpp:428 | BuildTaskGroupPlan | StateProvenance,holdProvenance | D | True | False | const StateProvenance saved_hold_provenance = holdProvenance; |
| src1.6.6/rdfw.cpp:429 | BuildTaskGroupPlan | StateProvenance,plateProvenance | D | True | False | const StateProvenance saved_plate_provenance = plateProvenance; |
| src1.6.6/rdfw.cpp:484 | BuildTaskGroupPlan | objectLocationInferredByMustNear | D | True | False | objectLocationInferredByMustNear = saved_inferred; |
| src1.6.6/rdfw.cpp:487 | BuildTaskGroupPlan | objectLocationVerified | D | True | False | objectLocationVerified = saved_location_verified; |
| src1.6.6/rdfw.cpp:488 | BuildTaskGroupPlan | objectInsideVerified | D | True | False | objectInsideVerified = saved_inside_verified; |
| src1.6.6/rdfw.cpp:489 | BuildTaskGroupPlan | containerStateVerified | D | True | False | containerStateVerified = saved_container_verified; |
| src1.6.6/rdfw.cpp:490 | BuildTaskGroupPlan | objectLocationSource | D | True | False | objectLocationSource = saved_location_source; |
| src1.6.6/rdfw.cpp:491 | BuildTaskGroupPlan | objectInsideSource | D | True | False | objectInsideSource = saved_inside_source; |
| src1.6.6/rdfw.cpp:492 | BuildTaskGroupPlan | containerStateSource | D | True | False | containerStateSource = saved_container_source; |
| src1.6.6/rdfw.cpp:493 | BuildTaskGroupPlan | locationProvenance | D | True | False | locationProvenance = saved_location_provenance; |
| src1.6.6/rdfw.cpp:494 | BuildTaskGroupPlan | insideProvenance | D | True | False | insideProvenance = saved_inside_provenance; |
| src1.6.6/rdfw.cpp:495 | BuildTaskGroupPlan | containerProvenance | D | True | False | containerProvenance = saved_container_provenance; |
| src1.6.6/rdfw.cpp:496 | BuildTaskGroupPlan | holdProvenance | D | True | False | holdProvenance = saved_hold_provenance; |
| src1.6.6/rdfw.cpp:497 | BuildTaskGroupPlan | plateProvenance | D | True | False | plateProvenance = saved_plate_provenance; |
| src1.6.6/rdfw.cpp:508 | BuildTaskGroupPlan | location | D | True | False | objects[i]->location = state.location; |
| src1.6.6/rdfw.cpp:515 | BuildTaskGroupPlan | inside | D | True | False | small->inside = state.inside; |
| src1.6.6/rdfw.cpp:525 | BuildTaskGroupPlan | isOpen | D | True | False | container->isOpen = object_states[i].is_open; |
| src1.6.6/rdfw.cpp:537 | BuildTaskGroupPlan | location | D | True | False | location = saved_location; |
| src1.6.6/rdfw.cpp:538 | BuildTaskGroupPlan | hold_id | D | True | False | hold_id = saved_hold_id; |
| src1.6.6/rdfw.cpp:539 | BuildTaskGroupPlan | plate_id | D | True | False | plate_id = saved_plate_id; |
| src1.6.6/rdfw.cpp:540 | BuildTaskGroupPlan | hold | D | True | False | hold = saved_hold_id > 0 && static_cast<std::size_t>(saved_hold_id) < objects.size() |
| src1.6.6/rdfw.cpp:542 | BuildTaskGroupPlan | plate | D | True | False | plate = saved_plate_id > 0 && static_cast<std::size_t>(saved_plate_id) < objects.size() |
| src1.6.6/rdfw.cpp:665 | BuildTaskGroupPlan | location | D | True | False | const int projected_location = location; |
| src1.6.6/rdfw.cpp:1261 | PlanStateSignature | hold_id,location,plate_id | D | True | False | out << location << ',' << hold_id << ',' << plate_id << ',' |
| src1.6.6/rdfw.cpp:1266 | PlanStateSignature | location | D | True | False | out << object->id << ',' << object->location << ',' |
| src1.6.6/rdfw.cpp:1270 | PlanStateSignature | inside | D | True | False | if (small) out << ',' << small->inside << ',' << small->on; |
| src1.6.6/rdfw.cpp:1274 | PlanStateSignature | isOpen | D | True | False | out << ',' << container->isOpen << '['; |
| src1.6.6/rdfw.cpp:1293 | PlanStateSignature | objectLocationVerified | D | True | False | out << (i < objectLocationVerified.size() && objectLocationVerified[i]) |
| src1.6.6/rdfw.cpp:1294 | PlanStateSignature | objectInsideVerified | D | True | False | << ':' << (i < objectInsideVerified.size() && objectInsideVerified[i]) |
| src1.6.6/rdfw.cpp:1295 | PlanStateSignature | containerStateVerified | D | True | False | << ':' << (i < containerStateVerified.size() && containerStateVerified[i]) |
| src1.6.6/rdfw.cpp:1296 | PlanStateSignature | objectLocationSource | D | True | False | << ':' << (i < objectLocationSource.size() ? |
| src1.6.6/rdfw.cpp:1297 | PlanStateSignature | objectLocationSource | D | True | False | static_cast<int>(objectLocationSource[i]) : -1) |
| src1.6.6/rdfw.cpp:1298 | PlanStateSignature | objectInsideSource | D | True | False | << ':' << (i < objectInsideSource.size() ? |
| src1.6.6/rdfw.cpp:1299 | PlanStateSignature | objectInsideSource | D | True | False | static_cast<int>(objectInsideSource[i]) : -1) |
| src1.6.6/rdfw.cpp:1300 | PlanStateSignature | containerStateSource | D | True | False | << ':' << (i < containerStateSource.size() ? |
| src1.6.6/rdfw.cpp:1301 | PlanStateSignature | containerStateSource | D | True | False | static_cast<int>(containerStateSource[i]) : -1) << ','; |
| src1.6.6/rdfw.cpp:1387 | UpdateConstraintLedger | hold_id,location | A | True | False | if (hold_id > 0) score_locations[hold_id] = location; |
| src1.6.6/rdfw.cpp:1388 | UpdateConstraintLedger | location,plate_id | A | True | False | if (plate_id > 0) score_locations[plate_id] = location; |
| src1.6.6/rdfw.cpp:1393 | UpdateConstraintLedger | location | A | True | False | performed == "FromPlate") score_locations[arguments[0]] = location; |
| src1.6.6/rdfw.cpp:1441 | DryRunActionSucceeds | location | A | True | False | static_cast<int>(arguments[0]) != location; |
| src1.6.6/rdfw.cpp:1449 | DryRunActionSucceeds | hold_id,plate_id | A | True | False | return small && hold_id == NONE && plate_id != static_cast<int>(a) && |
| src1.6.6/rdfw.cpp:1450 | DryRunActionSucceeds | location | A | True | False | small->location == location && |
| src1.6.6/rdfw.cpp:1451 | DryRunActionSucceeds | inside | A | True | False | (small->inside == NONE \|\| small->inside == UNKNOWN); |
| src1.6.6/rdfw.cpp:1453 | DryRunActionSucceeds | hold_id | A | True | False | if (action == "PutDown") return hold_id == static_cast<int>(a); |
| src1.6.6/rdfw.cpp:1455 | DryRunActionSucceeds | hold_id,plate_id | A | True | False | return hold_id == static_cast<int>(a) && plate_id == NONE; |
| src1.6.6/rdfw.cpp:1457 | DryRunActionSucceeds | hold_id,plate_id | A | True | False | return plate_id == static_cast<int>(a) && hold_id == NONE; |
| src1.6.6/rdfw.cpp:1461 | DryRunActionSucceeds | hold_id,location | A | True | False | return container && container->location == location && hold_id == NONE && |
| src1.6.6/rdfw.cpp:1462 | DryRunActionSucceeds | isOpen | A | True | False | container->isOpen == (action == "Open" ? 0 : 1); |
| src1.6.6/rdfw.cpp:1471 | DryRunActionSucceeds | location | A | True | False | if (!small \|\| !container \|\| container->location != location \|\| |
| src1.6.6/rdfw.cpp:1472 | DryRunActionSucceeds | isOpen | A | True | False | container->isOpen != 1) return false; |
| src1.6.6/rdfw.cpp:1473 | DryRunActionSucceeds | hold_id | A | True | False | if (action == "PutIn") return hold_id == static_cast<int>(a); |
| src1.6.6/rdfw.cpp:1474 | DryRunActionSucceeds | hold_id,inside | A | True | False | return hold_id == NONE && small->inside == static_cast<int>(b); |
| src1.6.6/rdfw.cpp:1481 | DryRunSenseIds | location | C | True | False | if (location < 0) return; |
| src1.6.6/rdfw.cpp:1483 | DryRunSenseIds | location | C | True | False | if (!objects[i] \|\| objects[i]->location != location) continue; |
| src1.6.6/rdfw.cpp:1484 | DryRunSenseIds | hold_id,plate_id | C | True | False | if (static_cast<int>(i) == hold_id \|\| static_cast<int>(i) == plate_id) continue; |
| src1.6.6/rdfw.cpp:1487 | DryRunSenseIds | inside | C | True | False | if (small && small->inside > 0 && |
| src1.6.6/rdfw.cpp:1488 | DryRunSenseIds | inside | C | True | False | static_cast<std::size_t>(small->inside) < objects.size()) { |
| src1.6.6/rdfw.cpp:1490 | DryRunSenseIds | inside | C | True | False | std::dynamic_pointer_cast<Container>(objects[small->inside]); |
| src1.6.6/rdfw.cpp:1491 | DryRunSenseIds | isOpen | C | True | False | if (container && container->isOpen != 1) continue; |
| src1.6.6/rdfw.cpp:1541 | InitializeDynamicArrays | objectLocationVerified | C | True | False | objectLocationVerified.assign(max_size, false); |
| src1.6.6/rdfw.cpp:1542 | InitializeDynamicArrays | objectLocationInferredByMustNear | C | True | False | objectLocationInferredByMustNear.assign(max_size, false); |
| src1.6.6/rdfw.cpp:1543 | InitializeDynamicArrays | objectInsideVerified | C | True | False | objectInsideVerified.assign(max_size, false); |
| src1.6.6/rdfw.cpp:1544 | InitializeDynamicArrays | containerStateVerified | C | True | False | containerStateVerified.assign(max_size, false); |
| src1.6.6/rdfw.cpp:1545 | InitializeDynamicArrays | EvidenceSource,objectLocationSource | C | True | False | objectLocationSource.assign(max_size, EvidenceSource::UNKNOWN); |
| src1.6.6/rdfw.cpp:1546 | InitializeDynamicArrays | EvidenceSource,objectInsideSource | C | True | False | objectInsideSource.assign(max_size, EvidenceSource::UNKNOWN); |
| src1.6.6/rdfw.cpp:1547 | InitializeDynamicArrays | EvidenceSource,containerStateSource | C | True | False | containerStateSource.assign(max_size, EvidenceSource::UNKNOWN); |
| src1.6.6/rdfw.cpp:1548 | InitializeDynamicArrays | StateProvenance,locationProvenance | C | True | False | locationProvenance.assign(max_size, StateProvenance()); |
| src1.6.6/rdfw.cpp:1549 | InitializeDynamicArrays | StateProvenance,insideProvenance | C | True | False | insideProvenance.assign(max_size, StateProvenance()); |
| src1.6.6/rdfw.cpp:1550 | InitializeDynamicArrays | StateProvenance,containerProvenance | C | True | False | containerProvenance.assign(max_size, StateProvenance()); |
| src1.6.6/rdfw.cpp:1551 | InitializeDynamicArrays | StateProvenance,holdProvenance | C | True | False | holdProvenance = StateProvenance(); |
| src1.6.6/rdfw.cpp:1552 | InitializeDynamicArrays | StateProvenance,plateProvenance | C | True | False | plateProvenance = StateProvenance(); |
| src1.6.6/rdfw.cpp:1779 | Plan | location | C | True | False | location = UNKNOWN; |
| src1.6.6/rdfw.cpp:1780 | Plan | hold | A | True | False | hold = nullptr; |
| src1.6.6/rdfw.cpp:1781 | Plan | hold_id | C | True | False | hold_id = 0; |
| src1.6.6/rdfw.cpp:1787 | Plan | objectLocationVerified | A | True | False | fill(objectLocationVerified.begin(), objectLocationVerified.end(), false); |
| src1.6.6/rdfw.cpp:1788 | Plan | objectLocationInferredByMustNear | A | True | False | fill(objectLocationInferredByMustNear.begin(), objectLocationInferredByMustNear.end(), false); |
| src1.6.6/rdfw.cpp:1789 | Plan | objectInsideVerified | A | True | False | fill(objectInsideVerified.begin(), objectInsideVerified.end(), false); |
| src1.6.6/rdfw.cpp:1790 | Plan | containerStateVerified | A | True | False | fill(containerStateVerified.begin(), containerStateVerified.end(), false); |
| src1.6.6/rdfw.cpp:1791 | Plan | EvidenceSource,objectLocationSource | A | True | False | fill(objectLocationSource.begin(), objectLocationSource.end(), EvidenceSource::UNKNOWN); |
| src1.6.6/rdfw.cpp:1792 | Plan | EvidenceSource,objectInsideSource | A | True | False | fill(objectInsideSource.begin(), objectInsideSource.end(), EvidenceSource::UNKNOWN); |
| src1.6.6/rdfw.cpp:1793 | Plan | EvidenceSource,containerStateSource | A | True | False | fill(containerStateSource.begin(), containerStateSource.end(), EvidenceSource::UNKNOWN); |
| src1.6.6/rdfw.cpp:1794 | Plan | StateProvenance,locationProvenance | A | True | False | fill(locationProvenance.begin(), locationProvenance.end(), StateProvenance()); |
| src1.6.6/rdfw.cpp:1795 | Plan | StateProvenance,insideProvenance | A | True | False | fill(insideProvenance.begin(), insideProvenance.end(), StateProvenance()); |
| src1.6.6/rdfw.cpp:1796 | Plan | StateProvenance,containerProvenance | A | True | False | fill(containerProvenance.begin(), containerProvenance.end(), StateProvenance()); |
| src1.6.6/rdfw.cpp:1797 | Plan | StateProvenance,holdProvenance | A | True | False | holdProvenance = StateProvenance(); |
| src1.6.6/rdfw.cpp:1798 | Plan | StateProvenance,plateProvenance | A | True | False | plateProvenance = StateProvenance(); |
| src1.6.6/rdfw.cpp:1954 | Plan | location | A | True | False | LOG("[TradeoffEvidence] probing current location before decisions\n"); |
| src1.6.6/rdfw.cpp:2487 | Cons_plan | location | A | True | False | if (cons.Y.empty() \|\| !cons.Y[0] \|\| cons.Y[0]->location < 0 \|\| |
| src1.6.6/rdfw.cpp:2488 | Cons_plan | location | A | True | False | !EnsureLocationCapacity(cons.Y[0]->location)) continue; |
| src1.6.6/rdfw.cpp:2489 | Cons_plan | location | A | True | False | if(cons.X[0]->location!=cons.Y[0]->location) putdown_cons[cons.X[0]->id][cons.Y[0]->location]++; |
| src1.6.6/rdfw.cpp:2490 | Cons_plan | hold_id,location,plate_id | A | True | False | else if(cons.X[0]->id==plate_id\|\|cons.X[0]->id==hold_id) putdown_cons[cons.X[0]->id][cons.Y[0]->location]++; |
| src1.6.6/rdfw.cpp:2492 | Cons_plan | inside | A | True | False | else if(cons.behave=="inside"\|\|cons.behave=="in") { |
| src1.6.6/rdfw.cpp:2495 | Cons_plan | inside | A | True | False | if(small && small->inside!=cons.Y[0]->id) putin_cons[cons.X[0]->id][cons.Y[0]->id]++; |
| src1.6.6/rdfw.cpp:2499 | Cons_plan | location | A | True | False | if(cons.Y[0]->location!=cons.X[0]->location) //如果约束没有触犯 |
| src1.6.6/rdfw.cpp:2501 | Cons_plan | location | A | True | False | if(cons.Y[0]->location!=UNKNOWN) move_cons[cons.X[0]->id][cons.Y[0]->location]++; |
| src1.6.6/rdfw.cpp:2502 | Cons_plan | location | A | True | False | if(cons.X[0]->location!=UNKNOWN) move_cons[cons.Y[0]->id][cons.X[0]->location]++; |
| src1.6.6/rdfw.cpp:2505 | Cons_plan | plate | A | True | False | else if(cons.behave == "plate") toplate_cons[cons.X[0]->id]++; |
| src1.6.6/rdfw.cpp:2508 | Cons_plan | isOpen | A | True | False | if(cont && cont->isOpen!=1) open_cons[cons.X[0]->id]++; |
| src1.6.6/rdfw.cpp:2513 | Cons_plan | isOpen | A | True | False | if(cont && cont->isOpen==1) close_cons[cons.X[0]->id]++; |
| src1.6.6/rdfw.cpp:2523 | Cons_plan | location | A | True | False | cons.X[0]->location==cons.Y[0]->location) { |
| src1.6.6/rdfw.cpp:2525 | Cons_plan | inside | A | True | False | if(small && small->inside!=cons.Y[0]->id) cons.X[0]->is_keep++; |
| src1.6.6/rdfw.cpp:2534 | Cons_plan | location | A | True | False | if (x_obj->location != UNKNOWN && x_obj->location == y_obj->location) { |
| src1.6.6/rdfw.cpp:2541 | Cons_plan | plate,plate_id | A | True | False | else if(cons.behave=="plate"&& plate_id==cons.X[0]->id)fromplate_cons[cons.X[0]->id]++; |
| src1.6.6/rdfw.cpp:2542 | Cons_plan | inside | A | True | False | else if(cons.behave=="inside"\|\|cons.behave=="in") |
| src1.6.6/rdfw.cpp:2546 | Cons_plan | inside | A | True | False | if(small && small->inside==cons.Y[0]->id)  takeout_cons[cons.X[0]->id][cons.Y[0]->id]++; |
| src1.6.6/rdfw.cpp:2550 | Cons_plan | isOpen | A | True | False | if(cont && cont->isOpen!=1) open_cons[cons.X[0]->id]++; |
| src1.6.6/rdfw.cpp:2554 | Cons_plan | isOpen | A | True | False | if(cont && cont->isOpen!=1) close_cons[cons.X[0]->id]++; |
| src1.6.6/rdfw.cpp:2567 | Cons_plan | location | A | True | False | cons.Y[0]->location >= 0 && EnsureLocationCapacity(cons.Y[0]->location)) |
| src1.6.6/rdfw.cpp:2568 | Cons_plan | location | A | True | False | putdown_cons[cons.X[0]->id][cons.Y[0]->location]++; |
| src1.6.6/rdfw.cpp:2569 | Cons_plan | location | A | True | False | else if(cons.behave=="goto" && cons.X[0]->location >= 0 && |
| src1.6.6/rdfw.cpp:2570 | Cons_plan | location | A | True | False | EnsureLocationCapacity(cons.X[0]->location)) goto_cons[cons.X[0]->location]++; |
| src1.6.6/rdfw.cpp:2577 | Cons_plan | hold_id,location | A | True | False | if(IsValidObjectId(hold_id) && location >= 0 && EnsureLocationCapacity(location)) { |
| src1.6.6/rdfw.cpp:2578 | Cons_plan | hold_id | A | True | False | x=hold_id; |
| src1.6.6/rdfw.cpp:2579 | Cons_plan | location | A | True | False | if(objects[x]->is_keep>putdown1_cons[x]+putdown_cons[x][location]+fromplate_cons[x]){ |
| src1.6.6/rdfw.cpp:2580 | Cons_plan | hold | A | True | False | cout<<"the hold object must putdown here!"<<endl; |
| src1.6.6/rdfw.cpp:2584 | Cons_plan | location,plate_id | A | True | False | if(IsValidObjectId(plate_id) && location >= 0 && EnsureLocationCapacity(location)) |
| src1.6.6/rdfw.cpp:2586 | Cons_plan | plate_id | A | True | False | x=plate_id; |
| src1.6.6/rdfw.cpp:2587 | Cons_plan | location | A | True | False | if(objects[x]->is_keep>putdown1_cons[x]+putdown_cons[x][location]+fromplate_cons[x]){ |
| src1.6.6/rdfw.cpp:2588 | Cons_plan | plate | A | True | False | cout<<"the plate object must putdown here!"<<endl; |
| src1.6.6/rdfw.cpp:2589 | Cons_plan | hold_id | A | True | False | if(hold_id>0) PutDown(hold_id); |
| src1.6.6/rdfw.cpp:2613 | FilterConstraintsByTaskConflicts | location | A | True | False | if ((task.behave == "goto" && has_x && task.X[0]->location == loc) \|\| |
| src1.6.6/rdfw.cpp:2614 | FilterConstraintsByTaskConflicts | location | A | True | False | (task.behave == "putin" && has_y && task.Y[0]->location == loc) \|\| |
| src1.6.6/rdfw.cpp:2615 | FilterConstraintsByTaskConflicts | location | A | True | False | (task.behave == "putin" && has_x && task.X[0]->location == loc)\|\| |
| src1.6.6/rdfw.cpp:2616 | FilterConstraintsByTaskConflicts | location | A | True | False | (task.behave == "puton" && has_y && task.Y[0]->location == loc)\|\| |
| src1.6.6/rdfw.cpp:2617 | FilterConstraintsByTaskConflicts | location | A | True | False | (task.behave == "puton" && has_x && task.X[0]->location == loc)\|\| |
| src1.6.6/rdfw.cpp:2618 | FilterConstraintsByTaskConflicts | location | A | True | False | (task.behave == "open" && has_x && task.X[0]->location == loc)\|\| |
| src1.6.6/rdfw.cpp:2619 | FilterConstraintsByTaskConflicts | location | A | True | False | (task.behave == "close" && has_x && task.X[0]->location == loc)\|\| |
| src1.6.6/rdfw.cpp:2620 | FilterConstraintsByTaskConflicts | location | A | True | False | (task.behave == "pickup" && has_x && task.X[0]->location == loc)\|\| |
| src1.6.6/rdfw.cpp:2621 | FilterConstraintsByTaskConflicts | location | A | True | False | (task.behave == "give" && has_x && task.X[0]->location == loc)\|\| |
| src1.6.6/rdfw.cpp:2622 | FilterConstraintsByTaskConflicts | location | A | True | False | (task.behave == "give" && has_y && task.Y[0]->location == loc)\|\| |
| src1.6.6/rdfw.cpp:2623 | FilterConstraintsByTaskConflicts | location | A | True | False | (task.behave == "takeout" && has_y && task.Y[0]->location == loc)) { |
| src1.6.6/rdfw.cpp:2625 | FilterConstraintsByTaskConflicts | location | A | True | False | cout << "[FilterConstraintsByTaskConflicts] Conflict found between goto_cons at location " << loc << " and task " << task.behave << endl; |
| src1.6.6/rdfw.cpp:2636 | FilterConstraintsByTaskConflicts | location | A | True | False | cout << "[FilterConstraintsByTaskConflicts] Conflict found between goto_cons at location " << loc << " with conflict count " << conflict_count << endl; |
| src1.6.6/rdfw.cpp:2644 | FilterConstraintsByTaskConflicts | location | A | True | False | cout << "[FilterConstraintsByTaskConflicts] Discarded goto_cons at location " << max_effect_loc << " due to " << max_effect << " conflicts." << endl; |
| src1.6.6/rdfw.cpp:2649 | FilterConstraintsByTaskConflicts | location | A | True | False | cout << "[FilterConstraintsByTaskConflicts] Discarded goto_cons at location " << it->first << " due to " << it->second << " conflicts." << endl; |
| src1.6.6/rdfw.cpp:2827 | CalculateTaskRisk | inside | A | True | False | if(small->inside!=t.Y[0]->id) return 0;//如果任务满足 |
| src1.6.6/rdfw.cpp:2828 | CalculateTaskRisk | location | A | True | False | t.risk+=takeout_cons[t.X[0]->id][t.Y[0]->id]+goto_risk(t.Y[0]->location); |
| src1.6.6/rdfw.cpp:2835 | CalculateTaskRisk | inside | A | True | False | if(small->inside==t.Y[0]->id) return 0; |
| src1.6.6/rdfw.cpp:2837 | CalculateTaskRisk | location | A | True | False | if (t.Y[0]->location >= 0 && EnsureLocationCapacity(t.Y[0]->location)) |
| src1.6.6/rdfw.cpp:2838 | CalculateTaskRisk | location | A | True | False | t.risk += move_cons[t.X[0]->id][t.Y[0]->location]; |
| src1.6.6/rdfw.cpp:2839 | CalculateTaskRisk | location | A | True | False | if(t.X[0]->location!=t.Y[0]->location) t.risk+=goto_risk(t.Y[0]->location); |
| src1.6.6/rdfw.cpp:2844 | CalculateTaskRisk | location | A | True | False | if (t.Y[0]->location >= 0 && EnsureLocationCapacity(t.Y[0]->location)) |
| src1.6.6/rdfw.cpp:2845 | CalculateTaskRisk | location | A | True | False | t.risk+= putdown_cons[t.X[0]->id][t.Y[0]->location]+move_cons[t.X[0]->id][t.Y[0]->location]; |
| src1.6.6/rdfw.cpp:2847 | CalculateTaskRisk | location | A | True | False | if(t.X[0]->location!=t.Y[0]->location) t.risk+=goto_risk(t.Y[0]->location); |
| src1.6.6/rdfw.cpp:2851 | CalculateTaskRisk | location | A | True | False | int loc = t.X[0]->location; |
| src1.6.6/rdfw.cpp:2859 | CalculateTaskRisk | location | A | True | False | else if(t.behave=="open") t.risk+=open_cons[t.X[0]->id]+goto_risk(t.X[0]->location); |
| src1.6.6/rdfw.cpp:2860 | CalculateTaskRisk | location | A | True | False | else if(t.behave=="close") t.risk+=close_cons[t.X[0]->id]+goto_risk(t.X[0]->location); |
| src1.6.6/rdfw.cpp:2868 | CalculateTaskRisk | location | A | True | False | if (human->location >= 0 && EnsureLocationCapacity(human->location)) |
| src1.6.6/rdfw.cpp:2869 | CalculateTaskRisk | location | A | True | False | t.risk += move_cons[t.X[0]->id][human->location]; |
| src1.6.6/rdfw.cpp:2870 | CalculateTaskRisk | location | A | True | False | if(t.X[0]->location!=human->location) t.risk+=goto_risk(human->location); |
| src1.6.6/rdfw.cpp:2875 | CalculateTaskRisk | location | D | True | False | // goto targets an object's location; the target object itself is untouched. |
| src1.6.6/rdfw.cpp:2896 | CalculateTaskRisk | location | A | True | False | if (other && other->location == t.X[0]->location && t.X[0]->location != UNKNOWN) { |
| src1.6.6/rdfw.cpp:2914 | CalculateStepRisk | location | A | True | False | if(t.X[0]->location!=location && t.X[0]->location >= 0) { |
| src1.6.6/rdfw.cpp:2915 | CalculateStepRisk | location | A | True | False | if (!EnsureLocationCapacity(t.X[0]->location)) return 0; |
| src1.6.6/rdfw.cpp:2916 | CalculateStepRisk | location | A | True | False | t.risk+=goto_cons[t.X[0]->location]; |
| src1.6.6/rdfw.cpp:2920 | CalculateStepRisk | inside | A | True | False | if(small->inside!=UNKNOWN&&small->inside!=NONE && |
| src1.6.6/rdfw.cpp:2921 | CalculateStepRisk | inside | A | True | False | IsValidObjectId(small->inside)) |
| src1.6.6/rdfw.cpp:2922 | CalculateStepRisk | inside | A | True | False | t.risk+=open_cons[small->inside]+takeout_cons[small->id][small->inside]; |
| src1.6.6/rdfw.cpp:2923 | CalculateStepRisk | inside | A | True | False | else if(small->inside==NONE) t.risk+=pickup_cons[small->id]; |
| src1.6.6/rdfw.cpp:2944 | EnsureLocationCapacity | inside | D | True | False | // Normal inputs stay inside the preallocated range.  Keep this hot path |
| src1.6.6/rdfw.cpp:2945 | EnsureLocationCapacity | location | D | True | False | // constant-time; full row scans are needed only when a new location column |
| src1.6.6/rdfw.cpp:3031 | EnsureEvidenceCapacity | objectLocationVerified | C | True | False | if (objectLocationVerified.size() < required) |
| src1.6.6/rdfw.cpp:3032 | EnsureEvidenceCapacity | objectLocationVerified | C | True | False | objectLocationVerified.resize(required, false); |
| src1.6.6/rdfw.cpp:3033 | EnsureEvidenceCapacity | objectLocationInferredByMustNear | C | True | False | if (objectLocationInferredByMustNear.size() < required) |
| src1.6.6/rdfw.cpp:3034 | EnsureEvidenceCapacity | objectLocationInferredByMustNear | C | True | False | objectLocationInferredByMustNear.resize(required, false); |
| src1.6.6/rdfw.cpp:3035 | EnsureEvidenceCapacity | objectInsideVerified | C | True | False | if (objectInsideVerified.size() < required) |
| src1.6.6/rdfw.cpp:3036 | EnsureEvidenceCapacity | objectInsideVerified | C | True | False | objectInsideVerified.resize(required, false); |
| src1.6.6/rdfw.cpp:3037 | EnsureEvidenceCapacity | containerStateVerified | C | True | False | if (containerStateVerified.size() < required) |
| src1.6.6/rdfw.cpp:3038 | EnsureEvidenceCapacity | containerStateVerified | C | True | False | containerStateVerified.resize(required, false); |
| src1.6.6/rdfw.cpp:3039 | EnsureEvidenceCapacity | objectLocationSource | C | True | False | if (objectLocationSource.size() < required) |
| src1.6.6/rdfw.cpp:3040 | EnsureEvidenceCapacity | EvidenceSource,objectLocationSource | C | True | False | objectLocationSource.resize(required, EvidenceSource::UNKNOWN); |
| src1.6.6/rdfw.cpp:3041 | EnsureEvidenceCapacity | objectInsideSource | C | True | False | if (objectInsideSource.size() < required) |
| src1.6.6/rdfw.cpp:3042 | EnsureEvidenceCapacity | EvidenceSource,objectInsideSource | C | True | False | objectInsideSource.resize(required, EvidenceSource::UNKNOWN); |
| src1.6.6/rdfw.cpp:3043 | EnsureEvidenceCapacity | containerStateSource | C | True | False | if (containerStateSource.size() < required) |
| src1.6.6/rdfw.cpp:3044 | EnsureEvidenceCapacity | EvidenceSource,containerStateSource | C | True | False | containerStateSource.resize(required, EvidenceSource::UNKNOWN); |
| src1.6.6/rdfw.cpp:3045 | EnsureEvidenceCapacity | locationProvenance | C | True | False | if (locationProvenance.size() < required) locationProvenance.resize(required); |
| src1.6.6/rdfw.cpp:3046 | EnsureEvidenceCapacity | insideProvenance | C | True | False | if (insideProvenance.size() < required) insideProvenance.resize(required); |
| src1.6.6/rdfw.cpp:3047 | EnsureEvidenceCapacity | containerProvenance | C | True | False | if (containerProvenance.size() < required) containerProvenance.resize(required); |
| src1.6.6/rdfw.cpp:3051 | MutableProvenance | MutableProvenance,StateProvenance | C | True | False | StateProvenance& RDFW::MutableProvenance(StateField field, unsigned int id) { |
| src1.6.6/rdfw.cpp:3052 | MutableProvenance | holdProvenance | C | True | False | if (field == StateField::HOLD) return holdProvenance; |
| src1.6.6/rdfw.cpp:3053 | MutableProvenance | plateProvenance | C | True | False | if (field == StateField::PLATE) return plateProvenance; |
| src1.6.6/rdfw.cpp:3054 | MutableProvenance | locationProvenance | C | True | False | if (field == StateField::LOCATION) return locationProvenance[id]; |
| src1.6.6/rdfw.cpp:3055 | MutableProvenance | insideProvenance | C | True | False | if (field == StateField::INSIDE) return insideProvenance[id]; |
| src1.6.6/rdfw.cpp:3056 | MutableProvenance | containerProvenance | C | True | False | return containerProvenance[id]; |
| src1.6.6/rdfw.cpp:3059 | Provenance | Provenance,StateProvenance | D | True | False | const StateProvenance& RDFW::Provenance(StateField field, unsigned int id) const { |
| src1.6.6/rdfw.cpp:3060 | Provenance | StateProvenance | D | True | False | static const StateProvenance empty; |
| src1.6.6/rdfw.cpp:3061 | Provenance | holdProvenance | D | True | False | if (field == StateField::HOLD) return holdProvenance; |
| src1.6.6/rdfw.cpp:3062 | Provenance | plateProvenance | D | True | False | if (field == StateField::PLATE) return plateProvenance; |
| src1.6.6/rdfw.cpp:3063 | Provenance | StateProvenance | D | True | False | const std::vector<StateProvenance>& records = field == StateField::LOCATION |
| src1.6.6/rdfw.cpp:3064 | Provenance | locationProvenance | D | True | False | ? locationProvenance : field == StateField::INSIDE |
| src1.6.6/rdfw.cpp:3065 | Provenance | containerProvenance,insideProvenance | D | True | False | ? insideProvenance : containerProvenance; |
| src1.6.6/rdfw.cpp:3069 | SetHold | EvidenceSource | C | True | False | void RDFW::SetHold(const shared_ptr<SmallObject>& item, EvidenceSource source) { |
| src1.6.6/rdfw.cpp:3070 | SetHold | plate_id | C | True | False | const int old_plate = plate_id; |
| src1.6.6/rdfw.cpp:3072 | SetHold | EvidenceSource | C | True | False | const bool verified = stage == 1 \|\| source == EvidenceSource::ACTION_SUCCESS; |
| src1.6.6/rdfw.cpp:3073 | SetHold | UpdateProvenance,hold_id | C | True | False | UpdateProvenance(StateField::HOLD, 0, hold_id, verified, source); |
| src1.6.6/rdfw.cpp:3079 | SetHold | plate_id | C | True | False | if (old_plate != plate_id) |
| src1.6.6/rdfw.cpp:3080 | SetHold | UpdateProvenance,plate_id | C | True | False | UpdateProvenance(StateField::PLATE, 0, plate_id, verified, source); |
| src1.6.6/rdfw.cpp:3083 | SetPlate | EvidenceSource | C | True | False | void RDFW::SetPlate(const shared_ptr<SmallObject>& item, EvidenceSource source) { |
| src1.6.6/rdfw.cpp:3084 | SetPlate | hold_id | C | True | False | const int old_hold = hold_id; |
| src1.6.6/rdfw.cpp:3086 | SetPlate | EvidenceSource | C | True | False | const bool verified = stage == 1 \|\| source == EvidenceSource::ACTION_SUCCESS; |
| src1.6.6/rdfw.cpp:3087 | SetPlate | hold_id | C | True | False | if (old_hold != hold_id) |
| src1.6.6/rdfw.cpp:3088 | SetPlate | UpdateProvenance,hold_id | C | True | False | UpdateProvenance(StateField::HOLD, 0, hold_id, verified, source); |
| src1.6.6/rdfw.cpp:3089 | SetPlate | UpdateProvenance,plate_id | C | True | False | UpdateProvenance(StateField::PLATE, 0, plate_id, verified, source); |
| src1.6.6/rdfw.cpp:3098 | HasContradictoryEvidence | Provenance,StateProvenance | A | True | False | const StateProvenance& p = Provenance(field, id); |
| src1.6.6/rdfw.cpp:3104 | ReceiveWeakClaim | EvidenceSource | C | True | False | EvidenceSource source) { |
| src1.6.6/rdfw.cpp:3106 | ReceiveWeakClaim | MutableProvenance,StateProvenance | C | True | False | StateProvenance& p = MutableProvenance(field, id); |
| src1.6.6/rdfw.cpp:3108 | ReceiveWeakClaim | EvidenceSource | C | True | False | (p.received.source == EvidenceSource::INITIAL \|\| |
| src1.6.6/rdfw.cpp:3109 | ReceiveWeakClaim | EvidenceSource | C | True | False | p.received.source == EvidenceSource::ASK_ANSWER \|\| |
| src1.6.6/rdfw.cpp:3110 | ReceiveWeakClaim | EvidenceSource | C | True | False | p.received.source == EvidenceSource::EXPLICIT_INFO); |
| src1.6.6/rdfw.cpp:3121 | MarkUnresolved | MutableProvenance,StateProvenance | C | True | False | StateProvenance& p = MutableProvenance(field, id); |
| src1.6.6/rdfw.cpp:3122 | MarkUnresolved | EvidenceSource | C | True | False | if (p.resolved_value != UNKNOWN \|\| p.resolved_source != EvidenceSource::UNKNOWN) |
| src1.6.6/rdfw.cpp:3125 | MarkUnresolved | EvidenceSource | C | True | False | p.resolved_source = EvidenceSource::UNKNOWN; |
| src1.6.6/rdfw.cpp:3130 | MarkUnresolved | EvidenceSource,objectLocationSource,objectLocationVerified | C | True | False | if (field == StateField::LOCATION) { objectLocationVerified[id]=false; objectLocationSource[id]=EvidenceSource::UNKNOWN; } |
| src1.6.6/rdfw.cpp:3131 | MarkUnresolved | EvidenceSource,objectInsideSource,objectInsideVerified | C | True | False | if (field == StateField::INSIDE) { objectInsideVerified[id]=false; objectInsideSource[id]=EvidenceSource::UNKNOWN; } |
| src1.6.6/rdfw.cpp:3132 | MarkUnresolved | EvidenceSource,containerStateSource,containerStateVerified | C | True | False | if (field == StateField::CONTAINER_STATE) { containerStateVerified[id]=false; containerStateSource[id]=EvidenceSource::UNKNOWN; } |
| src1.6.6/rdfw.cpp:3135 | UpdateProvenance | UpdateProvenance | C | True | False | void RDFW::UpdateProvenance(StateField field, unsigned int id, int value, |
| src1.6.6/rdfw.cpp:3136 | UpdateProvenance | EvidenceSource | C | True | False | bool verified, EvidenceSource source) { |
| src1.6.6/rdfw.cpp:3138 | UpdateProvenance | MutableProvenance,StateProvenance | C | True | False | StateProvenance& p = MutableProvenance(field, id); |
| src1.6.6/rdfw.cpp:3139 | UpdateProvenance | EvidenceSource | C | True | False | const bool derived = source == EvidenceSource::CONSTRAINT_DERIVED \|\| |
| src1.6.6/rdfw.cpp:3140 | UpdateProvenance | EvidenceSource | C | True | False | source == EvidenceSource::RELATION_DERIVED \|\| |
| src1.6.6/rdfw.cpp:3141 | UpdateProvenance | EvidenceSource | C | True | False | source == EvidenceSource::CONSTRAINT_HEURISTIC; |
| src1.6.6/rdfw.cpp:3142 | UpdateProvenance | EvidenceSource | C | True | False | if (!derived && source != EvidenceSource::UNKNOWN) { |
| src1.6.6/rdfw.cpp:3160 | UpdateProvenance | EvidenceSource | C | True | False | p.resolved_verified = verified && value != UNKNOWN && source != EvidenceSource::CONSTRAINT_HEURISTIC; |
| src1.6.6/rdfw.cpp:3162 | UpdateProvenance | objectLocationSource,objectLocationVerified | C | True | False | if (field == StateField::LOCATION) { objectLocationVerified[id]=p.resolved_verified; objectLocationSource[id]=source; } |
| src1.6.6/rdfw.cpp:3163 | UpdateProvenance | objectInsideSource,objectInsideVerified | C | True | False | if (field == StateField::INSIDE) { objectInsideVerified[id]=p.resolved_verified; objectInsideSource[id]=source; } |
| src1.6.6/rdfw.cpp:3164 | UpdateProvenance | containerStateSource,containerStateVerified | C | True | False | if (field == StateField::CONTAINER_STATE) { containerStateVerified[id]=p.resolved_verified; containerStateSource[id]=source; } |
| src1.6.6/rdfw.cpp:3170 | DependOn | MutableProvenance,StateProvenance | C | True | False | StateProvenance& p = MutableProvenance(derived_field, derived_id); |
| src1.6.6/rdfw.cpp:3172 | DependOn | Provenance,StateProvenance | C | True | False | const StateProvenance& support = Provenance(support_field, support_id); |
| src1.6.6/rdfw.cpp:3179 | SetConstraintSupport | MutableProvenance | C | True | False | MutableProvenance(field, id).support_constraint_index = index; |
| src1.6.6/rdfw.cpp:3183 | RecordConstraintSupports | MutableProvenance,StateProvenance | C | True | False | StateProvenance& p = MutableProvenance(field, id); |
| src1.6.6/rdfw.cpp:3214 | ResolutionEligible | Provenance,StateProvenance | B | True | False | const StateProvenance& p = Provenance(field, id); |
| src1.6.6/rdfw.cpp:3228 | ResolutionEligible | holdProvenance,plateProvenance | B | True | False | const auto& other = field == StateField::HOLD ? plateProvenance : holdProvenance; |
| src1.6.6/rdfw.cpp:3232 | ResolutionEligible | holdProvenance | B | True | False | ((holdProvenance.resolved_verified && holdProvenance.resolved_value == int(id)) \|\| |
| src1.6.6/rdfw.cpp:3233 | ResolutionEligible | plateProvenance | B | True | False | (plateProvenance.resolved_verified && plateProvenance.resolved_value == int(id)))) return false; |
| src1.6.6/rdfw.cpp:3234 | ResolutionEligible | EvidenceSource | B | True | False | if (p.resolved_source == EvidenceSource::UNKNOWN \|\| |
| src1.6.6/rdfw.cpp:3235 | ResolutionEligible | EvidenceSource | B | True | False | p.resolved_source == EvidenceSource::CONSTRAINT_HEURISTIC) return false; |
| src1.6.6/rdfw.cpp:3240 | ResolvedState | ResolvedState | B | True | False | StateClaim RDFW::ResolvedState(StateField field, unsigned int id) const { |
| src1.6.6/rdfw.cpp:3242 | ResolvedState | DependenciesCurrent | B | True | False | if (!ResolutionEligible(field,id) \|\| !DependenciesCurrent(field,id)) return StateClaim(); |
| src1.6.6/rdfw.cpp:3243 | ResolvedState | Provenance | B | True | False | const auto& p=Provenance(field,id); |
| src1.6.6/rdfw.cpp:3247 | DependenciesCurrent | DependenciesCurrent | B | True | False | bool RDFW::DependenciesCurrent(StateField field, unsigned int id) const { |
| src1.6.6/rdfw.cpp:3254 | DependenciesCurrentDepth | Provenance,StateProvenance | B | True | False | const StateProvenance& p = Provenance(field, id); |
| src1.6.6/rdfw.cpp:3271 | DependenciesCurrentDepth | Provenance,StateProvenance | B | True | False | const StateProvenance& support = Provenance(d.field, d.id); |
| src1.6.6/rdfw.cpp:3281 | MarkDirectLocationEvidence | EvidenceSource | C | True | False | EvidenceSource source) { |
| src1.6.6/rdfw.cpp:3283 | MarkDirectLocationEvidence | objectLocationVerified | C | True | False | objectLocationVerified[id] = verified; |
| src1.6.6/rdfw.cpp:3284 | MarkDirectLocationEvidence | objectLocationSource | C | True | False | objectLocationSource[id] = source; |
| src1.6.6/rdfw.cpp:3285 | MarkDirectLocationEvidence | location | C | True | False | const int value = id < objects.size() && objects[id] ? objects[id]->location : UNKNOWN; |
| src1.6.6/rdfw.cpp:3286 | MarkDirectLocationEvidence | UpdateProvenance | C | True | False | UpdateProvenance(StateField::LOCATION, id, value, verified, source); |
| src1.6.6/rdfw.cpp:3287 | MarkDirectLocationEvidence | EvidenceSource | C | True | False | if (source == EvidenceSource::CONSTRAINT_DERIVED \|\| source == EvidenceSource::CONSTRAINT_HEURISTIC) |
| src1.6.6/rdfw.cpp:3289 | MarkDirectLocationEvidence | objectLocationInferredByMustNear | C | True | False | objectLocationInferredByMustNear[id] = |
| src1.6.6/rdfw.cpp:3290 | MarkDirectLocationEvidence | EvidenceSource | C | True | False | source == EvidenceSource::CONSTRAINT_DERIVED \|\| |
| src1.6.6/rdfw.cpp:3291 | MarkDirectLocationEvidence | EvidenceSource | C | True | False | source == EvidenceSource::CONSTRAINT_HEURISTIC; |
| src1.6.6/rdfw.cpp:3294 | SetInsideEvidence | EvidenceSource | C | True | False | void RDFW::SetInsideEvidence(unsigned int id, bool verified, EvidenceSource source) { |
| src1.6.6/rdfw.cpp:3296 | SetInsideEvidence | objectInsideVerified | C | True | False | objectInsideVerified[id] = verified; |
| src1.6.6/rdfw.cpp:3297 | SetInsideEvidence | objectInsideSource | C | True | False | objectInsideSource[id] = source; |
| src1.6.6/rdfw.cpp:3299 | SetInsideEvidence | UpdateProvenance,inside | C | True | False | UpdateProvenance(StateField::INSIDE, id, small ? small->inside : UNKNOWN, verified, source); |
| src1.6.6/rdfw.cpp:3302 | SetContainerEvidence | EvidenceSource | C | True | False | void RDFW::SetContainerEvidence(unsigned int id, bool verified, EvidenceSource source) { |
| src1.6.6/rdfw.cpp:3304 | SetContainerEvidence | containerStateVerified | C | True | False | containerStateVerified[id] = verified; |
| src1.6.6/rdfw.cpp:3305 | SetContainerEvidence | containerStateSource | C | True | False | containerStateSource[id] = source; |
| src1.6.6/rdfw.cpp:3307 | SetContainerEvidence | UpdateProvenance | C | True | False | UpdateProvenance(StateField::CONTAINER_STATE, id, |
| src1.6.6/rdfw.cpp:3308 | SetContainerEvidence | isOpen | C | True | False | container ? container->isOpen : UNKNOWN, verified, source); |
| src1.6.6/rdfw.cpp:3309 | SetContainerEvidence | EvidenceSource | C | True | False | if (source == EvidenceSource::CONSTRAINT_DERIVED \|\| source == EvidenceSource::CONSTRAINT_HEURISTIC) |
| src1.6.6/rdfw.cpp:3313 | LocationSource | EvidenceSource,LocationSource | D | True | False | EvidenceSource RDFW::LocationSource(unsigned int id) const { |
| src1.6.6/rdfw.cpp:3314 | LocationSource | EvidenceSource,objectLocationSource | D | True | False | return id < objectLocationSource.size() ? objectLocationSource[id] : EvidenceSource::UNKNOWN; |
| src1.6.6/rdfw.cpp:3316 | InsideSource | EvidenceSource,InsideSource | D | True | False | EvidenceSource RDFW::InsideSource(unsigned int id) const { |
| src1.6.6/rdfw.cpp:3317 | InsideSource | EvidenceSource,objectInsideSource | D | True | False | return id < objectInsideSource.size() ? objectInsideSource[id] : EvidenceSource::UNKNOWN; |
| src1.6.6/rdfw.cpp:3319 | ContainerSource | ContainerSource,EvidenceSource | D | True | False | EvidenceSource RDFW::ContainerSource(unsigned int id) const { |
| src1.6.6/rdfw.cpp:3320 | ContainerSource | EvidenceSource,containerStateSource | D | True | False | return id < containerStateSource.size() ? containerStateSource[id] : EvidenceSource::UNKNOWN; |
| src1.6.6/rdfw.cpp:3332 | IsLocationVerified | IsLocationVerified | B | True | False | bool RDFW::IsLocationVerified(unsigned int id) const { |
| src1.6.6/rdfw.cpp:3333 | IsLocationVerified | ResolvedState | B | True | False | return ResolvedState(StateField::LOCATION, id).present; |
| src1.6.6/rdfw.cpp:3336 | IsInsideVerified | IsInsideVerified | B | True | False | bool RDFW::IsInsideVerified(unsigned int id) const { |
| src1.6.6/rdfw.cpp:3337 | IsInsideVerified | ResolvedState | B | True | False | return ResolvedState(StateField::INSIDE, id).present; |
| src1.6.6/rdfw.cpp:3340 | IsContainerStateVerified | IsContainerStateVerified | B | True | False | bool RDFW::IsContainerStateVerified(unsigned int id) const { |
| src1.6.6/rdfw.cpp:3341 | IsContainerStateVerified | ResolvedState | B | True | False | return ResolvedState(StateField::CONTAINER_STATE, id).present; |
| src1.6.6/rdfw.cpp:3348 | IsAbsentFromSensedLocation | hold_id,plate_id | C | True | False | hold_id == static_cast<int>(id) \|\| plate_id == static_cast<int>(id)) |
| src1.6.6/rdfw.cpp:3353 | IsAbsentFromSensedLocation | location | D | True | False | // A closed container can hide a small object at this location. |
| src1.6.6/rdfw.cpp:3476 | HoldSmallObject | plate_id | A | True | False | if (plate_id == a) |
| src1.6.6/rdfw.cpp:3478 | HoldSmallObject | hold_id | A | True | False | if (hold_id != NONE && !PutDown(hold_id)) return false; |
| src1.6.6/rdfw.cpp:3481 | HoldSmallObject | FactValue | B | True | False | else if(FactValue(StateField::HOLD)==static_cast<int>(a)) return true; |
| src1.6.6/rdfw.cpp:3482 | HoldSmallObject | hold_id | A | True | False | if (hold_id != NONE && !PutDown(hold_id)) return false; |
| src1.6.6/rdfw.cpp:3483 | HoldSmallObject | location | A | True | False | if(location!=target_small->location && !Move(target_small->location)) return false; |
| src1.6.6/rdfw.cpp:3484 | HoldSmallObject | inside | A | True | False | if(target_small->inside==NONE) return PickUp(a); |
| src1.6.6/rdfw.cpp:3485 | HoldSmallObject | inside | A | True | False | else if(target_small->inside!=UNKNOWN)//说明小物体在容器里面 |
| src1.6.6/rdfw.cpp:3487 | HoldSmallObject | inside | A | True | False | if (!IsValidObjectId(target_small->inside)) return false; |
| src1.6.6/rdfw.cpp:3488 | HoldSmallObject | inside | A | True | False | auto target_cont = dynamic_pointer_cast<Container>(objects[target_small->inside]); |
| src1.6.6/rdfw.cpp:3490 | HoldSmallObject | isOpen | A | True | False | if(!target_cont->isOpen && !Open(target_cont->id)) return false; |
| src1.6.6/rdfw.cpp:3496 | HoldSmallObject | hold_id | A | True | False | if (hold_id == static_cast<int>(a)) { |
| src1.6.6/rdfw.cpp:3497 | HoldSmallObject | FactValue | B | True | False | if (FactValue(StateField::HOLD) == static_cast<int>(a)) return true; |
| src1.6.6/rdfw.cpp:3498 | HoldSmallObject | hold | D | True | False | // 初始 hold 事实可能是错的。用一次可观察动作建立本地事实；失败则清除猜测。 |
| src1.6.6/rdfw.cpp:3500 | HoldSmallObject | EvidenceSource | A | True | False | SetHold(nullptr, EvidenceSource::ACTION_FAILURE); |
| src1.6.6/rdfw.cpp:3502 | HoldSmallObject | FactValue,plate_id | B | True | False | if (plate_id == static_cast<int>(a) && FactValue(StateField::PLATE) != static_cast<int>(a)) { |
| src1.6.6/rdfw.cpp:3504 | HoldSmallObject | EvidenceSource | A | True | False | SetPlate(nullptr, EvidenceSource::ACTION_FAILURE); |
| src1.6.6/rdfw.cpp:3506 | HoldSmallObject | hold_id | A | True | False | if (hold_id != a) |
| src1.6.6/rdfw.cpp:3508 | HoldSmallObject | hold_id | A | True | False | if (hold_id != NONE && !PutDown(hold_id)) return false; //如果拿着物体，先放下 |
| src1.6.6/rdfw.cpp:3509 | HoldSmallObject | plate_id | A | True | False | if (plate_id == a) |
| src1.6.6/rdfw.cpp:3517 | HoldSmallObject | location | A | True | False | if (target_small->location != UNKNOWN) |
| src1.6.6/rdfw.cpp:3519 | HoldSmallObject | location | A | True | False | if (location != target_small->location) |
| src1.6.6/rdfw.cpp:3520 | HoldSmallObject | location | A | True | False | if(Move(target_small->location)!=1) |
| src1.6.6/rdfw.cpp:3528 | HoldSmallObject | location | A | True | False | if(target_small->location == UNKNOWN ){ |
| src1.6.6/rdfw.cpp:3536 | HoldSmallObject | inside | A | True | False | if (target_small->inside == NONE\|\|target_small->inside == UNKNOWN) //这里我想了想，可能不会有UNKOWN的情况 |
| src1.6.6/rdfw.cpp:3539 | HoldSmallObject | location | A | True | False | if (target_small->location == location && PickUp(a)) return 1; |
| src1.6.6/rdfw.cpp:3542 | HoldSmallObject | location | A | True | False | if (!EnsureLocationCapacity(location)) return false; |
| src1.6.6/rdfw.cpp:3545 | HoldSmallObject | location | A | True | False | if ( posSensedFlag[location] |
| src1.6.6/rdfw.cpp:3546 | HoldSmallObject | location | A | True | False | && target_small->location == location |
| src1.6.6/rdfw.cpp:3547 | HoldSmallObject | location | A | True | False | && HasContainerAtLocation(location) |
| src1.6.6/rdfw.cpp:3549 | HoldSmallObject | location | A | True | False | unsigned int cont_id = GetContainerAtLocation(location); |
| src1.6.6/rdfw.cpp:3552 | HoldSmallObject | isOpen | A | True | False | return (cont && cont->isOpen); |
| src1.6.6/rdfw.cpp:3557 | HoldSmallObject | location | A | True | False | if (TakeOut(a, GetContainerAtLocation(location))) return 1; |
| src1.6.6/rdfw.cpp:3561 | HoldSmallObject | plate_id | A | True | False | if (plate_id == UNKNOWN && FromPlate(a)) return 1; |
| src1.6.6/rdfw.cpp:3562 | HoldSmallObject | EvidenceSource | A | True | False | ApplyStateValue(StateField::LOCATION,a,UNKNOWN,false,EvidenceSource::ACTION_FAILURE); |
| src1.6.6/rdfw.cpp:3575 | HoldSmallObject | inside | A | True | False | int initial_cont_id=target_small->inside; |
| src1.6.6/rdfw.cpp:3578 | HoldSmallObject | inside | C | True | False | target_small->inside = UNKNOWN; |
| src1.6.6/rdfw.cpp:3581 | HoldSmallObject | inside | A | True | False | TakeOutResult result = TakeOutLogic(a,target_small->inside); |
| src1.6.6/rdfw.cpp:3587 | HoldSmallObject | inside | A | True | False | else if(result == TakeOutResult::NeedContainerLocation) {if (t >= 2)  return 0;GetBigObjectStatus(target_small->inside);} |
| src1.6.6/rdfw.cpp:3617 | HoldSmallObject | FactValue | B | True | False | return FactValue(StateField::HOLD)==static_cast<int>(a); |
| src1.6.6/rdfw.cpp:3629 | TakeOutLogic | FactContainerState | B | True | False | if (FactContainerState(cont) != 1) return false; |
| src1.6.6/rdfw.cpp:3631 | TakeOutLogic | location | A | True | False | const bool absent = HasObjectAtLocation(location, cont) && |
| src1.6.6/rdfw.cpp:3632 | TakeOutLogic | location | A | True | False | !HasObjectAtLocation(location, small); |
| src1.6.6/rdfw.cpp:3635 | TakeOutLogic | inside | A | True | False | if (small_object && small_object->inside == static_cast<int>(cont)) { |
| src1.6.6/rdfw.cpp:3637 | TakeOutLogic | inside | C | True | False | small_object->inside = UNKNOWN; |
| src1.6.6/rdfw.cpp:3639 | TakeOutLogic | EvidenceSource | A | True | False | SetInsideEvidence(small, false, EvidenceSource::SENSE); |
| src1.6.6/rdfw.cpp:3645 | TakeOutLogic | location | A | True | False | if(target_cont->location==UNKNOWN)return TakeOutResult::NeedContainerLocation; |
| src1.6.6/rdfw.cpp:3647 | TakeOutLogic | isOpen | A | True | False | if(!target_cont->isOpen) |
| src1.6.6/rdfw.cpp:3659 | TakeOutLogic | isOpen | C | True | False | target_cont->isOpen = true; |
| src1.6.6/rdfw.cpp:3661 | TakeOutLogic | EvidenceSource | A | True | False | SetContainerEvidence(cont, true, EvidenceSource::ACTION_FAILURE); |
| src1.6.6/rdfw.cpp:3693 | SolveTask_PickUp | TaskFactSatisfied | B | True | False | if(TaskFactSatisfied("pickup",a)) return true; |
| src1.6.6/rdfw.cpp:3699 | SolveTask_PickUp | TaskFactSatisfied | B | True | False | if(TaskFactSatisfied("pickup",a)) return true; |
| src1.6.6/rdfw.cpp:3708 | SolveTask_PutDown | TaskFactSatisfied | B | True | False | if(TaskFactSatisfied("putdown",a)) return true; |
| src1.6.6/rdfw.cpp:3714 | SolveTask_PutDown | hold_id | A | True | False | if(hold_id==a){ |
| src1.6.6/rdfw.cpp:3715 | SolveTask_PutDown | location | A | True | False | if (location < 0 \|\| !EnsureLocationCapacity(location)) return false; |
| src1.6.6/rdfw.cpp:3716 | SolveTask_PutDown | location | A | True | False | if(putdown_cons[a][location]) { |
| src1.6.6/rdfw.cpp:3722 | SolveTask_PutDown | plate_id | A | True | False | else if(plate_id==a){ |
| src1.6.6/rdfw.cpp:3723 | SolveTask_PutDown | location | A | True | False | if (location < 0 \|\| !EnsureLocationCapacity(location)) return false; |
| src1.6.6/rdfw.cpp:3724 | SolveTask_PutDown | hold_id | A | True | False | if(hold_id>0) { |
| src1.6.6/rdfw.cpp:3725 | SolveTask_PutDown | hold_id | A | True | False | if (!PutDown(hold_id)) return false; |
| src1.6.6/rdfw.cpp:3726 | SolveTask_PutDown | location | A | True | False | if(putdown_cons[a][location]) { |
| src1.6.6/rdfw.cpp:3732 | SolveTask_PutDown | location | A | True | False | if(putdown_cons[a][location]) { |
| src1.6.6/rdfw.cpp:3741 | SolveTask_PutDown | TaskFactSatisfied | B | True | False | if (stage == 1 && TaskFactSatisfied("putdown",a)) return true; |
| src1.6.6/rdfw.cpp:3742 | SolveTask_PutDown | FactLocation,TaskFactSatisfied | B | True | False | if (stage == 2 && TaskFactSatisfied("putdown",a) && FactLocation(a) != UNKNOWN) |
| src1.6.6/rdfw.cpp:3745 | SolveTask_PutDown | location | A | True | False | if (location < 0) return false; |
| src1.6.6/rdfw.cpp:3746 | SolveTask_PutDown | location | A | True | False | if (!EnsureLocationCapacity(location)) return false; |
| src1.6.6/rdfw.cpp:3747 | SolveTask_PutDown | location | A | True | False | if (putdown_cons[a][location]) { |
| src1.6.6/rdfw.cpp:3761 | SolveTask_Goto | TaskFactSatisfied | B | True | False | if(TaskFactSatisfied("goto",a)){ |
| src1.6.6/rdfw.cpp:3764 | SolveTask_Goto | location | A | True | False | else return Move(objects[a]->location); |
| src1.6.6/rdfw.cpp:3768 | SolveTask_Goto | TaskFactSatisfied | B | True | False | if(TaskFactSatisfied("goto",a)) return true; |
| src1.6.6/rdfw.cpp:3770 | SolveTask_Goto | location | A | True | False | if(objects[a]->location==UNKNOWN) |
| src1.6.6/rdfw.cpp:3787 | SolveTask_Goto | location | A | True | False | if(location==objects[a]->location) { |
| src1.6.6/rdfw.cpp:3789 | SolveTask_Goto | location | A | True | False | if (HasObjectAtLocation(location, a)) return true; |
| src1.6.6/rdfw.cpp:3791 | SolveTask_Goto | FactInside | B | True | False | if (small && FactInside(a) > 0 && |
| src1.6.6/rdfw.cpp:3792 | SolveTask_Goto | FactInside,location | B | True | False | HasObjectAtLocation(location, FactInside(a))) { |
| src1.6.6/rdfw.cpp:3793 | SolveTask_Goto | EvidenceSource,location | A | True | False | ApplyStateValue(StateField::LOCATION,a,location,true,EvidenceSource::RELATION_DERIVED); |
| src1.6.6/rdfw.cpp:3795 | SolveTask_Goto | FactInside | B | True | False | DependOn(StateField::LOCATION,a,StateField::LOCATION,FactInside(a)); |
| src1.6.6/rdfw.cpp:3800 | SolveTask_Goto | location | A | True | False | else if(!Move(objects[a]->location)) |
| src1.6.6/rdfw.cpp:3808 | SolveTask_Goto | location | A | True | False | if (HasObjectAtLocation(location, a)) return true; |
| src1.6.6/rdfw.cpp:3810 | SolveTask_Goto | FactInside | B | True | False | if (small && FactInside(a) > 0 && |
| src1.6.6/rdfw.cpp:3811 | SolveTask_Goto | FactInside,location | B | True | False | HasObjectAtLocation(location, FactInside(a))) { |
| src1.6.6/rdfw.cpp:3812 | SolveTask_Goto | EvidenceSource,location | A | True | False | ApplyStateValue(StateField::LOCATION,a,location,true,EvidenceSource::RELATION_DERIVED); |
| src1.6.6/rdfw.cpp:3814 | SolveTask_Goto | FactInside | B | True | False | DependOn(StateField::LOCATION,a,StateField::LOCATION,FactInside(a)); |
| src1.6.6/rdfw.cpp:3831 | SolveTask_Open | TaskFactSatisfied | B | True | False | if(TaskFactSatisfied("open",a)) return true; |
| src1.6.6/rdfw.cpp:3837 | SolveTask_Open | TaskFactSatisfied | B | True | False | if(TaskFactSatisfied("open",a)) return true; |
| src1.6.6/rdfw.cpp:3838 | SolveTask_Open | hold_id | A | True | False | if(hold_id!=NONE && !PutDown(hold_id)) return false; |
| src1.6.6/rdfw.cpp:3841 | SolveTask_Open | location | A | True | False | if (location != objects[a]->location && !Move(objects[a]->location)) return false; |
| src1.6.6/rdfw.cpp:3846 | SolveTask_Open | location | A | True | False | if(objects[a]->location==UNKNOWN) |
| src1.6.6/rdfw.cpp:3855 | SolveTask_Open | location | A | True | False | if (location != objects[a]->location) |
| src1.6.6/rdfw.cpp:3856 | SolveTask_Open | location | A | True | False | if(!Move(objects[a]->location)) |
| src1.6.6/rdfw.cpp:3865 | SolveTask_Open | isOpen | C | True | False | cnt->isOpen = true; |
| src1.6.6/rdfw.cpp:3867 | SolveTask_Open | EvidenceSource | A | True | False | SetContainerEvidence(a, true, EvidenceSource::ACTION_FAILURE); |
| src1.6.6/rdfw.cpp:3868 | SolveTask_Open | EvidenceSource | A | True | False | MarkDirectLocationEvidence(a, true, EvidenceSource::SENSE); |
| src1.6.6/rdfw.cpp:3888 | SolveTask_Close | TaskFactSatisfied | B | True | False | if(TaskFactSatisfied("close",a)) return true; |
| src1.6.6/rdfw.cpp:3894 | SolveTask_Close | TaskFactSatisfied | B | True | False | if(TaskFactSatisfied("close",a)) return true; |
| src1.6.6/rdfw.cpp:3895 | SolveTask_Close | hold_id | A | True | False | if(hold_id!=NONE && !PutDown(hold_id)) return false; |
| src1.6.6/rdfw.cpp:3898 | SolveTask_Close | location | A | True | False | if (location != objects[a]->location && !Move(objects[a]->location)) return false; |
| src1.6.6/rdfw.cpp:3904 | SolveTask_Close | location | A | True | False | if(objects[a]->location==UNKNOWN) |
| src1.6.6/rdfw.cpp:3913 | SolveTask_Close | location | A | True | False | if (location != objects[a]->location) |
| src1.6.6/rdfw.cpp:3914 | SolveTask_Close | location | A | True | False | if(!Move(objects[a]->location)) |
| src1.6.6/rdfw.cpp:3923 | SolveTask_Close | isOpen | C | True | False | cnt->isOpen = false; |
| src1.6.6/rdfw.cpp:3925 | SolveTask_Close | EvidenceSource | A | True | False | SetContainerEvidence(a, true, EvidenceSource::ACTION_FAILURE); |
| src1.6.6/rdfw.cpp:3926 | SolveTask_Close | EvidenceSource | A | True | False | MarkDirectLocationEvidence(a, true, EvidenceSource::SENSE); |
| src1.6.6/rdfw.cpp:3944 | SolveTask_Give | location | A | True | False | if(human->location==UNKNOWN) |
| src1.6.6/rdfw.cpp:3949 | SolveTask_Give | TaskFactSatisfied | B | True | False | if(TaskFactSatisfied("give",a,human->id)) return true; |
| src1.6.6/rdfw.cpp:3968 | SolveTask_Putin | TaskFactSatisfied | B | True | False | if(TaskFactSatisfied("putin",a,b)) return true; |
| src1.6.6/rdfw.cpp:3975 | SolveTask_Putin | TaskFactSatisfied | B | True | False | if(TaskFactSatisfied("putin",a,b)) return true; |
| src1.6.6/rdfw.cpp:3980 | SolveTask_Putin | location | A | True | False | if(objects[a]->location==objects[b]->location) |
| src1.6.6/rdfw.cpp:3982 | SolveTask_Putin | location | A | True | False | if (location != target_cont->location && !Move(target_cont->location)) return false; |
| src1.6.6/rdfw.cpp:3983 | SolveTask_Putin | isOpen | A | True | False | if (target_cont->isOpen != 1 && !Open(b)) return false; |
| src1.6.6/rdfw.cpp:3990 | SolveTask_Putin | location | A | True | False | if (location != target_cont->location && !Move(target_cont->location)) return false; |
| src1.6.6/rdfw.cpp:3991 | SolveTask_Putin | isOpen | A | True | False | if (target_cont->isOpen != 1) |
| src1.6.6/rdfw.cpp:4004 | SolveTask_Putin | location | A | True | False | if(objects[b]->location==UNKNOWN) |
| src1.6.6/rdfw.cpp:4015 | SolveTask_Putin | location | A | True | False | if (location != target_cont->location) |
| src1.6.6/rdfw.cpp:4016 | SolveTask_Putin | location | A | True | False | if(!Move(target_cont->location)) |
| src1.6.6/rdfw.cpp:4024 | SolveTask_Putin | isOpen | A | True | False | if (!target_cont->isOpen) |
| src1.6.6/rdfw.cpp:4035 | SolveTask_Putin | isOpen | C | True | False | target_cont->isOpen = true; |
| src1.6.6/rdfw.cpp:4037 | SolveTask_Putin | EvidenceSource | A | True | False | SetContainerEvidence(b, true, EvidenceSource::ACTION_FAILURE); |
| src1.6.6/rdfw.cpp:4071 | SolveTask_Putin | hold_id | D | True | False | //     PutDown(hold_id); |
| src1.6.6/rdfw.cpp:4098 | SolveTask_TakeOut | TaskFactSatisfied | B | True | False | if(TaskFactSatisfied("takeout",a,b)) return true; |
| src1.6.6/rdfw.cpp:4108 | SolveTask_TakeOut | location | D | True | False | // Stage 2 location facts and AskLoc replies may be misleading. A known |
| src1.6.6/rdfw.cpp:4112 | SolveTask_TakeOut | TaskFactSatisfied | B | True | False | if (stage == 1 && TaskFactSatisfied("takeout",a,b)) |
| src1.6.6/rdfw.cpp:4120 | SolveTask_TakeOut | hold | A | True | False | if (hold!= nullptr && !PutDown(hold->id)) return false; |
| src1.6.6/rdfw.cpp:4121 | SolveTask_TakeOut | location | A | True | False | if (location != target_cont->location && !Move(target_cont->location)) return false; |
| src1.6.6/rdfw.cpp:4122 | SolveTask_TakeOut | isOpen | A | True | False | if (target_cont->isOpen != 1 && !Open(target_cont->id)) return false; |
| src1.6.6/rdfw.cpp:4126 | SolveTask_TakeOut | location | A | True | False | if(target_cont->location==UNKNOWN){GetBigObjectStatus(b);if(!IsKeepingGoing(task_index)) return false;} |
| src1.6.6/rdfw.cpp:4127 | SolveTask_TakeOut | hold | A | True | False | if (hold!= nullptr && !PutDown(hold->id)) return false; |
| src1.6.6/rdfw.cpp:4132 | SolveTask_TakeOut | location | A | True | False | if (location != target_cont->location) |
| src1.6.6/rdfw.cpp:4133 | SolveTask_TakeOut | location | A | True | False | if(!Move(target_cont->location)) |
| src1.6.6/rdfw.cpp:4146 | SolveTask_TakeOut | TaskFactSatisfied | B | True | False | if (TaskFactSatisfied("takeout",a,b)) return true; |
| src1.6.6/rdfw.cpp:4159 | SolveTask_TakeOut | TaskFactSatisfied,inside | B | True | False | return TaskFactSatisfied("takeout",a,b); // 未验证的非 inside 不是完成事实 |
| src1.6.6/rdfw.cpp:4175 | SolveTask_PutOn | TaskFactSatisfied | B | True | False | if(TaskFactSatisfied("puton",a,b)) |
| src1.6.6/rdfw.cpp:4178 | SolveTask_PutOn | location | A | True | False | if(objects[b]->location==UNKNOWN) |
| src1.6.6/rdfw.cpp:4188 | SolveTask_PutOn | location | A | True | False | if (location != objects[b]->location) |
| src1.6.6/rdfw.cpp:4190 | SolveTask_PutOn | location | A | True | False | if(!Move(objects[b]->location)) |
| src1.6.6/rdfw.cpp:4198 | SolveTask_PutOn | FactLocation | B | True | False | if (stage == 2 && (FactLocation(b) == UNKNOWN \|\| FactLocation(b) != FactLocation(0))) { |
| src1.6.6/rdfw.cpp:4200 | SolveTask_PutOn | location | A | True | False | if(!HasObjectAtLocation(location, b)) { |
| src1.6.6/rdfw.cpp:4406 | remove_if | location | A | True | False | int loc = (objects[id] ? objects[id]->location : UNKNOWN); |
| src1.6.6/rdfw.cpp:4444 | ExecuteMultiGotoAggregation | location | A | True | False | int loc = (objects[id] ? objects[id]->location : UNKNOWN); |
| src1.6.6/rdfw.cpp:4473 | ExecuteMultiGotoAggregation | location | A | True | False | int loc = (objects[id] ? objects[id]->location : UNKNOWN); |
| src1.6.6/rdfw.cpp:4509 | ExecuteMultiGotoAggregation | location | A | True | False | int loc = objects[id]->location; |
| src1.6.6/rdfw.cpp:4517 | ExecuteMultiGotoAggregation | location | A | True | False | int loc = objects[id]->location; |
| src1.6.6/rdfw.cpp:4525 | ExecuteMultiGotoAggregation | location | A | True | False | int loc = objects[id]->location; |
| src1.6.6/rdfw.cpp:4589 | ExecuteMultiGotoAggregation | location | A | True | False | int loc = objects[id]->location; |
| src1.6.6/rdfw.cpp:4612 | ExecuteMultiGotoAggregation | location | A | True | False | cout << "[MultiGoto] location " << loc << " has " << count << " small objects" << endl; |
| src1.6.6/rdfw.cpp:4648 | ExecuteMultiGotoAggregation | location | A | True | False | int loc = objects[big_id]->location; |
| src1.6.6/rdfw.cpp:4680 | ExecuteMultiGotoAggregation | location | A | True | False | LOG(YELLOW "[MultiGoto] No optimal location found, using first available: %d\n" RESET, chosen_loc); |
| src1.6.6/rdfw.cpp:4688 | ExecuteMultiGotoAggregation | location | A | True | False | LOG(YELLOW "[MultiGoto] No optimal location found, using first available: %d\n" RESET, loc); |
| src1.6.6/rdfw.cpp:4697 | ExecuteMultiGotoAggregation | location | A | True | False | LOG(RED "[MultiGoto] ERROR: No valid location found! chosen_loc=%d, rightlocation[%d]=%d\n" RESET, |
| src1.6.6/rdfw.cpp:4700 | ExecuteMultiGotoAggregation | location | A | True | False | chosen_loc = location; |
| src1.6.6/rdfw.cpp:4701 | ExecuteMultiGotoAggregation | location | A | True | False | LOG(YELLOW "[MultiGoto] Using current location as fallback: %d\n" RESET, chosen_loc); |
| src1.6.6/rdfw.cpp:4706 | ExecuteMultiGotoAggregation | location | D | True | False | // chosen_loc is a location, while SolveTask_PutOn expects an object id |
| src1.6.6/rdfw.cpp:4707 | ExecuteMultiGotoAggregation | location | D | True | False | // whose location is the destination.  Keep the legacy hub selection |
| src1.6.6/rdfw.cpp:4708 | ExecuteMultiGotoAggregation | location | D | True | False | // unchanged and map that location to a stable representative object. |
| src1.6.6/rdfw.cpp:4711 | ExecuteMultiGotoAggregation | location | A | True | False | if (!objects[i] \|\| objects[i]->location != chosen_loc) continue; |
| src1.6.6/rdfw.cpp:4721 | ExecuteMultiGotoAggregation | location | C | True | False | LOG(GREEN "[MultiGoto] hub location=%d representative_object=%u\n" RESET, |
| src1.6.6/rdfw.cpp:4733 | ExecuteMultiGotoAggregation | location | A | True | False | int loc = objects[id]->location; |
| src1.6.6/rdfw.cpp:4751 | ExecuteMultiGotoAggregation | location | A | True | False | if (location != chosen_loc) { |
| src1.6.6/rdfw.cpp:4765 | ExecuteMultiGotoAggregation | hold,plate | D | True | False | // 护栏：hold/plate 不在集合且跨区会触发 move 约束时，先就地处理 |
| src1.6.6/rdfw.cpp:4766 | ExecuteMultiGotoAggregation | hold_id | A | True | False | if (IsValidObjectId(hold_id) && !in_set(hold_id) && |
| src1.6.6/rdfw.cpp:4767 | ExecuteMultiGotoAggregation | hold_id | A | True | False | chosen_loc >= 0 && hold_id < static_cast<int>(move_cons.size()) && |
| src1.6.6/rdfw.cpp:4768 | ExecuteMultiGotoAggregation | hold_id | A | True | False | static_cast<std::size_t>(chosen_loc) < move_cons[hold_id].size() && |
| src1.6.6/rdfw.cpp:4769 | ExecuteMultiGotoAggregation | hold_id | A | True | False | move_cons[hold_id][chosen_loc]) { |
| src1.6.6/rdfw.cpp:4770 | ExecuteMultiGotoAggregation | hold_id | A | True | False | PutDown(hold_id); |
| src1.6.6/rdfw.cpp:4772 | ExecuteMultiGotoAggregation | plate_id | A | True | False | if (IsValidObjectId(plate_id) && !in_set(plate_id) && |
| src1.6.6/rdfw.cpp:4773 | ExecuteMultiGotoAggregation | plate_id | A | True | False | chosen_loc >= 0 && plate_id < static_cast<int>(move_cons.size()) && |
| src1.6.6/rdfw.cpp:4774 | ExecuteMultiGotoAggregation | plate_id | A | True | False | static_cast<std::size_t>(chosen_loc) < move_cons[plate_id].size() && |
| src1.6.6/rdfw.cpp:4775 | ExecuteMultiGotoAggregation | plate_id | A | True | False | move_cons[plate_id][chosen_loc]) { |
| src1.6.6/rdfw.cpp:4776 | ExecuteMultiGotoAggregation | hold_id | A | True | False | if (hold_id > 0) PutDown(hold_id); |
| src1.6.6/rdfw.cpp:4777 | ExecuteMultiGotoAggregation | plate_id | A | True | False | FromPlate(plate_id); |
| src1.6.6/rdfw.cpp:4778 | ExecuteMultiGotoAggregation | plate_id | A | True | False | PutDown(plate_id); |
| src1.6.6/rdfw.cpp:4781 | ExecuteMultiGotoAggregation | hold,plate | D | True | False | // 若 hold/plate 在集合里，优先处理 |
| src1.6.6/rdfw.cpp:4786 | ExecuteMultiGotoAggregation | hold_id | A | True | False | if (hold_id  > 0) promote_front(hold_id); |
| src1.6.6/rdfw.cpp:4787 | ExecuteMultiGotoAggregation | plate_id | A | True | False | if (plate_id > 0) promote_front(plate_id); |
| src1.6.6/rdfw.cpp:4793 | stable_sort | location | A | True | False | int da = (sa && sa->location == chosen_loc) ? 0 : 1; |
| src1.6.6/rdfw.cpp:4794 | stable_sort | location | A | True | False | int db = (sb && sb->location == chosen_loc) ? 0 : 1; |
| src1.6.6/rdfw.cpp:4833 | ExecuteMultiGotoAggregation | location | A | True | False | if (location != chosen_loc) { |
| src1.6.6/rdfw.cpp:4895 | ParseAskLocationReply | inside | A | True | False | "^\\s*(at\|inside)\\s*\\(\\s*([0-9]+)\\s*,\\s*([0-9]+)\\s*\\)\\s*$"); |
| src1.6.6/rdfw.cpp:4905 | ParseAskLocationReply | inside | A | True | False | if (relation == "inside" && reply_target > static_cast<int>(MAX_OBJECT_ID)) |
| src1.6.6/rdfw.cpp:4930 | GetSmallObjectStatus | inside | A | True | False | if (relation == "inside") { |
| src1.6.6/rdfw.cpp:4947 | GetSmallObjectStatus | IsInsideVerified | A | True | False | if (IsInsideVerified(a)) { |
| src1.6.6/rdfw.cpp:4948 | GetSmallObjectStatus | inside | A | True | False | const int answer_inside = chosen_relation == "inside" |
| src1.6.6/rdfw.cpp:4950 | GetSmallObjectStatus | FactInside | B | True | False | if (FactInside(a) != answer_inside) { |
| src1.6.6/rdfw.cpp:4951 | GetSmallObjectStatus | inside | A | True | False | LOG(YELLOW "AskLoc(%u) conflicts with trusted inside fact; ignored\n" RESET, a); |
| src1.6.6/rdfw.cpp:4955 | GetSmallObjectStatus | IsLocationVerified | A | True | False | if (IsLocationVerified(a)) { |
| src1.6.6/rdfw.cpp:4956 | GetSmallObjectStatus | inside | A | True | False | const int answer_location = chosen_relation == "inside" |
| src1.6.6/rdfw.cpp:4957 | GetSmallObjectStatus | location | A | True | False | ? objects[chosen_target]->location : static_cast<int>(chosen_target); |
| src1.6.6/rdfw.cpp:4958 | GetSmallObjectStatus | FactLocation | B | True | False | if (FactLocation(a) != answer_location) { |
| src1.6.6/rdfw.cpp:4959 | GetSmallObjectStatus | location | A | True | False | LOG(YELLOW "AskLoc(%u) conflicts with trusted location; ignored\n" RESET, a); |
| src1.6.6/rdfw.cpp:4963 | GetSmallObjectStatus | IsInsideVerified,IsLocationVerified | A | True | False | if (IsInsideVerified(a) && IsLocationVerified(a)) return true; |
| src1.6.6/rdfw.cpp:4965 | GetSmallObjectStatus | inside | A | True | False | const int answer_inside = chosen_relation == "inside" |
| src1.6.6/rdfw.cpp:4967 | GetSmallObjectStatus | inside | A | True | False | const int answer_location = chosen_relation == "inside" |
| src1.6.6/rdfw.cpp:4968 | GetSmallObjectStatus | location | A | True | False | ? objects[chosen_target]->location : static_cast<int>(chosen_target); |
| src1.6.6/rdfw.cpp:4969 | GetSmallObjectStatus | IsInsideVerified | A | True | False | const bool inside_conflict = !IsInsideVerified(a) && |
| src1.6.6/rdfw.cpp:4971 | GetSmallObjectStatus | EvidenceSource | A | True | False | EvidenceSource::ASK_ANSWER); |
| src1.6.6/rdfw.cpp:4972 | GetSmallObjectStatus | IsLocationVerified | A | True | False | const bool location_conflict = !IsLocationVerified(a) && |
| src1.6.6/rdfw.cpp:4975 | GetSmallObjectStatus | EvidenceSource | A | True | False | EvidenceSource::ASK_ANSWER); |
| src1.6.6/rdfw.cpp:4977 | GetSmallObjectStatus | inside | A | True | False | if (small->inside > 0 && static_cast<size_t>(small->inside) < objects.size()) { |
| src1.6.6/rdfw.cpp:4978 | GetSmallObjectStatus | inside | A | True | False | auto old_cont = dynamic_pointer_cast<Container>(objects[small->inside]); |
| src1.6.6/rdfw.cpp:4982 | GetSmallObjectStatus | inside | A | True | False | if (chosen_relation == "inside") { |
| src1.6.6/rdfw.cpp:4985 | GetSmallObjectStatus | location | A | True | False | if (cont->location == UNKNOWN) GetBigObjectStatus(cont->id); |
| src1.6.6/rdfw.cpp:4986 | GetSmallObjectStatus | location | C | True | False | small->location = cont->location; |
| src1.6.6/rdfw.cpp:4987 | GetSmallObjectStatus | inside | C | True | False | small->inside = cont->id; |
| src1.6.6/rdfw.cpp:4995 | GetSmallObjectStatus | location | C | True | False | small->location = static_cast<int>(chosen_target); |
| src1.6.6/rdfw.cpp:4996 | GetSmallObjectStatus | inside | C | True | False | small->inside = NONE; |
| src1.6.6/rdfw.cpp:4999 | GetSmallObjectStatus | IsLocationVerified | A | True | False | if (!IsLocationVerified(a)) |
| src1.6.6/rdfw.cpp:5000 | GetSmallObjectStatus | EvidenceSource | A | True | False | MarkDirectLocationEvidence(a, false, EvidenceSource::ASK_ANSWER); |
| src1.6.6/rdfw.cpp:5001 | GetSmallObjectStatus | IsInsideVerified | A | True | False | if (!IsInsideVerified(a)) |
| src1.6.6/rdfw.cpp:5002 | GetSmallObjectStatus | EvidenceSource | A | True | False | SetInsideEvidence(a, false, EvidenceSource::ASK_ANSWER); |
| src1.6.6/rdfw.cpp:5005 | GetSmallObjectStatus | location | A | True | False | if (small->location >= 0) { |
| src1.6.6/rdfw.cpp:5006 | GetSmallObjectStatus | location | A | True | False | if (!EnsureLocationCapacity(small->location)) return false; |
| src1.6.6/rdfw.cpp:5007 | GetSmallObjectStatus | location | A | True | False | posCorrectFlag[small->location] = false; |
| src1.6.6/rdfw.cpp:5034 | GetBigObjectStatus | location | A | True | False | LOG(YELLOW "AskLoc(%u) produced no usable bounded location reply\n" RESET, a); |
| src1.6.6/rdfw.cpp:5037 | GetBigObjectStatus | IsLocationVerified | A | True | False | if (IsLocationVerified(a)) { |
| src1.6.6/rdfw.cpp:5038 | GetBigObjectStatus | FactLocation | B | True | False | if (FactLocation(a) != static_cast<int>(chosen_location)) { |
| src1.6.6/rdfw.cpp:5039 | GetBigObjectStatus | location | A | True | False | LOG(YELLOW "AskLoc(%u) conflicts with trusted location; ignored\n" RESET, a); |
| src1.6.6/rdfw.cpp:5047 | GetBigObjectStatus | EvidenceSource | A | True | False | static_cast<int>(chosen_location), EvidenceSource::ASK_ANSWER); |
| src1.6.6/rdfw.cpp:5048 | GetBigObjectStatus | location | C | True | False | objects[a]->location = static_cast<int>(chosen_location); |
| src1.6.6/rdfw.cpp:5054 | GetBigObjectStatus | IsLocationVerified | A | True | False | if (IsLocationVerified(item->id)) continue; |
| src1.6.6/rdfw.cpp:5055 | GetBigObjectStatus | EvidenceSource,location | A | True | False | ApplyStateValue(StateField::LOCATION,item->id,cont->location,false,EvidenceSource::ASK_ANSWER); |
| src1.6.6/rdfw.cpp:5059 | GetBigObjectStatus | EvidenceSource | A | True | False | MarkDirectLocationEvidence(a, false, EvidenceSource::ASK_ANSWER); |
| src1.6.6/rdfw.cpp:5077 | AskLoc | inside | A | True | False | if (small && small->inside > 0) |
| src1.6.6/rdfw.cpp:5078 | AskLoc | inside | A | True | False | str = "inside(" + std::to_string(a) + "," + |
| src1.6.6/rdfw.cpp:5079 | AskLoc | inside | A | True | False | std::to_string(small->inside) + ")"; |
| src1.6.6/rdfw.cpp:5080 | AskLoc | location | A | True | False | else if (objects[a]->location >= 0) |
| src1.6.6/rdfw.cpp:5082 | AskLoc | location | A | True | False | std::to_string(objects[a]->location) + ")"; |
| src1.6.6/rdfw.cpp:5099 | Sense | location | D | True | False | // Sense 只观察当前位置，不应把 location 当作对象 ID，也不应隐式开关门。 |
| src1.6.6/rdfw.cpp:5109 | SenseCurrentLocationOnly | location | C | True | False | int curr_loc = location; |
| src1.6.6/rdfw.cpp:5147 | SenseCurrentLocationOnly | location | C | True | False | if (objects[id]->location != curr_loc) |
| src1.6.6/rdfw.cpp:5148 | SenseCurrentLocationOnly | location | C | True | False | InvalidateSenseAtLocation(objects[id]->location); |
| src1.6.6/rdfw.cpp:5149 | SenseCurrentLocationOnly | EvidenceSource | C | True | False | ApplyStateValue(StateField::LOCATION,id,curr_loc,true,EvidenceSource::SENSE); |
| src1.6.6/rdfw.cpp:5161 | SenseCurrentLocationOnly | location | C | True | False | LOG("[SenseCurrentLocationOnly] Container %d detected at location %d", id, curr_loc); |
| src1.6.6/rdfw.cpp:5163 | SenseCurrentLocationOnly | location | C | True | False | LOG("[SenseCurrentLocationOnly] Object %d detected at location %d", id, curr_loc); |
| src1.6.6/rdfw.cpp:5168 | SenseCurrentLocationOnly | inside | D | True | False | // 让位置证据与 inside 关系保持一致。开放容器与其内容同时可见时， |
| src1.6.6/rdfw.cpp:5174 | SenseCurrentLocationOnly | hold_id,plate_id | C | True | False | if (!small \|\| static_cast<int>(id) == hold_id \|\| static_cast<int>(id) == plate_id) continue; |
| src1.6.6/rdfw.cpp:5182 | SenseCurrentLocationOnly | FactContainerState | C | True | False | visible_container_is_open = visible_container && FactContainerState(sensed_container_id) != 0; |
| src1.6.6/rdfw.cpp:5186 | SenseCurrentLocationOnly | inside | C | True | False | small->inside == static_cast<int>(sensed_container_id) && visible_container_is_open; |
| src1.6.6/rdfw.cpp:5188 | SenseCurrentLocationOnly | EvidenceSource | C | True | False | SetInsideEvidence(id, false, EvidenceSource::SENSE); |
| src1.6.6/rdfw.cpp:5192 | SenseCurrentLocationOnly | inside | C | True | False | if (small->inside > 0 && static_cast<size_t>(small->inside) < objects.size()) { |
| src1.6.6/rdfw.cpp:5193 | SenseCurrentLocationOnly | inside | C | True | False | auto old_container = dynamic_pointer_cast<Container>(objects[small->inside]); |
| src1.6.6/rdfw.cpp:5196 | SenseCurrentLocationOnly | EvidenceSource | C | True | False | ApplyStateValue(StateField::INSIDE,id,NONE,true,EvidenceSource::SENSE); |
| src1.6.6/rdfw.cpp:5213 | SenseCurrentLocationOnly | FactContainerState | C | True | False | container_is_open = FactContainerState(sensed_container_id) == 1; |
| src1.6.6/rdfw.cpp:5221 | SenseCurrentLocationOnly | hold_id,plate_id | C | True | False | if (static_cast<int>(i) == hold_id \|\| static_cast<int>(i) == plate_id) continue; |
| src1.6.6/rdfw.cpp:5222 | SenseCurrentLocationOnly | location | C | True | False | if (objects[i]->location == curr_loc) { |
| src1.6.6/rdfw.cpp:5230 | SenseCurrentLocationOnly | EvidenceSource | C | True | False | ApplyStateValue(StateField::LOCATION,id,UNKNOWN,false,EvidenceSource::SENSE); |
| src1.6.6/rdfw.cpp:5232 | SenseCurrentLocationOnly | location | C | True | False | LOG(YELLOW "[SenseCurrentLocationOnly] Object id=%u expected at %d but not sensed, set location UNKNOWN\n" RESET, id, curr_loc); |
| src1.6.6/rdfw.cpp:5241 | SenseCurrentLocationOnly | inside | C | True | False | if (small && small->inside == sensed_container_id) { |
| src1.6.6/rdfw.cpp:5246 | SenseCurrentLocationOnly | EvidenceSource | C | True | False | ApplyStateValue(StateField::LOCATION,id,UNKNOWN,false,EvidenceSource::SENSE); |
| src1.6.6/rdfw.cpp:5248 | SenseCurrentLocationOnly | location | C | True | False | LOG(YELLOW "[SenseCurrentLocationOnly] Object id=%u expected at %d but not sensed, set location UNKNOWN\n" RESET, id, curr_loc); |
| src1.6.6/rdfw.cpp:5256 | GetLocationSensedInfo | location | C | True | False | const RDFW::LocationSensedInfo& RDFW::GetLocationSensedInfo(int location) const { |
| src1.6.6/rdfw.cpp:5258 | GetLocationSensedInfo | location | C | True | False | if (location >= 0 && location < locationSensedObjects.size()) { |
| src1.6.6/rdfw.cpp:5259 | GetLocationSensedInfo | location | C | True | False | return locationSensedObjects[location]; |
| src1.6.6/rdfw.cpp:5264 | HasObjectAtLocation | location | A | True | False | bool RDFW::HasObjectAtLocation(int location, unsigned int object_id) const { |
| src1.6.6/rdfw.cpp:5265 | HasObjectAtLocation | location | A | True | False | if (location >= 0 && location < locationSensedObjects.size()) { |
| src1.6.6/rdfw.cpp:5266 | HasObjectAtLocation | location | A | True | False | const auto& info = locationSensedObjects[location]; |
| src1.6.6/rdfw.cpp:5274 | HasContainerAtLocation | location | A | True | False | bool RDFW::HasContainerAtLocation(int location) const { |
| src1.6.6/rdfw.cpp:5275 | HasContainerAtLocation | location | A | True | False | if (location >= 0 && location < locationSensedObjects.size()) { |
| src1.6.6/rdfw.cpp:5276 | HasContainerAtLocation | location | A | True | False | return locationSensedObjects[location].has_container; |
| src1.6.6/rdfw.cpp:5281 | GetObjectsAtLocation | location | A | True | False | vector<unsigned int> RDFW::GetObjectsAtLocation(int location) const { |
| src1.6.6/rdfw.cpp:5282 | GetObjectsAtLocation | location | A | True | False | if (location >= 0 && location < locationSensedObjects.size()) { |
| src1.6.6/rdfw.cpp:5283 | GetObjectsAtLocation | location | A | True | False | return locationSensedObjects[location].object_ids; |
| src1.6.6/rdfw.cpp:5288 | GetContainerAtLocation | location | A | True | False | unsigned int RDFW::GetContainerAtLocation(int location) const { |
| src1.6.6/rdfw.cpp:5289 | GetContainerAtLocation | location | A | True | False | if (location >= 0 && location < locationSensedObjects.size()) { |
| src1.6.6/rdfw.cpp:5290 | GetContainerAtLocation | location | A | True | False | return locationSensedObjects[location].container_id; |
| src1.6.6/rdfw.cpp:5312 | sense | location | C | True | False | const bool moved = objects[id]->location != location; |
| src1.6.6/rdfw.cpp:5313 | sense | EvidenceSource,location | C | True | False | ApplyStateValue(StateField::LOCATION,id,location,true,EvidenceSource::SENSE); |
| src1.6.6/rdfw.cpp:5315 | sense | location | C | True | False | objects[id]->location = location; |
| src1.6.6/rdfw.cpp:5319 | sense | location | C | True | False | sp->location = location; |
| src1.6.6/rdfw.cpp:5320 | sense | FactInside | C | True | False | const bool entailed = FactInside(sp->id) == static_cast<int>(id); |
| src1.6.6/rdfw.cpp:5322 | sense | EvidenceSource | C | True | False | entailed ? EvidenceSource::CONSTRAINT_DERIVED |
| src1.6.6/rdfw.cpp:5323 | sense | EvidenceSource | C | True | False | : EvidenceSource::CONSTRAINT_HEURISTIC); |
| src1.6.6/rdfw.cpp:5329 | sense | inside | D | True | False | // 小物体分支无需强制改 inside，这里保持原有逻辑不动 |
| src1.6.6/rdfw.cpp:5331 | sense | EvidenceSource | C | True | False | MarkDirectLocationEvidence(id, true, EvidenceSource::SENSE); |
| src1.6.6/rdfw.cpp:5332 | sense | location | C | True | False | if (objects[id]->unable_site == location) objects[id]->unable_site = UNKNOWN; |
| src1.6.6/rdfw.cpp:5363 | Isinside | inside | A | True | False | if(small->inside==objects[b]->id) return true; |
| src1.6.6/rdfw.cpp:5383 | IsKeepingGoing | inside | A | True | False | if(small->inside==t.Y[0]->id){ //如果任务没有满足 |
| src1.6.6/rdfw.cpp:5384 | IsKeepingGoing | location | A | True | False | const int target_location = t.Y[0]->location; |
| src1.6.6/rdfw.cpp:5395 | IsKeepingGoing | inside | A | True | False | if(small->inside!=t.Y[0]->id) //如果任务没有满足 |
| src1.6.6/rdfw.cpp:5397 | IsKeepingGoing | location | A | True | False | const int target_location = t.Y[0]->location; |
| src1.6.6/rdfw.cpp:5402 | IsKeepingGoing | location | A | True | False | if(t.X[0]->location!=target_location) t.risk+=goto_cons[target_location]; |
| src1.6.6/rdfw.cpp:5408 | IsKeepingGoing | location | A | True | False | const int target_location = t.Y[0]->location; |
| src1.6.6/rdfw.cpp:5413 | IsKeepingGoing | location | A | True | False | if(t.X[0]->location!=target_location) t.risk+=goto_cons[target_location]; |
| src1.6.6/rdfw.cpp:5417 | IsKeepingGoing | location | A | True | False | else if(t.behave=="goto" && t.X[0]->location >= 0 && |
| src1.6.6/rdfw.cpp:5418 | IsKeepingGoing | location | A | True | False | EnsureLocationCapacity(t.X[0]->location)) t.risk+=goto_cons[t.X[0]->location]; |
| src1.6.6/rdfw.cpp:5421 | IsKeepingGoing | location | A | True | False | if (t.X[0]->location >= 0 && EnsureLocationCapacity(t.X[0]->location)) |
| src1.6.6/rdfw.cpp:5422 | IsKeepingGoing | location | A | True | False | t.risk+=goto_cons[t.X[0]->location]; |
| src1.6.6/rdfw.cpp:5426 | IsKeepingGoing | location | A | True | False | if (t.X[0]->location >= 0 && EnsureLocationCapacity(t.X[0]->location)) |
| src1.6.6/rdfw.cpp:5427 | IsKeepingGoing | location | A | True | False | t.risk+=goto_cons[t.X[0]->location]; |
| src1.6.6/rdfw.cpp:5435 | IsKeepingGoing | location | A | True | False | if (human && human->location >= 0) { |
| src1.6.6/rdfw.cpp:5436 | IsKeepingGoing | location | A | True | False | if (!EnsureLocationCapacity(human->location)) return false; |
| src1.6.6/rdfw.cpp:5437 | IsKeepingGoing | location | A | True | False | t.risk+=move_cons[t.X[0]->id][human->location]; |
| src1.6.6/rdfw.cpp:5438 | IsKeepingGoing | location | A | True | False | if(t.X[0]->location!=human->location) t.risk+=goto_cons[human->location]; |
| src1.6.6/rdfw.cpp:5539 | ReconcileLocationRelation | inside | C | True | False | if (!small \|\| small->inside <= 0) return; |
| src1.6.6/rdfw.cpp:5540 | ReconcileLocationRelation | inside | C | True | False | auto container = dynamic_pointer_cast<Container>(GetObject(small->inside)); |
| src1.6.6/rdfw.cpp:5541 | ReconcileLocationRelation | location | C | True | False | if (container && container->location != UNKNOWN && small->location != UNKNOWN && |
| src1.6.6/rdfw.cpp:5542 | ReconcileLocationRelation | location | C | True | False | container->location != small->location) { |
| src1.6.6/rdfw.cpp:5544 | ReconcileLocationRelation | EvidenceSource | C | True | False | ApplyStateValue(StateField::INSIDE,small->id,UNKNOWN,false,EvidenceSource::EXPLICIT_INFO); |
| src1.6.6/rdfw.cpp:5548 | declaration/inline | location | D | True | False | // A successful container action proves co-location even when the initial |
| src1.6.6/rdfw.cpp:5549 | declaration/inline | location | D | True | False | // location was misleading. Its contents inherit that location only with the |
| src1.6.6/rdfw.cpp:5550 | declaration/inline | inside | D | True | False | // strength of their own inside evidence. |
| src1.6.6/rdfw.cpp:5552 | ConfirmContainerLocation | location | C | True | False | if (container->location != location) |
| src1.6.6/rdfw.cpp:5553 | ConfirmContainerLocation | location | C | True | False | InvalidateSenseAtLocation(container->location); |
| src1.6.6/rdfw.cpp:5554 | ConfirmContainerLocation | location | C | True | False | container->location = location; |
| src1.6.6/rdfw.cpp:5557 | ConfirmContainerLocation | inside | C | True | False | if (!item \|\| item->inside != container->id) continue; |
| src1.6.6/rdfw.cpp:5558 | ConfirmContainerLocation | FactInside,FactLocation | C | True | False | if (FactLocation(item->id) != UNKNOWN && FactInside(item->id) == UNKNOWN && |
| src1.6.6/rdfw.cpp:5559 | ConfirmContainerLocation | FactLocation,location | C | True | False | FactLocation(item->id) != location) continue; |
| src1.6.6/rdfw.cpp:5560 | ConfirmContainerLocation | location | C | True | False | item->location = location; |
| src1.6.6/rdfw.cpp:5561 | ConfirmContainerLocation | FactInside | C | True | False | const bool inside_verified = FactInside(item->id) == container->id; |
| src1.6.6/rdfw.cpp:5562 | ConfirmContainerLocation | inside | D | True | False | // The action verifies the container, not an inside relation that was |
| src1.6.6/rdfw.cpp:5565 | ConfirmContainerLocation | EvidenceSource | C | True | False | const EvidenceSource source = |
| src1.6.6/rdfw.cpp:5566 | ConfirmContainerLocation | EvidenceSource,InsideSource | C | True | False | InsideSource(item->id) == EvidenceSource::CONSTRAINT_DERIVED |
| src1.6.6/rdfw.cpp:5567 | ConfirmContainerLocation | EvidenceSource | C | True | False | ? EvidenceSource::CONSTRAINT_DERIVED |
| src1.6.6/rdfw.cpp:5568 | ConfirmContainerLocation | EvidenceSource | C | True | False | : EvidenceSource::RELATION_DERIVED; |
| src1.6.6/rdfw.cpp:5591 | TakeOut | inside | C | True | False | small->inside = NONE; |
| src1.6.6/rdfw.cpp:5592 | TakeOut | location | C | True | False | small->location = location; |
| src1.6.6/rdfw.cpp:5594 | TakeOut | isOpen | C | True | False | cont->isOpen=1; |
| src1.6.6/rdfw.cpp:5599 | TakeOut | EvidenceSource | C | True | False | SetInsideEvidence(a, true, EvidenceSource::ACTION_SUCCESS); |
| src1.6.6/rdfw.cpp:5601 | TakeOut | EvidenceSource | C | True | False | SetContainerEvidence(b, true, EvidenceSource::ACTION_SUCCESS); |
| src1.6.6/rdfw.cpp:5602 | TakeOut | location | C | True | False | InvalidateSenseAtLocation(location); |
| src1.6.6/rdfw.cpp:5629 | PutIn | inside | C | True | False | small->inside = b; |
| src1.6.6/rdfw.cpp:5631 | PutIn | location | C | True | False | small->location = location; |
| src1.6.6/rdfw.cpp:5638 | PutIn | isOpen | C | True | False | cont->isOpen=1; |
| src1.6.6/rdfw.cpp:5642 | PutIn | EvidenceSource | C | True | False | SetInsideEvidence(a, true, EvidenceSource::ACTION_SUCCESS); |
| src1.6.6/rdfw.cpp:5644 | PutIn | EvidenceSource | C | True | False | SetContainerEvidence(b, true, EvidenceSource::ACTION_SUCCESS); |
| src1.6.6/rdfw.cpp:5645 | PutIn | location | C | True | False | InvalidateSenseAtLocation(location); |
| src1.6.6/rdfw.cpp:5668 | Close | isOpen | C | True | False | container->isOpen = false; |
| src1.6.6/rdfw.cpp:5670 | Close | EvidenceSource | C | True | False | SetContainerEvidence(a, true, EvidenceSource::ACTION_SUCCESS); |
| src1.6.6/rdfw.cpp:5671 | Close | location | C | True | False | InvalidateSenseAtLocation(location); |
| src1.6.6/rdfw.cpp:5694 | Open | isOpen | C | True | False | container->isOpen = true; |
| src1.6.6/rdfw.cpp:5696 | Open | EvidenceSource | C | True | False | SetContainerEvidence(a, true, EvidenceSource::ACTION_SUCCESS); |
| src1.6.6/rdfw.cpp:5697 | Open | location | C | True | False | InvalidateSenseAtLocation(location); |
| src1.6.6/rdfw.cpp:5723 | FromPlate | EvidenceSource | C | True | False | SetInsideEvidence(a, true, EvidenceSource::ACTION_SUCCESS); |
| src1.6.6/rdfw.cpp:5724 | FromPlate | location | C | True | False | InvalidateSenseAtLocation(location); |
| src1.6.6/rdfw.cpp:5748 | ToPlate | EvidenceSource | C | True | False | SetInsideEvidence(a, true, EvidenceSource::ACTION_SUCCESS); |
| src1.6.6/rdfw.cpp:5749 | ToPlate | location | C | True | False | InvalidateSenseAtLocation(location); |
| src1.6.6/rdfw.cpp:5773 | PutDown | location | C | True | False | small->location = location; |
| src1.6.6/rdfw.cpp:5774 | PutDown | inside | C | True | False | small->inside = NONE; |
| src1.6.6/rdfw.cpp:5778 | PutDown | EvidenceSource | C | True | False | SetInsideEvidence(a, true, EvidenceSource::ACTION_SUCCESS); |
| src1.6.6/rdfw.cpp:5779 | PutDown | location | C | True | False | InvalidateSenseAtLocation(location); |
| src1.6.6/rdfw.cpp:5782 | PutDown | location | C | True | False | if (location >= 0 && EnsureLocationCapacity(location)) |
| src1.6.6/rdfw.cpp:5783 | PutDown | location | C | True | False | putdown_cons[a][location]=0; |
| src1.6.6/rdfw.cpp:5805 | PickUp | location | C | True | False | small->location = location; |
| src1.6.6/rdfw.cpp:5806 | PickUp | inside | C | True | False | small->inside = NONE; |
| src1.6.6/rdfw.cpp:5808 | PickUp | EvidenceSource | C | True | False | SetInsideEvidence(a, true, EvidenceSource::ACTION_SUCCESS); |
| src1.6.6/rdfw.cpp:5809 | PickUp | location | C | True | False | InvalidateSenseAtLocation(location); |
| src1.6.6/rdfw.cpp:5851 | Move | hold_id | C | True | False | if (hold_id > 0 && hit_move_cons(hold_id, a)) { |
| src1.6.6/rdfw.cpp:5852 | Move | hold_id | C | True | False | if (!has_taskX0 \|\| tasks[task_index].X[0]->id != hold_id) { |
| src1.6.6/rdfw.cpp:5853 | Move | hold_id | C | True | False | PutDown(hold_id); |
| src1.6.6/rdfw.cpp:5856 | Move | plate_id | C | True | False | if (plate_id > 0 && hit_move_cons(plate_id, a)) { |
| src1.6.6/rdfw.cpp:5857 | Move | hold_id | C | True | False | if (hold_id > 0) PutDown(hold_id); |
| src1.6.6/rdfw.cpp:5858 | Move | plate_id | C | True | False | FromPlate(plate_id); |
| src1.6.6/rdfw.cpp:5859 | Move | hold_id | C | True | False | if (hold_id > 0) PutDown(hold_id); |
| src1.6.6/rdfw.cpp:5863 | Move | location | C | True | False | const int previous_location = location; |
| src1.6.6/rdfw.cpp:5875 | Move | EvidenceSource | C | True | False | ApplyStateValue(StateField::LOCATION,0,a,true,EvidenceSource::ACTION_SUCCESS); |
| src1.6.6/rdfw.cpp:5876 | Move | hold,location | C | True | False | if (hold)  hold->location  = a; |
| src1.6.6/rdfw.cpp:5877 | Move | location,plate | C | True | False | if (plate) plate->location = a; |
| src1.6.6/rdfw.cpp:5880 | Move | hold_id | C | True | False | if (hold_id > 0) { |
| src1.6.6/rdfw.cpp:5881 | Move | FactValue,hold_id | C | True | False | MarkDirectLocationEvidence(hold_id, FactValue(StateField::HOLD)==hold_id, |
| src1.6.6/rdfw.cpp:5882 | Move | EvidenceSource | C | True | False | EvidenceSource::RELATION_DERIVED); |
| src1.6.6/rdfw.cpp:5883 | Move | hold_id | C | True | False | DependOn(StateField::LOCATION,hold_id,StateField::HOLD,0); |
| src1.6.6/rdfw.cpp:5884 | Move | hold_id | C | True | False | DependOn(StateField::LOCATION,hold_id,StateField::LOCATION,0); |
| src1.6.6/rdfw.cpp:5886 | Move | plate_id | C | True | False | if (plate_id > 0) { |
| src1.6.6/rdfw.cpp:5887 | Move | FactValue,plate_id | C | True | False | MarkDirectLocationEvidence(plate_id, FactValue(StateField::PLATE)==plate_id, |
| src1.6.6/rdfw.cpp:5888 | Move | EvidenceSource | C | True | False | EvidenceSource::RELATION_DERIVED); |
| src1.6.6/rdfw.cpp:5889 | Move | plate_id | C | True | False | DependOn(StateField::LOCATION,plate_id,StateField::PLATE,0); |
| src1.6.6/rdfw.cpp:5890 | Move | plate_id | C | True | False | DependOn(StateField::LOCATION,plate_id,StateField::LOCATION,0); |
| src1.6.6/rdfw.cpp:5905 | Move | hold_id | C | True | False | if (hold_id > 0 && safe_idx(hold_id)) { |
| src1.6.6/rdfw.cpp:5906 | Move | hold_id | C | True | False | move_cons[hold_id][a] = 0; |
| src1.6.6/rdfw.cpp:5907 | Move | hold_id | C | True | False | objects[hold_id]->is_keep = 0; |
| src1.6.6/rdfw.cpp:5938 | PrintEnv | location | D | True | False | if (v->location == UNKNOWN) |
| src1.6.6/rdfw.cpp:5943 | PrintEnv | location | D | True | False | if (v->location < 0 \|\| v->location > MAX_LOCATION_ID) { |
| src1.6.6/rdfw.cpp:5947 | PrintEnv | location | D | True | False | if (static_cast<std::size_t>(v->location) >= objPos.size()) |
| src1.6.6/rdfw.cpp:5948 | PrintEnv | location | D | True | False | objPos.resize(v->location + 1); // expand objPos |
| src1.6.6/rdfw.cpp:5949 | PrintEnv | location | D | True | False | objPos[v->location].push_back(v); |
| src1.6.6/rdfw.cpp:5965 | PrintEnv | hold,plate | D | True | False | // print robot info (green) (hold, plate) |
| src1.6.6/rdfw.cpp:5967 | PrintEnv | hold,hold_id,plate,plate_id | D | True | False | cout << GREEN << "(" << v->sort << " hold:" << hold_id << " plate:" << plate_id << ")" << RESET; |
| src1.6.6/rdfw.cpp:5978 | PrintEnv | inside | D | True | False | cout << " inside:["; |
| src1.6.6/rdfw.cpp:5981 | PrintEnv | isOpen | D | True | False | cout << "] " << (p->isOpen ? "Open" : "Closed"); |
| src1.6.6/rdfw.cpp:6239 | ValidateInstruction | plate | A | True | False | else if (behave == "plate") |
| src1.6.6/rdfw.cpp:6241 | ValidateInstruction | inside | A | True | False | else if (behave == "inside" \|\| behave == "in") |
| src1.6.6/rdfw.cpp:6252 | ValidateInstruction | structuredSource | A | True | False | if (schema.give_form && !instruction.structuredSource && |
| src1.6.6/rdfw.cpp:6266 | ValidateInstruction | structuredSource | A | True | False | if (instruction.structuredSource) { |
| src1.6.6/rdfw.cpp:6357 | ValidateInstruction | inside | D | True | False | // synchronous per-item success logging inside the real-time budget. |
| src1.6.6/rdfw.cpp:6510 | ParseEnvSentence | hold,plate | C | True | False | const bool unary = firstToken == "hold" \|\| firstToken == "plate" \|\| |
| src1.6.6/rdfw.cpp:6514 | ParseEnvSentence | inside | C | True | False | firstToken == "inside" \|\| firstToken == "type"; |
| src1.6.6/rdfw.cpp:6529 | ParseEnvSentence | hold | C | True | False | if (firstToken == "hold") |
| src1.6.6/rdfw.cpp:6532 | ParseEnvSentence | hold_id | C | True | False | this->hold_id = index; |
| src1.6.6/rdfw.cpp:6535 | ParseEnvSentence | plate | C | True | False | else if (firstToken == "plate") |
| src1.6.6/rdfw.cpp:6537 | ParseEnvSentence | plate_id | C | True | False | this->plate_id = index; |
| src1.6.6/rdfw.cpp:6565 | ParseEnvSentence | EvidenceSource | C | True | False | ApplyStateValue(StateField::CONTAINER_STATE,index,(firstToken == "opened"),stage == 1,EvidenceSource::INITIAL); |
| src1.6.6/rdfw.cpp:6570 | ParseEnvSentence | location | C | True | False | LOG_ERROR("Env sentence has an invalid location: %s", sentence.c_str()); |
| src1.6.6/rdfw.cpp:6574 | ParseEnvSentence | EvidenceSource | C | True | False | location_id, EvidenceSource::INITIAL)) { |
| src1.6.6/rdfw.cpp:6575 | ParseEnvSentence | EvidenceSource | C | True | False | ApplyStateValue(StateField::LOCATION,index,UNKNOWN,false,EvidenceSource::UNKNOWN); |
| src1.6.6/rdfw.cpp:6581 | ParseEnvSentence | location | C | True | False | obj->location = location_id; |
| src1.6.6/rdfw.cpp:6585 | ParseEnvSentence | EvidenceSource | C | True | False | MarkDirectLocationEvidence(index, index == 0 \|\| stage == 1, EvidenceSource::INITIAL); |
| src1.6.6/rdfw.cpp:6605 | ParseEnvSentence | inside | C | True | False | } else if (firstToken == "color" \|\| firstToken == "inside") { |
| src1.6.6/rdfw.cpp:6619 | ParseEnvSentence | inside | C | True | False | LOG_ERROR("Env sentence has an invalid inside reference: %s", |
| src1.6.6/rdfw.cpp:6624 | ParseEnvSentence | EvidenceSource | C | True | False | container_id, EvidenceSource::INITIAL)) { |
| src1.6.6/rdfw.cpp:6625 | ParseEnvSentence | EvidenceSource | C | True | False | ApplyStateValue(StateField::INSIDE,index,UNKNOWN,false,EvidenceSource::UNKNOWN); |
| src1.6.6/rdfw.cpp:6628 | ParseEnvSentence | EvidenceSource | C | True | False | ApplyStateValue(StateField::INSIDE,index,container_id,stage == 1,EvidenceSource::INITIAL); |
| src1.6.6/rdfw.cpp:6677 | ParseEnv | inside | D | True | False | // Preserve explicit ASP locations before inside propagates planner locations. |
| src1.6.6/rdfw.cpp:6680 | ParseEnv | hold_id | C | True | False | if (hold_id > 0) |
| src1.6.6/rdfw.cpp:6682 | ParseEnv | hold_id | C | True | False | auto held = std::dynamic_pointer_cast<SmallObject>(GetObject(hold_id)); |
| src1.6.6/rdfw.cpp:6684 | ParseEnv | hold,hold_id | C | True | False | LOG_ERROR("Ignoring invalid hold reference %d", hold_id); |
| src1.6.6/rdfw.cpp:6685 | ParseEnv | hold_id | C | True | False | hold_id = NONE; |
| src1.6.6/rdfw.cpp:6686 | ParseEnv | EvidenceSource | C | True | False | SetHold(nullptr, EvidenceSource::INITIAL); |
| src1.6.6/rdfw.cpp:6688 | ParseEnv | EvidenceSource | C | True | False | SetHold(held, EvidenceSource::INITIAL); |
| src1.6.6/rdfw.cpp:6689 | ParseEnv | hold_id,location | C | True | False | score_locations[hold_id] = location; |
| src1.6.6/rdfw.cpp:6690 | ParseEnv | EvidenceSource,hold_id | C | True | False | MarkDirectLocationEvidence(hold_id, stage == 1, EvidenceSource::INITIAL); |
| src1.6.6/rdfw.cpp:6691 | ParseEnv | EvidenceSource,hold_id | C | True | False | SetInsideEvidence(hold_id, stage == 1, EvidenceSource::INITIAL); |
| src1.6.6/rdfw.cpp:6694 | ParseEnv | plate_id | C | True | False | if (plate_id > 0) |
| src1.6.6/rdfw.cpp:6696 | ParseEnv | plate_id | C | True | False | auto plated = std::dynamic_pointer_cast<SmallObject>(GetObject(plate_id)); |
| src1.6.6/rdfw.cpp:6697 | ParseEnv | hold_id,plate_id | C | True | False | if (!plated \|\| plate_id == hold_id) { |
| src1.6.6/rdfw.cpp:6698 | ParseEnv | plate,plate_id | C | True | False | LOG_ERROR("Ignoring invalid plate reference %d", plate_id); |
| src1.6.6/rdfw.cpp:6699 | ParseEnv | plate_id | C | True | False | plate_id = NONE; |
| src1.6.6/rdfw.cpp:6700 | ParseEnv | EvidenceSource | C | True | False | SetPlate(nullptr, EvidenceSource::INITIAL); |
| src1.6.6/rdfw.cpp:6702 | ParseEnv | EvidenceSource | C | True | False | SetPlate(plated, EvidenceSource::INITIAL); |
| src1.6.6/rdfw.cpp:6703 | ParseEnv | location,plate_id | C | True | False | score_locations[plate_id] = location; |
| src1.6.6/rdfw.cpp:6704 | ParseEnv | EvidenceSource,plate_id | C | True | False | MarkDirectLocationEvidence(plate_id, stage == 1, EvidenceSource::INITIAL); |
| src1.6.6/rdfw.cpp:6705 | ParseEnv | EvidenceSource,plate_id | C | True | False | SetInsideEvidence(plate_id, stage == 1, EvidenceSource::INITIAL); |
| src1.6.6/rdfw.cpp:6708 | ParseEnv | holdProvenance | C | True | False | if (!holdProvenance.received.present) |
| src1.6.6/rdfw.cpp:6709 | ParseEnv | UpdateProvenance,hold_id | C | True | False | UpdateProvenance(StateField::HOLD, 0, hold_id, |
| src1.6.6/rdfw.cpp:6710 | ParseEnv | EvidenceSource | C | True | False | stage == 1, EvidenceSource::INITIAL); |
| src1.6.6/rdfw.cpp:6711 | ParseEnv | plateProvenance | C | True | False | if (!plateProvenance.received.present) |
| src1.6.6/rdfw.cpp:6712 | ParseEnv | UpdateProvenance,plate_id | C | True | False | UpdateProvenance(StateField::PLATE, 0, plate_id, |
| src1.6.6/rdfw.cpp:6713 | ParseEnv | EvidenceSource | C | True | False | stage == 1, EvidenceSource::INITIAL); |
| src1.6.6/rdfw.cpp:6717 | ParseEnv | hold,plate | C | True | False | if (s == plate \|\| s == hold) |
| src1.6.6/rdfw.cpp:6719 | ParseEnv | inside | C | True | False | if (s->inside != UNKNOWN && s->inside != NONE) |
| src1.6.6/rdfw.cpp:6721 | ParseEnv | inside | C | True | False | auto p = dynamic_pointer_cast<Container>(GetObject(s->inside)); |
| src1.6.6/rdfw.cpp:6727 | ParseEnv | FactLocation | C | True | False | const int container_fact = FactLocation(p->id); |
| src1.6.6/rdfw.cpp:6728 | ParseEnv | location | C | True | False | ApplyStateValue(StateField::LOCATION,s->id,container_fact!=UNKNOWN?container_fact:p->location, |
| src1.6.6/rdfw.cpp:6729 | ParseEnv | FactInside | C | True | False | FactInside(s->id)==p->id && container_fact!=UNKNOWN, |
| src1.6.6/rdfw.cpp:6730 | ParseEnv | EvidenceSource | C | True | False | EvidenceSource::INITIAL); |
| src1.6.6/rdfw.cpp:6736 | ParseEnv | location | C | True | False | s->location = UNKNOWN; |
| src1.6.6/rdfw.cpp:6737 | ParseEnv | inside | C | True | False | s->inside = UNKNOWN; |
| src1.6.6/rdfw.cpp:6738 | ParseEnv | EvidenceSource | C | True | False | MarkDirectLocationEvidence(s->id,false,EvidenceSource::UNKNOWN); |
| src1.6.6/rdfw.cpp:6739 | ParseEnv | EvidenceSource | C | True | False | SetInsideEvidence(s->id,false,EvidenceSource::UNKNOWN); |
| src1.6.6/rdfw.cpp:6742 | ParseEnv | location | C | True | False | else if (s->location != UNKNOWN && |
| src1.6.6/rdfw.cpp:6744 | ParseEnv | inside | C | True | False | s->inside = NONE; |
| src1.6.6/rdfw.cpp:6745 | ParseEnv | hold,inside,plate | C | True | False | if (s->inside != UNKNOWN && s != plate && s != hold && |
| src1.6.6/rdfw.cpp:6746 | ParseEnv | Provenance,inside | C | True | False | Provenance(StateField::INSIDE,s->id).resolved_value!=s->inside) |
| src1.6.6/rdfw.cpp:6747 | ParseEnv | EvidenceSource | C | True | False | SetInsideEvidence(s->id, stage == 1, EvidenceSource::INITIAL); |
| src1.6.6/rdfw.cpp:6748 | ParseEnv | EvidenceSource,LocationSource,location | C | True | False | if (s->location != UNKNOWN && LocationSource(s->id) == EvidenceSource::UNKNOWN) |
| src1.6.6/rdfw.cpp:6749 | ParseEnv | EvidenceSource | C | True | False | MarkDirectLocationEvidence(s->id, stage == 1, EvidenceSource::INITIAL); |
| src1.6.6/rdfw.cpp:6774 | ParseInfo | FactLocation | C | True | False | const int yFact = FactLocation(info.Y[0]->id); |
| src1.6.6/rdfw.cpp:6775 | ParseInfo | location | C | True | False | int thelocation = yFact!=UNKNOWN ? yFact : info.Y[0]->location; |
| src1.6.6/rdfw.cpp:6778 | ParseInfo | EvidenceSource,IsLocationVerified | C | True | False | ApplyStateValue(StateField::LOCATION,v->id,thelocation,stage == 1 && IsLocationVerified(info.Y[0]->id),EvidenceSource::EXPLICIT_INFO); |
| src1.6.6/rdfw.cpp:6782 | ParseInfo | location | D | True | False | // Official on/near mean co-location; neither proves outside. |
| src1.6.6/rdfw.cpp:6790 | ParseInfo | FactLocation | C | True | False | const int yFact = FactLocation(info.Y[0]->id); |
| src1.6.6/rdfw.cpp:6791 | ParseInfo | FactLocation | C | True | False | const int xFact = FactLocation(info.X[0]->id); |
| src1.6.6/rdfw.cpp:6792 | ParseInfo | location | C | True | False | int yLocation = yFact!=UNKNOWN ? yFact : info.Y[0]->location; |
| src1.6.6/rdfw.cpp:6793 | ParseInfo | location | C | True | False | int xLocation = xFact!=UNKNOWN ? xFact : info.X[0]->location; |
| src1.6.6/rdfw.cpp:6799 | ParseInfo | EvidenceSource,IsLocationVerified | C | True | False | ApplyStateValue(StateField::LOCATION,v->id,yLocation,stage == 1 && IsLocationVerified(info.Y[0]->id),EvidenceSource::EXPLICIT_INFO); |
| src1.6.6/rdfw.cpp:6812 | ParseInfo | EvidenceSource,IsLocationVerified | C | True | False | ApplyStateValue(StateField::LOCATION,v->id,xLocation,stage == 1 && IsLocationVerified(info.X[0]->id),EvidenceSource::EXPLICIT_INFO); |
| src1.6.6/rdfw.cpp:6821 | ParseInfo | plate | C | True | False | else if (behave == "plate") |
| src1.6.6/rdfw.cpp:6823 | ParseInfo | plate | C | True | False | if (plate == nullptr) |
| src1.6.6/rdfw.cpp:6828 | ParseInfo | EvidenceSource,hold_id | C | True | False | if (hold_id == small->id) SetHold(nullptr, EvidenceSource::EXPLICIT_INFO); |
| src1.6.6/rdfw.cpp:6829 | ParseInfo | EvidenceSource | C | True | False | SetPlate(small, EvidenceSource::EXPLICIT_INFO); |
| src1.6.6/rdfw.cpp:6830 | ParseInfo | EvidenceSource | C | True | False | SetInsideEvidence(small->id, stage == 1, EvidenceSource::EXPLICIT_INFO); |
| src1.6.6/rdfw.cpp:6834 | ParseInfo | plate | C | True | False | LOG_ERROR("The plate already has a small object (%d %s)", plate->id, plate->sort.c_str()); |
| src1.6.6/rdfw.cpp:6837 | ParseInfo | inside | C | True | False | else if (behave == "inside" \|\| behave == "in") |
| src1.6.6/rdfw.cpp:6848 | ParseInfo | EvidenceSource,hold_id | C | True | False | if (hold_id == p->id) SetHold(nullptr, EvidenceSource::EXPLICIT_INFO); |
| src1.6.6/rdfw.cpp:6849 | ParseInfo | EvidenceSource,plate_id | C | True | False | if (plate_id == p->id) SetPlate(nullptr, EvidenceSource::EXPLICIT_INFO); |
| src1.6.6/rdfw.cpp:6851 | ParseInfo | inside | C | True | False | p->inside = cId; |
| src1.6.6/rdfw.cpp:6852 | ParseInfo | FactLocation | C | True | False | const int containerFact = FactLocation(cId); |
| src1.6.6/rdfw.cpp:6853 | ParseInfo | location | C | True | False | p->location=containerFact!=UNKNOWN ? containerFact : c->location; |
| src1.6.6/rdfw.cpp:6854 | ParseInfo | EvidenceSource | C | True | False | SetInsideEvidence(p->id, stage == 1, EvidenceSource::EXPLICIT_INFO); |
| src1.6.6/rdfw.cpp:6855 | ParseInfo | IsLocationVerified | C | True | False | MarkDirectLocationEvidence(p->id, stage == 1 && IsLocationVerified(cId), |
| src1.6.6/rdfw.cpp:6856 | ParseInfo | EvidenceSource | C | True | False | EvidenceSource::EXPLICIT_INFO); |
| src1.6.6/rdfw.cpp:6868 | ParseInfo | EvidenceSource | C | True | False | ApplyStateValue(StateField::CONTAINER_STATE,p->id,true,stage == 1,EvidenceSource::EXPLICIT_INFO); |
| src1.6.6/rdfw.cpp:6877 | ParseInfo | EvidenceSource | C | True | False | ApplyStateValue(StateField::CONTAINER_STATE,p->id,false,stage == 1,EvidenceSource::EXPLICIT_INFO); |
| src1.6.6/rdfw.cpp:6996 | Fini | StateProvenance,holdProvenance,plateProvenance | C | True | False | holdProvenance=StateProvenance(); plateProvenance=StateProvenance(); |
| src1.6.6/rdfw.cpp:7000 | Fini | location | C | True | False | location = UNKNOWN; |
| src1.6.6/rdfw.cpp:7001 | Fini | hold | C | True | False | hold = nullptr; |
| src1.6.6/rdfw.cpp:7002 | Fini | hold_id | C | True | False | hold_id = 0; |
| src1.6.6/rdfw.cpp:7006 | Fini | plate | C | True | False | plate = nullptr; |
| src1.6.6/rdfw.cpp:7007 | Fini | plate_id | C | True | False | plate_id = 0; |
| src1.6.6/rdfw.cpp:7029 | Fini | objectLocationVerified | C | True | False | objectLocationVerified.clear(); |
| src1.6.6/rdfw.cpp:7030 | Fini | objectLocationInferredByMustNear | C | True | False | objectLocationInferredByMustNear.clear(); |
| src1.6.6/rdfw.cpp:7031 | Fini | objectInsideVerified | C | True | False | objectInsideVerified.clear(); |
| src1.6.6/rdfw.cpp:7032 | Fini | containerStateVerified | C | True | False | containerStateVerified.clear(); |
| src1.6.6/rdfw.cpp:7033 | Fini | objectLocationSource | C | True | False | objectLocationSource.clear(); |
| src1.6.6/rdfw.cpp:7034 | Fini | locationProvenance | C | True | False | locationProvenance.clear(); |
| src1.6.6/rdfw.cpp:7035 | Fini | insideProvenance | C | True | False | insideProvenance.clear(); |
| src1.6.6/rdfw.cpp:7036 | Fini | containerProvenance | C | True | False | containerProvenance.clear(); |
| src1.6.6/rdfw.cpp:7037 | Fini | objectInsideSource | C | True | False | objectInsideSource.clear(); |
| src1.6.6/rdfw.cpp:7038 | Fini | containerStateSource | C | True | False | containerStateSource.clear(); |
| src1.6.6/rdfw.cpp:7057 | Fini | objectLocationVerified | C | True | False | objectLocationVerified.shrink_to_fit(); |
| src1.6.6/rdfw.cpp:7058 | Fini | objectLocationInferredByMustNear | C | True | False | objectLocationInferredByMustNear.shrink_to_fit(); |
| src1.6.6/rdfw.cpp:7059 | Fini | objectInsideVerified | C | True | False | objectInsideVerified.shrink_to_fit(); |
| src1.6.6/rdfw.cpp:7060 | Fini | containerStateVerified | C | True | False | containerStateVerified.shrink_to_fit(); |
| src1.6.6/rdfw.cpp:7097 | Fini | objectLocationVerified | C | True | False | objectLocationVerified.resize(100, false); |
| src1.6.6/rdfw.cpp:7098 | Fini | objectLocationInferredByMustNear | C | True | False | objectLocationInferredByMustNear.resize(100, false); |
| src1.6.6/rdfw.cpp:7099 | Fini | objectInsideVerified | C | True | False | objectInsideVerified.resize(100, false); |
| src1.6.6/rdfw.cpp:7100 | Fini | containerStateVerified | C | True | False | containerStateVerified.resize(100, false); |
| src1.6.6/rdfw.cpp:7143 | OptimizeMemoryUsage | objectLocationVerified | A | True | False | objectLocationVerified.shrink_to_fit(); |
| src1.6.6/rdfw.cpp:7144 | OptimizeMemoryUsage | objectLocationInferredByMustNear | A | True | False | objectLocationInferredByMustNear.shrink_to_fit(); |
| src1.6.6/rdfw.cpp:7145 | OptimizeMemoryUsage | objectInsideVerified | A | True | False | objectInsideVerified.shrink_to_fit(); |
| src1.6.6/rdfw.cpp:7146 | OptimizeMemoryUsage | containerStateVerified | A | True | False | containerStateVerified.shrink_to_fit(); |
| src1.6.6/rdfw.cpp:7215 | Instruction | structuredSource | A | True | False | structuredSource = true; |
| src1.6.6/rdfw.cpp:7430 | BuildMustNearRelations | hold_id | A | True | False | hold_mustnear = hold_id > 0 && static_cast<size_t>(hold_id) < mustNearComponent.size() && |
| src1.6.6/rdfw.cpp:7431 | BuildMustNearRelations | hold_id | A | True | False | mustNearComponent[hold_id] != UNKNOWN; |
| src1.6.6/rdfw.cpp:7432 | BuildMustNearRelations | plate_id | A | True | False | plate_mustnear = plate_id > 0 && static_cast<size_t>(plate_id) < mustNearComponent.size() && |
| src1.6.6/rdfw.cpp:7433 | BuildMustNearRelations | plate_id | A | True | False | mustNearComponent[plate_id] != UNKNOWN; |
| src1.6.6/rdfw.cpp:7455 | RefreshMustNearConstraintState | location | C | True | False | const int loc = objects[id]->location; |
| src1.6.6/rdfw.cpp:7457 | RefreshMustNearConstraintState | FactLocation,objectLocationInferredByMustNear | C | True | False | if (FactLocation(id) == loc && !objectLocationInferredByMustNear[id]) |
| src1.6.6/rdfw.cpp:7459 | RefreshMustNearConstraintState | objectLocationInferredByMustNear | C | True | False | if (!objectLocationInferredByMustNear[id]) ++candidate_votes[loc]; |
| src1.6.6/rdfw.cpp:7479 | RefreshMustNearConstraintState | location | C | True | False | if (objects[id]->location == chosen_location && |
| src1.6.6/rdfw.cpp:7480 | RefreshMustNearConstraintState | objectLocationInferredByMustNear | C | True | False | !objectLocationInferredByMustNear[id] && |
| src1.6.6/rdfw.cpp:7481 | RefreshMustNearConstraintState | FactLocation | C | True | False | (direct_votes.empty() \|\| FactLocation(id) == chosen_location)) { |
| src1.6.6/rdfw.cpp:7497 | RefreshMustNearConstraintState | FactLocation,objectLocationInferredByMustNear | C | True | False | if (FactLocation(id) != UNKNOWN && !objectLocationInferredByMustNear[id] && |
| src1.6.6/rdfw.cpp:7498 | RefreshMustNearConstraintState | location | C | True | False | objects[id]->location != UNKNOWN && objects[id]->location != chosen_location) { |
| src1.6.6/rdfw.cpp:7509 | RefreshMustNearConstraintState | objectLocationInferredByMustNear | C | True | False | if (!objectLocationInferredByMustNear[id]) continue; |
| src1.6.6/rdfw.cpp:7511 | RefreshMustNearConstraintState | location | C | True | False | objects[id]->location != chosen_location) { |
| src1.6.6/rdfw.cpp:7512 | RefreshMustNearConstraintState | EvidenceSource | C | True | False | ApplyStateValue(StateField::LOCATION,id,UNKNOWN,false,EvidenceSource::UNKNOWN); |
| src1.6.6/rdfw.cpp:7516 | RefreshMustNearConstraintState | EvidenceSource | C | True | False | anchored ? EvidenceSource::CONSTRAINT_DERIVED |
| src1.6.6/rdfw.cpp:7517 | RefreshMustNearConstraintState | EvidenceSource | C | True | False | : EvidenceSource::CONSTRAINT_HEURISTIC); |
| src1.6.6/rdfw.cpp:7526 | RefreshMustNearConstraintState | location | C | True | False | if (objects[id]->location == chosen_location && |
| src1.6.6/rdfw.cpp:7527 | RefreshMustNearConstraintState | objectLocationInferredByMustNear | C | True | False | !objectLocationInferredByMustNear[id] && |
| src1.6.6/rdfw.cpp:7528 | RefreshMustNearConstraintState | FactLocation | C | True | False | (FactLocation(id) == chosen_location \|\| !anchored)) continue; |
| src1.6.6/rdfw.cpp:7530 | RefreshMustNearConstraintState | location | C | True | False | objects[id]->location = chosen_location; |
| src1.6.6/rdfw.cpp:7532 | RefreshMustNearConstraintState | EvidenceSource | C | True | False | anchored ? EvidenceSource::CONSTRAINT_DERIVED |
| src1.6.6/rdfw.cpp:7533 | RefreshMustNearConstraintState | EvidenceSource | C | True | False | : EvidenceSource::CONSTRAINT_HEURISTIC); |
| src1.6.6/rdfw.cpp:7538 | RefreshMustNearConstraintState | inside | D | True | False | // SmallObject::inside/on，near 本身不代表包含或承载关系。 |
| src1.6.6/rdfw.cpp:7542 | RefreshMustNearConstraintState | inside | C | True | False | if (!item \|\| item->inside != container->id) continue; |
| src1.6.6/rdfw.cpp:7543 | RefreshMustNearConstraintState | location | C | True | False | item->location = chosen_location; |
| src1.6.6/rdfw.cpp:7544 | RefreshMustNearConstraintState | FactInside | C | True | False | const bool location_entailed = anchored && FactInside(item->id) == container->id; |
| src1.6.6/rdfw.cpp:7546 | RefreshMustNearConstraintState | EvidenceSource | C | True | False | location_entailed ? EvidenceSource::CONSTRAINT_DERIVED |
| src1.6.6/rdfw.cpp:7547 | RefreshMustNearConstraintState | EvidenceSource | C | True | False | : EvidenceSource::CONSTRAINT_HEURISTIC); |
| src1.6.6/rdfw.cpp:7552 | RefreshMustNearConstraintState | location | C | True | False | LOG(GREEN "[MustNear] inferred obj %u at location %d\n" RESET, |
| src1.6.6/rdfw.cpp:7560 | RefreshMustNearConstraintState | location | C | True | False | const int loc = objects[id]->location; |
| src1.6.6/rdfw.cpp:7601 | ApplyMustInConstraintCorrection | inside | C | True | False | if (cons.IsUsable() && (cons.behave == "inside" \|\| cons.behave == "in") && |
| src1.6.6/rdfw.cpp:7616 | ApplyMustInConstraintCorrection | inside | C | True | False | cout<<"sm->inside: "<<sm->inside<<endl; |
| src1.6.6/rdfw.cpp:7618 | ApplyMustInConstraintCorrection | inside | C | True | False | if (sm->inside != UNKNOWN && sm->inside != y) { |
| src1.6.6/rdfw.cpp:7619 | ApplyMustInConstraintCorrection | inside | C | True | False | if (sm->inside >= 0 && sm->inside < numObjs) { |
| src1.6.6/rdfw.cpp:7620 | ApplyMustInConstraintCorrection | inside | C | True | False | if (auto old_cont = std::dynamic_pointer_cast<Container>(objects[sm->inside])) { |
| src1.6.6/rdfw.cpp:7629 | ApplyMustInConstraintCorrection | EvidenceSource | C | True | False | ApplyStateValue(StateField::INSIDE,x,y,true,EvidenceSource::CONSTRAINT_DERIVED); |
| src1.6.6/rdfw.cpp:7647 | ApplyMustInConstraintCorrection | FactLocation | C | True | False | const int y_fact = FactLocation(y); |
| src1.6.6/rdfw.cpp:7648 | ApplyMustInConstraintCorrection | location | C | True | False | int y_loc = y_fact!=UNKNOWN ? y_fact : objects[y]->location; |
| src1.6.6/rdfw.cpp:7650 | ApplyMustInConstraintCorrection | location | C | True | False | objects[x]->location = y_loc; |
| src1.6.6/rdfw.cpp:7653 | ApplyMustInConstraintCorrection | EvidenceSource | C | True | False | location_entailed ? EvidenceSource::CONSTRAINT_DERIVED |
| src1.6.6/rdfw.cpp:7654 | ApplyMustInConstraintCorrection | EvidenceSource | C | True | False | : EvidenceSource::CONSTRAINT_HEURISTIC); |
| src1.6.6/rdfw.cpp:7667 | ApplyMustInConstraintCorrection | inside | C | True | False | if (cons.behave != "inside"&&cons.behave != "in") continue; |
| src1.6.6/rdfw.cpp:7676 | ApplyMustInConstraintCorrection | inside | C | True | False | if (smObj->inside == y) { |
| src1.6.6/rdfw.cpp:7678 | ApplyMustInConstraintCorrection | inside | C | True | False | smObj->inside = UNKNOWN; |
| src1.6.6/rdfw.cpp:7679 | ApplyMustInConstraintCorrection | location | C | True | False | int old_loc = smObj->location; |
| src1.6.6/rdfw.cpp:7680 | ApplyMustInConstraintCorrection | location | C | True | False | smObj->location = UNKNOWN; |
| src1.6.6/rdfw.cpp:7681 | ApplyMustInConstraintCorrection | EvidenceSource | C | True | False | SetInsideEvidence(x,false,EvidenceSource::UNKNOWN); |
| src1.6.6/rdfw.cpp:7682 | ApplyMustInConstraintCorrection | EvidenceSource | C | True | False | MarkDirectLocationEvidence(x,false,EvidenceSource::UNKNOWN); |
| src1.6.6/rdfw.cpp:7733 | ApplyOpenCloseCorrection | isOpen | C | True | False | if (cont->isOpen != 1) { |
| src1.6.6/rdfw.cpp:7734 | ApplyOpenCloseCorrection | isOpen | C | True | False | cont->isOpen = true; |
| src1.6.6/rdfw.cpp:7740 | ApplyOpenCloseCorrection | isOpen | C | True | False | if (cont->isOpen) { |
| src1.6.6/rdfw.cpp:7741 | ApplyOpenCloseCorrection | isOpen | C | True | False | cont->isOpen = false; |
| src1.6.6/rdfw.cpp:7747 | ApplyOpenCloseCorrection | isOpen | C | True | False | if (cont->isOpen) { |
| src1.6.6/rdfw.cpp:7748 | ApplyOpenCloseCorrection | isOpen | C | True | False | cont->isOpen = false; |
| src1.6.6/rdfw.cpp:7754 | ApplyOpenCloseCorrection | isOpen | C | True | False | if (cont->isOpen != 1) { |
| src1.6.6/rdfw.cpp:7755 | ApplyOpenCloseCorrection | isOpen | C | True | False | cont->isOpen = true; |
| src1.6.6/rdfw.cpp:7762 | ApplyOpenCloseCorrection | isOpen | C | True | False | cont->isOpen = false; |
| src1.6.6/rdfw.cpp:7770 | ApplyOpenCloseCorrection | EvidenceSource | C | True | False | contradictory ? EvidenceSource::CONSTRAINT_HEURISTIC |
| src1.6.6/rdfw.cpp:7771 | ApplyOpenCloseCorrection | EvidenceSource | C | True | False | : EvidenceSource::CONSTRAINT_DERIVED); |
| src1.6.6/rdfw.hpp:36 | declaration/inline | Source | D | True | False | // Source of the current fact, separate from whether it is reliable enough |
| src1.6.6/rdfw.hpp:38 | declaration/inline | EvidenceSource | D | True | False | enum class EvidenceSource { |
| src1.6.6/rdfw.hpp:44 | declaration/inline | StateProvenance | D | True | False | // StateProvenance plus canonical queries alone qualify current facts. |
| src1.6.6/rdfw.hpp:48 | declaration/inline | EvidenceSource | D | True | False | EvidenceSource source = EvidenceSource::UNKNOWN; |
| src1.6.6/rdfw.hpp:51 | StateClaim | EvidenceSource | A | True | False | StateClaim(int v, EvidenceSource s, bool p) : value(v), source(s), present(p) {} |
| src1.6.6/rdfw.hpp:62 | declaration/inline | StateProvenance | D | True | False | struct StateProvenance { |
| src1.6.6/rdfw.hpp:66 | declaration/inline | EvidenceSource | D | True | False | EvidenceSource resolved_source = EvidenceSource::UNKNOWN; |
| src1.6.6/rdfw.hpp:107 | declaration/inline | location | D | True | False | *      location    (int)   : ... |
| src1.6.6/rdfw.hpp:113 | declaration/inline | location | D | True | False | *      Object (Init)       : Initialize id, sort and location (id must be known) |
| src1.6.6/rdfw.hpp:119 | declaration/inline | location | D | True | False | int location; |
| src1.6.6/rdfw.hpp:125 | Object | location | C | True | False | Object(int id, const string &sort = "", int location = UNKNOWN) |
| src1.6.6/rdfw.hpp:126 | Object | location | C | True | False | : sort(sort), location(location), id(id) {}   // Initialize id, sort and location (id must be known) |
| src1.6.6/rdfw.hpp:131 | ToString | location | D | True | False | return "id:" + to_string(id) + "    at:" + to_string(location) + "     sort:" + sort + "\n"; |
| src1.6.6/rdfw.hpp:142 | declaration/inline | inside | D | True | False | *      inside      (int)   : the big object id which small object inside |
| src1.6.6/rdfw.hpp:145 | declaration/inline | location | D | True | False | *      Object (Init)       : Initialize id, sort and location (id must be known) |
| src1.6.6/rdfw.hpp:152 | declaration/inline | inside | D | True | False | int inside = UNKNOWN;  // the big object id which small object inside |
| src1.6.6/rdfw.hpp:156 | SmallObject | location | C | True | False | SmallObject(int id, int location = UNKNOWN, const string &sort = "", const string &color = "") |
| src1.6.6/rdfw.hpp:157 | SmallObject | location | C | True | False | : Object(id, sort, location), color(color) {} |
| src1.6.6/rdfw.hpp:166 | ToString | inside | D | True | False | return Object::ToString() + "color:" + color + "    inside:" + to_string(inside) + "    on:" + to_string(on) + "\n"; |
| src1.6.6/rdfw.hpp:176 | declaration/inline | inside | D | True | False | *      inside      (int)   : the big object id which small object inside |
| src1.6.6/rdfw.hpp:183 | BigObject | location | C | True | False | BigObject(int id, int location = UNKNOWN, string sort = "") |
| src1.6.6/rdfw.hpp:184 | BigObject | location | C | True | False | : Object(id, sort, location) {} |
| src1.6.6/rdfw.hpp:198 | declaration/inline | isOpen | D | True | False | *      isOpen      (int)   : 0(closed)  1(open) |
| src1.6.6/rdfw.hpp:200 | declaration/inline | inside | D | True | False | *      inside      (int)   : the big object id which small object inside |
| src1.6.6/rdfw.hpp:210 | declaration/inline | isOpen | D | True | False | int isOpen = 0; |
| src1.6.6/rdfw.hpp:212 | Container | isOpen,location | C | True | False | Container(int id, int location = UNKNOWN, bool isOpen = true, string sort = "") |
| src1.6.6/rdfw.hpp:213 | Container | isOpen,location | C | True | False | : BigObject(id, location, sort), isOpen(isOpen) {} |
| src1.6.6/rdfw.hpp:217 | Container | isOpen | C | True | False | : BigObject(obj), isOpen(UNKNOWN) {} |
| src1.6.6/rdfw.hpp:221 | Container | isOpen | C | True | False | : BigObject(*obj), isOpen(UNKNOWN) {} |
| src1.6.6/rdfw.hpp:251 | declaration/inline | hold | D | True | False | *      hold        (shared_ptr<SmallObject>)   : ... |
| src1.6.6/rdfw.hpp:252 | declaration/inline | plate | D | True | False | *      plate       (shared_ptr<SmallObject>)   : ... |
| src1.6.6/rdfw.hpp:253 | declaration/inline | hold_id | D | True | False | *      hold_id     (int)   : ... |
| src1.6.6/rdfw.hpp:254 | declaration/inline | plate_id | D | True | False | *      plate_id    (int)   : ... |
| src1.6.6/rdfw.hpp:264 | declaration/inline | hold | D | True | False | shared_ptr<SmallObject> hold; |
| src1.6.6/rdfw.hpp:265 | declaration/inline | plate | D | True | False | shared_ptr<SmallObject> plate; |
| src1.6.6/rdfw.hpp:267 | declaration/inline | hold_id,plate_id | D | True | False | int hold_id = NONE, plate_id = UNKNOWN; |
| src1.6.6/rdfw.hpp:269 | Robot | location | C | True | False | Robot(int id, int location = UNKNOWN) |
| src1.6.6/rdfw.hpp:270 | Robot | location | C | True | False | : Object(id, "robot", location) {} |
| src1.6.6/rdfw.hpp:274 | SetHold | hold | C | True | False | void SetHold(const shared_ptr<SmallObject> &hold) { |
| src1.6.6/rdfw.hpp:275 | SetHold | hold | C | True | False | this->hold = hold; |
| src1.6.6/rdfw.hpp:276 | SetHold | hold | C | True | False | if (hold != nullptr) { |
| src1.6.6/rdfw.hpp:277 | SetHold | hold,location | C | True | False | this->hold->location = location; |
| src1.6.6/rdfw.hpp:278 | SetHold | hold,hold_id | C | True | False | hold_id = hold->id; |
| src1.6.6/rdfw.hpp:279 | SetHold | hold,inside | C | True | False | hold->inside = NONE; |
| src1.6.6/rdfw.hpp:280 | SetHold | hold | C | True | False | hold->on = NONE; |
| src1.6.6/rdfw.hpp:281 | SetHold | hold_id,plate_id | C | True | False | if (plate_id == hold_id) { |
| src1.6.6/rdfw.hpp:282 | SetHold | plate | C | True | False | plate.reset(); |
| src1.6.6/rdfw.hpp:283 | SetHold | plate_id | C | True | False | plate_id = NONE; |
| src1.6.6/rdfw.hpp:287 | SetHold | hold_id | C | True | False | hold_id = NONE; |
| src1.6.6/rdfw.hpp:290 | SetPlate | plate | C | True | False | void SetPlate(const shared_ptr<SmallObject> &plate) { |
| src1.6.6/rdfw.hpp:291 | SetPlate | plate | C | True | False | this->plate = plate; |
| src1.6.6/rdfw.hpp:292 | SetPlate | plate | C | True | False | if (plate != nullptr) { |
| src1.6.6/rdfw.hpp:293 | SetPlate | location,plate | C | True | False | this->plate->location = location; |
| src1.6.6/rdfw.hpp:294 | SetPlate | plate,plate_id | C | True | False | plate_id = plate->id; |
| src1.6.6/rdfw.hpp:295 | SetPlate | inside,plate | C | True | False | plate->inside = NONE; |
| src1.6.6/rdfw.hpp:296 | SetPlate | plate | C | True | False | plate->on = NONE; |
| src1.6.6/rdfw.hpp:297 | SetPlate | hold_id,plate_id | C | True | False | if (hold_id == plate_id) { |
| src1.6.6/rdfw.hpp:298 | SetPlate | hold | C | True | False | hold.reset(); |
| src1.6.6/rdfw.hpp:299 | SetPlate | hold_id | C | True | False | hold_id = NONE; |
| src1.6.6/rdfw.hpp:303 | SetPlate | plate_id | C | True | False | plate_id = NONE; |
| src1.6.6/rdfw.hpp:307 | ToString | hold,plate | D | True | False | return Object::ToString() + "hold:\n" + (hold != nullptr ? hold->ToString() : "") + "plate:\n" + (plate != nullptr ? plate->ToString() : ""); |
| src1.6.6/rdfw.hpp:443 | declaration/inline | inside | D | True | False | // Stage 1 ASP at facts, separate from planner locations inferred from inside. |
| src1.6.6/rdfw.hpp:475 | declaration/inline | inside | D | True | False | vector<vector<int>> putin_cons;      //not_info   inside   + not_task   putin |
| src1.6.6/rdfw.hpp:476 | declaration/inline | inside | D | True | False | vector<vector<int>> takeout_cons;    // ontnot_infor  inside   + not_task   takeout |
| src1.6.6/rdfw.hpp:478 | declaration/inline | hold,plate | D | True | False | vector<int> putdown1_cons;        //not_task   putdown  + hold  + plate |
| src1.6.6/rdfw.hpp:482 | declaration/inline | plate | D | True | False | vector<int> pickup_cons;         //not_info   plate   + not_task   pickup |
| src1.6.6/rdfw.hpp:485 | declaration/inline | hold | D | True | False | vector<int> fromplate_cons;      //hold |
| src1.6.6/rdfw.hpp:486 | declaration/inline | plate | D | True | False | vector<int> toplate_cons;        //plate |
| src1.6.6/rdfw.hpp:499 | declaration/inline | objectLocationInferredByMustNear | D | True | False | // objectLocationInferredByMustNear 用来区分直接证据和约束推导证据， |
| src1.6.6/rdfw.hpp:502 | declaration/inline | objectLocationInferredByMustNear | D | True | False | std::vector<bool> objectLocationInferredByMustNear; |
| src1.6.6/rdfw.hpp:528 | declaration/inline | FactValue,ResolvedState | D | True | False | // Object fields to answer truth; query ResolvedState/FactValue instead. |
| src1.6.6/rdfw.hpp:529 | declaration/inline | objectLocationVerified | D | True | False | vector<bool> objectLocationVerified; |
| src1.6.6/rdfw.hpp:530 | declaration/inline | objectInsideVerified | D | True | False | vector<bool> objectInsideVerified; |
| src1.6.6/rdfw.hpp:531 | declaration/inline | containerStateVerified | D | True | False | vector<bool> containerStateVerified; |
| src1.6.6/rdfw.hpp:532 | declaration/inline | EvidenceSource,objectLocationSource | D | True | False | vector<EvidenceSource> objectLocationSource; |
| src1.6.6/rdfw.hpp:533 | declaration/inline | EvidenceSource,objectInsideSource | D | True | False | vector<EvidenceSource> objectInsideSource; |
| src1.6.6/rdfw.hpp:534 | declaration/inline | EvidenceSource,containerStateSource | D | True | False | vector<EvidenceSource> containerStateSource; |
| src1.6.6/rdfw.hpp:536 | declaration/inline | StateProvenance,locationProvenance | D | True | False | vector<StateProvenance> locationProvenance; |
| src1.6.6/rdfw.hpp:537 | declaration/inline | StateProvenance,insideProvenance | D | True | False | vector<StateProvenance> insideProvenance; |
| src1.6.6/rdfw.hpp:538 | declaration/inline | StateProvenance,containerProvenance | D | True | False | vector<StateProvenance> containerProvenance; |
| src1.6.6/rdfw.hpp:539 | declaration/inline | StateProvenance,holdProvenance | D | True | False | StateProvenance holdProvenance; |
| src1.6.6/rdfw.hpp:540 | declaration/inline | StateProvenance,plateProvenance | D | True | False | StateProvenance plateProvenance; |
| src1.6.6/rdfw.hpp:541 | declaration/inline | Provenance,StateProvenance | D | True | False | const StateProvenance& Provenance(StateField field, unsigned int id) const; |
| src1.6.6/rdfw.hpp:545 | declaration/inline | DependenciesCurrent | D | True | False | bool DependenciesCurrent(StateField field, unsigned int id) const; |
| src1.6.6/rdfw.hpp:546 | declaration/inline | ResolvedState | D | True | False | StateClaim ResolvedState(StateField field, unsigned int id) const; |
| src1.6.6/rdfw.hpp:548 | declaration/inline | Source,Verified | D | True | False | // Source/Verified arrays or Object planning hypotheses for qualification. |
| src1.6.6/rdfw.hpp:549 | declaration/inline | FactValue | D | True | False | int FactValue(StateField field, unsigned int id = 0) const; |
| src1.6.6/rdfw.hpp:550 | FactLocation | FactLocation,FactValue | B | True | False | int FactLocation(unsigned int id) const { return FactValue(StateField::LOCATION, id); } |
| src1.6.6/rdfw.hpp:551 | FactInside | FactInside,FactValue | B | True | False | int FactInside(unsigned int id) const { return FactValue(StateField::INSIDE, id); } |
| src1.6.6/rdfw.hpp:552 | FactContainerState | FactContainerState,FactValue | B | True | False | int FactContainerState(unsigned int id) const { return FactValue(StateField::CONTAINER_STATE, id); } |
| src1.6.6/rdfw.hpp:554 | declaration/inline | IsStoredFact | D | True | False | bool IsStoredFact(unsigned int id) const; |
| src1.6.6/rdfw.hpp:555 | declaration/inline | IsNotStoredFact | D | True | False | bool IsNotStoredFact(unsigned int id) const; |
| src1.6.6/rdfw.hpp:559 | declaration/inline | EvidenceSource | D | True | False | bool verified, EvidenceSource source); |
| src1.6.6/rdfw.hpp:564 | declaration/inline | TaskFactSatisfied | D | True | False | bool TaskFactSatisfied(const std::string& behave, unsigned int x, |
| src1.6.6/rdfw.hpp:568 | declaration/inline | EvidenceSource | D | True | False | EvidenceSource source); |
| src1.6.6/rdfw.hpp:581 | declaration/inline | location | D | True | False | const LocationSensedInfo& GetLocationSensedInfo(int location) const; |
| src1.6.6/rdfw.hpp:582 | declaration/inline | location | D | True | False | bool HasObjectAtLocation(int location, unsigned int object_id) const; |
| src1.6.6/rdfw.hpp:583 | declaration/inline | location | D | True | False | bool HasContainerAtLocation(int location) const; |
| src1.6.6/rdfw.hpp:584 | declaration/inline | location | D | True | False | vector<unsigned int> GetObjectsAtLocation(int location) const; |
| src1.6.6/rdfw.hpp:585 | declaration/inline | location | D | True | False | unsigned int GetContainerAtLocation(int location) const; |
| src1.6.6/rdfw.hpp:586 | declaration/inline | location | D | True | False | int CountObjectsAtLocation(int location) const; |
| src1.6.6/rdfw.hpp:731 | declaration/inline | EvidenceSource | D | True | False | EvidenceSource source = EvidenceSource::ACTION_SUCCESS); |
| src1.6.6/rdfw.hpp:732 | declaration/inline | EvidenceSource | D | True | False | void SetInsideEvidence(unsigned int id, bool verified, EvidenceSource source); |
| src1.6.6/rdfw.hpp:733 | declaration/inline | EvidenceSource | D | True | False | void SetContainerEvidence(unsigned int id, bool verified, EvidenceSource source); |
| src1.6.6/rdfw.hpp:734 | declaration/inline | EvidenceSource,LocationSource | D | True | False | EvidenceSource LocationSource(unsigned int id) const; |
| src1.6.6/rdfw.hpp:735 | declaration/inline | EvidenceSource,InsideSource | D | True | False | EvidenceSource InsideSource(unsigned int id) const; |
| src1.6.6/rdfw.hpp:736 | declaration/inline | ContainerSource,EvidenceSource | D | True | False | EvidenceSource ContainerSource(unsigned int id) const; |
| src1.6.6/rdfw.hpp:751 | declaration/inline | IsLocationVerified | D | True | False | bool IsLocationVerified(unsigned int id) const; |
| src1.6.6/rdfw.hpp:752 | declaration/inline | IsInsideVerified | D | True | False | bool IsInsideVerified(unsigned int id) const; |
| src1.6.6/rdfw.hpp:753 | declaration/inline | IsContainerStateVerified | D | True | False | bool IsContainerStateVerified(unsigned int id) const; |
| src1.6.6/rdfw.hpp:756 | declaration/inline | EvidenceSource | D | True | False | EvidenceSource source = EvidenceSource::ACTION_SUCCESS); |
| src1.6.6/rdfw.hpp:758 | declaration/inline | EvidenceSource | D | True | False | EvidenceSource source = EvidenceSource::ACTION_SUCCESS); |
| src1.6.6/rdfw.hpp:855 | declaration/inline | MutableProvenance,StateProvenance | D | True | False | StateProvenance& MutableProvenance(StateField field, unsigned int id); |
| src1.6.6/rdfw.hpp:856 | declaration/inline | UpdateProvenance | D | True | False | void UpdateProvenance(StateField field, unsigned int id, int value, |
| src1.6.6/rdfw.hpp:857 | declaration/inline | EvidenceSource | D | True | False | bool verified, EvidenceSource source); |
| src1.6.6/rdfw.hpp:963 | declaration/inline | structuredSource | D | True | False | bool structuredSource = false; |
| src1.6.6/terminal_checker.cpp:29 | locationValue | FactLocation,location | A | True | False | return hypothesis ? o->location : w.FactLocation(o->id); |
| src1.6.6/terminal_checker.cpp:33 | insideValue | FactInside,inside | A | True | False | return hypothesis ? o->inside : w.FactInside(o->id); |
| src1.6.6/terminal_checker.cpp:37 | containerValue | FactContainerState,isOpen | A | True | False | return hypothesis ? o->isOpen : w.FactContainerState(o->id); |
| src1.6.6/terminal_checker.cpp:45 | scoreLocation | location | A | True | False | if (o->id==0) return w.location; |
| src1.6.6/terminal_checker.cpp:46 | scoreLocation | location | A | True | False | return o->id < w.score_locations.size() ? w.score_locations[o->id] : o->location; |
| src1.6.6/terminal_checker.cpp:78 | evaluatePair | FactLocation,location | A | True | False | const int robot_location=hypothesis?world.location:world.FactLocation(0); |
| src1.6.6/terminal_checker.cpp:79 | evaluatePair | FactValue,hold_id | A | True | False | const int hand=hypothesis?world.hold_id:world.FactValue(StateField::HOLD); |
| src1.6.6/terminal_checker.cpp:80 | evaluatePair | FactValue,plate_id | A | True | False | const int tray=hypothesis?world.plate_id:world.FactValue(StateField::PLATE); |
| src1.6.6/terminal_checker.cpp:82 | evaluatePair | IsNotStoredFact | B | True | False | const bool not_stored=hypothesis?(hand!=x->id && tray!=x->id):world.IsNotStoredFact(x->id); |
| src1.6.6/terminal_checker.cpp:107 | evaluatePair | IsInsideVerified | B | True | False | if (!hypothesis && world.stage == 2 && !world.IsInsideVerified(x->id)) |
| src1.6.6/terminal_checker.cpp:117 | evaluatePair | IsInsideVerified | B | True | False | if (!hypothesis && world.stage == 2 && !world.IsInsideVerified(x->id)) |
| src1.6.6/terminal_checker.cpp:124 | evaluatePair | inside | B | True | False | if (behave == "putin" \|\| behave == "inside" \|\| behave == "in") { |
| src1.6.6/terminal_checker.cpp:165 | evaluatePair | plate | B | True | False | if (behave == "plate") { |
| src1.6.6/terminal_checker.cpp:166 | evaluatePair | IsInsideVerified | B | True | False | if (!hypothesis && world.stage == 2 && !world.IsInsideVerified(x->id)) |
| src1.6.6/terminal_checker.cpp:172 | evaluatePair | hold | B | True | False | if (behave == "hold") { |
| src1.6.6/terminal_checker.cpp:173 | evaluatePair | IsInsideVerified | B | True | False | if (!hypothesis && world.stage == 2 && !world.IsInsideVerified(x->id)) |
| src1.6.6/terminal_checker.cpp:235 | evaluateConstraint | hold | D | True | False | // Each grounded constraint must hold; negate BEFORE combining bindings. |
| src1.6.6/tests/canonical_baseline_probe.cpp:17 | main | hold,plate | D | True | False | assert(w->ParseEnv("(hold 0) (plate 0) (at 0 1) (sort 1 human) (size 1 big) (at 1 1) " |
| src1.6.6/tests/canonical_baseline_probe.cpp:23 | main | EvidenceSource | D | True | False | w->MarkDirectLocationEvidence(2,true,EvidenceSource::SENSE);w->MarkUnresolved(StateField::LOCATION,2); |
| src1.6.6/tests/canonical_baseline_probe.cpp:24 | main | IsLocationVerified | D | True | False | assert(!w->IsLocationVerified(2)); |
| src1.6.6/tests/canonical_baseline_probe.cpp:26 | main | EvidenceSource,location | D | True | False | w->MarkDirectLocationEvidence(2,true,EvidenceSource::SENSE);c->location=1; |
| src1.6.6/tests/canonical_baseline_probe.cpp:34 | main | ResolvedState | D | True | False | w->SetHold(s);assert(w->ResolvedState(StateField::INSIDE,3).present); |
| src1.6.6/tests/canonical_baseline_probe.cpp:35 | main | ResolvedState | D | True | False | assert(w->ResolvedState(StateField::LOCATION,3).present); |
| src1.6.6/tests/canonical_baseline_probe.cpp:37 | main | inside | D | True | False | w->notnot_infoConstrains={T("inside",s,c)};w->ApplyMustInConstraintCorrection(); |
| src1.6.6/tests/canonical_baseline_probe.cpp:38 | main | inside | D | True | False | w->not_infoConstrains={T("inside",s,c)};w->ApplyMustInConstraintCorrection(); |
| src1.6.6/tests/canonical_baseline_probe.cpp:39 | main | IsInsideVerified | D | True | False | assert(!w->IsInsideVerified(3)); |
| src1.6.6/tests/canonical_baseline_probe.cpp:41 | main | inside | D | True | False | w->notnot_infoConstrains={T("inside",s,c)};w->ApplyMustInConstraintCorrection(); |
| src1.6.6/tests/canonical_baseline_probe.cpp:42 | main | EvidenceSource,location | D | True | False | c->location=5;w->MarkDirectLocationEvidence(2,true,EvidenceSource::SENSE); |
| src1.6.6/tests/canonical_baseline_probe.cpp:44 | main | ResolvedState | D | True | False | w->constraint_uncertain={true};assert(!w->ResolvedState(StateField::LOCATION,3).present); |
| src1.6.6/tests/canonical_baseline_probe.cpp:46 | main | ResolvedState | D | True | False | w->SetHold(s);w->Fini();assert(!w->ResolvedState(StateField::HOLD,0).present); |
| src1.6.6/tests/canonical_baseline_probe.cpp:48 | main | EvidenceSource | D | True | False | w->SetHold(s,EvidenceSource::INITIAL);assert(ScoreSemanticsTestAccess::Move(*w)); |
| src1.6.6/tests/canonical_baseline_probe.cpp:49 | main | ResolvedState | D | True | False | assert(!w->ResolvedState(StateField::LOCATION,3).present); |
| src1.6.6/tests/canonical_baseline_probe.cpp:51 | main | EvidenceSource | D | True | False | w->MarkDirectLocationEvidence(2,true,EvidenceSource::CONSTRAINT_HEURISTIC); |
| src1.6.6/tests/canonical_baseline_probe.cpp:52 | main | ResolvedState | D | True | False | assert(!w->ResolvedState(StateField::LOCATION,2).present); |
| src1.6.6/tests/canonical_baseline_probe.cpp:54 | main | EvidenceSource,location | D | True | False | w->MarkDirectLocationEvidence(2,true,EvidenceSource::SENSE);c->location=1; |
| src1.6.6/tests/canonical_baseline_probe.cpp:55 | main | inside | D | True | False | w->notnot_infoConstrains={T("inside",s,c)};w->ApplyMustInConstraintCorrection(); |
| src1.6.6/tests/canonical_baseline_probe.cpp:56 | main | ResolvedState | D | True | False | assert(w->ResolvedState(StateField::LOCATION,3).value==5); |
| src1.6.6/tests/canonical_baseline_probe.cpp:58 | main | EvidenceSource,location | D | True | False | w->stage=1;w->MarkDirectLocationEvidence(2,true,EvidenceSource::SENSE);c->location=1; |
| src1.6.6/tests/canonical_baseline_probe.cpp:59 | main | ResolvedState | D | True | False | w->ParseInfo(T("on",s,c));assert(w->ResolvedState(StateField::LOCATION,3).value==5); |
| src1.6.6/tests/canonical_baseline_probe.cpp:61 | main | EvidenceSource,inside | D | True | False | s->inside=NONE;w->SetInsideEvidence(3,true,EvidenceSource::SENSE); |
| src1.6.6/tests/canonical_baseline_probe.cpp:62 | main | inside | D | True | False | s->inside=2;c->smallObjectsInside.push_back(s); |
| src1.6.6/tests/canonical_baseline_probe.cpp:64 | main | ResolvedState | D | True | False | assert(!w->ResolvedState(StateField::LOCATION,3).present); |
| src1.6.6/tests/canonical_baseline_probe.cpp:66 | main | EvidenceSource,inside | D | True | False | s->inside=1;w->SetInsideEvidence(3,true,EvidenceSource::SENSE); |
| src1.6.6/tests/canonical_baseline_probe.cpp:67 | main | ResolvedState | D | True | False | assert(!w->ResolvedState(StateField::INSIDE,3).present); |
| src1.6.6/tests/canonical_state_tests.cpp:29 | World | hold,plate | D | True | False | assert(w->ParseEnv("(hold 0) (plate 0) (at 0 1) (sort 1 human) (size 1 big) (at 1 1) " |
| src1.6.6/tests/canonical_state_tests.cpp:31 | World | inside | D | True | False | "(sort 3 cup) (size 3 small) (inside 3 2) (sort 4 table) (size 4 big) (at 4 5)")); |
| src1.6.6/tests/canonical_state_tests.cpp:38 | main | EvidenceSource | D | True | False | const auto fact=[&](StateField f,unsigned id,int value,EvidenceSource source=EvidenceSource::SENSE) {w->ApplyStateValue(f,id,value,true,source);}; |
| src1.6.6/tests/canonical_state_tests.cpp:41 | main | objectLocationVerified | D | True | False | w->objectLocationVerified[2]=true; // deliberate stale compatibility |
| src1.6.6/tests/canonical_state_tests.cpp:42 | main | FactLocation,IsLocationVerified,location | D | True | False | assert(c->location==1 && w->FactLocation(2)==UNKNOWN && !w->IsLocationVerified(2)); |
| src1.6.6/tests/canonical_state_tests.cpp:44 | main | location | D | True | False | fact(StateField::LOCATION,2,1);w->objects[4]->location=UNKNOWN; |
| src1.6.6/tests/canonical_state_tests.cpp:46 | main | FactLocation | D | True | False | assert(w->FactLocation(4)==1);w->constraint_eligible={test!=2};w->constraint_uncertain={test!=2}; |
| src1.6.6/tests/canonical_state_tests.cpp:48 | main | FactLocation,location | D | True | False | assert(w->objects[4]->location==1 && w->FactLocation(4)==UNKNOWN); |
| src1.6.6/tests/canonical_state_tests.cpp:55 | main | location | D | True | False | w->tasks={Task("goto",c)};assert(c->location==w->location); |
| src1.6.6/tests/canonical_state_tests.cpp:59 | main | location | D | True | False | if(test==12) { fact(StateField::LOCATION,2,5);c->location=1; |
| src1.6.6/tests/canonical_state_tests.cpp:63 | main | inside,isOpen,location | D | True | False | assert(c->location==5 && s->inside==NONE && c->isOpen==1); |
| src1.6.6/tests/canonical_state_tests.cpp:64 | main | FactContainerState,FactInside,FactLocation | D | True | False | assert(w->FactLocation(2)==5 && w->FactInside(3)==NONE && w->FactContainerState(2)==1); |
| src1.6.6/tests/canonical_state_tests.cpp:67 | main | location | D | True | False | fact(StateField::LOCATION,2,5);c->location=1; |
| src1.6.6/tests/canonical_state_tests.cpp:68 | main | FactLocation,objectLocationVerified | D | True | False | assert(w->FactLocation(2)==5);w->objectLocationVerified[2]=false; |
| src1.6.6/tests/canonical_state_tests.cpp:69 | main | FactLocation | D | True | False | assert(w->FactLocation(2)==5);assert(!w->DebugStateConsistency().empty()); |
| src1.6.6/tests/canonical_state_tests.cpp:71 | main | FactInside,FactLocation,FactValue | D | True | False | w->SetHold(s);assert(w->FactValue(StateField::HOLD)==3 && w->FactInside(3)==NONE && w->FactLocation(3)==1); |
| src1.6.6/tests/canonical_state_tests.cpp:72 | main | FactValue | D | True | False | w->SetPlate(s);assert(w->FactValue(StateField::PLATE)==3 && w->FactValue(StateField::HOLD)==NONE); |
| src1.6.6/tests/canonical_state_tests.cpp:73 | main | hold,plate | D | True | False | assert(w->plate==s && !w->hold && w->DebugStateConsistency().empty()); |
| src1.6.6/tests/canonical_state_tests.cpp:75 | main | containerStateVerified,isOpen | D | True | False | c->isOpen=1;w->containerStateVerified[2]=true; |
| src1.6.6/tests/canonical_state_tests.cpp:77 | main | FactContainerState | D | True | False | assert(w->FactContainerState(2)==UNKNOWN); |
| src1.6.6/tests/canonical_state_tests.cpp:80 | main | EvidenceSource | D | True | False | w->ApplyStateValue(StateField::LOCATION,2,5,false,EvidenceSource::ASK_ANSWER); |
| src1.6.6/tests/canonical_state_tests.cpp:81 | main | location | D | True | False | assert(c->location==5 && w->HasContradictoryEvidence(StateField::LOCATION,2)); |
| src1.6.6/tests/canonical_state_tests.cpp:82 | main | FactLocation | D | True | False | assert(w->FactLocation(2)==UNKNOWN); |
| src1.6.6/tests/canonical_state_tests.cpp:83 | main | FactLocation | D | True | False | fact(StateField::LOCATION,2,5);assert(w->FactLocation(2)==5); // new observation resolves current truth |
| src1.6.6/tests/canonical_state_tests.cpp:94 | main | location | D | True | False | fact(StateField::LOCATION,2,1);w->objects[4]->location=UNKNOWN; |
| src1.6.6/tests/canonical_state_tests.cpp:102 | main | EvidenceSource | D | True | False | w->SetPlate(s,EvidenceSource::INITIAL);w->tasks={Task("pickup",s)}; |
| src1.6.6/tests/canonical_state_tests.cpp:106 | main | location | D | True | False | fact(StateField::LOCATION,2,1);c->location=5; |
| src1.6.6/tests/canonical_state_tests.cpp:108 | main | EvidenceSource | D | True | False | w->ApplyStateValue(StateField::LOCATION,2,1,true,EvidenceSource::SENSE); |
| src1.6.6/tests/canonical_state_tests.cpp:111 | main | inside,location | D | True | False | s->location=1;s->inside=NONE;w->tasks={Task("give",s)};w->SetActionResults({false,false,false,false}); |
| src1.6.6/tests/canonical_state_tests.cpp:114 | main | inside | D | True | False | s->inside=NONE;w->tasks={Task("putin",s,c)}; |
| src1.6.6/tests/canonical_state_tests.cpp:117 | main | inside | D | True | False | w->notnot_infoConstrains={Task("inside",s,c)};w->ApplyMustInConstraintCorrection(); |
| src1.6.6/tests/canonical_state_tests.cpp:119 | main | FactLocation,Provenance | D | True | False | assert(w->FactLocation(3)==1 && w->Provenance(StateField::LOCATION,3).dependency_count==2); |
| src1.6.6/tests/canonical_state_tests.cpp:120 | main | FactLocation | D | True | False | w->constraint_uncertain={true};assert(w->FactLocation(3)==UNKNOWN); |
| src1.6.6/tests/canonical_state_tests.cpp:122 | main | inside | D | True | False | w->notnot_infoConstrains={Task("inside",s,c)};w->ApplyMustInConstraintCorrection(); |
| src1.6.6/tests/canonical_state_tests.cpp:123 | main | inside | D | True | False | w->not_infoConstrains={Task("inside",s,c)};w->ApplyMustInConstraintCorrection(); |
| src1.6.6/tests/canonical_state_tests.cpp:124 | main | FactInside,IsInsideVerified,inside | D | True | False | assert(s->inside==UNKNOWN && w->FactInside(3)==UNKNOWN && !w->IsInsideVerified(3)); |
| src1.6.6/tests/canonical_state_tests.cpp:126 | main | ResolvedState | D | True | False | w->SetHold(s);w->Fini();assert(!w->ResolvedState(StateField::HOLD,0).present); |
| src1.6.6/tests/canonical_state_tests.cpp:127 | main | ResolvedState | D | True | False | assert(!w->ResolvedState(StateField::PLATE,0).present); |
| src1.6.6/tests/canonical_state_tests.cpp:130 | main | ResolvedState | D | True | False | assert(!w->ResolvedState(StateField::LOCATION,2).present); // weak support revision matches, but is not fact |
| src1.6.6/tests/canonical_state_tests.cpp:132 | main | EvidenceSource | D | True | False | w->ApplyStateValue(StateField::LOCATION,2,1,true,EvidenceSource::CONSTRAINT_HEURISTIC); |
| src1.6.6/tests/canonical_state_tests.cpp:133 | main | ResolvedState | D | True | False | assert(!w->ResolvedState(StateField::LOCATION,2).present); |
| src1.6.6/tests/canonical_state_tests.cpp:136 | main | FactLocation | D | True | False | for(int i=0;i<1000;++i)assert(w->FactLocation(2)==1); |
| src1.6.6/tests/canonical_state_tests.cpp:139 | main | EvidenceSource | D | True | False | fact(StateField::INSIDE,3,2,EvidenceSource::CONSTRAINT_DERIVED); |
| src1.6.6/tests/canonical_state_tests.cpp:140 | main | FactInside | D | True | False | w->SetConstraintSupport(StateField::INSIDE,3,0);assert(w->FactInside(3)==UNKNOWN); // removed support |
| src1.6.6/tests/canonical_state_tests.cpp:142 | main | EvidenceSource | D | True | False | w->SetHold(s,EvidenceSource::INITIAL); |
| src1.6.6/tests/canonical_state_tests.cpp:144 | main | FactLocation,location | D | True | False | assert(s->location==5 && w->FactLocation(3)==UNKNOWN); |
| src1.6.6/tests/canonical_state_tests.cpp:145 | main | FactValue | D | True | False | assert(w->FactValue(StateField::HOLD)==UNKNOWN); |
| src1.6.6/tests/canonical_state_tests.cpp:147 | main | FactContainerState | D | True | False | fact(StateField::CONTAINER_STATE,2,2);assert(w->FactContainerState(2)==UNKNOWN); |
| src1.6.6/tests/canonical_state_tests.cpp:148 | main | holdProvenance,plate,plateProvenance,plate_id | D | True | False | w->SetHold(s);w->plateProvenance=w->holdProvenance;w->plate_id=3;w->plate=s; |
| src1.6.6/tests/canonical_state_tests.cpp:149 | main | FactValue | D | True | False | assert(w->FactValue(StateField::HOLD)==UNKNOWN && w->FactValue(StateField::PLATE)==UNKNOWN); |
| src1.6.6/tests/canonical_state_tests.cpp:154 | main | FactLocation | D | True | False | assert(w->FactLocation(3)==UNKNOWN); // matching revision of an invalid state is no support |
| src1.6.6/tests/canonical_state_tests.cpp:161 | main | location | D | True | False | fact(StateField::LOCATION,2,5);c->location=1; |
| src1.6.6/tests/canonical_state_tests.cpp:162 | main | inside | D | True | False | w->notnot_infoConstrains={Task("inside",s,c)};w->ApplyMustInConstraintCorrection(); |
| src1.6.6/tests/canonical_state_tests.cpp:163 | main | FactLocation,location | D | True | False | assert(w->FactLocation(3)==5 && s->location==5); |
| src1.6.6/tests/canonical_state_tests.cpp:164 | main | FactInside | D | True | False | assert(w->FactInside(3)==2); |
| src1.6.6/tests/canonical_state_tests.cpp:166 | main | location | D | True | False | w->stage=1;fact(StateField::LOCATION,2,5);c->location=1; |
| src1.6.6/tests/canonical_state_tests.cpp:167 | main | FactLocation | D | True | False | w->ParseInfo(Task("on",s,c));assert(w->FactLocation(3)==5); |
| src1.6.6/tests/canonical_state_tests.cpp:168 | main | FactLocation | D | True | False | w->ParseInfo(Task("near",s,c));assert(w->FactLocation(3)==5); |
| src1.6.6/tests/canonical_state_tests.cpp:169 | main | FactLocation,inside | D | True | False | w->ParseInfo(Task("inside",s,c));assert(w->FactLocation(3)==5); |
| src1.6.6/tests/canonical_state_tests.cpp:171 | main | inside | D | True | False | fact(StateField::INSIDE,3,NONE);s->inside=2;c->smallObjectsInside.push_back(s); |
| src1.6.6/tests/canonical_state_tests.cpp:174 | main | FactLocation,inside | D | True | False | assert(w->FactLocation(3)==UNKNOWN); // cache membership cannot prove inside |
| src1.6.6/tests/canonical_state_tests.cpp:177 | main | FactInside | D | True | False | assert(w->FactInside(3)==UNKNOWN && !w->DebugStateConsistency().empty()); |
| src1.6.6/tests/guarded_decision_tests.cpp:19 | Run | hold,plate | D | True | False | "(hold 0) (plate 0) (at 0 1) " |
| src1.6.6/tests/guarded_decision_tests.cpp:39 | declaration/inline | hold,plate | D | True | False | "(hold 0) (plate 0) (at 0 1) " |
| src1.6.6/tests/input_safety_tests.cpp:54 | main | inside | D | True | False | assert(world->ParseEnv("(inside 2 99) (at 0 1)")); |
| src1.6.6/tests/input_safety_tests.cpp:55 | main | inside | D | True | False | assert(std::dynamic_pointer_cast<SmallObject>(world->objects[2])->inside == UNKNOWN); |
| src1.6.6/tests/input_safety_tests.cpp:56 | main | hold | D | True | False | assert(world->ParseEnv("(hold 3) (at 0 1)")); |
| src1.6.6/tests/input_safety_tests.cpp:57 | main | hold,hold_id | D | True | False | assert(world->hold_id == NONE && !world->hold); |
| src1.6.6/tests/input_safety_tests.cpp:62 | main | hold | D | True | False | "(:domain (hold 0) (sort 5 bowl) (size 5 small) (at 5 5))")); |
| src1.6.6/tests/input_safety_tests.cpp:64 | main | location | D | True | False | assert(world->objects[5]->sort == "bowl" && world->objects[5]->location == 5); |
| src1.6.6/tests/input_safety_tests.cpp:66 | main | location | D | True | False | // The largest supported sparse id is bounded and all object/location |
| src1.6.6/tests/interval_gate_tests.cpp:27 | main | hold,plate | D | True | False | assert(w->ParseEnv("(hold 0) (plate 0) (at 0 1) (sort 1 cupboard) " |
| src1.6.6/tests/interval_gate_tests.cpp:95 | main | EvidenceSource | D | True | False | w->ApplyStateValue(StateField::CONTAINER_STATE,1,1,true,EvidenceSource::SENSE); |
| src1.6.6/tests/legal_preservation_tests.cpp:14 | main | Facts | D | True | False | // Facts can be reordered; late size/type must not erase closed state. |
| src1.6.6/tests/legal_preservation_tests.cpp:19 | main | isOpen | D | True | False | assert(std::dynamic_pointer_cast<Container>(w->objects[3])->isOpen == 0); |
| src1.6.6/tests/parse_snapshot.cpp:9 | snapshot | hold_id,location,plate_id | D | True | False | std::cout << "SNAP " << phase << " robot=" << w.location << ',' << w.hold_id << ',' << w.plate_id << '\n'; |
| src1.6.6/tests/parse_snapshot.cpp:11 | snapshot | location | D | True | False | std::cout<<"SNAP object "<<o->id<<' '<<o->sort<<' '<<o->location; |
| src1.6.6/tests/parse_snapshot.cpp:15 | snapshot | inside | D | True | False | if(s) std::cout<<" small "<<s->color<<' '<<s->inside<<' '<<s->on; |
| src1.6.6/tests/parse_snapshot.cpp:16 | snapshot | isOpen | D | True | False | else if(c) std::cout<<" container "<<c->isOpen; |
| src1.6.6/tests/question_preflight_tests.cpp:12 | declaration/inline | hold,plate | D | True | False | "(hold 0) (plate 0) (at 0 1) " |
| src1.6.6/tests/question_preflight_tests.cpp:91 | GotoAndConflicts | location | D | True | False | // Different IDs at the SAME location must not be merged. |
| src1.6.6/tests/question_preflight_tests.cpp:115 | CanonicalRelationsAndSets | inside | D | True | False | Not(Info("inside X Y", "(id X 2) (id Y 3)")) + |
| src1.6.6/tests/question_preflight_tests.cpp:146 | MalformedConstraintRecovery | inside | D | True | False | "(:cons_not (:info (inside X) (:cond (id X 2))))"}) { |
| src1.6.6/tests/question_preflight_tests.cpp:166 | WorldSafetyAndStage2Unknowns | location | D | True | False | w->objects[2]->location = UNKNOWN; |
| src1.6.6/tests/question_preflight_tests.cpp:167 | WorldSafetyAndStage2Unknowns | location | D | True | False | w->objects[3]->location = UNKNOWN; |
| src1.6.6/tests/question_preflight_tests.cpp:168 | WorldSafetyAndStage2Unknowns | isOpen | D | True | False | std::dynamic_pointer_cast<Container>(w->objects[3])->isOpen = UNKNOWN; |
| src1.6.6/tests/question_preflight_tests.cpp:170 | WorldSafetyAndStage2Unknowns | location | D | True | False | w->objects[3]->location = 1; // Stage 2 err may collide with human |
| src1.6.6/tests/recovery_evidence_tests.cpp:30 | declaration/inline | hold,plate | D | True | False | "(hold 0) (plate 0) (at 0 2) " |
| src1.6.6/tests/recovery_evidence_tests.cpp:40 | main | inside | D | True | False | // A: a guaranteed initial must-inside repairs inside, but the cupboard's |
| src1.6.6/tests/recovery_evidence_tests.cpp:41 | main | location | D | True | False | // unverified initial location does not become a Sense-quality book location. |
| src1.6.6/tests/recovery_evidence_tests.cpp:42 | main | inside | D | True | False | auto inside = World(argv[1], 2, kitchen); |
| src1.6.6/tests/recovery_evidence_tests.cpp:43 | main | inside | D | True | False | Instruction must_in = Unary("inside", inside->objects[3]); |
| src1.6.6/tests/recovery_evidence_tests.cpp:44 | main | inside | D | True | False | must_in.Y.push_back(inside->objects[2]); |
| src1.6.6/tests/recovery_evidence_tests.cpp:45 | main | inside | D | True | False | inside->notnot_infoConstrains.push_back(must_in); |
| src1.6.6/tests/recovery_evidence_tests.cpp:46 | main | inside | D | True | False | inside->ApplyMustInConstraintCorrection(); |
| src1.6.6/tests/recovery_evidence_tests.cpp:47 | main | IsInsideVerified,inside | D | True | False | assert(inside->IsInsideVerified(3)); |
| src1.6.6/tests/recovery_evidence_tests.cpp:48 | main | EvidenceSource,InsideSource,inside | D | True | False | assert(inside->InsideSource(3) == EvidenceSource::CONSTRAINT_DERIVED); |
| src1.6.6/tests/recovery_evidence_tests.cpp:49 | main | IsLocationVerified,inside | D | True | False | assert(!inside->IsLocationVerified(3)); |
| src1.6.6/tests/recovery_evidence_tests.cpp:50 | main | EvidenceSource,LocationSource,inside | D | True | False | assert(inside->LocationSource(3) == EvidenceSource::CONSTRAINT_HEURISTIC); |
| src1.6.6/tests/recovery_evidence_tests.cpp:51 | main | inside | D | True | False | Instruction putin = Unary("putin", inside->objects[3]); |
| src1.6.6/tests/recovery_evidence_tests.cpp:52 | main | inside | D | True | False | putin.Y.push_back(inside->objects[2]); |
| src1.6.6/tests/recovery_evidence_tests.cpp:53 | main | inside | D | True | False | assert(inside->ZeroActionPreCheck(putin)); |
| src1.6.6/tests/recovery_evidence_tests.cpp:58 | main | ContainerSource,EvidenceSource | D | True | False | assert(closed->ContainerSource(2) == EvidenceSource::INITIAL); |
| src1.6.6/tests/recovery_evidence_tests.cpp:59 | main | IsContainerStateVerified | D | True | False | assert(!closed->IsContainerStateVerified(2)); |
| src1.6.6/tests/recovery_evidence_tests.cpp:62 | main | IsContainerStateVerified | D | True | False | assert(closed->IsContainerStateVerified(2)); |
| src1.6.6/tests/recovery_evidence_tests.cpp:63 | main | ContainerSource,EvidenceSource | D | True | False | assert(closed->ContainerSource(2) == EvidenceSource::CONSTRAINT_DERIVED); |
| src1.6.6/tests/recovery_evidence_tests.cpp:71 | main | ContainerSource,EvidenceSource | D | True | False | assert(explicit_info->ContainerSource(2) == EvidenceSource::EXPLICIT_INFO); |
| src1.6.6/tests/recovery_evidence_tests.cpp:73 | main | IsContainerStateVerified | D | True | False | assert(!explicit_info->IsContainerStateVerified(2)); |
| src1.6.6/tests/recovery_evidence_tests.cpp:78 | main | location | D | True | False | // must-near inference, even if the robot stands at one reported location. |
| src1.6.6/tests/recovery_evidence_tests.cpp:80 | main | hold,plate | D | True | False | "(hold 0) (plate 0) (at 0 4) " |
| src1.6.6/tests/recovery_evidence_tests.cpp:88 | main | IsLocationVerified | D | True | False | assert(!conflict->IsLocationVerified(3)); |
| src1.6.6/tests/recovery_evidence_tests.cpp:92 | main | hold,plate | D | True | False | "(hold 0) (plate 0) (at 0 2) " |
| src1.6.6/tests/recovery_evidence_tests.cpp:100 | main | location | D | True | False | assert(weak->objects[3]->location == 2); |
| src1.6.6/tests/recovery_evidence_tests.cpp:101 | main | EvidenceSource,LocationSource | D | True | False | assert(weak->LocationSource(3) == EvidenceSource::CONSTRAINT_HEURISTIC); |
| src1.6.6/tests/recovery_evidence_tests.cpp:102 | main | IsLocationVerified | D | True | False | assert(!weak->IsLocationVerified(3)); |
| src1.6.6/tests/recovery_evidence_tests.cpp:108 | main | hold,plate | D | True | False | "(hold 0) (plate 0) (at 0 2) " |
| src1.6.6/tests/recovery_evidence_tests.cpp:114 | main | EvidenceSource | D | True | False | changed->ApplyStateValue(StateField::LOCATION,2,4,true,EvidenceSource::SENSE); |
| src1.6.6/tests/recovery_evidence_tests.cpp:126 | main | location | D | True | False | assert(changed->location == 2 && changed->objects[2]->location == 4); |
| src1.6.6/tests/recovery_evidence_tests.cpp:145 | main | hold,plate | D | True | False | "(hold 0) (plate 0) (at 0 2) " |
| src1.6.6/tests/recovery_evidence_tests.cpp:149 | main | hold,plate | D | True | False | "(hold 0) (plate 0) (at 0 2) (sort 1 human) (size 1 big) (at 1 1) " |
| src1.6.6/tests/score_semantics_tests.cpp:28 | declaration/inline | hold,plate | D | True | False | "(hold 0) (plate 0) (at 0 1) " |
| src1.6.6/tests/score_semantics_tests.cpp:31 | declaration/inline | inside | D | True | False | "(sort 3 cup) (size 3 small) (color 3 red) (inside 3 2) (at 3 1) " |
| src1.6.6/tests/score_semantics_tests.cpp:124 | main | hold | D | True | False | carried.replace(carried.find("(hold 0)"), 8, "(hold 3)"); |
| src1.6.6/tests/score_semantics_tests.cpp:125 | main | inside | D | True | False | carried.replace(carried.find("(inside 3 2)"), 12, ""); |
| src1.6.6/tests/score_semantics_tests.cpp:147 | main | EvidenceSource | D | True | False | w->ApplyStateValue(StateField::CONTAINER_STATE,2,1,true,EvidenceSource::SENSE); |
| src1.6.6/tests/score_semantics_tests.cpp:156 | main | EvidenceSource | D | True | False | w->ApplyStateValue(StateField::CONTAINER_STATE,2,0,true,EvidenceSource::CONSTRAINT_DERIVED); |
| src1.6.6/tests/state_invariant_tests.cpp:42 | main | hold,plate | D | True | False | assert(w->ParseEnv("(hold 0) (plate 0) (at 0 1) " |
| src1.6.6/tests/state_invariant_tests.cpp:45 | main | inside | D | True | False | "(sort 3 cup) (size 3 small) (color 3 red) (inside 3 2) " |
| src1.6.6/tests/state_invariant_tests.cpp:51 | main | location | D | True | False | assert(a.id==7 && a.location==11 && b.id==8 && b.location==12); |
| src1.6.6/tests/state_invariant_tests.cpp:52 | main | location | D | True | False | assert(d.id==9 && d.location==13); |
| src1.6.6/tests/state_invariant_tests.cpp:55 | main | IsLocationVerified,location | D | True | False | assert(c->location==w->location && w->IsLocationVerified(2)); |
| src1.6.6/tests/state_invariant_tests.cpp:56 | main | IsLocationVerified,location | D | True | False | assert(s->location==c->location && !w->IsLocationVerified(3)); |
| src1.6.6/tests/state_invariant_tests.cpp:59 | main | inside | D | True | False | assert(s->inside==NONE && c->smallObjectsInside.empty()); |
| src1.6.6/tests/state_invariant_tests.cpp:60 | main | hold,hold_id | D | True | False | assert(w->hold==s && w->hold_id==3); |
| src1.6.6/tests/state_invariant_tests.cpp:62 | main | hold,plate | D | True | False | assert(!w->hold && w->plate==s); |
| src1.6.6/tests/state_invariant_tests.cpp:64 | main | location | D | True | False | assert(s->location==5); |
| src1.6.6/tests/state_invariant_tests.cpp:66 | main | hold,plate | D | True | False | assert(!w->plate && w->hold==s); |
| src1.6.6/tests/state_invariant_tests.cpp:68 | main | hold,inside | D | True | False | assert(!w->hold && s->inside==NONE); |
| src1.6.6/tests/state_invariant_tests.cpp:70 | main | inside | D | True | False | w->ParseInfo(Task("inside",s,w->objects[4])); |
| src1.6.6/tests/state_invariant_tests.cpp:71 | main | inside | D | True | False | w->ParseInfo(Task("inside",s,w->objects[4])); |
| src1.6.6/tests/state_invariant_tests.cpp:79 | main | isOpen,location | D | True | False | c->isOpen=UNKNOWN; c->location=w->location; w->SetHold(s); |
| src1.6.6/tests/state_invariant_tests.cpp:86 | main | inside,isOpen,location | D | True | False | int loc=w->location, sloc=s->location, in=s->inside, op=c->isOpen; |
| src1.6.6/tests/state_invariant_tests.cpp:89 | main | inside,location | D | True | False | assert(w->location==loc && s->location==sloc && s->inside==in); |
| src1.6.6/tests/state_invariant_tests.cpp:90 | main | isOpen | D | True | False | assert(c->isOpen==op && c->smallObjectsInside==contents); |
| src1.6.6/tests/state_invariant_tests.cpp:93 | main | location | D | True | False | w->stage=1; c->location=w->location; s->location=w->location; |
| src1.6.6/tests/state_invariant_tests.cpp:94 | main | isOpen | D | True | False | c->isOpen=1; w->tasks.push_back(Task("takeout",s,c)); |
| src1.6.6/tests/state_invariant_tests.cpp:97 | main | hold_id,inside | D | True | False | assert(p.dry_run_succeeded && w->hold_id==NONE && s->inside==2); |
| src1.6.6/tests/state_invariant_tests.cpp:104 | main | location | D | True | False | c->location=1; s->location=1; w->SetSenseResult({2}); |
| src1.6.6/tests/state_invariant_tests.cpp:107 | main | IsLocationVerified | D | True | False | assert(!w->IsLocationVerified(3)); |
| src1.6.6/tests/state_invariant_tests.cpp:111 | main | location | D | True | False | w->objects[4]->location=UNKNOWN; |
| src1.6.6/tests/state_invariant_tests.cpp:113 | main | location | D | True | False | assert(w->objects[4]->location==4); |
| src1.6.6/tests/state_invariant_tests.cpp:114 | main | location,objectLocationVerified | D | True | False | c->location=1; w->objectLocationVerified[2]=true; |
| src1.6.6/tests/state_invariant_tests.cpp:115 | main | objectLocationInferredByMustNear | D | True | False | w->objectLocationInferredByMustNear[2]=false; |
| src1.6.6/tests/state_invariant_tests.cpp:116 | main | EvidenceSource,objectLocationSource | D | True | False | w->objectLocationSource[2]=EvidenceSource::SENSE; |
| src1.6.6/tests/state_invariant_tests.cpp:118 | main | location | D | True | False | assert(w->objects[4]->location==UNKNOWN); |
| src1.6.6/tests/state_invariant_tests.cpp:119 | main | IsLocationVerified | D | True | False | assert(!w->IsLocationVerified(4)); |
| src1.6.6/tests/state_invariant_tests.cpp:121 | main | inside,location | D | True | False | s->inside=UNKNOWN; s->location=UNKNOWN; |
| src1.6.6/tests/state_invariant_tests.cpp:122 | main | inside | D | True | False | w->SetAskResult("inside(3,4)"); |
| src1.6.6/tests/state_invariant_tests.cpp:125 | main | IsInsideVerified,IsLocationVerified | D | True | False | assert(!w->IsInsideVerified(3) && !w->IsLocationVerified(3)); |
| src1.6.6/tests/state_invariant_tests.cpp:128 | main | isOpen,location | D | True | False | c->location=1; s->location=1; c->isOpen=UNKNOWN; |
| src1.6.6/tests/state_invariant_tests.cpp:130 | main | IsInsideVerified,inside | D | True | False | assert(s->inside==2 && !w->IsInsideVerified(3)); |
| src1.6.6/tests/state_invariant_tests.cpp:136 | main | hold,inside | D | True | False | assert(w->hold==s && s->inside==NONE && c->smallObjectsInside.empty()); |
| src1.6.6/tests/state_invariant_tests.cpp:138 | main | hold,inside | D | True | False | assert(!w->hold && s->inside==2 && c->smallObjectsInside.size()==1); |
| src1.6.6/tests/state_invariant_tests.cpp:139 | main | isOpen,location | D | True | False | assert(c->location==s->location && c->isOpen==1); |
| src1.6.6/tests/state_invariant_tests.cpp:149 | main | inside | D | True | False | auto goal=Task("inside",s,c); w->notnot_infoConstrains.push_back(goal); |
| src1.6.6/tests/state_invariant_tests.cpp:161 | main | EvidenceSource | D | True | False | w->SetHold(s,EvidenceSource::INITIAL); w->SetInsideEvidence(3,true,EvidenceSource::SENSE); |
| src1.6.6/tests/state_invariant_tests.cpp:164 | main | IsLocationVerified,location | D | True | False | assert(w->location==1 && !w->IsLocationVerified(3)); |
| src1.6.6/tests/state_invariant_tests.cpp:169 | main | EvidenceSource | D | True | False | w->SetInsideEvidence(3,true,EvidenceSource::SENSE); |
| src1.6.6/tests/state_invariant_tests.cpp:171 | main | inside | D | True | False | assert(s->inside==2 && c->smallObjectsInside.size()==1); |
| src1.6.6/tests/state_invariant_tests.cpp:173 | main | IsInsideVerified,inside | D | True | False | assert(s->inside==2 && w->IsInsideVerified(3)); |
| src1.6.6/tests/state_invariant_tests.cpp:174 | main | EvidenceSource | D | True | False | w->ApplyStateValue(StateField::INSIDE,3,UNKNOWN,false,EvidenceSource::UNKNOWN); |
| src1.6.6/tests/state_invariant_tests.cpp:176 | main | IsInsideVerified,inside | D | True | False | assert(s->inside==UNKNOWN && !w->IsInsideVerified(3)); |
| src1.6.6/tests/state_invariant_tests.cpp:184 | main | hold_id,plate,plate_id | D | True | False | assert(w->hold_id==3 && w->plate_id==NONE && !w->plate); |
| src1.6.6/tests/state_invariant_tests.cpp:187 | main | location | D | True | False | w->objects[4]->location=UNKNOWN; |
| src1.6.6/tests/state_invariant_tests.cpp:189 | main | EvidenceSource,LocationSource | D | True | False | assert(w->LocationSource(2)==EvidenceSource::INITIAL); |
| src1.6.6/tests/state_invariant_tests.cpp:190 | main | EvidenceSource,LocationSource | D | True | False | assert(w->LocationSource(4)==EvidenceSource::CONSTRAINT_HEURISTIC); |
| src1.6.6/tests/state_invariant_tests.cpp:192 | main | location | D | True | False | assert(w->objects[2]->location==4 && w->objects[4]->location==4); |
| src1.6.6/tests/state_invariant_tests.cpp:193 | main | IsLocationVerified | D | True | False | assert(!w->IsLocationVerified(4)); |
| src1.6.6/tests/state_invariant_tests.cpp:194 | main | location,objectLocationVerified | D | True | False | c->location=UNKNOWN; w->objectLocationVerified[2]=false; |
| src1.6.6/tests/state_invariant_tests.cpp:196 | main | location | D | True | False | assert(w->objects[4]->location==UNKNOWN); |
| src1.6.6/tests/state_invariant_tests.cpp:198 | main | inside | D | True | False | w->notnot_infoConstrains.push_back(Task("inside",s,c)); |
| src1.6.6/tests/state_invariant_tests.cpp:200 | main | EvidenceSource,InsideSource | D | True | False | assert(w->InsideSource(3)==EvidenceSource::CONSTRAINT_DERIVED); |
| src1.6.6/tests/state_invariant_tests.cpp:203 | main | location | D | True | False | assert(s->location==1); |
| src1.6.6/tests/state_invariant_tests.cpp:204 | main | EvidenceSource,LocationSource | D | True | False | assert(w->LocationSource(3)==EvidenceSource::CONSTRAINT_DERIVED); |
| src1.6.6/tests/state_invariant_tests.cpp:209 | main | isOpen,location | D | True | False | c->location=1; s->location=1; c->isOpen=UNKNOWN; |
| src1.6.6/tests/state_invariant_tests.cpp:211 | main | inside,location | D | True | False | assert(s->inside==2 && s->location==1); |
| src1.6.6/tests/state_invariant_tests.cpp:212 | main | IsLocationVerified | D | True | False | assert(!w->IsLocationVerified(3)); |
| src1.6.6/tests/state_invariant_tests.cpp:214 | main | isOpen | D | True | False | c->isOpen=UNKNOWN; |
| src1.6.6/tests/state_invariant_tests.cpp:217 | main | IsContainerStateVerified,isOpen | D | True | False | assert(c->isOpen==1 && w->IsContainerStateVerified(2)); |
| src1.6.6/tests/state_layer_tests.cpp:24 | main | hold,plate | D | True | False | assert(w->ParseEnv("(hold 0) (plate 0) (at 0 1) " |
| src1.6.6/tests/state_layer_tests.cpp:27 | main | inside | D | True | False | "(sort 3 cup) (size 3 small) (inside 3 2)")); |
| src1.6.6/tests/state_layer_tests.cpp:31 | main | Provenance | D | True | False | const auto& p=w->Provenance(StateField::LOCATION,2); |
| src1.6.6/tests/state_layer_tests.cpp:33 | main | EvidenceSource | D | True | False | assert(p.received.source==EvidenceSource::INITIAL); |
| src1.6.6/tests/state_layer_tests.cpp:34 | main | IsLocationVerified | D | True | False | assert(p.resolved_value==4 && !w->IsLocationVerified(2)); |
| src1.6.6/tests/state_layer_tests.cpp:38 | main | IsLocationVerified,location | D | True | False | assert(c->location==5 && !w->IsLocationVerified(2)); |
| src1.6.6/tests/state_layer_tests.cpp:39 | main | Provenance | D | True | False | assert(w->Provenance(StateField::LOCATION,2).resolved_value==UNKNOWN); |
| src1.6.6/tests/state_layer_tests.cpp:40 | main | EvidenceSource,Provenance | D | True | False | assert(w->Provenance(StateField::LOCATION,2).received.source==EvidenceSource::ASK_ANSWER); |
| src1.6.6/tests/state_layer_tests.cpp:43 | main | Provenance | D | True | False | const auto& p=w->Provenance(StateField::CONTAINER_STATE,2); |
| src1.6.6/tests/state_layer_tests.cpp:44 | main | isOpen | D | True | False | assert(c->isOpen==1 && p.resolved_value==1); |
| src1.6.6/tests/state_layer_tests.cpp:45 | main | EvidenceSource,IsContainerStateVerified | D | True | False | assert(p.received.source==EvidenceSource::ACTION_SUCCESS && w->IsContainerStateVerified(2)); |
| src1.6.6/tests/state_layer_tests.cpp:48 | main | IsContainerStateVerified,isOpen | D | True | False | assert(c->isOpen==0 && !w->IsContainerStateVerified(2)); |
| src1.6.6/tests/state_layer_tests.cpp:49 | main | EvidenceSource,Provenance | D | True | False | assert(w->Provenance(StateField::CONTAINER_STATE,2).received.source==EvidenceSource::INITIAL); |
| src1.6.6/tests/state_layer_tests.cpp:52 | main | location | D | True | False | assert(c->location==UNKNOWN && w->HasContradictoryEvidence(StateField::LOCATION,2)); |
| src1.6.6/tests/state_layer_tests.cpp:53 | main | IsLocationVerified | D | True | False | assert(!w->IsLocationVerified(2)); |
| src1.6.6/tests/state_layer_tests.cpp:57 | main | location | D | True | False | w->objects[1]->location=UNKNOWN; |
| src1.6.6/tests/state_layer_tests.cpp:58 | main | EvidenceSource,location | D | True | False | c->location=1; w->MarkDirectLocationEvidence(2,true,EvidenceSource::SENSE); |
| src1.6.6/tests/state_layer_tests.cpp:60 | main | location | D | True | False | assert(w->objects[1]->location==1); |
| src1.6.6/tests/state_layer_tests.cpp:61 | main | Provenance | D | True | False | assert(w->Provenance(StateField::LOCATION,1).dependency_count>0); |
| src1.6.6/tests/state_layer_tests.cpp:66 | main | EvidenceSource,location | D | True | False | c->location=5; w->MarkDirectLocationEvidence(2,true,EvidenceSource::SENSE); |
| src1.6.6/tests/state_layer_tests.cpp:67 | main | DependenciesCurrent | D | True | False | assert(!w->DependenciesCurrent(StateField::LOCATION,1)); |
| src1.6.6/tests/state_layer_tests.cpp:68 | main | IsLocationVerified | D | True | False | assert(!w->IsLocationVerified(1)); |
| src1.6.6/tests/state_layer_tests.cpp:73 | main | EvidenceSource,location | D | True | False | c->location=1; w->MarkDirectLocationEvidence(2,true,EvidenceSource::SENSE); |
| src1.6.6/tests/state_layer_tests.cpp:74 | main | location | D | True | False | w->objects[1]->location=UNKNOWN; |
| src1.6.6/tests/state_layer_tests.cpp:80 | main | Provenance | D | True | False | const auto derived_before=w->Provenance(StateField::LOCATION,1); |
| src1.6.6/tests/state_layer_tests.cpp:83 | main | Provenance | D | True | False | auto before=w->Provenance(StateField::LOCATION,2); |
| src1.6.6/tests/state_layer_tests.cpp:86 | main | Provenance | D | True | False | const auto& after=w->Provenance(StateField::LOCATION,2); |
| src1.6.6/tests/state_layer_tests.cpp:89 | main | Provenance | D | True | False | const auto& derived_after=w->Provenance(StateField::LOCATION,1); |
| src1.6.6/tests/state_layer_tests.cpp:100 | main | ResolvedState | D | True | False | assert(w->ResolvedState(StateField::LOCATION,1).present); |
| src1.6.6/tests/state_layer_tests.cpp:102 | main | location | D | True | False | w->stage=1; c->location=1; |
| src1.6.6/tests/state_layer_tests.cpp:113 | main | Provenance | D | True | False | assert(w->Provenance(StateField::CONTAINER_STATE,2).resolved_value==1); |
| src1.6.6/tests/state_layer_tests.cpp:114 | main | ContainerSource,EvidenceSource | D | True | False | assert(w->ContainerSource(2)==EvidenceSource::ACTION_SUCCESS); |
| src1.6.6/tests/state_layer_tests.cpp:117 | main | EvidenceSource,inside | D | True | False | s->inside=UNKNOWN; w->SetInsideEvidence(3,false,EvidenceSource::UNKNOWN); |
| src1.6.6/tests/state_layer_tests.cpp:123 | main | EvidenceSource,Provenance | D | True | False | assert(w->Provenance(StateField::CONTAINER_STATE,2).received.source==EvidenceSource::EXPLICIT_INFO); |
| src1.6.6/tests/state_layer_tests.cpp:124 | main | IsContainerStateVerified | D | True | False | assert(!w->IsContainerStateVerified(2)); |
| src1.6.6/tests/state_layer_tests.cpp:128 | main | location | D | True | False | assert(w->location==5); |
| src1.6.6/tests/state_layer_tests.cpp:129 | main | IsInsideVerified | D | True | False | assert(!w->IsInsideVerified(3)); |
| src1.6.6/tests/state_layer_tests.cpp:133 | main | inside,location | D | True | False | assert(s->inside==NONE && s->location==5); |
| src1.6.6/tests/state_layer_tests.cpp:134 | main | Provenance | D | True | False | assert(w->Provenance(StateField::INSIDE,3).resolved_value==UNKNOWN); |
| src1.6.6/tests/state_layer_tests.cpp:135 | main | Provenance | D | True | False | assert(w->Provenance(StateField::LOCATION,3).resolved_value==UNKNOWN); |
| src1.6.6/tests/state_layer_tests.cpp:139 | main | inside | D | True | False | assert(w->ParseEnvSentence("(inside 3 1)")); |
| src1.6.6/tests/state_layer_tests.cpp:140 | main | inside | D | True | False | assert(s->inside==UNKNOWN); |
| src1.6.6/tests/state_layer_tests.cpp:143 | main | inside | D | True | False | Instruction must=Goal("inside",s); must.Y.push_back(c); |
| src1.6.6/tests/state_layer_tests.cpp:146 | main | IsInsideVerified | D | True | False | assert(w->IsInsideVerified(3)); |
| src1.6.6/tests/state_layer_tests.cpp:147 | main | Provenance | D | True | False | assert(w->Provenance(StateField::INSIDE,3).support_constraint_index==0); |
| src1.6.6/tests/state_layer_tests.cpp:149 | main | IsInsideVerified | D | True | False | assert(!w->IsInsideVerified(3)); |
| src1.6.6/tests/state_layer_tests.cpp:151 | main | EvidenceSource,Provenance | D | True | False | assert(w->Provenance(StateField::HOLD,0).received.source==EvidenceSource::INITIAL); |
| src1.6.6/tests/state_layer_tests.cpp:152 | main | Provenance | D | True | False | assert(w->Provenance(StateField::PLATE,0).resolved_value==NONE); |
| src1.6.6/tests/state_layer_tests.cpp:154 | main | Provenance | D | True | False | assert(w->Provenance(StateField::HOLD,0).resolved_value==3); |
| src1.6.6/tests/state_layer_tests.cpp:155 | main | Provenance | D | True | False | assert(w->Provenance(StateField::HOLD,0).resolved_verified); |
| src1.6.6/tests/state_layer_tests.cpp:156 | main | EvidenceSource,Provenance | D | True | False | assert(w->Provenance(StateField::HOLD,0).received.source==EvidenceSource::ACTION_SUCCESS); |
| src1.6.6/tests/state_layer_tests.cpp:160 | main | ResolvedState | D | True | False | assert(w->ResolvedState(StateField::CONTAINER_STATE,2).present); |
| src1.6.6/tests/state_layer_tests.cpp:161 | main | Provenance | D | True | False | assert(w->Provenance(StateField::CONTAINER_STATE,2).supporting_constraints.size()==1); |
| src1.6.6/tests/state_layer_tests.cpp:163 | main | DependenciesCurrent | D | True | False | assert(!w->DependenciesCurrent(StateField::CONTAINER_STATE,2)); |
| src1.6.6/tests/state_layer_tests.cpp:164 | main | ResolvedState | D | True | False | assert(!w->ResolvedState(StateField::CONTAINER_STATE,2).present); |
| src1.6.6/tests/state_layer_tests.cpp:165 | main | IsContainerStateVerified | D | True | False | assert(!w->IsContainerStateVerified(2)); |
| src1.6.6/tests/state_layer_tests.cpp:167 | main | EvidenceSource,location | D | True | False | c->location=1; w->MarkDirectLocationEvidence(2,true,EvidenceSource::SENSE); |
| src1.6.6/tests/state_layer_tests.cpp:168 | main | location | D | True | False | w->objects[1]->location=UNKNOWN; |
| src1.6.6/tests/state_layer_tests.cpp:172 | main | ResolvedState | D | True | False | assert(w->ResolvedState(StateField::LOCATION,1).present); |
| src1.6.6/tests/state_layer_tests.cpp:173 | main | Provenance | D | True | False | assert(w->Provenance(StateField::LOCATION,1).supporting_constraints.size()==1); |
| src1.6.6/tests/state_layer_tests.cpp:175 | main | ResolvedState | D | True | False | assert(!w->ResolvedState(StateField::LOCATION,1).present); |
| src1.6.6/tests/state_layer_tests.cpp:179 | main | ResolvedState | D | True | False | assert(!w->ResolvedState(StateField::LOCATION,2).present); |
| src1.6.6/tests/state_layer_tests.cpp:181 | main | ResolvedState | D | True | False | assert(w->ResolvedState(StateField::LOCATION,2).value==1); |
| src1.6.6/tests/state_layer_tests.cpp:183 | main | DependenciesCurrent | D | True | False | assert(!w->DependenciesCurrent(StateField::LOCATION,2)); |
| src1.6.6/tests/state_layer_tests.cpp:184 | main | ResolvedState | D | True | False | assert(!w->ResolvedState(StateField::LOCATION,2).present); |
| src1.6.6/tests/task_group_projection_tests.cpp:24 | main | hold,plate | D | True | False | "(hold 0) (plate 0) (at 0 1) " |
| src1.6.6/tests/task_group_projection_tests.cpp:31 | main | location | D | True | False | const int initial_location = world.location; |
| src1.6.6/tests/task_group_projection_tests.cpp:39 | main | location | D | True | False | assert(world.location == initial_location); |
| src1.6.6/tests/task_group_projection_tests.cpp:46 | main | location | D | True | False | assert(world.location == initial_location); |
| src1.6.6/tests/task_group_projection_tests.cpp:58 | main | location | D | True | False | assert(world.location == initial_location); |
| src1.6.6/tests/task_group_projection_tests.cpp:67 | main | hold,plate | D | True | False | "(hold 0) (plate 0) (at 0 1) " |
| src1.6.6/tests/three_a_tests.cpp:28 | main | hold,plate | D | True | False | " (hold 0) (plate 0) (at 0 4) " |
| src1.6.6/tests/three_a_tests.cpp:70 | main | EvidenceSource | D | True | False | world->ApplyStateValue(StateField::CONTAINER_STATE,2,0,true,EvidenceSource::SENSE); |
| src1.6.6/tests/three_a_tests.cpp:82 | main | isOpen | D | True | False | std::dynamic_pointer_cast<Container>(world->objects[2])->isOpen = false; |
| src1.6.6/tests/three_a_tests.cpp:83 | main | location | D | True | False | const int location_before_preview = world->location; |
| src1.6.6/tests/three_a_tests.cpp:104 | main | location | D | True | False | assert(world->location == location_before_preview); |
| src1.6.6/tests/three_a_tests.cpp:105 | main | isOpen | D | True | False | assert(!std::dynamic_pointer_cast<Container>(world->objects[2])->isOpen); |
| src1.6.6/tests/three_a_tests.cpp:114 | main | EvidenceSource | D | True | False | world->ApplyStateValue(StateField::LOCATION,0,3,true,EvidenceSource::ACTION_SUCCESS); |
| src1.6.6/tests/three_a_tests.cpp:120 | main | location | D | True | False | assert(world->location == 3 && world->objects[2]->location == 4); |
