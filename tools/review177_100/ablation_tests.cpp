#include "rdfw.hpp"
#include "audit_ablation.hpp"
#include <cassert>
#include <cmath>
#include <iostream>
using namespace _home;
namespace _home {struct InformationModelTestAccess {
 static ProbabilityBounds forecast(RDFW&w,unsigned id,int loc,unsigned opened=0){return w.VisibilityProbability(id,loc,opened);}
};}
int main(int argc,char**argv) {
 assert(argc==2);const int mode=AuditAblation();
 LocationBelief belief;belief.initialize({{'a',1},{'a',2}},{'a',1});
 if(mode==1)assert(std::abs(belief.probability({'a',1})-belief.probability({'a',2}))<1e-12);
 else assert(belief.probability({'a',1})>belief.probability({'a',2}));
 AskObservationModel model({{'a',1},{'a',2}});
 double sum=0;for(auto observation:model.observations())sum+=model.likelihood(observation,{'a',1});assert(std::abs(sum-1)<1e-12);
 if(mode==1 || mode==2) {
  for(auto observation:model.observations())assert(model.likelihood(observation,{'a',1})==model.likelihood(observation,{'a',2}));
  const auto before=belief.distribution();assert(belief.posterior({'a',2},model).distribution()==before);
  assert(belief.observe({'a',2},model,7));assert(belief.distribution()==before);assert(!belief.observe({'a',2},model,7));
 } else {assert(belief.posterior({'a',2},model).probability({'a',2})>belief.probability({'a',2}));}
 belief.ruleOut({'a',2});assert(belief.probability({'a',2})==0);
 belief.observe({'a',1},model,8);assert(belief.probability({'a',2})==0);
 auto w=std::make_shared<RDFW>();char n[]="audit",p[]="-path";char*args[]={n,p,argv[1]};w->Init(3,args);w->stage=1;
 assert(w->ParseEnv("(hold 0) (plate 0) (at 0 1) (sort 1 human) (size 1 big) (at 1 1) "
   "(sort 2 table) (size 2 big) (at 2 2) (sort 3 cup) (size 3 small) (at 3 2) "
   "(sort 4 cupboard) (size 4 big) (at 4 1) (type 4 container) (closed 4)"));
 const auto before=w->DebugStateSnapshot();auto known=InformationModelTestAccess::forecast(*w,3,2);assert(known.lower==1 && known.upper==1);
 assert(w->DebugStateSnapshot()==before);
 w->ApplyStateValue(StateField::LOCATION,3,UNKNOWN,false,EvidenceSource::ASK_ANSWER);
 const auto fact=w->ExplicitAt(3);assert(fact==2); // weak hints cannot erase physical truth in any arm
 assert(InformationModelTestAccess::forecast(*w,3,2).lower==1);
 std::cout<<"ABLATION_MODE "<<mode<<" PASS likelihood, posterior, hard exclusion, canonical authority, read isolation\n";
}
