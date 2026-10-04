#pragma once
#include <map>
#include <set>
#include <utility>

namespace _home {
using LocationHypothesis = std::pair<char,int>;
// '?' is residual world support. '*' aggregates replies outside the local domain.
// Neither symbol is a canonical location or permission to act.
class AskObservationModel {
public:
    explicit AskObservationModel(const std::set<LocationHypothesis>& replies,
                                 double correct = .6, double random = .3,
                                 double unknown = .1, double uncovered_random = .1);
    double likelihood(LocationHypothesis reply, LocationHypothesis world) const;
    std::set<LocationHypothesis> observations() const;
    AskObservationModel withReply(LocationHypothesis reply) const;
    // SDK noise samples initial fact entries, so repeated locations have weight.
    AskObservationModel reweighted(const std::map<LocationHypothesis,double>& weights,
                                  double uncovered_random) const;
    const std::map<LocationHypothesis,double>& randomDistribution() const {return random_replies;}
private:
    double correct_mass, random_mass, unknown_mass, uncovered_mass;
    std::map<LocationHypothesis,double> random_replies;
};
}
