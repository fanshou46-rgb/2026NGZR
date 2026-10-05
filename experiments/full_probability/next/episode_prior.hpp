#pragma once
#include "sdk_episode.hpp"
#include <cstdint>
namespace _home {
enum class PriorField {HAND,PLATE,EXPLICIT_AT,INSIDE_EDGE,DOOR};
struct PriorValue {int value;double probability;};
struct PublicPriorFactor {
    PriorField field;unsigned object=0,parent=0;
    std::vector<PriorValue> values;
};
struct EpisodeSceneBatch {
    std::vector<WeightedEpisode> scenes;
    bool exact=false;
    std::size_t assignments=0,draws=0;
    // A sampled batch approximates a full generative prior. Its unseen sample
    // error is not a certified residual mass and never authorizes a fact.
    std::string scope;
};
class EpisodePrior {
public:
    static EpisodeSceneBatch generate(const JointWorld& public_template,
        const std::vector<PublicPriorFactor>& factors,std::size_t constraint_count,
        std::size_t scenes,std::uint64_t deterministic_offset=0);
};
}
