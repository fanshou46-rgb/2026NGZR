#include "execution_evidence.hpp"
#include <sstream>
using namespace _home;
namespace {
const char* statusName(ExecutionStatus s) {
    switch(s) {
    case ExecutionStatus::PREPARED:return "prepared";
    case ExecutionStatus::SENT:return "sent";
    case ExecutionStatus::SUCCEEDED:return "succeeded";
    case ExecutionStatus::FAILED:return "failed";
    case ExecutionStatus::OBSERVED:return "observed";
    case ExecutionStatus::INDETERMINATE:return "indeterminate";
    case ExecutionStatus::COMMITTED:return "committed";
    case ExecutionStatus::CANCELLED:return "cancelled";
    }
    return "invalid";
}
const char* permitName(PermitKind p) {
    return p==PermitKind::CONFIRMED?"confirmed":p==PermitKind::MODELED_PROBE?"modeled_probe":"legacy_unqualified";
}
}
void ExecutionEvidence::reset(bool enforce) {rows_.clear();rows_.reserve(256);enforce_=enforce;}
ActionReceipt& ExecutionEvidence::writable(std::size_t id) {
    if(!id || id>rows_.size())throw std::logic_error("missing action receipt");
    return rows_[id-1];
}
const ActionReceipt& ExecutionEvidence::receipt(std::size_t id) const {
    if(!id || id>rows_.size())throw std::logic_error("missing action receipt");
    return rows_[id-1];
}
std::uint64_t ExecutionEvidence::digest(const std::string& s) {
    // Deterministic trace identifier; archive SHA256 provides cryptographic integrity.
    std::uint64_t h=14695981039346656037ULL;
    for(unsigned char c:s){h^=c;h*=1099511628211ULL;}return h;
}
std::size_t ExecutionEvidence::prepare(const ActionPermit& permit) {
    if(permit.action.empty() || permit.state_signature.empty() || permit.cost<0 ||
       permit.remaining_ms<=permit.reserved_ms)throw std::logic_error("invalid action permit");
    if(enforce_ && permit.kind==PermitKind::LEGACY_UNQUALIFIED)
        throw std::logic_error("unknown preconditions require modeled probe permit");
    if(permit.kind==PermitKind::MODELED_PROBE && (!permit.policy || !permit.branches_complete))
        throw std::logic_error("probe has no complete observation policy");
    if(permit.kind==PermitKind::CONFIRMED)
        for(const auto& ref:permit.evidence)if(!ref.confirmed)
            throw std::logic_error("unconfirmed evidence in deterministic permit");
    if(!rows_.empty() && rows_.back().status!=ExecutionStatus::COMMITTED &&
       rows_.back().status!=ExecutionStatus::CANCELLED)
        throw std::logic_error("prior action outcome not committed");
    ActionReceipt r;r.id=rows_.size()+1;r.permit=permit;
    r.parent_digest=rows_.empty()?0:rows_.back().digest;
    rows_.push_back(r);return r.id;
}
void ExecutionEvidence::send(std::size_t id,const std::string& current) {
    auto& r=writable(id);
    if(r.status!=ExecutionStatus::PREPARED || r.sent)throw std::logic_error("action can only be sent once");
    if(current!=r.permit.state_signature)throw std::logic_error("action evidence changed before dispatch");
    r.status=ExecutionStatus::SENT;r.sent=true;
}
void ExecutionEvidence::duration(std::size_t id,long long ns) {
    auto& r=writable(id);
    if(r.status!=ExecutionStatus::SENT || ns<0 || r.sdk_ns>=0)throw std::logic_error("invalid SDK call duration");
    r.sdk_ns=ns;
}
void ExecutionEvidence::answer(std::size_t id,ExecutionStatus result,const std::string& raw) {
    auto& r=writable(id);
    if(r.status!=ExecutionStatus::SENT)throw std::logic_error("response has no unique sent action");
    if(result!=ExecutionStatus::SUCCEEDED && result!=ExecutionStatus::FAILED &&
       result!=ExecutionStatus::OBSERVED && result!=ExecutionStatus::INDETERMINATE)
        throw std::logic_error("invalid external outcome");
    r.outcome=result;r.status=result;r.public_feedback=raw;
}
void ExecutionEvidence::commit(std::size_t id,const std::string& after) {
    auto& r=writable(id);
    if(r.status!=ExecutionStatus::SUCCEEDED && r.status!=ExecutionStatus::FAILED &&
       r.status!=ExecutionStatus::OBSERVED && r.status!=ExecutionStatus::INDETERMINATE)
        throw std::logic_error("commit requires actual public outcome");
    r.state_after=after;r.state_committed=true;r.status=ExecutionStatus::COMMITTED;
    r.digest=digest(std::to_string(r.parent_digest)+json(r,"committed"));
}
void ExecutionEvidence::cancel(std::size_t id) {
    auto& r=writable(id);
    if(r.sent || r.status!=ExecutionStatus::PREPARED)throw std::logic_error("sent command cannot be cancelled as unsent");
    r.status=ExecutionStatus::CANCELLED;
    r.digest=digest(std::to_string(r.parent_digest)+json(r,"cancelled"));
}
std::string ExecutionEvidence::jsonString(const std::string& value) {
    std::ostringstream s;s<<'"';
    for(unsigned char c:value) {
        if(c=='"')s<<"\\\"";else if(c=='\\')s<<"\\\\";
        else if(c=='\n')s<<"\\n";else if(c=='\r')s<<"\\r";else if(c=='\t')s<<"\\t";
        else if(c<32){const char* h="0123456789abcdef";s<<"\\u00"<<h[c>>4]<<h[c&15];}
        else s<<char(c);
    }
    s<<'"';return s.str();
}
std::string ExecutionEvidence::json(const ActionReceipt& r,const char* event) {
    std::ostringstream s;s<<"{\"schema\":\"execution_evidence.v1\",\"event\":"<<jsonString(event)
        <<",\"id\":"<<r.id<<",\"action\":"<<jsonString(r.permit.action)<<",\"args\":[";
    for(std::size_t i=0;i<r.permit.arguments.size();++i){if(i)s<<',';s<<r.permit.arguments[i];}
    s<<"],\"permit\":"<<jsonString(permitName(r.permit.kind))<<",\"status\":"<<jsonString(statusName(r.status))
        <<",\"outcome\":"<<jsonString(statusName(r.outcome))<<",\"policy\":"<<r.permit.policy
        <<",\"revision\":"<<r.permit.public_revision<<",\"before\":"<<digest(r.permit.state_signature)
        <<",\"after\":"<<digest(r.state_after)<<",\"cost\":"<<r.permit.cost<<",\"remaining_ms\":"<<r.permit.remaining_ms
        <<",\"reserved_ms\":"<<r.permit.reserved_ms<<",\"sdk_ns\":"<<r.sdk_ns<<",\"reason\":"<<jsonString(r.permit.selection_reason)
        <<",\"feedback\":"<<jsonString(r.public_feedback)<<",\"parent_digest\":"<<r.parent_digest<<",\"digest\":"<<r.digest
        <<",\"evidence\":[";
    for(std::size_t i=0;i<r.permit.evidence.size();++i) {
        if(i)s<<',';const auto& e=r.permit.evidence[i];
        s<<"{\"predicate\":"<<jsonString(e.predicate)<<",\"object\":"<<e.object<<",\"value\":"<<e.value
            <<",\"source\":"<<jsonString(e.source)<<",\"revision\":"<<e.revision<<",\"event\":"<<e.event
            <<",\"confirmed\":"<<(e.confirmed?"true":"false")<<'}';
    }
    s<<"]}";return s.str();
}
