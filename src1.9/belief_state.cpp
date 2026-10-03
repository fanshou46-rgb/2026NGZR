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
bool LocationBelief::answer(Hypothesis observation,std::size_t event_id) {
    if (observation.first!='a' && observation.first!='i') return false;
    if (event_id && received_events.count(event_id)) return false;
    if (!weights.count(observation)) {
        weights[observation]=weights[{'?',-1}]*0.5;
        weights[{'?',-1}]*=0.5;
    }
    std::set<Hypothesis> replies;
    for (const auto& v:weights) if(v.first.first!='?') replies.insert(v.first);
    return observe(observation,AskObservationModel(replies),event_id);
}

double LocationBelief::observationProbability(Hypothesis observation,const AskObservationModel& model) const {
    double result=0;
    for (const auto& v:weights) result+=v.second*model.likelihood(observation,v.first);
    return result;
}

LocationBelief LocationBelief::posterior(Hypothesis observation,const AskObservationModel& model) const {
    LocationBelief next=*this;
    const double probability=observationProbability(observation,model);
    if (probability<=0) return next; // impossible observations cannot create evidence
    for (auto& v:next.weights) v.second*=model.likelihood(observation,v.first)/probability;
    next.normalize(); return next;
}

bool LocationBelief::observe(Hypothesis observation,const AskObservationModel& model,std::size_t event_id) {
    if (event_id && !received_events.insert(event_id).second) return false;
    if (observation.first=='?') return false;
    if ((observation.first=='a' || observation.first=='i') && !weights.count(observation)) {
        weights[observation]=weights[{'?',-1}]*.5;
        weights[{'?',-1}]*=.5;
    }
    const auto supported=model.withReply(observation);
    if (observationProbability(observation,supported)<=0) return false;
    weights=posterior(observation,supported).weights;
    return true;
}
void LocationBelief::ruleOut(Hypothesis h) {
    auto i=weights.find(h); if(i!=weights.end()) { i->second=0; normalize(); }
}
bool LocationBelief::filterVisibility(int location,bool visible,
    const std::map<int,std::pair<int,int>>& containers) {
    bool changed=false;
    for(auto& entry:weights) {
        const auto h=entry.first;
        bool contradicted=false;
        if(h.first=='a') contradicted=visible!=(h.second==location);
        else if(h.first=='i') {
            const auto c=containers.find(h.second);
            if(c!=containers.end()) {
                const int at=c->second.first,opened=c->second.second;
                if(visible) contradicted=(at>=0 && at!=location) || opened==0;
                else contradicted=at==location && opened==1;
            }
        }
        // Residual support and unknown visibility remain possible. This is
        // support filtering, not a numerical likelihood for an unknown door.
        if(contradicted && entry.second>0) {entry.second=0;changed=true;}
    }
    if(changed) normalize();return changed;
}
void LocationBelief::confirm(Hypothesis h) {
    weights.clear();weights[h]=1;
}
double LocationBelief::probability(Hypothesis h) const {
    auto i=weights.find(h); return i==weights.end()?0:i->second;
}
