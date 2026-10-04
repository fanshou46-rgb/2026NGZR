#pragma once
#include "observation_model.hpp"
#include <chrono>
#include <functional>
#include <map>
#include <memory>
#include <set>
#include <string>
#include <vector>

namespace _home {
// Value objects only. No RDFW, canonical facts, SDK handles or execution rights.
struct JointObject {
    bool small, container;
    int at;                 // Explicit SDK at fact; -1 means none.
    std::set<unsigned> inside; // Independent SDK edges; multiple parents are legal.
    bool opened;
    JointObject(bool s=false,bool c=false,int a=-1,unsigned i=0,bool o=false)
        :small(s),container(c),at(a),opened(o) { if(i) inside.insert(i); }
};
struct JointWorld {
    int robot = -1;
    unsigned hand = 0, plate = 0;
    std::set<int> locations;
    std::map<unsigned,JointObject> objects;
    std::map<LocationHypothesis,double> initial_reply_counts;
    void freezeSdkReplyDomain();
    void validate() const;
    bool atLocation(unsigned id,int location) const;
    std::set<unsigned> visible() const;
    std::set<LocationHypothesis> truthfulReplies(unsigned id) const;
};
enum class JointActionKind { MOVE, PICKUP, PUTDOWN, TOPLATE, FROMPLATE,
    OPEN, CLOSE, PUTIN, TAKEOUT, SENSE, ASK };
struct JointAction {
    JointActionKind kind;
    unsigned a, b;
    std::chrono::milliseconds duration;
    JointAction(JointActionKind k,unsigned x=0,unsigned y=0,int ms=-1)
        :kind(k),a(x),b(y),duration(ms==-1?(k==JointActionKind::MOVE?120:100):ms) {}
    int cost() const;
};
struct JointObservation {
    enum class Kind { FEEDBACK, VISIBLE, ANSWER } kind = Kind::FEEDBACK;
    bool success = false;
    std::set<unsigned> ids;
    LocationHypothesis reply = {'?',-1};
    bool operator<(const JointObservation& other) const;
};
struct JointStep {
    JointWorld world;
    JointObservation observation;
};
class JointDynamics {
public:
    // Deterministic physical step. ASK uses noisyBranches, never a truth oracle.
    static JointStep step(const JointWorld& world,const JointAction& action);
};
struct WeightedJointWorld { JointWorld world; double weight; };
struct JointBranch;
struct ProbabilityBounds {
    double lower=0, upper=1, residual=1;
};
class JointBelief {
public:
    explicit JointBelief(std::vector<WeightedJointWorld> worlds,double residual=0);
    const std::vector<WeightedJointWorld>& support() const {return worlds;}
    double residualMass() const {return residual;}
    double expectation(const std::function<double(const JointWorld&)>& value) const;
    ProbabilityBounds probabilityBounds(const std::function<bool(const JointWorld&)>& event) const;
    // Conservative conditioning: uncovered support may give this observation
    // likelihood anywhere in [0,1]. Retain its upper posterior mass, never
    // silently redistribute it over enumerated worlds. No canonical authority.
    bool condition(const std::function<double(const JointWorld&)>& likelihood,std::size_t event=0);
    std::vector<JointBranch> branches(const JointAction& action,
                                     const AskObservationModel& model) const;
    // Exact update only for covered support. Impossible observations leave it intact.
    bool observe(const JointAction& action,const JointObservation& observation,
                 const AskObservationModel& model,std::size_t event=0);
private:
    std::vector<WeightedJointWorld> worlds;
    double residual;
    std::set<std::size_t> received_events;
};
struct JointBranch {
    JointObservation observation;
    double probability;
    JointBelief posterior;
};
struct JointPolicy {
    bool stop = true;
    JointAction action = {JointActionKind::SENSE};
    // Only observations distinguish decisions; hidden world IDs cannot index it.
    std::map<JointObservation,std::shared_ptr<JointPolicy>> children;
};
struct JointPlan {
    std::shared_ptr<JointPolicy> policy;
    double stop_value = 0, value = 0;
    std::size_t nodes = 0;
    bool search_complete = true, support_complete = true;
    std::string reason;
};
class JointPolicySearch {
public:
    // A static action catalogue, not a different action set for each hidden world.
    // Returned policy is a modeled lower bound, not real execution authorization.
    static JointPlan solve(const JointBelief& belief,const std::vector<JointAction>& actions,
        const AskObservationModel& observation_model,
        const std::function<double(const JointWorld&)>& terminal_value,
        unsigned depth,std::chrono::milliseconds remaining,
        std::size_t max_nodes=4096,std::chrono::milliseconds search_time=std::chrono::milliseconds(10));
};
}
