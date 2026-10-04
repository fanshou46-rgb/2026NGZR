#include "rdfw.hpp"
#include "evaluate.h"
#include <cassert>
#include <cstdlib>
#include <iostream>
#include <fstream>
#include <algorithm>
using namespace _home;
namespace _home { struct ScoreSemanticsTestAccess {
    static void sense(RDFW& w) { w.SenseCurrentLocationOnly(true); }
    static bool action(RDFW& w,int a) {
        if(a==0)return w.PickUp(3);
        if(a==1)return w.PutDown(3);
        if(a==2)return w.FromPlate(3);
        if(a==3)return w.PutIn(3,2);
        assert(false);return false;
    }
}; }
int main(int argc,char** argv) {
    assert(argc==3);const int test=std::atoi(argv[2]);
    const std::string common="(at 0 1) (sort 1 table) (size 1 big) (at 1 1) "
        "(sort 2 cupboard) (size 2 big) (type 2 container) (at 2 2) (opened 2) "
        "(sort 3 cup) (size 3 small) (at 3 1)";
    const std::string slots=test==1 || test==4?"(hold 3) (plate 0) ":
        test==2 || test==5?"(hold 0) (plate 3) ":"(hold 0) (plate 0) ";
    const std::string env="(:domain "+slots+common+")";
    const std::string task="(:ins (:task (putdown X) (:cond (sort X cup))))";
    Evaluate sdk;std::string name="storage-authority-"+std::to_string(test);
    sdk.newteam(name.c_str());assert(sdk.init_et(env.c_str(),env.size()));
    assert(sdk.init_it(task.c_str(),task.size()));
    auto owner=std::make_shared<RDFW>();auto& w=*owner;
    char program[]="authority",path[]="-path";char* args[]={program,path,argv[1]};
    w.Init(3,args);w.stage=2;
    // Identical weak agent input for three different SDK truths. No truth is
    // copied into canonical slots or supplied to planning/terminal checking.
    assert(w.ParseEnv("(hold 0) (plate 0) "+common));
    assert(w.ParseInstruction(task));
    std::vector<unsigned int> ids;sdk.EvaluateSense(ids);std::sort(ids.begin(),ids.end());
    assert((ids==std::vector<unsigned int>{1,3}));
    w.SetSenseResult(ids);ScoreSemanticsTestAccess::sense(w);
    assert(w.FactValue(StateField::HOLD)==UNKNOWN && w.FactValue(StateField::PLATE)==UNKNOWN);
    assert(!w.IsNotStoredFact(3));
    assert(w.GetTerminalSummary().goals[0]==TerminalStatus::UNKNOWN);
    int cost=1;
    auto act=[&](int a) {
        bool ok=a==0?sdk.EvaluatePickUp(3):a==1?sdk.EvaluatePutDown(3):
            a==2?sdk.EvaluateFromPlate(3):sdk.EvaluatePutIn(3,2);
        w.SetActionResults({ok});assert(ScoreSemanticsTestAccess::action(w,a)==ok);
        cost+=2;return ok;
    };
    if(test==3 || test==6) {
        assert(act(0));assert(act(1));assert(w.IsNotStoredFact(3));
        assert(w.FactValue(StateField::PLATE)==UNKNOWN);
        assert(w.GetTerminalSummary().goals[0]==TerminalStatus::SATISFIED);
        if(test==6) {
            assert(act(0));assert(!w.IsNotStoredFact(3));
            w.MarkUnresolved(StateField::HOLD,0);
            assert(w.GetTerminalSummary().goals[0]==TerminalStatus::UNKNOWN);
        }
    } else if(test==4) {
        assert(act(1));assert(!w.IsNotStoredFact(3));
        assert(w.GetTerminalSummary().goals[0]==TerminalStatus::UNKNOWN);
    } else if(test==5) {
        assert(act(2));assert(act(1));assert(w.IsNotStoredFact(3));
        assert(w.GetTerminalSummary().goals[0]==TerminalStatus::SATISFIED);
    }
    const int expected=((test==1 || test==2 || test==6)?0:40)-cost;
    const int actual=sdk.EndEvaluation(5.0);assert(actual==expected);
    std::ofstream trace(name+".txt");trace<<"sdk-score="<<actual<<"\ncanonical-not-stored="
        <<w.IsNotStoredFact(3)<<"\ncanonical-goal="<<TerminalStatusName(w.GetTerminalSummary().goals[0])<<"\n";
    std::cout<<name<<" SDK="<<actual<<" passed\n";
}
