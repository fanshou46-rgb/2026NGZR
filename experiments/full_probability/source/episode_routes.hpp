#pragma once
#include "sdk_episode.hpp"
namespace _home {
using EpisodeRoute=std::vector<JointAction>;
class EpisodeRouteSearch {
public:
    // Every route is scored on the WHOLE belief. A world-derived proposal has
    // no execution privilege; feedback, never a hidden index, selects children.
    // Each physical false reply terminates its route and retains paid costs.
    // Optional exact aggregation applies only to physical/Sense evaluation.
    // Information roots retain all ASK selectors and frequencies; a route
    // containing ASK disables aggregation for that solve. It never replaces
    // the caller's belief or gives a representative execution authority.
    static EpisodePlan solve(const EpisodeBelief&,const SdkEpisodeModel&,
        const std::vector<EpisodeRoute>& public_routes,const std::vector<JointAction>& observations,
        const AskObservationModel&,std::chrono::milliseconds remaining,
        std::size_t work_limit,std::chrono::milliseconds wall,bool physical_reuse=true);
};
}
