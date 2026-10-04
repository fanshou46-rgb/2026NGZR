"""Freeze original sources and make an explicitly experimental clone."""
from common import *
import shutil, subprocess

HEADER = r'''#pragma once
#include <cstdlib>
#include <cstring>
namespace _home {
inline int AuditAblation() {
 static const int mode=[](){const char* s=std::getenv("RDFW_AUDIT_ABLATION");
  if(!s || !std::strcmp(s,"default"))return 0;
  if(!std::strcmp(s,"neutral"))return 1;
  if(!std::strcmp(s,"no_ask"))return 2;
  if(!std::strcmp(s,"legacy_visibility"))return 3;
  std::abort();}();return mode;
}
}
'''

def main():
    OUT.mkdir(parents=True,exist_ok=False)
    assert subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip()=='68fe263b096e0d3075da4c358fe9560a98ebf359'
    save(OUT/'original-source-hashes.json',{k:core(p) for k,p in SOURCES.items()})
    dest=OUT/'experiment/source';dest.mkdir(parents=True)
    for p in SOURCES['177'].iterdir():
        if p.suffix in ('.cpp','.hpp','.h') or p.name in ('words.txt','CMakeLists.txt'):shutil.copy2(p,dest/p.name)
    shutil.copytree(SOURCES['177']/'tests',dest/'tests',ignore=shutil.ignore_patterns('__pycache__'))
    (dest/'audit_ablation.hpp').write_text(HEADER,encoding='utf8')
    def edit(name,old,new):
        p=dest/name;s=p.read_text(encoding='utf8');assert s.count(old)==1,(name,old[:50]);p.write_text(s.replace(old,new),encoding='utf8')
    for name in ('belief_state.cpp','observation_model.cpp','visibility_forecast.cpp'):
        p=dest/name;p.write_text('#include "audit_ablation.hpp"\n'+p.read_text(encoding='utf8'),encoding='utf8')
    edit('belief_state.cpp',"if (hint.first!='?') {", "if (AuditAblation()!=1 && hint.first!='?') {")
    edit('belief_state.cpp','LocationBelief next=*this;','LocationBelief next=*this;\n    if(AuditAblation()==1 || AuditAblation()==2)return next;')
    # Preserve support expansion/event deduplication and every hard observation.
    # Uniformization in neutral applies to live positive alternatives, never revives hard exclusions.
    edit('belief_state.cpp','weights=posterior(observation,supported).weights;', '''if(AuditAblation()==1) {for(auto& v:weights)if(v.second>0)v.second=1;normalize();}
    else if(AuditAblation()!=2) weights=posterior(observation,supported).weights;''')
    edit('observation_model.cpp','double AskObservationModel::likelihood(LocationHypothesis reply,LocationHypothesis world) const {', '''double AskObservationModel::likelihood(LocationHypothesis reply,LocationHypothesis world) const {
    if(AuditAblation()==1 || AuditAblation()==2) {
        if(reply.first=='?')return unknown_mass;
        auto found=random_replies.find(reply);
        return found==random_replies.end()?0:(1-unknown_mass)*found->second;
    }''')
    edit('visibility_forecast.cpp','// The legacy distribution supplies reference hypotheses, not exclusive', '''if(AuditAblation()==1) {
        ProbabilityBounds b;b.lower=b.upper=.5;b.residual=0;
        bool definitely_visible=false,all_parents_known_invisible=true;
        const auto& evidence=Provenance(StateField::INSIDE,id);
        for(const auto& e:evidence.inside_edges) if(InsideRelation(id,e.first)==1) {
            const int loc=FactLocation(e.first),door=FactContainerState(e.first);
            if(loc==target && (e.first==int(opened) || door==1))definitely_visible=true;
            if(loc==UNKNOWN || (loc==target && (e.first==int(opened) || door!=0)))all_parents_known_invisible=false;
        }
        if(definitely_visible)b.lower=b.upper=1;
        else if(at!=UNKNOWN && evidence.inside_complete && all_parents_known_invisible &&
                FactValue(StateField::HOLD)!=UNKNOWN && FactValue(StateField::PLATE)!=UNKNOWN) b.lower=b.upper=0;
        return b;
    }
    if(AuditAblation()==3) {
        double probability=0;
        for(const auto& h:BeliefFor(id).distribution()) {
            if(h.first.first=='a' && h.first.second==target && !IsAbsentFromSensedLocation(id,target))probability+=h.second;
            if(h.first.first=='i' && (opened || FactContainerState(h.first.second)==1) &&
                FactLocation(h.first.second)==target)probability+=h.second;
        }
        ProbabilityBounds b;b.lower=b.upper=std::min(1.0,probability);b.residual=0;return b;
    }
    // The legacy distribution supplies reference hypotheses, not exclusive''')
    save(OUT/'experiment/diff-receipt.json',dict(original=core(SOURCES['177']),experiment=core(dest),
        modes={'default':'unaltered numerical path','neutral':'equal live hypotheses, answer-independent likelihood, unknown visibility 0.5',
               'no_ask':'answer-independent likelihood and no numerical answer posterior; support retained',
               'legacy_visibility':'single-object categorical visibility scalar without joint/residual forecast'},
        forbidden_changes='No fact mutation, physical feedback, task/candidate generation, constraint checks, terminal loss or deadline edits'))
    print('PREPARED',OUT,flush=True)
if __name__=='__main__':main()
