#pragma once
#include <chrono>
#include <stdexcept>

namespace _home {
struct BudgetExceeded {};

class TimeBudget {
public:
    typedef std::chrono::steady_clock Clock;
    enum class Phase { Normal, Finishing, Expired };
    TimeBudget() : limit_ms_(4500), reserve_ms_(500), started_(Clock::now()) {}
    void configure(long limit, long reserve) {
        if (limit < 0 || reserve < 0 || (limit > 0 && reserve >= limit))
            throw std::invalid_argument("budget must be 0 (disabled), or greater than reserve");
        limit_ms_ = limit;
        reserve_ms_ = reserve;
    }
    void reset() { started_ = Clock::now(); }
    long elapsed_ms() const {
        return std::chrono::duration_cast<std::chrono::milliseconds>(Clock::now() - started_).count();
    }
    Phase phase_at(long elapsed) const {
        if (limit_ms_ == 0) return Phase::Normal;
        if (elapsed >= limit_ms_) return Phase::Expired;
        if (elapsed >= limit_ms_ - reserve_ms_) return Phase::Finishing;
        return Phase::Normal;
    }
    Phase phase() const { return phase_at(elapsed_ms()); }
    void check() const { if (phase() == Phase::Expired) throw BudgetExceeded(); }
    long limit_ms() const { return limit_ms_; }
private:
    long limit_ms_, reserve_ms_;
    Clock::time_point started_;
};
}
