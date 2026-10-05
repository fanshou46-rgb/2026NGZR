#pragma once
#include "sdk_episode.hpp"
#include <algorithm>
#include <stdexcept>
namespace _home {
// No execution rights. This signature intentionally excludes ASK selectors
// and random frequencies. Only physical/Sense simulation may use it.
inline void appendPhysicalNumber(std::string& key,std::uint64_t value) {
    for(unsigned byte=0;byte<8;++byte)key.push_back(static_cast<char>((value>>(8*byte))&255));
}
inline std::string physicalRouteSignature(const JointWorld& world) {
    // Fixed-width, length-delimited little-endian values: exact key equality,
    // no digest collisions or locale/stream formatting overhead.
    std::string s;
    appendPhysicalNumber(s,world.robot);appendPhysicalNumber(s,world.hand);appendPhysicalNumber(s,world.plate);
    appendPhysicalNumber(s,world.locations.size());
    for(int location:world.locations)appendPhysicalNumber(s,location);
    appendPhysicalNumber(s,world.objects.size());
    for(const auto& item:world.objects) {
        const auto& o=item.second;appendPhysicalNumber(s,item.first);
        s.push_back(o.small);s.push_back(o.container);appendPhysicalNumber(s,o.at);s.push_back(o.opened);
        appendPhysicalNumber(s,o.inside.size());
        for(unsigned parent:o.inside)appendPhysicalNumber(s,parent);
    }
    s.push_back(world.initial_reply_counts.empty());std::size_t locations=0;
    for(const auto& entry:world.initial_reply_counts)locations+=entry.first.first=='a';
    appendPhysicalNumber(s,locations);
    for(const auto& entry:world.initial_reply_counts)if(entry.first.first=='a')appendPhysicalNumber(s,entry.first.second);
    return s;
}
inline std::string physicalEpisodeSignature(const SdkEpisode& episode) {
    auto s=physicalRouteSignature(episode.world);appendPhysicalNumber(s,episode.paid);appendPhysicalNumber(s,episode.credits.size());
    for(bool credit:episode.credits)s.push_back(credit);
    return s;
}
inline bool physicalReuseWorthwhile(const EpisodeBelief& belief) {
    // A deterministic fixed first-eight check only chooses between two exact
    // evaluation representations. It never changes posterior weights or facts.
    const auto inspected=std::min(std::size_t(8),belief.support().size());
    if(inspected<2)return false;
    std::set<std::string> keys;
    for(std::size_t i=0;i<inspected;++i)keys.insert(physicalEpisodeSignature(belief.support()[i].episode));
    return keys.size()*2<=inspected;
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
