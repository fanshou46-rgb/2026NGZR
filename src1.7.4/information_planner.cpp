#include "information_planner.hpp"
#include <stdexcept>
#include <cmath>
using namespace _home;

namespace {
AnswerBranch choose(const LocationBelief& belief,const std::vector<VerificationRoute>& routes,
                    std::chrono::milliseconds remaining,bool new_answer=false) {
    AnswerBranch result; // stop has value zero
    for (const auto& route:routes) {
        if (!route.feasible || route.worst_duration>remaining) continue;
        if (route.requires_new_answer && !new_answer) continue;
        const double match=belief.probability(route.hypothesis);
        const double value=match*route.success_value+(1-match)*route.failure_value;
        if (value>result.value) {
            result.value=value; result.selected_route=route.hypothesis; result.posterior_match=match;
        }
    }
    return result;
}
}
InformationValue InformationPlanner::ask(const LocationBelief& belief,const AskObservationModel& model,
    const std::vector<VerificationRoute>& routes,double ask_cost,std::chrono::milliseconds remaining,
    std::chrono::milliseconds ask_duration) {
    if (ask_cost<0) throw std::invalid_argument("negative information action cost");
    for(const auto& route:routes) if(!std::isfinite(route.success_value) || !std::isfinite(route.failure_value) || route.failure_value>0)
        throw std::invalid_argument("invalid verification success/failure value");
    InformationValue result;
    result.direct_value=choose(belief,routes,remaining).value;
    for (auto observation:model.observations()) {
        const double probability=belief.observationProbability(observation,model);
        if (probability<=0) continue;
        auto branch=choose(belief.posterior(observation,model),routes,remaining-ask_duration,
            (observation.first=='a' || observation.first=='i') && belief.probability(observation)>0);
        branch.observation=observation; branch.probability=probability;
        result.after_answer_value+=probability*branch.value;
        result.branches.push_back(branch);
    }
    result.net_value=result.after_answer_value-result.direct_value-ask_cost;
    return result;
}
