#include "rdfw.hpp"
#include <cassert>
#include <cstdlib>
#include <memory>
#include <thread>

namespace _home {
struct UnifiedSchedulerTestAccess {
    static std::vector<CandidatePlan> Candidates(RDFW& w, bool gotos = true) {
        return w.EvaluateShadowCandidates("unit", gotos, static_cast<std::size_t>(-1));
    }
    static const CandidatePlan* Select(RDFW& w, const std::vector<CandidatePlan>& p) {
        return w.SelectGreedyCandidate(p);
    }
    static void Greedy(RDFW& w, bool defer = false) {
        w.task_group_search_used = std::chrono::milliseconds(100);
        w.ExecuteMainTaskLoop(defer);
    }
    static bool Guard(RDFW& w, bool defer = false) {
        auto roots = Candidates(w, !defer);
        return w.TryGuardedDecision(defer, 0, roots) != RDFW::GuardedDecisionOutcome::USE_GREEDY;
    }
    static void Budget(RDFW& w, int ms) { w.deadline_manager.reset(std::chrono::milliseconds(ms)); }
    static void Cpu(RDFW& w, int ms) { w.task_group_search_used = std::chrono::milliseconds(ms); }
    static void Stop(RDFW& w) { w.normal_stop_requested = true; }
    static void Fail(RDFW& w, std::size_t id) {
        w.failed_task_revision.assign(w.tasks.size(), RDFW::NO_FAILED_REVISION);
        w.failed_task_revision[id] = w.world_revision;
        w.tasks[id].isEnable = false;
    }
    static void Revise(RDFW& w) { ++w.world_revision; }
    static void Cap(RDFW& w, std::size_t id) {
        w.task_attempts.resize(w.tasks.size()); w.task_attempts[id] = 3;
    }
    static std::string Snapshot(RDFW& w) {
        std::string out = w.PlanStateSignature();
        for (auto v : w.failed_task_revision) out += std::to_string(v) + ',';
        for (auto v : w.task_attempts) out += std::to_string(v) + ',';
        out += std::to_string(w.scheduler_steps) + ':' + std::to_string(w.decision_feedback.size());
        return out;
    }
    static CandidatePlan Horizon(RDFW& w, int ms) {
        w.comparison_time_fixed = true; w.comparison_time_budget = std::chrono::milliseconds(ms);
        const auto p = w.PreviewGreedyContinuation(0, false);
        w.comparison_time_fixed = false;
        return p;
    }
    static bool Stale(RDFW& w, const CandidatePlan& p) { return w.ExecuteGuardedGroup(p); }
    static CandidatePlan Authorize(RDFW& w, const std::vector<std::size_t>& ids) {
        w.capture_action_preconditions = true;
        const auto p = w.PreviewTaskGroupPlan(ids);
        w.capture_action_preconditions = false;
        return p;
    }
    static bool ProgressEqual(RDFW& w) {
        auto before = w.DecisionProgressSignature();
        ++w.world_revision; ++w.solved_task_num; w.score_evaluator.recordAction(ActionCategory::MOVE);
        return before == w.DecisionProgressSignature();
    }
};
}
using namespace _home;
using A = UnifiedSchedulerTestAccess;

static const char* route_env =
    "(hold 0) (plate 0) (at 0 1) "
    "(sort 1 human) (size 1 big) (at 1 1) "
    "(sort 2 cupboard) (size 2 big) (type 2 container) (closed 2) (at 2 2) "
    "(sort 3 closet) (size 3 big) (type 3 container) (opened 3) (at 3 3) "
    "(sort 4 cup) (size 4 small) (at 4 2)";
static const char* route_tasks =
    "(:task (open X) (:cond (sort X cupboard))) "
    "(:task (close X) (:cond (sort X closet))) "
    "(:task (pickup X) (:cond (sort X cup)))";

static std::shared_ptr<RDFW> World(const char* words, const char* env = route_env,
                                   const char* tasks = route_tasks, int stage = 1) {
    auto w = std::make_shared<RDFW>();
    char program[] = "unified_scheduler_tests", option[] = "-path";
    char* args[] = {program, option, const_cast<char*>(words)};
    w->Init(3, args); w->stage = stage;
    assert(w->ParseEnv(env)); assert(w->ParseInstruction(tasks));
    w->Cons_plan(); w->tasks = w->TaskOptimization();
    return w;
}

