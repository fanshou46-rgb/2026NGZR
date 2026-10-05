#pragma once
#include "episode_prior.hpp"
#include "episode_replay.hpp"
namespace _home {
struct ConditionedProposal {
    std::vector<WeightedEpisode> scenes;
    std::size_t checks=0;
    bool complete=true,work_cut=false,wall_cut=false;
    std::string scope;
};
class EpisodeProposal {
public:
    // PUBLIC deterministic feedback conditions each small-object block given
    // shared slots, static big positions and doors. Importance weights retain
    // each block's acceptance mass. Ask likelihood and every SDK transition
    // must still pass complete EpisodeReplay before installation.
    static ConditionedProposal generate(const JointWorld&,const std::vector<PublicPriorFactor>&,
        const std::vector<EpisodeEvidence>&,std::size_t constraints,std::size_t particles,
        std::uint64_t offset,std::size_t max_checks,std::chrono::milliseconds wall);
};
}
