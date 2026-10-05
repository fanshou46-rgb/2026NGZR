#include "task_group_search.hpp"
#include <cassert>
#include <stdexcept>
using namespace _home;
static CandidatePlan plan(const std::vector<std::size_t>& ids,int value) {
    CandidatePlan p;p.task_indices=ids;p.task_index=ids.front();p.eligible=true;
    p.dry_run_succeeded=true;p.score_after.deterministic_base_score=value;return p;
}
int main() {
    auto a=plan({0},-10),b=plan({1},-10);
    TaskGroupSearchOptions o;o.max_depth=3;o.max_evaluations=3;
    auto p=[](const std::vector<std::size_t>& ids) {return plan(ids,80);};
    for(int repeat=0;repeat<50;++repeat) {
        auto r=SearchTaskGroups({a,b},p,o);
        assert(r.work_exhausted && !r.budget_exhausted && r.evaluated==3);
        assert(r.has_safe && r.best_safe.score_after.deterministic_base_score==80);
        assert(r.best_safe.task_indices==std::vector<std::size_t>({0,1}));
    }
    o.max_evaluations=0;int calls=0;
    auto r=SearchTaskGroups({a,b},[&](const std::vector<std::size_t>& ids) {
        if(++calls==2)throw std::runtime_error("later projection interrupted");
        return plan(ids,80);
    },o);
    assert(r.projection_failed && r.has_safe);
    assert(r.best_safe.task_indices==std::vector<std::size_t>({0,1}));
    // A failed projection cannot donate its attractive, unfinished suffix.
    calls=0;
    r=SearchTaskGroups({a,b},[&](const std::vector<std::size_t>& ids) {
        auto p=plan(ids,9999);p.dry_run_succeeded=false;return p;
    },o);
    assert(r.best_safe.score_after.deterministic_base_score==-10);
}
