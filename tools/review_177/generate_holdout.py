"""Independent structured questions; no planner scores or traces are read."""
from pathlib import Path
import hashlib,json,random,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2];DEST=ROOT/'题目/generalization_177_20261004'
def main():
    DEST.mkdir(exist_ok=False);rows=[]
    families=['explicit_at_with_remote_closed_parent','two_deliveries_sharing_parent',
              'two_parents_after_slot_transfer','same_object_both_slots']
    for fi,family in enumerate(families):
        for vi in range(2):
            rng=random.Random(17741004+fi*101+vi)
            names=['table','desk','cupboard','closet','human','cup','book','bottle','can']
            nums=list(range(1,10));rng.shuffle(nums);ids=dict(zip(names,nums))
            spots=list(range(1,6));rng.shuffle(spots);loc=dict(zip(names[:5],spots))
            hand=ids['cup'] if fi==3 else 0;tray=ids['cup'] if fi>=2 else 0
            info=['(at 0 %d)'%loc['cupboard'],'(hold %d)'%hand,'(plate %d)'%tray]
            for n in names:
                info+=['(sort %d %s)'%(ids[n],n),'(size %d %s)'%(ids[n],'small' if n in names[5:] else 'big')]
                if n in names[:5]:info+=['(at %d %d)'%(ids[n],loc[n])]
                if n in ('cupboard','closet'):info+=['(type %d container)'%ids[n],'(closed %d)'%ids[n]]
            info+=['(at %d %d)'%(ids[n],loc['desk'] if n=='book' else loc['human']) for n in names[5:]]
            info+=['(inside %d %d)'%(ids['cup'],ids['cupboard'])]
            if fi==1:info+=['(inside %d %d)'%(ids['book'],ids['cupboard'])]
            if fi==2:info+=['(inside %d %d)'%(ids['cup'],ids['closet'])]
            pairs=[('(:task (puton X Y) (:cond (sort X cup) (sort Y table)))','Put the cup on the table.'),
                ('(:task (takeout X Y) (:cond (sort X cup) (sort Y cupboard)))','Take out the cup from the cupboard.'),
                ('(:task (puton X Y) (:cond (sort X book) (sort Y desk)))','Put the book on the desk.'),
                ('(:task (give human X) (:cond (sort X bottle)))','Give the bottle to the human.'),
                ('(:task (puton X Y) (:cond (sort X can) (sort Y table)))','Put the can on the table.'),
                ('(:task (goto X) (:cond (sort X table)))','Go to the table.')]
            rng.shuffle(pairs)
            plan=[];current=loc['cupboard']
            def move(to):
                nonlocal current
                if current!=to:plan.append(['Move',to]);current=to
            if hand:plan+=[['PutDown',hand]]
            if tray:plan+=[['FromPlate',tray],['PutDown',tray]]
            plan+=[['Open',ids['cupboard']],['TakeOut',ids['cup'],ids['cupboard']]]
            move(loc['table']);plan+=[['PutDown',ids['cup']]]
            move(loc['human']);plan+=[['PickUp',ids['bottle']],['PutDown',ids['bottle']],['PickUp',ids['can']]]
            move(loc['table']);plan+=[['PutDown',ids['can']]]
            test=ET.Element('test');env=ET.SubElement(test,'env',mis='on',err='on',ans='on')
            ET.SubElement(env,'info').text='\n'+'\n'.join(info)+'\n'
            missing=[]
            if fi>=2:missing+=['(plate %d)'%tray]
            if fi==3:missing+=['(hold %d)'%hand,'(closed %d)'%ids['cupboard']]
            ET.SubElement(env,'mis').text=' '.join(missing)
            err=ET.SubElement(env,'err');ET.SubElement(err,'r');ET.SubElement(err,'w');ET.SubElement(env,'extra')
            ET.SubElement(test,'instr').text='(:ins '+' '.join(x[0] for x in pairs)+')'
            ET.SubElement(test,'nl').text=' '.join(x[1] for x in pairs)
            name='k%02d%s'%(fi+1,chr(97+vi));path=DEST/(name+'.xml')
            ET.ElementTree(test).write(str(path),encoding='utf8',xml_declaration=True)
            rows.append(dict(id=name,path=path.name,family=family,stage=2,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),reference_actions=plan,reference_goals=6,reference_constraints=0))
    (DEST/'catalogue.json').write_text(json.dumps(dict(design_seed=17741004,cases=rows),ensure_ascii=False,indent=2),encoding='utf8')
    (DEST/'.gitattributes').write_text('*.xml -text\n*.json -text\n',encoding='utf8')
    (DEST/'README.md').write_text('# 1.7.7 独立结构题\n\n8题、4族、每题6目标。显式 at 与远处闭柜、两个送达共用父容器、槽位与双父、双槽同物。ID/地点/任务序独立变化；书初始在书桌且保持独立 inside（相应族）；其送达目标是已满足控制。作者路径缩短以适应5秒预算，只验证SDK可解性。生成器不读取规划器结果；观察结果后这些题转为回归集。\n',encoding='utf8')
if __name__=='__main__':main()
