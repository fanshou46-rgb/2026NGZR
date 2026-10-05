#include "model_time_ledger.hpp"
#include <cassert>
#include <iostream>
using namespace _home;
namespace { ModelTimeLedger::Clock::time_point tick(long long ns) {
    return ModelTimeLedger::Clock::time_point(std::chrono::nanoseconds(ns));
} }
int main() {
    for(unsigned repeat=0;repeat<50;++repeat) {
        ModelTimeLedger m;
        m.start("initialize",0,tick(0));m.close(0,tick(2));
        m.start("initial_forecast",0,tick(2));m.close(0,tick(4));
        // The ten-nanosecond gap is an SDK call, not model computation.
        m.start("feedback_replay",1,tick(14));m.close(1,tick(16));
        m.start("aborted_candidate_search",1,tick(16));m.close(1,tick(31));
        assert(m.used()==std::chrono::nanoseconds(21) && !m.isActive() && m.records().size()==4);
        ModelTimeLedger::Clock::duration sum{};
        for(const auto& s:m.records())sum+=s.end-s.begin;
        assert(sum==m.used());
        bool duplicate=false,overlap=false,nested=false,backwards=false,sdk_inside=false,stale=false;
        try{m.close(1,tick(32));}catch(const std::logic_error&){duplicate=true;}
        try{m.start("overlap",1,tick(30));}catch(const std::logic_error&){overlap=true;}
        try{m.start("stale",0,tick(31));}catch(const std::logic_error&){stale=true;}
        m.start("candidate",1,tick(32));
        try{m.start("nested",1,tick(33));}catch(const std::logic_error&){nested=true;}
        try{m.close(1,tick(31));}catch(const std::logic_error&){backwards=true;}
        try{m.close(2,tick(33));}catch(const std::logic_error&){sdk_inside=true;}
        assert(m.isActive());m.close(1,tick(33));
        assert(duplicate && overlap && nested && backwards && sdk_inside && stale && m.used()==std::chrono::nanoseconds(22));
    }
    std::cout<<"50 deterministic model-time ledgers: aborted work charged once, SDK gaps excluded, exact totals and receipt/time violations rejected\n";
}
