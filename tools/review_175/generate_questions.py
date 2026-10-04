"""Freeze larger questions without reading any planner results."""
from pathlib import Path
import hashlib, json, random, xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2]
DEST=ROOT/'题目'/'generalization_175_20261004_v4'
def main():
 DEST.mkdir(parents=True,exist_ok=False);rows=[]
 families=['scaled_closed','colocated_three','retained_tray','mixed_destinations']
 for fi,family in enumerate(families):
  for variant in range(3):
   rng=random.Random(17541004+fi*101+variant);ids=list(range(1,12));rng.shuffle(ids)
   names=['table','desk','cupboard','refrigerator','closet','couch','human','cup','book','bottle','can']
   ident=dict(zip(names,ids));ls=list(range(1,8));rng.shuffle(ls);loc=dict(zip(names[:7],ls))
   if family=='colocated_three':
    loc['refrigerator']=loc['cupboard'];loc['closet']=loc['cupboard']
   sources=['cup','book','bottle','can'];containers=['cupboard','refrigerator','closet']
   colors=dict(zip(sources,['blue','red','green','white']))
   opened={c:family=='colocated_three' and c!='refrigerator' for c in containers}
   where={n:('inside',ident[containers[i%2]]) for i,n in enumerate(sources)}
   if family=='colocated_three':where={n:('inside',ident[containers[i%3]]) for i,n in enumerate(sources)}
   if family=='retained_tray':
    where={n:('at',loc['couch'] if i%2 else loc['human']) for i,n in enumerate(sources)};where['cup']=('inside',ident['cupboard'])
   if family=='mixed_destinations':where['can']=('at',loc['human'])
   robot=loc['desk'];tray=ident['cup'] if family=='retained_tray' else 0
   info=[f'(at 0 {robot})','(hold 0)',f'(plate {tray})']
   for n in names:
    small=n in sources;info += [f'(sort {ident[n]} {n})',f'(size {ident[n]} '+('small)' if small else 'big)')]
    if small:
     info += [f'(color {ident[n]} {colors[n]})',f'({where[n][0]} {ident[n]} {where[n][1]})']
    else:info.append(f'(at {ident[n]} {loc[n]})')
    if n in containers:info += [f'(type {ident[n]} container)',f'('+('opened' if opened[n] else 'closed')+f' {ident[n]})']
   target={n:('desk' if family=='mixed_destinations' and i%2 else 'table') for i,n in enumerate(sources)}
   ins=[];nl=[]
   for n in sources:
    ins.append(f'(:task (puton X Y) (:cond (sort X {n}) (color X {colors[n]}) (sort Y {target[n]})))')
    nl.append(f'Put the {colors[n]} {n} on the {target[n]}.')
   ins += ['(:task (takeout X Y) (:cond (sort X cup) (color X blue) (sort Y cupboard)))','(:task (goto X) (:cond (sort X table)))']
   nl += ['Take out the blue cup from the cupboard.','Go to the table.']
   # Six goals with different route length, shared containers, and slot coupling.
   pairs=list(zip(ins,nl));rng.shuffle(pairs);ins,nl=map(list,zip(*pairs))
   plan=[];current=robot;doors=dict(opened)
   def move(dest):
    nonlocal current
    if current!=dest:plan.append(['Move',dest]);current=dest
   for n in sources:
    rel,val=where[n];a=ident[n]
    if rel=='inside':
     c=next(c for c in containers if ident[c]==val);move(loc[c])
     if not doors[c]:plan.append(['Open',val]);doors[c]=True
     plan.append(['TakeOut',a,val])
    else:move(val);plan.append(['PickUp',a])
    move(loc[target[n]]);plan.append(['PutDown',a])
    if tray==a:plan += [['FromPlate',a],['PutDown',a]];tray=0
   move(loc['table'])
   xml=ET.Element('test');env=ET.SubElement(xml,'env',mis='on',err='on',ans='on')
   ET.SubElement(env,'info').text='\n'+'\n'.join(info)+'\n'
   missing=[]
   if family=='retained_tray':missing=[f'(plate {ident["cup"]})']
   else:
    for n in ('book','bottle'):missing.append(f'({where[n][0]} {ident[n]} {where[n][1]})')
   ET.SubElement(env,'mis').text=' '.join(missing)
   err=ET.SubElement(env,'err');ET.SubElement(err,'r');ET.SubElement(err,'w');ET.SubElement(env,'extra')
   ET.SubElement(xml,'instr').text='(:ins '+' '.join(ins)+')';ET.SubElement(xml,'nl').text=' '.join(nl)
   name='h%02d%s'%(fi+1,chr(97+variant));path=DEST/(name+'.xml');ET.ElementTree(xml).write(str(path),encoding='utf-8',xml_declaration=True)
   rows.append(dict(id=name,family=family,split='new_frozen_evaluation',stress=family=='retained_tray',stage=2,path=path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),reference_actions=plan,reference_goals=6,reference_constraints=0))
 (DEST/'catalogue.json').write_text(json.dumps(dict(design_seed=17541004,planner_seeds=[2026100401,2026100402],budget_ms=5000,cases=rows),ensure_ascii=False,indent=2),encoding='utf8')
 (DEST/'README.md').write_text('# 1.7.5 独立扩展题\n\n12 题，每题 6 个目标。生成器不读取规划器结果；覆盖更长路线、三个容器同地、同物体柜内与托盘并存、不同目的地。每题保留 SDK 可行参考路径，规划器不会收到该路径。冻结后全部报告，不按得分筛题；与旧题分别统计。首次评估后这些题应作为回归题，下一轮需要另建留出集。\n\n新旧题统一 5 秒官方预算，按套题分别统计。新题另含重叠的取出与送达目标，考查真实终态而非执行标记。\n',encoding='utf8')
if __name__=='__main__':main()
