#pragma once
#include "candidate_plan.hpp"
#include <map>
#include <string>
#include <vector>

namespace _home {
enum class StateField;
struct ProbePolicy {
    std::size_t max_total_probes_per_problem = 8;
    std::size_t max_same_probe = 2;
    std::size_t max_same_ask = 3;
    int max_total_probe_cost = 32;
    std::size_t max_probe_constraint_risks = 2;
};
struct BlockingFact {
    std::size_t task_index = 0, stable_task_id = 0;
    StateField field = static_cast<StateField>(0);
    unsigned int object_id = 0;
    std::string reason;
    std::map<int, std::string> location_hints;
};
enum class ProbeKind { SENSE_CURRENT_LOCATION_ONLY, MOVE_AND_SENSE, ASK_LOCATION, OPEN_AND_SENSE };
struct ProbeCandidate {
    ProbeKind kind = ProbeKind::SENSE_CURRENT_LOCATION_ONLY;
    int target_location = -1;
    unsigned target_object = 0;
    double information_estimate = 0, expected_gain = 0;
    int continuation_cost = 0;
    std::size_t continuation_bundles = 1;
    std::vector<std::size_t> constraint_risks;
    std::size_t world_revision = 0, stable_id = 0;
    std::string signature, fact_context, state_before;
    std::vector<BlockingFact> facts;
    std::vector<std::size_t> task_indices;
    std::vector<CandidateAction> actions;
    bool eligible = false;
    int potential_goal_value = 0, action_cost = 0;
    std::chrono::milliseconds estimated_duration{0}, continuation_duration{0};
    std::string constraint_result = "constraint_safe", rejection;
};
struct ProbeExecutionRecord {
    ProbeCandidate candidate;
    std::size_t revision_before = 0, revision_after = 0, issued_actions = 0;
    bool received_feedback = false, sense_attempted = false, move_failed = false;
    bool related_new_evidence = false, effective = false;
    std::size_t sense_evidence_changes = 0, action_success_evidence_changes = 0;
    std::size_t action_failure_evidence_changes = 0;
    std::vector<std::size_t> restored_tasks, completed_tasks;
    std::string failure, context_after, ask_reply;
};
struct ProbeHistory {
    std::size_t attempts = 0, world_revision = 0;
    bool related_new_evidence = false, answer_usable = false;
    std::string context_after;
    std::map<std::pair<StateField, unsigned int>, std::string> fact_contexts_after;
};
} // namespace _home
