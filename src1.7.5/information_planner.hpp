#pragma once
#include "belief_state.hpp"
#include <chrono>
#include <string>
#include <vector>

namespace _home {
// A fixed follow-up verification route, valued against every possible world.
// It is selected from the posterior, never from the hidden true world.
struct VerificationRoute {
    LocationHypothesis hypothesis{'?',-1};
    double success_value=0, failure_value=0;
    std::chrono::milliseconds worst_duration{0};
    bool feasible=false;
    bool requires_new_answer=false;
    int success_cost=0;
    std::string reason;
};
struct AnswerBranch {
    LocationHypothesis observation{'?',-1}, selected_route{'?',-1};
    double probability=0, value=0, posterior_match=0;
};
struct InformationValue {
    double direct_value=0, after_answer_value=0, net_value=0;
    std::vector<AnswerBranch> branches;
};
class InformationPlanner {
public:
    static InformationValue ask(const LocationBelief& belief,const AskObservationModel& model,
                                const std::vector<VerificationRoute>& routes,double ask_cost,
                                std::chrono::milliseconds remaining,
                                std::chrono::milliseconds ask_duration = std::chrono::milliseconds(0));
};
}
