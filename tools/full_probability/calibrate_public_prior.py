"""Offline development-only calibration; author facts never enter robot input.

Reconstructs only SDK TestDesc's initial Grader/Plug atom lists. These are
initial-field labels, not labels for unexecuted action candidates. Freeze a
fresh independent bank after fitting; do not call this holdout evaluation.
"""
from pathlib import Path
import argparse,collections,hashlib,json,re,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2];LAB=ROOT/'experiments/full_probability'
ATOM=re.compile(r'\(([^()]*)\)')
def atoms(text):return [tuple(s.split()) for s in ATOM.findall(text or '')]
def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
    assert Path(a.output).name==a.output
    out=LAB/a.output;assert not out.exists(),'Calibration snapshot is immutable'
    bank=ROOT/'题目/independent_100_20261004'
    cat=json.loads((bank/'catalogue.json').read_text(encoding='utf8'))
    counts=collections.defaultdict(collections.Counter);cases=[]
    for row in cat['cases']:
        if row['stage']!=2 or row['kind']=='invalid':continue
        path=bank/row['path'];data=path.read_bytes();env=ET.fromstring(data).find('env')
        get=lambda name:env.findtext(name) or ''
        truth=set(atoms(get('info')+' '+get('mis')+' '+get('err/r')+' '+get('extra')))
        public=atoms(get('info')+' '+('' if env.get('mis')=='on' else get('mis'))+' '+
                     (get('err/w') if env.get('err')=='on' else get('err/r')))
        small={int(t[1]) for t in public if t[0]=='size' and t[2]=='small'}
        containers={int(t[1]) for t in public if t[0]=='type' and t[2]=='container'}
        per=collections.Counter();errors=0
        for t in public:
            if t[0] not in ('at','inside','hold','plate','opened','closed'):continue
            group='door' if t[0] in ('opened','closed') else t[0]
            if t[0]=='at':group='robot_at' if t[1]=='0' else 'small_at' if int(t[1]) in small else 'big_at'
            correct=t in truth;counts[group]['total']+=1;counts[group]['correct']+=correct
            per[group]+=1;errors+=not correct
        provided_at={int(t[1]) for t in public if t[0]=='at'}
        provided_inside={int(t[1]) for t in public if t[0]=='inside'}
        true_at={int(t[1]) for t in truth if t[0]=='at'}
        supplied_edges={(int(t[1]),int(t[2])) for t in public if t[0]=='inside'}
        true_edges={(int(t[1]),int(t[2])) for t in truth if t[0]=='inside'}
        for id in small:
            for parent in containers:
                if (id,parent) in supplied_edges:continue
                counts['absent_inside_edge']['total']+=1
                counts['absent_inside_edge']['correct']+=(id,parent) not in true_edges
        for id in small-provided_at:
            group='absent_at_with_inside' if id in provided_inside else 'absent_at_no_inside'
            counts[group]['total']+=1;counts[group]['correct']+=id not in true_at
        cases.append(dict(id=row['id'],sha256=hashlib.sha256(data).hexdigest(),fields=dict(per),erroneous_public_fields=errors))
    result=dict(scope='initial public-field calibration on already used development bank only; no candidate-feedback or holdout calibration',
        sdk_semantics='platform.cpp TestDesc getEnv4Grader/getEnv4Plug',
        sdk_source_sha256=hashlib.sha256(Path('/tmp/env-release-2026-search/src/platform.cpp').read_bytes()).hexdigest(),cases=cases,
        estimates={k:dict(v,laplace_probability=(v['correct']+1)/(v['total']+2)) for k,v in sorted(counts.items())})
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result['estimates'],ensure_ascii=False))
if __name__=='__main__':main()
