#include "cserver/plug.hpp"
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
class Reference : public _home::Plug {
public: Reference():Plug("review-reference"){}
protected:
 void Plan() override {
  const char* path=std::getenv("RDFW_REFERENCE_PLAN");
  if(!path)throw std::runtime_error("reference plan missing");
  std::ifstream in(path); std::string line;
  while(std::getline(in,line)) {
   std::istringstream s(line);std::string action;unsigned a=0,b=0;s>>action>>a>>b;bool ok=false;
   if(action=="Move")ok=Move(a);
   else if(action=="PickUp")ok=PickUp(a);
   else if(action=="PutDown")ok=PutDown(a);
   else if(action=="FromPlate")ok=FromPlate(a);
   else if(action=="Open")ok=Open(a);
   else if(action=="Close")ok=Close(a);
   else if(action=="TakeOut")ok=TakeOut(a,b);
   else throw std::runtime_error("unknown reference action");
   if(!ok){std::cerr<<"REFERENCE_ACTION_FAILED "<<line<<std::endl;return;}
  }
 }
};
int main(){Reference robot;robot.Run();}