int main(int argc, char** argv) {
    assert(argc == 3); const int test = std::atoi(argv[2]);
    auto w = World(argv[1]);
    if (test == 0) { // Select after filtering, even with adversarial vector order.
        auto p = A::Candidates(*w);
        assert(p.size() == 3);
        p[0].eligible = false; p[0].marginal_score = 9999;
        p[1].dry_run_succeeded = false; p[1].marginal_score = 9998;
        const auto* best = A::Select(*w, p); assert(best == &p[2]);
    } else if (test == 1) { // Duration, then original stable input ID, break ties.
        auto p = A::Candidates(*w); assert(p.size() == 3);
        for (auto& v : p) { v.marginal_score = 40; v.estimated_duration = std::chrono::milliseconds(400); }
        p[1].estimated_duration = p[2].estimated_duration = std::chrono::milliseconds(100);
        p[1].stable_task_id = 8; p[2].stable_task_id = 3;
        assert(A::Select(*w, p) == &p[2]);
    } else if (test == 2) { // Every real greedy execution is freshly projected.
        const auto first = A::Candidates(*w); const auto selected = A::Select(*w, first)->task_index;
        A::Greedy(*w);
        assert(!w->DecisionFeedback().empty());
        assert(w->DecisionFeedback()[0].candidate.task_index == selected);
        for (std::size_t i = 1; i < w->DecisionFeedback().size(); ++i) {
            const auto& a = w->DecisionFeedback()[i-1]; const auto& b = w->DecisionFeedback()[i];
            assert(b.candidate.world_revision > a.candidate.world_revision);
            assert(b.candidate.score_before.action_cost == a.actual.values.action_cost + a.candidate.score_before.action_cost);
            assert(b.candidate.marginal_score > 0);
        }
    } else if (test == 3) { // First goal activates whole-question constraint credit.
        w = World(argv[1], route_env,
            "(:task (open X) (:cond (sort X cupboard))) "
            "(:cons_notnot (:info (opened X) (:cond (sort X closet))))");
        assert(w->GetScoreSnapshot().deterministic_base_score == 0);
        const auto p = w->PreviewCandidatePlan(0);
        assert(p.marginal_score == 54 && p.score_after.completed_goals == 1);
        assert(p.score_after.satisfied_constraints == 1);
    } else if (test == 4) { // Better route proof; timed search may safely fall back.
        A::Candidates(*w); // initialize scheduler bookkeeping as in production
        const auto reference = w->PreviewGreedyContinuation(0, false);
        const auto proof = A::Authorize(*w, {1,0,2});
        assert(proof.dry_run_succeeded && proof.score_after.deterministic_base_score == 106);
        assert(proof.score_after.deterministic_base_score > reference.score_after.possible_base_score);
        assert(w->TestPlatformCalls() == 0);
        const auto before = A::Snapshot(*w);
        if (A::Guard(*w)) {
            assert(w->GetScoreSnapshot().deterministic_base_score > reference.score_after.possible_base_score);
            assert(w->GetScoreSnapshot().deterministic_base_score == 106);
            assert(w->DecisionFeedback().front().candidate.task_indices.size() == 3);
        } else {
            assert(w->TestPlatformCalls() == 0 && A::Snapshot(*w) == before);
        }
    } else if (test == 5) { // Equal score retains greedy; Stage 2 automatic fallback.
        w = World(argv[1], route_env, "(:task (open X) (:cond (sort X cupboard)))");
        assert(!A::Guard(*w)); assert(w->TestPlatformCalls() == 0);
        w->stage = 2; assert(!A::Guard(*w)); assert(w->TestPlatformCalls() == 0);
    } else if (test == 6) { // Exhausted cumulative budget never restarts per round.
        A::Cpu(*w, 100); assert(!A::Guard(*w));
        A::Revise(*w); assert(!A::Guard(*w)); assert(w->TestPlatformCalls() == 0);
        A::Cpu(*w, 0); A::Budget(*w, 220); assert(!A::Guard(*w));
    } else if (test == 7) { // Failure blocks same revision, reactivation is bounded.
        A::Fail(*w, 0); auto p = A::Candidates(*w);
        for (const auto& v : p) assert(v.task_index != 0);
        A::Revise(*w); p = A::Candidates(*w); bool found = false;
        for (const auto& v : p) found |= v.task_index == 0;
        assert(found); A::Cap(*w, 0); A::Revise(*w); p = A::Candidates(*w);
        for (const auto& v : p) assert(v.task_index != 0);
    } else if (test == 8) { // Failed approved first action aborts and charges once.
        // Exercise actual authorized execution without requiring a wall-clock
        // search win first. Timing fallback is covered independently above.
        A::Candidates(*w);
        const auto approved = A::Authorize(*w, {1,0,2});
        assert(approved.dry_run_succeeded);
        w->SetActionResults({false}); assert(!A::Stale(*w, approved));
        assert(w->TestPlatformCalls() == 1);
        const auto r = w->DecisionFeedback().front();
        assert(!r.actual.succeeded && r.actual.failed_action);
        assert(r.actual.values.action_cost == 4 && r.actual.values.action_count == 1);
        const auto p = A::Candidates(*w);
        for (const auto& v : p) assert(v.task_index != r.candidate.task_indices.front());
    } else if (test == 9) { // State mismatch aborts *before* issuing an action.
        const auto p = A::Authorize(*w, {0,1,2}); assert(p.dry_run_succeeded);
        A::Revise(*w); assert(!A::Stale(*w, p)); assert(w->TestPlatformCalls() == 0);
    } else if (test == 10) { // Simulation restores state, feedback and failures.
        A::Fail(*w, 1); A::Cap(*w, 2);
        const auto before = A::Snapshot(*w);
        const auto p = w->PreviewGreedyContinuation(0, false); assert(p.dry_run_succeeded);
        assert(A::Snapshot(*w) == before); assert(w->TestPlatformCalls() == 0);
    } else if (test == 11) { // A nested greedy forecast consumes the prefix time.
        const auto p = A::Horizon(*w, 550);
        assert(p.dry_run_succeeded);
        assert(p.estimated_duration + std::chrono::milliseconds(200) <= std::chrono::milliseconds(550));
        assert(w->TestPlatformCalls() == 0);
    } else if (test == 12) { // Bookkeeping alone does not count as progress.
        assert(A::ProgressEqual(*w));
        A::Stop(*w); w->ExecuteTerminalRecovery(); assert(w->TestPlatformCalls() == 0);
    } else if (test == 13) { // Single GOTO participates normally.
        w = World(argv[1], route_env, "(:task (goto X) (:cond (sort X cupboard)))");
        A::Greedy(*w); assert(w->GetTerminalSummary().allGoalsSatisfied());
        assert(w->TestPlatformCalls() == 1);
    } else if (test == 14) { // Multi-GOTO stays deferred, guard support unchanged.
        w = World(argv[1], route_env,
            "(:task (goto X) (:cond (sort X cupboard))) (:task (goto X) (:cond (sort X closet)))");
        assert(w->CheckAndDeferMultiGoto()); assert(!A::Guard(*w, true));
        A::Greedy(*w, true); assert(w->TestPlatformCalls() == 0);
        w->ExecuteMultiGotoAggregation();
        assert(w->GetTerminalSummary().satisfied_goals >= 1);
        assert(w->TestPlatformCalls() == 1);
    } else if (test == 15) { // Stable ID remains tied to original task after sorting.
        assert(w->tasks[0].stable_id == 0 && w->tasks[1].stable_id == 1 && w->tasks[2].stable_id == 2);
        std::swap(w->tasks[0], w->tasks[2]);
        auto p = A::Candidates(*w);
        for (const auto& v : p) assert(v.stable_task_id == w->tasks[v.task_index].stable_id);
    } else if (test == 16) { // No positive single can still have a valuable group.
        w = World(argv[1],
            "(hold 4) (plate 0) (at 0 1) (sort 1 human) (size 1 big) (at 1 1) "
            "(sort 2 cupboard) (size 2 big) (type 2 container) (closed 2) (at 2 1) "
            "(sort 3 table) (size 3 big) (at 3 2) (sort 4 cup) (size 4 small) (at 4 1)",
            "(:task (pickup X) (:cond (sort X cup))) "
            "(:task (puton X Y) (:cond (sort X cup) (sort Y table))) "
            "(:task (open X) (:cond (sort X cupboard)))");
        const auto roots = A::Candidates(*w);
        assert(!A::Select(*w, roots));
        assert(A::Guard(*w)); assert(w->GetScoreSnapshot().completed_goals >= 2);
        assert(w->DecisionFeedback().front().candidate.task_indices.size() >= 2);
    } else if (test == 17) { // Missing Y and mixed priority verbs used to form a cycle.
        Instruction a, b, c;
        a.behave = c.behave = "takeout"; b.behave = "putdown";
        a.X = b.X = c.X = {w->objects[4]};
        a.Y = {w->objects[3]}; c.Y = {w->objects[2]};
        w->tasks = {a, b, c}; auto sorted = w->TaskOptimization();
        assert(sorted[0].stable_id == 2 && sorted[1].stable_id == 0 && sorted[2].stable_id == 1);
        a.Y.clear(); c.Y = {nullptr}; w->tasks = {a,b,c}; sorted = w->TaskOptimization();
        assert(sorted[0].stable_id == 0 && sorted[1].stable_id == 2 && sorted[2].stable_id == 1);
    } else if (test == 18) { // Confirmed Stage 2 may use a strictly improving guarded group.
        w->stage = 2; w->ExecuteMainTaskLoop(false);
        assert(!w->DecisionFeedback().empty());
        assert(w->GetTerminalSummary().allGoalsSatisfied());
        for (const auto& r : w->DecisionFeedback()) for (const auto& a : r.candidate.actions)
            assert(a.category != ActionCategory::OBSERVATION && a.category != ActionCategory::HUMAN_INTERACTION);
    } else if (test == 19) { // Failure cannot loop indefinitely with no state changes.
        w->SetActionResults(std::vector<bool>(100, false));
        A::Greedy(*w);
        assert(w->DecisionFeedback().size() <= 3 && w->TestPlatformCalls() <= 3);
        for (const auto& r : w->DecisionFeedback()) assert(!r.actual.succeeded);
    } else { assert(false); }
}
