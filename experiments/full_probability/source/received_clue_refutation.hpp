#pragma once
#include "execution_evidence.hpp"
#include <algorithm>
#include <regex>
namespace _home {
struct ReceivedAtRefutation {
    std::size_t sense,query;int site;
    ReceivedAtRefutation(std::size_t sense_id=0,std::size_t query_id=0,int at_site=-1)
        :sense(sense_id),query(query_id),site(at_site){}
};
// SDK explicit AT implies visibility even when independent inside edges also
// exist. This proof uses actual raw Sense/Ask receipts, not finite posterior
// absence. Any intervening physical command conservatively invalidates it.
inline ReceivedAtRefutation receivedAtRefutation(const std::vector<ActionReceipt>& rows,unsigned object,int site) {
    if(site<0)return {};
    const ActionReceipt* sense=nullptr;const ActionReceipt* query=nullptr;
    for(auto it=rows.rbegin();it!=rows.rend();++it) {
        if(!sense && it->permit.action=="Sense")sense=&*it;
        if(!query && it->permit.action=="AskLoc" && it->permit.arguments==std::vector<unsigned>{object})query=&*it;
        if(sense && query)break;
    }
    if(!sense || !query || !sense->sent || !query->sent || !sense->state_committed || !query->state_committed ||
        sense->status!=ExecutionStatus::COMMITTED || query->status!=ExecutionStatus::COMMITTED ||
        sense->outcome!=ExecutionStatus::OBSERVED || query->outcome!=ExecutionStatus::OBSERVED)return {};
    if(query->public_feedback!="at("+std::to_string(object)+","+std::to_string(site)+")")return {};
    const auto first=std::min(sense->id,query->id);
    for(const auto& r:rows)if(r.id>first && r.sent && r.permit.action!="Sense" && r.permit.action!="AskLoc")return {};
    unsigned robot_refs=0;
    for(const auto& e:sense->permit.evidence)if(e.predicate=="robot_at" && e.object==0) {
        if(!e.confirmed || e.value!=site)return {};
        ++robot_refs;
    }
    if(robot_refs!=1 || !std::regex_match(sense->public_feedback,std::regex("\\[(?:[0-9]+(?:,[0-9]+)*)?\\]")))return {};
    const std::regex number("[0-9]+");
    for(std::sregex_iterator it(sense->public_feedback.begin(),sense->public_feedback.end(),number),end;it!=end;++it)
        if(std::stoul(it->str())==object)return {};
    return {sense->id,query->id,site};
}
}
