"""Read-only interim publication. Never ranks unfinished rounds together."""
from pathlib import Path
import json, collections
OUT=Path(__file__).resolve().parents[1]
def main():
    rows=[]
    for line in (OUT/'results.jsonl').read_text(encoding='utf8').splitlines():
        try: rows.append(json.loads(line))
        except json.JSONDecodeError: break
    counts=collections.Counter((r['suite'],r['round']) for r in rows)
    complete=[n for (s,n),c in counts.items() if s=='new' and c==1080]
    text=['# 1.7.7审核：阶段汇总', '',
          '这是运行中快照，不能替代完整矩阵报告。最终结果由REPORT.md、逐题表及所有失败记录给出。', '',
          '## 已完成验收', '',
          '- 独立100题生成：70全解、20取舍、10非法；90合法题含45组Stage1/Stage2配对，每题7目标、30不同约束、名义毛分880。',
          '- 静态/指南/结构审计5项通过；180个IT/NT参考执行通过后才冻结题库并开始机器人评测。',
          '- 原版及实验默认模式各320项检查通过；四模式专项检查通过；8组默认模式动作/G/C/K/base等价。',
          '- 原始比赛版本保持冻结，三个消融只存在独立副本。', '',
          f'## 运行进度：{len(rows)}/6726', '',
          '矩阵包含新题4320、历史71输入1704、已有52结构题624、非法题60、历史异常18。基础分/评分缺失和截止全部保留。', '',
          f'新题已完整运行的轮次：{complete}；尚未完成的轮次不混入下表。', '',
          '| 对照 | 已完成新题运行 | G合计 | 基础分已评分合计 | 封顶正式分已评分合计 | 缺失 | SDK截止 |',
          '|---|---:|---:|---:|---:|---:|---:|']
    for arm in ('167','167_200','177','neutral','no_ask','legacy_visibility'):
        part=[r['result'] for r in rows if r['suite']=='new' and r['round'] in complete and r['arm']==arm]
        total=lambda k:sum(r.get(k) or 0 for r in part)
        missing=sum(r.get('official_score') is None for r in part)
        text.append(f'| {arm} | {len(part)} | {total("final_goals")} | {total("base")} | {total("official_score")} | {missing} | {total("platform_timed_out")} |')
    text+=['', '## 已确认的审核方向', '',
           '确定信息Stage1也出现提前停止，须先审计组合搜索与继续路线。概率进入物理Probe的执行过滤，但其排序仍主要依赖类型/事实数；可见性机会不能解释成任务完成概率。',
           '三个独立种子的270组新Stage2中，1.7.7与三个消融的动作、G/C/K/base完全一致；没有执行Ask。本轮新题尚未显示概率模块的有效执行收益。Stage1消融间差异不能归因于只在Stage2使用的概率决策。' if len(complete)>=3 else '概率实证结论等待完整的新题轮次。', '',
           '优化顺序与验收用例见[OPTIMIZATION_PLAN.md](OPTIMIZATION_PLAN.md)。本轮不修改策略，也不创建新比赛版本。', '']
    (OUT/'LIVE_REPORT.md').write_text('\n'.join(text),encoding='utf8')
    print('Snapshot',len(rows),'complete new rounds',complete)
if __name__=='__main__':main()
