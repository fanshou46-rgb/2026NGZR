#include "execution_evidence.hpp"
#include <cassert>
#include <functional>
using namespace _home;
static bool rejects(const std::function<void()>& f) {try{f();return false;}catch(const std::logic_error&){return true;}}
static ActionPermit known() {
    ActionPermit p;p.action="Open";p.arguments={5};p.state_signature="hold=0;at(5)=3;closed(5)=1";
    p.kind=PermitKind::CONFIRMED;p.cost=2;p.remaining_ms=4000;p.reserved_ms=200;return p;
}
int main() {
    ExecutionEvidence l(true);auto p=known();
    auto id=l.prepare(p);
    assert(rejects([&]{l.send(id,"hold=7;at(5)=3;closed(5)=1");}));
    assert(!l.receipt(id).sent);l.send(id,p.state_signature);
    assert(rejects([&]{l.send(id,p.state_signature);}));
    assert(rejects([&]{l.prepare(p);}));
    l.answer(id,ExecutionStatus::FAILED,"false");
    l.commit(id,"hold=0;at(5)=3;opened(5)=unknown");
    assert(l.receipt(id).outcome==ExecutionStatus::FAILED && l.receipt(id).state_committed);
    assert(rejects([&]{l.answer(id,ExecutionStatus::SUCCEEDED,"true");}));
    p.kind=PermitKind::LEGACY_UNQUALIFIED;
    assert(rejects([&]{l.prepare(p);}));
    p.kind=PermitKind::MODELED_PROBE;p.policy=42;
    assert(rejects([&]{l.prepare(p);}));
    p.branches_complete=true;id=l.prepare(p);l.send(id,p.state_signature);
    l.answer(id,ExecutionStatus::INDETERMINATE,"RPC threw after dispatch");
    l.commit(id,"door=unknown");
    assert(l.receipt(id).outcome==ExecutionStatus::INDETERMINATE);
    assert(rejects([&]{l.cancel(id);}));
    // Identical public execution is replayable, excluding real clock measurements.
    ExecutionEvidence a(true),b(true);p=known();
    for(auto* x:{&a,&b}) {id=x->prepare(p);x->send(id,p.state_signature);x->answer(id,ExecutionStatus::SUCCEEDED,"true");x->commit(id,"opened=1");}
    assert(a.receipt(1).digest==b.receipt(1).digest);
    p=known();ActionEvidenceRef ref;ref.predicate="hand";ref.confirmed=false;p.evidence.push_back(ref);
    assert(rejects([&]{a.prepare(p);}));
    assert(ExecutionEvidence::jsonString("a\"\\\nb") == "\"a\\\"\\\\\\nb\"");
}
