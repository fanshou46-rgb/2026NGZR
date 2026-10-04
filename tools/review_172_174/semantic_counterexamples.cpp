// A reproduction succeeds when it confirms the documented disagreement.
// Passing this program does NOT mean the planner is correct.
#include "rdfw.hpp"
#include "joint_world.hpp"
#include "evaluate.h"
#include <cassert>
#include <cstdlib>
#include <fstream>
#include <iostream>
using namespace _home;
namespace _home { struct ScoreSemanticsTestAccess {
 static void sense(RDFW& w){w.SenseCurrentLocationOnly(true);}
 static bool pickup(RDFW& w){return w.PickUp(3);}
 static bool putdown(RDFW& w){return w.PutDown(3);}
 static bool close(RDFW& w){return w.Close(2);}
}; }
int main(int argc,char** argv){
 assert(argc==3);int test=std::atoi(argv[2]);
 const std::string common="(at 0 1) (sort 1 table) (size 1 big) (at 1 2) "
  "(sort 2 cupboard) (size 2 big) (type 2 container) (at 2 1) "+std::string(test==0 || test==3?"(opened 2) ":"(closed 2) ")+
  "(sort 3 cup) (size 3 small) (color 3 blue) (at 3 1) (inside 3 2)";
 const std::string facts=std::string("(hold 0) (plate ")+(test==3?"3":"0")+") "+common;
 const std::string env="(:domain "+facts+")";
 const std::string task="(:ins (:info (closed X) (:cond (sort X cupboard))) "
  "(:task (takeout X Y) (:cond (sort X cup) (color X blue) (sort Y cupboard))))";
 Evaluate sdk;sdk.newteam(("review-semantic-"+std::to_string(test)).c_str());
 assert(sdk.init_et(env.c_str(),env.size()));assert(sdk.init_it(task.c_str(),task.size()));
 if(test==3){
  JointWorld world;world.robot=1;world.plate=3;world.locations={1,2};
  world.objects={{1,{false,false,2}},{2,{false,true,1,0,true}},{3,{true,false,1,2}}};
  world.validate();bool sdk_ok=sdk.EvaluateTakeOut(3,2);bool throws=false;
  try{JointDynamics::step(world,{JointActionKind::TAKEOUT,3,2});}catch(const std::logic_error& e){throws=true;std::cout<<e.what()<<'\n';}
  std::cout<<"REPRO sdk_takeout="<<sdk_ok<<" joint_transition_throws="<<throws<<'\n';
  assert(sdk_ok && throws);return 0;
 }
 auto owner=std::make_shared<RDFW>();auto& w=*owner;
 char program[]="review",path[]="-path";char* args[]={program,path,argv[1]};w.Init(3,args);w.stage=2;
 assert(w.ParseEnv(facts));assert(w.ParseInstruction(task));int cost=0;
 if(test==0){bool ok=sdk.EvaluateClose(2);assert(ok);w.SetActionResults({ok});assert(ScoreSemanticsTestAccess::close(w));std::vector<unsigned> ids;sdk.EvaluateSense(ids);w.SetSenseResult(ids);ScoreSemanticsTestAccess::sense(w);cost=3;}
 else{bool ok=sdk.EvaluatePickUp(3);assert(ok);w.SetActionResults({ok});assert(ScoreSemanticsTestAccess::pickup(w));cost=2;
  if(test==2){ok=sdk.EvaluatePutDown(3);assert(ok);w.SetActionResults({ok});assert(ScoreSemanticsTestAccess::putdown(w));cost+=2;}}
 std::ifstream f("vstate.lp");std::string state((std::istreambuf_iterator<char>(f)),std::istreambuf_iterator<char>());
 std::ofstream("sdk-final-state.lp")<<state;
 int actual=sdk.EndEvaluation(5.0);auto terminal=w.GetTerminalSummary().goals.at(0);
 std::cout<<"REPRO case="<<test<<" canonical_inside="<<w.FactInside(3)<<" terminal="<<TerminalStatusName(terminal)<<" sdk_score="<<actual<<" action_cost="<<cost<<std::endl;
 assert(actual==-cost);assert(w.FactInside(3)==NONE);assert(terminal==TerminalStatus::SATISFIED);
}
