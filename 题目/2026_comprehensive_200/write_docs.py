#!/usr/bin/env python3
"""Render human-readable question cards and package the checked suite."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
import zipfile

sys.dont_write_bytecode = True
from offline_check import load_case, Term
from build_suite import SPECS

HERE = Path(__file__).resolve().parent
CN = dict(human='人', table='餐桌', desk='书桌', cupboard='碗柜', closet='衣柜',
          microwave='微波炉', refrigerator='冰箱', sofa='沙发', can='罐子', cup='杯子',
          book='书', bottle='瓶子', remotecontrol='遥控器', red='红色', white='白色',
          green='绿色', black='黑色', yellow='黄色', blue='蓝色')
TAG_NAMES = dict(E04='可见性判断', E05='查询信息价值', E07='最终双物体携带', E10='单条件翻转')


def save(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')


def noun(world, obj):
    o = world.objects[obj]
    return CN.get(o.get('color'), '') + CN[o['sort']] + f'（#{obj}）'


def meaning(w, t):
    n = [noun(w, x) for x in t.args]
    if t.kind == 'constraint' and t.inner == 'info':
        if t.pred == 'near': return f'{n[0]}与{n[1]}全程' + ('保持同位置' if t.positive else '不得处于同一位置')
        if t.pred == 'inside': return f'{n[0]}全程' + ('留在' if t.positive else '不得进入') + n[1]
        if t.pred == 'plate': return n[0] + ('全程在托盘上' if t.positive else '全程禁止上托盘')
        if t.pred in ('opened', 'closed'): return n[0] + ('全程保持' if t.positive else '全程不得处于') + ('打开' if t.pred == 'opened' else '关闭') + '状态'
    if t.pred == 'goto': s = '结束时机器人位于' + n[0] + '的位置'
    elif t.pred == 'pickup': s = '结束时携带' + n[0] + '（手或托盘）'
    elif t.pred == 'putdown': s = '结束时已放下' + n[0] + '（不在手或托盘上）'
    elif t.pred == 'puton': s = '把' + n[0] + '放到' + n[1] + '处'
    elif t.pred == 'putin': s = '把' + n[0] + '放入' + n[1]
    elif t.pred == 'takeout': s = '使' + n[0] + '最终离开' + n[1] + '内部'
    elif t.pred == 'give': s = '把' + n[1] + '交给' + n[0]
    elif t.pred == 'open': s = n[0] + '最终打开'
    elif t.pred == 'close': s = n[0] + '最终关闭'
    else: raise ValueError(t)
    return '全过程禁止：' + s if t.kind == 'constraint' else s


def action_text(w, action):
    op, *args = action
    if op == 'move':
        furniture = '、'.join(noun(w, i) for i, o in w.objects.items() if o['size'] == 'big' and w.at[i] == args[0])
        return f'移动到位置 {args[0]}（{furniture}）'
    if op == 'sense': return '观察当前位置；容器内部仅在容器打开时可见'
    if op == 'askloc': return '询问' + noun(w, args[0]) + '的位置（见证记录采用真值回答）'
    n = [noun(w, i) for i in args]
    verbs = dict(pickup='拾取', putdown='放下', toplate='放上托盘：', fromplate='从托盘拿到手中：', open='打开', close='关闭')
    if op in verbs: return verbs[op] + n[0]
    if op == 'putin': return '把' + n[0] + '放入' + n[1]
    if op == 'takeout': return '从' + n[1] + '取出' + n[0]
    raise ValueError(action)


def main():
    cat = json.loads((HERE / 'catalogue.json').read_text(encoding='utf-8'))
    report = json.loads((HERE / 'validation_report.json').read_text(encoding='utf-8'))
    assert report['status'] == 'passed' and report['passed_cases'] == 200
    basis = {}
    for relative in ('env-release-2026/bin/evaluate.lp', 'env-release-2026/bin/fortask.lp',
                     'env-release-2026/bin/forcons.lp', 'env-release-2026/src/evaluate.cpp'):
        source = HERE.parents[2] / relative
        if source.is_file(): basis[relative] = hashlib.sha256(source.read_bytes()).hexdigest()
    metadata_path = HERE / 'verification_scope.json'
    if basis or not metadata_path.exists():
        save(metadata_path, json.dumps(dict(mode='offline correctness checks only', platform_executed=False,
                     scores_measured=False, source_basis_sha256=basis, python_version=sys.version,
                     verifier_sha256=hashlib.sha256((HERE / 'offline_check.py').read_bytes()).hexdigest(),
                     generator_sha256=hashlib.sha256((HERE / 'build_suite.py').read_bytes()).hexdigest(),
                     scenario_sha256=hashlib.sha256((HERE / 'scenario_design.py').read_bytes()).hexdigest(),
                     guide_auditor_sha256=hashlib.sha256((HERE / 'guide_audit.py').read_bytes()).hexdigest(),
                     limitations=['controlled English grammar only', 'truth-informed witness, not a tested autonomous policy',
                                  'random answer sequences and platform runtime have not been exercised']),
                     ensure_ascii=False, indent=2) + '\n')
    entries = cat['cases']
    lookup = {e['id']: e for e in entries}
    results = {r['id']: r for r in report['results']}
    kind_cn = dict(full='全解题', tradeoff='策略取舍题', invalid='故意非法的校验用例')
    index = ['**200 题总览**', '', '每行对应同一真实场景的 Stage 1／Stage 2 两道题。点击题卡可审阅中文目标、约束、信息差异及参考动作。', '',
             '| 场景／中文题卡 | 主方向 | 性质 | 目标／约束 | 新增方向 | 两份 XML |',
             '|---|---|---|---:|---|---|']
    for entry in entries:
        if entry.get('stage') != 1: continue
        pair, cid = entry['pair_id'], entry['id']
        s2 = lookup[pair + '-s2']
        ref = json.loads((HERE / entry['reference']).read_text(encoding='utf-8'))
        parsed = load_case(HERE / entry['path'])
        w, terms = parsed['world'], parsed['terms']
        r = results[cid]
        tags = '、'.join(TAG_NAMES[t] for t in entry['tags']) or '基础复合方向'
        lines = [f'**{pair}：{entry["title"]}**', '',
                 f'{kind_cn[entry["kind"]]}；{entry["goals"]} 个目标＋{entry["constraints"]} 条约束＝{entry["nominal_gross"]} 分名义毛分；标签：{tags}。', '',
                 f'[Stage 1 XML](../{entry["path"]}) · [Stage 2 XML](../{s2["path"]}) · [结构化参考方案](../{entry["reference"]})', '',
                 '本题通过离线格式、受控英文语义、状态与动作前置条件检查。参考方案使用作者真值，证明场景可行性；未执行平台、未测比赛得分。', '',
                 '**真实初态。**机器人在位置 ' + str(w.robot) + '；手中：' + (noun(w, w.hand) if w.hand else '空')
                 + '；托盘：' + (noun(w, w.plate) if w.plate else '空') + '。', '',
                 '| 对象 | 真实位置／归属 | 门状态 |', '|---|---|---|']
        for obj, attrs in w.objects.items():
            place = '手中' if obj == w.hand else '托盘' if obj == w.plate else '在' + noun(w, w.inside[obj]) + '内' if obj in w.inside else '位置 ' + str(w.at[obj])
            door = ('打开' if obj in w.opened else '关闭') if attrs.get('type') == 'container' else '—'
            lines.append(f'| {noun(w, obj)} | {place} | {door} |')
        lines.extend(['', '**目标与约束。**目标检查最终状态；约束从初态起逐步维护，违约记录保留。★ 为核心约束。', '',
                      '| 编号 | 类型 | 中文含义 | 对应英文 |', '|---:|---|---|---|'])
        core = set(ref['focus']['core_constraint_ids'])
        for i, (t, c) in enumerate(zip(terms, ref['clauses']), 1):
            lines.append(f'| {i} | {"目标" if t.kind == "task" else "约束★" if i in core else "约束"} | {meaning(w, t)} | {c["english"]} |')
        perturb = s2['information_perturbation']
        lines.extend(['', '**Stage 2 信息变化。**真实环境与 Stage 1 完全相同；mis、err、ans 开关打开。', ''])
        for f in perturb['missing']: lines.append('- 隐藏真值：`(' + ' '.join(f) + ')`。')
        for correct, wrong in zip(perturb['true_facts'], perturb['false_facts']):
            lines.append('- 将真值 `(' + ' '.join(correct) + ')` 呈现为 `(' + ' '.join(wrong) + ')`。')
        lines.extend(['', '**离线参考方案与结果。**下面只报告目标和约束逻辑结果，不计算实际平台分数。', '',
                      '| 方案 | 用途 | 最终完成目标 | 过程违约条数 | 动作数 |', '|---|---|---:|---:|---:|'])
        for plan, checked in zip(ref['plans'], r['plans']):
            lines.append(f'| {plan["name"]} | {plan["role"]} | {checked["completed_goals"]}/{entry["goals"]} | {len(checked["violated_constraint_ids"])} | {checked["action_count"]} |')
        lines.extend(['', ref['proof']['statement'], '', '主方案的具体步骤：', '', '| 步骤 | 操作 |', '|---:|---|'])
        for step, act in enumerate(ref['plans'][0]['actions'], 1): lines.append(f'| {step} | {action_text(w, act)} |')
        lines.extend(['', '比较方案的完整动作和首个违约步骤见结构化参考方案与 validation_report.json。', ''])
        for tag, data in r['focus_checks'].items(): lines.append(f'- {TAG_NAMES[tag]}检查：`{json.dumps(data, ensure_ascii=False)}`。')
        matching = [p for p in cat['counterfactual_pairs'] if cid in p]
        if matching:
            other = next(x for x in matching[0] if x != cid)
            other_pair = lookup[other]['pair_id']
            lines.append(f'- 单条件翻转对照：[对照题 {other_pair}]({other_pair}.md)。除禁止上托盘的对象外，真实初态与其他条目相同。双方主方案对换后均会违约。')
        save(HERE / 'cards' / (pair + '.md'), '\n'.join(lines) + '\n')
        index.append(f'| [{pair}](cards/{pair}.md) | {entry["title"]} | {kind_cn[entry["kind"]]} | {entry["goals"]}/{entry["constraints"]} | {tags} | [S1]({entry["path"]}) · [S2]({s2["path"]}) |')
    index.extend(['', '**异常校验用例。**每题由一个正常母题单故障变异而来，预期结果是被指定层识别。', '',
                  '| 用例 | 母题 | 注入错误 | 预期识别层 |', '|---|---|---|---|'])
    for e in entries:
        if e['kind'] == 'invalid':
            index.append(f'| [{e["id"]}]({e["path"]}) | [{Path(e["source_path"]).stem}]({e["source_path"]}) | {e["mutation"]} | {e["expected_layer"]} |')
    save(HERE / '题目总览.md', '\n'.join(index) + '\n')

    summary = ['**离线正确性检查报告**', '',
               f'结果：{report["passed_cases"]}/200 用例符合各自预期。正常题通过正确性检查；20 道故意非法题均在预期层被识别。', '',
               '本次没有启动 cserver、ASP 求解器或参赛客户端，也没有平台得分。执行内容是 XML/IT/受控 NT 解析、真值一致性核对及本地动作前置条件和约束轨迹检查。', '',
               '| 检查项目 | 结果 |', '|---|---|',
               '| 正常 XML / IT / NT 对应 | 180 / 180 |',
               '| 出题指南独立逐项检查 | 180 / 180；详见出题指南复核报告.md |',
               '| 全解题参考方案：全部目标、全部约束 | 140 / 140 |',
               '| 取舍题：候选方案与结构性上界前提 | 40 / 40 |',
               '| 故意非法用例：预期层识别 | 20 / 20 |',
               '| Stage 1 / Stage 2 真值及指令一致 | 90 / 90 对 |',
               '| 单条件翻转与旧方案失效检查 | 8 / 8 对 |',
               f'| 最大估算报文 | {report["maximum_estimated_packet_bytes"]} 字节，小于 3900 字节门槛 |',
               '| 正常题名义毛分 | 每题 880–900，当前时间奖励上界约 100 |',
               '| 检查器语义与指南错误注入回归 | 20 项通过 |', '',
               '| 新增方向 | 覆盖文件数 |', '|---|---:|']
    for tag, count in report['focus_case_counts'].items(): summary.append(f'| {tag}：{TAG_NAMES[tag]} | {count} |')
    summary.extend(['', '可见性、查询价值和最终双携带各覆盖 20 份 XML；单条件翻转覆盖 16 份 XML、组成 8 对。覆盖数量按标签统计，可以与主类型交叉。', '',
                    '检查器基于当前仓库的动作与判定规则实现了本题库使用的子集。IT／NT 检查覆盖生成器的受控句式；Stage 2 随机问答分布、官方解析器运行表现及实际时间消耗未作实测。', '',
                    '取舍题的 880、860、800、820 等上界是目标与约束的逻辑毛分上界，不包含动作成本和时间奖励，不是平台实测成绩。', '',
                    '[完整机器可读报告](validation_report.json) · [逐题总览](题目总览.md)', ''])
    save(HERE / '检查报告.md', '\n'.join(summary))

    readme = ['**2026 综合 200 题：离线正确性检查版**', '',
              '已生成 200 份 XML：140 道可全解题、40 道策略取舍题、20 道故意非法校验用例。包含 90 个真实场景的 Stage 1／Stage 2 配对，以及 90 份中文题卡和结构化参考方案。', '',
              '正常题每题 7 个目标、30–31 条约束，目标与约束毛分为 880–900 分，为当前平台最多约 100 分的时间奖励预留空间，总分上界为 980–1000 分。本次仅作出题正确性检查，未启动平台或测分。', '',
              '[逐题总览与中文题卡](题目总览.md) · [本轮逐项复核与修订](出题指南复核报告.md) · [检查报告](检查报告.md) · [机器清单](catalogue.json)', '',
              '| 内容 | 位置 |', '|---|---|',
              '| Stage 1 完整信息题，90 份 | cases/stage1/ |',
              '| Stage 2 缺失／错误信息题，90 份 | cases/stage2/ |',
              '| 故意非法题，20 份；含预期错误清单 | invalid/ |',
              '| 中文题卡：初态、目标、约束、信息变化、主方案 | cards/ |',
              '| 主方案、反例／比较方案、核心约束、逻辑论证 | references/ |',
              '| 360 个 IT／NT 入口清单，尚未执行 | run_manifest.json |', '',
              '优先查看新增方向的代表题：', '',
              '- [A02-01：关闭容器中看不到物体，不等于物体不存在](cards/A02-01.md)。',
              '- [A01-01：先查询共享容器的位置，解除多个目标依赖](cards/A01-01.md)。',
              '- [D03-01：最终双物体携带，交付和关门提前完成](cards/D03-01.md)。',
              '- [B01-01](cards/B01-01.md) 与 [B01-02](cards/B01-02.md)：只交换禁止上托盘的对象，手与托盘分配随之交换。', '',
              '| 主类型 | 数量 | 目标／约束 |', '|---|---:|---:|']
    for cat_id, (title, g, c, _) in SPECS.items():
        counts = sorted({e['constraints'] for e in entries if e['category'] == cat_id})
        readme.append(f'| {cat_id} {title} | 10 | 7/{"–".join(map(str, counts))} |')
    readme.extend(['| X01 格式与指令错误 | 10 | 异常测试 |', '| X02 IT／NT 语义不一致 | 10 | 异常测试 |', '',
                   '离线检查方式（在本目录运行）：', '', '```powershell', 'python -B -m unittest -v test_offline_check.py test_guide_audit.py',
                   'python -B guide_audit.py', 'python -B offline_check.py', '```', '',
                   '需要按相同设计重新生成文件时：', '', '```powershell', 'python -B build_suite.py',
                   'python -B guide_audit.py', 'python -B offline_check.py', 'python -B write_docs.py', '```', '',
                   '生成器和检查器均不包含启动平台或客户端的操作。正常题参考方案使用作者真值；Stage 2 中的随机 unknown／错误回答只配置开关，未实测或强制具体回答序列。', '',
                   '本地检查覆盖全部 9 种目标动作：goto、pickup、putdown、puton、putin、takeout、give、open、close。任务按最终状态判定，过程中的约束违约会保留；pickup 目标允许手或托盘，最终必须在手的对象另有禁止上托盘约束。', ''])
    save(HERE / 'README.md', '\n'.join(readme))
    # Package only suite artifacts; no executables, runtime platform or result logs from other projects.
    zip_path = HERE.parent / '2026_comprehensive_200.zip'
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(HERE.rglob('*')):
            if path.is_file() and '__pycache__' not in path.parts:
                archive.write(path, path.relative_to(HERE.parent))
    with zipfile.ZipFile(zip_path) as archive:
        assert archive.testzip() is None
        assert sum(n.endswith('.xml') for n in archive.namelist()) == 200
    print(json.dumps(dict(cards=90, xml_files=200, archive_bytes=zip_path.stat().st_size,
                          archive_sha256=hashlib.sha256(zip_path.read_bytes()).hexdigest(),
                          platform_executed=False), indent=2))


if __name__ == '__main__':
    main()
