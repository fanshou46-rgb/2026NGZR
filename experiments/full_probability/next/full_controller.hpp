#pragma once
#include "episode_prior.hpp"
#include "episode_replay.hpp"
#include "episode_router.hpp"
#include "execution_evidence.hpp"
namespace _home {
class RDFW;
class FullModelController {
public:
    explicit FullModelController(RDFW&);
    void run();
    bool qualify(ActionPermit&) const;
private:
    RDFW& owner;
    SdkEpisodeModel model;
    JointWorld initial_template,modal;
    std::vector<PublicPriorFactor> factors;
    std::unique_ptr<EpisodeReplay> replay;
    AskObservationModel ask;
    std::shared_ptr<EpisodePolicy> policy;
    std::string expected_signature;
    bool selecting=false;
    std::size_t decision=0;
    std::map<unsigned,unsigned> asked;
    std::chrono::steady_clock::duration cpu_used{};
    void initialize();
    bool dispatch(const JointAction&);
    JointObservation feedback(const JointAction&,const ActionReceipt&) const;
};
}
