#pragma once
#include <map>
#include <set>
#include <utility>

namespace _home {
// Joint alternatives: ('a', location), ('i', container), ('?', -1).
// A distribution is a planning hint, never authority for a canonical fact.
class LocationBelief {
public:
    typedef std::pair<char,int> Hypothesis;
    void initialize(const std::set<Hypothesis>& domain, Hypothesis hint);
    bool answer(Hypothesis observation);
    void ruleOut(Hypothesis observation);
    double probability(Hypothesis h) const;
    const std::map<Hypothesis,double>& distribution() const { return weights; }
    bool empty() const { return weights.empty(); }
private:
    void normalize();
    std::map<Hypothesis,double> weights;
    std::set<Hypothesis> received;
};
}
