#!/usr/bin/env python3
"""Copy representative historical failures with source-byte provenance."""
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'logs/representative_failures'


def digest(data): return hashlib.sha256(data).hexdigest()


def save(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    samples = []
    def sample(name, category, phenomenon, conclusion, seed, sources, references):
        target = OUT / name; target.mkdir(exist_ok=True); entries = []; results = {}
        for label, rel in sources.items():
            original = ROOT / rel
            if original.is_dir():
                dest = target / label; dest.mkdir(exist_ok=True)
                for filename in ('server.log', 'client.log', 'summary.json'):
                    p = original / filename
                    if p.exists():
                        payload = p.read_bytes(); (dest / filename).write_bytes(payload)
                        entries.append({'source': p.relative_to(ROOT).as_posix(),
                                        'saved': (dest / filename).relative_to(ROOT).as_posix(),
                                        'sha256': digest(payload), 'bytes': len(payload)})
                if (original / 'summary.json').exists(): results[label] = json.loads((original / 'summary.json').read_text())
                runtime = original / 'runtime.zip'
                if runtime.exists():
                    with zipfile.ZipFile(runtime) as z:
                        assert z.testzip() is None
                        for member in z.namelist():
                            filename = member.split('/')[-1]
                            if filename not in ('vanswer.txt', 'vstate.lp', 'vcons.lp', 'vtask.lp', 'vaction.lp', 'case.xml'): continue
                            relative = member.removeprefix('runtime/').lstrip('/')
                            assert '..' not in relative.split('/')
                            p = dest / 'official_runtime' / relative; p.parent.mkdir(parents=True, exist_ok=True)
                            payload = z.read(member); p.write_bytes(payload)
                            entries.append({'source': runtime.relative_to(ROOT).as_posix(), 'member': member,
                                            'saved': p.relative_to(ROOT).as_posix(), 'sha256': digest(payload), 'bytes': len(payload)})
                else:
                    for filename in ('vanswer.txt', 'vstate.lp', 'vcons.lp', 'vtask.lp', 'vaction.lp', 'tests/case.xml'):
                        p = original / 'runtime' / filename
                        if p.exists():
                            payload = p.read_bytes(); q = dest / 'official_runtime' / filename; q.parent.mkdir(parents=True, exist_ok=True); q.write_bytes(payload)
                            entries.append({'source': p.relative_to(ROOT).as_posix(), 'saved': q.relative_to(ROOT).as_posix(), 'sha256': digest(payload), 'bytes': len(payload)})
            else:
                payload = original.read_bytes(); q = target / (label + original.suffix); q.write_bytes(payload)
                entries.append({'source': original.relative_to(ROOT).as_posix(), 'saved': q.relative_to(ROOT).as_posix(),
                                'sha256': digest(payload), 'bytes': len(payload)})
        meta = {'id': name, 'category': category, 'phenomenon': phenomenon, 'conclusion': conclusion,
                'seed': seed, 'references': references, 'runs': results, 'files': entries}
        save(target / 'CASE.json', meta); samples.append(meta)
    independent = 'validation/review177-100-20261004/runs/'
    sample('early-stop-A01-02', '提前停止', '1.7.7 在剩余约 4366ms 时停止，基线继续运输和关闭。',
           '日志确认组合因 search_incomplete_or_timeout 回退并停止；局部筛选与预算设计是后续修复入口。', 2026100403,
           {'candidate': independent + 'new-A01-02-s1-it-r1-177', 'baseline_200ms': independent + 'new-A01-02-s1-it-r1-167_200'},
           ['validation/review177-100-20261004/REPORT.md'])
    sample('sdk-deadline-j04b', 'SDK截止', '1.7.7 的 seen-j04b IT 第一轮触发 5000ms SDK 截止，评分仍有效。',
           '保留截止标志和完整动作；这是 1.7.7 超时样本，不是原 200ms 基线超时。', 2026100403,
           {'candidate': independent + 'seen-j04b-it-r1-177', 'baseline_200ms': independent + 'seen-j04b-it-r1-167_200'},
           ['validation/review177-100-20261004/REPORT.md'])
    recovery = 'validation/review176-20261004/raw/frozen-v2/runs/'
    sample('recovery-h03a', '恢复失败与内部高报', '1.7.5 内部高报 G6，SDK G5；1.7.6 修正关系后，额外探索移动丢掉 goto，SDK G4。',
           '完整收益遗漏已完成 goto 的损失；未知柜门与返回投影缺陷阻断恢复。原因由日志及独立 SDK 反例支持。', 2026100401,
           {'candidate_176': recovery + 'seen175-2026100401-h03a-it-src1.7.6', 'baseline_175': recovery + 'seen175-2026100401-h03a-it-src1.7.5'},
           ['validation/review176-20261004/REPORT.md'])
    semantic = 'validation/review-20261004/semantics/'
    sample('independent-inside-semantics', '事实终态误判', 'PickUp/PutDown 不自动删 inside；联合模型漏掉旧 inside 边。',
           '以官方 SDK 状态复现独立 at/inside、多父关系；按指定边更新关系。直接语义检查不使用题目随机种子。', None,
           {'results': semantic + 'results.json', 'multi_inside': semantic + 'results-multi.json',
            'sdk_log': semantic + 'v2-0/reproduction.log', 'counterexample': 'tools/review_172_174/semantic_counterexamples.cpp'},
           ['docs/AUDIT_1.7.2_1.7.4.md'])
    lab = 'experiments/full_probability/runs/'
    budget = json.loads((ROOT / 'experiments/full_probability/f29-smoke2-full-budget-evidence.json').read_text())
    worst = max(budget['rows'], key=lambda r: r['model_ns'])
    sample('model-budget-f29', '模型预算超限', 'f29 的累计模型工作超过 250ms 目标，最高 269.904959ms。',
           '完整时间账本显示检查通过仍有预算超限；该值是模型累计时间，区别于 200ms 规划余量。', 2026100403,
           {'candidate': lab + worst['key'], 'budget_audit': 'experiments/full_probability/f29-smoke2-full-budget-evidence.json'},
           ['experiments/full_probability/LATEST_RESULT.md'])
    sample('repeat-divergence-f29', '重复运行分叉', 'A01-01-s2 NT 同种子首轮与重复轮 G6→G7，费用 K74→K86。',
           '固定随机种子仍有公开历史后不同决策；工作配额与墙钟截断需要另行修复。重复轮用于稳定性检查。', 2026100403,
           {'first': lab + 'f29-smoke2-full-A01-01-s2-nt-repeat0-lab', 'repeat': lab + 'f29-smoke2-full-A01-01-s2-nt-repeat1-lab',
            'repeat_audit': 'experiments/full_probability/f29-smoke2-full-repeat-evidence.json'},
           ['experiments/full_probability/LATEST_RESULT.md'])
    checks = 'src1.6.7.1-200ms/test-results/comprehensive200-20261006/checks/'
    sample('sanitizer-incomplete-competition', 'sanitizer卡顿', '连续 CTest 不同生命周期用例 10 秒超时，input_safety 后续未完成。',
           '普通检查和正式 SDK 对照已通过；连续 sanitizer 检查保留未完成状态。无题目/模式/随机种子。', None,
           {'ctest': checks + 'rc1671-200-asan-ctest.log', 'except_input': checks + 'rc1671-200-asan-ctest-except-input.log',
            'initial_critical': checks + 'rc1671-200-asan-critical.log'},
           ['src1.6.7.1-200ms/docs/RELEASE_1.6.7.1-200ms.md'])
    for meta in samples:
        for item in meta['files']:
            assert digest((ROOT / item['saved']).read_bytes()) == item['sha256']
    save(OUT / 'INDEX.json', {'samples': samples, 'all_saved_sha256_verified': True})
    print('CURATED', len(samples), 'representative cases')


if __name__ == '__main__': main()
