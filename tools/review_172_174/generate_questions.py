"""New, frozen semantic/generalization questions; never read planner results."""
from pathlib import Path
import hashlib, json, random, re, xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / '题目' / 'generalization_20261004'
FAMILIES = [
    'known_delivery', 'missing_floor', 'wrong_floor', 'hidden_closed',
    'wrong_container', 'occupied_tray', 'occupied_hand', 'closed_constraint',
    'colocated_containers', 'independent_at_inside', 'shared_sort', 'terminal_conflict']

def main():
    DEST.mkdir(parents=True, exist_ok=False)
    rows=[]
    for family_index,family in enumerate(FAMILIES):
        for variant in range(2):
            rng=random.Random(714203+family_index*13+variant)
            ids=list(range(1,11)); rng.shuffle(ids)
            names=['human','table','desk','cupboard','refrigerator','couch','cup','book','bottle','can']
            ident=dict(zip(names,ids))
            locs=list(range(1,7)); rng.shuffle(locs)
            loc=dict(zip(names[:6],locs))
            colors={'cup':'blue','book':'red','bottle':'green','can':'white'}
            kinds={n:n for n in names}
            if family=='shared_sort': kinds['book']='cup'; kinds['bottle']='cup'
            if family=='colocated_containers': loc['refrigerator']=loc['cupboard']
            start=loc['desk']; hand=0; tray=0
            where={'cup':('at',loc['couch']),'book':('at',loc['desk']),
                   'bottle':('at',loc['human']),'can':('at',loc['table'])}
            opened={'cupboard':False,'refrigerator':False}
            if family in ('hidden_closed','wrong_container','closed_constraint','independent_at_inside'):
                where['cup']=('inside',ident['cupboard'])
            if family=='closed_constraint':
                where['book']=('inside',ident['cupboard']);where['bottle']=('inside',ident['cupboard'])
            if family=='colocated_containers':
                opened={'cupboard':True,'refrigerator':True}
                where['cup']=('inside',ident['cupboard']);where['book']=('inside',ident['refrigerator'])
            if family=='occupied_tray': tray=ident['cup'];where['cup']=('at',start)
            if family=='occupied_hand': hand=ident['book'];where['book']=('at',start)
            info=[f'(hold {hand}) (plate {tray}) (at 0 {start})']
            for name in names:
                n=ident[name]; small=name in colors
                info.append(f'(sort {n} {kinds[name]}) (size {n} {"small" if small else "big"})')
                if small: info.append(f'(color {n} {colors[name]})')
                else: info.append(f'(at {n} {loc[name]})')
                if name in opened: info.append(f'(type {n} container) ({"opened" if opened[name] else "closed"} {n})')
            missing=[]; correct=[]; wrong=[]
            for name,(relation,value) in where.items():
                n=ident[name];atom=f'({relation} {n} {value})'
                if family in ('missing_floor','hidden_closed','colocated_containers') and name in ('cup','book'):
                    missing.append(atom)
                elif family=='wrong_floor' and name=='cup':
                    correct.append(atom);wrong.append(f'(at {n} {loc["desk"]})')
                elif family=='wrong_container' and name=='cup':
                    correct.append(atom);wrong.append(f'(inside {n} {ident["refrigerator"]})')
                else: info.append(atom)
            if family=='independent_at_inside': info.append(f'(at {ident["cup"]} {loc["cupboard"]})')
            instructions=[];nl=[]
            def task(action,name,target=None):
                cond=f'(sort X {kinds[name]})'+(f' (color X {colors[name]})' if name in colors else '')
                if target:cond+=f' (sort Y {kinds[target]})'
                instructions.append(f'(:task ({action} X'+(' Y' if target else '')+f') (:cond {cond}))')
                noun=(colors[name]+' ' if name in colors else '')+kinds[name]
                if action=='puton':nl.append(f'Put the {noun} on the {kinds[target]}.')
                elif action=='goto':nl.append(f'Go to the {noun}.')
                elif action=='takeout':nl.append(f'Take out the {noun} from the {kinds[target]}.')
                elif action=='pickup':nl.append(f'Pick up the {noun}.')
            for name in ('cup','book','bottle'):task('puton',name,'table')
            task('goto','table')
            if family=='independent_at_inside':task('takeout','cup','cupboard')
            if family=='terminal_conflict':task('pickup','cup')
            if family=='closed_constraint':
                instructions.insert(0,'(:cons_notnot (:info (closed X) (:cond (sort X cupboard))))')
                nl.insert(0,'The cupboard must be closed.')
            # Reference plan knows the truth only to verify question validity.
            # This data is never supplied to the competing planners.
            plan=[];robot=start;is_open=dict(opened)
            def move(destination):
                nonlocal robot
                if robot!=destination:plan.append(['Move',destination]);robot=destination
            order=['book','cup','bottle'] if hand else ['cup','book','bottle']
            for name in order:
                n=ident[name];relation,value=where[name]
                if n==hand:hand=0
                elif n==tray:plan.append(['FromPlate',n]);tray=0
                elif relation=='inside':
                    container=next(k for k,v in ident.items() if v==value)
                    move(loc[container])
                    if not is_open[container]:plan.append(['Open',value]);is_open[container]=True
                    plan.append(['TakeOut',n,value])
                else:move(value);plan.append(['PickUp',n])
                move(loc['table']);plan.append(['PutDown',n])
            paired=list(zip(instructions,nl));rng.shuffle(paired)
            instructions,nl=zip(*paired)
            stage=1 if family=='known_delivery' else 2
            root=ET.Element('test');env=ET.SubElement(root,'env',mis='on' if stage==2 else 'off',err='on' if stage==2 else 'off',ans='on' if stage==2 else 'off')
            ET.SubElement(env,'info').text='\n'+'\n'.join(info)+'\n'
            ET.SubElement(env,'mis').text=' '.join(missing)
            err=ET.SubElement(env,'err');ET.SubElement(err,'r').text=' '.join(correct);ET.SubElement(err,'w').text=' '.join(wrong)
            ET.SubElement(env,'extra')
            ET.SubElement(root,'instr').text='(:ins\n'+'\n'.join(instructions)+'\n)'
            ET.SubElement(root,'nl').text='\n'.join(nl)
            case_id=f'g{family_index+1:02d}{"ab"[variant]}'
            path=DEST/(case_id+'.xml');ET.ElementTree(root).write(path,encoding='utf-8',xml_declaration=True)
            goals=5 if family=='independent_at_inside' else 4
            row=dict(id=case_id,family=family,variant=variant,stage=stage,
                     split='structural_holdout' if family_index>=8 else 'development_audit',
                     stress=family in ('colocated_containers','independent_at_inside'),
                     path=path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                     reference_actions=plan,reference_goals=goals,reference_constraints=0,
                     requested_goals=sum(s.startswith('(:task') for s in instructions),
                     reference_optimality='feasible witness only; not an optimality oracle')
            rows.append(row)
    catalogue=dict(design_seed=714203,planner_seeds=[2026100401,2026100402],
                   policy='Freeze before any planner run. No parameter/code changes after exposure. All runs retained.',
                   cases=rows)
    (DEST/'catalogue.json').write_text(json.dumps(catalogue,ensure_ascii=False,indent=2),encoding='utf8')
    print('Frozen',len(rows),'cases at',DEST)

if __name__=='__main__':main()
