"""Update repository entry and required work log from the final report."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'validation/review177-20261004'
def main():
    assert (OUT/'REPORT.md').exists()
    summary=json.loads((OUT/'SUMMARY.json').read_text(encoding='utf8'))
    audit=json.loads((OUT/'checks/staged-publication-audit.json').read_text(encoding='utf8'))
    names={'old':'24旧题','seen175':'12已见175题','seen176':'8已见176题','holdout177':'8新增177题','competition':'6比赛样本','stage1_control':'4个Stage1控制'}
    entry=['## 2026-10-04：src1.7.7 可见性概率、独立 at 与探索损失','',
    '- 基线：从已提交 1.7.6（567619fe366537ff890ac6b2971b7b67dfc9bff7）独立复制，分支 feat/v1.7.7-visibility-probability；保留全部旧版。upstream/main 为 4b0f3f3e8f0f777be3bf184a149572a22f03d31e。按此前明确授权同步完成的开发检查点到 codex-cloud-20261003，发布前后核对远端，不强推。',
    '- 代码：区分独立 SDK at 与路线可见地点，UNKNOWN/无at/地点0分别保存；按成功物理动作更新，失败不确认，参与投影/事务/缓存。模拟 Sense 采用 at、全部正 inside、槽位的可见并集；PickUp 和零动作送达不把已确认无at的开柜可见当作独立at。探索扣每项预测终态损失40分，多正确询问顺序未知时拒绝该项概率估价。',
    '- 概率：物理 Probe 接入最多32个局部联合可见性场景，保留residual、输出上下界、使用下界。公开 Sense 条件化采用保守包络，支持缺失保留未知；内核增加事件去重和似然校验。覆盖常量.75/.5为查看新题机器人成绩前冻结的开发假设，未校准。当前概率是可见性机会，expected_gain仍是部分启发式，不是任务完成概率或完整收益下界。',
    '- 新题：8道/4族/每题6目标，独立ID/地点/顺序，生成器不看规划器成绩。第一作者预检k03a NT在5秒只完成12/16动作，G3；同IT用4.645秒完成。此时0规划器运行。保留全部初稿输入/工具/10次预检记录；统一把书初始at放书桌作为已满足控制，缩短四族参考路径，保留相应inside。最终16次参考均真实G6/C0、约定动作/费用、无SDK或外部截止；不供机器人，不证明最优。',
    '- 检查：最终320/320普通与直接SDK（29项直接SDK，5.99秒）、291/291 ASan/UBSan/泄漏（23.74秒，不含SDK子进程）。新增16项可见性/概率/终态检查，六项已有SDK关系测试增逐动作Sense比较。新增终态捷径用例先失败后修正；前序编译/单测失败及草稿290项内存日志保留，草稿不作最终证据。79个最终检查相关文件冻结与发布核对。',
    '- 协议：旧/已见175/已见176各第一种子IT/NT两版176次；新177和预选六题比赛两种子IT/NT两版112次；四个Stage1控制第一种子IT/NT两版16次，共304次/152对。5秒、串行轮换，参与字节与二进制前后固定，无并行构建，不重跑替换不利格。']
    for suite,name in names.items():
        g=summary['suites'][suite];a,b=g['src1.7.6'],g['src1.7.7'];d=g['delta']
        entry.append('- {}（{}对）：基础分 {}→{}（{:+d}）、正式分 {}→{}（{:+d}）、G {}→{}（{:+d}）、C {}→{}、K {}→{}（{:+d}）、秒数 {:.3f}→{:.3f}（{:+.3f}）、硬截止 {}→{}。'.format(name,a['runs'],a['base'],b['base'],d['base'],a['official_score'],b['official_score'],d['official_score'],a['goals'],b['goals'],d['goals'],a['constraints'],b['constraints'],a['cost'],b['cost'],d['cost'],a['seconds'],b['seconds'],d['seconds'],a['sdk_timeouts'],b['sdk_timeouts']))
    entry+=['- 真实退化：正式分上涨不表示完成更多任务。逐动作原因见TRACE_ANALYSIS.md；严格独立at门槛下缺少不确定拿取的完整成功/失败分支，恢复路线仍不闭合，部分送达被放弃。未知门、双槽和耗时预留仍有缺口，不能靠恢复错误事实/调大信息价值解决。此版本为开发检查点，不宣称完整联合概率模型通过或全面恢复历史比赛能力。',
    '- 证据：validation/review177-20261004完整报告/逐格/退化/Probe审计/Stage1审计及五个逐项CRC/SHA证据包，另存原预检输入/工具和68个最终冻结输入/工具的精确字节。发布核对{}个文件，{}个Git字节完全一致（本版79个检查相关文件），{}个历史换行差异单列保留，不改历史文件。'.format(len(audit['expected_sha256']),audit['exact_git_and_workspace_files'],len(audit['historical_git_line_ending_differences'])),
    '- 后续：补持久联合动作后验、不确定拿取/门/多答案反馈路线、完成并返回的完整收益、概率与动作耗时校准，用新独立结构题和全比赛回归。当前联合策略内核仍未替换生产。GitHub固定源码再次复核，未复制外部代码/增加运行时；真实14步流程、版本新增表与校准步骤位于src1.7.7/docs。','']
    log=ROOT/'2026工作日志/工作日志.md';s=log.read_text(encoding='utf8');assert '## 2026-10-04：src1.7.7' not in s
    s=s.replace('# 2026 工作日志\n', '# 2026 工作日志\n\n'+'\n'.join(entry)+'\n',1);log.write_text(s,encoding='utf8')
    readme=ROOT/'README.md';s=readme.read_text(encoding='utf8')
    s=s.replace('└── src1.7.6/','├── src1.7.6/')
    marker='├── src1.7.6/              # src 1.7.6：生产多容器关系与公开失败反馈\n'
    assert marker in s;s=s.replace(marker,marker+'└── src1.7.7/              # src 1.7.7：可见性概率区间、独立at与探索损失\n')
    entry='最新开发检查点：`src1.7.7/`，生产观察使用有限联合可见性场景、概率区间和未覆盖质量，\n公开反馈条件更新；新增独立 at 证据，修正共存可见性模拟、完成捷径和探索目标损失。\n320/320 普通及直接 SDK、291/291 内存检查，304 次真实配对见\n[本轮报告与全部退化](validation/review177-20261004/REPORT.md)。部分题正式分提高但目标减少，\n完整联合动作策略和概率/耗时校准仍未完成，不能仅按正式分认定能力提升。\n[模型边界](src1.7.7/docs/PROBABILITY_1.7.7.md)、[实际决策](src1.7.7/docs/ROBOT_FLOW_1.7.7.md)、\n[历次新增与后续路线](src1.7.7/docs/PROBABILITY_ROADMAP.md)。\n\n'
    assert '最新开发版本：`src1.7.6/`' in s
    s=s.replace('最新开发版本：`src1.7.6/`',entry+'上一开发版本：`src1.7.6/`',1);readme.write_text(s,encoding='utf8')
if __name__=='__main__':main()
