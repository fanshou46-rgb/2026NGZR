#include "episode_conditioner.hpp"
#include <algorithm>
#include <set>
using namespace _home;
InitialConditioning EpisodeConditioner::initial(const JointWorld& base,const std::vector<PublicPriorFactor>& factors,
    const std::vector<EpisodeEvidence>& history) {
    InitialConditioning result;result.factors=factors;
    const auto restrict=[&](PriorField field,unsigned object,unsigned parent,int value,bool equal,
        std::size_t receipt,const char* predicate) {
        if(!result.consistent)return;
        auto variable=std::find_if(result.factors.begin(),result.factors.end(),[&](const PublicPriorFactor& f){
            return f.field==field && f.object==object && f.parent==parent;
        });
        if(variable==result.factors.end()) {
            int fixed=0;
            if(field==PriorField::HAND)fixed=int(base.hand);
            else if(field==PriorField::PLATE)fixed=int(base.plate);
            else if(field==PriorField::DOOR)fixed=base.objects.at(object).opened?1:0;
            else if(field==PriorField::INSIDE_EDGE)fixed=base.objects.at(object).inside.count(parent)?1:0;
            else fixed=base.objects.at(object).at;
            if((fixed==value)!=equal)result.consistent=false;
        } else {
            double retained=0;
            for(const auto& candidate:variable->values)if((candidate.value==value)==equal)retained+=candidate.probability;
            if(retained<=0){result.consistent=false;return;}
            variable->values.erase(std::remove_if(variable->values.begin(),variable->values.end(),
                [&](const PriorValue& v){return (v.value==value)!=equal;}),variable->values.end());
            for(auto& candidate:variable->values)candidate.probability/=retained;
            result.retained_prior_mass*=retained;
        }
        result.proofs.push_back({field,object,parent,receipt,predicate});
    };
    const auto variable=[&](PriorField field,unsigned object) {
        return std::any_of(factors.begin(),factors.end(),[&](const PublicPriorFactor& f){return f.field==field&&f.object==object;});
    };
    int robot=base.robot,hand=variable(PriorField::HAND,0)?-1:int(base.hand);
    bool hand_changed=false,plate_changed=false;
    std::set<unsigned> door_changed;
    std::set<std::pair<unsigned,unsigned>> edge_changed;
    std::map<unsigned,int> big_at;
    for(const auto& object:base.objects)if(!object.second.small && !variable(PriorField::EXPLICIT_AT,object.first))big_at[object.first]=object.second.at;
    for(const auto& event:history) {
        const auto& a=event.action;const auto& o=event.observation;
        if(o.kind==JointObservation::Kind::VISIBLE) {
            for(const auto& object:base.objects)if(!object.second.small) {
                const bool seen=o.ids.count(object.first);
                restrict(PriorField::EXPLICIT_AT,object.first,0,robot,seen,event.receipt,
                    seen?"static_big_id_visible_at_robot":"static_big_id_absent_at_robot");
                if(seen)big_at[object.first]=robot;
            }
            continue;
        }
        if(o.kind!=JointObservation::Kind::FEEDBACK)continue; // Ask remains weak
        if(!o.success) {
            if((a.kind==JointActionKind::OPEN || a.kind==JointActionKind::CLOSE) && hand==0 &&
               big_at.count(a.a) && big_at[a.a]==robot && !door_changed.count(a.a)) {
                restrict(PriorField::DOOR,a.a,0,a.kind==JointActionKind::OPEN?1:0,true,event.receipt,
                    "false_door_command_all_other_preconditions_proved");
            }
            continue;
        }
        if(a.kind==JointActionKind::MOVE){robot=int(a.a);continue;}
        if(a.kind==JointActionKind::OPEN || a.kind==JointActionKind::CLOSE ||
           a.kind==JointActionKind::PUTIN || a.kind==JointActionKind::TAKEOUT) {
            const unsigned container=(a.kind==JointActionKind::OPEN || a.kind==JointActionKind::CLOSE)?a.a:a.b;
            restrict(PriorField::EXPLICIT_AT,container,0,robot,true,event.receipt,"successful_container_command_static_colocation");
            big_at[container]=robot;
        }
        const bool requires_empty=a.kind==JointActionKind::OPEN || a.kind==JointActionKind::CLOSE ||
            a.kind==JointActionKind::PICKUP || a.kind==JointActionKind::FROMPLATE || a.kind==JointActionKind::TAKEOUT;
        if(requires_empty && !hand_changed)restrict(PriorField::HAND,0,0,0,true,event.receipt,"successful_command_initial_empty_hand");
        if((a.kind==JointActionKind::PUTDOWN || a.kind==JointActionKind::TOPLATE || a.kind==JointActionKind::PUTIN) && !hand_changed)
            restrict(PriorField::HAND,0,0,int(a.a),true,event.receipt,"successful_command_initial_held_item");
        if(a.kind==JointActionKind::PICKUP && !plate_changed)
            restrict(PriorField::PLATE,0,0,int(a.a),false,event.receipt,"successful_pickup_initial_tray_not_item");
        if(a.kind==JointActionKind::TOPLATE && !plate_changed)
            restrict(PriorField::PLATE,0,0,0,true,event.receipt,"successful_toplate_initial_empty_tray");
        if(a.kind==JointActionKind::FROMPLATE && !plate_changed)
            restrict(PriorField::PLATE,0,0,int(a.a),true,event.receipt,"successful_fromplate_initial_tray_item");
        if(a.kind==JointActionKind::OPEN || a.kind==JointActionKind::CLOSE) {
            if(!door_changed.count(a.a))restrict(PriorField::DOOR,a.a,0,a.kind==JointActionKind::OPEN?0:1,true,event.receipt,
                "first_successful_door_command_initial_state");
            door_changed.insert(a.a);hand=0;
        } else if(a.kind==JointActionKind::PICKUP) {
            // Before either slot has changed, successful PickUp proves it was
            // not initially stored and thus identifies its initial explicit at.
            if(!hand_changed && !plate_changed)restrict(PriorField::EXPLICIT_AT,a.a,0,robot,true,event.receipt,
                "first_pickup_unmoved_unstored_item_initial_at");
            hand=int(a.a);hand_changed=true;
        } else if(a.kind==JointActionKind::TAKEOUT) {
            if(!edge_changed.count({a.a,a.b}))restrict(PriorField::INSIDE_EDGE,a.a,a.b,1,true,event.receipt,
                "first_takeout_initial_inside_edge");
            edge_changed.insert({a.a,a.b});hand=int(a.a);hand_changed=true;
        } else if(a.kind==JointActionKind::PUTIN) {
            edge_changed.insert({a.a,a.b});hand=0;hand_changed=true;
        } else if(a.kind==JointActionKind::PUTDOWN || a.kind==JointActionKind::TOPLATE) {
            hand=0;hand_changed=true;if(a.kind==JointActionKind::TOPLATE)plate_changed=true;
        } else if(a.kind==JointActionKind::FROMPLATE) {
            hand=int(a.a);hand_changed=true;plate_changed=true;
        }
    }
    return result;
}
