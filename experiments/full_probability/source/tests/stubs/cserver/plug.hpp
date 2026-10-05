#pragma once

#include <string>
#include <vector>
#include <functional>
#include <stdexcept>

namespace _home {

// Header-only platform stub used only by local unit/syntax tests.  Production
// builds put the competition SDK include directory before this test directory.
class Plug {
public:
    virtual ~Plug() {}
    void Run() { Plan(); Fini(); }
    void SetTestInput(const std::string& env, const std::string& task) {
        env_ = env;
        task_ = task;
        platform_calls_ = 0;
    }
    unsigned int TestPlatformCalls() const { return platform_calls_; }
    void SetSenseResult(const std::vector<unsigned int>& values) { sense_result_ = values; }
    void SetSenseCallback(const std::function<void(std::vector<unsigned int>&)>& callback) {sense_callback_=callback;}
    void SetAskCallback(const std::function<std::string(unsigned)>& callback) {ask_callback_=callback;}
    void SetAskResult(const std::string& value) { ask_result_ = value; }
    void SetActionCallback(const std::function<void()>& callback) { action_callback_ = callback; }
    void SetThrowAction(bool value) { throw_action_ = value; }
    void SetThrowSense(bool value) { throw_sense_ = value; }
    void SetActionResults(const std::vector<bool>& results) {
        action_results_ = results;
        action_result_cursor_ = 0;
    }

protected:
    explicit Plug(const std::string& name) : name_(name) {}
    virtual void Plan() = 0;
    virtual void Fini() {}

    const std::string& GetName() const { return name_; }
    const std::string& GetTestName() const { return empty_; }
    const std::string& GetEnvDes() const { return env_; }
    const std::string& GetTaskDes() const { return task_; }

    virtual bool Move(unsigned int) { return NextActionResult(); }
    virtual bool PickUp(unsigned int) { return NextActionResult(); }
    virtual bool PutDown(unsigned int) { return NextActionResult(); }
    virtual bool ToPlate(unsigned int) { return NextActionResult(); }
    virtual bool FromPlate(unsigned int) { return NextActionResult(); }
    virtual bool Open(unsigned int) { return NextActionResult(); }
    virtual bool Close(unsigned int) { return NextActionResult(); }
    virtual bool PutIn(unsigned int, unsigned int) { return NextActionResult(); }
    virtual bool TakeOut(unsigned int, unsigned int) { return NextActionResult(); }
    virtual std::string AskLoc(unsigned int id) { ++platform_calls_; return ask_callback_?ask_callback_(id):ask_result_; }
    virtual void Sense(std::vector<unsigned int>& values) {
        ++platform_calls_; if (throw_sense_) throw std::runtime_error("sense fixture exception");
        if(sense_callback_)sense_callback_(values);else values = sense_result_;
    }

private:
    bool NextActionResult() {
        ++platform_calls_;
        if (throw_action_) throw std::runtime_error("action fixture exception");
        if (action_callback_) action_callback_();
        return action_result_cursor_ < action_results_.size() ?
            action_results_[action_result_cursor_++] : true;
    }
    std::string name_;
    std::string empty_;
    std::string env_, task_;
    unsigned int platform_calls_ = 0;
    std::vector<bool> action_results_;
    std::size_t action_result_cursor_ = 0;
    std::vector<unsigned int> sense_result_;
    std::function<void(std::vector<unsigned int>&)> sense_callback_;
    std::function<std::string(unsigned)> ask_callback_;
    std::string ask_result_ = "not_known";
    std::function<void()> action_callback_;
    bool throw_action_ = false, throw_sense_ = false;
};

} // namespace _home
