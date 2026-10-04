#include "evaluate.h"
#include <algorithm>
#include <cassert>
#include <iostream>
#include <string>
#include <vector>
int main() {
    const std::string env="(:domain (hold 0) (plate 0) (at 0 1) "
        "(sort 1 human) (size 1 big) (at 1 1) "
        "(sort 2 table) (size 2 big) (at 2 2) "
        "(sort 4 cupboard) (size 4 big) (type 4 container) (at 4 1) (closed 4) "
        "(sort 3 cup) (size 3 small) (at 3 2) (inside 3 4))";
    const std::string tasks="(:ins (:task (puton X Y) (:cond (sort X cup) (sort Y table))) "
        "(:task (goto X) (:cond (sort X table))))";
    Evaluate sdk;sdk.newteam("goto-oracle");
    assert(sdk.init_et(env.c_str(),env.size()));assert(sdk.init_it(tasks.c_str(),tasks.size()));
    assert(sdk.EvaluateMove(2));std::vector<unsigned> ids;sdk.EvaluateSense(ids);
    assert(std::find(ids.begin(),ids.end(),3)!=ids.end());
    const int base=sdk.EndEvaluation(5.0);assert(base==75); // G2 minus Move4 + Sense1
    std::cout<<"SDK sees cup with explicit at despite closed inside; G=2 K=5 base="<<base<<"\n";
}
