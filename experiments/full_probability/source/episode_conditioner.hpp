#pragma once
#include "episode_prior.hpp"
#include "episode_replay.hpp"
namespace _home {
struct InitialFactorProof {
    PriorField field;unsigned object,parent;std::size_t receipt;
    std::string predicate;
};
struct InitialConditioning {
    bool consistent=true;
    double retained_prior_mass=1;
    std::vector<PublicPriorFactor> factors;
    std::vector<InitialFactorProof> proofs;
};
class EpisodeConditioner {
public:
    // Condition only initial variables logically identified by PUBLIC SDK
    // preconditions/feedback. Moving small objects are never mistaken for
    // initial coordinates. No posterior mode or weak Ask becomes a hard fact.
    static InitialConditioning initial(const JointWorld&,const std::vector<PublicPriorFactor>&,
        const std::vector<EpisodeEvidence>&);
};
}
