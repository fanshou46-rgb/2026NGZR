#pragma once
#include <chrono>
#include <string>
#include <utility>
#include <vector>
#include <stdexcept>
namespace _home {
// Only MODEL phases may be bracketed. The actual receipt watermark must not
// change inside a phase. SDK waits stay outside these explicit intervals.
class ModelTimeLedger {
public:
    using Clock=std::chrono::steady_clock;
    struct Span {
        std::string phase;Clock::time_point begin,end;std::size_t receipt_mark;
        Span(std::string name,Clock::time_point first,Clock::time_point last,std::size_t mark)
            :phase(std::move(name)),begin(first),end(last),receipt_mark(mark){}
    };
    Clock::time_point start(const std::string& phase,std::size_t receipts,Clock::time_point now=Clock::now()) {
        if(active || phase.empty() || (!spans.empty() && (now<spans.back().end || receipts<spans.back().receipt_mark)))
            throw std::logic_error("invalid model-time phase start");
        current_phase=phase;began=now;watermark=receipts;active=true;return began;
    }
    Clock::duration close(std::size_t receipts,Clock::time_point now=Clock::now()) {
        if(!active || receipts!=watermark || now<began)
            throw std::logic_error("SDK receipt or invalid time inside model phase");
        total+=now-began;spans.emplace_back(current_phase,began,now,watermark);active=false;return total;
    }
    bool isActive() const {return active;}
    Clock::duration used() const {return total;}
    const std::vector<Span>& records() const {return spans;}
private:
    bool active=false;
    Clock::time_point began{};
    Clock::duration total{};
    std::size_t watermark=0;
    std::string current_phase;
    std::vector<Span> spans;
};
}
