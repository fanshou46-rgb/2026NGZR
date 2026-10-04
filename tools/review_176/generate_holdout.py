"""Freeze structural holdouts before any planner execution; no score inputs."""
from pathlib import Path
import hashlib,json,random,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2]
DEST=ROOT/'题目/generalization_176_20261004'

def main():
    DEST.mkdir(exist_ok=False);rows=[]
    families=['two_parents','tray_two_parents','hidden_door_two_parents','other_tray_split_delivery']
    for fi,family in enumerate(families):
        for vi in range(2):
            rng=random.Random(17641004+101*fi+vi)
            names=['table','desk','cupboard','closet','human','cup','book','bottle','can']
            ids=list(range(1,10));rng.shuffle(ids);ident=dict(zip(names,ids))
            locs=list(range(1,6));rng.shuffle(locs);loc=dict(zip(names[:5],locs))
            if fi==0:loc['closet']=loc['cupboard']
            tray=ident['cup'] if fi==1 else ident['can'] if fi==3 else 0
            info=['(at 0 %d)'%loc['cupboard'],'(hold 0)','(plate %d)'%tray]
            for n in names:
                info+=['(sort %d %s)'%(ident[n],n),'(size %d %s)'%(ident[n],'small' if n in names[5:] else 'big')]
                if n in names[:5]:info+=['(at %d %d)'%(ident[n],loc[n])]
                if n in ['cupboard','closet']:info+=['(type %d container)'%ident[n],'(closed %d)'%ident[n]]
            info+=['(inside %d %d)'%(ident['cup'],ident[c]) for c in ['cupboard','closet']]
            # Explicit at and two inside edges coexist. These are legal SDK facts.
            if fi==3:info+=['(at %d %d)'%(ident['cup'],loc['cupboard'])]
            info+=['(at %d %d)'%(ident[n],loc['human']) for n in ['book','bottle','can']]
            tasks=[];nl=[]
            for c in ['cupboard','closet']:
                tasks+=['(:task (takeout X Y) (:cond (sort X cup) (sort Y %s)))'%c]
                nl+=['Take out the cup from the %s.'%c]
            tasks+=['(:task (puton X Y) (:cond (sort X cup) (sort Y table)))',
                    '(:task (puton X Y) (:cond (sort X book) (sort Y desk)))',
                    '(:task (give human X) (:cond (sort X bottle)))',
                    '(:task (goto X) (:cond (sort X table)))']
            nl+=['Put the cup on the table.','Put the book on the desk.','Give the bottle to the human.','Go to the table.']
            pairs=list(zip(tasks,nl));rng.shuffle(pairs);tasks,nl=map(list,zip(*pairs))
            plan=[];current=loc['cupboard']
            def move(destination):
                nonlocal current
                if current!=destination:plan.append(['Move',destination]);current=destination
            for c in ['cupboard','closet']:
                move(loc[c]);plan+=[['Open',ident[c]],['TakeOut',ident['cup'],ident[c]],['PutDown',ident['cup']]]
            # Cup now has an explicit at relation at the second container.
            if tray==ident['cup']:plan+=[['FromPlate',ident['cup']]]
            else:plan+=[['PickUp',ident['cup']]]
            move(loc['table']);plan+=[['PutDown',ident['cup']]]
            move(loc['human']);plan+=[['PickUp',ident['book']]]
            move(loc['desk']);plan+=[['PutDown',ident['book']]]
            move(loc['human']);plan+=[['PickUp',ident['bottle']],['PutDown',ident['bottle']]]
            move(loc['table'])
            xml=ET.Element('test');env=ET.SubElement(xml,'env',mis='on',err='on',ans='on')
            ET.SubElement(env,'info').text='\n'+'\n'.join(info)+'\n'
            missing=['(plate %d)'%tray] if tray else []
            if fi==2:missing+=['(closed %d)'%ident[c] for c in ['cupboard','closet']]
            ET.SubElement(env,'mis').text=' '.join(missing)
            error=ET.SubElement(env,'err');ET.SubElement(error,'r');ET.SubElement(error,'w');ET.SubElement(env,'extra')
            ET.SubElement(xml,'instr').text='(:ins '+' '.join(tasks)+')';ET.SubElement(xml,'nl').text=' '.join(nl)
            name='j%02d%s'%(fi+1,chr(97+vi));path=DEST/(name+'.xml')
            ET.ElementTree(xml).write(str(path),encoding='utf8',xml_declaration=True)
            rows.append(dict(id=name,path=path.name,family=family,stage=2,stress=True,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),reference_actions=plan,reference_goals=6,reference_constraints=0))
    (DEST/'catalogue.json').write_text(json.dumps(dict(design_seed=17641004,planner_seeds=[2026100401,2026100402],budget_ms=5000,cases=rows),ensure_ascii=False,indent=2),encoding='utf8')
    (DEST/'README.md').write_text('# 1.7.6 结构留出题\n\n8 题、4 族、每题 6 目标。生成器不读取规划器结果，参考路径只用于官方 SDK 可解性验证，不输入机器人。覆盖两个父容器、托盘与双父关系、未知柜门、显式地点与双父关系及另一物占托盘。ID、地点和任务顺序独立变换。首次运行后转为回归题；全部结果与失败原样报告。\n',encoding='utf8')
    (DEST/'.gitattributes').write_text('*.xml -text\n*.json -text\n',encoding='utf8')
if __name__=='__main__':main()
