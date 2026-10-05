#pragma once
#include "sdk_episode.hpp"
#include "episode_latency.hpp"
namespace _home {
using EpisodeRoute=std::vector<JointAction>;
class EpisodeRouteSearch {
public:
    // Every route is scored on the WHOLE belief. A world-derived proposal has
    // no execution privilege; feedback, never a hidden index, selects children.
    // Each physical false reply terminates its route and retains paid costs.
    // Exact physical/Sense aggregation retains live ASK worlds. Catalogues
    // containing ASK fall back to full support. Optional latency uses an
    // explicit empirical future-time proxy, while value stays base reward.
    static EpisodePlan solve(const EpisodeBelief&,const SdkEpisodeModel&,
        const std::vector<EpisodeRoute>& public_routes,const std::vector<JointAction>& observations,
        const AskObservationModel&,std::chrono::milliseconds remaining,
        std::size_t work_limit,std::chrono::milliseconds wall,bool physical_reuse=true,const EpisodeLatencyModel* latency=nullptr);
};
}
