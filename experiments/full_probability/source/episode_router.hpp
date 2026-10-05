#pragma once
#include "episode_routes.hpp"
namespace _home {
struct EpisodeProposalBatch {
    std::vector<EpisodeRoute> routes;
    std::size_t transitions=0;
    std::size_t physical_worlds=0,reused_worlds=0;
    bool work_cut=false,wall_cut=false;
};
class EpisodeRouter {
public:
    // Hypothetical worlds propose routes; the policy evaluator must compare
    // each proposal on the complete public belief before it can be selected.
    static EpisodeProposalBatch propose(const EpisodeBelief&,const SdkEpisodeModel&,
        std::size_t work_limit,std::chrono::milliseconds wall,bool arrival_sense=true);
};
}
