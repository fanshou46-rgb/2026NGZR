#pragma once
#include <cstdint>
#include <stdexcept>
#include <string>
#include <vector>

namespace _home {
struct ActionEvidenceRef {
    std::string predicate, source;
    unsigned object=0;
    int value=-1;
    std::size_t revision=0, event=0;
    bool confirmed=false;
};
enum class PermitKind { CONFIRMED, MODELED_PROBE, LEGACY_UNQUALIFIED };
enum class ExecutionStatus { PREPARED, SENT, SUCCEEDED, FAILED, OBSERVED,
                             INDETERMINATE, COMMITTED, CANCELLED };
struct ActionPermit {
    std::string action, state_signature, selection_reason;
    std::vector<unsigned> arguments;
    std::vector<ActionEvidenceRef> evidence;
    PermitKind kind=PermitKind::LEGACY_UNQUALIFIED;
    std::size_t policy=0, public_revision=0;
    int cost=0;
    long long remaining_ms=0, reserved_ms=0;
    // A probe permit references an observation-complete policy, not just p>0.
    bool branches_complete=false;
};
struct ActionReceipt {
    std::size_t id=0;
    ActionPermit permit;
    ExecutionStatus status=ExecutionStatus::PREPARED;
    ExecutionStatus outcome=ExecutionStatus::PREPARED;
    std::string public_feedback, state_after;
    std::uint64_t parent_digest=0, digest=0;
    bool sent=false, state_committed=false;
    long long sdk_ns=-1;
};

class ExecutionEvidence {
public:
    explicit ExecutionEvidence(bool enforce=false):enforce_(enforce) {}
    void reset(bool enforce=false);
    std::size_t prepare(const ActionPermit& permit);
    void send(std::size_t id,const std::string& current_signature);
    void answer(std::size_t id,ExecutionStatus outcome,const std::string& raw);
    void duration(std::size_t id,long long sdk_ns);
    void commit(std::size_t id,const std::string& state_after);
    void cancel(std::size_t id);
    const std::vector<ActionReceipt>& receipts() const {return rows_;}
    const ActionReceipt& receipt(std::size_t id) const;
    bool enforcing() const {return enforce_;}
    static std::uint64_t digest(const std::string& value);
    static std::string jsonString(const std::string& value);
    static std::string json(const ActionReceipt& receipt,const char* event);
private:
    bool enforce_;
    std::vector<ActionReceipt> rows_;
    ActionReceipt& writable(std::size_t id);
};
}
