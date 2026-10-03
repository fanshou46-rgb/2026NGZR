# Direct access inventory BEFORE

A hypothesis; B fact query; C mutation; D serialization/restore/debug.
Functions are tracked by definition/body scope; mixed-function classifications are completed in CANONICAL_AUDIT_REVIEW.md / CANONICAL_AUDIT_FINAL.md.
Safe/Modify are review triage; each JSON row also records its semantic reason.

| File:line | Function | Fields | Type | Safe | Modify | Code |
|---|---|---|---|---|---|---|
| src1.6.5/legacy_priority.cpp:25 | isLocationKnown | location | B | False | True | if (!object \|\| object->location == _home::UNKNOWN) return false; |
| src1.6.5/legacy_priority.cpp:26 | isLocationKnown | location | B | False | True | if (object->id == 0) return world.location != _home::UNKNOWN; |
| src1.6.5/legacy_priority.cpp:27 | isLocationKnown | IsLocationVerified | B | False | True | return world.stage == 1 \|\| world.IsLocationVerified(object->id); |
| src1.6.5/legacy_priority.cpp:31 | isInsideKnown | inside | B | False | True | return object && object->inside != _home::UNKNOWN && |
| src1.6.5/legacy_priority.cpp:32 | isInsideKnown | IsInsideVerified | B | False | True | (world.stage == 1 \|\| world.IsInsideVerified(object->id)); |
| src1.6.5/legacy_priority.cpp:37 | isContainerStateKnown | isOpen | B | False | True | return container && (container->isOpen == 0 \|\| container->isOpen == 1) && |
| src1.6.5/legacy_priority.cpp:38 | isContainerStateKnown | IsContainerStateVerified | B | False | True | (world.stage == 1 \|\| world.IsContainerStateVerified(container->id)); |
| src1.6.5/legacy_priority.cpp:51 | evaluatePair | location | B | False | True | if (world.location != _home::UNKNOWN && |
| src1.6.5/legacy_priority.cpp:52 | evaluatePair | location | B | False | True | world.IsAbsentFromSensedLocation(x->id, world.location)) |
| src1.6.5/legacy_priority.cpp:54 | evaluatePair | location | B | False | True | if (!isLocationKnown(world, x) \|\| world.location == _home::UNKNOWN) |
| src1.6.5/legacy_priority.cpp:56 | evaluatePair | location | B | False | True | return boolStatus(world.location == x->location); |
| src1.6.5/legacy_priority.cpp:66 | evaluatePair | isOpen | B | False | True | return boolStatus(static_cast<bool>(container->isOpen) == expect_open); |
| src1.6.5/legacy_priority.cpp:70 | evaluatePair | hold_id,plate_id | B | False | True | const bool stored = world.hold_id == x->id \|\| world.plate_id == x->id; |
| src1.6.5/legacy_priority.cpp:71 | evaluatePair | IsInsideVerified | B | False | True | if (world.stage == 2 && !world.IsInsideVerified(x->id)) |
| src1.6.5/legacy_priority.cpp:80 | evaluatePair | hold_id,plate_id | B | False | True | if (world.hold_id == x->id \|\| world.plate_id == x->id) |
| src1.6.5/legacy_priority.cpp:82 | evaluatePair | inside | B | False | True | if (small->inside != _home::NONE) return TerminalStatus::UNSATISFIED; |
| src1.6.5/legacy_priority.cpp:87 | evaluatePair | inside | B | False | True | if (behave == "putin" \|\| behave == "inside" \|\| behave == "in") { |
| src1.6.5/legacy_priority.cpp:91 | evaluatePair | inside | B | False | True | return boolStatus(small->inside == y->id); |
| src1.6.5/legacy_priority.cpp:98 | evaluatePair | inside | B | False | True | return boolStatus(small->inside != y->id); |
| src1.6.5/legacy_priority.cpp:106 | evaluatePair | location | B | False | True | world.IsAbsentFromSensedLocation(target->id, x->location)) |
| src1.6.5/legacy_priority.cpp:109 | evaluatePair | location | B | False | True | world.IsAbsentFromSensedLocation(x->id, target->location)) |
| src1.6.5/legacy_priority.cpp:118 | evaluatePair | hold_id,plate_id | B | False | True | if (world.hold_id == x->id \|\| world.plate_id == x->id) |
| src1.6.5/legacy_priority.cpp:120 | evaluatePair | inside | B | False | True | if (small->inside != _home::NONE) return TerminalStatus::UNSATISFIED; |
| src1.6.5/legacy_priority.cpp:122 | evaluatePair | location | B | False | True | return boolStatus(x->location == target->location); |
| src1.6.5/legacy_priority.cpp:125 | evaluatePair | plate | B | False | True | if (behave == "plate") { |
| src1.6.5/legacy_priority.cpp:126 | evaluatePair | IsInsideVerified | B | False | True | if (world.stage == 2 && !world.IsInsideVerified(x->id)) |
| src1.6.5/legacy_priority.cpp:128 | evaluatePair | plate_id | B | False | True | return boolStatus(world.plate_id == x->id); |
| src1.6.5/legacy_priority.cpp:131 | evaluatePair | hold | B | False | True | if (behave == "hold") { |
| src1.6.5/legacy_priority.cpp:132 | evaluatePair | IsInsideVerified | B | False | True | if (world.stage == 2 && !world.IsInsideVerified(x->id)) |
| src1.6.5/legacy_priority.cpp:134 | evaluatePair | hold_id | B | False | True | return boolStatus(world.hold_id == x->id); |
| src1.6.5/parser.cpp:651 | get_info_instruction | plate | A | True | False | if (instr.behave == "on" && instr.isUseY && instr.conditionY.sort == "plate") |
| src1.6.5/parser.cpp:653 | get_info_instruction | plate | A | True | False | instr.behave = "plate"; |
| src1.6.5/question_preflight.cpp:30 | SemanticInstructionKey | location | D | True | False | // Do NOT use positions: two objects at the same location remain two goals. |
| src1.6.5/question_preflight.cpp:32 | SemanticInstructionKey | inside | A | True | False | if (predicate == "in") predicate = "inside"; |
| src1.6.5/question_preflight.cpp:56 | RunQuestionPreflight | location | A | True | False | if (location < 0 \|\| location > MAX_LOCATION_ID) |
| src1.6.5/question_preflight.cpp:57 | RunQuestionPreflight | location | A | True | False | world_error("robot has no usable initial location"); |
| src1.6.5/question_preflight.cpp:71 | RunQuestionPreflight | location | A | True | False | if (object->sort.empty() && !small && !big && object->location == UNKNOWN) |
| src1.6.5/question_preflight.cpp:75 | RunQuestionPreflight | location | A | True | False | if (object->location < UNKNOWN \|\| object->location > MAX_LOCATION_ID) |
| src1.6.5/question_preflight.cpp:76 | RunQuestionPreflight | location | A | True | False | world_error("object location out of bounds: " + std::to_string(i)); |
| src1.6.5/question_preflight.cpp:82 | RunQuestionPreflight | location | D | True | False | // Stage 2 location descriptions can be wrong; collisions there are NOT |
| src1.6.5/question_preflight.cpp:84 | RunQuestionPreflight | location | A | True | False | if (stage == 1 && big && object->location != UNKNOWN && |
| src1.6.5/question_preflight.cpp:85 | RunQuestionPreflight | location | A | True | False | !big_locations.emplace(object->location, object->id).second) |
| src1.6.5/question_preflight.cpp:86 | RunQuestionPreflight | location | A | True | False | world_warning("multiple big objects at Stage 1 location " + |
| src1.6.5/question_preflight.cpp:87 | RunQuestionPreflight | location | A | True | False | std::to_string(object->location)); |
| src1.6.5/rdfw.cpp:178 | EvidenceName | EvidenceSource | A | True | False | const char* EvidenceName(EvidenceSource source) { |
| src1.6.5/rdfw.cpp:180 | EvidenceName | EvidenceSource | A | True | False | case EvidenceSource::UNKNOWN: return "unknown"; |
| src1.6.5/rdfw.cpp:181 | EvidenceName | EvidenceSource | A | True | False | case EvidenceSource::INITIAL: return "initial"; |
| src1.6.5/rdfw.cpp:182 | EvidenceName | EvidenceSource | A | True | False | case EvidenceSource::EXPLICIT_INFO: return "explicit_info"; |
| src1.6.5/rdfw.cpp:183 | EvidenceName | EvidenceSource | A | True | False | case EvidenceSource::CONSTRAINT_DERIVED: return "constraint_derived"; |
| src1.6.5/rdfw.cpp:184 | EvidenceName | EvidenceSource | A | True | False | case EvidenceSource::RELATION_DERIVED: return "relation_derived"; |
| src1.6.5/rdfw.cpp:185 | EvidenceName | EvidenceSource | A | True | False | case EvidenceSource::CONSTRAINT_HEURISTIC: return "constraint_heuristic"; |
| src1.6.5/rdfw.cpp:186 | EvidenceName | EvidenceSource | A | True | False | case EvidenceSource::SENSE: return "sense"; |
| src1.6.5/rdfw.cpp:187 | EvidenceName | EvidenceSource | A | True | False | case EvidenceSource::ACTION_SUCCESS: return "action_success"; |
| src1.6.5/rdfw.cpp:188 | EvidenceName | EvidenceSource | A | True | False | case EvidenceSource::ACTION_FAILURE: return "action_failure"; |
| src1.6.5/rdfw.cpp:189 | EvidenceName | EvidenceSource | A | True | False | case EvidenceSource::ASK_ANSWER: return "ask_answer"; |
| src1.6.5/rdfw.cpp:275 | CaptureCandidateEvidence | objectLocationSource | B | False | True | if (i < objectLocationSource.size() && |
| src1.6.5/rdfw.cpp:276 | CaptureCandidateEvidence | EvidenceSource,objectLocationSource | B | False | True | objectLocationSource[i] != EvidenceSource::UNKNOWN) { |
| src1.6.5/rdfw.cpp:279 | CaptureCandidateEvidence | location | B | False | True | fact.fact = "location"; |
| src1.6.5/rdfw.cpp:280 | CaptureCandidateEvidence | objectLocationSource | B | False | True | fact.source = EvidenceName(objectLocationSource[i]); |
| src1.6.5/rdfw.cpp:281 | CaptureCandidateEvidence | IsLocationVerified | B | False | True | fact.verified = IsLocationVerified(static_cast<unsigned int>(i)); |
| src1.6.5/rdfw.cpp:284 | CaptureCandidateEvidence | objectInsideSource | B | False | True | if (i < objectInsideSource.size() && |
| src1.6.5/rdfw.cpp:285 | CaptureCandidateEvidence | EvidenceSource,objectInsideSource | B | False | True | objectInsideSource[i] != EvidenceSource::UNKNOWN) { |
| src1.6.5/rdfw.cpp:288 | CaptureCandidateEvidence | inside | B | False | True | fact.fact = "inside"; |
| src1.6.5/rdfw.cpp:289 | CaptureCandidateEvidence | objectInsideSource | B | False | True | fact.source = EvidenceName(objectInsideSource[i]); |
| src1.6.5/rdfw.cpp:290 | CaptureCandidateEvidence | IsInsideVerified | B | False | True | fact.verified = IsInsideVerified(static_cast<unsigned int>(i)); |
| src1.6.5/rdfw.cpp:293 | CaptureCandidateEvidence | containerStateSource | B | False | True | if (i < containerStateSource.size() && |
| src1.6.5/rdfw.cpp:294 | CaptureCandidateEvidence | EvidenceSource,containerStateSource | B | False | True | containerStateSource[i] != EvidenceSource::UNKNOWN) { |
| src1.6.5/rdfw.cpp:298 | CaptureCandidateEvidence | containerStateSource | B | False | True | fact.source = EvidenceName(containerStateSource[i]); |
| src1.6.5/rdfw.cpp:299 | CaptureCandidateEvidence | IsContainerStateVerified | B | False | True | fact.verified = IsContainerStateVerified(static_cast<unsigned int>(i)); |
| src1.6.5/rdfw.cpp:339 | BuildTaskGroupPlan | location | D | True | False | int location; |
| src1.6.5/rdfw.cpp:343 | BuildTaskGroupPlan | inside | D | True | False | int inside; |
| src1.6.5/rdfw.cpp:359 | BuildTaskGroupPlan | location | D | True | False | state.location = objects[i]->location; |
| src1.6.5/rdfw.cpp:366 | BuildTaskGroupPlan | inside | D | True | False | state.inside = small->inside; |
| src1.6.5/rdfw.cpp:373 | BuildTaskGroupPlan | isOpen | D | True | False | state.is_open = container->isOpen; |
| src1.6.5/rdfw.cpp:383 | BuildTaskGroupPlan | location | D | True | False | const int saved_location = location; |
| src1.6.5/rdfw.cpp:384 | BuildTaskGroupPlan | hold_id | D | True | False | const int saved_hold_id = hold_id; |
| src1.6.5/rdfw.cpp:385 | BuildTaskGroupPlan | plate_id | D | True | False | const int saved_plate_id = plate_id; |
| src1.6.5/rdfw.cpp:414 | BuildTaskGroupPlan | objectLocationInferredByMustNear | D | True | False | const std::vector<bool> saved_inferred = objectLocationInferredByMustNear; |
| src1.6.5/rdfw.cpp:417 | BuildTaskGroupPlan | objectLocationVerified | D | True | False | const std::vector<bool> saved_location_verified = objectLocationVerified; |
| src1.6.5/rdfw.cpp:418 | BuildTaskGroupPlan | objectInsideVerified | D | True | False | const std::vector<bool> saved_inside_verified = objectInsideVerified; |
| src1.6.5/rdfw.cpp:419 | BuildTaskGroupPlan | containerStateVerified | D | True | False | const std::vector<bool> saved_container_verified = containerStateVerified; |
| src1.6.5/rdfw.cpp:420 | BuildTaskGroupPlan | EvidenceSource,objectLocationSource | D | True | False | const std::vector<EvidenceSource> saved_location_source = objectLocationSource; |
| src1.6.5/rdfw.cpp:421 | BuildTaskGroupPlan | EvidenceSource,objectInsideSource | D | True | False | const std::vector<EvidenceSource> saved_inside_source = objectInsideSource; |
| src1.6.5/rdfw.cpp:422 | BuildTaskGroupPlan | EvidenceSource,containerStateSource | D | True | False | const std::vector<EvidenceSource> saved_container_source = containerStateSource; |
| src1.6.5/rdfw.cpp:423 | BuildTaskGroupPlan | StateProvenance,locationProvenance | D | True | False | const std::vector<StateProvenance> saved_location_provenance = locationProvenance; |
| src1.6.5/rdfw.cpp:424 | BuildTaskGroupPlan | StateProvenance,insideProvenance | D | True | False | const std::vector<StateProvenance> saved_inside_provenance = insideProvenance; |
| src1.6.5/rdfw.cpp:425 | BuildTaskGroupPlan | StateProvenance,containerProvenance | D | True | False | const std::vector<StateProvenance> saved_container_provenance = containerProvenance; |
| src1.6.5/rdfw.cpp:426 | BuildTaskGroupPlan | StateProvenance,holdProvenance | D | True | False | const StateProvenance saved_hold_provenance = holdProvenance; |
| src1.6.5/rdfw.cpp:427 | BuildTaskGroupPlan | StateProvenance,plateProvenance | D | True | False | const StateProvenance saved_plate_provenance = plateProvenance; |
| src1.6.5/rdfw.cpp:482 | BuildTaskGroupPlan | objectLocationInferredByMustNear | D | True | False | objectLocationInferredByMustNear = saved_inferred; |
| src1.6.5/rdfw.cpp:485 | BuildTaskGroupPlan | objectLocationVerified | D | True | False | objectLocationVerified = saved_location_verified; |
| src1.6.5/rdfw.cpp:486 | BuildTaskGroupPlan | objectInsideVerified | D | True | False | objectInsideVerified = saved_inside_verified; |
| src1.6.5/rdfw.cpp:487 | BuildTaskGroupPlan | containerStateVerified | D | True | False | containerStateVerified = saved_container_verified; |
| src1.6.5/rdfw.cpp:488 | BuildTaskGroupPlan | objectLocationSource | D | True | False | objectLocationSource = saved_location_source; |
| src1.6.5/rdfw.cpp:489 | BuildTaskGroupPlan | objectInsideSource | D | True | False | objectInsideSource = saved_inside_source; |
| src1.6.5/rdfw.cpp:490 | BuildTaskGroupPlan | containerStateSource | D | True | False | containerStateSource = saved_container_source; |
| src1.6.5/rdfw.cpp:491 | BuildTaskGroupPlan | locationProvenance | D | True | False | locationProvenance = saved_location_provenance; |
| src1.6.5/rdfw.cpp:492 | BuildTaskGroupPlan | insideProvenance | D | True | False | insideProvenance = saved_inside_provenance; |
| src1.6.5/rdfw.cpp:493 | BuildTaskGroupPlan | containerProvenance | D | True | False | containerProvenance = saved_container_provenance; |
| src1.6.5/rdfw.cpp:494 | BuildTaskGroupPlan | holdProvenance | D | True | False | holdProvenance = saved_hold_provenance; |
| src1.6.5/rdfw.cpp:495 | BuildTaskGroupPlan | plateProvenance | D | True | False | plateProvenance = saved_plate_provenance; |
| src1.6.5/rdfw.cpp:506 | BuildTaskGroupPlan | location | D | True | False | objects[i]->location = state.location; |
| src1.6.5/rdfw.cpp:513 | BuildTaskGroupPlan | inside | D | True | False | small->inside = state.inside; |
| src1.6.5/rdfw.cpp:523 | BuildTaskGroupPlan | isOpen | D | True | False | container->isOpen = object_states[i].is_open; |
| src1.6.5/rdfw.cpp:535 | BuildTaskGroupPlan | location | D | True | False | location = saved_location; |
| src1.6.5/rdfw.cpp:536 | BuildTaskGroupPlan | hold_id | D | True | False | hold_id = saved_hold_id; |
| src1.6.5/rdfw.cpp:537 | BuildTaskGroupPlan | plate_id | D | True | False | plate_id = saved_plate_id; |
| src1.6.5/rdfw.cpp:538 | BuildTaskGroupPlan | hold | D | True | False | hold = saved_hold_id > 0 && static_cast<std::size_t>(saved_hold_id) < objects.size() |
| src1.6.5/rdfw.cpp:540 | BuildTaskGroupPlan | plate | D | True | False | plate = saved_plate_id > 0 && static_cast<std::size_t>(saved_plate_id) < objects.size() |
| src1.6.5/rdfw.cpp:663 | BuildTaskGroupPlan | location | D | True | False | const int projected_location = location; |
| src1.6.5/rdfw.cpp:1259 | PlanStateSignature | hold_id,location,plate_id | D | True | False | out << location << ',' << hold_id << ',' << plate_id << ',' |
| src1.6.5/rdfw.cpp:1264 | PlanStateSignature | location | D | True | False | out << object->id << ',' << object->location << ',' |
| src1.6.5/rdfw.cpp:1268 | PlanStateSignature | inside | D | True | False | if (small) out << ',' << small->inside << ',' << small->on; |
| src1.6.5/rdfw.cpp:1272 | PlanStateSignature | isOpen | D | True | False | out << ',' << container->isOpen << '['; |
| src1.6.5/rdfw.cpp:1291 | PlanStateSignature | objectLocationVerified | D | True | False | out << (i < objectLocationVerified.size() && objectLocationVerified[i]) |
| src1.6.5/rdfw.cpp:1292 | PlanStateSignature | objectInsideVerified | D | True | False | << ':' << (i < objectInsideVerified.size() && objectInsideVerified[i]) |
| src1.6.5/rdfw.cpp:1293 | PlanStateSignature | containerStateVerified | D | True | False | << ':' << (i < containerStateVerified.size() && containerStateVerified[i]) |
| src1.6.5/rdfw.cpp:1294 | PlanStateSignature | objectLocationSource | D | True | False | << ':' << (i < objectLocationSource.size() ? |
| src1.6.5/rdfw.cpp:1295 | PlanStateSignature | objectLocationSource | D | True | False | static_cast<int>(objectLocationSource[i]) : -1) |
| src1.6.5/rdfw.cpp:1296 | PlanStateSignature | objectInsideSource | D | True | False | << ':' << (i < objectInsideSource.size() ? |
| src1.6.5/rdfw.cpp:1297 | PlanStateSignature | objectInsideSource | D | True | False | static_cast<int>(objectInsideSource[i]) : -1) |
| src1.6.5/rdfw.cpp:1298 | PlanStateSignature | containerStateSource | D | True | False | << ':' << (i < containerStateSource.size() ? |
| src1.6.5/rdfw.cpp:1299 | PlanStateSignature | containerStateSource | D | True | False | static_cast<int>(containerStateSource[i]) : -1) << ','; |
| src1.6.5/rdfw.cpp:1385 | UpdateConstraintLedger | hold_id,location | A | True | False | if (hold_id > 0) score_locations[hold_id] = location; |
| src1.6.5/rdfw.cpp:1386 | UpdateConstraintLedger | location,plate_id | A | True | False | if (plate_id > 0) score_locations[plate_id] = location; |
| src1.6.5/rdfw.cpp:1391 | UpdateConstraintLedger | location | A | True | False | performed == "FromPlate") score_locations[arguments[0]] = location; |
| src1.6.5/rdfw.cpp:1439 | DryRunActionSucceeds | location | A | True | False | static_cast<int>(arguments[0]) != location; |
| src1.6.5/rdfw.cpp:1447 | DryRunActionSucceeds | hold_id,plate_id | A | True | False | return small && hold_id == NONE && plate_id != static_cast<int>(a) && |
| src1.6.5/rdfw.cpp:1448 | DryRunActionSucceeds | location | A | True | False | small->location == location && |
| src1.6.5/rdfw.cpp:1449 | DryRunActionSucceeds | inside | A | True | False | (small->inside == NONE \|\| small->inside == UNKNOWN); |
| src1.6.5/rdfw.cpp:1451 | DryRunActionSucceeds | hold_id | A | True | False | if (action == "PutDown") return hold_id == static_cast<int>(a); |
| src1.6.5/rdfw.cpp:1453 | DryRunActionSucceeds | hold_id,plate_id | A | True | False | return hold_id == static_cast<int>(a) && plate_id == NONE; |
| src1.6.5/rdfw.cpp:1455 | DryRunActionSucceeds | hold_id,plate_id | A | True | False | return plate_id == static_cast<int>(a) && hold_id == NONE; |
| src1.6.5/rdfw.cpp:1459 | DryRunActionSucceeds | hold_id,location | A | True | False | return container && container->location == location && hold_id == NONE && |
| src1.6.5/rdfw.cpp:1460 | DryRunActionSucceeds | isOpen | A | True | False | container->isOpen == (action == "Open" ? 0 : 1); |
| src1.6.5/rdfw.cpp:1469 | DryRunActionSucceeds | location | A | True | False | if (!small \|\| !container \|\| container->location != location \|\| |
| src1.6.5/rdfw.cpp:1470 | DryRunActionSucceeds | isOpen | A | True | False | container->isOpen != 1) return false; |
| src1.6.5/rdfw.cpp:1471 | DryRunActionSucceeds | hold_id | A | True | False | if (action == "PutIn") return hold_id == static_cast<int>(a); |
| src1.6.5/rdfw.cpp:1472 | DryRunActionSucceeds | hold_id,inside | A | True | False | return hold_id == NONE && small->inside == static_cast<int>(b); |
| src1.6.5/rdfw.cpp:1479 | DryRunSenseIds | location | C | True | False | if (location < 0) return; |
| src1.6.5/rdfw.cpp:1481 | DryRunSenseIds | location | C | True | False | if (!objects[i] \|\| objects[i]->location != location) continue; |
| src1.6.5/rdfw.cpp:1482 | DryRunSenseIds | hold_id,plate_id | C | True | False | if (static_cast<int>(i) == hold_id \|\| static_cast<int>(i) == plate_id) continue; |
| src1.6.5/rdfw.cpp:1485 | DryRunSenseIds | inside | C | True | False | if (small && small->inside > 0 && |
| src1.6.5/rdfw.cpp:1486 | DryRunSenseIds | inside | C | True | False | static_cast<std::size_t>(small->inside) < objects.size()) { |
| src1.6.5/rdfw.cpp:1488 | DryRunSenseIds | inside | C | True | False | std::dynamic_pointer_cast<Container>(objects[small->inside]); |
| src1.6.5/rdfw.cpp:1489 | DryRunSenseIds | isOpen | C | True | False | if (container && container->isOpen != 1) continue; |
| src1.6.5/rdfw.cpp:1539 | InitializeDynamicArrays | objectLocationVerified | C | True | False | objectLocationVerified.assign(max_size, false); |
| src1.6.5/rdfw.cpp:1540 | InitializeDynamicArrays | objectLocationInferredByMustNear | C | True | False | objectLocationInferredByMustNear.assign(max_size, false); |
| src1.6.5/rdfw.cpp:1541 | InitializeDynamicArrays | objectInsideVerified | C | True | False | objectInsideVerified.assign(max_size, false); |
| src1.6.5/rdfw.cpp:1542 | InitializeDynamicArrays | containerStateVerified | C | True | False | containerStateVerified.assign(max_size, false); |
| src1.6.5/rdfw.cpp:1543 | InitializeDynamicArrays | EvidenceSource,objectLocationSource | C | True | False | objectLocationSource.assign(max_size, EvidenceSource::UNKNOWN); |
| src1.6.5/rdfw.cpp:1544 | InitializeDynamicArrays | EvidenceSource,objectInsideSource | C | True | False | objectInsideSource.assign(max_size, EvidenceSource::UNKNOWN); |
| src1.6.5/rdfw.cpp:1545 | InitializeDynamicArrays | EvidenceSource,containerStateSource | C | True | False | containerStateSource.assign(max_size, EvidenceSource::UNKNOWN); |
| src1.6.5/rdfw.cpp:1546 | InitializeDynamicArrays | StateProvenance,locationProvenance | C | True | False | locationProvenance.assign(max_size, StateProvenance()); |
| src1.6.5/rdfw.cpp:1547 | InitializeDynamicArrays | StateProvenance,insideProvenance | C | True | False | insideProvenance.assign(max_size, StateProvenance()); |
| src1.6.5/rdfw.cpp:1548 | InitializeDynamicArrays | StateProvenance,containerProvenance | C | True | False | containerProvenance.assign(max_size, StateProvenance()); |
| src1.6.5/rdfw.cpp:1549 | InitializeDynamicArrays | StateProvenance,holdProvenance | C | True | False | holdProvenance = StateProvenance(); |
| src1.6.5/rdfw.cpp:1550 | InitializeDynamicArrays | StateProvenance,plateProvenance | C | True | False | plateProvenance = StateProvenance(); |
| src1.6.5/rdfw.cpp:1777 | Plan | location | C | True | False | location = UNKNOWN; |
| src1.6.5/rdfw.cpp:1778 | Plan | hold | A | True | False | hold = nullptr; |
| src1.6.5/rdfw.cpp:1779 | Plan | hold_id | C | True | False | hold_id = 0; |
| src1.6.5/rdfw.cpp:1785 | Plan | objectLocationVerified | A | True | False | fill(objectLocationVerified.begin(), objectLocationVerified.end(), false); |
| src1.6.5/rdfw.cpp:1786 | Plan | objectLocationInferredByMustNear | A | True | False | fill(objectLocationInferredByMustNear.begin(), objectLocationInferredByMustNear.end(), false); |
| src1.6.5/rdfw.cpp:1787 | Plan | objectInsideVerified | A | True | False | fill(objectInsideVerified.begin(), objectInsideVerified.end(), false); |
| src1.6.5/rdfw.cpp:1788 | Plan | containerStateVerified | A | True | False | fill(containerStateVerified.begin(), containerStateVerified.end(), false); |
| src1.6.5/rdfw.cpp:1789 | Plan | EvidenceSource,objectLocationSource | A | True | False | fill(objectLocationSource.begin(), objectLocationSource.end(), EvidenceSource::UNKNOWN); |
| src1.6.5/rdfw.cpp:1790 | Plan | EvidenceSource,objectInsideSource | A | True | False | fill(objectInsideSource.begin(), objectInsideSource.end(), EvidenceSource::UNKNOWN); |
| src1.6.5/rdfw.cpp:1791 | Plan | EvidenceSource,containerStateSource | A | True | False | fill(containerStateSource.begin(), containerStateSource.end(), EvidenceSource::UNKNOWN); |
| src1.6.5/rdfw.cpp:1792 | Plan | StateProvenance,locationProvenance | A | True | False | fill(locationProvenance.begin(), locationProvenance.end(), StateProvenance()); |
| src1.6.5/rdfw.cpp:1793 | Plan | StateProvenance,insideProvenance | A | True | False | fill(insideProvenance.begin(), insideProvenance.end(), StateProvenance()); |
| src1.6.5/rdfw.cpp:1794 | Plan | StateProvenance,containerProvenance | A | True | False | fill(containerProvenance.begin(), containerProvenance.end(), StateProvenance()); |
| src1.6.5/rdfw.cpp:1795 | Plan | StateProvenance,holdProvenance | A | True | False | holdProvenance = StateProvenance(); |
| src1.6.5/rdfw.cpp:1796 | Plan | StateProvenance,plateProvenance | A | True | False | plateProvenance = StateProvenance(); |
| src1.6.5/rdfw.cpp:1954 | Plan | location | A | True | False | LOG("[TradeoffEvidence] probing current location before decisions\n"); |
| src1.6.5/rdfw.cpp:2487 | Cons_plan | location | A | True | False | if (cons.Y.empty() \|\| !cons.Y[0] \|\| cons.Y[0]->location < 0 \|\| |
| src1.6.5/rdfw.cpp:2488 | Cons_plan | location | A | True | False | !EnsureLocationCapacity(cons.Y[0]->location)) continue; |
| src1.6.5/rdfw.cpp:2489 | Cons_plan | location | A | True | False | if(cons.X[0]->location!=cons.Y[0]->location) putdown_cons[cons.X[0]->id][cons.Y[0]->location]++; |
| src1.6.5/rdfw.cpp:2490 | Cons_plan | hold_id,location,plate_id | A | True | False | else if(cons.X[0]->id==plate_id\|\|cons.X[0]->id==hold_id) putdown_cons[cons.X[0]->id][cons.Y[0]->location]++; |
| src1.6.5/rdfw.cpp:2492 | Cons_plan | inside | A | True | False | else if(cons.behave=="inside"\|\|cons.behave=="in") { |
| src1.6.5/rdfw.cpp:2495 | Cons_plan | inside | A | True | False | if(small && small->inside!=cons.Y[0]->id) putin_cons[cons.X[0]->id][cons.Y[0]->id]++; |
| src1.6.5/rdfw.cpp:2499 | Cons_plan | location | A | True | False | if(cons.Y[0]->location!=cons.X[0]->location) //如果约束没有触犯 |
| src1.6.5/rdfw.cpp:2501 | Cons_plan | location | A | True | False | if(cons.Y[0]->location!=UNKNOWN) move_cons[cons.X[0]->id][cons.Y[0]->location]++; |
| src1.6.5/rdfw.cpp:2502 | Cons_plan | location | A | True | False | if(cons.X[0]->location!=UNKNOWN) move_cons[cons.Y[0]->id][cons.X[0]->location]++; |
| src1.6.5/rdfw.cpp:2505 | Cons_plan | plate | A | True | False | else if(cons.behave == "plate") toplate_cons[cons.X[0]->id]++; |
| src1.6.5/rdfw.cpp:2508 | Cons_plan | isOpen | A | True | False | if(cont && cont->isOpen!=1) open_cons[cons.X[0]->id]++; |
| src1.6.5/rdfw.cpp:2513 | Cons_plan | isOpen | A | True | False | if(cont && cont->isOpen==1) close_cons[cons.X[0]->id]++; |
| src1.6.5/rdfw.cpp:2523 | Cons_plan | location | A | True | False | cons.X[0]->location==cons.Y[0]->location) { |
| src1.6.5/rdfw.cpp:2525 | Cons_plan | inside | A | True | False | if(small && small->inside!=cons.Y[0]->id) cons.X[0]->is_keep++; |
| src1.6.5/rdfw.cpp:2534 | Cons_plan | location | A | True | False | if (x_obj->location != UNKNOWN && x_obj->location == y_obj->location) { |
| src1.6.5/rdfw.cpp:2541 | Cons_plan | plate,plate_id | A | True | False | else if(cons.behave=="plate"&& plate_id==cons.X[0]->id)fromplate_cons[cons.X[0]->id]++; |
| src1.6.5/rdfw.cpp:2542 | Cons_plan | inside | A | True | False | else if(cons.behave=="inside"\|\|cons.behave=="in") |
| src1.6.5/rdfw.cpp:2546 | Cons_plan | inside | A | True | False | if(small && small->inside==cons.Y[0]->id)  takeout_cons[cons.X[0]->id][cons.Y[0]->id]++; |
| src1.6.5/rdfw.cpp:2550 | Cons_plan | isOpen | A | True | False | if(cont && cont->isOpen!=1) open_cons[cons.X[0]->id]++; |
| src1.6.5/rdfw.cpp:2554 | Cons_plan | isOpen | A | True | False | if(cont && cont->isOpen!=1) close_cons[cons.X[0]->id]++; |
| src1.6.5/rdfw.cpp:2567 | Cons_plan | location | A | True | False | cons.Y[0]->location >= 0 && EnsureLocationCapacity(cons.Y[0]->location)) |
| src1.6.5/rdfw.cpp:2568 | Cons_plan | location | A | True | False | putdown_cons[cons.X[0]->id][cons.Y[0]->location]++; |
| src1.6.5/rdfw.cpp:2569 | Cons_plan | location | A | True | False | else if(cons.behave=="goto" && cons.X[0]->location >= 0 && |
| src1.6.5/rdfw.cpp:2570 | Cons_plan | location | A | True | False | EnsureLocationCapacity(cons.X[0]->location)) goto_cons[cons.X[0]->location]++; |
| src1.6.5/rdfw.cpp:2577 | Cons_plan | hold_id,location | A | True | False | if(IsValidObjectId(hold_id) && location >= 0 && EnsureLocationCapacity(location)) { |
| src1.6.5/rdfw.cpp:2578 | Cons_plan | hold_id | A | True | False | x=hold_id; |
| src1.6.5/rdfw.cpp:2579 | Cons_plan | location | A | True | False | if(objects[x]->is_keep>putdown1_cons[x]+putdown_cons[x][location]+fromplate_cons[x]){ |
| src1.6.5/rdfw.cpp:2580 | Cons_plan | hold | A | True | False | cout<<"the hold object must putdown here!"<<endl; |
| src1.6.5/rdfw.cpp:2584 | Cons_plan | location,plate_id | A | True | False | if(IsValidObjectId(plate_id) && location >= 0 && EnsureLocationCapacity(location)) |
| src1.6.5/rdfw.cpp:2586 | Cons_plan | plate_id | A | True | False | x=plate_id; |
| src1.6.5/rdfw.cpp:2587 | Cons_plan | location | A | True | False | if(objects[x]->is_keep>putdown1_cons[x]+putdown_cons[x][location]+fromplate_cons[x]){ |
| src1.6.5/rdfw.cpp:2588 | Cons_plan | plate | A | True | False | cout<<"the plate object must putdown here!"<<endl; |
| src1.6.5/rdfw.cpp:2589 | Cons_plan | hold_id | A | True | False | if(hold_id>0) PutDown(hold_id); |
| src1.6.5/rdfw.cpp:2613 | FilterConstraintsByTaskConflicts | location | A | True | False | if ((task.behave == "goto" && has_x && task.X[0]->location == loc) \|\| |
| src1.6.5/rdfw.cpp:2614 | FilterConstraintsByTaskConflicts | location | A | True | False | (task.behave == "putin" && has_y && task.Y[0]->location == loc) \|\| |
| src1.6.5/rdfw.cpp:2615 | FilterConstraintsByTaskConflicts | location | A | True | False | (task.behave == "putin" && has_x && task.X[0]->location == loc)\|\| |
| src1.6.5/rdfw.cpp:2616 | FilterConstraintsByTaskConflicts | location | A | True | False | (task.behave == "puton" && has_y && task.Y[0]->location == loc)\|\| |
| src1.6.5/rdfw.cpp:2617 | FilterConstraintsByTaskConflicts | location | A | True | False | (task.behave == "puton" && has_x && task.X[0]->location == loc)\|\| |
| src1.6.5/rdfw.cpp:2618 | FilterConstraintsByTaskConflicts | location | A | True | False | (task.behave == "open" && has_x && task.X[0]->location == loc)\|\| |
| src1.6.5/rdfw.cpp:2619 | FilterConstraintsByTaskConflicts | location | A | True | False | (task.behave == "close" && has_x && task.X[0]->location == loc)\|\| |
| src1.6.5/rdfw.cpp:2620 | FilterConstraintsByTaskConflicts | location | A | True | False | (task.behave == "pickup" && has_x && task.X[0]->location == loc)\|\| |
| src1.6.5/rdfw.cpp:2621 | FilterConstraintsByTaskConflicts | location | A | True | False | (task.behave == "give" && has_x && task.X[0]->location == loc)\|\| |
| src1.6.5/rdfw.cpp:2622 | FilterConstraintsByTaskConflicts | location | A | True | False | (task.behave == "give" && has_y && task.Y[0]->location == loc)\|\| |
| src1.6.5/rdfw.cpp:2623 | FilterConstraintsByTaskConflicts | location | A | True | False | (task.behave == "takeout" && has_y && task.Y[0]->location == loc)) { |
| src1.6.5/rdfw.cpp:2625 | FilterConstraintsByTaskConflicts | location | A | True | False | cout << "[FilterConstraintsByTaskConflicts] Conflict found between goto_cons at location " << loc << " and task " << task.behave << endl; |
| src1.6.5/rdfw.cpp:2636 | FilterConstraintsByTaskConflicts | location | A | True | False | cout << "[FilterConstraintsByTaskConflicts] Conflict found between goto_cons at location " << loc << " with conflict count " << conflict_count << endl; |
| src1.6.5/rdfw.cpp:2644 | FilterConstraintsByTaskConflicts | location | A | True | False | cout << "[FilterConstraintsByTaskConflicts] Discarded goto_cons at location " << max_effect_loc << " due to " << max_effect << " conflicts." << endl; |
| src1.6.5/rdfw.cpp:2649 | FilterConstraintsByTaskConflicts | location | A | True | False | cout << "[FilterConstraintsByTaskConflicts] Discarded goto_cons at location " << it->first << " due to " << it->second << " conflicts." << endl; |
| src1.6.5/rdfw.cpp:2827 | CalculateTaskRisk | inside | A | True | False | if(small->inside!=t.Y[0]->id) return 0;//如果任务满足 |
| src1.6.5/rdfw.cpp:2828 | CalculateTaskRisk | location | A | True | False | t.risk+=takeout_cons[t.X[0]->id][t.Y[0]->id]+goto_risk(t.Y[0]->location); |
| src1.6.5/rdfw.cpp:2835 | CalculateTaskRisk | inside | A | True | False | if(small->inside==t.Y[0]->id) return 0; |
| src1.6.5/rdfw.cpp:2837 | CalculateTaskRisk | location | A | True | False | if (t.Y[0]->location >= 0 && EnsureLocationCapacity(t.Y[0]->location)) |
| src1.6.5/rdfw.cpp:2838 | CalculateTaskRisk | location | A | True | False | t.risk += move_cons[t.X[0]->id][t.Y[0]->location]; |
| src1.6.5/rdfw.cpp:2839 | CalculateTaskRisk | location | A | True | False | if(t.X[0]->location!=t.Y[0]->location) t.risk+=goto_risk(t.Y[0]->location); |
| src1.6.5/rdfw.cpp:2844 | CalculateTaskRisk | location | A | True | False | if (t.Y[0]->location >= 0 && EnsureLocationCapacity(t.Y[0]->location)) |
| src1.6.5/rdfw.cpp:2845 | CalculateTaskRisk | location | A | True | False | t.risk+= putdown_cons[t.X[0]->id][t.Y[0]->location]+move_cons[t.X[0]->id][t.Y[0]->location]; |
| src1.6.5/rdfw.cpp:2847 | CalculateTaskRisk | location | A | True | False | if(t.X[0]->location!=t.Y[0]->location) t.risk+=goto_risk(t.Y[0]->location); |
| src1.6.5/rdfw.cpp:2851 | CalculateTaskRisk | location | A | True | False | int loc = t.X[0]->location; |
| src1.6.5/rdfw.cpp:2859 | CalculateTaskRisk | location | A | True | False | else if(t.behave=="open") t.risk+=open_cons[t.X[0]->id]+goto_risk(t.X[0]->location); |
| src1.6.5/rdfw.cpp:2860 | CalculateTaskRisk | location | A | True | False | else if(t.behave=="close") t.risk+=close_cons[t.X[0]->id]+goto_risk(t.X[0]->location); |
| src1.6.5/rdfw.cpp:2868 | CalculateTaskRisk | location | A | True | False | if (human->location >= 0 && EnsureLocationCapacity(human->location)) |
| src1.6.5/rdfw.cpp:2869 | CalculateTaskRisk | location | A | True | False | t.risk += move_cons[t.X[0]->id][human->location]; |
| src1.6.5/rdfw.cpp:2870 | CalculateTaskRisk | location | A | True | False | if(t.X[0]->location!=human->location) t.risk+=goto_risk(human->location); |
| src1.6.5/rdfw.cpp:2875 | CalculateTaskRisk | location | D | True | False | // goto targets an object's location; the target object itself is untouched. |
| src1.6.5/rdfw.cpp:2896 | CalculateTaskRisk | location | A | True | False | if (other && other->location == t.X[0]->location && t.X[0]->location != UNKNOWN) { |
| src1.6.5/rdfw.cpp:2914 | CalculateStepRisk | location | A | True | False | if(t.X[0]->location!=location && t.X[0]->location >= 0) { |
| src1.6.5/rdfw.cpp:2915 | CalculateStepRisk | location | A | True | False | if (!EnsureLocationCapacity(t.X[0]->location)) return 0; |
| src1.6.5/rdfw.cpp:2916 | CalculateStepRisk | location | A | True | False | t.risk+=goto_cons[t.X[0]->location]; |
| src1.6.5/rdfw.cpp:2920 | CalculateStepRisk | inside | A | True | False | if(small->inside!=UNKNOWN&&small->inside!=NONE && |
| src1.6.5/rdfw.cpp:2921 | CalculateStepRisk | inside | A | True | False | IsValidObjectId(small->inside)) |
| src1.6.5/rdfw.cpp:2922 | CalculateStepRisk | inside | A | True | False | t.risk+=open_cons[small->inside]+takeout_cons[small->id][small->inside]; |
| src1.6.5/rdfw.cpp:2923 | CalculateStepRisk | inside | A | True | False | else if(small->inside==NONE) t.risk+=pickup_cons[small->id]; |
| src1.6.5/rdfw.cpp:2944 | EnsureLocationCapacity | inside | D | True | False | // Normal inputs stay inside the preallocated range.  Keep this hot path |
| src1.6.5/rdfw.cpp:2945 | EnsureLocationCapacity | location | D | True | False | // constant-time; full row scans are needed only when a new location column |
| src1.6.5/rdfw.cpp:3031 | EnsureEvidenceCapacity | objectLocationVerified | C | True | False | if (objectLocationVerified.size() < required) |
| src1.6.5/rdfw.cpp:3032 | EnsureEvidenceCapacity | objectLocationVerified | C | True | False | objectLocationVerified.resize(required, false); |
| src1.6.5/rdfw.cpp:3033 | EnsureEvidenceCapacity | objectLocationInferredByMustNear | C | True | False | if (objectLocationInferredByMustNear.size() < required) |
| src1.6.5/rdfw.cpp:3034 | EnsureEvidenceCapacity | objectLocationInferredByMustNear | C | True | False | objectLocationInferredByMustNear.resize(required, false); |
| src1.6.5/rdfw.cpp:3035 | EnsureEvidenceCapacity | objectInsideVerified | C | True | False | if (objectInsideVerified.size() < required) |
| src1.6.5/rdfw.cpp:3036 | EnsureEvidenceCapacity | objectInsideVerified | C | True | False | objectInsideVerified.resize(required, false); |
| src1.6.5/rdfw.cpp:3037 | EnsureEvidenceCapacity | containerStateVerified | C | True | False | if (containerStateVerified.size() < required) |
| src1.6.5/rdfw.cpp:3038 | EnsureEvidenceCapacity | containerStateVerified | C | True | False | containerStateVerified.resize(required, false); |
| src1.6.5/rdfw.cpp:3039 | EnsureEvidenceCapacity | objectLocationSource | C | True | False | if (objectLocationSource.size() < required) |
| src1.6.5/rdfw.cpp:3040 | EnsureEvidenceCapacity | EvidenceSource,objectLocationSource | C | True | False | objectLocationSource.resize(required, EvidenceSource::UNKNOWN); |
| src1.6.5/rdfw.cpp:3041 | EnsureEvidenceCapacity | objectInsideSource | C | True | False | if (objectInsideSource.size() < required) |
| src1.6.5/rdfw.cpp:3042 | EnsureEvidenceCapacity | EvidenceSource,objectInsideSource | C | True | False | objectInsideSource.resize(required, EvidenceSource::UNKNOWN); |
| src1.6.5/rdfw.cpp:3043 | EnsureEvidenceCapacity | containerStateSource | C | True | False | if (containerStateSource.size() < required) |
| src1.6.5/rdfw.cpp:3044 | EnsureEvidenceCapacity | EvidenceSource,containerStateSource | C | True | False | containerStateSource.resize(required, EvidenceSource::UNKNOWN); |
| src1.6.5/rdfw.cpp:3045 | EnsureEvidenceCapacity | locationProvenance | C | True | False | if (locationProvenance.size() < required) locationProvenance.resize(required); |
| src1.6.5/rdfw.cpp:3046 | EnsureEvidenceCapacity | insideProvenance | C | True | False | if (insideProvenance.size() < required) insideProvenance.resize(required); |
| src1.6.5/rdfw.cpp:3047 | EnsureEvidenceCapacity | containerProvenance | C | True | False | if (containerProvenance.size() < required) containerProvenance.resize(required); |
| src1.6.5/rdfw.cpp:3051 | MutableProvenance | MutableProvenance,StateProvenance | C | True | False | StateProvenance& RDFW::MutableProvenance(StateField field, unsigned int id) { |
| src1.6.5/rdfw.cpp:3052 | MutableProvenance | holdProvenance | C | True | False | if (field == StateField::HOLD) return holdProvenance; |
| src1.6.5/rdfw.cpp:3053 | MutableProvenance | plateProvenance | C | True | False | if (field == StateField::PLATE) return plateProvenance; |
| src1.6.5/rdfw.cpp:3054 | MutableProvenance | locationProvenance | C | True | False | if (field == StateField::LOCATION) return locationProvenance[id]; |
| src1.6.5/rdfw.cpp:3055 | MutableProvenance | insideProvenance | C | True | False | if (field == StateField::INSIDE) return insideProvenance[id]; |
| src1.6.5/rdfw.cpp:3056 | MutableProvenance | containerProvenance | C | True | False | return containerProvenance[id]; |
| src1.6.5/rdfw.cpp:3059 | Provenance | Provenance,StateProvenance | D | True | False | const StateProvenance& RDFW::Provenance(StateField field, unsigned int id) const { |
| src1.6.5/rdfw.cpp:3060 | Provenance | StateProvenance | D | True | False | static const StateProvenance empty; |
| src1.6.5/rdfw.cpp:3061 | Provenance | holdProvenance | D | True | False | if (field == StateField::HOLD) return holdProvenance; |
| src1.6.5/rdfw.cpp:3062 | Provenance | plateProvenance | D | True | False | if (field == StateField::PLATE) return plateProvenance; |
| src1.6.5/rdfw.cpp:3063 | Provenance | StateProvenance | D | True | False | const std::vector<StateProvenance>& records = field == StateField::LOCATION |
| src1.6.5/rdfw.cpp:3064 | Provenance | locationProvenance | D | True | False | ? locationProvenance : field == StateField::INSIDE |
| src1.6.5/rdfw.cpp:3065 | Provenance | containerProvenance,insideProvenance | D | True | False | ? insideProvenance : containerProvenance; |
| src1.6.5/rdfw.cpp:3069 | SetHold | EvidenceSource | C | False | True | void RDFW::SetHold(const shared_ptr<SmallObject>& item, EvidenceSource source) { |
| src1.6.5/rdfw.cpp:3070 | SetHold | plate_id | C | False | True | const int old_plate = plate_id; |
| src1.6.5/rdfw.cpp:3072 | SetHold | EvidenceSource | C | False | True | const bool verified = stage == 1 \|\| source == EvidenceSource::ACTION_SUCCESS; |
| src1.6.5/rdfw.cpp:3073 | SetHold | UpdateProvenance,hold_id | C | False | True | UpdateProvenance(StateField::HOLD, 0, hold_id, verified, source); |
| src1.6.5/rdfw.cpp:3074 | SetHold | plate_id | C | False | True | if (old_plate != plate_id) |
| src1.6.5/rdfw.cpp:3075 | SetHold | UpdateProvenance,plate_id | C | False | True | UpdateProvenance(StateField::PLATE, 0, plate_id, verified, source); |
| src1.6.5/rdfw.cpp:3078 | SetPlate | EvidenceSource | C | False | True | void RDFW::SetPlate(const shared_ptr<SmallObject>& item, EvidenceSource source) { |
| src1.6.5/rdfw.cpp:3079 | SetPlate | hold_id | C | False | True | const int old_hold = hold_id; |
| src1.6.5/rdfw.cpp:3081 | SetPlate | EvidenceSource | C | False | True | const bool verified = stage == 1 \|\| source == EvidenceSource::ACTION_SUCCESS; |
| src1.6.5/rdfw.cpp:3082 | SetPlate | hold_id | C | False | True | if (old_hold != hold_id) |
| src1.6.5/rdfw.cpp:3083 | SetPlate | UpdateProvenance,hold_id | C | False | True | UpdateProvenance(StateField::HOLD, 0, hold_id, verified, source); |
| src1.6.5/rdfw.cpp:3084 | SetPlate | UpdateProvenance,plate_id | C | False | True | UpdateProvenance(StateField::PLATE, 0, plate_id, verified, source); |
| src1.6.5/rdfw.cpp:3088 | HasContradictoryEvidence | Provenance,StateProvenance | A | True | False | const StateProvenance& p = Provenance(field, id); |
| src1.6.5/rdfw.cpp:3094 | ReceiveWeakClaim | EvidenceSource | C | True | False | EvidenceSource source) { |
| src1.6.5/rdfw.cpp:3096 | ReceiveWeakClaim | MutableProvenance,StateProvenance | C | True | False | StateProvenance& p = MutableProvenance(field, id); |
| src1.6.5/rdfw.cpp:3098 | ReceiveWeakClaim | EvidenceSource | C | True | False | (p.received.source == EvidenceSource::INITIAL \|\| |
| src1.6.5/rdfw.cpp:3099 | ReceiveWeakClaim | EvidenceSource | C | True | False | p.received.source == EvidenceSource::ASK_ANSWER \|\| |
| src1.6.5/rdfw.cpp:3100 | ReceiveWeakClaim | EvidenceSource | C | True | False | p.received.source == EvidenceSource::EXPLICIT_INFO); |
| src1.6.5/rdfw.cpp:3111 | MarkUnresolved | MutableProvenance,StateProvenance | C | False | True | StateProvenance& p = MutableProvenance(field, id); |
| src1.6.5/rdfw.cpp:3112 | MarkUnresolved | EvidenceSource | C | False | True | if (p.resolved_value != UNKNOWN \|\| p.resolved_source != EvidenceSource::UNKNOWN) |
| src1.6.5/rdfw.cpp:3115 | MarkUnresolved | EvidenceSource | C | False | True | p.resolved_source = EvidenceSource::UNKNOWN; |
| src1.6.5/rdfw.cpp:3122 | UpdateProvenance | UpdateProvenance | C | True | False | void RDFW::UpdateProvenance(StateField field, unsigned int id, int value, |
| src1.6.5/rdfw.cpp:3123 | UpdateProvenance | EvidenceSource | C | True | False | bool verified, EvidenceSource source) { |
| src1.6.5/rdfw.cpp:3125 | UpdateProvenance | MutableProvenance,StateProvenance | C | True | False | StateProvenance& p = MutableProvenance(field, id); |
| src1.6.5/rdfw.cpp:3126 | UpdateProvenance | EvidenceSource | C | True | False | const bool derived = source == EvidenceSource::CONSTRAINT_DERIVED \|\| |
| src1.6.5/rdfw.cpp:3127 | UpdateProvenance | EvidenceSource | C | True | False | source == EvidenceSource::RELATION_DERIVED \|\| |
| src1.6.5/rdfw.cpp:3128 | UpdateProvenance | EvidenceSource | C | True | False | source == EvidenceSource::CONSTRAINT_HEURISTIC; |
| src1.6.5/rdfw.cpp:3129 | UpdateProvenance | EvidenceSource | C | True | False | if (!derived && source != EvidenceSource::UNKNOWN) { |
| src1.6.5/rdfw.cpp:3148 | DependOn | MutableProvenance,StateProvenance | C | True | False | StateProvenance& p = MutableProvenance(derived_field, derived_id); |
| src1.6.5/rdfw.cpp:3150 | DependOn | Provenance,StateProvenance | C | True | False | const StateProvenance& support = Provenance(support_field, support_id); |
| src1.6.5/rdfw.cpp:3157 | SetConstraintSupport | MutableProvenance | C | True | False | MutableProvenance(field, id).support_constraint_index = index; |
| src1.6.5/rdfw.cpp:3161 | RecordConstraintSupports | MutableProvenance,StateProvenance | C | True | False | StateProvenance& p = MutableProvenance(field, id); |
| src1.6.5/rdfw.cpp:3188 | ResolvedState | ResolvedState | B | False | True | StateClaim RDFW::ResolvedState(StateField field, unsigned int id) const { |
| src1.6.5/rdfw.cpp:3189 | ResolvedState | Provenance,StateProvenance | B | False | True | const StateProvenance& p = Provenance(field, id); |
| src1.6.5/rdfw.cpp:3191 | ResolvedState | DependenciesCurrent | B | False | True | !DependenciesCurrent(field, id)) return StateClaim(); |
| src1.6.5/rdfw.cpp:3195 | DependenciesCurrent | DependenciesCurrent | B | False | True | bool RDFW::DependenciesCurrent(StateField field, unsigned int id) const { |
| src1.6.5/rdfw.cpp:3202 | DependenciesCurrentDepth | Provenance,StateProvenance | B | False | True | const StateProvenance& p = Provenance(field, id); |
| src1.6.5/rdfw.cpp:3215 | DependenciesCurrentDepth | Provenance,StateProvenance | B | False | True | const StateProvenance& support = Provenance(d.field, d.id); |
| src1.6.5/rdfw.cpp:3224 | MarkDirectLocationEvidence | EvidenceSource | C | True | False | EvidenceSource source) { |
| src1.6.5/rdfw.cpp:3226 | MarkDirectLocationEvidence | objectLocationVerified | C | True | False | objectLocationVerified[id] = verified; |
| src1.6.5/rdfw.cpp:3227 | MarkDirectLocationEvidence | objectLocationSource | C | True | False | objectLocationSource[id] = source; |
| src1.6.5/rdfw.cpp:3228 | MarkDirectLocationEvidence | location | C | True | False | const int value = id < objects.size() && objects[id] ? objects[id]->location : UNKNOWN; |
| src1.6.5/rdfw.cpp:3229 | MarkDirectLocationEvidence | UpdateProvenance | C | True | False | UpdateProvenance(StateField::LOCATION, id, value, verified, source); |
| src1.6.5/rdfw.cpp:3230 | MarkDirectLocationEvidence | EvidenceSource | C | True | False | if (source == EvidenceSource::CONSTRAINT_DERIVED \|\| source == EvidenceSource::CONSTRAINT_HEURISTIC) |
| src1.6.5/rdfw.cpp:3232 | MarkDirectLocationEvidence | objectLocationInferredByMustNear | C | True | False | objectLocationInferredByMustNear[id] = |
| src1.6.5/rdfw.cpp:3233 | MarkDirectLocationEvidence | EvidenceSource | C | True | False | source == EvidenceSource::CONSTRAINT_DERIVED \|\| |
| src1.6.5/rdfw.cpp:3234 | MarkDirectLocationEvidence | EvidenceSource | C | True | False | source == EvidenceSource::CONSTRAINT_HEURISTIC; |
| src1.6.5/rdfw.cpp:3237 | SetInsideEvidence | EvidenceSource | C | True | False | void RDFW::SetInsideEvidence(unsigned int id, bool verified, EvidenceSource source) { |
| src1.6.5/rdfw.cpp:3239 | SetInsideEvidence | objectInsideVerified | C | True | False | objectInsideVerified[id] = verified; |
| src1.6.5/rdfw.cpp:3240 | SetInsideEvidence | objectInsideSource | C | True | False | objectInsideSource[id] = source; |
| src1.6.5/rdfw.cpp:3242 | SetInsideEvidence | UpdateProvenance,inside | C | True | False | UpdateProvenance(StateField::INSIDE, id, small ? small->inside : UNKNOWN, verified, source); |
| src1.6.5/rdfw.cpp:3245 | SetContainerEvidence | EvidenceSource | C | True | False | void RDFW::SetContainerEvidence(unsigned int id, bool verified, EvidenceSource source) { |
| src1.6.5/rdfw.cpp:3247 | SetContainerEvidence | containerStateVerified | C | True | False | containerStateVerified[id] = verified; |
| src1.6.5/rdfw.cpp:3248 | SetContainerEvidence | containerStateSource | C | True | False | containerStateSource[id] = source; |
| src1.6.5/rdfw.cpp:3250 | SetContainerEvidence | UpdateProvenance | C | True | False | UpdateProvenance(StateField::CONTAINER_STATE, id, |
| src1.6.5/rdfw.cpp:3251 | SetContainerEvidence | isOpen | C | True | False | container ? container->isOpen : UNKNOWN, verified, source); |
| src1.6.5/rdfw.cpp:3252 | SetContainerEvidence | EvidenceSource | C | True | False | if (source == EvidenceSource::CONSTRAINT_DERIVED \|\| source == EvidenceSource::CONSTRAINT_HEURISTIC) |
| src1.6.5/rdfw.cpp:3256 | LocationSource | EvidenceSource,LocationSource | D | True | False | EvidenceSource RDFW::LocationSource(unsigned int id) const { |
| src1.6.5/rdfw.cpp:3257 | LocationSource | EvidenceSource,objectLocationSource | D | True | False | return id < objectLocationSource.size() ? objectLocationSource[id] : EvidenceSource::UNKNOWN; |
| src1.6.5/rdfw.cpp:3259 | InsideSource | EvidenceSource,InsideSource | D | True | False | EvidenceSource RDFW::InsideSource(unsigned int id) const { |
| src1.6.5/rdfw.cpp:3260 | InsideSource | EvidenceSource,objectInsideSource | D | True | False | return id < objectInsideSource.size() ? objectInsideSource[id] : EvidenceSource::UNKNOWN; |
| src1.6.5/rdfw.cpp:3262 | ContainerSource | ContainerSource,EvidenceSource | D | True | False | EvidenceSource RDFW::ContainerSource(unsigned int id) const { |
| src1.6.5/rdfw.cpp:3263 | ContainerSource | EvidenceSource,containerStateSource | D | True | False | return id < containerStateSource.size() ? containerStateSource[id] : EvidenceSource::UNKNOWN; |
| src1.6.5/rdfw.cpp:3275 | IsLocationVerified | IsLocationVerified | B | False | True | bool RDFW::IsLocationVerified(unsigned int id) const { |
| src1.6.5/rdfw.cpp:3276 | IsLocationVerified | objectLocationVerified | B | False | True | return id < objectLocationVerified.size() && objectLocationVerified[id] && |
| src1.6.5/rdfw.cpp:3277 | IsLocationVerified | DependenciesCurrent | B | False | True | DependenciesCurrent(StateField::LOCATION, id); |
| src1.6.5/rdfw.cpp:3280 | IsInsideVerified | IsInsideVerified | B | False | True | bool RDFW::IsInsideVerified(unsigned int id) const { |
| src1.6.5/rdfw.cpp:3281 | IsInsideVerified | objectInsideVerified | B | False | True | return id < objectInsideVerified.size() && objectInsideVerified[id] && |
| src1.6.5/rdfw.cpp:3282 | IsInsideVerified | DependenciesCurrent | B | False | True | DependenciesCurrent(StateField::INSIDE, id); |
| src1.6.5/rdfw.cpp:3285 | IsContainerStateVerified | IsContainerStateVerified | B | False | True | bool RDFW::IsContainerStateVerified(unsigned int id) const { |
| src1.6.5/rdfw.cpp:3286 | IsContainerStateVerified | containerStateVerified | B | False | True | return id < containerStateVerified.size() && containerStateVerified[id] && |
| src1.6.5/rdfw.cpp:3287 | IsContainerStateVerified | DependenciesCurrent | B | False | True | DependenciesCurrent(StateField::CONTAINER_STATE, id); |
| src1.6.5/rdfw.cpp:3294 | IsAbsentFromSensedLocation | hold_id,plate_id | C | True | False | hold_id == static_cast<int>(id) \|\| plate_id == static_cast<int>(id)) |
| src1.6.5/rdfw.cpp:3299 | IsAbsentFromSensedLocation | location | D | True | False | // A closed container can hide a small object at this location. |
| src1.6.5/rdfw.cpp:3422 | HoldSmallObject | plate_id | A | True | False | if (plate_id == a) |
| src1.6.5/rdfw.cpp:3424 | HoldSmallObject | hold_id | A | True | False | if (hold_id != NONE && !PutDown(hold_id)) return false; |
| src1.6.5/rdfw.cpp:3427 | HoldSmallObject | hold_id | B | False | True | else if(hold_id==a) return true; |
| src1.6.5/rdfw.cpp:3428 | HoldSmallObject | hold_id | A | True | False | if (hold_id != NONE && !PutDown(hold_id)) return false; |
| src1.6.5/rdfw.cpp:3429 | HoldSmallObject | location | A | True | False | if(location!=target_small->location && !Move(target_small->location)) return false; |
| src1.6.5/rdfw.cpp:3430 | HoldSmallObject | inside | A | True | False | if(target_small->inside==NONE) return PickUp(a); |
| src1.6.5/rdfw.cpp:3431 | HoldSmallObject | inside | A | True | False | else if(target_small->inside!=UNKNOWN)//说明小物体在容器里面 |
| src1.6.5/rdfw.cpp:3433 | HoldSmallObject | inside | A | True | False | if (!IsValidObjectId(target_small->inside)) return false; |
| src1.6.5/rdfw.cpp:3434 | HoldSmallObject | inside | A | True | False | auto target_cont = dynamic_pointer_cast<Container>(objects[target_small->inside]); |
| src1.6.5/rdfw.cpp:3436 | HoldSmallObject | isOpen | A | True | False | if(!target_cont->isOpen && !Open(target_cont->id)) return false; |
| src1.6.5/rdfw.cpp:3442 | HoldSmallObject | hold_id | B | False | True | if (hold_id == static_cast<int>(a)) { |
| src1.6.5/rdfw.cpp:3443 | HoldSmallObject | IsInsideVerified | B | False | True | if (IsInsideVerified(a)) return true; |
| src1.6.5/rdfw.cpp:3444 | HoldSmallObject | hold | D | True | False | // 初始 hold 事实可能是错的。用一次可观察动作建立本地事实；失败则清除猜测。 |
| src1.6.5/rdfw.cpp:3446 | HoldSmallObject | EvidenceSource | A | True | False | SetHold(nullptr, EvidenceSource::ACTION_FAILURE); |
| src1.6.5/rdfw.cpp:3448 | HoldSmallObject | IsInsideVerified,plate_id | B | False | True | if (plate_id == static_cast<int>(a) && !IsInsideVerified(a)) { |
| src1.6.5/rdfw.cpp:3450 | HoldSmallObject | EvidenceSource | A | True | False | SetPlate(nullptr, EvidenceSource::ACTION_FAILURE); |
| src1.6.5/rdfw.cpp:3452 | HoldSmallObject | hold_id | A | True | False | if (hold_id != a) |
| src1.6.5/rdfw.cpp:3454 | HoldSmallObject | hold_id | A | True | False | if (hold_id != NONE && !PutDown(hold_id)) return false; //如果拿着物体，先放下 |
| src1.6.5/rdfw.cpp:3455 | HoldSmallObject | plate_id | A | True | False | if (plate_id == a) |
| src1.6.5/rdfw.cpp:3463 | HoldSmallObject | location | A | True | False | if (target_small->location != UNKNOWN) |
| src1.6.5/rdfw.cpp:3465 | HoldSmallObject | location | A | True | False | if (location != target_small->location) |
| src1.6.5/rdfw.cpp:3466 | HoldSmallObject | location | A | True | False | if(Move(target_small->location)!=1) |
| src1.6.5/rdfw.cpp:3474 | HoldSmallObject | location | A | True | False | if(target_small->location == UNKNOWN ){ |
| src1.6.5/rdfw.cpp:3482 | HoldSmallObject | inside | A | True | False | if (target_small->inside == NONE\|\|target_small->inside == UNKNOWN) //这里我想了想，可能不会有UNKOWN的情况 |
| src1.6.5/rdfw.cpp:3485 | HoldSmallObject | location | A | True | False | if (target_small->location == location && PickUp(a)) return 1; |
| src1.6.5/rdfw.cpp:3488 | HoldSmallObject | location | A | True | False | if (!EnsureLocationCapacity(location)) return false; |
| src1.6.5/rdfw.cpp:3491 | HoldSmallObject | location | A | True | False | if ( posSensedFlag[location] |
| src1.6.5/rdfw.cpp:3492 | HoldSmallObject | location | A | True | False | && target_small->location == location |
| src1.6.5/rdfw.cpp:3493 | HoldSmallObject | location | A | True | False | && HasContainerAtLocation(location) |
| src1.6.5/rdfw.cpp:3495 | HoldSmallObject | location | A | True | False | unsigned int cont_id = GetContainerAtLocation(location); |
| src1.6.5/rdfw.cpp:3498 | HoldSmallObject | isOpen | A | True | False | return (cont && cont->isOpen); |
| src1.6.5/rdfw.cpp:3503 | HoldSmallObject | location | A | True | False | if (TakeOut(a, GetContainerAtLocation(location))) return 1; |
| src1.6.5/rdfw.cpp:3507 | HoldSmallObject | plate_id | A | True | False | if (plate_id == UNKNOWN && FromPlate(a)) return 1; |
| src1.6.5/rdfw.cpp:3508 | HoldSmallObject | location | C | True | False | target_small->location = UNKNOWN; |
| src1.6.5/rdfw.cpp:3509 | HoldSmallObject | EvidenceSource | A | True | False | MarkDirectLocationEvidence(a, false, EvidenceSource::ACTION_FAILURE); |
| src1.6.5/rdfw.cpp:3522 | HoldSmallObject | inside | A | True | False | int initial_cont_id=target_small->inside; |
| src1.6.5/rdfw.cpp:3525 | HoldSmallObject | inside | C | True | False | target_small->inside = UNKNOWN; |
| src1.6.5/rdfw.cpp:3528 | HoldSmallObject | inside | B | False | True | TakeOutResult result = TakeOutLogic(a,target_small->inside); |
| src1.6.5/rdfw.cpp:3534 | HoldSmallObject | inside | A | True | False | else if(result == TakeOutResult::NeedContainerLocation) {if (t >= 2)  return 0;GetBigObjectStatus(target_small->inside);} |
| src1.6.5/rdfw.cpp:3576 | TakeOutLogic | IsContainerStateVerified,isOpen | A | True | False | if (!target_cont->isOpen \|\| !IsContainerStateVerified(cont)) return false; |
| src1.6.5/rdfw.cpp:3578 | TakeOutLogic | location | A | True | False | const bool absent = HasObjectAtLocation(location, cont) && |
| src1.6.5/rdfw.cpp:3579 | TakeOutLogic | location | A | True | False | !HasObjectAtLocation(location, small); |
| src1.6.5/rdfw.cpp:3582 | TakeOutLogic | inside | A | True | False | if (small_object && small_object->inside == static_cast<int>(cont)) { |
| src1.6.5/rdfw.cpp:3584 | TakeOutLogic | inside | C | True | False | small_object->inside = UNKNOWN; |
| src1.6.5/rdfw.cpp:3586 | TakeOutLogic | EvidenceSource | A | True | False | SetInsideEvidence(small, false, EvidenceSource::SENSE); |
| src1.6.5/rdfw.cpp:3592 | TakeOutLogic | location | A | True | False | if(target_cont->location==UNKNOWN)return TakeOutResult::NeedContainerLocation; |
| src1.6.5/rdfw.cpp:3594 | TakeOutLogic | isOpen | A | True | False | if(!target_cont->isOpen) |
| src1.6.5/rdfw.cpp:3606 | TakeOutLogic | isOpen | C | True | False | target_cont->isOpen = true; |
| src1.6.5/rdfw.cpp:3608 | TakeOutLogic | EvidenceSource | A | True | False | SetContainerEvidence(cont, true, EvidenceSource::ACTION_FAILURE); |
| src1.6.5/rdfw.cpp:3640 | SolveTask_PickUp | hold_id,plate_id | B | False | True | if(hold_id==a\|\|plate_id==a) return true; |
| src1.6.5/rdfw.cpp:3646 | SolveTask_PickUp | hold_id,plate_id | B | False | True | if(hold_id==a \|\|plate_id==a) return true; |
| src1.6.5/rdfw.cpp:3655 | SolveTask_PutDown | hold_id,plate_id | B | False | True | if(hold_id!=a&&plate_id!=a) return true; |
| src1.6.5/rdfw.cpp:3661 | SolveTask_PutDown | hold_id | A | True | False | if(hold_id==a){ |
| src1.6.5/rdfw.cpp:3662 | SolveTask_PutDown | location | A | True | False | if (location < 0 \|\| !EnsureLocationCapacity(location)) return false; |
| src1.6.5/rdfw.cpp:3663 | SolveTask_PutDown | location | A | True | False | if(putdown_cons[a][location]) { |
| src1.6.5/rdfw.cpp:3669 | SolveTask_PutDown | plate_id | A | True | False | else if(plate_id==a){ |
| src1.6.5/rdfw.cpp:3670 | SolveTask_PutDown | location | A | True | False | if (location < 0 \|\| !EnsureLocationCapacity(location)) return false; |
| src1.6.5/rdfw.cpp:3671 | SolveTask_PutDown | hold_id | A | True | False | if(hold_id>0) { |
| src1.6.5/rdfw.cpp:3672 | SolveTask_PutDown | hold_id | A | True | False | if (!PutDown(hold_id)) return false; |
| src1.6.5/rdfw.cpp:3673 | SolveTask_PutDown | location | A | True | False | if(putdown_cons[a][location]) { |
| src1.6.5/rdfw.cpp:3679 | SolveTask_PutDown | location | A | True | False | if(putdown_cons[a][location]) { |
| src1.6.5/rdfw.cpp:3688 | SolveTask_PutDown | inside | B | False | True | if (stage == 1 && small->inside == NONE) return true; |
| src1.6.5/rdfw.cpp:3689 | SolveTask_PutDown | IsInsideVerified,IsLocationVerified,inside | B | False | True | if (stage == 2 && IsInsideVerified(a) && IsLocationVerified(a) && small->inside == NONE) |
| src1.6.5/rdfw.cpp:3692 | SolveTask_PutDown | location | A | True | False | if (location < 0) return false; |
| src1.6.5/rdfw.cpp:3693 | SolveTask_PutDown | location | A | True | False | if (!EnsureLocationCapacity(location)) return false; |
| src1.6.5/rdfw.cpp:3694 | SolveTask_PutDown | location | A | True | False | if (putdown_cons[a][location]) { |
| src1.6.5/rdfw.cpp:3708 | SolveTask_Goto | location | B | False | True | if(location==objects[a]->location){ |
| src1.6.5/rdfw.cpp:3711 | SolveTask_Goto | location | A | True | False | else return Move(objects[a]->location); |
| src1.6.5/rdfw.cpp:3715 | SolveTask_Goto | IsLocationVerified,location | B | False | True | if(location==objects[a]->location && IsLocationVerified(a)) return true; |
| src1.6.5/rdfw.cpp:3717 | SolveTask_Goto | location | A | True | False | if(objects[a]->location==UNKNOWN) |
| src1.6.5/rdfw.cpp:3734 | SolveTask_Goto | location | B | False | True | if(location==objects[a]->location) { |
| src1.6.5/rdfw.cpp:3736 | SolveTask_Goto | location | B | False | True | if (HasObjectAtLocation(location, a)) return true; |
| src1.6.5/rdfw.cpp:3738 | SolveTask_Goto | IsInsideVerified,inside | A | True | False | if (small && small->inside > 0 && IsInsideVerified(a) && |
| src1.6.5/rdfw.cpp:3739 | SolveTask_Goto | inside,location | A | True | False | HasObjectAtLocation(location, small->inside)) { |
| src1.6.5/rdfw.cpp:3740 | SolveTask_Goto | location | C | True | False | small->location = location; |
| src1.6.5/rdfw.cpp:3741 | SolveTask_Goto | EvidenceSource | B | False | True | MarkDirectLocationEvidence(a, true, EvidenceSource::SENSE); |
| src1.6.5/rdfw.cpp:3746 | SolveTask_Goto | location | A | True | False | else if(!Move(objects[a]->location)) |
| src1.6.5/rdfw.cpp:3754 | SolveTask_Goto | location | B | False | True | if (HasObjectAtLocation(location, a)) return true; |
| src1.6.5/rdfw.cpp:3756 | SolveTask_Goto | IsInsideVerified,inside | A | True | False | if (small && small->inside > 0 && IsInsideVerified(a) && |
| src1.6.5/rdfw.cpp:3757 | SolveTask_Goto | inside,location | A | True | False | HasObjectAtLocation(location, small->inside)) { |
| src1.6.5/rdfw.cpp:3758 | SolveTask_Goto | location | C | True | False | small->location = location; |
| src1.6.5/rdfw.cpp:3759 | SolveTask_Goto | EvidenceSource | B | False | True | MarkDirectLocationEvidence(a, true, EvidenceSource::SENSE); |
| src1.6.5/rdfw.cpp:3776 | SolveTask_Open | IsContainerStateVerified,isOpen | B | False | True | if(cnt->isOpen && (stage == 1 \|\| IsContainerStateVerified(a))) return true; |
| src1.6.5/rdfw.cpp:3782 | SolveTask_Open | IsContainerStateVerified,isOpen | B | False | True | if(cnt->isOpen && (stage == 1 \|\| IsContainerStateVerified(a))) return true; |
| src1.6.5/rdfw.cpp:3783 | SolveTask_Open | hold_id | A | True | False | if(hold_id!=NONE && !PutDown(hold_id)) return false; |
| src1.6.5/rdfw.cpp:3786 | SolveTask_Open | location | A | True | False | if (location != objects[a]->location && !Move(objects[a]->location)) return false; |
| src1.6.5/rdfw.cpp:3791 | SolveTask_Open | location | A | True | False | if(objects[a]->location==UNKNOWN) |
| src1.6.5/rdfw.cpp:3800 | SolveTask_Open | location | A | True | False | if (location != objects[a]->location) |
| src1.6.5/rdfw.cpp:3801 | SolveTask_Open | location | A | True | False | if(!Move(objects[a]->location)) |
| src1.6.5/rdfw.cpp:3810 | SolveTask_Open | isOpen | C | True | False | cnt->isOpen = true; |
| src1.6.5/rdfw.cpp:3812 | SolveTask_Open | EvidenceSource | B | False | True | SetContainerEvidence(a, true, EvidenceSource::ACTION_FAILURE); |
| src1.6.5/rdfw.cpp:3813 | SolveTask_Open | EvidenceSource | B | False | True | MarkDirectLocationEvidence(a, true, EvidenceSource::SENSE); |
| src1.6.5/rdfw.cpp:3833 | SolveTask_Close | IsContainerStateVerified,isOpen | B | False | True | if(!cnt->isOpen && (stage == 1 \|\| IsContainerStateVerified(a))) return true; |
| src1.6.5/rdfw.cpp:3839 | SolveTask_Close | IsContainerStateVerified,isOpen | B | False | True | if(!cnt->isOpen && (stage == 1 \|\| IsContainerStateVerified(a))) return true; |
| src1.6.5/rdfw.cpp:3840 | SolveTask_Close | hold_id | A | True | False | if(hold_id!=NONE && !PutDown(hold_id)) return false; |
| src1.6.5/rdfw.cpp:3843 | SolveTask_Close | location | A | True | False | if (location != objects[a]->location && !Move(objects[a]->location)) return false; |
| src1.6.5/rdfw.cpp:3849 | SolveTask_Close | location | A | True | False | if(objects[a]->location==UNKNOWN) |
| src1.6.5/rdfw.cpp:3858 | SolveTask_Close | location | A | True | False | if (location != objects[a]->location) |
| src1.6.5/rdfw.cpp:3859 | SolveTask_Close | location | A | True | False | if(!Move(objects[a]->location)) |
| src1.6.5/rdfw.cpp:3868 | SolveTask_Close | isOpen | C | True | False | cnt->isOpen = false; |
| src1.6.5/rdfw.cpp:3870 | SolveTask_Close | EvidenceSource | B | False | True | SetContainerEvidence(a, true, EvidenceSource::ACTION_FAILURE); |
| src1.6.5/rdfw.cpp:3871 | SolveTask_Close | EvidenceSource | B | False | True | MarkDirectLocationEvidence(a, true, EvidenceSource::SENSE); |
| src1.6.5/rdfw.cpp:3889 | SolveTask_Give | location | A | True | False | if(human->location==UNKNOWN) |
| src1.6.5/rdfw.cpp:3894 | SolveTask_Give | hold_id,location,plate_id | B | False | True | if(objects[a]->location==human->location && plate_id!=a && hold_id!=a) return true; |
| src1.6.5/rdfw.cpp:3913 | SolveTask_Putin | IsInsideVerified | B | False | True | if(Isinside(a,b) && (stage == 1 \|\| IsInsideVerified(a))) return true; |
| src1.6.5/rdfw.cpp:3920 | SolveTask_Putin | IsInsideVerified | B | False | True | if(Isinside(a,b) && (stage == 1 \|\| IsInsideVerified(a))) return true; |
| src1.6.5/rdfw.cpp:3925 | SolveTask_Putin | location | A | True | False | if(objects[a]->location==objects[b]->location) |
| src1.6.5/rdfw.cpp:3927 | SolveTask_Putin | location | A | True | False | if (location != target_cont->location && !Move(target_cont->location)) return false; |
| src1.6.5/rdfw.cpp:3928 | SolveTask_Putin | isOpen | A | True | False | if (target_cont->isOpen != 1 && !Open(b)) return false; |
| src1.6.5/rdfw.cpp:3935 | SolveTask_Putin | location | A | True | False | if (location != target_cont->location && !Move(target_cont->location)) return false; |
| src1.6.5/rdfw.cpp:3936 | SolveTask_Putin | isOpen | A | True | False | if (target_cont->isOpen != 1) |
| src1.6.5/rdfw.cpp:3949 | SolveTask_Putin | location | A | True | False | if(objects[b]->location==UNKNOWN) |
| src1.6.5/rdfw.cpp:3960 | SolveTask_Putin | location | A | True | False | if (location != target_cont->location) |
| src1.6.5/rdfw.cpp:3961 | SolveTask_Putin | location | A | True | False | if(!Move(target_cont->location)) |
| src1.6.5/rdfw.cpp:3969 | SolveTask_Putin | isOpen | A | True | False | if (!target_cont->isOpen) |
| src1.6.5/rdfw.cpp:3980 | SolveTask_Putin | isOpen | C | True | False | target_cont->isOpen = true; |
| src1.6.5/rdfw.cpp:3982 | SolveTask_Putin | EvidenceSource | A | True | False | SetContainerEvidence(b, true, EvidenceSource::ACTION_FAILURE); |
| src1.6.5/rdfw.cpp:4016 | SolveTask_Putin | hold_id | D | True | False | //     PutDown(hold_id); |
| src1.6.5/rdfw.cpp:4053 | SolveTask_TakeOut | location | D | True | False | // Stage 2 location facts and AskLoc replies may be misleading. A known |
| src1.6.5/rdfw.cpp:4057 | SolveTask_TakeOut | inside | B | False | True | if (stage == 1 && small->inside != target_cont->id && small->inside != UNKNOWN) |
| src1.6.5/rdfw.cpp:4065 | SolveTask_TakeOut | hold | A | True | False | if (hold!= nullptr && !PutDown(hold->id)) return false; |
| src1.6.5/rdfw.cpp:4066 | SolveTask_TakeOut | location | A | True | False | if (location != target_cont->location && !Move(target_cont->location)) return false; |
| src1.6.5/rdfw.cpp:4067 | SolveTask_TakeOut | isOpen | A | True | False | if (target_cont->isOpen != 1 && !Open(target_cont->id)) return false; |
| src1.6.5/rdfw.cpp:4071 | SolveTask_TakeOut | location | A | True | False | if(target_cont->location==UNKNOWN){GetBigObjectStatus(b);if(!IsKeepingGoing(task_index)) return false;} |
| src1.6.5/rdfw.cpp:4072 | SolveTask_TakeOut | hold | A | True | False | if (hold!= nullptr && !PutDown(hold->id)) return false; |
| src1.6.5/rdfw.cpp:4077 | SolveTask_TakeOut | location | A | True | False | if (location != target_cont->location) |
| src1.6.5/rdfw.cpp:4078 | SolveTask_TakeOut | location | A | True | False | if(!Move(target_cont->location)) |
| src1.6.5/rdfw.cpp:4091 | SolveTask_TakeOut | IsInsideVerified | B | False | True | if (!Isinside(a,b) && IsInsideVerified(a)) return true; |
| src1.6.5/rdfw.cpp:4120 | SolveTask_PutOn | inside,location | A | True | False | if(small && small->inside==NONE && small->location==objects[b]->location && |
| src1.6.5/rdfw.cpp:4121 | SolveTask_PutOn | hold_id,plate_id | B | False | True | plate_id!=a && hold_id!=a && |
| src1.6.5/rdfw.cpp:4122 | SolveTask_PutOn | IsInsideVerified,IsLocationVerified | B | False | True | (stage == 1 \|\| (IsInsideVerified(a) && IsLocationVerified(a) && IsLocationVerified(b)))) |
| src1.6.5/rdfw.cpp:4125 | SolveTask_PutOn | location | A | True | False | if(objects[b]->location==UNKNOWN) |
| src1.6.5/rdfw.cpp:4135 | SolveTask_PutOn | location | A | True | False | if (location != objects[b]->location) |
| src1.6.5/rdfw.cpp:4137 | SolveTask_PutOn | location | A | True | False | if(!Move(objects[b]->location)) |
| src1.6.5/rdfw.cpp:4145 | SolveTask_PutOn | IsLocationVerified,location | A | True | False | if (stage == 2 && (!IsLocationVerified(b) \|\| objects[b]->location != location)) { |
| src1.6.5/rdfw.cpp:4147 | SolveTask_PutOn | location | A | True | False | if(!HasObjectAtLocation(location, b)) { |
| src1.6.5/rdfw.cpp:4353 | remove_if | location | A | True | False | int loc = (objects[id] ? objects[id]->location : UNKNOWN); |
| src1.6.5/rdfw.cpp:4391 | ExecuteMultiGotoAggregation | location | A | True | False | int loc = (objects[id] ? objects[id]->location : UNKNOWN); |
| src1.6.5/rdfw.cpp:4420 | ExecuteMultiGotoAggregation | location | A | True | False | int loc = (objects[id] ? objects[id]->location : UNKNOWN); |
| src1.6.5/rdfw.cpp:4456 | ExecuteMultiGotoAggregation | location | A | True | False | int loc = objects[id]->location; |
| src1.6.5/rdfw.cpp:4464 | ExecuteMultiGotoAggregation | location | A | True | False | int loc = objects[id]->location; |
| src1.6.5/rdfw.cpp:4472 | ExecuteMultiGotoAggregation | location | A | True | False | int loc = objects[id]->location; |
| src1.6.5/rdfw.cpp:4536 | ExecuteMultiGotoAggregation | location | A | True | False | int loc = objects[id]->location; |
| src1.6.5/rdfw.cpp:4559 | ExecuteMultiGotoAggregation | location | A | True | False | cout << "[MultiGoto] location " << loc << " has " << count << " small objects" << endl; |
| src1.6.5/rdfw.cpp:4595 | ExecuteMultiGotoAggregation | location | A | True | False | int loc = objects[big_id]->location; |
| src1.6.5/rdfw.cpp:4627 | ExecuteMultiGotoAggregation | location | A | True | False | LOG(YELLOW "[MultiGoto] No optimal location found, using first available: %d\n" RESET, chosen_loc); |
| src1.6.5/rdfw.cpp:4635 | ExecuteMultiGotoAggregation | location | A | True | False | LOG(YELLOW "[MultiGoto] No optimal location found, using first available: %d\n" RESET, loc); |
| src1.6.5/rdfw.cpp:4644 | ExecuteMultiGotoAggregation | location | A | True | False | LOG(RED "[MultiGoto] ERROR: No valid location found! chosen_loc=%d, rightlocation[%d]=%d\n" RESET, |
| src1.6.5/rdfw.cpp:4647 | ExecuteMultiGotoAggregation | location | A | True | False | chosen_loc = location; |
| src1.6.5/rdfw.cpp:4648 | ExecuteMultiGotoAggregation | location | A | True | False | LOG(YELLOW "[MultiGoto] Using current location as fallback: %d\n" RESET, chosen_loc); |
| src1.6.5/rdfw.cpp:4653 | ExecuteMultiGotoAggregation | location | D | True | False | // chosen_loc is a location, while SolveTask_PutOn expects an object id |
| src1.6.5/rdfw.cpp:4654 | ExecuteMultiGotoAggregation | location | D | True | False | // whose location is the destination.  Keep the legacy hub selection |
| src1.6.5/rdfw.cpp:4655 | ExecuteMultiGotoAggregation | location | D | True | False | // unchanged and map that location to a stable representative object. |
| src1.6.5/rdfw.cpp:4658 | ExecuteMultiGotoAggregation | location | A | True | False | if (!objects[i] \|\| objects[i]->location != chosen_loc) continue; |
| src1.6.5/rdfw.cpp:4668 | ExecuteMultiGotoAggregation | location | C | True | False | LOG(GREEN "[MultiGoto] hub location=%d representative_object=%u\n" RESET, |
| src1.6.5/rdfw.cpp:4680 | ExecuteMultiGotoAggregation | location | A | True | False | int loc = objects[id]->location; |
| src1.6.5/rdfw.cpp:4698 | ExecuteMultiGotoAggregation | location | A | True | False | if (location != chosen_loc) { |
| src1.6.5/rdfw.cpp:4712 | ExecuteMultiGotoAggregation | hold,plate | D | True | False | // 护栏：hold/plate 不在集合且跨区会触发 move 约束时，先就地处理 |
| src1.6.5/rdfw.cpp:4713 | ExecuteMultiGotoAggregation | hold_id | A | True | False | if (IsValidObjectId(hold_id) && !in_set(hold_id) && |
| src1.6.5/rdfw.cpp:4714 | ExecuteMultiGotoAggregation | hold_id | A | True | False | chosen_loc >= 0 && hold_id < static_cast<int>(move_cons.size()) && |
| src1.6.5/rdfw.cpp:4715 | ExecuteMultiGotoAggregation | hold_id | A | True | False | static_cast<std::size_t>(chosen_loc) < move_cons[hold_id].size() && |
| src1.6.5/rdfw.cpp:4716 | ExecuteMultiGotoAggregation | hold_id | A | True | False | move_cons[hold_id][chosen_loc]) { |
| src1.6.5/rdfw.cpp:4717 | ExecuteMultiGotoAggregation | hold_id | A | True | False | PutDown(hold_id); |
| src1.6.5/rdfw.cpp:4719 | ExecuteMultiGotoAggregation | plate_id | A | True | False | if (IsValidObjectId(plate_id) && !in_set(plate_id) && |
| src1.6.5/rdfw.cpp:4720 | ExecuteMultiGotoAggregation | plate_id | A | True | False | chosen_loc >= 0 && plate_id < static_cast<int>(move_cons.size()) && |
| src1.6.5/rdfw.cpp:4721 | ExecuteMultiGotoAggregation | plate_id | A | True | False | static_cast<std::size_t>(chosen_loc) < move_cons[plate_id].size() && |
| src1.6.5/rdfw.cpp:4722 | ExecuteMultiGotoAggregation | plate_id | A | True | False | move_cons[plate_id][chosen_loc]) { |
| src1.6.5/rdfw.cpp:4723 | ExecuteMultiGotoAggregation | hold_id | A | True | False | if (hold_id > 0) PutDown(hold_id); |
| src1.6.5/rdfw.cpp:4724 | ExecuteMultiGotoAggregation | plate_id | A | True | False | FromPlate(plate_id); |
| src1.6.5/rdfw.cpp:4725 | ExecuteMultiGotoAggregation | plate_id | A | True | False | PutDown(plate_id); |
| src1.6.5/rdfw.cpp:4728 | ExecuteMultiGotoAggregation | hold,plate | D | True | False | // 若 hold/plate 在集合里，优先处理 |
| src1.6.5/rdfw.cpp:4733 | ExecuteMultiGotoAggregation | hold_id | A | True | False | if (hold_id  > 0) promote_front(hold_id); |
| src1.6.5/rdfw.cpp:4734 | ExecuteMultiGotoAggregation | plate_id | A | True | False | if (plate_id > 0) promote_front(plate_id); |
| src1.6.5/rdfw.cpp:4740 | stable_sort | location | A | True | False | int da = (sa && sa->location == chosen_loc) ? 0 : 1; |
| src1.6.5/rdfw.cpp:4741 | stable_sort | location | A | True | False | int db = (sb && sb->location == chosen_loc) ? 0 : 1; |
| src1.6.5/rdfw.cpp:4780 | ExecuteMultiGotoAggregation | location | A | True | False | if (location != chosen_loc) { |
| src1.6.5/rdfw.cpp:4842 | ParseAskLocationReply | inside | A | True | False | "^\\s*(at\|inside)\\s*\\(\\s*([0-9]+)\\s*,\\s*([0-9]+)\\s*\\)\\s*$"); |
| src1.6.5/rdfw.cpp:4852 | ParseAskLocationReply | inside | A | True | False | if (relation == "inside" && reply_target > static_cast<int>(MAX_OBJECT_ID)) |
| src1.6.5/rdfw.cpp:4877 | GetSmallObjectStatus | inside | A | True | False | if (relation == "inside") { |
| src1.6.5/rdfw.cpp:4894 | GetSmallObjectStatus | IsInsideVerified | A | True | False | if (IsInsideVerified(a)) { |
| src1.6.5/rdfw.cpp:4895 | GetSmallObjectStatus | inside | A | True | False | const int answer_inside = chosen_relation == "inside" |
| src1.6.5/rdfw.cpp:4897 | GetSmallObjectStatus | inside | A | True | False | if (small->inside != answer_inside) { |
| src1.6.5/rdfw.cpp:4898 | GetSmallObjectStatus | inside | A | True | False | LOG(YELLOW "AskLoc(%u) conflicts with trusted inside fact; ignored\n" RESET, a); |
| src1.6.5/rdfw.cpp:4902 | GetSmallObjectStatus | IsLocationVerified | A | True | False | if (IsLocationVerified(a)) { |
| src1.6.5/rdfw.cpp:4903 | GetSmallObjectStatus | inside | A | True | False | const int answer_location = chosen_relation == "inside" |
| src1.6.5/rdfw.cpp:4904 | GetSmallObjectStatus | location | A | True | False | ? objects[chosen_target]->location : static_cast<int>(chosen_target); |
| src1.6.5/rdfw.cpp:4905 | GetSmallObjectStatus | location | A | True | False | if (objects[a]->location != answer_location) { |
| src1.6.5/rdfw.cpp:4906 | GetSmallObjectStatus | location | A | True | False | LOG(YELLOW "AskLoc(%u) conflicts with trusted location; ignored\n" RESET, a); |
| src1.6.5/rdfw.cpp:4910 | GetSmallObjectStatus | IsInsideVerified,IsLocationVerified | A | True | False | if (IsInsideVerified(a) && IsLocationVerified(a)) return true; |
| src1.6.5/rdfw.cpp:4912 | GetSmallObjectStatus | inside | A | True | False | const int answer_inside = chosen_relation == "inside" |
| src1.6.5/rdfw.cpp:4914 | GetSmallObjectStatus | inside | A | True | False | const int answer_location = chosen_relation == "inside" |
| src1.6.5/rdfw.cpp:4915 | GetSmallObjectStatus | location | A | True | False | ? objects[chosen_target]->location : static_cast<int>(chosen_target); |
| src1.6.5/rdfw.cpp:4916 | GetSmallObjectStatus | IsInsideVerified | A | True | False | const bool inside_conflict = !IsInsideVerified(a) && |
| src1.6.5/rdfw.cpp:4918 | GetSmallObjectStatus | EvidenceSource | A | True | False | EvidenceSource::ASK_ANSWER); |
| src1.6.5/rdfw.cpp:4919 | GetSmallObjectStatus | IsLocationVerified | A | True | False | const bool location_conflict = !IsLocationVerified(a) && |
| src1.6.5/rdfw.cpp:4922 | GetSmallObjectStatus | EvidenceSource | A | True | False | EvidenceSource::ASK_ANSWER); |
| src1.6.5/rdfw.cpp:4924 | GetSmallObjectStatus | inside | A | True | False | if (small->inside > 0 && static_cast<size_t>(small->inside) < objects.size()) { |
| src1.6.5/rdfw.cpp:4925 | GetSmallObjectStatus | inside | A | True | False | auto old_cont = dynamic_pointer_cast<Container>(objects[small->inside]); |
| src1.6.5/rdfw.cpp:4929 | GetSmallObjectStatus | inside | A | True | False | if (chosen_relation == "inside") { |
| src1.6.5/rdfw.cpp:4932 | GetSmallObjectStatus | location | A | True | False | if (cont->location == UNKNOWN) GetBigObjectStatus(cont->id); |
| src1.6.5/rdfw.cpp:4933 | GetSmallObjectStatus | location | C | True | False | small->location = cont->location; |
| src1.6.5/rdfw.cpp:4934 | GetSmallObjectStatus | inside | C | True | False | small->inside = cont->id; |
| src1.6.5/rdfw.cpp:4942 | GetSmallObjectStatus | location | C | True | False | small->location = static_cast<int>(chosen_target); |
| src1.6.5/rdfw.cpp:4943 | GetSmallObjectStatus | inside | C | True | False | small->inside = NONE; |
| src1.6.5/rdfw.cpp:4946 | GetSmallObjectStatus | IsLocationVerified | A | True | False | if (!IsLocationVerified(a)) |
| src1.6.5/rdfw.cpp:4947 | GetSmallObjectStatus | EvidenceSource | A | True | False | MarkDirectLocationEvidence(a, false, EvidenceSource::ASK_ANSWER); |
| src1.6.5/rdfw.cpp:4948 | GetSmallObjectStatus | IsInsideVerified | A | True | False | if (!IsInsideVerified(a)) |
| src1.6.5/rdfw.cpp:4949 | GetSmallObjectStatus | EvidenceSource | A | True | False | SetInsideEvidence(a, false, EvidenceSource::ASK_ANSWER); |
| src1.6.5/rdfw.cpp:4952 | GetSmallObjectStatus | location | A | True | False | if (small->location >= 0) { |
| src1.6.5/rdfw.cpp:4953 | GetSmallObjectStatus | location | A | True | False | if (!EnsureLocationCapacity(small->location)) return false; |
| src1.6.5/rdfw.cpp:4954 | GetSmallObjectStatus | location | A | True | False | posCorrectFlag[small->location] = false; |
| src1.6.5/rdfw.cpp:4981 | GetBigObjectStatus | location | A | True | False | LOG(YELLOW "AskLoc(%u) produced no usable bounded location reply\n" RESET, a); |
| src1.6.5/rdfw.cpp:4984 | GetBigObjectStatus | IsLocationVerified | A | True | False | if (IsLocationVerified(a)) { |
| src1.6.5/rdfw.cpp:4985 | GetBigObjectStatus | location | A | True | False | if (objects[a]->location != static_cast<int>(chosen_location)) { |
| src1.6.5/rdfw.cpp:4986 | GetBigObjectStatus | location | A | True | False | LOG(YELLOW "AskLoc(%u) conflicts with trusted location; ignored\n" RESET, a); |
| src1.6.5/rdfw.cpp:4994 | GetBigObjectStatus | EvidenceSource | A | True | False | static_cast<int>(chosen_location), EvidenceSource::ASK_ANSWER); |
| src1.6.5/rdfw.cpp:4995 | GetBigObjectStatus | location | C | True | False | objects[a]->location = static_cast<int>(chosen_location); |
| src1.6.5/rdfw.cpp:5001 | GetBigObjectStatus | IsLocationVerified | A | True | False | if (IsLocationVerified(item->id)) continue; |
| src1.6.5/rdfw.cpp:5002 | GetBigObjectStatus | location | C | True | False | item->location = cont->location; |
| src1.6.5/rdfw.cpp:5003 | GetBigObjectStatus | EvidenceSource | A | True | False | MarkDirectLocationEvidence(item->id, false, EvidenceSource::ASK_ANSWER); |
| src1.6.5/rdfw.cpp:5007 | GetBigObjectStatus | EvidenceSource | A | True | False | MarkDirectLocationEvidence(a, false, EvidenceSource::ASK_ANSWER); |
| src1.6.5/rdfw.cpp:5025 | AskLoc | inside | A | True | False | if (small && small->inside > 0) |
| src1.6.5/rdfw.cpp:5026 | AskLoc | inside | A | True | False | str = "inside(" + std::to_string(a) + "," + |
| src1.6.5/rdfw.cpp:5027 | AskLoc | inside | A | True | False | std::to_string(small->inside) + ")"; |
| src1.6.5/rdfw.cpp:5028 | AskLoc | location | A | True | False | else if (objects[a]->location >= 0) |
| src1.6.5/rdfw.cpp:5030 | AskLoc | location | A | True | False | std::to_string(objects[a]->location) + ")"; |
| src1.6.5/rdfw.cpp:5047 | Sense | location | D | True | False | // Sense 只观察当前位置，不应把 location 当作对象 ID，也不应隐式开关门。 |
| src1.6.5/rdfw.cpp:5057 | SenseCurrentLocationOnly | location | C | True | False | int curr_loc = location; |
| src1.6.5/rdfw.cpp:5095 | SenseCurrentLocationOnly | location | C | True | False | if (objects[id]->location != curr_loc) |
| src1.6.5/rdfw.cpp:5096 | SenseCurrentLocationOnly | location | C | True | False | InvalidateSenseAtLocation(objects[id]->location); |
| src1.6.5/rdfw.cpp:5097 | SenseCurrentLocationOnly | location | C | True | False | objects[id]->location = curr_loc; |
| src1.6.5/rdfw.cpp:5098 | SenseCurrentLocationOnly | EvidenceSource | C | True | False | MarkDirectLocationEvidence(id, true, EvidenceSource::SENSE); |
| src1.6.5/rdfw.cpp:5110 | SenseCurrentLocationOnly | location | C | True | False | LOG("[SenseCurrentLocationOnly] Container %d detected at location %d", id, curr_loc); |
| src1.6.5/rdfw.cpp:5112 | SenseCurrentLocationOnly | location | C | True | False | LOG("[SenseCurrentLocationOnly] Object %d detected at location %d", id, curr_loc); |
| src1.6.5/rdfw.cpp:5117 | SenseCurrentLocationOnly | inside | D | True | False | // 让位置证据与 inside 关系保持一致。开放容器与其内容同时可见时， |
| src1.6.5/rdfw.cpp:5123 | SenseCurrentLocationOnly | hold_id,plate_id | C | True | False | if (!small \|\| static_cast<int>(id) == hold_id \|\| static_cast<int>(id) == plate_id) continue; |
| src1.6.5/rdfw.cpp:5131 | SenseCurrentLocationOnly | isOpen | C | True | False | visible_container_is_open = visible_container && visible_container->isOpen != 0; |
| src1.6.5/rdfw.cpp:5135 | SenseCurrentLocationOnly | inside | C | True | False | small->inside == static_cast<int>(sensed_container_id) && visible_container_is_open; |
| src1.6.5/rdfw.cpp:5137 | SenseCurrentLocationOnly | EvidenceSource | C | True | False | SetInsideEvidence(id, false, EvidenceSource::SENSE); |
| src1.6.5/rdfw.cpp:5141 | SenseCurrentLocationOnly | inside | C | True | False | if (small->inside > 0 && static_cast<size_t>(small->inside) < objects.size()) { |
| src1.6.5/rdfw.cpp:5142 | SenseCurrentLocationOnly | inside | C | True | False | auto old_container = dynamic_pointer_cast<Container>(objects[small->inside]); |
| src1.6.5/rdfw.cpp:5145 | SenseCurrentLocationOnly | inside | C | True | False | small->inside = NONE; |
| src1.6.5/rdfw.cpp:5146 | SenseCurrentLocationOnly | EvidenceSource | C | True | False | SetInsideEvidence(id, true, EvidenceSource::SENSE); |
| src1.6.5/rdfw.cpp:5163 | SenseCurrentLocationOnly | isOpen | C | True | False | container_is_open = cont->isOpen == 1; |
| src1.6.5/rdfw.cpp:5171 | SenseCurrentLocationOnly | hold_id,plate_id | C | True | False | if (static_cast<int>(i) == hold_id \|\| static_cast<int>(i) == plate_id) continue; |
| src1.6.5/rdfw.cpp:5172 | SenseCurrentLocationOnly | location | C | True | False | if (objects[i]->location == curr_loc) { |
| src1.6.5/rdfw.cpp:5180 | SenseCurrentLocationOnly | location | C | True | False | objects[id]->location = UNKNOWN; |
| src1.6.5/rdfw.cpp:5181 | SenseCurrentLocationOnly | EvidenceSource | C | True | False | MarkDirectLocationEvidence(id, false, EvidenceSource::SENSE); |
| src1.6.5/rdfw.cpp:5183 | SenseCurrentLocationOnly | location | C | True | False | LOG(YELLOW "[SenseCurrentLocationOnly] Object id=%u expected at %d but not sensed, set location UNKNOWN\n" RESET, id, curr_loc); |
| src1.6.5/rdfw.cpp:5192 | SenseCurrentLocationOnly | inside | C | True | False | if (small && small->inside == sensed_container_id) { |
| src1.6.5/rdfw.cpp:5197 | SenseCurrentLocationOnly | location | C | True | False | objects[id]->location = UNKNOWN; |
| src1.6.5/rdfw.cpp:5198 | SenseCurrentLocationOnly | EvidenceSource | C | True | False | MarkDirectLocationEvidence(id, false, EvidenceSource::SENSE); |
| src1.6.5/rdfw.cpp:5200 | SenseCurrentLocationOnly | location | C | True | False | LOG(YELLOW "[SenseCurrentLocationOnly] Object id=%u expected at %d but not sensed, set location UNKNOWN\n" RESET, id, curr_loc); |
| src1.6.5/rdfw.cpp:5208 | GetLocationSensedInfo | location | C | True | False | const RDFW::LocationSensedInfo& RDFW::GetLocationSensedInfo(int location) const { |
| src1.6.5/rdfw.cpp:5210 | GetLocationSensedInfo | location | C | True | False | if (location >= 0 && location < locationSensedObjects.size()) { |
| src1.6.5/rdfw.cpp:5211 | GetLocationSensedInfo | location | C | True | False | return locationSensedObjects[location]; |
| src1.6.5/rdfw.cpp:5216 | HasObjectAtLocation | location | A | True | False | bool RDFW::HasObjectAtLocation(int location, unsigned int object_id) const { |
| src1.6.5/rdfw.cpp:5217 | HasObjectAtLocation | location | A | True | False | if (location >= 0 && location < locationSensedObjects.size()) { |
| src1.6.5/rdfw.cpp:5218 | HasObjectAtLocation | location | A | True | False | const auto& info = locationSensedObjects[location]; |
| src1.6.5/rdfw.cpp:5226 | HasContainerAtLocation | location | A | True | False | bool RDFW::HasContainerAtLocation(int location) const { |
| src1.6.5/rdfw.cpp:5227 | HasContainerAtLocation | location | A | True | False | if (location >= 0 && location < locationSensedObjects.size()) { |
| src1.6.5/rdfw.cpp:5228 | HasContainerAtLocation | location | A | True | False | return locationSensedObjects[location].has_container; |
| src1.6.5/rdfw.cpp:5233 | GetObjectsAtLocation | location | A | True | False | vector<unsigned int> RDFW::GetObjectsAtLocation(int location) const { |
| src1.6.5/rdfw.cpp:5234 | GetObjectsAtLocation | location | A | True | False | if (location >= 0 && location < locationSensedObjects.size()) { |
| src1.6.5/rdfw.cpp:5235 | GetObjectsAtLocation | location | A | True | False | return locationSensedObjects[location].object_ids; |
| src1.6.5/rdfw.cpp:5240 | GetContainerAtLocation | location | A | True | False | unsigned int RDFW::GetContainerAtLocation(int location) const { |
| src1.6.5/rdfw.cpp:5241 | GetContainerAtLocation | location | A | True | False | if (location >= 0 && location < locationSensedObjects.size()) { |
| src1.6.5/rdfw.cpp:5242 | GetContainerAtLocation | location | A | True | False | return locationSensedObjects[location].container_id; |
| src1.6.5/rdfw.cpp:5264 | sense | location | C | False | True | if (objects[id]->location != location) { |
| src1.6.5/rdfw.cpp:5265 | sense | location | C | False | True | objects[id]->location = location; |
| src1.6.5/rdfw.cpp:5269 | sense | location | C | False | True | sp->location = location; |
| src1.6.5/rdfw.cpp:5270 | sense | IsInsideVerified | C | False | True | const bool entailed = IsInsideVerified(sp->id); |
| src1.6.5/rdfw.cpp:5272 | sense | EvidenceSource | C | False | True | entailed ? EvidenceSource::CONSTRAINT_DERIVED |
| src1.6.5/rdfw.cpp:5273 | sense | EvidenceSource | C | False | True | : EvidenceSource::CONSTRAINT_HEURISTIC); |
| src1.6.5/rdfw.cpp:5277 | sense | inside | D | True | False | // 小物体分支无需强制改 inside，这里保持原有逻辑不动 |
| src1.6.5/rdfw.cpp:5279 | sense | EvidenceSource | C | False | True | MarkDirectLocationEvidence(id, true, EvidenceSource::SENSE); |
| src1.6.5/rdfw.cpp:5280 | sense | location | C | False | True | if (objects[id]->unable_site == location) objects[id]->unable_site = UNKNOWN; |
| src1.6.5/rdfw.cpp:5311 | Isinside | inside | A | True | False | if(small->inside==objects[b]->id) return true; |
| src1.6.5/rdfw.cpp:5331 | IsKeepingGoing | inside | A | True | False | if(small->inside==t.Y[0]->id){ //如果任务没有满足 |
| src1.6.5/rdfw.cpp:5332 | IsKeepingGoing | location | A | True | False | const int target_location = t.Y[0]->location; |
| src1.6.5/rdfw.cpp:5343 | IsKeepingGoing | inside | A | True | False | if(small->inside!=t.Y[0]->id) //如果任务没有满足 |
| src1.6.5/rdfw.cpp:5345 | IsKeepingGoing | location | A | True | False | const int target_location = t.Y[0]->location; |
| src1.6.5/rdfw.cpp:5350 | IsKeepingGoing | location | A | True | False | if(t.X[0]->location!=target_location) t.risk+=goto_cons[target_location]; |
| src1.6.5/rdfw.cpp:5356 | IsKeepingGoing | location | A | True | False | const int target_location = t.Y[0]->location; |
| src1.6.5/rdfw.cpp:5361 | IsKeepingGoing | location | A | True | False | if(t.X[0]->location!=target_location) t.risk+=goto_cons[target_location]; |
| src1.6.5/rdfw.cpp:5365 | IsKeepingGoing | location | A | True | False | else if(t.behave=="goto" && t.X[0]->location >= 0 && |
| src1.6.5/rdfw.cpp:5366 | IsKeepingGoing | location | A | True | False | EnsureLocationCapacity(t.X[0]->location)) t.risk+=goto_cons[t.X[0]->location]; |
| src1.6.5/rdfw.cpp:5369 | IsKeepingGoing | location | A | True | False | if (t.X[0]->location >= 0 && EnsureLocationCapacity(t.X[0]->location)) |
| src1.6.5/rdfw.cpp:5370 | IsKeepingGoing | location | A | True | False | t.risk+=goto_cons[t.X[0]->location]; |
| src1.6.5/rdfw.cpp:5374 | IsKeepingGoing | location | A | True | False | if (t.X[0]->location >= 0 && EnsureLocationCapacity(t.X[0]->location)) |
| src1.6.5/rdfw.cpp:5375 | IsKeepingGoing | location | A | True | False | t.risk+=goto_cons[t.X[0]->location]; |
| src1.6.5/rdfw.cpp:5383 | IsKeepingGoing | location | A | True | False | if (human && human->location >= 0) { |
| src1.6.5/rdfw.cpp:5384 | IsKeepingGoing | location | A | True | False | if (!EnsureLocationCapacity(human->location)) return false; |
| src1.6.5/rdfw.cpp:5385 | IsKeepingGoing | location | A | True | False | t.risk+=move_cons[t.X[0]->id][human->location]; |
| src1.6.5/rdfw.cpp:5386 | IsKeepingGoing | location | A | True | False | if(t.X[0]->location!=human->location) t.risk+=goto_cons[human->location]; |
| src1.6.5/rdfw.cpp:5487 | ReconcileLocationRelation | inside | C | True | False | if (!small \|\| small->inside <= 0) return; |
| src1.6.5/rdfw.cpp:5488 | ReconcileLocationRelation | inside | C | True | False | auto container = dynamic_pointer_cast<Container>(GetObject(small->inside)); |
| src1.6.5/rdfw.cpp:5489 | ReconcileLocationRelation | location | C | True | False | if (container && container->location != UNKNOWN && small->location != UNKNOWN && |
| src1.6.5/rdfw.cpp:5490 | ReconcileLocationRelation | location | C | True | False | container->location != small->location) { |
| src1.6.5/rdfw.cpp:5492 | ReconcileLocationRelation | inside | C | True | False | small->inside = UNKNOWN; |
| src1.6.5/rdfw.cpp:5493 | ReconcileLocationRelation | EvidenceSource | C | True | False | SetInsideEvidence(small->id, false, EvidenceSource::EXPLICIT_INFO); |
| src1.6.5/rdfw.cpp:5497 | declaration/inline | location | D | True | False | // A successful container action proves co-location even when the initial |
| src1.6.5/rdfw.cpp:5498 | declaration/inline | location | D | True | False | // location was misleading. Its contents inherit that location only with the |
| src1.6.5/rdfw.cpp:5499 | declaration/inline | inside | D | True | False | // strength of their own inside evidence. |
| src1.6.5/rdfw.cpp:5501 | ConfirmContainerLocation | location | C | True | False | if (container->location != location) |
| src1.6.5/rdfw.cpp:5502 | ConfirmContainerLocation | location | C | True | False | InvalidateSenseAtLocation(container->location); |
| src1.6.5/rdfw.cpp:5503 | ConfirmContainerLocation | location | C | True | False | container->location = location; |
| src1.6.5/rdfw.cpp:5506 | ConfirmContainerLocation | inside | C | True | False | if (!item \|\| item->inside != container->id) continue; |
| src1.6.5/rdfw.cpp:5507 | ConfirmContainerLocation | IsInsideVerified,IsLocationVerified | C | True | False | if (IsLocationVerified(item->id) && !IsInsideVerified(item->id) && |
| src1.6.5/rdfw.cpp:5508 | ConfirmContainerLocation | location | C | True | False | item->location != location) continue; |
| src1.6.5/rdfw.cpp:5509 | ConfirmContainerLocation | location | C | True | False | item->location = location; |
| src1.6.5/rdfw.cpp:5510 | ConfirmContainerLocation | IsInsideVerified | C | True | False | const bool inside_verified = IsInsideVerified(item->id); |
| src1.6.5/rdfw.cpp:5511 | ConfirmContainerLocation | inside | D | True | False | // The action verifies the container, not an inside relation that was |
| src1.6.5/rdfw.cpp:5514 | ConfirmContainerLocation | EvidenceSource | C | True | False | const EvidenceSource source = |
| src1.6.5/rdfw.cpp:5515 | ConfirmContainerLocation | EvidenceSource,InsideSource | C | True | False | InsideSource(item->id) == EvidenceSource::CONSTRAINT_DERIVED |
| src1.6.5/rdfw.cpp:5516 | ConfirmContainerLocation | EvidenceSource | C | True | False | ? EvidenceSource::CONSTRAINT_DERIVED |
| src1.6.5/rdfw.cpp:5517 | ConfirmContainerLocation | EvidenceSource | C | True | False | : EvidenceSource::RELATION_DERIVED; |
| src1.6.5/rdfw.cpp:5540 | TakeOut | inside | C | True | False | small->inside = NONE; |
| src1.6.5/rdfw.cpp:5541 | TakeOut | location | C | True | False | small->location = location; |
| src1.6.5/rdfw.cpp:5543 | TakeOut | isOpen | C | True | False | cont->isOpen=1; |
| src1.6.5/rdfw.cpp:5548 | TakeOut | EvidenceSource | C | True | False | SetInsideEvidence(a, true, EvidenceSource::ACTION_SUCCESS); |
| src1.6.5/rdfw.cpp:5550 | TakeOut | EvidenceSource | C | True | False | SetContainerEvidence(b, true, EvidenceSource::ACTION_SUCCESS); |
| src1.6.5/rdfw.cpp:5551 | TakeOut | location | C | True | False | InvalidateSenseAtLocation(location); |
| src1.6.5/rdfw.cpp:5578 | PutIn | inside | C | True | False | small->inside = b; |
| src1.6.5/rdfw.cpp:5580 | PutIn | location | C | True | False | small->location = location; |
| src1.6.5/rdfw.cpp:5587 | PutIn | isOpen | C | True | False | cont->isOpen=1; |
| src1.6.5/rdfw.cpp:5591 | PutIn | EvidenceSource | C | True | False | SetInsideEvidence(a, true, EvidenceSource::ACTION_SUCCESS); |
| src1.6.5/rdfw.cpp:5593 | PutIn | EvidenceSource | C | True | False | SetContainerEvidence(b, true, EvidenceSource::ACTION_SUCCESS); |
| src1.6.5/rdfw.cpp:5594 | PutIn | location | C | True | False | InvalidateSenseAtLocation(location); |
| src1.6.5/rdfw.cpp:5617 | Close | isOpen | C | True | False | container->isOpen = false; |
| src1.6.5/rdfw.cpp:5619 | Close | EvidenceSource | C | True | False | SetContainerEvidence(a, true, EvidenceSource::ACTION_SUCCESS); |
| src1.6.5/rdfw.cpp:5620 | Close | location | C | True | False | InvalidateSenseAtLocation(location); |
| src1.6.5/rdfw.cpp:5643 | Open | isOpen | C | True | False | container->isOpen = true; |
| src1.6.5/rdfw.cpp:5645 | Open | EvidenceSource | C | True | False | SetContainerEvidence(a, true, EvidenceSource::ACTION_SUCCESS); |
| src1.6.5/rdfw.cpp:5646 | Open | location | C | True | False | InvalidateSenseAtLocation(location); |
| src1.6.5/rdfw.cpp:5672 | FromPlate | EvidenceSource | C | True | False | SetInsideEvidence(a, true, EvidenceSource::ACTION_SUCCESS); |
| src1.6.5/rdfw.cpp:5673 | FromPlate | location | C | True | False | InvalidateSenseAtLocation(location); |
| src1.6.5/rdfw.cpp:5697 | ToPlate | EvidenceSource | C | True | False | SetInsideEvidence(a, true, EvidenceSource::ACTION_SUCCESS); |
| src1.6.5/rdfw.cpp:5698 | ToPlate | location | C | True | False | InvalidateSenseAtLocation(location); |
| src1.6.5/rdfw.cpp:5722 | PutDown | location | C | True | False | small->location = location; |
| src1.6.5/rdfw.cpp:5723 | PutDown | inside | C | True | False | small->inside = NONE; |
| src1.6.5/rdfw.cpp:5727 | PutDown | EvidenceSource | C | True | False | SetInsideEvidence(a, true, EvidenceSource::ACTION_SUCCESS); |
| src1.6.5/rdfw.cpp:5728 | PutDown | location | C | True | False | InvalidateSenseAtLocation(location); |
| src1.6.5/rdfw.cpp:5731 | PutDown | location | C | True | False | if (location >= 0 && EnsureLocationCapacity(location)) |
| src1.6.5/rdfw.cpp:5732 | PutDown | location | C | True | False | putdown_cons[a][location]=0; |
| src1.6.5/rdfw.cpp:5754 | PickUp | location | C | True | False | small->location = location; |
| src1.6.5/rdfw.cpp:5755 | PickUp | inside | C | True | False | small->inside = NONE; |
| src1.6.5/rdfw.cpp:5757 | PickUp | EvidenceSource | C | True | False | SetInsideEvidence(a, true, EvidenceSource::ACTION_SUCCESS); |
| src1.6.5/rdfw.cpp:5758 | PickUp | location | C | True | False | InvalidateSenseAtLocation(location); |
| src1.6.5/rdfw.cpp:5800 | Move | hold_id | C | False | True | if (hold_id > 0 && hit_move_cons(hold_id, a)) { |
| src1.6.5/rdfw.cpp:5801 | Move | hold_id | C | False | True | if (!has_taskX0 \|\| tasks[task_index].X[0]->id != hold_id) { |
| src1.6.5/rdfw.cpp:5802 | Move | hold_id | C | False | True | PutDown(hold_id); |
| src1.6.5/rdfw.cpp:5805 | Move | plate_id | C | False | True | if (plate_id > 0 && hit_move_cons(plate_id, a)) { |
| src1.6.5/rdfw.cpp:5806 | Move | hold_id | C | False | True | if (hold_id > 0) PutDown(hold_id); |
| src1.6.5/rdfw.cpp:5807 | Move | plate_id | C | False | True | FromPlate(plate_id); |
| src1.6.5/rdfw.cpp:5808 | Move | hold_id | C | False | True | if (hold_id > 0) PutDown(hold_id); |
| src1.6.5/rdfw.cpp:5812 | Move | location | C | False | True | const int previous_location = location; |
| src1.6.5/rdfw.cpp:5824 | Move | location | C | False | True | location = a; |
| src1.6.5/rdfw.cpp:5825 | Move | hold,location | C | False | True | if (hold)  hold->location  = a; |
| src1.6.5/rdfw.cpp:5826 | Move | location,plate | C | False | True | if (plate) plate->location = a; |
| src1.6.5/rdfw.cpp:5829 | Move | hold_id | C | False | True | if (hold_id > 0) { |
| src1.6.5/rdfw.cpp:5830 | Move | hold_id | C | False | True | MarkDirectLocationEvidence(hold_id, true); |
| src1.6.5/rdfw.cpp:5832 | Move | plate_id | C | False | True | if (plate_id > 0) { |
| src1.6.5/rdfw.cpp:5833 | Move | plate_id | C | False | True | MarkDirectLocationEvidence(plate_id, true); |
| src1.6.5/rdfw.cpp:5848 | Move | hold_id | C | False | True | if (hold_id > 0 && safe_idx(hold_id)) { |
| src1.6.5/rdfw.cpp:5849 | Move | hold_id | C | False | True | move_cons[hold_id][a] = 0; |
| src1.6.5/rdfw.cpp:5850 | Move | hold_id | C | False | True | objects[hold_id]->is_keep = 0; |
| src1.6.5/rdfw.cpp:5881 | PrintEnv | location | D | True | False | if (v->location == UNKNOWN) |
| src1.6.5/rdfw.cpp:5886 | PrintEnv | location | D | True | False | if (v->location < 0 \|\| v->location > MAX_LOCATION_ID) { |
| src1.6.5/rdfw.cpp:5890 | PrintEnv | location | D | True | False | if (static_cast<std::size_t>(v->location) >= objPos.size()) |
| src1.6.5/rdfw.cpp:5891 | PrintEnv | location | D | True | False | objPos.resize(v->location + 1); // expand objPos |
| src1.6.5/rdfw.cpp:5892 | PrintEnv | location | D | True | False | objPos[v->location].push_back(v); |
| src1.6.5/rdfw.cpp:5908 | PrintEnv | hold,plate | D | True | False | // print robot info (green) (hold, plate) |
| src1.6.5/rdfw.cpp:5910 | PrintEnv | hold,hold_id,plate,plate_id | D | True | False | cout << GREEN << "(" << v->sort << " hold:" << hold_id << " plate:" << plate_id << ")" << RESET; |
| src1.6.5/rdfw.cpp:5921 | PrintEnv | inside | D | True | False | cout << " inside:["; |
| src1.6.5/rdfw.cpp:5924 | PrintEnv | isOpen | D | True | False | cout << "] " << (p->isOpen ? "Open" : "Closed"); |
| src1.6.5/rdfw.cpp:6182 | ValidateInstruction | plate | A | True | False | else if (behave == "plate") |
| src1.6.5/rdfw.cpp:6184 | ValidateInstruction | inside | A | True | False | else if (behave == "inside" \|\| behave == "in") |
| src1.6.5/rdfw.cpp:6195 | ValidateInstruction | structuredSource | A | True | False | if (schema.give_form && !instruction.structuredSource && |
| src1.6.5/rdfw.cpp:6209 | ValidateInstruction | structuredSource | A | True | False | if (instruction.structuredSource) { |
| src1.6.5/rdfw.cpp:6300 | ValidateInstruction | inside | D | True | False | // synchronous per-item success logging inside the real-time budget. |
| src1.6.5/rdfw.cpp:6453 | ParseEnvSentence | hold,plate | C | True | False | const bool unary = firstToken == "hold" \|\| firstToken == "plate" \|\| |
| src1.6.5/rdfw.cpp:6457 | ParseEnvSentence | inside | C | True | False | firstToken == "inside" \|\| firstToken == "type"; |
| src1.6.5/rdfw.cpp:6472 | ParseEnvSentence | hold | C | True | False | if (firstToken == "hold") |
| src1.6.5/rdfw.cpp:6475 | ParseEnvSentence | hold_id | C | True | False | this->hold_id = index; |
| src1.6.5/rdfw.cpp:6478 | ParseEnvSentence | plate | C | True | False | else if (firstToken == "plate") |
| src1.6.5/rdfw.cpp:6480 | ParseEnvSentence | plate_id | C | True | False | this->plate_id = index; |
| src1.6.5/rdfw.cpp:6508 | ParseEnvSentence | isOpen | C | True | False | containerPtr->isOpen = (firstToken == "opened"); |
| src1.6.5/rdfw.cpp:6509 | ParseEnvSentence | EvidenceSource | C | True | False | SetContainerEvidence(index, stage == 1, EvidenceSource::INITIAL); |
| src1.6.5/rdfw.cpp:6514 | ParseEnvSentence | location | C | True | False | LOG_ERROR("Env sentence has an invalid location: %s", sentence.c_str()); |
| src1.6.5/rdfw.cpp:6518 | ParseEnvSentence | EvidenceSource | C | True | False | location_id, EvidenceSource::INITIAL)) { |
| src1.6.5/rdfw.cpp:6519 | ParseEnvSentence | location | C | True | False | obj->location = UNKNOWN; |
| src1.6.5/rdfw.cpp:6520 | ParseEnvSentence | EvidenceSource | C | True | False | MarkDirectLocationEvidence(index, false, EvidenceSource::UNKNOWN); |
| src1.6.5/rdfw.cpp:6526 | ParseEnvSentence | location | C | True | False | obj->location = location_id; |
| src1.6.5/rdfw.cpp:6531 | ParseEnvSentence | EvidenceSource | C | True | False | MarkDirectLocationEvidence(index, stage == 1, EvidenceSource::INITIAL); |
| src1.6.5/rdfw.cpp:6551 | ParseEnvSentence | inside | C | True | False | } else if (firstToken == "color" \|\| firstToken == "inside") { |
| src1.6.5/rdfw.cpp:6565 | ParseEnvSentence | inside | C | True | False | LOG_ERROR("Env sentence has an invalid inside reference: %s", |
| src1.6.5/rdfw.cpp:6570 | ParseEnvSentence | EvidenceSource | C | True | False | container_id, EvidenceSource::INITIAL)) { |
| src1.6.5/rdfw.cpp:6571 | ParseEnvSentence | inside | C | True | False | small->inside = UNKNOWN; |
| src1.6.5/rdfw.cpp:6572 | ParseEnvSentence | EvidenceSource | C | True | False | SetInsideEvidence(index, false, EvidenceSource::UNKNOWN); |
| src1.6.5/rdfw.cpp:6575 | ParseEnvSentence | inside | C | True | False | small->inside = container_id; |
| src1.6.5/rdfw.cpp:6576 | ParseEnvSentence | EvidenceSource | C | True | False | SetInsideEvidence(index, stage == 1, EvidenceSource::INITIAL); |
| src1.6.5/rdfw.cpp:6625 | ParseEnv | inside | D | True | False | // Preserve explicit ASP locations before inside propagates planner locations. |
| src1.6.5/rdfw.cpp:6628 | ParseEnv | hold_id | C | True | False | if (hold_id > 0) |
| src1.6.5/rdfw.cpp:6630 | ParseEnv | hold_id | C | True | False | auto held = std::dynamic_pointer_cast<SmallObject>(GetObject(hold_id)); |
| src1.6.5/rdfw.cpp:6632 | ParseEnv | hold,hold_id | C | True | False | LOG_ERROR("Ignoring invalid hold reference %d", hold_id); |
| src1.6.5/rdfw.cpp:6633 | ParseEnv | hold_id | C | True | False | hold_id = NONE; |
| src1.6.5/rdfw.cpp:6634 | ParseEnv | EvidenceSource | C | True | False | SetHold(nullptr, EvidenceSource::INITIAL); |
| src1.6.5/rdfw.cpp:6636 | ParseEnv | EvidenceSource | C | True | False | SetHold(held, EvidenceSource::INITIAL); |
| src1.6.5/rdfw.cpp:6637 | ParseEnv | hold_id,location | C | True | False | score_locations[hold_id] = location; |
| src1.6.5/rdfw.cpp:6638 | ParseEnv | EvidenceSource,hold_id | C | True | False | MarkDirectLocationEvidence(hold_id, stage == 1, EvidenceSource::INITIAL); |
| src1.6.5/rdfw.cpp:6639 | ParseEnv | EvidenceSource,hold_id | C | True | False | SetInsideEvidence(hold_id, stage == 1, EvidenceSource::INITIAL); |
| src1.6.5/rdfw.cpp:6642 | ParseEnv | plate_id | C | True | False | if (plate_id > 0) |
| src1.6.5/rdfw.cpp:6644 | ParseEnv | plate_id | C | True | False | auto plated = std::dynamic_pointer_cast<SmallObject>(GetObject(plate_id)); |
| src1.6.5/rdfw.cpp:6645 | ParseEnv | hold_id,plate_id | C | True | False | if (!plated \|\| plate_id == hold_id) { |
| src1.6.5/rdfw.cpp:6646 | ParseEnv | plate,plate_id | C | True | False | LOG_ERROR("Ignoring invalid plate reference %d", plate_id); |
| src1.6.5/rdfw.cpp:6647 | ParseEnv | plate_id | C | True | False | plate_id = NONE; |
| src1.6.5/rdfw.cpp:6648 | ParseEnv | EvidenceSource | C | True | False | SetPlate(nullptr, EvidenceSource::INITIAL); |
| src1.6.5/rdfw.cpp:6650 | ParseEnv | EvidenceSource | C | True | False | SetPlate(plated, EvidenceSource::INITIAL); |
| src1.6.5/rdfw.cpp:6651 | ParseEnv | location,plate_id | C | True | False | score_locations[plate_id] = location; |
| src1.6.5/rdfw.cpp:6652 | ParseEnv | EvidenceSource,plate_id | C | True | False | MarkDirectLocationEvidence(plate_id, stage == 1, EvidenceSource::INITIAL); |
| src1.6.5/rdfw.cpp:6653 | ParseEnv | EvidenceSource,plate_id | C | True | False | SetInsideEvidence(plate_id, stage == 1, EvidenceSource::INITIAL); |
| src1.6.5/rdfw.cpp:6656 | ParseEnv | holdProvenance | C | True | False | if (!holdProvenance.received.present) |
| src1.6.5/rdfw.cpp:6657 | ParseEnv | UpdateProvenance,hold_id | C | True | False | UpdateProvenance(StateField::HOLD, 0, hold_id, |
| src1.6.5/rdfw.cpp:6658 | ParseEnv | EvidenceSource | C | True | False | stage == 1, EvidenceSource::INITIAL); |
| src1.6.5/rdfw.cpp:6659 | ParseEnv | plateProvenance | C | True | False | if (!plateProvenance.received.present) |
| src1.6.5/rdfw.cpp:6660 | ParseEnv | UpdateProvenance,plate_id | C | True | False | UpdateProvenance(StateField::PLATE, 0, plate_id, |
| src1.6.5/rdfw.cpp:6661 | ParseEnv | EvidenceSource | C | True | False | stage == 1, EvidenceSource::INITIAL); |
| src1.6.5/rdfw.cpp:6665 | ParseEnv | hold,plate | C | True | False | if (s == plate \|\| s == hold) |
| src1.6.5/rdfw.cpp:6667 | ParseEnv | inside | C | True | False | if (s->inside != UNKNOWN && s->inside != NONE) |
| src1.6.5/rdfw.cpp:6669 | ParseEnv | inside | C | True | False | auto p = dynamic_pointer_cast<Container>(GetObject(s->inside)); |
| src1.6.5/rdfw.cpp:6673 | ParseEnv | location | C | True | False | s->location = p->location; |
| src1.6.5/rdfw.cpp:6677 | ParseEnv | location | C | True | False | s->location = UNKNOWN; |
| src1.6.5/rdfw.cpp:6678 | ParseEnv | inside | C | True | False | s->inside = UNKNOWN; |
| src1.6.5/rdfw.cpp:6681 | ParseEnv | location | C | True | False | else if (s->location != UNKNOWN && |
| src1.6.5/rdfw.cpp:6683 | ParseEnv | inside | C | True | False | s->inside = NONE; |
| src1.6.5/rdfw.cpp:6684 | ParseEnv | hold,inside,plate | C | True | False | if (s->inside != UNKNOWN && s != plate && s != hold) |
| src1.6.5/rdfw.cpp:6685 | ParseEnv | EvidenceSource | C | True | False | SetInsideEvidence(s->id, stage == 1, EvidenceSource::INITIAL); |
| src1.6.5/rdfw.cpp:6686 | ParseEnv | EvidenceSource,LocationSource,location | C | True | False | if (s->location != UNKNOWN && LocationSource(s->id) == EvidenceSource::UNKNOWN) |
| src1.6.5/rdfw.cpp:6687 | ParseEnv | EvidenceSource | C | True | False | MarkDirectLocationEvidence(s->id, stage == 1, EvidenceSource::INITIAL); |
| src1.6.5/rdfw.cpp:6712 | ParseInfo | location | C | True | False | int thelocation = info.Y[0]->location; |
| src1.6.5/rdfw.cpp:6715 | ParseInfo | location | C | True | False | v->location = thelocation; |
| src1.6.5/rdfw.cpp:6716 | ParseInfo | IsLocationVerified | C | True | False | MarkDirectLocationEvidence(v->id, stage == 1 && IsLocationVerified(info.Y[0]->id), |
| src1.6.5/rdfw.cpp:6717 | ParseInfo | EvidenceSource | C | True | False | EvidenceSource::EXPLICIT_INFO); |
| src1.6.5/rdfw.cpp:6721 | ParseInfo | location | D | True | False | // Official on/near mean co-location; neither proves outside. |
| src1.6.5/rdfw.cpp:6729 | ParseInfo | location | C | True | False | int yLocation = info.Y[0]->location; |
| src1.6.5/rdfw.cpp:6730 | ParseInfo | location | C | True | False | int xLocation = info.X[0]->location; |
| src1.6.5/rdfw.cpp:6736 | ParseInfo | location | C | True | False | v->location = yLocation; |
| src1.6.5/rdfw.cpp:6737 | ParseInfo | IsLocationVerified | C | True | False | MarkDirectLocationEvidence(v->id, stage == 1 && IsLocationVerified(info.Y[0]->id), |
| src1.6.5/rdfw.cpp:6738 | ParseInfo | EvidenceSource | C | True | False | EvidenceSource::EXPLICIT_INFO); |
| src1.6.5/rdfw.cpp:6751 | ParseInfo | location | C | True | False | v->location = xLocation; |
| src1.6.5/rdfw.cpp:6752 | ParseInfo | IsLocationVerified | C | True | False | MarkDirectLocationEvidence(v->id, stage == 1 && IsLocationVerified(info.X[0]->id), |
| src1.6.5/rdfw.cpp:6753 | ParseInfo | EvidenceSource | C | True | False | EvidenceSource::EXPLICIT_INFO); |
| src1.6.5/rdfw.cpp:6762 | ParseInfo | plate | C | True | False | else if (behave == "plate") |
| src1.6.5/rdfw.cpp:6764 | ParseInfo | plate | C | True | False | if (plate == nullptr) |
| src1.6.5/rdfw.cpp:6769 | ParseInfo | EvidenceSource,hold_id | C | True | False | if (hold_id == small->id) SetHold(nullptr, EvidenceSource::EXPLICIT_INFO); |
| src1.6.5/rdfw.cpp:6770 | ParseInfo | EvidenceSource | C | True | False | SetPlate(small, EvidenceSource::EXPLICIT_INFO); |
| src1.6.5/rdfw.cpp:6771 | ParseInfo | EvidenceSource | C | True | False | SetInsideEvidence(small->id, stage == 1, EvidenceSource::EXPLICIT_INFO); |
| src1.6.5/rdfw.cpp:6775 | ParseInfo | plate | C | True | False | LOG_ERROR("The plate already has a small object (%d %s)", plate->id, plate->sort.c_str()); |
| src1.6.5/rdfw.cpp:6778 | ParseInfo | inside | C | True | False | else if (behave == "inside" \|\| behave == "in") |
| src1.6.5/rdfw.cpp:6789 | ParseInfo | EvidenceSource,hold_id | C | True | False | if (hold_id == p->id) SetHold(nullptr, EvidenceSource::EXPLICIT_INFO); |
| src1.6.5/rdfw.cpp:6790 | ParseInfo | EvidenceSource,plate_id | C | True | False | if (plate_id == p->id) SetPlate(nullptr, EvidenceSource::EXPLICIT_INFO); |
| src1.6.5/rdfw.cpp:6792 | ParseInfo | inside | C | True | False | p->inside = cId; |
| src1.6.5/rdfw.cpp:6793 | ParseInfo | location | C | True | False | p->location=c->location; |
| src1.6.5/rdfw.cpp:6794 | ParseInfo | EvidenceSource | C | True | False | SetInsideEvidence(p->id, stage == 1, EvidenceSource::EXPLICIT_INFO); |
| src1.6.5/rdfw.cpp:6795 | ParseInfo | IsLocationVerified | C | True | False | MarkDirectLocationEvidence(p->id, stage == 1 && IsLocationVerified(cId), |
| src1.6.5/rdfw.cpp:6796 | ParseInfo | EvidenceSource | C | True | False | EvidenceSource::EXPLICIT_INFO); |
| src1.6.5/rdfw.cpp:6808 | ParseInfo | isOpen | C | True | False | p->isOpen = true; |
| src1.6.5/rdfw.cpp:6809 | ParseInfo | EvidenceSource | C | True | False | SetContainerEvidence(p->id, stage == 1, EvidenceSource::EXPLICIT_INFO); |
| src1.6.5/rdfw.cpp:6818 | ParseInfo | isOpen | C | True | False | p->isOpen = false; |
| src1.6.5/rdfw.cpp:6819 | ParseInfo | EvidenceSource | C | True | False | SetContainerEvidence(p->id, stage == 1, EvidenceSource::EXPLICIT_INFO); |
| src1.6.5/rdfw.cpp:6941 | Fini | location | C | False | True | location = UNKNOWN; |
| src1.6.5/rdfw.cpp:6942 | Fini | hold | C | False | True | hold = nullptr; |
| src1.6.5/rdfw.cpp:6943 | Fini | hold_id | C | False | True | hold_id = 0; |
| src1.6.5/rdfw.cpp:6947 | Fini | plate | C | False | True | plate = nullptr; |
| src1.6.5/rdfw.cpp:6948 | Fini | plate_id | C | False | True | plate_id = 0; |
| src1.6.5/rdfw.cpp:6970 | Fini | objectLocationVerified | C | False | True | objectLocationVerified.clear(); |
| src1.6.5/rdfw.cpp:6971 | Fini | objectLocationInferredByMustNear | C | False | True | objectLocationInferredByMustNear.clear(); |
| src1.6.5/rdfw.cpp:6972 | Fini | objectInsideVerified | C | False | True | objectInsideVerified.clear(); |
| src1.6.5/rdfw.cpp:6973 | Fini | containerStateVerified | C | False | True | containerStateVerified.clear(); |
| src1.6.5/rdfw.cpp:6974 | Fini | objectLocationSource | C | False | True | objectLocationSource.clear(); |
| src1.6.5/rdfw.cpp:6975 | Fini | locationProvenance | C | False | True | locationProvenance.clear(); |
| src1.6.5/rdfw.cpp:6976 | Fini | insideProvenance | C | False | True | insideProvenance.clear(); |
| src1.6.5/rdfw.cpp:6977 | Fini | containerProvenance | C | False | True | containerProvenance.clear(); |
| src1.6.5/rdfw.cpp:6978 | Fini | objectInsideSource | C | False | True | objectInsideSource.clear(); |
| src1.6.5/rdfw.cpp:6979 | Fini | containerStateSource | C | False | True | containerStateSource.clear(); |
| src1.6.5/rdfw.cpp:6998 | Fini | objectLocationVerified | C | False | True | objectLocationVerified.shrink_to_fit(); |
| src1.6.5/rdfw.cpp:6999 | Fini | objectLocationInferredByMustNear | C | False | True | objectLocationInferredByMustNear.shrink_to_fit(); |
| src1.6.5/rdfw.cpp:7000 | Fini | objectInsideVerified | C | False | True | objectInsideVerified.shrink_to_fit(); |
| src1.6.5/rdfw.cpp:7001 | Fini | containerStateVerified | C | False | True | containerStateVerified.shrink_to_fit(); |
| src1.6.5/rdfw.cpp:7038 | Fini | objectLocationVerified | C | False | True | objectLocationVerified.resize(100, false); |
| src1.6.5/rdfw.cpp:7039 | Fini | objectLocationInferredByMustNear | C | False | True | objectLocationInferredByMustNear.resize(100, false); |
| src1.6.5/rdfw.cpp:7040 | Fini | objectInsideVerified | C | False | True | objectInsideVerified.resize(100, false); |
| src1.6.5/rdfw.cpp:7041 | Fini | containerStateVerified | C | False | True | containerStateVerified.resize(100, false); |
| src1.6.5/rdfw.cpp:7084 | OptimizeMemoryUsage | objectLocationVerified | A | True | False | objectLocationVerified.shrink_to_fit(); |
| src1.6.5/rdfw.cpp:7085 | OptimizeMemoryUsage | objectLocationInferredByMustNear | A | True | False | objectLocationInferredByMustNear.shrink_to_fit(); |
| src1.6.5/rdfw.cpp:7086 | OptimizeMemoryUsage | objectInsideVerified | A | True | False | objectInsideVerified.shrink_to_fit(); |
| src1.6.5/rdfw.cpp:7087 | OptimizeMemoryUsage | containerStateVerified | A | True | False | containerStateVerified.shrink_to_fit(); |
| src1.6.5/rdfw.cpp:7156 | Instruction | structuredSource | A | True | False | structuredSource = true; |
| src1.6.5/rdfw.cpp:7371 | BuildMustNearRelations | hold_id | A | True | False | hold_mustnear = hold_id > 0 && static_cast<size_t>(hold_id) < mustNearComponent.size() && |
| src1.6.5/rdfw.cpp:7372 | BuildMustNearRelations | hold_id | A | True | False | mustNearComponent[hold_id] != UNKNOWN; |
| src1.6.5/rdfw.cpp:7373 | BuildMustNearRelations | plate_id | A | True | False | plate_mustnear = plate_id > 0 && static_cast<size_t>(plate_id) < mustNearComponent.size() && |
| src1.6.5/rdfw.cpp:7374 | BuildMustNearRelations | plate_id | A | True | False | mustNearComponent[plate_id] != UNKNOWN; |
| src1.6.5/rdfw.cpp:7396 | RefreshMustNearConstraintState | location | C | True | False | const int loc = objects[id]->location; |
| src1.6.5/rdfw.cpp:7398 | RefreshMustNearConstraintState | objectLocationInferredByMustNear,objectLocationVerified | C | True | False | if (objectLocationVerified[id] && !objectLocationInferredByMustNear[id]) |
| src1.6.5/rdfw.cpp:7400 | RefreshMustNearConstraintState | objectLocationInferredByMustNear | C | True | False | if (!objectLocationInferredByMustNear[id]) ++candidate_votes[loc]; |
| src1.6.5/rdfw.cpp:7420 | RefreshMustNearConstraintState | location | C | True | False | if (objects[id]->location == chosen_location && |
| src1.6.5/rdfw.cpp:7421 | RefreshMustNearConstraintState | objectLocationInferredByMustNear | C | True | False | !objectLocationInferredByMustNear[id] && |
| src1.6.5/rdfw.cpp:7422 | RefreshMustNearConstraintState | objectLocationVerified | C | True | False | (direct_votes.empty() \|\| objectLocationVerified[id])) { |
| src1.6.5/rdfw.cpp:7438 | RefreshMustNearConstraintState | objectLocationInferredByMustNear,objectLocationVerified | C | True | False | if (objectLocationVerified[id] && !objectLocationInferredByMustNear[id] && |
| src1.6.5/rdfw.cpp:7439 | RefreshMustNearConstraintState | location | C | True | False | objects[id]->location != UNKNOWN && objects[id]->location != chosen_location) { |
| src1.6.5/rdfw.cpp:7450 | RefreshMustNearConstraintState | objectLocationInferredByMustNear | C | True | False | if (!objectLocationInferredByMustNear[id]) continue; |
| src1.6.5/rdfw.cpp:7452 | RefreshMustNearConstraintState | location | C | True | False | objects[id]->location != chosen_location) { |
| src1.6.5/rdfw.cpp:7453 | RefreshMustNearConstraintState | location | C | True | False | objects[id]->location = UNKNOWN; |
| src1.6.5/rdfw.cpp:7454 | RefreshMustNearConstraintState | EvidenceSource | C | True | False | MarkDirectLocationEvidence(id, false, EvidenceSource::UNKNOWN); |
| src1.6.5/rdfw.cpp:7458 | RefreshMustNearConstraintState | EvidenceSource | C | True | False | anchored ? EvidenceSource::CONSTRAINT_DERIVED |
| src1.6.5/rdfw.cpp:7459 | RefreshMustNearConstraintState | EvidenceSource | C | True | False | : EvidenceSource::CONSTRAINT_HEURISTIC); |
| src1.6.5/rdfw.cpp:7468 | RefreshMustNearConstraintState | location | C | True | False | if (objects[id]->location == chosen_location && |
| src1.6.5/rdfw.cpp:7469 | RefreshMustNearConstraintState | objectLocationInferredByMustNear | C | True | False | !objectLocationInferredByMustNear[id] && |
| src1.6.5/rdfw.cpp:7470 | RefreshMustNearConstraintState | objectLocationVerified | C | True | False | (objectLocationVerified[id] \|\| !anchored)) continue; |
| src1.6.5/rdfw.cpp:7472 | RefreshMustNearConstraintState | location | C | True | False | objects[id]->location = chosen_location; |
| src1.6.5/rdfw.cpp:7474 | RefreshMustNearConstraintState | EvidenceSource | C | True | False | anchored ? EvidenceSource::CONSTRAINT_DERIVED |
| src1.6.5/rdfw.cpp:7475 | RefreshMustNearConstraintState | EvidenceSource | C | True | False | : EvidenceSource::CONSTRAINT_HEURISTIC); |
| src1.6.5/rdfw.cpp:7480 | RefreshMustNearConstraintState | inside | D | True | False | // SmallObject::inside/on，near 本身不代表包含或承载关系。 |
| src1.6.5/rdfw.cpp:7484 | RefreshMustNearConstraintState | inside | C | True | False | if (!item \|\| item->inside != container->id) continue; |
| src1.6.5/rdfw.cpp:7485 | RefreshMustNearConstraintState | location | C | True | False | item->location = chosen_location; |
| src1.6.5/rdfw.cpp:7486 | RefreshMustNearConstraintState | IsInsideVerified | C | True | False | const bool location_entailed = anchored && IsInsideVerified(item->id); |
| src1.6.5/rdfw.cpp:7488 | RefreshMustNearConstraintState | EvidenceSource | C | True | False | location_entailed ? EvidenceSource::CONSTRAINT_DERIVED |
| src1.6.5/rdfw.cpp:7489 | RefreshMustNearConstraintState | EvidenceSource | C | True | False | : EvidenceSource::CONSTRAINT_HEURISTIC); |
| src1.6.5/rdfw.cpp:7494 | RefreshMustNearConstraintState | location | C | True | False | LOG(GREEN "[MustNear] inferred obj %u at location %d\n" RESET, |
| src1.6.5/rdfw.cpp:7502 | RefreshMustNearConstraintState | location | C | True | False | const int loc = objects[id]->location; |
| src1.6.5/rdfw.cpp:7543 | ApplyMustInConstraintCorrection | inside | C | False | True | if (cons.IsUsable() && (cons.behave == "inside" \|\| cons.behave == "in") && |
| src1.6.5/rdfw.cpp:7558 | ApplyMustInConstraintCorrection | inside | C | False | True | cout<<"sm->inside: "<<sm->inside<<endl; |
| src1.6.5/rdfw.cpp:7560 | ApplyMustInConstraintCorrection | inside | C | False | True | if (sm->inside != UNKNOWN && sm->inside != y) { |
| src1.6.5/rdfw.cpp:7561 | ApplyMustInConstraintCorrection | inside | C | False | True | if (sm->inside >= 0 && sm->inside < numObjs) { |
| src1.6.5/rdfw.cpp:7562 | ApplyMustInConstraintCorrection | inside | C | False | True | if (auto old_cont = std::dynamic_pointer_cast<Container>(objects[sm->inside])) { |
| src1.6.5/rdfw.cpp:7571 | ApplyMustInConstraintCorrection | inside | C | False | True | sm->inside = y; |
| src1.6.5/rdfw.cpp:7572 | ApplyMustInConstraintCorrection | EvidenceSource | C | False | True | SetInsideEvidence(x, true, EvidenceSource::CONSTRAINT_DERIVED); |
| src1.6.5/rdfw.cpp:7590 | ApplyMustInConstraintCorrection | location | C | False | True | int y_loc = objects[y]->location; |
| src1.6.5/rdfw.cpp:7592 | ApplyMustInConstraintCorrection | location | C | False | True | objects[x]->location = y_loc; |
| src1.6.5/rdfw.cpp:7593 | ApplyMustInConstraintCorrection | IsLocationVerified | C | False | True | const bool location_entailed = IsLocationVerified(y); |
| src1.6.5/rdfw.cpp:7595 | ApplyMustInConstraintCorrection | EvidenceSource | C | False | True | location_entailed ? EvidenceSource::CONSTRAINT_DERIVED |
| src1.6.5/rdfw.cpp:7596 | ApplyMustInConstraintCorrection | EvidenceSource | C | False | True | : EvidenceSource::CONSTRAINT_HEURISTIC); |
| src1.6.5/rdfw.cpp:7609 | ApplyMustInConstraintCorrection | inside | C | False | True | if (cons.behave != "inside"&&cons.behave != "in") continue; |
| src1.6.5/rdfw.cpp:7618 | ApplyMustInConstraintCorrection | inside | C | False | True | if (smObj->inside == y) { |
| src1.6.5/rdfw.cpp:7620 | ApplyMustInConstraintCorrection | inside | C | False | True | smObj->inside = UNKNOWN; |
| src1.6.5/rdfw.cpp:7621 | ApplyMustInConstraintCorrection | location | C | False | True | int old_loc = smObj->location; |
| src1.6.5/rdfw.cpp:7622 | ApplyMustInConstraintCorrection | location | C | False | True | smObj->location = UNKNOWN; |
| src1.6.5/rdfw.cpp:7673 | ApplyOpenCloseCorrection | isOpen | C | True | False | if (cont->isOpen != 1) { |
| src1.6.5/rdfw.cpp:7674 | ApplyOpenCloseCorrection | isOpen | C | True | False | cont->isOpen = true; |
| src1.6.5/rdfw.cpp:7680 | ApplyOpenCloseCorrection | isOpen | C | True | False | if (cont->isOpen) { |
| src1.6.5/rdfw.cpp:7681 | ApplyOpenCloseCorrection | isOpen | C | True | False | cont->isOpen = false; |
| src1.6.5/rdfw.cpp:7687 | ApplyOpenCloseCorrection | isOpen | C | True | False | if (cont->isOpen) { |
| src1.6.5/rdfw.cpp:7688 | ApplyOpenCloseCorrection | isOpen | C | True | False | cont->isOpen = false; |
| src1.6.5/rdfw.cpp:7694 | ApplyOpenCloseCorrection | isOpen | C | True | False | if (cont->isOpen != 1) { |
| src1.6.5/rdfw.cpp:7695 | ApplyOpenCloseCorrection | isOpen | C | True | False | cont->isOpen = true; |
| src1.6.5/rdfw.cpp:7702 | ApplyOpenCloseCorrection | isOpen | C | True | False | cont->isOpen = false; |
| src1.6.5/rdfw.cpp:7710 | ApplyOpenCloseCorrection | EvidenceSource | C | True | False | contradictory ? EvidenceSource::CONSTRAINT_HEURISTIC |
| src1.6.5/rdfw.cpp:7711 | ApplyOpenCloseCorrection | EvidenceSource | C | True | False | : EvidenceSource::CONSTRAINT_DERIVED); |
| src1.6.5/rdfw.hpp:36 | declaration/inline | Source | D | True | False | // Source of the current fact, separate from whether it is reliable enough |
| src1.6.5/rdfw.hpp:38 | declaration/inline | EvidenceSource | D | True | False | enum class EvidenceSource { |
| src1.6.5/rdfw.hpp:48 | declaration/inline | EvidenceSource | D | True | False | EvidenceSource source = EvidenceSource::UNKNOWN; |
| src1.6.5/rdfw.hpp:51 | StateClaim | EvidenceSource | A | True | False | StateClaim(int v, EvidenceSource s, bool p) : value(v), source(s), present(p) {} |
| src1.6.5/rdfw.hpp:62 | declaration/inline | StateProvenance | D | True | False | struct StateProvenance { |
| src1.6.5/rdfw.hpp:66 | declaration/inline | EvidenceSource | D | True | False | EvidenceSource resolved_source = EvidenceSource::UNKNOWN; |
| src1.6.5/rdfw.hpp:107 | declaration/inline | location | D | True | False | *      location    (int)   : ... |
| src1.6.5/rdfw.hpp:113 | declaration/inline | location | D | True | False | *      Object (Init)       : Initialize id, sort and location (id must be known) |
| src1.6.5/rdfw.hpp:119 | declaration/inline | location | D | True | False | int location; |
| src1.6.5/rdfw.hpp:125 | Object | location | C | True | False | Object(int id, const string &sort = "", int location = UNKNOWN) |
| src1.6.5/rdfw.hpp:126 | Object | location | C | True | False | : sort(sort), location(location), id(id) {}   // Initialize id, sort and location (id must be known) |
| src1.6.5/rdfw.hpp:131 | ToString | location | D | True | False | return "id:" + to_string(id) + "    at:" + to_string(location) + "     sort:" + sort + "\n"; |
| src1.6.5/rdfw.hpp:142 | declaration/inline | inside | D | True | False | *      inside      (int)   : the big object id which small object inside |
| src1.6.5/rdfw.hpp:145 | declaration/inline | location | D | True | False | *      Object (Init)       : Initialize id, sort and location (id must be known) |
| src1.6.5/rdfw.hpp:152 | declaration/inline | inside | D | True | False | int inside = UNKNOWN;  // the big object id which small object inside |
| src1.6.5/rdfw.hpp:156 | SmallObject | location | C | True | False | SmallObject(int id, int location = UNKNOWN, const string &sort = "", const string &color = "") |
| src1.6.5/rdfw.hpp:157 | SmallObject | location | C | True | False | : Object(id, sort, location), color(color) {} |
| src1.6.5/rdfw.hpp:166 | ToString | inside | D | True | False | return Object::ToString() + "color:" + color + "    inside:" + to_string(inside) + "    on:" + to_string(on) + "\n"; |
| src1.6.5/rdfw.hpp:176 | declaration/inline | inside | D | True | False | *      inside      (int)   : the big object id which small object inside |
| src1.6.5/rdfw.hpp:183 | BigObject | location | C | True | False | BigObject(int id, int location = UNKNOWN, string sort = "") |
| src1.6.5/rdfw.hpp:184 | BigObject | location | C | True | False | : Object(id, sort, location) {} |
| src1.6.5/rdfw.hpp:198 | declaration/inline | isOpen | D | True | False | *      isOpen      (int)   : 0(closed)  1(open) |
| src1.6.5/rdfw.hpp:200 | declaration/inline | inside | D | True | False | *      inside      (int)   : the big object id which small object inside |
| src1.6.5/rdfw.hpp:210 | declaration/inline | isOpen | D | True | False | int isOpen = 0; |
| src1.6.5/rdfw.hpp:212 | Container | isOpen,location | C | True | False | Container(int id, int location = UNKNOWN, bool isOpen = true, string sort = "") |
| src1.6.5/rdfw.hpp:213 | Container | isOpen,location | C | True | False | : BigObject(id, location, sort), isOpen(isOpen) {} |
| src1.6.5/rdfw.hpp:217 | Container | isOpen | C | True | False | : BigObject(obj), isOpen(UNKNOWN) {} |
| src1.6.5/rdfw.hpp:221 | Container | isOpen | C | True | False | : BigObject(*obj), isOpen(UNKNOWN) {} |
| src1.6.5/rdfw.hpp:251 | declaration/inline | hold | D | True | False | *      hold        (shared_ptr<SmallObject>)   : ... |
| src1.6.5/rdfw.hpp:252 | declaration/inline | plate | D | True | False | *      plate       (shared_ptr<SmallObject>)   : ... |
| src1.6.5/rdfw.hpp:253 | declaration/inline | hold_id | D | True | False | *      hold_id     (int)   : ... |
| src1.6.5/rdfw.hpp:254 | declaration/inline | plate_id | D | True | False | *      plate_id    (int)   : ... |
| src1.6.5/rdfw.hpp:264 | declaration/inline | hold | D | True | False | shared_ptr<SmallObject> hold; |
| src1.6.5/rdfw.hpp:265 | declaration/inline | plate | D | True | False | shared_ptr<SmallObject> plate; |
| src1.6.5/rdfw.hpp:267 | declaration/inline | hold_id,plate_id | D | True | False | int hold_id = NONE, plate_id = UNKNOWN; |
| src1.6.5/rdfw.hpp:269 | Robot | location | C | True | False | Robot(int id, int location = UNKNOWN) |
| src1.6.5/rdfw.hpp:270 | Robot | location | C | True | False | : Object(id, "robot", location) {} |
| src1.6.5/rdfw.hpp:274 | SetHold | hold | C | False | True | void SetHold(const shared_ptr<SmallObject> &hold) { |
| src1.6.5/rdfw.hpp:275 | SetHold | hold | C | False | True | this->hold = hold; |
| src1.6.5/rdfw.hpp:276 | SetHold | hold | C | False | True | if (hold != nullptr) { |
| src1.6.5/rdfw.hpp:277 | SetHold | hold,location | C | False | True | this->hold->location = location; |
| src1.6.5/rdfw.hpp:278 | SetHold | hold,hold_id | C | False | True | hold_id = hold->id; |
| src1.6.5/rdfw.hpp:279 | SetHold | hold,inside | C | False | True | hold->inside = NONE; |
| src1.6.5/rdfw.hpp:280 | SetHold | hold | C | False | True | hold->on = NONE; |
| src1.6.5/rdfw.hpp:281 | SetHold | hold_id,plate_id | C | False | True | if (plate_id == hold_id) { |
| src1.6.5/rdfw.hpp:282 | SetHold | plate | C | False | True | plate.reset(); |
| src1.6.5/rdfw.hpp:283 | SetHold | plate_id | C | False | True | plate_id = NONE; |
| src1.6.5/rdfw.hpp:287 | SetHold | hold_id | C | False | True | hold_id = NONE; |
| src1.6.5/rdfw.hpp:290 | SetPlate | plate | C | False | True | void SetPlate(const shared_ptr<SmallObject> &plate) { |
| src1.6.5/rdfw.hpp:291 | SetPlate | plate | C | False | True | this->plate = plate; |
| src1.6.5/rdfw.hpp:292 | SetPlate | plate | C | False | True | if (plate != nullptr) { |
| src1.6.5/rdfw.hpp:293 | SetPlate | location,plate | C | False | True | this->plate->location = location; |
| src1.6.5/rdfw.hpp:294 | SetPlate | plate,plate_id | C | False | True | plate_id = plate->id; |
| src1.6.5/rdfw.hpp:295 | SetPlate | inside,plate | C | False | True | plate->inside = NONE; |
| src1.6.5/rdfw.hpp:296 | SetPlate | plate | C | False | True | plate->on = NONE; |
| src1.6.5/rdfw.hpp:297 | SetPlate | hold_id,plate_id | C | False | True | if (hold_id == plate_id) { |
| src1.6.5/rdfw.hpp:298 | SetPlate | hold | C | False | True | hold.reset(); |
| src1.6.5/rdfw.hpp:299 | SetPlate | hold_id | C | False | True | hold_id = NONE; |
| src1.6.5/rdfw.hpp:303 | SetPlate | plate_id | C | False | True | plate_id = NONE; |
| src1.6.5/rdfw.hpp:307 | ToString | hold,plate | D | True | False | return Object::ToString() + "hold:\n" + (hold != nullptr ? hold->ToString() : "") + "plate:\n" + (plate != nullptr ? plate->ToString() : ""); |
| src1.6.5/rdfw.hpp:443 | declaration/inline | inside | D | True | False | // Stage 1 ASP at facts, separate from planner locations inferred from inside. |
| src1.6.5/rdfw.hpp:475 | declaration/inline | inside | D | True | False | vector<vector<int>> putin_cons;      //not_info   inside   + not_task   putin |
| src1.6.5/rdfw.hpp:476 | declaration/inline | inside | D | True | False | vector<vector<int>> takeout_cons;    // ontnot_infor  inside   + not_task   takeout |
| src1.6.5/rdfw.hpp:478 | declaration/inline | hold,plate | D | True | False | vector<int> putdown1_cons;        //not_task   putdown  + hold  + plate |
| src1.6.5/rdfw.hpp:482 | declaration/inline | plate | D | True | False | vector<int> pickup_cons;         //not_info   plate   + not_task   pickup |
| src1.6.5/rdfw.hpp:485 | declaration/inline | hold | D | True | False | vector<int> fromplate_cons;      //hold |
| src1.6.5/rdfw.hpp:486 | declaration/inline | plate | D | True | False | vector<int> toplate_cons;        //plate |
| src1.6.5/rdfw.hpp:499 | declaration/inline | objectLocationInferredByMustNear | D | True | False | // objectLocationInferredByMustNear 用来区分直接证据和约束推导证据， |
| src1.6.5/rdfw.hpp:502 | declaration/inline | objectLocationInferredByMustNear | D | True | False | std::vector<bool> objectLocationInferredByMustNear; |
| src1.6.5/rdfw.hpp:530 | declaration/inline | objectLocationVerified | D | True | False | vector<bool> objectLocationVerified; |
| src1.6.5/rdfw.hpp:531 | declaration/inline | objectInsideVerified | D | True | False | vector<bool> objectInsideVerified; |
| src1.6.5/rdfw.hpp:532 | declaration/inline | containerStateVerified | D | True | False | vector<bool> containerStateVerified; |
| src1.6.5/rdfw.hpp:533 | declaration/inline | EvidenceSource,objectLocationSource | D | True | False | vector<EvidenceSource> objectLocationSource; |
| src1.6.5/rdfw.hpp:534 | declaration/inline | EvidenceSource,objectInsideSource | D | True | False | vector<EvidenceSource> objectInsideSource; |
| src1.6.5/rdfw.hpp:535 | declaration/inline | EvidenceSource,containerStateSource | D | True | False | vector<EvidenceSource> containerStateSource; |
| src1.6.5/rdfw.hpp:537 | declaration/inline | StateProvenance,locationProvenance | D | True | False | vector<StateProvenance> locationProvenance; |
| src1.6.5/rdfw.hpp:538 | declaration/inline | StateProvenance,insideProvenance | D | True | False | vector<StateProvenance> insideProvenance; |
| src1.6.5/rdfw.hpp:539 | declaration/inline | StateProvenance,containerProvenance | D | True | False | vector<StateProvenance> containerProvenance; |
| src1.6.5/rdfw.hpp:540 | declaration/inline | StateProvenance,holdProvenance | D | True | False | StateProvenance holdProvenance; |
| src1.6.5/rdfw.hpp:541 | declaration/inline | StateProvenance,plateProvenance | D | True | False | StateProvenance plateProvenance; |
| src1.6.5/rdfw.hpp:542 | declaration/inline | Provenance,StateProvenance | D | True | False | const StateProvenance& Provenance(StateField field, unsigned int id) const; |
| src1.6.5/rdfw.hpp:546 | declaration/inline | DependenciesCurrent | D | True | False | bool DependenciesCurrent(StateField field, unsigned int id) const; |
| src1.6.5/rdfw.hpp:547 | declaration/inline | ResolvedState | D | True | False | StateClaim ResolvedState(StateField field, unsigned int id) const; |
| src1.6.5/rdfw.hpp:550 | declaration/inline | EvidenceSource | D | True | False | EvidenceSource source); |
| src1.6.5/rdfw.hpp:563 | declaration/inline | location | D | True | False | const LocationSensedInfo& GetLocationSensedInfo(int location) const; |
| src1.6.5/rdfw.hpp:564 | declaration/inline | location | D | True | False | bool HasObjectAtLocation(int location, unsigned int object_id) const; |
| src1.6.5/rdfw.hpp:565 | declaration/inline | location | D | True | False | bool HasContainerAtLocation(int location) const; |
| src1.6.5/rdfw.hpp:566 | declaration/inline | location | D | True | False | vector<unsigned int> GetObjectsAtLocation(int location) const; |
| src1.6.5/rdfw.hpp:567 | declaration/inline | location | D | True | False | unsigned int GetContainerAtLocation(int location) const; |
| src1.6.5/rdfw.hpp:568 | declaration/inline | location | D | True | False | int CountObjectsAtLocation(int location) const; |
| src1.6.5/rdfw.hpp:713 | declaration/inline | EvidenceSource | D | True | False | EvidenceSource source = EvidenceSource::ACTION_SUCCESS); |
| src1.6.5/rdfw.hpp:714 | declaration/inline | EvidenceSource | D | True | False | void SetInsideEvidence(unsigned int id, bool verified, EvidenceSource source); |
| src1.6.5/rdfw.hpp:715 | declaration/inline | EvidenceSource | D | True | False | void SetContainerEvidence(unsigned int id, bool verified, EvidenceSource source); |
| src1.6.5/rdfw.hpp:716 | declaration/inline | EvidenceSource,LocationSource | D | True | False | EvidenceSource LocationSource(unsigned int id) const; |
| src1.6.5/rdfw.hpp:717 | declaration/inline | EvidenceSource,InsideSource | D | True | False | EvidenceSource InsideSource(unsigned int id) const; |
| src1.6.5/rdfw.hpp:718 | declaration/inline | ContainerSource,EvidenceSource | D | True | False | EvidenceSource ContainerSource(unsigned int id) const; |
| src1.6.5/rdfw.hpp:733 | declaration/inline | IsLocationVerified | D | True | False | bool IsLocationVerified(unsigned int id) const; |
| src1.6.5/rdfw.hpp:734 | declaration/inline | IsInsideVerified | D | True | False | bool IsInsideVerified(unsigned int id) const; |
| src1.6.5/rdfw.hpp:735 | declaration/inline | IsContainerStateVerified | D | True | False | bool IsContainerStateVerified(unsigned int id) const; |
| src1.6.5/rdfw.hpp:738 | declaration/inline | EvidenceSource | D | True | False | EvidenceSource source = EvidenceSource::ACTION_SUCCESS); |
| src1.6.5/rdfw.hpp:740 | declaration/inline | EvidenceSource | D | True | False | EvidenceSource source = EvidenceSource::ACTION_SUCCESS); |
| src1.6.5/rdfw.hpp:837 | declaration/inline | MutableProvenance,StateProvenance | D | True | False | StateProvenance& MutableProvenance(StateField field, unsigned int id); |
| src1.6.5/rdfw.hpp:838 | declaration/inline | UpdateProvenance | D | True | False | void UpdateProvenance(StateField field, unsigned int id, int value, |
| src1.6.5/rdfw.hpp:839 | declaration/inline | EvidenceSource | D | True | False | bool verified, EvidenceSource source); |
| src1.6.5/rdfw.hpp:944 | declaration/inline | structuredSource | D | True | False | bool structuredSource = false; |
| src1.6.5/terminal_checker.cpp:43 | isLocationKnown | location | B | False | True | if (!object \|\| object->location == _home::UNKNOWN) return false; |
| src1.6.5/terminal_checker.cpp:44 | isLocationKnown | location | B | False | True | if (object->id == 0) return world.location != _home::UNKNOWN; |
| src1.6.5/terminal_checker.cpp:45 | isLocationKnown | IsLocationVerified | B | False | True | return world.stage == 1 \|\| (world.IsLocationVerified(object->id) && |
| src1.6.5/terminal_checker.cpp:46 | isLocationKnown | EvidenceSource,LocationSource | B | False | True | (world.LocationSource(object->id) != EvidenceSource::CONSTRAINT_DERIVED \|\| |
| src1.6.5/terminal_checker.cpp:52 | scoreLocation | location | B | False | True | if (object->id == 0) return world.location; |
| src1.6.5/terminal_checker.cpp:55 | scoreLocation | location | B | False | True | return object->location; |
| src1.6.5/terminal_checker.cpp:59 | isInsideKnown | inside | B | False | True | return object && object->inside != _home::UNKNOWN && |
| src1.6.5/terminal_checker.cpp:60 | isInsideKnown | IsInsideVerified | B | False | True | (world.stage == 1 \|\| (world.IsInsideVerified(object->id) && |
| src1.6.5/terminal_checker.cpp:61 | isInsideKnown | EvidenceSource,InsideSource | B | False | True | (world.InsideSource(object->id) != EvidenceSource::CONSTRAINT_DERIVED \|\| |
| src1.6.5/terminal_checker.cpp:67 | isContainerStateKnown | isOpen | B | False | True | return container && (container->isOpen == 0 \|\| container->isOpen == 1) && |
| src1.6.5/terminal_checker.cpp:68 | isContainerStateKnown | IsContainerStateVerified | B | False | True | (world.stage == 1 \|\| (world.IsContainerStateVerified(container->id) && |
| src1.6.5/terminal_checker.cpp:69 | isContainerStateKnown | ContainerSource,EvidenceSource | B | False | True | (world.ContainerSource(container->id) != EvidenceSource::CONSTRAINT_DERIVED \|\| |
| src1.6.5/terminal_checker.cpp:99 | evaluatePair | location | B | False | True | world.location == scoreLocation(world, x)); |
| src1.6.5/terminal_checker.cpp:100 | evaluatePair | location | B | False | True | if (world.location != _home::UNKNOWN && |
| src1.6.5/terminal_checker.cpp:101 | evaluatePair | location | B | False | True | world.IsAbsentFromSensedLocation(x->id, world.location)) |
| src1.6.5/terminal_checker.cpp:103 | evaluatePair | location | B | False | True | if (!isLocationKnown(world, x) \|\| world.location == _home::UNKNOWN) |
| src1.6.5/terminal_checker.cpp:105 | evaluatePair | location | B | False | True | return boolStatus(world.location == x->location); |
| src1.6.5/terminal_checker.cpp:115 | evaluatePair | isOpen | B | False | True | return boolStatus(static_cast<bool>(container->isOpen) == expect_open); |
| src1.6.5/terminal_checker.cpp:119 | evaluatePair | hold_id,plate_id | B | False | True | const bool stored = world.hold_id == x->id \|\| world.plate_id == x->id; |
| src1.6.5/terminal_checker.cpp:120 | evaluatePair | IsInsideVerified | B | False | True | if (world.stage == 2 && !world.IsInsideVerified(x->id)) |
| src1.6.5/terminal_checker.cpp:129 | evaluatePair | IsInsideVerified | B | False | True | if (world.stage == 2 && !world.IsInsideVerified(x->id)) |
| src1.6.5/terminal_checker.cpp:131 | evaluatePair | hold_id,plate_id | B | False | True | if (world.hold_id == x->id \|\| world.plate_id == x->id) |
| src1.6.5/terminal_checker.cpp:136 | evaluatePair | inside | B | False | True | if (behave == "putin" \|\| behave == "inside" \|\| behave == "in") { |
| src1.6.5/terminal_checker.cpp:140 | evaluatePair | inside | B | False | True | return boolStatus(small->inside == y->id); |
| src1.6.5/terminal_checker.cpp:147 | evaluatePair | inside | B | False | True | return boolStatus(small->inside != y->id); |
| src1.6.5/terminal_checker.cpp:159 | evaluatePair | location | B | False | True | world.IsAbsentFromSensedLocation(target->id, x->location)) |
| src1.6.5/terminal_checker.cpp:162 | evaluatePair | location | B | False | True | world.IsAbsentFromSensedLocation(x->id, target->location)) |
| src1.6.5/terminal_checker.cpp:171 | evaluatePair | hold_id,plate_id | B | False | True | if (world.hold_id == x->id \|\| world.plate_id == x->id) |
| src1.6.5/terminal_checker.cpp:177 | evaluatePair | plate | B | False | True | if (behave == "plate") { |
| src1.6.5/terminal_checker.cpp:178 | evaluatePair | IsInsideVerified | B | False | True | if (world.stage == 2 && !world.IsInsideVerified(x->id)) |
| src1.6.5/terminal_checker.cpp:180 | evaluatePair | plate_id | B | False | True | return boolStatus(world.plate_id == x->id); |
| src1.6.5/terminal_checker.cpp:183 | evaluatePair | hold | B | False | True | if (behave == "hold") { |
| src1.6.5/terminal_checker.cpp:184 | evaluatePair | IsInsideVerified | B | False | True | if (world.stage == 2 && !world.IsInsideVerified(x->id)) |
| src1.6.5/terminal_checker.cpp:186 | evaluatePair | hold_id | B | False | True | return boolStatus(world.hold_id == x->id); |
| src1.6.5/terminal_checker.cpp:245 | evaluateConstraint | hold | D | True | False | // Each grounded constraint must hold; negate BEFORE combining bindings. |
| src1.6.5/tests/guarded_decision_tests.cpp:19 | Run | hold,plate | D | True | False | "(hold 0) (plate 0) (at 0 1) " |
| src1.6.5/tests/guarded_decision_tests.cpp:39 | declaration/inline | hold,plate | D | True | False | "(hold 0) (plate 0) (at 0 1) " |
| src1.6.5/tests/input_safety_tests.cpp:54 | main | inside | D | True | False | assert(world->ParseEnv("(inside 2 99) (at 0 1)")); |
| src1.6.5/tests/input_safety_tests.cpp:55 | main | inside | D | True | False | assert(std::dynamic_pointer_cast<SmallObject>(world->objects[2])->inside == UNKNOWN); |
| src1.6.5/tests/input_safety_tests.cpp:56 | main | hold | D | True | False | assert(world->ParseEnv("(hold 3) (at 0 1)")); |
| src1.6.5/tests/input_safety_tests.cpp:57 | main | hold,hold_id | D | True | False | assert(world->hold_id == NONE && !world->hold); |
| src1.6.5/tests/input_safety_tests.cpp:62 | main | hold | D | True | False | "(:domain (hold 0) (sort 5 bowl) (size 5 small) (at 5 5))")); |
| src1.6.5/tests/input_safety_tests.cpp:64 | main | location | D | True | False | assert(world->objects[5]->sort == "bowl" && world->objects[5]->location == 5); |
| src1.6.5/tests/input_safety_tests.cpp:66 | main | location | D | True | False | // The largest supported sparse id is bounded and all object/location |
| src1.6.5/tests/interval_gate_tests.cpp:27 | main | hold,plate | D | True | False | assert(w->ParseEnv("(hold 0) (plate 0) (at 0 1) (sort 1 cupboard) " |
| src1.6.5/tests/interval_gate_tests.cpp:95 | main | isOpen | D | True | False | std::dynamic_pointer_cast<Container>(w->objects[1])->isOpen = true; |
| src1.6.5/tests/legal_preservation_tests.cpp:14 | main | Facts | D | True | False | // Facts can be reordered; late size/type must not erase closed state. |
| src1.6.5/tests/legal_preservation_tests.cpp:19 | main | isOpen | D | True | False | assert(std::dynamic_pointer_cast<Container>(w->objects[3])->isOpen == 0); |
| src1.6.5/tests/parse_snapshot.cpp:9 | snapshot | hold_id,location,plate_id | D | True | False | std::cout << "SNAP " << phase << " robot=" << w.location << ',' << w.hold_id << ',' << w.plate_id << '\n'; |
| src1.6.5/tests/parse_snapshot.cpp:11 | snapshot | location | D | True | False | std::cout<<"SNAP object "<<o->id<<' '<<o->sort<<' '<<o->location; |
| src1.6.5/tests/parse_snapshot.cpp:15 | snapshot | inside | D | True | False | if(s) std::cout<<" small "<<s->color<<' '<<s->inside<<' '<<s->on; |
| src1.6.5/tests/parse_snapshot.cpp:16 | snapshot | isOpen | D | True | False | else if(c) std::cout<<" container "<<c->isOpen; |
| src1.6.5/tests/question_preflight_tests.cpp:12 | declaration/inline | hold,plate | D | True | False | "(hold 0) (plate 0) (at 0 1) " |
| src1.6.5/tests/question_preflight_tests.cpp:91 | GotoAndConflicts | location | D | True | False | // Different IDs at the SAME location must not be merged. |
| src1.6.5/tests/question_preflight_tests.cpp:115 | CanonicalRelationsAndSets | inside | D | True | False | Not(Info("inside X Y", "(id X 2) (id Y 3)")) + |
| src1.6.5/tests/question_preflight_tests.cpp:146 | MalformedConstraintRecovery | inside | D | True | False | "(:cons_not (:info (inside X) (:cond (id X 2))))"}) { |
| src1.6.5/tests/question_preflight_tests.cpp:166 | WorldSafetyAndStage2Unknowns | location | D | True | False | w->objects[2]->location = UNKNOWN; |
| src1.6.5/tests/question_preflight_tests.cpp:167 | WorldSafetyAndStage2Unknowns | location | D | True | False | w->objects[3]->location = UNKNOWN; |
| src1.6.5/tests/question_preflight_tests.cpp:168 | WorldSafetyAndStage2Unknowns | isOpen | D | True | False | std::dynamic_pointer_cast<Container>(w->objects[3])->isOpen = UNKNOWN; |
| src1.6.5/tests/question_preflight_tests.cpp:170 | WorldSafetyAndStage2Unknowns | location | D | True | False | w->objects[3]->location = 1; // Stage 2 err may collide with human |
| src1.6.5/tests/recovery_evidence_tests.cpp:30 | declaration/inline | hold,plate | D | True | False | "(hold 0) (plate 0) (at 0 2) " |
| src1.6.5/tests/recovery_evidence_tests.cpp:40 | main | inside | D | True | False | // A: a guaranteed initial must-inside repairs inside, but the cupboard's |
| src1.6.5/tests/recovery_evidence_tests.cpp:41 | main | location | D | True | False | // unverified initial location does not become a Sense-quality book location. |
| src1.6.5/tests/recovery_evidence_tests.cpp:42 | main | inside | D | True | False | auto inside = World(argv[1], 2, kitchen); |
| src1.6.5/tests/recovery_evidence_tests.cpp:43 | main | inside | D | True | False | Instruction must_in = Unary("inside", inside->objects[3]); |
| src1.6.5/tests/recovery_evidence_tests.cpp:44 | main | inside | D | True | False | must_in.Y.push_back(inside->objects[2]); |
| src1.6.5/tests/recovery_evidence_tests.cpp:45 | main | inside | D | True | False | inside->notnot_infoConstrains.push_back(must_in); |
| src1.6.5/tests/recovery_evidence_tests.cpp:46 | main | inside | D | True | False | inside->ApplyMustInConstraintCorrection(); |
| src1.6.5/tests/recovery_evidence_tests.cpp:47 | main | IsInsideVerified,inside | D | True | False | assert(inside->IsInsideVerified(3)); |
| src1.6.5/tests/recovery_evidence_tests.cpp:48 | main | EvidenceSource,InsideSource,inside | D | True | False | assert(inside->InsideSource(3) == EvidenceSource::CONSTRAINT_DERIVED); |
| src1.6.5/tests/recovery_evidence_tests.cpp:49 | main | IsLocationVerified,inside | D | True | False | assert(!inside->IsLocationVerified(3)); |
| src1.6.5/tests/recovery_evidence_tests.cpp:50 | main | EvidenceSource,LocationSource,inside | D | True | False | assert(inside->LocationSource(3) == EvidenceSource::CONSTRAINT_HEURISTIC); |
| src1.6.5/tests/recovery_evidence_tests.cpp:51 | main | inside | D | True | False | Instruction putin = Unary("putin", inside->objects[3]); |
| src1.6.5/tests/recovery_evidence_tests.cpp:52 | main | inside | D | True | False | putin.Y.push_back(inside->objects[2]); |
| src1.6.5/tests/recovery_evidence_tests.cpp:53 | main | inside | D | True | False | assert(inside->ZeroActionPreCheck(putin)); |
| src1.6.5/tests/recovery_evidence_tests.cpp:58 | main | ContainerSource,EvidenceSource | D | True | False | assert(closed->ContainerSource(2) == EvidenceSource::INITIAL); |
| src1.6.5/tests/recovery_evidence_tests.cpp:59 | main | IsContainerStateVerified | D | True | False | assert(!closed->IsContainerStateVerified(2)); |
| src1.6.5/tests/recovery_evidence_tests.cpp:62 | main | IsContainerStateVerified | D | True | False | assert(closed->IsContainerStateVerified(2)); |
| src1.6.5/tests/recovery_evidence_tests.cpp:63 | main | ContainerSource,EvidenceSource | D | True | False | assert(closed->ContainerSource(2) == EvidenceSource::CONSTRAINT_DERIVED); |
| src1.6.5/tests/recovery_evidence_tests.cpp:71 | main | ContainerSource,EvidenceSource | D | True | False | assert(explicit_info->ContainerSource(2) == EvidenceSource::EXPLICIT_INFO); |
| src1.6.5/tests/recovery_evidence_tests.cpp:73 | main | IsContainerStateVerified | D | True | False | assert(!explicit_info->IsContainerStateVerified(2)); |
| src1.6.5/tests/recovery_evidence_tests.cpp:78 | main | location | D | True | False | // must-near inference, even if the robot stands at one reported location. |
| src1.6.5/tests/recovery_evidence_tests.cpp:80 | main | hold,plate | D | True | False | "(hold 0) (plate 0) (at 0 4) " |
| src1.6.5/tests/recovery_evidence_tests.cpp:88 | main | IsLocationVerified | D | True | False | assert(!conflict->IsLocationVerified(3)); |
| src1.6.5/tests/recovery_evidence_tests.cpp:92 | main | hold,plate | D | True | False | "(hold 0) (plate 0) (at 0 2) " |
| src1.6.5/tests/recovery_evidence_tests.cpp:100 | main | location | D | True | False | assert(weak->objects[3]->location == 2); |
| src1.6.5/tests/recovery_evidence_tests.cpp:101 | main | EvidenceSource,LocationSource | D | True | False | assert(weak->LocationSource(3) == EvidenceSource::CONSTRAINT_HEURISTIC); |
| src1.6.5/tests/recovery_evidence_tests.cpp:102 | main | IsLocationVerified | D | True | False | assert(!weak->IsLocationVerified(3)); |
| src1.6.5/tests/recovery_evidence_tests.cpp:108 | main | hold,plate | D | True | False | "(hold 0) (plate 0) (at 0 2) " |
| src1.6.5/tests/recovery_evidence_tests.cpp:114 | main | location | D | True | False | changed->objects[2]->location = 4; |
| src1.6.5/tests/recovery_evidence_tests.cpp:126 | main | location | D | True | False | assert(changed->location == 2 && changed->objects[2]->location == 4); |
| src1.6.5/tests/recovery_evidence_tests.cpp:145 | main | hold,plate | D | True | False | "(hold 0) (plate 0) (at 0 2) " |
| src1.6.5/tests/recovery_evidence_tests.cpp:149 | main | hold,plate | D | True | False | "(hold 0) (plate 0) (at 0 2) (sort 1 human) (size 1 big) (at 1 1) " |
| src1.6.5/tests/score_semantics_tests.cpp:28 | declaration/inline | hold,plate | D | True | False | "(hold 0) (plate 0) (at 0 1) " |
| src1.6.5/tests/score_semantics_tests.cpp:31 | declaration/inline | inside | D | True | False | "(sort 3 cup) (size 3 small) (color 3 red) (inside 3 2) (at 3 1) " |
| src1.6.5/tests/score_semantics_tests.cpp:124 | main | hold | D | True | False | carried.replace(carried.find("(hold 0)"), 8, "(hold 3)"); |
| src1.6.5/tests/score_semantics_tests.cpp:125 | main | inside | D | True | False | carried.replace(carried.find("(inside 3 2)"), 12, ""); |
| src1.6.5/tests/score_semantics_tests.cpp:144 | main | containerStateVerified | D | True | False | w->containerStateVerified[2] = false; |
| src1.6.5/tests/score_semantics_tests.cpp:147 | main | containerStateVerified | D | True | False | w->containerStateVerified[2] = true; |
| src1.6.5/tests/score_semantics_tests.cpp:148 | main | isOpen | D | True | False | std::dynamic_pointer_cast<Container>(w->objects[2])->isOpen = 1; |
| src1.6.5/tests/score_semantics_tests.cpp:157 | main | EvidenceSource,containerStateSource | D | True | False | w->containerStateSource[2] = EvidenceSource::CONSTRAINT_DERIVED; |
| src1.6.5/tests/score_semantics_tests.cpp:158 | main | isOpen | D | True | False | std::dynamic_pointer_cast<Container>(w->objects[2])->isOpen = 0; |
| src1.6.5/tests/state_invariant_tests.cpp:42 | main | hold,plate | D | True | False | assert(w->ParseEnv("(hold 0) (plate 0) (at 0 1) " |
| src1.6.5/tests/state_invariant_tests.cpp:45 | main | inside | D | True | False | "(sort 3 cup) (size 3 small) (color 3 red) (inside 3 2) " |
| src1.6.5/tests/state_invariant_tests.cpp:51 | main | location | D | True | False | assert(a.id==7 && a.location==11 && b.id==8 && b.location==12); |
| src1.6.5/tests/state_invariant_tests.cpp:52 | main | location | D | True | False | assert(d.id==9 && d.location==13); |
| src1.6.5/tests/state_invariant_tests.cpp:55 | main | IsLocationVerified,location | D | True | False | assert(c->location==w->location && w->IsLocationVerified(2)); |
| src1.6.5/tests/state_invariant_tests.cpp:56 | main | IsLocationVerified,location | D | True | False | assert(s->location==c->location && !w->IsLocationVerified(3)); |
| src1.6.5/tests/state_invariant_tests.cpp:59 | main | inside | D | True | False | assert(s->inside==NONE && c->smallObjectsInside.empty()); |
| src1.6.5/tests/state_invariant_tests.cpp:60 | main | hold,hold_id | D | True | False | assert(w->hold==s && w->hold_id==3); |
| src1.6.5/tests/state_invariant_tests.cpp:62 | main | hold,plate | D | True | False | assert(!w->hold && w->plate==s); |
| src1.6.5/tests/state_invariant_tests.cpp:64 | main | location | D | True | False | assert(s->location==5); |
| src1.6.5/tests/state_invariant_tests.cpp:66 | main | hold,plate | D | True | False | assert(!w->plate && w->hold==s); |
| src1.6.5/tests/state_invariant_tests.cpp:68 | main | hold,inside | D | True | False | assert(!w->hold && s->inside==NONE); |
| src1.6.5/tests/state_invariant_tests.cpp:70 | main | inside | D | True | False | w->ParseInfo(Task("inside",s,w->objects[4])); |
| src1.6.5/tests/state_invariant_tests.cpp:71 | main | inside | D | True | False | w->ParseInfo(Task("inside",s,w->objects[4])); |
| src1.6.5/tests/state_invariant_tests.cpp:79 | main | isOpen,location | D | True | False | c->isOpen=UNKNOWN; c->location=w->location; w->SetHold(s); |
| src1.6.5/tests/state_invariant_tests.cpp:86 | main | inside,isOpen,location | D | True | False | int loc=w->location, sloc=s->location, in=s->inside, op=c->isOpen; |
| src1.6.5/tests/state_invariant_tests.cpp:89 | main | inside,location | D | True | False | assert(w->location==loc && s->location==sloc && s->inside==in); |
| src1.6.5/tests/state_invariant_tests.cpp:90 | main | isOpen | D | True | False | assert(c->isOpen==op && c->smallObjectsInside==contents); |
| src1.6.5/tests/state_invariant_tests.cpp:93 | main | location | D | True | False | w->stage=1; c->location=w->location; s->location=w->location; |
| src1.6.5/tests/state_invariant_tests.cpp:94 | main | isOpen | D | True | False | c->isOpen=1; w->tasks.push_back(Task("takeout",s,c)); |
| src1.6.5/tests/state_invariant_tests.cpp:97 | main | hold_id,inside | D | True | False | assert(p.dry_run_succeeded && w->hold_id==NONE && s->inside==2); |
| src1.6.5/tests/state_invariant_tests.cpp:104 | main | location | D | True | False | c->location=1; s->location=1; w->SetSenseResult({2}); |
| src1.6.5/tests/state_invariant_tests.cpp:107 | main | IsLocationVerified | D | True | False | assert(!w->IsLocationVerified(3)); |
| src1.6.5/tests/state_invariant_tests.cpp:111 | main | location | D | True | False | w->objects[4]->location=UNKNOWN; |
| src1.6.5/tests/state_invariant_tests.cpp:113 | main | location | D | True | False | assert(w->objects[4]->location==4); |
| src1.6.5/tests/state_invariant_tests.cpp:114 | main | location,objectLocationVerified | D | True | False | c->location=1; w->objectLocationVerified[2]=true; |
| src1.6.5/tests/state_invariant_tests.cpp:115 | main | objectLocationInferredByMustNear | D | True | False | w->objectLocationInferredByMustNear[2]=false; |
| src1.6.5/tests/state_invariant_tests.cpp:116 | main | EvidenceSource,objectLocationSource | D | True | False | w->objectLocationSource[2]=EvidenceSource::SENSE; |
| src1.6.5/tests/state_invariant_tests.cpp:118 | main | location | D | True | False | assert(w->objects[4]->location==UNKNOWN); |
| src1.6.5/tests/state_invariant_tests.cpp:119 | main | IsLocationVerified | D | True | False | assert(!w->IsLocationVerified(4)); |
| src1.6.5/tests/state_invariant_tests.cpp:121 | main | inside,location | D | True | False | s->inside=UNKNOWN; s->location=UNKNOWN; |
| src1.6.5/tests/state_invariant_tests.cpp:122 | main | inside | D | True | False | w->SetAskResult("inside(3,4)"); |
| src1.6.5/tests/state_invariant_tests.cpp:125 | main | IsInsideVerified,IsLocationVerified | D | True | False | assert(!w->IsInsideVerified(3) && !w->IsLocationVerified(3)); |
| src1.6.5/tests/state_invariant_tests.cpp:128 | main | isOpen,location | D | True | False | c->location=1; s->location=1; c->isOpen=UNKNOWN; |
| src1.6.5/tests/state_invariant_tests.cpp:130 | main | IsInsideVerified,inside | D | True | False | assert(s->inside==2 && !w->IsInsideVerified(3)); |
| src1.6.5/tests/state_invariant_tests.cpp:136 | main | hold,inside | D | True | False | assert(w->hold==s && s->inside==NONE && c->smallObjectsInside.empty()); |
| src1.6.5/tests/state_invariant_tests.cpp:138 | main | hold,inside | D | True | False | assert(!w->hold && s->inside==2 && c->smallObjectsInside.size()==1); |
| src1.6.5/tests/state_invariant_tests.cpp:139 | main | isOpen,location | D | True | False | assert(c->location==s->location && c->isOpen==1); |
| src1.6.5/tests/state_invariant_tests.cpp:149 | main | inside | D | True | False | auto goal=Task("inside",s,c); w->notnot_infoConstrains.push_back(goal); |
| src1.6.5/tests/state_invariant_tests.cpp:161 | main | objectInsideVerified | D | True | False | w->SetHold(s); w->objectInsideVerified[3]=true; |
| src1.6.5/tests/state_invariant_tests.cpp:164 | main | IsLocationVerified,location | D | True | False | assert(w->location==1 && !w->IsLocationVerified(3)); |
| src1.6.5/tests/state_invariant_tests.cpp:169 | main | objectInsideVerified | D | True | False | w->objectInsideVerified[3]=true; |
| src1.6.5/tests/state_invariant_tests.cpp:171 | main | inside | D | True | False | assert(s->inside==2 && c->smallObjectsInside.size()==1); |
| src1.6.5/tests/state_invariant_tests.cpp:173 | main | IsInsideVerified,inside | D | True | False | assert(s->inside==2 && w->IsInsideVerified(3)); |
| src1.6.5/tests/state_invariant_tests.cpp:174 | main | inside,objectInsideVerified | D | True | False | s->inside=UNKNOWN; w->objectInsideVerified[3]=false; |
| src1.6.5/tests/state_invariant_tests.cpp:176 | main | IsInsideVerified,inside | D | True | False | assert(s->inside==UNKNOWN && !w->IsInsideVerified(3)); |
| src1.6.5/tests/state_invariant_tests.cpp:184 | main | hold_id,plate,plate_id | D | True | False | assert(w->hold_id==3 && w->plate_id==NONE && !w->plate); |
| src1.6.5/tests/state_invariant_tests.cpp:187 | main | location | D | True | False | w->objects[4]->location=UNKNOWN; |
| src1.6.5/tests/state_invariant_tests.cpp:189 | main | EvidenceSource,LocationSource | D | True | False | assert(w->LocationSource(2)==EvidenceSource::INITIAL); |
| src1.6.5/tests/state_invariant_tests.cpp:190 | main | EvidenceSource,LocationSource | D | True | False | assert(w->LocationSource(4)==EvidenceSource::CONSTRAINT_HEURISTIC); |
| src1.6.5/tests/state_invariant_tests.cpp:192 | main | location | D | True | False | assert(w->objects[2]->location==4 && w->objects[4]->location==4); |
| src1.6.5/tests/state_invariant_tests.cpp:193 | main | IsLocationVerified | D | True | False | assert(!w->IsLocationVerified(4)); |
| src1.6.5/tests/state_invariant_tests.cpp:194 | main | location,objectLocationVerified | D | True | False | c->location=UNKNOWN; w->objectLocationVerified[2]=false; |
| src1.6.5/tests/state_invariant_tests.cpp:196 | main | location | D | True | False | assert(w->objects[4]->location==UNKNOWN); |
| src1.6.5/tests/state_invariant_tests.cpp:198 | main | inside | D | True | False | w->notnot_infoConstrains.push_back(Task("inside",s,c)); |
| src1.6.5/tests/state_invariant_tests.cpp:200 | main | EvidenceSource,InsideSource | D | True | False | assert(w->InsideSource(3)==EvidenceSource::CONSTRAINT_DERIVED); |
| src1.6.5/tests/state_invariant_tests.cpp:203 | main | location | D | True | False | assert(s->location==1); |
| src1.6.5/tests/state_invariant_tests.cpp:204 | main | EvidenceSource,LocationSource | D | True | False | assert(w->LocationSource(3)==EvidenceSource::CONSTRAINT_DERIVED); |
| src1.6.5/tests/state_invariant_tests.cpp:209 | main | isOpen,location | D | True | False | c->location=1; s->location=1; c->isOpen=UNKNOWN; |
| src1.6.5/tests/state_invariant_tests.cpp:211 | main | inside,location | D | True | False | assert(s->inside==2 && s->location==1); |
| src1.6.5/tests/state_invariant_tests.cpp:212 | main | IsLocationVerified | D | True | False | assert(!w->IsLocationVerified(3)); |
| src1.6.5/tests/state_invariant_tests.cpp:214 | main | isOpen | D | True | False | c->isOpen=UNKNOWN; |
| src1.6.5/tests/state_invariant_tests.cpp:217 | main | IsContainerStateVerified,isOpen | D | True | False | assert(c->isOpen==1 && w->IsContainerStateVerified(2)); |
| src1.6.5/tests/state_layer_tests.cpp:24 | main | hold,plate | D | True | False | assert(w->ParseEnv("(hold 0) (plate 0) (at 0 1) " |
| src1.6.5/tests/state_layer_tests.cpp:27 | main | inside | D | True | False | "(sort 3 cup) (size 3 small) (inside 3 2)")); |
| src1.6.5/tests/state_layer_tests.cpp:31 | main | Provenance | D | True | False | const auto& p=w->Provenance(StateField::LOCATION,2); |
| src1.6.5/tests/state_layer_tests.cpp:33 | main | EvidenceSource | D | True | False | assert(p.received.source==EvidenceSource::INITIAL); |
| src1.6.5/tests/state_layer_tests.cpp:34 | main | IsLocationVerified | D | True | False | assert(p.resolved_value==4 && !w->IsLocationVerified(2)); |
| src1.6.5/tests/state_layer_tests.cpp:38 | main | IsLocationVerified,location | D | True | False | assert(c->location==5 && !w->IsLocationVerified(2)); |
| src1.6.5/tests/state_layer_tests.cpp:39 | main | Provenance | D | True | False | assert(w->Provenance(StateField::LOCATION,2).resolved_value==UNKNOWN); |
| src1.6.5/tests/state_layer_tests.cpp:40 | main | EvidenceSource,Provenance | D | True | False | assert(w->Provenance(StateField::LOCATION,2).received.source==EvidenceSource::ASK_ANSWER); |
| src1.6.5/tests/state_layer_tests.cpp:43 | main | Provenance | D | True | False | const auto& p=w->Provenance(StateField::CONTAINER_STATE,2); |
| src1.6.5/tests/state_layer_tests.cpp:44 | main | isOpen | D | True | False | assert(c->isOpen==1 && p.resolved_value==1); |
| src1.6.5/tests/state_layer_tests.cpp:45 | main | EvidenceSource,IsContainerStateVerified | D | True | False | assert(p.received.source==EvidenceSource::ACTION_SUCCESS && w->IsContainerStateVerified(2)); |
| src1.6.5/tests/state_layer_tests.cpp:48 | main | IsContainerStateVerified,isOpen | D | True | False | assert(c->isOpen==0 && !w->IsContainerStateVerified(2)); |
| src1.6.5/tests/state_layer_tests.cpp:49 | main | EvidenceSource,Provenance | D | True | False | assert(w->Provenance(StateField::CONTAINER_STATE,2).received.source==EvidenceSource::INITIAL); |
| src1.6.5/tests/state_layer_tests.cpp:52 | main | location | D | True | False | assert(c->location==UNKNOWN && w->HasContradictoryEvidence(StateField::LOCATION,2)); |
| src1.6.5/tests/state_layer_tests.cpp:53 | main | IsLocationVerified | D | True | False | assert(!w->IsLocationVerified(2)); |
| src1.6.5/tests/state_layer_tests.cpp:57 | main | location | D | True | False | w->objects[1]->location=UNKNOWN; |
| src1.6.5/tests/state_layer_tests.cpp:58 | main | EvidenceSource,location | D | True | False | c->location=1; w->MarkDirectLocationEvidence(2,true,EvidenceSource::SENSE); |
| src1.6.5/tests/state_layer_tests.cpp:60 | main | location | D | True | False | assert(w->objects[1]->location==1); |
| src1.6.5/tests/state_layer_tests.cpp:61 | main | Provenance | D | True | False | assert(w->Provenance(StateField::LOCATION,1).dependency_count>0); |
| src1.6.5/tests/state_layer_tests.cpp:66 | main | EvidenceSource,location | D | True | False | c->location=5; w->MarkDirectLocationEvidence(2,true,EvidenceSource::SENSE); |
| src1.6.5/tests/state_layer_tests.cpp:67 | main | DependenciesCurrent | D | True | False | assert(!w->DependenciesCurrent(StateField::LOCATION,1)); |
| src1.6.5/tests/state_layer_tests.cpp:68 | main | IsLocationVerified | D | True | False | assert(!w->IsLocationVerified(1)); |
| src1.6.5/tests/state_layer_tests.cpp:73 | main | EvidenceSource,location | D | True | False | c->location=1; w->MarkDirectLocationEvidence(2,true,EvidenceSource::SENSE); |
| src1.6.5/tests/state_layer_tests.cpp:74 | main | location | D | True | False | w->objects[1]->location=UNKNOWN; |
| src1.6.5/tests/state_layer_tests.cpp:80 | main | Provenance | D | True | False | const auto derived_before=w->Provenance(StateField::LOCATION,1); |
| src1.6.5/tests/state_layer_tests.cpp:83 | main | Provenance | D | True | False | auto before=w->Provenance(StateField::LOCATION,2); |
| src1.6.5/tests/state_layer_tests.cpp:86 | main | Provenance | D | True | False | const auto& after=w->Provenance(StateField::LOCATION,2); |
| src1.6.5/tests/state_layer_tests.cpp:89 | main | Provenance | D | True | False | const auto& derived_after=w->Provenance(StateField::LOCATION,1); |
| src1.6.5/tests/state_layer_tests.cpp:100 | main | ResolvedState | D | True | False | assert(w->ResolvedState(StateField::LOCATION,1).present); |
| src1.6.5/tests/state_layer_tests.cpp:102 | main | location | D | True | False | w->stage=1; c->location=1; |
| src1.6.5/tests/state_layer_tests.cpp:113 | main | Provenance | D | True | False | assert(w->Provenance(StateField::CONTAINER_STATE,2).resolved_value==1); |
| src1.6.5/tests/state_layer_tests.cpp:114 | main | ContainerSource,EvidenceSource | D | True | False | assert(w->ContainerSource(2)==EvidenceSource::ACTION_SUCCESS); |
| src1.6.5/tests/state_layer_tests.cpp:117 | main | EvidenceSource,inside | D | True | False | s->inside=UNKNOWN; w->SetInsideEvidence(3,false,EvidenceSource::UNKNOWN); |
| src1.6.5/tests/state_layer_tests.cpp:123 | main | EvidenceSource,Provenance | D | True | False | assert(w->Provenance(StateField::CONTAINER_STATE,2).received.source==EvidenceSource::EXPLICIT_INFO); |
| src1.6.5/tests/state_layer_tests.cpp:124 | main | IsContainerStateVerified | D | True | False | assert(!w->IsContainerStateVerified(2)); |
| src1.6.5/tests/state_layer_tests.cpp:128 | main | location | D | True | False | assert(w->location==5); |
| src1.6.5/tests/state_layer_tests.cpp:129 | main | IsInsideVerified | D | True | False | assert(!w->IsInsideVerified(3)); |
| src1.6.5/tests/state_layer_tests.cpp:133 | main | inside,location | D | True | False | assert(s->inside==NONE && s->location==5); |
| src1.6.5/tests/state_layer_tests.cpp:134 | main | Provenance | D | True | False | assert(w->Provenance(StateField::INSIDE,3).resolved_value==UNKNOWN); |
| src1.6.5/tests/state_layer_tests.cpp:135 | main | Provenance | D | True | False | assert(w->Provenance(StateField::LOCATION,3).resolved_value==UNKNOWN); |
| src1.6.5/tests/state_layer_tests.cpp:139 | main | inside | D | True | False | assert(w->ParseEnvSentence("(inside 3 1)")); |
| src1.6.5/tests/state_layer_tests.cpp:140 | main | inside | D | True | False | assert(s->inside==UNKNOWN); |
| src1.6.5/tests/state_layer_tests.cpp:143 | main | inside | D | True | False | Instruction must=Goal("inside",s); must.Y.push_back(c); |
| src1.6.5/tests/state_layer_tests.cpp:146 | main | IsInsideVerified | D | True | False | assert(w->IsInsideVerified(3)); |
| src1.6.5/tests/state_layer_tests.cpp:147 | main | Provenance | D | True | False | assert(w->Provenance(StateField::INSIDE,3).support_constraint_index==0); |
| src1.6.5/tests/state_layer_tests.cpp:149 | main | IsInsideVerified | D | True | False | assert(!w->IsInsideVerified(3)); |
| src1.6.5/tests/state_layer_tests.cpp:151 | main | EvidenceSource,Provenance | D | True | False | assert(w->Provenance(StateField::HOLD,0).received.source==EvidenceSource::INITIAL); |
| src1.6.5/tests/state_layer_tests.cpp:152 | main | Provenance | D | True | False | assert(w->Provenance(StateField::PLATE,0).resolved_value==NONE); |
| src1.6.5/tests/state_layer_tests.cpp:154 | main | Provenance | D | True | False | assert(w->Provenance(StateField::HOLD,0).resolved_value==3); |
| src1.6.5/tests/state_layer_tests.cpp:155 | main | Provenance | D | True | False | assert(w->Provenance(StateField::HOLD,0).resolved_verified); |
| src1.6.5/tests/state_layer_tests.cpp:156 | main | EvidenceSource,Provenance | D | True | False | assert(w->Provenance(StateField::HOLD,0).received.source==EvidenceSource::ACTION_SUCCESS); |
| src1.6.5/tests/state_layer_tests.cpp:160 | main | ResolvedState | D | True | False | assert(w->ResolvedState(StateField::CONTAINER_STATE,2).present); |
| src1.6.5/tests/state_layer_tests.cpp:161 | main | Provenance | D | True | False | assert(w->Provenance(StateField::CONTAINER_STATE,2).supporting_constraints.size()==1); |
| src1.6.5/tests/state_layer_tests.cpp:163 | main | DependenciesCurrent | D | True | False | assert(!w->DependenciesCurrent(StateField::CONTAINER_STATE,2)); |
| src1.6.5/tests/state_layer_tests.cpp:164 | main | ResolvedState | D | True | False | assert(!w->ResolvedState(StateField::CONTAINER_STATE,2).present); |
| src1.6.5/tests/state_layer_tests.cpp:165 | main | IsContainerStateVerified | D | True | False | assert(!w->IsContainerStateVerified(2)); |
| src1.6.5/tests/state_layer_tests.cpp:167 | main | EvidenceSource,location | D | True | False | c->location=1; w->MarkDirectLocationEvidence(2,true,EvidenceSource::SENSE); |
| src1.6.5/tests/state_layer_tests.cpp:168 | main | location | D | True | False | w->objects[1]->location=UNKNOWN; |
| src1.6.5/tests/state_layer_tests.cpp:172 | main | ResolvedState | D | True | False | assert(w->ResolvedState(StateField::LOCATION,1).present); |
| src1.6.5/tests/state_layer_tests.cpp:173 | main | Provenance | D | True | False | assert(w->Provenance(StateField::LOCATION,1).supporting_constraints.size()==1); |
| src1.6.5/tests/state_layer_tests.cpp:175 | main | ResolvedState | D | True | False | assert(!w->ResolvedState(StateField::LOCATION,1).present); |
| src1.6.5/tests/state_layer_tests.cpp:179 | main | ResolvedState | D | True | False | assert(!w->ResolvedState(StateField::LOCATION,2).present); |
| src1.6.5/tests/state_layer_tests.cpp:181 | main | ResolvedState | D | True | False | assert(w->ResolvedState(StateField::LOCATION,2).value==1); |
| src1.6.5/tests/state_layer_tests.cpp:183 | main | DependenciesCurrent | D | True | False | assert(!w->DependenciesCurrent(StateField::LOCATION,2)); |
| src1.6.5/tests/state_layer_tests.cpp:184 | main | ResolvedState | D | True | False | assert(!w->ResolvedState(StateField::LOCATION,2).present); |
| src1.6.5/tests/task_group_projection_tests.cpp:24 | main | hold,plate | D | True | False | "(hold 0) (plate 0) (at 0 1) " |
| src1.6.5/tests/task_group_projection_tests.cpp:31 | main | location | D | True | False | const int initial_location = world.location; |
| src1.6.5/tests/task_group_projection_tests.cpp:39 | main | location | D | True | False | assert(world.location == initial_location); |
| src1.6.5/tests/task_group_projection_tests.cpp:46 | main | location | D | True | False | assert(world.location == initial_location); |
| src1.6.5/tests/task_group_projection_tests.cpp:58 | main | location | D | True | False | assert(world.location == initial_location); |
| src1.6.5/tests/task_group_projection_tests.cpp:67 | main | hold,plate | D | True | False | "(hold 0) (plate 0) (at 0 1) " |
| src1.6.5/tests/three_a_tests.cpp:28 | main | hold,plate | D | True | False | " (hold 0) (plate 0) (at 0 4) " |
| src1.6.5/tests/three_a_tests.cpp:67 | main | containerStateVerified | D | True | False | world->containerStateVerified[2] = false; |
| src1.6.5/tests/three_a_tests.cpp:70 | main | containerStateVerified | D | True | False | world->containerStateVerified[2] = true; |
| src1.6.5/tests/three_a_tests.cpp:82 | main | isOpen | D | True | False | std::dynamic_pointer_cast<Container>(world->objects[2])->isOpen = false; |
| src1.6.5/tests/three_a_tests.cpp:83 | main | location | D | True | False | const int location_before_preview = world->location; |
| src1.6.5/tests/three_a_tests.cpp:104 | main | location | D | True | False | assert(world->location == location_before_preview); |
| src1.6.5/tests/three_a_tests.cpp:105 | main | isOpen | D | True | False | assert(!std::dynamic_pointer_cast<Container>(world->objects[2])->isOpen); |
| src1.6.5/tests/three_a_tests.cpp:114 | main | location | D | True | False | world->location = 3; |
| src1.6.5/tests/three_a_tests.cpp:120 | main | location | D | True | False | assert(world->location == 3 && world->objects[2]->location == 4); |
