#!/usr/bin/env python3
"""Generate inspectable Chinese design, score, and execution reports from evidence."""
import csv
import json
import re
from pathlib import Path
from design import SUITE

ROOT=SUITE.parents[1]
RUN=ROOT/'test-results/liuyifan1.0-20260924-final'
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
cases=load(SUITE/'manifest.json'); rows=load(RUN/'suite.json')
fixed=[r for r in rows if r['who']=='fixed']; refs={r['id']:r for r in rows if r['who']=='reference'}
natural={(r['id'],r['mode']):r for r in fixed if r['seed']=='natural'}
checks={r['id']:r for r in load(SUITE/'static-validation.json')}

def link(r,file='server.log'):
    return '../../'+r['output']+'/'+file

def sequence(r):
    return ' → '.join(e['action']+'('+e['args'].replace(' ',',')+')'+('×' if e['reply']=='false' else '') for e in r['events'])

def final_snapshot(r):
    raw=(ROOT/r['output']/'client.log').read_text(encoding='utf-8',errors='replace')
    raw=re.sub(r'\x1b\[[0-9;]*m','',raw)
    match=re.findall(r'\[3A\]\[final\] goals=(\d+)/(\d+) \(unknown=(\d+)\), constraints=(\d+)/(\d+) \(unknown=(\d+)\), base_score=(-?\d+)',raw)
    return list(map(int,match[-1])) if match else None

def write(name,lines):
    (SUITE/name).write_text('\n'.join(lines)+'\n',encoding='utf-8')

