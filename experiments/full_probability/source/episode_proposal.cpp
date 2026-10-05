#include "episode_proposal.hpp"
#include <algorithm>
#include <cmath>
#include <stdexcept>
using namespace _home;
namespace {
std::uint64_t mix(std::uint64_t v) {
    v+=0x9e3779b97f4a7c15ULL;v=(v^(v>>30))*0xbf58476d1ce4e5b9ULL;
    v=(v^(v>>27))*0x94d049bb133111ebULL;return v^(v>>31);
}
struct Context {int robot;unsigned hand,plate;std::set<unsigned> open_here;};
void forced(JointWorld& w,const JointAction& a) {
    // Preview conditional on an ACTUAL successful receipt. This never grants
    // an execution permit. Exact preconditions are checked in block selection
    // and again in replay; an impossible forced preview cannot be installed.
    if(a.kind==JointActionKind::MOVE) {
        w.robot=int(a.a);for(unsigned id:{w.hand,w.plate})if(id)w.objects.at(id).at=w.robot;
    } else if(a.kind==JointActionKind::OPEN || a.kind==JointActionKind::CLOSE)
        w.objects.at(a.a).opened=a.kind==JointActionKind::OPEN;
    else if(a.kind==JointActionKind::PICKUP || a.kind==JointActionKind::FROMPLATE || a.kind==JointActionKind::TAKEOUT) {
        w.hand=a.a;w.objects.at(a.a).at=w.robot;
        if(a.kind==JointActionKind::FROMPLATE)w.plate=0;
        if(a.kind==JointActionKind::TAKEOUT)w.objects.at(a.a).inside.erase(a.b);
    } else if(a.kind==JointActionKind::PUTDOWN || a.kind==JointActionKind::TOPLATE || a.kind==JointActionKind::PUTIN) {
        w.hand=0;
        if(a.kind==JointActionKind::TOPLATE)w.plate=a.a;
        if(a.kind==JointActionKind::PUTIN) {
            w.objects.at(a.a).inside.insert(a.b);
            if(w.objects.at(a.a).at==w.robot)w.objects.at(a.a).at=-1;
        } else w.objects.at(a.a).at=w.robot;
    }
}
bool contexts(JointWorld world,const std::vector<EpisodeEvidence>& history,std::vector<Context>& output) {
    for(const auto& e:history) {
        Context c{world.robot,world.hand,world.plate,{}};
        for(const auto& item:world.objects)if(item.second.container && item.second.opened && item.second.at==world.robot)c.open_here.insert(item.first);
        output.push_back(c);
        if(e.action.kind==JointActionKind::SENSE) {
            for(const auto& item:world.objects)if(!item.second.small &&
                (item.second.at==world.robot)!=bool(e.observation.ids.count(item.first)))return false;
        } else if(e.action.kind==JointActionKind::MOVE) {
            // Its loc precondition depends on initial small AT factors that
            // have not been chosen yet. Check map legality only in full replay.
            if(e.observation.success && world.robot==int(e.action.a))return false;
        } else if(e.action.kind==JointActionKind::OPEN || e.action.kind==JointActionKind::CLOSE) {
            if(JointDynamics::step(world,e.action).observation.success!=e.observation.success)return false;
        }
        if(e.observation.kind==JointObservation::Kind::FEEDBACK && e.observation.success)forced(world,e.action);
    }
    return true;
}
bool explains(unsigned id,JointObject item,const std::vector<EpisodeEvidence>& history,
    const std::vector<Context>& states,std::size_t& work,std::size_t cap,
    std::chrono::steady_clock::time_point end,ConditionedProposal& result,bool& latest_matches) {
    latest_matches=false;
    for(std::size_t i=0;i<history.size();++i) {
        if(work>=cap || std::chrono::steady_clock::now()>=end) {
            result.complete=false;result.work_cut=work>=cap;result.wall_cut=std::chrono::steady_clock::now()>=end;return false;
        }
        ++work;const auto& e=history[i];const auto& c=states[i];const auto& a=e.action;const auto& o=e.observation;
        const bool at=item.at==c.robot || c.hand==id || c.plate==id;
        if(a.kind==JointActionKind::SENSE) {
            bool visible=at;for(unsigned parent:item.inside)visible|=bool(c.open_here.count(parent));
            if(visible!=bool(e.observation.ids.count(id)))return false;
        } else if(a.kind==JointActionKind::ASK && a.a==id) {
            // This is a proposal hint, never a likelihood or a hard truth.
            // The complete replay still checks noisy/random/blank answers,
            // the actual initial reply pool and the persistent answer order.
            latest_matches=o.reply.first=='a'?item.at==o.reply.second ||
                ((c.hand==id || c.plate==id) && c.robot==o.reply.second):
                o.reply.first=='i' && item.inside.count(unsigned(o.reply.second));
        } else if(e.observation.kind==JointObservation::Kind::FEEDBACK && a.a==id && a.kind!=JointActionKind::MOVE) {
            bool ok=false;
            switch(a.kind) {
            case JointActionKind::PICKUP:ok=!c.hand && c.plate!=id && at;break;
            case JointActionKind::PUTDOWN:ok=c.hand==id;break;
            case JointActionKind::TOPLATE:ok=c.hand==id && !c.plate;break;
            case JointActionKind::FROMPLATE:ok=!c.hand && c.plate==id;break;
            case JointActionKind::PUTIN:ok=c.hand==id && c.open_here.count(a.b);break;
            case JointActionKind::TAKEOUT:ok=!c.hand && c.open_here.count(a.b) && item.inside.count(a.b);break;
            default:throw std::logic_error("small block received invalid command");
            }
            if(ok!=e.observation.success)return false;
            if(ok) {
                if(a.kind==JointActionKind::PUTIN){item.inside.insert(a.b);if(item.at==c.robot)item.at=-1;}
                else {item.at=c.robot;if(a.kind==JointActionKind::TAKEOUT)item.inside.erase(a.b);}
            }
        }
        if(a.kind==JointActionKind::MOVE && e.observation.success && (c.hand==id || c.plate==id))item.at=int(a.a);
    }
    return true;
}
}
ConditionedProposal EpisodeProposal::generate(const JointWorld& base,const std::vector<PublicPriorFactor>& factors,
    const std::vector<EpisodeEvidence>& history,std::size_t constraints,std::size_t particles,
    std::uint64_t offset,std::size_t cap,std::chrono::milliseconds wall) {
    if(!particles || particles>4096 || !cap || wall.count()<=0)throw std::invalid_argument("invalid conditional proposal budget");
    std::size_t previous=0;
    for(const auto& e:history) {
        if(!e.receipt || e.receipt<=previous)throw std::invalid_argument("unordered public evidence");previous=e.receipt;
        const auto expected=e.action.kind==JointActionKind::SENSE?JointObservation::Kind::VISIBLE:
            e.action.kind==JointActionKind::ASK?JointObservation::Kind::ANSWER:JointObservation::Kind::FEEDBACK;
        if(e.observation.kind!=expected)throw std::invalid_argument("command feedback mismatch");
    }
    // Validate all factors before decomposing them. This is at most one draw.
    EpisodePrior::generate(base,factors,constraints,1,offset);
    std::vector<PublicPriorFactor> globals;std::map<unsigned,std::vector<PublicPriorFactor>> blocks;
    for(const auto& item:base.objects)if(item.second.small)blocks[item.first]={};
    for(const auto& f:factors) {
        if((f.field==PriorField::EXPLICIT_AT || f.field==PriorField::INSIDE_EDGE) && base.objects.at(f.object).small)
            blocks[f.object].push_back(f);
        else globals.push_back(f);
    }
    auto shared=EpisodePrior::generate(base,globals,constraints,particles,offset,true);
    ConditionedProposal result;result.scope="public feedback conditional block importance approximation; no certified finite-domain coverage";
    const auto end=std::chrono::steady_clock::now()+wall;
    const std::size_t repeats=std::max(std::size_t(1),particles/shared.scenes.size());
    struct LocalChoice {JointObject item;double prior;bool matches;};
    struct LocalBlock {std::vector<LocalChoice> choices;double mass=0,clue_mass=0;};
    // A call owns one frozen public history and factor catalogue. Given the
    // same shared history contexts, a small block has exactly the same
    // acceptance distribution. Answer-order seeds do not affect this physical
    // filtering and are still handled independently by full replay.
    std::map<std::pair<unsigned,std::vector<int>>,LocalBlock> cache;
    std::size_t draw=0;
    for(const auto& g:shared.scenes)for(std::size_t repeat=0;repeat<repeats;++repeat,++draw) {
        if(std::chrono::steady_clock::now()>=end){result.complete=false;result.wall_cut=true;result.scenes.clear();return result;}
        std::vector<Context> states;if(!contexts(g.episode.world,history,states))continue;
        std::vector<int> signature;
        for(const auto& c:states) {
            signature.push_back(c.robot);signature.push_back(int(c.hand));signature.push_back(int(c.plate));
            signature.push_back(int(c.open_here.size()));
            for(unsigned id:c.open_here)signature.push_back(int(id));
        }
        JointWorld candidate=g.episode.world;double importance=g.weight/repeats;bool viable=true;
        for(const auto& block:blocks) {
            std::size_t combinations=1;
            for(const auto& f:block.second) {
                if(combinations>4096/f.values.size()){result.complete=false;result.work_cut=true;result.scenes.clear();return result;}
                combinations*=f.values.size();
            }
            const auto key=std::make_pair(block.first,signature);
            auto entry=cache.find(key);
            if(entry!=cache.end())++result.block_cache_hits;
            else {
            LocalBlock local;
            for(std::size_t n=0;n<combinations;++n) {
                auto item=base.objects.at(block.first);double probability=1;std::size_t code=n;
                for(const auto& f:block.second) {
                    const auto& v=f.values[code%f.values.size()];code/=f.values.size();probability*=v.probability;
                    if(f.field==PriorField::EXPLICIT_AT)item.at=v.value;
                    else if(v.value)item.inside.insert(f.parent);else item.inside.erase(f.parent);
                }
                if(probability<=0)continue;
                bool matches=false;
                if(explains(block.first,item,history,states,result.checks,cap,end,result,matches)) {
                    local.mass+=probability;if(matches)local.clue_mass+=probability;
                    local.choices.push_back({std::move(item),probability,matches});
                }
                if(!result.complete){result.scenes.clear();return result;}
            }
            entry=cache.emplace(key,std::move(local)).first;
            }
            const auto& local=entry->second.choices;const double mass=entry->second.mass,clue_mass=entry->second.clue_mass;
            if(mass<=0){viable=false;break;}
            const auto q=[&](const LocalChoice& item) {
                const double conditional=item.prior/mass;
                return clue_mass>0?.5*conditional+(item.matches?.5*item.prior/clue_mass:0):conditional;
            };
            double choice=double(mix((offset+draw)*0xd6e8feb86659fd93ULL+block.first)>>11)/9007199254740992.0;
            const LocalChoice* selected=&local.back();
            for(const auto& item:local){choice-=q(item);if(choice<0){selected=&item;break;}}
            candidate.objects[block.first]=selected->item;
            // The target remains the original generative prior. No noisy
            // answer is counted here as truth or counted twice as likelihood.
            // q has a nonzero prior component for every positive hypothesis.
            importance*=selected->prior/q(*selected);
            if(clue_mass>0)++result.clue_mixture_draws;
        }
        if(viable && importance>0) {
            candidate.initial_reply_counts.clear();candidate.freezeSdkReplyDomain();
            candidate.answer_order_assumed=true;candidate.answer_order_seed=mix(offset+draw+0x859b66ULL);
            SdkEpisode initial;initial.world=std::move(candidate);initial.credits.assign(constraints,true);
            result.scenes.push_back({std::move(initial),importance});
        }
    }
    return result;
}
