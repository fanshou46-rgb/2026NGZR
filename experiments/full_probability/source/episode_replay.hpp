#pragma once
#include "sdk_episode.hpp"
namespace _home {
struct EpisodeEvidence {
    std::size_t receipt;
    JointAction action;
    JointObservation observation;
};
struct EpisodeRepairResult {
    bool installed=false,work_cut=false,wall_cut=false;
    std::size_t transitions=0;
    std::string reason;
};
// Owns the public history. Replacement support is always INITIAL worlds;
// replay preserves paid actions and irreversible credits. It cannot authorize
// commands or write canonical facts, and has no SDK/environment handle.
class EpisodeReplay {
public:
    explicit EpisodeReplay(EpisodeBelief initial):current(std::move(initial)) {}
    const EpisodeBelief& belief() const {return current;}
    const std::vector<EpisodeEvidence>& evidence() const {return history;}
    EpisodeUpdate observe(const SdkEpisodeModel&,const JointAction&,
        const JointObservation&,const AskObservationModel&,std::size_t);
    EpisodeRepairResult repair(const SdkEpisodeModel&,const AskObservationModel&,
        const std::vector<WeightedEpisode>& initial,std::size_t max_transitions,
        std::chrono::milliseconds wall);
private:
    EpisodeBelief current;
    std::vector<EpisodeEvidence> history;
};
}