def main():
    assert len(rows)==26 and len(fixed)==20
    assert all(r['status']=='ok' and r['evaluator_valid'] for r in rows)
    assert all(r['semantic_equal'] for r in load(RUN/'parse/comparison.json'))
    assert load(RUN/'source-unchanged.json')['verified']
    stable=[]
    for c in cases:
        runs=[r for r in fixed if r['id']==c['id']]
        stable.append(dict(id=c['id'],action_trace_equal=all(r['events']==runs[0]['events'] for r in runs),
            score_min=min(r['raw_score'] for r in runs),score_max=max(r['raw_score'] for r in runs),
            runs=len(runs),final_goals=runs[0]['final_goals'],credited_constraints=runs[0]['credited_constraints']))
    assert all(r['action_trace_equal'] for r in stable)
    (RUN/'stability.json').write_text(json.dumps(stable,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    with (SUITE/'scores.csv').open('w',encoding='utf-8-sig',newline='') as f:
        fields=['who','seed','id','title','stage','mode','raw_score','official_score','final_goals','credited_constraints',
                'action_count','action_cost','base_score','efficiency_score','platform_seconds','status','output']
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore'); w.writeheader(); w.writerows(rows)
    score=['# liuyifan1.0 分数报告','',
        '日期：2026-09-24。6道原型题，原版 src1.3.3-fixed 完成20次正式求解测试；另有6次作者参考方案的官方运行。26次均取得有效官方评分，0次平台硬超时、0次客户端崩溃。',
        '', '## 测试口径','',
        '- WSL2 发行版 Ubuntu-18.04，系统 Ubuntu 18.04.2 LTS，g++ 7.5.0。',
        '- 官方 SDK：`/home/yifan/env-release-2026`；cserver、libasp、libframe及求解器源码哈希见[构建记录](../../test-results/liuyifan1.0-20260924-final/build-fixed/build.json)。',
        '- 出题依据是仓库中的2025规则及出题指南；执行评分使用现有2026 SDK，5000 ms。该测试结果不冒称为2025平台实测。',
        '- 01、02、05、06为Stage 1；03、04为Stage 2。所有题均测IT和NT。Stage 2再使用20260924、20260925两个固定种子各测IT/NT。',
        '- 原版求解器保持不变；[前后源码哈希核验](../../test-results/liuyifan1.0-20260924-final/source-unchanged.json)通过。固定种子仅用于测试端srand插桩；无种子的原生运行完整保留。',
        '- 分数、目标数和约束数来自官方server及ASP answer-set；基础分=40×完成目标+20×计分约束−动作成本。效率分采用官方总分减基础分，避免规则文字与平台公式差异。',
        '- 参考客户端执行公开的作者动作序列，用于证明可行解和比较动作成本；它掌握题目真值、没有在线搜索开销，所得分数不是最优解证明，也不计入求解器成绩。',
        '', '## 主测试：未固定随机种子','',
        '|题|主题|阶段|IT分|NT分|完成目标/总目标|维护约束/总约束|动作数|基础分|参考基础分|',
        '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for c in cases:
        a=natural[(c['id'],'it')]; b=natural[(c['id'],'nt')]; ref=refs[c['id']]
        score.append('|[{}]({}.xml)|{}|{}|{}|{}|{}/{}|{}/{}|{}|{}|{}|'.format(c['id'],c['id'],c['title'],c['stage'],
            a['raw_score'],b['raw_score'],a['final_goals'],c['goals'],a['credited_constraints'],c['constraints'],a['action_count'],a['base_score'],ref['base_score']))
    it=sum(natural[(c['id'],'it')]['raw_score'] for c in cases); nt=sum(natural[(c['id'],'nt')]['raw_score'] for c in cases)
    score += ['', '**IT合计：{}分；NT合计：{}分；两个子项目合计：{}分。** 这只是6道原型的测试合计。所有分数均低于1000，因此raw与封顶后的official字段相同。'.format(it,nt,it+nt),
        '', '06有意放弃give目标，维护三个约束；05有意牺牲must-closed约束。两者都符合题目的收益取舍设计。04少完成的goto目标属于实际失分。',
        '', '## 第二阶段复测','',
        '|题|模式|自然运行|种子20260924|种子20260925|动作轨迹|', '|---|---|---:|---:|---:|---|']
    for c in cases:
        if c['stage']!=2: continue
        for mode in ('it','nt'):
            rs={r['seed']:r for r in fixed if r['id']==c['id'] and r['mode']==mode}
            score.append('|{}|{}|{}|{}|{}|完全一致|'.format(c['id'],mode.upper(),*[rs[s]['raw_score'] for s in ('natural','20260924','20260925')]))
    score += ['', '这两题各6次运行的动作、反馈、目标数、约束数均一致。04的251–253分变化来自耗时奖励；其基础分恒为193。所有当前测试轨迹均没有AskLoc，故种子复测证明本题执行稳定，不覆盖错误询问回答分支。',
        '', '## 逐次完整记录','',
        '|执行者|题|模式|种子|官方分|基础分|效率分|动作成本|用时s|证据|',
        '|---|---|---|---|---:|---:|---:|---:|---:|---|']
    for r in rows:
        score.append('|{}|{}|{}|{}|{}|{}|{}|{}|{:.3f}|[server]({}) / [trace]({})|'.format(r['who'],r['id'],r['mode'].upper(),r['seed'],
            r['raw_score'],r['base_score'],r['efficiency_score'],r['action_cost'],r['platform_seconds'],link(r),link(r,'trace.json')))
    score += ['', '## 结论','',
        '01、02、05、06的基础分与作者参考方案相同；03多一次Sense，基础分少1；04基础分少43，构成为少一个goto目标40分、动作净成本多3分。六题基础分合计1492，参考方案为1536，相差44分。',
        '', '题库适合继续作为小规模原型与回归集。04应在修复求解器后再考虑作为优势题推广。',
        '', '机器可读结果：[scores.csv](scores.csv)。设计说明：[DESIGN.md](DESIGN.md)。执行分析：[STRATEGY_REPORT.md](STRATEGY_REPORT.md)。']
    write('SCORE_REPORT.md',score)
    strategy=['# liuyifan1.0 执行策略报告','',
        '五道题达到作者参考方案的目标完成数和约束保持数；04稳定少完成一个终态goto目标。05同时验证了当前内部约束估分会把已破坏的约束重新计入。以下分析以自然运行IT日志为主，各题IT/NT动作及回复一致。',
        '', '## 01 自由终态汇聚','',
        '程序选择位置2的table为汇聚点，保留原地红书、蓝杯，把位置3的白瓶、绿罐和位置4的黄遥控器、黑书依次搬来。最终七个goto同时成立。16动作、成本48，与参考方案一致。这道题直接验证现有MultiGoto聚合能力。',
        '', '## 02 搬运与到达共享终态','',
        '程序先做四个puton，把全部小物体搬到table，最后的四个小物体goto和table goto随布局一起成立。九个目标全部完成，16动作、成本48。它没有在完成搬运后再逐个无效访问原位置。',
        '', '## 03 must-near纠错与缺失补全','',
        '初始红书被错报在位置4，蓝杯位置缺失。初始must-near投票在位置2/4之间出现平票，日志明确记录“不传播”；代码没有立即从约束得出可靠位置。搬运白瓶回table时执行一次Sense，实际读到红书、蓝杯及table，再完成绿罐搬运，七目标、两约束全部获得官方计分。',
        '', '实际优势是冲突证据下保持谨慎、用一次感知恢复正确状态并共享该结果。相对参考多1次Sense、少1基础分；本题不能作为“初始零感知纠错成功”的证据。',
        '', '## 04 容器纠错后的终态丢失','',
        '六次官方运行均完成5/6目标、保持2/2约束，18动作、成本47、基础分193。缺失的是goto microwave。',
        '', '执行链：先将蓝杯、白瓶、绿罐放入microwave并关闭；随后Move(3)，对真实已经关闭的cupboard执行Close(3)，平台返回false，再Sense确认柜子。机器人最终停在cupboard处，而microwave位于位置4。',
        '', '源码与日志对应的原因：',
        '', '- `ApplyOpenCloseCorrection`依据must-closed设置了cupboard的isOpen=false，但没有建立对应已验证证据；`SolveTask_Close`在Stage 2仍选择实际验证，产生离开终点和失败动作。',
        '- `AfterSolveTask(close microwave)`给microwave的is_keep增加2；`CalculateTaskRisk(goto microwave)`把同一keep值加到goto风险，尽管移动机器人不需要移动microwave。该候选因此eligible=false。',
        '- 最终候选日志显示goto计划完整、预计220ms、边际收益+35，却因eligible=false被StopGate拒绝。当时仍剩约2700ms，失分不是硬超时造成的。',
        '', '与参考的基础分差为43：目标少40，动作净成本多3。参考计划预先空手开microwave；当前程序在首件物体已拿起时额外使用盘子暂存，随后又去cupboard。因此成本差不能简单等同于末尾三步的7分。',
        '', '修复优先级：先拆分“物体不可移动”与“机器人可到达”的风险；再统一约束推导证据与零动作完成判定；最后根据真实终态重新激活仍有收益的goto。04保留原题作为回归用例。',
        '', '## 05 牺牲一个约束的收益取舍','',
        '旧启发式检测到open_cons与四个putin冲突，放弃该限制，执行Open→四组PickUp/PutIn→Close。官方完成6/6目标、计0/1约束，10动作、成本20、基础分220。选择与参考相同。',
        '', '这里同时出现估分缺陷：客户端最终日志显示constraints=1/1、base_score=240；官方为0/1和220。它把重新关闭的柜门视为恢复了约束，但全过程must-closed已经在Open时永久失去计分资格。当前题目选对了策略，内部评分仍高估20分。将shadow收益排序投入实际选任务前，应先接入不可逆的约束破坏记录。',
        '', '## 06 放弃低收益目标','',
        'give红杯的风险被计算为3，程序跳过该目标，只将蓝书、白瓶放到table，随后三个goto全部满足。官方完成5/6目标、保持3/3约束，7动作、成本20、基础分240，与参考相同。',
        '', '交付红杯需要打开cupboard、把红杯取出并送到human，从而破坏must-closed、must-inside、must-not-near human三个不同约束。新增40目标分不足以弥补60约束分及动作成本；放弃该目标是本题的预期策略。',
        '', '## 逐题真实动作','', '以下`×`表示平台返回false，完整反馈在trace.json中。']
    for c in cases:
        r=natural[(c['id'],'it')]
        strategy += ['', '### {} {}'.format(c['id'],c['title']), '', sequence(r), '',
            '[客户端决策日志]({}) · [官方反馈日志]({}) · [最终ASP评分]({})'.format(link(r,'client.log'),link(r),link(r,'runtime/vanswer.txt'))]
    strategy += ['', '## 内部估分与官方基础分','',
        '|题|客户端最终目标数|客户端计入约束数|客户端基础分|官方基础分|解释|',
        '|---|---:|---:|---:|---:|---|']
    notes={'01':'一致','02':'一致','03':'一致','04':'must-inside仍为UNKNOWN，少计一个已维护约束20分','05':'只看恢复后的关闭状态，多计已破坏约束20分','06':'一致'}
    for c in cases:
        r=natural[(c['id'],'it')]; s=final_snapshot(r)
        strategy.append('|{}|{}|{}|{}|{}|{}|'.format(c['id'],s[0],s[3],s[6],r['base_score'],notes[c['id']]))
    strategy += ['', '## 出题与开发建议','',
        '01/02可继续发展为终态规划题；03可扩展为有真实观测锚点的关系推理题；05/06可作为成对收益取舍回归。04优先用于修复终态回收和容器证据问题。当前测试没有执行AskLoc，也没有直接验证关闭容器搜索能力，后续应另设有信息线索的搜索原型。',
        '', '建议修复顺序：goto误用keep风险 → 全过程约束记账 → 约束推导证据一致性 → 候选收益驱动任务组调度。本轮保持src1.3.3-fixed源码不变。']
    write('STRATEGY_REPORT.md',strategy)
    design=['# liuyifan1.0 原型题设计','',
        '首批共6道。依据2025规则编写；每题包含完整env、instr和nl，Stage 1四题、Stage 2两题。',
        '', '## 合规与计分边界','',
        '对象ID连续，robot=0、唯一human=1；所有小物体有颜色且以sort+color唯一绑定；所有大物体种类唯一且真实位置不重合；指令无重复、无两个小物体同句；goto小物体初始均在外部。所有约束在真实初态成立。第二阶段错误仅作用于允许的at/inside和容器开关字段。',
        '', '04的NT仅在物体名、颜色词中加入#和混合大小写；其空格、句号和动作词保持合法。extra的microwave关闭信息有独立info句补充。',
        '', '每个参考方案的基础分均≥200；按40×目标数+20×约束数+100计算的保守总分上界均≤1000。参考动作已经官方运行验证，所以理论可达分数落在规则要求区间内。参考方案不宣称动作最优。',
        '', 'IT/NT实际解析、对象绑定与纠错后快照通过等价比较；只规范化in/inside别名和give的literal-human/显式human绑定表示。',
        '', '## 原型明细']
    for c in cases:
        ch=checks[c['id']]
        design += ['', '### {} {}'.format(c['id'],c['title']), '',
            '- 文件：[{}.xml]({}.xml)，Stage {}，{}目标、{}约束。'.format(c['id'],c['id'],c['stage'],c['goals'],c['constraints']),
            '- 测试意图：'+c['intent'], '- 参考策略：'+c['strategy'],
            '- 参考基础分{}；保守总分上界{}。'.format(ch['reference_base_score'],ch['conservative_score_upper_bound']),
            '', '|对象ID|物体|真实初始状态|', '|---:|---|---|',
            '|0|robot|位置{}，手爪和盘子均为空|'.format(c['robot'])]
        for o in c['objects']:
            state='inside '+str(o['inside']) if 'inside' in o else '位置'+str(o['at'])
            if o.get('type'): state+='，'+('关闭' if o['closed'] else '打开')
            design.append('|{}|{} {}|{}|'.format(o['id'],o.get('color',''),o['sort'],state))
        design += ['', '|类别|IT|NT|', '|---|---|---|']
        for i,ntline in zip(c['instructions'],c['rendered_nt']):
            design.append('|{}|`{}`|{}|'.format(i['kind'],i['it'],ntline))
        design += ['', '参考动作：[reference-plans/{}.txt](reference-plans/{}.txt)。'.format(c['id'],c['id'])]
    design += ['', '## 设计验收修订','',
        '初稿06使用“红杯在cupboard内部且必须near cupboard”。官方平台并不自动把inside投影为near，参考运行只计两个约束。最终06已将第三约束改为“红杯必须不near human”，重新通过静态检查和官方参考运行。初稿证据单独保留在test-results/liuyifan1.0-20260924；正式统计只采用带-final的目录。',
        '', '规则来源：[2025赛事规则](../../docs/rules/rules-2025.pdf)、[2025出题指南](../../docs/rules/question-guide-2025.pdf)。']
    write('DESIGN.md',design)
    readme=['# liuyifan1.0','',
        '6道2025规则原型题，附WSL2 Ubuntu 18.04官方平台测试结果。当前求解器：src1.3.3-fixed。',
        '', '- [分数报告](SCORE_REPORT.md)：主测试、随机种子复测、逐次分数与原始证据。',
        '- [执行策略报告](STRATEGY_REPORT.md)：真实动作序列、收益取舍、04失分原因、05内部估分偏差。',
        '- [题目设计](DESIGN.md)：环境、IT/NT、参考策略与合规说明。',
        '- [scores.csv](scores.csv)：26次官方运行的结构化结果。',
        '- [test.list](test.list)：仅列出本批6道题。',
        '', '|题号|题型|阶段|', '|---|---|---|']
    readme += ['|[{}]({}.xml)|{}|{}|'.format(c['id'],c['id'],c['title'],c['stage']) for c in cases]
    readme += ['', '## 复现','', '从仓库根目录，在WSL2 Ubuntu-18.04中运行：','', '```bash',
        'python3 题目/liuyifan1.0/tools/check.py',
        'python3 题目/liuyifan1.0/tools/run.py --output test-results/liuyifan1.0-rerun-001', '```',
        '', '输出目录必须尚不存在。run.py重新编译求解器、验证IT/NT解析并执行26次官方运行；官方平台使用端口7932，脚本在运行前检查占用。报告生成器report.py绑定本次-final证据目录。',
        '', 'test.list同时含两个阶段，竞赛客户端按每题对应stage运行；本批runner会自动选择。正式按阶段提交时，应分别使用Stage 1的01/02/05/06与Stage 2的03/04。',
        '', '参考客户端只用于作者可行解验收，依据reference-plans执行固定动作；原版求解器测试不读取这些动作，也没有加入题号特判。']
    write('README.md',readme)
    print('Reports written; natural totals IT={} NT={}, {} official runs'.format(it,nt,len(rows)))

if __name__=='__main__': main()
