#pragma once
#include "joint_world.hpp"
#include <algorithm>
#include <cmath>
#include <stdexcept>
namespace _home {
// Frozen f19 repeat0 actual SDK receipts only. These are descriptive
// estimates, not feedback labels for unexecuted candidates or hard bounds.
// source_sha256=46eba649d2005e79f6ea36416e25a50d9f105b0729a89a65ce1a1e1ce67cc325
struct EpisodeLatencyModel {
    struct Estimate {double median_ms,p90_ms;unsigned count;};
    Estimate action[11],failed[11];
    void validate() const {
        for(unsigned i=0;i<11;++i) {
            const auto valid=[](const Estimate& e) {return e.count>0 && std::isfinite(e.median_ms) && e.median_ms>0 && std::isfinite(e.p90_ms) && e.p90_ms>0;};
            if(!valid(action[i]) || (failed[i].count && !valid(failed[i])))
                throw std::invalid_argument("invalid empirical SDK latency estimate");
        }
    }
    static EpisodeLatencyModel development() {
        EpisodeLatencyModel m{};
        m.action[0]={111.1763880000,118.2882780000,228}; // Move
        m.failed[0]={110.3335460000,118.7866960000,6};
        m.action[1]={111.2351630000,119.2099110000,100}; // PickUp
        m.action[2]={111.4028430000,116.0915700000,80}; // PutDown
        m.action[3]={114.8260575000,119.2471280000,16}; // ToPlate
        m.action[4]={111.0588945000,114.5667200000,10}; // FromPlate
        m.action[5]={111.1951820000,119.6447510000,63}; // Open
        m.action[6]={110.9623825000,115.2959830000,22}; // Close
        m.action[7]={111.2251935000,118.8261710000,26}; // PutIn
        m.action[8]={114.0715295000,118.5515660000,38}; // TakeOut
        m.action[9]={112.8687160000,118.9707190000,323}; // Sense
        m.action[10]={110.7505385000,118.5979940000,124}; // AskLoc
        return m;
    }
    Estimate estimate(const JointAction& a,const JointObservation& o) const {
        const auto id=static_cast<unsigned>(a.kind);
        return o.kind==JointObservation::Kind::FEEDBACK && !o.success && failed[id].count?failed[id]:action[id];
    }
    std::chrono::milliseconds reserve(const JointAction& a) const {
        const auto id=static_cast<unsigned>(a.kind);
        // Preserve the action duration and use at least 120ms. Actual
        // deadline guards remain necessary; p90 is not a hard bound.
        const auto ms=static_cast<long long>(std::ceil(std::max(action[id].p90_ms,failed[id].count?failed[id].p90_ms:0)));
        return std::chrono::milliseconds(std::max<long long>(a.duration.count(),std::max(120LL,ms)));
    }
};
}
