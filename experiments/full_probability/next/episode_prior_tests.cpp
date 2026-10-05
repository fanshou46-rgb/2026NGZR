#include "episode_prior.hpp"
#include <cassert>
#include <iostream>
using namespace _home;
PublicPriorFactor factor(PriorField f,unsigned id,unsigned parent) {
    PublicPriorFactor p;p.field=f;p.object=id;p.parent=parent;p.values={{0,.5},{1,.5}};return p;
}
int main() {
    JointWorld w;w.robot=1;w.locations={1,2};w.objects[2]=JointObject(false,true,1);
    w.objects[3]=JointObject(true,false,1);w.objects[4]=JointObject(false,true,2);
    auto hand=factor(PriorField::HAND,0,0);hand.values={{0,.5},{3,.5}};
    auto plate=hand;plate.field=PriorField::PLATE;
    auto one=factor(PriorField::INSIDE_EDGE,3,2),two=factor(PriorField::INSIDE_EDGE,3,4);
    const std::vector<PublicPriorFactor> factors={hand,plate,one,two};
    for(unsigned repeat=0;repeat<50;++repeat) {
        const auto exact=EpisodePrior::generate(w,factors,2,32);
        assert(exact.exact && exact.assignments==16 && exact.scenes.size()==16);
        unsigned coexist=0,multiparent=0;double mass=0;
        for(const auto& s:exact.scenes) {
            const auto& world=s.episode.world;mass+=s.weight;
            assert(s.episode.paid==0 && s.episode.credits==std::vector<bool>({true,true}));
            if(world.hand==3 && world.plate==3)++coexist;
            if(world.objects.at(3).inside.size()==2)++multiparent;
            assert(world.objects.at(3).at==1); // at and inside remain independent
        }
        assert(coexist==4 && multiparent==4 && mass==1);
        const auto sampled=EpisodePrior::generate(w,factors,2,8);
        assert(!sampled.exact && sampled.draws==8 && sampled.scenes.size()==8);
        const auto duplicate=EpisodePrior::generate(w,factors,2,8);
        for(std::size_t i=0;i<sampled.scenes.size();++i) {
            const auto& a=sampled.scenes[i].episode.world;const auto& b=duplicate.scenes[i].episode.world;
            assert(a.hand==b.hand && a.plate==b.plate && a.objects.at(3).inside==b.objects.at(3).inside);
        }
    }
    std::cout<<"public factor prior, dual storage, independent at/multi-parent and 50 repeats passed\n";
}
