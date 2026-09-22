#pragma once

#include <string>
#include <vector>

namespace _home {

// Header-only platform stub used only by local unit/syntax tests.  Production
// builds put the competition SDK include directory before this test directory.
class Plug {
public:
    virtual ~Plug() {}
    void Run() { Plan(); Fini(); }

protected:
    explicit Plug(const std::string& name) : name_(name) {}
    virtual void Plan() = 0;
    virtual void Fini() {}

    const std::string& GetName() const { return name_; }
    const std::string& GetTestName() const { return empty_; }
    const std::string& GetEnvDes() const { return empty_; }
    const std::string& GetTaskDes() const { return empty_; }

    virtual bool Move(unsigned int) { return true; }
    virtual bool PickUp(unsigned int) { return true; }
    virtual bool PutDown(unsigned int) { return true; }
    virtual bool ToPlate(unsigned int) { return true; }
    virtual bool FromPlate(unsigned int) { return true; }
    virtual bool Open(unsigned int) { return true; }
    virtual bool Close(unsigned int) { return true; }
    virtual bool PutIn(unsigned int, unsigned int) { return true; }
    virtual bool TakeOut(unsigned int, unsigned int) { return true; }
    virtual std::string AskLoc(unsigned int) { return "not_known"; }
    virtual void Sense(std::vector<unsigned int>& values) { values.clear(); }

private:
    std::string name_;
    std::string empty_;
};

} // namespace _home
