#include "episode_prior.hpp"
#include <algorithm>
#include <cmath>
#include <limits>
#include <stdexcept>
#include <tuple>
using namespace _home;
namespace {
std::uint64_t mix(std::uint64_t v) {
    v+=0x9e3779b97f4a7c15ULL;v=(v^(v>>30))*0xbf58476d1ce4e5b9ULL;
    v=(v^(v>>27))*0x94d049bb133111ebULL;return v^(v>>31);
}
void assign(JointWorld& w,const PublicPriorFactor& f,int value) {
    if(f.field==PriorField::HAND || f.field==PriorField::PLATE) {
        if(value<0 || (value && (!w.objects.count(unsigned(value)) || !w.objects.at(unsigned(value)).small)))
            throw std::invalid_argument("prior storage value is not a public small object");
        if(f.field==PriorField::HAND)w.hand=unsigned(value);else w.plate=unsigned(value);
        return;
    }
    auto item=w.objects.find(f.object);
    if(item==w.objects.end())throw std::invalid_argument("prior factor has no public object");
    if(f.field==PriorField::EXPLICIT_AT) {
        if(value<-1 || (value>=0 && !w.locations.count(value)))throw std::invalid_argument("invalid prior location");
        item->second.at=value;
    } else if(f.field==PriorField::DOOR) {
        if(!item->second.container || (value!=0 && value!=1))throw std::invalid_argument("invalid prior door");
        item->second.opened=value==1;
    } else if(f.field==PriorField::INSIDE_EDGE) {
        if(!item->second.small || !w.objects.count(f.parent) || !w.objects.at(f.parent).container || (value!=0 && value!=1))
            throw std::invalid_argument("invalid independent prior inside edge");
        if(value)item->second.inside.insert(f.parent);else item->second.inside.erase(f.parent);
    } else throw std::invalid_argument("unsupported prior field");
}
}
EpisodeSceneBatch EpisodePrior::generate(const JointWorld& base,const std::vector<PublicPriorFactor>& factors,
    std::size_t constraints,std::size_t limit,std::uint64_t offset,bool order_prior) {
    if(!limit || limit>4096 || factors.size()>4096)throw std::invalid_argument("invalid prior generation budget");
    base.validate();
    using Key=std::tuple<PriorField,unsigned,unsigned>;std::set<Key> assigned;
    std::size_t count=1;
    for(const auto& f:factors) {
        if(!assigned.insert(Key(f.field,f.object,f.parent)).second)throw std::invalid_argument("prior variable assigned twice");
        if(f.values.empty())throw std::invalid_argument("prior variable has no values");
        double mass=0;std::set<int> values;
        for(const auto& v:f.values) {
            if(!std::isfinite(v.probability)||v.probability<=0 || !values.insert(v.value).second)
                throw std::invalid_argument("invalid prior probability or duplicate value");
            JointWorld probe=base;assign(probe,f,v.value);mass+=v.probability;
        }
        if(std::abs(mass-1)>1e-9)throw std::invalid_argument("prior probabilities must sum to one");
        count=count>std::numeric_limits<std::size_t>::max()/f.values.size()?
            std::numeric_limits<std::size_t>::max():count*f.values.size();
    }
    EpisodeSceneBatch result;result.assignments=count;result.exact=count<=limit;
    std::uint64_t order_draw=0;
    const auto make=[&](JointWorld w,double weight) {
        if(order_prior){w.answer_order_assumed=true;w.answer_order_seed=mix(offset+(order_draw++)+0x859b66ULL);}
        w.freezeSdkReplyDomain();w.validate();SdkEpisode e;e.world=std::move(w);
        e.credits.assign(constraints,true);result.scenes.push_back({std::move(e),weight});
    };
    if(result.exact) {
        for(std::size_t n=0;n<count;++n) {
            JointWorld w=base;double p=1;std::size_t code=n;
            for(const auto& f:factors){const auto& v=f.values[code%f.values.size()];code/=f.values.size();assign(w,f,v.value);p*=v.probability;}
            const auto replicas=order_prior?std::max(std::size_t(1),limit/count):1;
            for(std::size_t replica=0;replica<replicas;++replica)make(w,p/replicas);
        }
        result.scope="exact finite public factor domain";
    } else {
        for(std::size_t n=0;n<limit;++n) {
            JointWorld w=base;std::uint64_t variable=0;
            for(const auto& f:factors) {
                // Stateless deterministic draws, independent of the SDK seed,
                // actual answers, system time and ordering of executed commands.
                const double u=double(mix((offset+n)*0xd6e8feb86659fd93ULL+variable++)>>11)/9007199254740992.0;
                double cumulative=0;const PriorValue* chosen=&f.values.back();
                for(const auto& v:f.values){cumulative+=v.probability;if(u<cumulative){chosen=&v;break;}}
                assign(w,f,chosen->value);
            }
            make(std::move(w),1.0/limit);
        }
        result.draws=limit;result.scope="deterministic Monte Carlo approximation; finite domain only; no certified coverage mass";
    }
    if(order_prior) {
        result.exact=false;result.draws=result.scenes.size();
        result.scope+="; sampled persistent answer-order ranking prior, uncalibrated";
    }
    return result;
}
