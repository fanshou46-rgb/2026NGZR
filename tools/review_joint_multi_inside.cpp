// Supplemental direct-SDK counterexample. Exit 0 confirms model disagreement.
#include "joint_world.hpp"
#include "evaluate.h"
#include <cassert>
#include <fstream>
#include <iostream>
#include <algorithm>
#include <cctype>
using namespace _home;
int main(){
 JointWorld w;w.robot=1;w.locations={1,2};
 w.objects={{1,{false,true,1,0,true}},{2,{false,true,2,0,true}},{3,{true,false,1,1}}};
 w.validate();
 const std::string env="(:domain (hold 0) (plate 0) (at 0 1) "
  "(sort 1 cupboard) (size 1 big) (type 1 container) (at 1 1) (opened 1) "
  "(sort 2 refrigerator) (size 2 big) (type 2 container) (at 2 2) (opened 2) "
  "(sort 3 cup) (size 3 small) (at 3 1) (inside 3 1))";
 const std::string task="(:ins (:task (takeout X Y) (:cond (sort X cup) (sort Y cupboard))))";
 Evaluate sdk;sdk.newteam("review-joint-multi-inside");
 assert(sdk.init_et(env.c_str(),env.size()));assert(sdk.init_it(task.c_str(),task.size()));
 assert(sdk.EvaluatePickUp(3));w=JointDynamics::step(w,{JointActionKind::PICKUP,3}).world;
 assert(sdk.EvaluateMove(2));w=JointDynamics::step(w,{JointActionKind::MOVE,2}).world;
 assert(sdk.EvaluatePutIn(3,2));w=JointDynamics::step(w,{JointActionKind::PUTIN,3,2}).world;
 std::ifstream f("vstate.lp");std::string state((std::istreambuf_iterator<char>(f)),std::istreambuf_iterator<char>());
 std::ofstream("sdk-final-state.lp")<<state;
 state.erase(std::remove_if(state.begin(),state.end(),[](unsigned char c){return std::isspace(c);}),state.end());
 const bool original=state.find("h(inside(3,1),0)")!=std::string::npos;
 const bool destination=state.find("h(inside(3,2),0)")!=std::string::npos;
 int score=sdk.EndEvaluation(5.0);
 std::cout<<"REPRO sdk_inside_original="<<original<<" sdk_inside_destination="<<destination<<" joint_inside="<<w.objects.at(3).inside<<" sdk_score="<<score<<std::endl;
 assert(original && destination && w.objects.at(3).inside==2 && score==-8);
}
