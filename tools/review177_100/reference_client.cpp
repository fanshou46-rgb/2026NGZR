#include "cserver/plug.hpp"
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
class Reference : public _home::Plug {
public: Reference():Plug("independent-100-reference"){}
protected:
 void Plan() override {
  const char* path=std::getenv("RDFW_REFERENCE_PLAN");
  if(!path)throw std::runtime_error("reference missing");
  std::ifstream in(path);std::string line;
  while(std::getline(in,line)) {
   std::istringstream s(line);std::string action;unsigned a=0,b=0;s>>action>>a>>b;bool ok=false;
   if(action=="move")ok=Move(a);else if(action=="pickup")ok=PickUp(a);
   else if(action=="putdown")ok=PutDown(a);else if(action=="fromplate")ok=FromPlate(a);
   else if(action=="toplate")ok=ToPlate(a);else if(action=="open")ok=Open(a);
   else if(action=="close")ok=Close(a);else if(action=="takeout")ok=TakeOut(a,b);
   else if(action=="putin")ok=PutIn(a,b);else if(action=="sense"){std::vector<unsigned> ids;Sense(ids);ok=true;}
   else if(action=="askloc"){AskLoc(a);ok=true;}
   else throw std::runtime_error("unknown reference action: "+action);
   if(!ok){std::cerr<<"REFERENCE_ACTION_FAILED "<<line<<std::endl;return;}
  }
 }
};
int main(){Reference robot;robot.Run();}
