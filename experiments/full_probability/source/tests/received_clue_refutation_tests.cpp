#include "received_clue_refutation.hpp"
#include <cassert>
#include <iostream>
using namespace _home;
int main() {
    ActionReceipt sense;sense.id=1;sense.permit.action="Sense";sense.sent=true;sense.state_committed=true;
    sense.outcome=ExecutionStatus::OBSERVED;sense.status=ExecutionStatus::COMMITTED;sense.public_feedback="[1,2]";
    ActionEvidenceRef robot;robot.predicate="robot_at";robot.object=0;robot.value=1;robot.confirmed=true;
    sense.permit.evidence={robot};
    ActionReceipt query=sense;query.id=2;query.permit.action="AskLoc";query.permit.arguments={3};query.public_feedback="at(3,1)";
    std::vector<ActionReceipt> receipts={sense,query};
    const auto proof=receivedAtRefutation(receipts,3,1);assert(proof.sense==1 && proof.query==2 && proof.site==1);
    auto rejected=[&](std::vector<ActionReceipt> rows){assert(!receivedAtRefutation(rows,3,1).sense);};
    auto rows=receipts;rows[0].public_feedback="[1,2,3]";rejected(rows);
    rows=receipts;rows[0].permit.evidence[0].confirmed=false;rejected(rows);
    rows=receipts;rows[0].permit.evidence[0].value=2;rejected(rows);
    rows=receipts;rows[1].public_feedback="inside(3,2)";rejected(rows);
    rows=receipts;rows[1].state_committed=false;rejected(rows);
    rows=receipts;rows[0].sent=false;rejected(rows);
    rows=receipts;rows[0].status=ExecutionStatus::CANCELLED;rejected(rows);
    rows=receipts;rows[0].public_feedback="[bad]";rejected(rows);
    rows=receipts;auto physical=query;physical.id=3;physical.permit.action="Move";physical.outcome=ExecutionStatus::FAILED;
    rows.push_back(physical);rejected(rows); // even false physical commands conservatively invalidate
    rows=receipts;auto later=sense;later.id=3;later.public_feedback="[3]";rows.push_back(later);rejected(rows);
    rows=receipts;auto other=query;other.id=3;other.permit.arguments={4};other.public_feedback="at(4,1)";rows.push_back(other);
    assert(receivedAtRefutation(rows,3,1).sense==1);
    rows=receipts;later=sense;later.id=3;rows.push_back(later);assert(receivedAtRefutation(rows,3,1).sense==3);
    rows=receipts;other=query;other.id=3;other.public_feedback="not_known";rows.push_back(other);rejected(rows);
    assert(!receivedAtRefutation(receipts,3,9).sense && !receivedAtRefutation(receipts,4,1).sense);
    std::cout<<"actual receipt AT refutation; visible IDs, pose provenance, committed observation, latest frames and intervening action counterexamples passed\n";
}
