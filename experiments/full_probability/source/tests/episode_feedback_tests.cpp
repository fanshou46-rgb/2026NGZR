#include "sdk_episode.hpp"
#include <cassert>
#include <cmath>
#include <iostream>
using namespace _home;
void sameWorld(const JointWorld& a,const JointWorld& b) {
    assert(a.robot==b.robot && a.hand==b.hand && a.plate==b.plate && a.locations==b.locations);
    assert(a.initial_reply_counts==b.initial_reply_counts && a.answer_order_seed==b.answer_order_seed && a.answer_order_assumed==b.answer_order_assumed);
    assert(a.objects.size()==b.objects.size());
    for(const auto& pair:a.objects) {
        const auto& x=pair.second;const auto& y=b.objects.at(pair.first);
        assert(x.small==y.small && x.container==y.container && x.at==y.at && x.opened==y.opened && x.inside==y.inside);
    }
}
int main() {
    SdkEpisodeModel model;
    model.goals={SdkPredicate{"pickup",{{4,0}}},SdkPredicate{"putin",{{4,2}}},SdkPredicate{"goto",{{2,0}}}};
    model.constraints={{SdkPredicate{"plate",{{4,0}}},false},{SdkPredicate{"closed",{{2,0}}},true}};
    const auto ask=AskObservationModel({{'a',1},{'a',2},{'i',2},{'i',3}}).withPersistentAnswerOrderPrior();
    const std::vector<JointAction> actions={{JointActionKind::MOVE,1},{JointActionKind::MOVE,2},
        {JointActionKind::PICKUP,4},{JointActionKind::PUTDOWN,4},{JointActionKind::TOPLATE,4},
        {JointActionKind::FROMPLATE,4},{JointActionKind::OPEN,2},{JointActionKind::CLOSE,2},
        {JointActionKind::PUTIN,4,2},{JointActionKind::TAKEOUT,4,2},{JointActionKind::SENSE},
        {JointActionKind::ASK,4},{JointActionKind::ASK,5},{JointActionKind::ASK,0}};
    unsigned worlds=0,branches=0;
    for(int robot:{1,2})for(int at:{-1,1,2})for(unsigned parents=0;parents<4;++parents)
    for(bool open2:{false,true})for(bool open3:{false,true})for(unsigned hand:{0u,4u})for(unsigned plate:{0u,4u}) {
        SdkEpisode initial;auto& w=initial.world;w.robot=robot;w.locations={1,2};w.hand=hand;w.plate=plate;
        w.objects[2]=JointObject(false,true,1,0,open2);w.objects[3]=JointObject(false,true,2,0,open3);
        w.objects[4]=JointObject(true,false,at);w.objects[5]=JointObject(true,false,-1);
        if(parents&1)w.objects[4].inside.insert(2);if(parents&2)w.objects[4].inside.insert(3);
        w.answer_order_assumed=true;w.answer_order_seed=++worlds;w.freezeSdkReplyDomain();
        initial.paid=7;initial.credits={true,true};
        auto other=initial;other.world.robot=3-robot;other.world.hand=0;other.world.plate=4;
        // Keep the frozen INITIAL noise/map domain after a different current
        // robot position, as actual SDK movement requires.
        const EpisodeBelief prior({{initial,.35},{other,.65}});
        for(const auto& action:actions) {
            const auto enumerated=prior.branches(model,action,ask);
            for(const auto& branch:enumerated) {
                auto conditioned=prior;
                const double p=conditioned.conditionPublicFeedback(model,action,branch.observation,ask);++branches;
                assert(std::abs(p-branch.probability)<1e-12);
                assert(conditioned.support().size()==branch.posterior.support().size());
                for(std::size_t i=0;i<conditioned.support().size();++i) {
                    const auto& x=conditioned.support()[i];const auto& y=branch.posterior.support()[i];
                    assert(std::abs(x.weight-y.weight)<1e-12 && x.episode.paid==y.episode.paid && x.episode.credits==y.episode.credits);
                    sameWorld(x.episode.world,y.episode.world);
                }
                const auto a=conditioned.reward(model),b=branch.posterior.reward(model);
                assert(std::abs(a.lower-b.lower)<1e-10 && std::abs(a.upper-b.upper)<1e-10);
            }
            JointObservation impossible;impossible.kind=JointObservation::Kind::ANSWER;impossible.reply={'a',999};
            auto unchanged=prior;assert(unchanged.conditionPublicFeedback(model,action,impossible,ask)==0);
            for(std::size_t i=0;i<prior.support().size();++i) {
                assert(unchanged.support()[i].weight==prior.support()[i].weight && unchanged.support()[i].episode.paid==7);
                sameWorld(unchanged.support()[i].episode.world,prior.support()[i].episode.world);
            }
        }
    }
    assert(worlds==384 && branches>6000);
    std::cout<<"observed-only posterior equals full enumeration: "<<worlds<<" joint worlds, "<<branches<<" branches, fees/credits/noise/order/slots/independent AT/multi-inside checked\n";
}
