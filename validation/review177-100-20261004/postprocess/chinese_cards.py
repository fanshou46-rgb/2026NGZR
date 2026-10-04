"""Documentation overlay; does not edit frozen XML/cards/reference inputs."""
from pathlib import Path
import json,re,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parents[1]
BANK=ROOT/'题目/independent_100_20261004'
SORT={'human':'人','table':'桌子','desk':'书桌','cupboard':'橱柜','closet':'衣柜','microwave':'微波炉','refrigerator':'冰箱','sofa':'沙发','can':'罐子','cup':'杯子','book':'书','bottle':'瓶子'}
COLOR={'red':'红色','blue':'蓝色','green':'绿色','yellow':'黄色','black':'黑色','white':'白色'}
MUTATION={'missing_nl_end_tag':'缺少自然语言结束标签','unescaped_ampersand':'未转义的&字符','unbalanced_it_parenthesis':'IT括号不闭合','wrong_task_arity':'任务参数数量错误','unknown_task_predicate':'使用未知任务谓词','target_object_replaced':'IT与NT目标物不同','negation_removed':'IT与NT否定语义不同','inside_changed_to_near':'IT与NT把容器内关系和靠近关系混用','one_sentence_omitted':'NT遗漏一条IT指令','door_target_reversed':'IT与NT柜门目标相反'}
def names(path):
    info=ET.parse(path).getroot().find('env/info').text
    objects={}
    for clause in re.findall(r'\(([^()]*)\)',info):
        p=clause.split()
        if p[0] in ('sort','color'):objects.setdefault(int(p[1]),{})[p[0]]=p[2]
    return lambda i:('机器人' if i==0 else COLOR.get(objects.get(i,{}).get('color',''),'')+SORT.get(objects.get(i,{}).get('sort',''),str(i)))+f'〔{i}〕'
def translate(t,n):
    a=[n(i) for i in t['args']];p=t['pred']
    phrases={'give':lambda:f'把{a[1]}交给{a[0]}','putin':lambda:f'把{a[0]}放进{a[1]}','puton':lambda:f'把{a[0]}放到{a[1]}处','close':lambda:f'关闭{a[0]}','takeout':lambda:f'从{a[1]}取出{a[0]}','pickup':lambda:f'拿起{a[0]}','goto':lambda:f'前往{a[0]}','open':lambda:f'打开{a[0]}','putdown':lambda:f'放下{a[0]}','inside':lambda:f'{a[0]}在{a[1]}内','near':lambda:f'{a[0]}靠近{a[1]}','plate':lambda:f'{a[0]}在托盘上','closed':lambda:f'{a[0]}关闭'}
    description=phrases[p]()
    if t['kind']=='constraint':description=('必须保持：' if t['positive'] else '禁止出现/执行：')+description
    return description
def action(a,n):
    p=a[0];v=a[1:]
    if p=='move':return f'移动到地点{v[0]}'
    if p=='sense':return '观察当前地点'
    if p=='askloc':return f'询问{n(v[0])}位置（回答仍待验证）'
    if p=='toplate':return f'把{n(v[0])}放到托盘'
    if p=='fromplate':return f'从托盘取出{n(v[0])}'
    return translate(dict(kind='task',pred=p,args=v),n)
def main():
    cat=json.loads((BANK/'catalogue.json').read_text(encoding='utf8'))['cases']
    errors={x['id']:x for x in json.loads((BANK/'invalid/expected_errors.json').read_text(encoding='utf8'))}
    dest=OUT/'中文题卡';dest.mkdir(exist_ok=True);index=['# 独立100题中文题卡','', '本目录是冻结后的阅读说明，不改变执行XML及参考动作。90道合法题为45组Stage1/Stage2；10道非法题没有执行参考方案，正确处理是识别并拒绝对应错误。正式评分、预检与生成时快照分开记录。','']
    for c in cat:
        lines=[f'# {c["id"]}','',f'冻结输入：[XML](../../../题目/independent_100_20261004/{c["path"]})','',f'SHA256：`{c["sha256"]}`','']
        if c['kind']=='invalid':
            e=errors[c['id']]
            lines+=['类别：非法题（不计能力得分）。','',f'预期错误：{MUTATION.get(e["mutation"],e["mutation"])}；识别层：{e["expected_layer"]}。',f'离线实际检查：`{e["offline_error"]}`。','', '参考处理：在执行物理动作前拒绝。真实SDK/三版处理结果另见非法题表，不把平台接受误报为题目合法。']
        else:
            ref=json.loads((BANK/c['reference']).read_text(encoding='utf8'));n=names(BANK/c['path'])
            lines+=[ref['title'], '', c['novelty'],'',f'类别：{"全解" if c["kind"]=="full" else "取舍"}；Stage{c["stage"]}；7目标、30约束、名义毛分880。','', '## 目标与约束','']
            lines += [f'{t["id"]}. {translate(t,n)}。' for t in ref['clauses']]
            lines += ['', '目标按官方终态计分，动作完成不等于目标永远成立。约束是否受到过程影响，以官方SDK语义及记录的全过程为准。','', '## 信息扰动','',json.dumps(c['information_perturbation'],ensure_ascii=False,indent=2),'', '## 参考与比较方案','', '以下使用作者真值，是可执行见证；不提供给机器人，也不是能自主处理所有随机回答的策略或最短路线证明。']
            for plan in ref['plans']:
                lines += ['',f'### {plan["name"]}（{plan["role"]}）','',f'参考G={plan["expected_completed_goals"]}，违反约束={plan["expected_violated_constraints"]}。','']
                lines += [f'{i}. {action(a,n)}。' for i,a in enumerate(plan['actions'],1)]
            proof=ref['proof'];lines+=['','## 可解性或结构上界','',proof['statement']]
            if 'theoretical_gross_upper' in proof:lines+=['',f'结构毛分上界：{proof["theoretical_gross_upper"]}；尚须扣实际动作K。时间奖励和SDK正式分不由此界推出。']
        (dest/(c['id']+'.md')).write_text('\n'.join(lines)+'\n',encoding='utf8')
        index.append(f'- [{c["id"]}]({c["id"]}.md)')
    assert len(cat)==100 and len([p for p in dest.glob('*.md') if p.name!='README.md'])==100
    (dest/'README.md').write_text('\n'.join(index)+'\n',encoding='utf8')
    print('100 Chinese cards; frozen input bytes untouched')
if __name__=='__main__':main()
