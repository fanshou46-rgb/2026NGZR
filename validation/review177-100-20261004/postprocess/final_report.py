"""Evidence-grounded Chinese report; never replace missing labels with guesses."""
from pathlib import Path
import collections,json,csv
OUT=Path(__file__).resolve().parents[1]

def main():
    facts=json.loads((OUT/'REPORT_FACTS.json').read_text(encoding='utf8'))
    audit=json.loads((OUT/'final-audit.json').read_text(encoding='utf8'))
    summary=json.loads((OUT/'SUMMARY.json').read_text(encoding='utf8'))
    trace=json.loads((OUT/'TRACE_AUDIT.json').read_text(encoding='utf8'))
    rr=[json.loads(x) for x in (OUT/'results.jsonl').read_text(encoding='utf8').splitlines()]
    assert audit['runs']==facts['runs']==summary['runs']==trace['runs']==6726
    names={'167':'1.6.7（300ms预留）','167_200':'1.6.7-200ms','177':'1.7.7','neutral':'概率中性','no_ask':'关闭询问更新','legacy_visibility':'旧式可见性'}
    lines=['# 1.7.7审核、1.6.7对照与独立100题最终报告','',
      '1.7.7在独立新题和完整71输入矩阵上没有超过两版1.6.7。已有52道结构题中目标与基础分提高，但正式分下降并有截止。新题Stage2三个概率消融均未改变实际路径，因此本轮没有证明新增模型带来重要任务收益。优先修复提前停止、反馈路线及执行稳定性，再验证完整概率决策。','',
      '## 运行范围与冻结证据','',
      '以68fe263b为冻结对象，共6726次：新题4320、历史1704、已有52题624、非法60、历史排除异常18。180次作者SDK参考及16次默认等价检查单列。全部源、输入、工具、SDK、二进制、种子和5000ms期限核对通过，三版比赛源码未修改。',
      '新100题为70全解、20取舍、10非法。90合法题组成45组Stage1/Stage2；每题7个不同目标、30条不同约束、名义毛分880。指南/离线/结构检查以及IT/NT参考执行先通过，随后冻结并观察机器人。参考使用作者真值，仅作为可行性见证，不进入机器人，也不证明Stage2自主最优。','',
      '## 正式代码排名：三个独立种子','',
      '新题与历史表只汇总前三个不同种子；第四轮是首种子重复，不作为独立样本。已有52题按协议只有前两个种子。各题库目标数量、重复目标和约束密度不同，因此分别排名。']
    for suite,title,arms in [('new','独立新90道合法题',tuple(names)),('historical','完整71输入',('167','167_200','177')),('seen','已有52道结构回归题',('167','167_200','177'))]:
        lines+=['',f'### {title}','','| 对照 | 次数 | G | C | K | 基础分已标签合计 | 封顶正式分合计 | 平均正式分 | SDK秒数 | SDK截止 | 外部超时 |','|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
        for arm in arms:
            p=facts['cohorts'][suite][arm]['primary'];s=lambda k:p[k]['sum']
            lines.append('| {} | {} | {} | {} | {} | {} | {} | {:.2f} | {:.3f} | {} | {} |'.format(names[arm],p['runs'],s('final_goals'),s('credited_constraints'),s('action_cost'),s('base'),s('official_score'),p['official_score']['mean'],s('platform_seconds'),p['sdk_cutoff'],p['external_timeout']))
    lines+=['','合法矩阵中评分和基础标签均无缺失；已评分合计与缺失按零的保守正式分汇总相同。所有原始分仍保留，正式分逐题封顶1000。负基础分保留。基础公式为40G + 20·I(G>0)C − K，G/C来自SDK终态而非机器人完成计数。',
      '新题1.7.7比原1.6.7少1233个目标，目标分−49320；约束分+480、动作费用节省16080，基础分仍少32760。时间奖励补回部分差距，但节省时间不能抵消执行缺失。新题90题中60题初态已有1目标、24题已有2目标、6题没有；实际G含这些目标，不能等同新增运输次数。','',
      '## 概率模块的实证贡献','',
      '三个独立种子的270格Stage2中，三个消融与1.7.7动作/G/C/K/base全部一致；重复轮也一致。全Stage聚合的消融差异来自Stage1，Stage1未使用这些概率决策，不能将其收益归因模型。',
      '各新模型臂Stage2的Probe层执行48次额外当前地点Sense；SDK完整动作流为450次Sense、0次Ask。两者统计范围不同。组合因unverified_storage回退618次，移动探测constraint_safety_unknown拒绝1386次，Ask候选nonpositive_answer_branch_value拒绝822次。它们是重复相关的内部事件，不是独立样本。',
      '本轮没有足够实际询问来评估询问后验的收益。未执行候选没有反馈标签，不能宣称校准完成。结论限于本轮新题：新增模型尚未产生有效决策收益，不能推导概率方法普遍无用。','',
      '## 稳定性、内部判断与截止','',
      '原始及实验默认各320项检查、四模式专项检查及8组默认动作/基础指标等价通过；这些检查覆盖已有断言，不代表复杂场景的时间行为完全相等。']
    lines+=['','| 对照 | 首种子重复比较次数 | 动作改变 | G改变 |','|---|---:|---:|---:|']
    for arm in names:
        p=facts['repeats'][arm];lines.append('| {} | {} | {} | {} |'.format(names[arm],p['pairs'],p['action_changes'],p['goal_changes']))
    lines+=['','新题重复轮中两版1.6.7的180格动作和G均一致；1.7.7有11格动作、10格G改变，均来自Stage1。墙钟搜索截止仍使固定种子不能保证相同路线。重复轮不加入独立种子置信区间。',
      '内部完成判断与SDK的逐题差异见RUNS.csv及SUMMARY.json。内部少计可能是证据不足；内部高计也需要区分绑定与真实事实问题，不能仅凭一个计数自动定因。官方目标ID和原始反馈见OFFICIAL_IDS.csv、DECISION_DIVERGENCES.csv。','',
      '全部SDK硬截止记录如下；即使已有评分，也保留其截止性质：']
    for r in rr:
        v=r['result']
        if v.get('platform_timed_out') or v.get('external_timeout'):
            lines.append('- `{}`：SDK截止={}，外部超时={}，正式分={}，G={}，base={}。'.format(r['key'],bool(v.get('platform_timed_out')),bool(v.get('external_timeout')),v.get('official_score'),v.get('final_goals'),v.get('base')))
    lines+=['','## 非法题与历史异常','',
      '非法题及历史02/04/05均不计入能力汇总。5道格式/指令错误与5道IT/NT语义不一致逐项记录预期层和实际执行；机器人只能检查实际收到的表示，跨表示一致性由题库/运行器负责。SDK接受并执行某些错误题，不意味着错误题变成合法能力样本。','',
      '| 题目 | 预期错误层 | 模式 | 对照 | 状态 | 实际动作数 | 正式分 | 基础真值 |','|---|---|---|---|---|---:|---:|---:|']
    expected=json.loads((OUT.parents[1]/'题目/independent_100_20261004/invalid/expected_errors.json').read_text(encoding='utf8'))
    expected={x['id']:x for x in expected}
    for r in rr:
        if r['suite']!='invalid':continue
        v=r['result'];lines.append('| {} | {} | {} | {} | {} | {} | {} | {} |'.format(r['id'],expected[r['id']]['expected_layer'],r['mode'],names[r['arm']],v['status'],len(v['action_sequence']),v.get('official_score'),v.get('base')))
    lines+=['','历史02/04/05的18次核查仍没有SDK终态目标标签；0分保留，基础分保持缺失，原排除理由保留。不得把缺失基础分补成0，也不得并入排名。','',
      '## 关键退化与完善优先级','',
      '新题A01-02-s1的已验证实例：1.7.7执行Move3→Open5→TakeOut14,5→Move5→PutDown14后停止，G3/C30/K14/base706，SDK正式分792，耗时0.635秒；内部尚余4366ms。单任务为负，组合以search_incomplete_or_timeout回退。200ms基线继续运输、存放、关门、携带与返回，正式分876。首动作差异是定位入口，关键阻断是后续丢弃组合并停止。',
      'P0：保留已验证完整组合、固定搜索工作量、按任务依赖筛选已确认子集。P1：统一逐动作许可/反馈收据、未知槽位与柜门的合规反馈路线、任务完成与恢复策略。P2：持久联合后验、完整分支收益、概率校准与独立耗时预算。每项触发场景、代码原因、修法和验收用例见OPTIMIZATION_PLAN.md，代码审计见CODE_AUDIT.md。',
      '用户随后授权在独立实验副本执行完整概率优化。原审核正式代码继续冻结；新优化的成绩须另行验证，不回写本轮结果，也不创建1.7.8。当前100题将成为开发回归题，泛化结论需要新的独立留出结构题。','',
      '## 交付、检查与复现','',
      '- 题库：题目/independent_100_20261004，中文题卡100份，作者参考及取舍比较方案。',
      '- RUNS.csv、PAIRS.csv、STRATA.csv：逐题、配对与Stage/ITNT/题型/种子分层；REGRESSIONS.csv保留全部得分、目标或约束退化及成本/耗时增长。',
      '- CONFIDENCE.json：按场景聚类，反事实关联场景同组，重复轮排除；原始指标和缺失标记不丢弃。',
      '- TRACE_AUDIT.json及相关表：SDK目标ID、失败反馈、费用交叉核对与首分叉；首分叉不自动构成模块因果证据。',
      '- EVIDENCE_MANIFEST.json：全部运行、参考、默认等价、作者失败草稿、编译失败、源及工具归档；每个压缩条目核对CRC和SHA256。SDK共享文件、编译二进制以哈希和配方引用。',
      '- POSTPROCESS_REPAIR.json：冻结分析工具遇到“已评分但终态标签缺失”时的修正收据；原工具字节保留，运行数据未变。',
      '- frozen-audit.json与final-audit.json：执行前冻结和执行后核对。experiment/diff-receipt.json属于早期准备快照，最终编译消融以冻结收据和build.json为准。','',
      '相关构建、运行、分析失败均保留。作者参考成功不替代机器人自主能力，模型内部推断不替代SDK终态。']
    (OUT/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    (OUT/'LIVE_REPORT.md').write_text('# 审核矩阵已完成\n\n6726/6726次，最终汇总见[REPORT.md](REPORT.md)，新题专题见[NEW100_RESULTS.md](NEW100_RESULTS.md)。\n',encoding='utf8')
    print('FINAL REPORT',audit['runs'],'runs',trace['pairs'],'trace pairs')

if __name__=='__main__':main()
