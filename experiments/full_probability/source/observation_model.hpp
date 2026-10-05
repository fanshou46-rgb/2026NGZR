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
    // Explicit modeling assumption, NOT a documented SDK atom-order rule.
    // The default strict kernel refuses nonunique truth; experiments can put
    // an uncalibrated equal prior on the unspecified truthful selector.
    AskObservationModel withPersistentAnswerOrderPrior() const {
        auto result=*this;result.uniform_order_prior=true;return result;
    }
    bool assumesUniformAnswerOrder() const {return uniform_order_prior;}
    // SDK noise samples initial fact entries, so repeated locations have weight.
    AskObservationModel reweighted(const std::map<LocationHypothesis,double>& weights,
                                  double uncovered_random) const;
    const std::map<LocationHypothesis,double>& randomDistribution() const {return random_replies;}
private:
    double correct_mass, random_mass, unknown_mass, uncovered_mass;
    std::map<LocationHypothesis,double> random_replies;
    bool uniform_order_prior=false;
};
}
