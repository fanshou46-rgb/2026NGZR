#include "rdfw.hpp"
#include <atomic>
#include <cassert>
#include <chrono>
#include <condition_variable>
#include <exception>
#include <future>
#include <iostream>
#include <memory>
#include <mutex>
#include <stdexcept>
#include <thread>
#include <cstring>
#include <new>

using namespace _home;

struct Barrier {
    std::mutex mutex;
    std::condition_variable changed;
    bool entered = false, released = false;
    void pause() {
        std::unique_lock<std::mutex> lock(mutex);
        entered = true; changed.notify_all();
        changed.wait(lock, [this] { return released; });
    }
    void wait() {
        std::unique_lock<std::mutex> lock(mutex);
        assert(changed.wait_for(lock, std::chrono::seconds(3), [this] { return entered; }));
    }
    void release() {
        std::lock_guard<std::mutex> lock(mutex);
        released = true; changed.notify_all();
    }
};

std::shared_ptr<RDFW> world(const char* words) {
    auto value = std::make_shared<RDFW>();
    char program[] = "lifecycle"; char path[] = "-path";
    char* args[] = {program, path, const_cast<char*>(words)};
    value->Init(3, args);
    // Invalid input deliberately ends without platform calls when not cancelled.
    value->SetTestInput("invalid environment", "");
    return value;
}

int main(int argc, char** argv) {
    assert(argc == 3);
    const int test = std::stoi(argv[2]);
    auto value = world(argv[1]);
    if (test == 0 || test == 2 || test == 4 || test == 5 || test == 6) {
        Barrier barrier;
        std::atomic<bool> fini_started(false);
        std::exception_ptr planner_error;
        const auto hook = [&] {
            barrier.pause();
            if (test == 2) throw std::runtime_error("unrelated input error");
            if (test == 6) throw std::runtime_error("platform disconnected");
        };
        if (test >= 5) {
            value->stage = 1;
            value->SetTestInput("(at 0 1) (hold 0) (plate 0) (sort 1 table) (size 1 big) (at 1 2)",
                "(:ins (:task (goto X) (:cond (sort X table))))");
            value->SetPlatformHook(hook);
        } else {
            value->SetEnvReadHook(hook);
        }
        std::thread planner([&] { try { value->Plan(); } catch (...) { planner_error = std::current_exception(); } });
        barrier.wait();
        auto cleanup = std::async(std::launch::async, [&] { fini_started.store(true); value->Fini(); });
        while (!fini_started.load()) std::this_thread::yield();
        const bool cleanup_waited = cleanup.wait_for(std::chrono::milliseconds(150)) == std::future_status::timeout;
        barrier.release();
        planner.join(); cleanup.get();
        if (!cleanup_waited) {
            std::cerr << "REGRESSION: Fini cleaned state while Plan still owned it\n";
            return 42; // same test against unchanged 1.6.7 is expected to fail here
        }
        assert(value->TestPlatformCalls() == (test >= 5 ? 1U : 0U));
        assert(value->objects.size() == 1 && value->objects[0].get() == static_cast<Object*>(value.get()));
        if (test == 2 || test == 6) {
            assert(planner_error);
            try { std::rethrow_exception(planner_error); }
            catch (const std::runtime_error& error) {
                assert(std::string(error.what()) == (test == 2 ? "unrelated input error" : "platform disconnected"));
            }
        } else {
            assert(!planner_error);
        }
        if (test == 4) {
            // Cancellation of one test must not disable the next SDK test.
            value->SetEnvReadHook(std::function<void()>());
            value->SetTestInput("(at 0 1) (hold 0) (plate 0) (sort 1 table) (size 1 big) (at 1 1)", "");
            value->Run();
            assert(value->objects.size() == 1);
        }
    } else if (test == 1) {
        value->SetEnvReadHook([] { throw std::runtime_error("ordinary failure"); });
        bool propagated = false;
        try { value->Plan(); } catch (const std::runtime_error& error) {
            propagated = std::string(error.what()) == "ordinary failure";
        }
        assert(propagated);
        value->Fini(); // the owner lock and active flag unwound on exception
    } else if (test == 7) {
        // Check the object representation without reading an uninitialized bool
        // in the before binary. Dirty storage makes the inherited defect visible.
        alignas(RDFW) unsigned char storage[sizeof(RDFW)];
        std::memset(storage, 0xa5, sizeof(storage));
        RDFW* fresh = new (storage) RDFW();
        unsigned char flag = 0;
        std::memcpy(&flag, &fresh->isMultiGotoMode, sizeof(flag));
        fresh->~RDFW();
        if (flag != 0) {
            std::cerr << "REGRESSION: multi-goto flag has no construction default\n";
            return 43;
        }
    } else if (test == 3) {
        for (int cycle = 0; cycle < 3; ++cycle) {
            value->SetTestInput("(at 0 1) (hold 0) (plate 0) (sort 1 table) (size 1 big) (at 1 1)", "");
            value->Run();
            assert(value->objects.size() == 1);
        }
    } else {
        return 2;
    }
    std::cout << "LIFECYCLE_PASS " << test << '\n';
}
