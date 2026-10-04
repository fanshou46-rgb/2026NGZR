#include "audit_ablation.hpp"
#include "observation_model.hpp"
#include <cmath>
#include <stdexcept>
using namespace _home;

AskObservationModel::AskObservationModel(const std::set<LocationHypothesis>& replies,
    double correct,double random,double unknown,double uncovered_random)
    :correct_mass(correct),random_mass(random),unknown_mass(unknown),uncovered_mass(uncovered_random) {
    if (!std::isfinite(correct+random+unknown+uncovered_random) || correct<0 || random<0 || unknown<0 ||
        std::abs(correct+random+unknown-1)>1e-9 || uncovered_random<0 || uncovered_random>1)
        throw std::invalid_argument("invalid observation model probabilities");
    std::set<LocationHypothesis> concrete;
    for (auto h:replies) if ((h.first=='a' || h.first=='i') && h.second>=0) concrete.insert(h);
    for (auto h:concrete) random_replies[h]=(1-uncovered_random)/concrete.size();
    random_replies[{'*',-2}]=concrete.empty()?1:uncovered_random;
}

double AskObservationModel::likelihood(LocationHypothesis reply,LocationHypothesis world) const {
    if(AuditAblation()==1 || AuditAblation()==2) {
        if(reply.first=='?')return unknown_mass;
        auto found=random_replies.find(reply);
        return found==random_replies.end()?0:(1-unknown_mass)*found->second;
    }
    if (reply.first=='?') return unknown_mass;
    auto noise=random_replies.find(reply);
    double value=noise==random_replies.end()?0:random_mass*noise->second;
    // Residual worlds send their truthful response to the outside-domain bucket.
    const auto truthful=random_replies.count(world)?world:LocationHypothesis{'*',-2};
    if (reply==truthful) value+=correct_mass;
    return value;
}

std::set<LocationHypothesis> AskObservationModel::observations() const {
    std::set<LocationHypothesis> result{{'?',-1}};
    for (const auto& r:random_replies) result.insert(r.first);
    return result;
}

AskObservationModel AskObservationModel::withReply(LocationHypothesis reply) const {
    auto result=*this;
    if((reply.first=='a' || reply.first=='i') && !result.random_replies.count(reply)) {
        // Refinement of an uncovered bucket is an explicit approximate split;
        // existing reply probabilities must not revert to uniform.
        double& outside=result.random_replies[{'*',-2}];
        result.random_replies[reply]=outside*.5;outside*=.5;
        result.uncovered_mass=outside;
    }
    return result;
}
AskObservationModel AskObservationModel::reweighted(
    const std::map<LocationHypothesis,double>& weights,double outside) const {
    AskObservationModel result({},correct_mass,random_mass,unknown_mass,outside);
    double total=0;
    for(const auto& item:weights) {
        if((item.first.first!='a' && item.first.first!='i') || item.first.second<0 ||
            !std::isfinite(item.second) || item.second<0)
            throw std::invalid_argument("invalid random reply weight");
        total+=item.second;
    }
    if(!std::isfinite(total)) throw std::invalid_argument("random reply weight overflow");
    result.random_replies.clear();
    for(const auto& item:weights)if(item.second>0)result.random_replies[item.first]=(1-outside)*item.second/total;
    result.random_replies[{'*',-2}]=total>0?outside:1;
    return result;
}
