#include "belief_state.hpp"
#include <algorithm>
using namespace _home;

void LocationBelief::normalize() {
    double sum=0; for (const auto& v:weights) sum+=v.second;
    if (sum<=0) { weights.clear(); weights[{'?',-1}]=1; return; }
    for (auto& v:weights) v.second/=sum;
}
void LocationBelief::initialize(const std::set<Hypothesis>& domain,Hypothesis hint) {
    if (!empty()) return;
    for (auto h:domain) weights[h]=1;
    weights[{'?',-1}]=1;
    normalize();
    // Explicit uncalibrated prior: reserve half for alternatives, half for the input hint.
    if (hint.first!='?') {
        for (auto& v:weights) v.second*=0.5;
        weights[hint]+=0.5;
    }
}
bool LocationBelief::answer(Hypothesis observation) {
    if (observation.first=='?' || !received.insert(observation).second) return false;
    if (!weights.count(observation)) {
        weights[observation]=weights[{'?',-1}]*0.5;
        weights[{'?',-1}]*=0.5;
    }
    // SDK noise model: 0.6 true + 0.3 random answer + 0.1 unknown.
    // Domain is local and incomplete; residual mass prevents fabricated certainty.
    const double noise=0.3/std::max<std::size_t>(1,weights.size()-1);
    for (auto& v:weights) v.second*=noise+(v.first==observation?0.6:0.0);
    normalize(); return true;
}
void LocationBelief::ruleOut(Hypothesis h) {
    auto i=weights.find(h); if(i!=weights.end()) { i->second=0; normalize(); }
}
double LocationBelief::probability(Hypothesis h) const {
    auto i=weights.find(h); return i==weights.end()?0:i->second;
}
