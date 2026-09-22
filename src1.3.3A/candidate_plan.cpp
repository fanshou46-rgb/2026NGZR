#include "candidate_plan.hpp"

#include <algorithm>

namespace _home {
namespace {

std::chrono::milliseconds deterministicDuration(ActionCategory category) {
    // These are deterministic execution-budget constants, not probabilities.
    // DeadlineManager only sees their sum for the complete remaining plan.
    switch (category) {
    case ActionCategory::MOVE:
        return std::chrono::milliseconds(120);
    case ActionCategory::HUMAN_INTERACTION:
    case ActionCategory::PHYSICAL:
    case ActionCategory::OBSERVATION:
        return std::chrono::milliseconds(100);
    }
    return std::chrono::milliseconds(100);
}

int terminalPoints(const ScoreSnapshot& snapshot) {
    const int goal_points = static_cast<int>(snapshot.completed_goals) * 40;
    const int constraint_points = snapshot.completed_goals == 0
        ? 0 : static_cast<int>(snapshot.satisfied_constraints) * 20;
    return goal_points + constraint_points;
}

} // namespace

CandidateAction::CandidateAction()
    : name(), arguments(), category(ActionCategory::PHYSICAL), cost(0),
      estimated_duration(0) {
}

CandidateAction::CandidateAction(
    const std::string& action_name,
    const std::vector<unsigned int>& action_arguments,
    ActionCategory action_category)
    : name(action_name), arguments(action_arguments), category(action_category),
      cost(ScoreEvaluator::costForAction(action_category)),
      estimated_duration(deterministicDuration(action_category)) {
}

CandidatePlan::CandidatePlan()
    : task_index(0), task_label(), eligible(false), dry_run_succeeded(false),
      actions(), terminal_before(), terminal_after(), score_before(),
      score_after(), gained_goals(), lost_goals(), broken_constraints(),
      preserved_constraints(), action_cost(0), marginal_score(0), utility(0),
      estimated_duration(0), executed_actions(0) {
}

int CandidatePlan::remainingActionCost() const {
    int result = 0;
    const std::size_t begin = std::min(executed_actions, actions.size());
    for (std::size_t i = begin; i < actions.size(); ++i)
        result += actions[i].cost;
    return result;
}

std::chrono::milliseconds CandidatePlan::remainingDuration() const {
    std::chrono::milliseconds result(0);
    const std::size_t begin = std::min(executed_actions, actions.size());
    for (std::size_t i = begin; i < actions.size(); ++i)
        result += actions[i].estimated_duration;
    return result;
}

int CandidatePlan::remainingUtility(const ScoreSnapshot& current) const {
    const int projected_score = terminalPoints(score_after) -
        current.action_cost - remainingActionCost();
    return projected_score - current.deterministic_base_score;
}

CandidatePlan CandidatePlanEvaluator::evaluate(
    std::size_t task_index,
    const std::string& task_label,
    bool eligible,
    bool dry_run_succeeded,
    const std::vector<CandidateAction>& actions,
    const TerminalSummary& terminal_before,
    const TerminalSummary& terminal_after,
    const ScoreSnapshot& score_before,
    const ScoreSnapshot& score_after) {
    CandidatePlan result;
    result.task_index = task_index;
    result.task_label = task_label;
    result.eligible = eligible;
    result.dry_run_succeeded = dry_run_succeeded;
    result.actions = actions;
    result.terminal_before = terminal_before;
    result.terminal_after = terminal_after;
    result.score_before = score_before;
    result.score_after = score_after;

    const std::size_t goal_count = std::min(
        terminal_before.goals.size(), terminal_after.goals.size());
    for (std::size_t i = 0; i < goal_count; ++i) {
        if (terminal_before.goals[i] != TerminalStatus::SATISFIED &&
            terminal_after.goals[i] == TerminalStatus::SATISFIED)
            result.gained_goals.push_back(i);
        if (terminal_before.goals[i] == TerminalStatus::SATISFIED &&
            terminal_after.goals[i] != TerminalStatus::SATISFIED)
            result.lost_goals.push_back(i);
    }

    const std::size_t constraint_count = std::min(
        terminal_before.constraints.size(), terminal_after.constraints.size());
    for (std::size_t i = 0; i < constraint_count; ++i) {
        if (terminal_after.constraints[i] == TerminalStatus::UNSATISFIED &&
            terminal_before.constraints[i] != TerminalStatus::UNSATISFIED)
            result.broken_constraints.push_back(i);
        if (terminal_before.constraints[i] == TerminalStatus::SATISFIED &&
            terminal_after.constraints[i] == TerminalStatus::SATISFIED)
            result.preserved_constraints.push_back(i);
    }

    for (std::size_t i = 0; i < actions.size(); ++i) {
        result.action_cost += actions[i].cost;
        result.estimated_duration += actions[i].estimated_duration;
    }
    result.marginal_score = score_after.deterministic_base_score -
                            score_before.deterministic_base_score;
    result.utility = result.marginal_score;
    return result;
}

} // namespace _home
