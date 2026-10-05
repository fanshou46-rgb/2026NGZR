#pragma once
#include "sdk_episode.hpp"
#include <sstream>
#include <stdexcept>
namespace _home {
// No execution rights. This signature intentionally excludes ASK selectors
// and random frequencies. Only physical/Sense simulation may use it.
inline std::string physicalRouteSignature(const JointWorld& world) {
    std::ostringstream s;s<<world.robot<<','<<world.hand<<','<<world.plate<<';';
    for(int location:world.locations)s<<location<<',';
    s<<';';
    for(const auto& item:world.objects) {
        const auto& o=item.second;s<<item.first<<':'<<o.small<<','<<o.container<<','<<o.at<<','<<o.opened<<':';
        for(unsigned parent:o.inside)s<<parent<<',';
        s<<';';
    }
    s<<'|'<<world.initial_reply_counts.empty()<<':';
    for(const auto& entry:world.initial_reply_counts)if(entry.first.first=='a')s<<entry.first.second<<',';
    return s.str();
}
inline std::string physicalEpisodeSignature(const SdkEpisode& episode) {
    std::ostringstream s;s<<physicalRouteSignature(episode.world)<<'|'<<episode.paid<<'|'<<episode.credits.size()<<':';
    for(bool credit:episode.credits)s<<credit;
    return s.str();
}
struct PhysicalRouteView {
    EpisodeBelief belief;
    std::size_t original_worlds,physical_worlds;
    // Evaluation-only aggregate: NEVER replace EpisodeReplay or use this
    // view for ASK. Original receipt events/answer selectors stay in replay.
    static PhysicalRouteView make(const EpisodeBelief& original) {
        if(!original.modelValid() || original.residualMass()>0)
            throw std::logic_error("physical evaluation requires valid covered belief");
        std::map<std::string,std::size_t> groups;std::vector<WeightedEpisode> states;
        for(const auto& state:original.support()) {
            const auto key=physicalEpisodeSignature(state.episode);
            const auto found=groups.find(key);
            if(found==groups.end()){groups[key]=states.size();states.push_back(state);}
            else states[found->second].weight+=state.weight;
        }
        const auto retained=states.size();
        return {EpisodeBelief(std::move(states)),original.support().size(),retained};
    }
};
}
