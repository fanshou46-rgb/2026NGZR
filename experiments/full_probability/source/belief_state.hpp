#pragma once
#include <map>
#include <set>
#include <utility>
#include "observation_model.hpp"

namespace _home {
// Joint alternatives: ('a', location), ('i', container), ('?', -1).
// A distribution is a planning hint, never authority for a canonical fact.
class LocationBelief {
public:
    typedef LocationHypothesis Hypothesis;
    void initialize(const std::set<Hypothesis>& domain, Hypothesis hint);
    bool answer(Hypothesis observation, std::size_t event_id = 0);
    bool observe(Hypothesis observation, const AskObservationModel& model, std::size_t event_id = 0);
    LocationBelief posterior(Hypothesis observation, const AskObservationModel& model) const;
    double observationProbability(Hypothesis observation, const AskObservationModel& model) const;
    void ruleOut(Hypothesis observation);
    // Apply only hard visibility contradictions. Unknown doors/locations retain
    // alternatives; no independence or calibrated visibility probability is assumed.
    bool filterVisibility(int location, bool visible,
                          const std::map<int,std::pair<int,int>>& containers, bool coexistence=false);
    void confirm(Hypothesis hypothesis);
    double probability(Hypothesis h) const;
    const std::map<Hypothesis,double>& distribution() const { return weights; }
    bool empty() const { return weights.empty(); }
private:
    void normalize();
    std::map<Hypothesis,double> weights;
    std::set<std::size_t> received_events;
};
}
