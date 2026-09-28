#pragma once

#include "score_evaluator.hpp"
#include "terminal_checker.hpp"

#include <chrono>
#include <cstddef>
#include <string>
#include <vector>

namespace _home {

struct CandidateAction {
    std::string name;
    std::vector<unsigned int> arguments;
    ActionCategory category;
    int cost;
    std::chrono::milliseconds estimated_duration;

    CandidateAction();
    CandidateAction(const std::string& action_name,
                    const std::vector<unsigned int>& action_arguments,
                    ActionCategory action_category);
};

// A complete action sequence emitted by the existing planner for one task
// group.  Stage 3B only observes and scores these plans; it does not use their
// utility to replace the legacy task choice.
struct CandidatePlan {
    std::size_t task_index;
    std::string task_label;
    bool eligible;
    bool dry_run_succeeded;
    std::vector<CandidateAction> actions;
    TerminalSummary terminal_before;
    TerminalSummary terminal_after;
    ScoreSnapshot score_before;
    ScoreSnapshot score_after;
    std::vector<std::size_t> gained_goals;
    std::vector<std::size_t> lost_goals;
    std::vector<std::size_t> broken_constraints;
    std::vector<std::size_t> preserved_constraints;
    int action_cost;
    int marginal_score;
    int utility;
    std::chrono::milliseconds estimated_duration;
    std::size_t executed_actions;

    CandidatePlan();

    int remainingActionCost() const;
    std::chrono::milliseconds remainingDuration() const;
    int remainingUtility(const ScoreSnapshot& current) const;
};

class CandidatePlanEvaluator {
public:
    static CandidatePlan evaluate(
        std::size_t task_index,
        const std::string& task_label,
        bool eligible,
        bool dry_run_succeeded,
        const std::vector<CandidateAction>& actions,
        const TerminalSummary& terminal_before,
        const TerminalSummary& terminal_after,
        const ScoreSnapshot& score_before,
        const ScoreSnapshot& score_after);
};

} // namespace _home
