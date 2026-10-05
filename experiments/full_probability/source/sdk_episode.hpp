#pragma once
#include "joint_world.hpp"
#include <utility>
namespace _home {
struct SdkPredicate {
    std::string verb;
    std::vector<std::pair<unsigned,unsigned>> bindings;
};
struct SdkConstraint {SdkPredicate predicate;bool must_hold;};
struct SdkRewardBounds {double lower=0,upper=0;unsigned goals_lower=0,goals_upper=0,credits=0;};
struct SdkEpisode {
    JointWorld world;
    std::vector<bool> credits;
    int paid=0;
};
class SdkEpisodeModel {
public:
    std::vector<SdkPredicate> goals;
    std::vector<SdkConstraint> constraints;
    bool predicate(const JointWorld&,const std::string&,unsigned,unsigned) const;
    bool constraint(const JointWorld&,const SdkConstraint&) const;
    SdkRewardBounds reward(const SdkEpisode&) const;
    SdkEpisode next(const SdkEpisode&,const JointAction&,const JointWorld&,bool) const;
};
struct WeightedEpisode {SdkEpisode episode;double weight;};
struct EpisodeBranch;
enum class EpisodeUpdate {APPLIED, DUPLICATE, SUPPORT_MISS};
class EpisodeBelief {
public:
    explicit EpisodeBelief(std::vector<WeightedEpisode>,double residual=0);
    const std::vector<WeightedEpisode>& support() const {return states;}
    double residualMass() const {return outside;}
    bool modelValid() const {return valid;}
    SdkRewardBounds reward(const SdkEpisodeModel&) const;
    std::vector<EpisodeBranch> branches(const SdkEpisodeModel&,const JointAction&,const AskObservationModel&) const;
    // Condition a modeled episode on ONE already received public feedback.
    // Returns its likelihood; zero leaves this belief intact. No event IDs or
    // canonical authority: observe owns actual receipt deduplication/fees.
    double conditionPublicFeedback(const SdkEpisodeModel&,const JointAction&,const JointObservation&,const AskObservationModel&);
    EpisodeUpdate observe(const SdkEpisodeModel&,const JointAction&,const JointObservation&,const AskObservationModel&,std::size_t);
private:
    std::vector<WeightedEpisode> states;
    double outside;
    bool valid=true;
    std::set<std::size_t> events;
};
struct EpisodeBranch {JointObservation observation;double probability;EpisodeBelief posterior;};
struct EpisodePolicy {
    bool stop=true;
    JointAction action={JointActionKind::SENSE};
    std::map<JointObservation,std::shared_ptr<EpisodePolicy>> children;
    std::map<JointObservation,double> probabilities;
};
struct EpisodePlan {
    std::shared_ptr<EpisodePolicy> policy;
    SdkRewardBounds value;
    std::size_t transitions=0;
    std::size_t prefix_cache_hits=0;
    std::size_t physical_view_inputs=0,physical_view_worlds=0;
    bool work_cut=false,wall_cut=false,support_complete=true;
};
class EpisodePolicySearch {
public:
    static EpisodePlan solve(const EpisodeBelief&,const SdkEpisodeModel&,
        const std::vector<JointAction>&,const AskObservationModel&,unsigned,
        std::chrono::milliseconds,std::size_t,std::chrono::milliseconds);
};
}
