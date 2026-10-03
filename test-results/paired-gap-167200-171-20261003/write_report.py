#!/usr/bin/env python3
"""Narrative from reconciled analysis, retaining all negative pairs."""
from pathlib import Path
import json, collections

HERE=Path(__file__).resolve().parent
OUT=HERE/'analysis'
load=lambda p:json.loads(p.read_text(encoding='utf-8'))

def main():
    m=load(OUT/'metrics.json');t=load(OUT/'pair-traces.json');v=load(OUT/'analysis-validation.json');reviews=load(HERE/'case_review.json')
    import csv
    with (OUT/'category-summary.csv').open(encoding='utf-8-sig') as f:cats=list(csv.DictReader(f))
    with (OUT/'gaps.csv').open(encoding='utf-8-sig') as f:gaps=list(csv.DictReader(f))
    n=m['negative_stage2']
    lines=['# src1.6.7-200ms → src1.7.1 直接配对与 Stage 2 gap 诊断','',
        '原71输入、IT/NT、两轮的284对直接比较已经完成。Stage 2 中 G_old > G_new 的 %d 对来自 %d 个输入，目标净损失 %d、基础分损失 %d。'%(n['pairs'],n['unique_inputs'],n['goal_loss'],n['base_loss']),
        '其中 %d 对属于“旧版实际成功且全约束安全”的 recoverable gap，净损失 %d 个目标、%d 基础分；另外 %d 对是旧版实际成功的约束交换。依赖错误信息碰巧得到旧版独有目标的 legacy-lucky 为 %d 对。'%(n['safe_pairs'],n['safe']['goal_loss'],n['safe']['base_loss'],n['constraint_trade_pairs'],n['legacy_lucky_pairs']),
        '', '## 比较口径与冻结','',
        '- 比较臂直接为 src1.6.7-200ms 与冻结的 src1.7.1；两版重新完整编译并链接原官方 SDK，没有拼接前两次发布的成绩作为本次结果。',
        '- 71输入沿用 src1.7 原始 input-audit 的 ID、stage、SHA256。旧路径移动到 HistoryVersion 时，只接受字节哈希相同的文件。33道原比赛题、37道原 release fixtures、1道原 unified fixture；原先排除的02/04/05维持排除。',
        '- 每输入 × IT/NT × 两轮，seed=20260924、5000ms；串行交替 AB/BA；StageTiming=0，正常默认策略。每一次 cserver 日志均核对种子标记。固定 seed 不保证分叉后观察值一致，动作不同会改变随机数消费。',
        '- 运行前后核对两版源码与全部题源哈希，final-audit 通过。scheduler、Probe、canonical、mutation、score、题源均保持字节一致；仅新增独立分析目录。',
        '- G/C 使用官方 vanswer 的 value(id,40/20)，K 从 server.log 单流动作重算，基础分 B=40G+20I(G>0)C−K。官方分含时间奖励并封顶1000，raw_score 单独保留。内部 canonical 终态另列，不替代官方指标。',
        '- 先按实际动作及反馈对齐共同前缀，再追踪资格、排序、Probe、任务尝试次数、实际成功动作至旧独有官方目标。记录第一次动作分叉与后续决定损失的分叉，二者可以不同。',
        '- 两轮是同一 seed 的重复，所有数值按配对运行计数；重复题目中的目标也按官方 ID 计数。它们不构成独立随机样本，重复目标数不等于独立物理动作数。',
        '', '## 全量结果','',
        '|范围|对数|G 旧→新|C 旧→新|K 旧→新|基础分 旧→新|官方分 旧→新|G提高/相等/下降|','|---|---:|---:|---:|---:|---:|---:|---:|']
    for scope in ('all','stage1','stage2','it','nt'):
        x=m[scope];a,b=x['baseline'],x['current'];g=x['goal_pairs']
        lines.append('|%s|%s|%s→%s|%s→%s|%s→%s|%s→%s|%s→%s|%s/%s/%s|'%(scope,x['pairs'],a['final_goals'],b['final_goals'],a['credited_constraints'],b['credited_constraints'],a['action_cost'],b['action_cost'],a['base'],b['base'],a['official_score'],b['official_score'],g['increase'],g['equal'],g['decrease']))
    lines+=['','失败/超时：旧 %d/%d，新 %d/%d。逐 pair CSV 保留全284对，筛选 CSV 保留全部负向 Stage 2 对。'%(m['all']['baseline']['failures'],m['all']['baseline']['timeouts'],m['all']['current']['failures'],m['all']['current']['timeouts']),
        '', '## 互斥的 pair 主分类','',
        '每个负向 pair 只有一个主分类，基础分只计入主分类；次要机制是诊断标签，不能相加。类别名表示本次差异的机制，其中 qualification-too-strict / constraint-gate-strict 并不自动意味着可以安全放宽。',
        '', '|主分类|pair|输入|目标净损失|目标分损失|约束分损失|成本项|基础分净损失|安全可恢复pair|','|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for c in cats:lines.append('|%s|%s|%s|%s|%s|%s|%s|%s|%s|'%(c['category'],c['pairs'],c['unique_inputs'],c['goal_loss'],c['goal_component_loss'],c['constraint_component_loss'],c['cost_component_loss'],c['base_loss'],c['safe_recoverable_pairs']))
    lines+=['', '目标分损失=40(G_old−G_new)，约束分损失=20(C_old−C_new)，成本项=K_new−K_old；成本项可为负。三项严格相加等于基础分净损失。所有分类基础分相加=%d，与筛选集合一致。'%n['base_loss'],
        '', '## 逐目标分类','',
        'goal-gaps.csv 每行一个旧版独有官方目标 ID。每个目标记录 ASP 条件、类别、旧版持续满足起始事件和动作反馈，以及新版是否曾经满足。目标分类只归因40分目标项，探索成本与约束信用不任意摊到单个目标。',
        '36.xml 的 pair 主类为 probe-coverage-gap，但其六个黑杯重复目标属于 Probe 覆盖缺口，红杯 putin 的一个目标属于 ordering-cascade。因此目标级分类与 pair 主分类的目标数分布不同。',
        '', '|目标级类别|旧独有目标ID计数|目标分损失|','|---|---:|---:|']
    for c in cats:
        if int(c['goal_level_old_only_count']):lines.append('|%s|%s|%s|'%(c['category'],c['goal_level_old_only_count'],c['goal_level_points']))
    lines+=['', '## 每个输入的行为链','',
        '|输入|主类|每pair G 旧→新|每pair基础分损失|安全性|代表性证据|','|---|---|---:|---:|---|---|']
    for cid in sorted(set(g['id'] for g in gaps)):
        rs=[g for g in gaps if g['id']==cid];r=rs[0]
        lines.append('|%s %s|%s|%s→%s|%s|%s|[%s](%s)|'%(cid,Path(r['case']).name,r['primary'],r['G_old'],r['G_new'],r['base_loss'],r['safety'],r['pair'],r['evidence']))
    lines+=['','全部IT/NT与两轮的逐pair链条均在 pair-evidence/ 中；pair-traces.json 保留精确日志行号、动作序号、官方目标差集与评分结果。','']
    for cid in sorted(set(g['id'] for g in gaps)):
        rv=reviews[cid]
        if 'same_review_as' in rv:rv=reviews[rv['same_review_as']]
        r=next(g for g in gaps if g['id']==cid)
        lines+=['### '+cid+' / '+Path(r['case']).name,'',rv['mechanism'],'',rv['safety_note'],'', '[本输入代表性日志链](%s)'%r['evidence'],'']
    lines+=['## recoverable 与 legacy lucky 的证据标准','',
        'recoverable-safe-observed 要求旧版独有目标由真实世界终态和成功动作支持，并且旧版所有官方约束保有信用。含错误初始信息、动作失败或 AskLoc 错误响应本身不使结果成为 lucky；要检查获胜目标是否在正确证据下实际完成，以及错误线索是否决定了它的成功。',
        '本次安全可恢复集合为10、14、18、34、35、36.xml，共%d对；约束交换集合为06、22、23、24.xml和P09，共%d对。'% (n['safe_pairs'],n['constraint_trade_pairs']),
        '36.xml 是纠错后的安全恢复：PickUp14 false → AskLoc14 inside(14,6)（与题源真值一致）→ TakeOut14 6 true → PutDown14 true。错误outside信息触发了纠错，成功依靠正确inside反馈与实际动作；应归入Probe能力覆盖差异。',
        '22–24.xml 是实际成功的约束交换：沙发位置从错误4被AskLoc/Sense纠正到真实6后才放物；旧版0/2约束信用，所以不能列入安全恢复，也不能据“使用了错误初始线索”归成legacy-lucky。',
        '14.xml 的旧版 AskLoc19 inside(19,5) 与真实inside(19,12)不符，随后TakeOut19 5和PutDown19失败；这个错误信息分支没有产生本次旧独有的GOTO目标。06.xml通过错误椅子线索到8后发现书本，是两版共同前缀，不能解释旧独有差集。',
        '本次负向差集中没有验证到 legacy-lucky。该结论只覆盖这71题、这个seed的获胜目标链；已有错误信息分支照样保存在原始证据中。安全可恢复是对已观察旧版路径的诊断，尚未执行任何新版修复的反事实验证。',
        '', '## 未占主分类的类别与边界证据','',
        '- no-location-clue：14.xml中白杯21缺地点线索，影响双方没有完成的give；它不属于旧版独有目标差集，故没有把它误计入目标损失。',
        '- deadline：所有负向pair均有明确非deadline停止机制。06.xml旧版尾部接近预算，但新版在明显余时停止且有requires_verified_group/constraint_rejected证据；不能将其归为deadline。',
        '- terminal/score-disagreement：多对内部约束终态与官方信用不同，例如18.xml内部C=0/20、unknown=19，官方两版都是20/20。这会影响保守资格/Probe安全证明，作为次要证据保存；官方重算的G差异不是客户端计数差异造成。',
        '- other：已筛选负向pair均有审阅过的主机制，没有未归类残差。没有运行的类别不提供虚构代表日志；其边界证据见[CATEGORY_EVIDENCE.md](CATEGORY_EVIDENCE.md)。',
        '', '## 完整性与复核','',
        '核验284个唯一pair、568次运行、71个输入的完整IT/NT×两轮网格。每次官方G/C、动作K和基础分从原始日志重算，并与运行结果逐一相等；%d个旧独有目标的轻量动作重放与官方终态一致。'%v['goal_rows'],
        '两轮动作/G/基础分不一致的臂数：%d。所有原始运行、输入、官方ASP、两版二进制、编译命令及seed interposer保存在raw-evidence.zip，原件未删除。'%len(v['repeat_differences']),
        '', '## 交付文件','',
        '- [pairs.csv](pairs.csv)：全部284对；[gaps.csv](gaps.csv)：全部负向Stage 2对。',
        '- [goal-gaps.csv](goal-gaps.csv)：逐目标类别与成功动作；[category-summary.csv](category-summary.csv)：11类完整汇总，包括0计数。',
        '- [CATEGORY_EVIDENCE.md](CATEGORY_EVIDENCE.md)：每类代表日志与边界证据；[pair-traces.json](pair-traces.json)：完整机器可读追踪。',
        '- [analysis-validation.json](analysis-validation.json)、[repeat-audit.json](repeat-audit.json)、[source-receipt.json](source-receipt.json)：网格、重算、重复与来源核验。',
        '- [原始证据归档](../raw-evidence.zip)、[运行冻结核验](../raw-metadata/final-audit.json)、[输入与源码审计](../raw-metadata/input-audit.json)。',
        '- 分析与复跑入口：run_direct_pairs.py / analyze_direct_pairs.py / case_review.json / write_report.py。复跑必须选用新的输出目录。']
    with (OUT/'REPORT.md').open('x',encoding='utf-8') as f:f.write('\n'.join(lines)+'\n')
    ce=['# 11类证据索引','', '主分类互斥；次要机制与目标级细分分别列出。日志行号是保留原件中的实际行号，客户端摘录已去ANSI，仅为了阅读。','']
    for c in cats:
        cat=c['category'];ce+=['## '+cat,'','主分类 %s pair，目标净损失 %s，基础分损失 %s；目标级独有ID %s，40分目标损失 %s。'%(c['pairs'],c['goal_loss'],c['base_loss'],c['goal_level_old_only_count'],c['goal_level_points']),'']
        ts=[x for x in t if x['classification']['primary']==cat]
        if not ts:
            ce+=['本筛选集合没有该类主因，不能提供正例代表。','']
            if cat=='legacy-lucky':ce+=['错误信息与真实成功必须分开。参见[c011：错误AskLoc未产生成绩差集](pair-evidence/c011-it-r1.md)、[c003：共同前缀中的错误线索发现](pair-evidence/c003-it-r1.md)、[c033：纠正inside之后的成功](pair-evidence/c033-it-r1.md)。','']
            elif cat=='no-location-clue':ce+=['[c011](pair-evidence/c011-it-r1.md)未知白杯21影响双方give；旧独有goal5为已知地点的GOTO，主因是三次上限。','']
            elif cat=='deadline':ce+=['[c003](pair-evidence/c003-it-r1.md)新版停止时仍有余时且约束gate/Probe明确拒绝；每pair末轮remaining在完整日志中。','']
            elif cat=='terminal/score-disagreement':ce+=['[c015](pair-evidence/c015-it-r1.md)内部C=0/20、unknown=19，但官方C=20/20。pairs.csv的canonical_old/new字段保留内部指标，正式损失按vanswer重算。','']
            continue
        x=ts[0];ce+=[x['classification']['mechanism'],'',x['classification']['safety_note'],'','[完整代表pair](pair-evidence/'+x['pair']+'.md)','']
        for arm in ('baseline','current'):
            ce+=['### '+arm,'']
            for e in x['excerpts'][arm][:7]:ce+=['[%s:L%d](%s#L%d)'%(Path(e['path']).parent.name,e['line'],e['path'],e['line']),'```text',e['text'],'```','']
    with (OUT/'CATEGORY_EVIDENCE.md').open('x',encoding='utf-8') as f:f.write('\n'.join(ce)+'\n')
    print(OUT/'REPORT.md')

if __name__=='__main__':main()
