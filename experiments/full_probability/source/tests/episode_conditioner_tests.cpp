#include "episode_conditioner.hpp"
#include <cassert>
#include <iostream>
using namespace _home;
PublicPriorFactor factor(PriorField field,unsigned object,unsigned parent,std::vector<PriorValue> values) {
    PublicPriorFactor f;f.field=field;f.object=object;f.parent=parent;f.values=std::move(values);return f;
}
JointObservation success(bool value){JointObservation o;o.success=value;return o;}
const PublicPriorFactor& find(const InitialConditioning& c,PriorField field,unsigned id) {
    for(const auto& f:c.factors)if(f.field==field&&f.object==id)return f;
    assert(false);return c.factors.front();
}
int main() {
    JointWorld w;w.robot=1;w.locations={1,2};w.objects[2]=JointObject(false,true,1);
    w.objects[3]=JointObject(true,false,1);w.objects[4]=JointObject(false,true,2);
    const auto h=factor(PriorField::HAND,0,0,{{0,.5},{3,.5}});
    const auto p=factor(PriorField::PLATE,0,0,{{0,.5},{3,.5}});
    const auto at=factor(PriorField::EXPLICIT_AT,3,0,{{1,.5},{2,.5}});
    const auto big=factor(PriorField::EXPLICIT_AT,4,0,{{1,.5},{2,.5}});
    const auto door=factor(PriorField::DOOR,2,0,{{0,.5},{1,.5}});
    for(unsigned repeat=0;repeat<50;++repeat) {
        JointObservation visible;visible.kind=JointObservation::Kind::VISIBLE;visible.ids={2,3};
        std::vector<EpisodeEvidence> history={{1,{JointActionKind::SENSE},visible},
            {2,{JointActionKind::PICKUP,3},success(true)},{3,{JointActionKind::MOVE,2},success(true)},
            {4,{JointActionKind::PUTDOWN,3},success(true)},{5,{JointActionKind::PICKUP,3},success(true)}};
        auto conditioned=EpisodeConditioner::initial(w,{h,p,at,big,door},history);
        assert(conditioned.consistent && conditioned.retained_prior_mass==.0625);
        assert(find(conditioned,PriorField::EXPLICIT_AT,3).values.size()==1);
        assert(find(conditioned,PriorField::EXPLICIT_AT,3).values[0].value==1); // late coordinate 2 is not initial
        assert(find(conditioned,PriorField::EXPLICIT_AT,4).values[0].value==2);
        assert(find(conditioned,PriorField::HAND,0).values[0].value==0);
        assert(find(conditioned,PriorField::PLATE,0).values[0].value==0);
        assert(find(conditioned,PriorField::DOOR,2).values.size()==2);
        JointObservation answer;answer.kind=JointObservation::Kind::ANSWER;answer.reply={'a',2};
        auto weak=EpisodeConditioner::initial(w,{h,p,at,big,door},{{1,{JointActionKind::ASK,3},answer}});
        assert(weak.consistent && weak.retained_prior_mass==1 && weak.proofs.empty());
        assert(find(weak,PriorField::EXPLICIT_AT,3).values.size()==2);
        auto failed=EpisodeConditioner::initial(w,{h,door},{{1,{JointActionKind::OPEN,2},success(false)}});
        assert(failed.consistent && find(failed,PriorField::DOOR,2).values.size()==2);
        auto same=w;same.objects[4].at=1;
        auto proof=EpisodeConditioner::initial(same,{h,door},{{1,{JointActionKind::OPEN,4},success(true)},
            {2,{JointActionKind::OPEN,2},success(false)}});
        assert(proof.consistent && find(proof,PriorField::HAND,0).values[0].value==0);
        assert(find(proof,PriorField::DOOR,2).values[0].value==1);
        visible.ids={3};
        auto contradiction=EpisodeConditioner::initial(w,{},{{1,{JointActionKind::SENSE},visible}});
        assert(!contradiction.consistent); // immutable public big at cannot be overwritten
    }
    std::cout<<"receipt-only initial conditioning, moved coordinates, weak Ask and 50 repeats passed\n";
}
