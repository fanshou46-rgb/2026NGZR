// Test-only author witness. Executes a supplied, documented action trace.
// Never linked into or selected by the competing src1.3.3-fixed solver.
#include <cserver/plug.hpp>
#include <fstream>
#include <sstream>
#include <iostream>
#include <cstdlib>
class Reference : public _home::Plug {
public:
    Reference():Plug("liuyifan1.0-reference") {}
    void Plan() override {
        const char* path=std::getenv("LIUYIFAN_REFERENCE_PLAN");
        if (!path) throw std::runtime_error("reference plan missing");
        std::ifstream f(path);
        if (!f) throw std::runtime_error("reference plan unreadable");
        std::string line;
        while (std::getline(f,line)) {
            std::istringstream s(line); std::string name; unsigned a=0,b=0;
            if (!(s>>name)) continue;
            s>>a>>b; bool ok=false;
            if(name=="Move") ok=Move(a);
            else if(name=="PickUp") ok=PickUp(a);
            else if(name=="PutDown") ok=PutDown(a);
            else if(name=="Open") ok=Open(a);
            else if(name=="Close") ok=Close(a);
            else if(name=="PutIn") ok=PutIn(a,b);
            else if(name=="TakeOut") ok=TakeOut(a,b);
            else throw std::runtime_error("unsupported reference action");
            std::cout<<"REFERENCE "<<line<<" "<<ok<<std::endl;
            if(!ok) throw std::runtime_error("reference action failed");
        }
    }
};
int main() { try { Reference p; p.Run(); } catch (const std::exception& e) {
    std::cerr<<e.what()<<std::endl; return 1;
} }
