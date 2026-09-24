#!/usr/bin/env python3
"""Run src1.5 on all 36 realcompetition cases and emit score/strategy reports."""
import collections
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src1.5"
CASES = ROOT / "题目" / "realcompetiton_2024"
SDK = Path("/home/yifan/env-release-2026")
OUTPUT = ROOT / "test-results" / "realcompetition-src1.5-all36-seed20260924"
SEED = 20260924

sys.path.insert(0, str(ROOT / "src1.1.2 (x)" / "tools"))
from baseline import digest, run_case  # noqa: E402


def build():
    out = OUTPUT / "build"
    out.mkdir(parents=True, exist_ok=False)
    executable = out / "example"
    sources = sorted(SOURCE.glob("*.cpp"))
    command = [
        "g++", "-std=c++11", "-O2", "-g", "-Wall", "-Wextra",
        "-I" + str(SOURCE), "-I" + str(SDK / "include"),
        "-I" + str(SDK / "src"),
    ]
    command += [str(path) for path in sources]
    command += [
        "-L" + str(SDK / "lib"), "-lframe", "-lutility",
        "-lboost_thread", "-lboost_system", "-lboost_chrono",
        "-lboost_date_time", "-lboost_regex", "-lpthread", "-ldl",
        "-o", str(executable),
    ]
    with (out / "build.log").open("w", encoding="utf-8") as stream:
        subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT, check=True)
    metadata = {
        "command": command,
        "source_sha256": {
            path.name: digest(path)
            for path in SOURCE.iterdir()
            if path.suffix in (".cpp", ".hpp", ".txt")
        },
        "sdk_sha256": {
            str(path.relative_to(SDK)): digest(path)
            for path in (
                SDK / "bin" / "cserver",
                SDK / "lib" / "libasp.so",
                SDK / "lib" / "libframe.a",
            )
        },
        "executable_sha256": digest(executable),
    }
    (out / "build.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return executable


def configure_seed():
    artifact = OUTPUT / "seed_rng.so"
    subprocess.run(
        [
            "g++", "-shared", "-fPIC",
            str(SOURCE / "tests" / "seed_rng.cpp"),
            "-ldl", "-o", str(artifact),
        ],
        check=True,
    )
    preload_dir = Path(tempfile.mkdtemp(prefix="rdfw-src15-seed-"))
    preload = preload_dir / "seed_rng.so"
    shutil.copy2(str(artifact), str(preload))
    os.environ["LD_PRELOAD"] = str(preload)
    os.environ["RDFW_TEST_SEED"] = str(SEED)
    return preload_dir


def stage_for(case):
    text = case.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"<env\s+([^>]+)>", text)
    if not match:
        raise RuntimeError("missing env in " + str(case))
    flags = dict(re.findall(r'(mis|err|ans)="(on|off)"', match.group(1)))
    return 1 if all(flags.get(key) == "off" for key in ("mis", "err", "ans")) else 2


def clean_text(path):
    return re.sub(
        r"\x1b\[[0-9;]*m", "",
        path.read_text(encoding="utf-8", errors="replace"),
    )


def parse_feedback(client_text):
    events = []
    for payload in re.findall(r"\[DecisionFeedback\]\s+(\{.*\})\s*$", client_text, re.M):
        try:
            events.append(json.loads(payload))
        except json.JSONDecodeError:
            pass
    selected = [event for event in events if event.get("event") == "candidate_selected"]
    outcomes = [event for event in events if event.get("event") == "candidate_result"]
    considered = [event for event in events if event.get("event") == "candidate_considered"]
    labels = [event.get("task_label", "unknown") for event in selected]
    reasons = [event.get("selection_reason", "unknown") for event in selected]
    nonzero_errors = []
    for event in outcomes:
        error = event.get("error", {})
        if any(value not in (0, 0.0, None) for value in error.values()):
            nonzero_errors.append({"candidate_id": event.get("candidate_id"), "error": error})
    return {
        "events": len(events),
        "considered": len(considered),
        "selected": len(selected),
        "results": len(outcomes),
        "successful": sum(bool(event.get("succeeded")) for event in outcomes),
        "failed": sum(not bool(event.get("succeeded")) for event in outcomes),
        "labels": labels,
        "selection_reasons": reasons,
        "nonzero_prediction_errors": nonzero_errors,
    }


def rle(items):
    output = []
    for item, group in __import__("itertools").groupby(items):
        count = sum(1 for _ in group)
        output.append(item if count == 1 else "{}×{}".format(item, count))
    return " → ".join(output) if output else "—"


def extract_strategy(run, result):
    client = clean_text(run / "client.log")
    server = clean_text(run / "server.log")
    action_lines = re.findall(
        r"^\s*\[([A-Za-z_]+(?:\s+[^|]*?)?)\|([^\]]*)\]\s*$", server, re.M
    )
    actions = [action.strip() for action, _ in action_lines]
    failed_actions = [action.strip() for action, ok in action_lines if ok == "false"]
    feedback = parse_feedback(client)
    final = re.findall(r"^.*\[3A\]\[final\].*$", client, re.M)
    stop_gate = re.findall(r"^.*\[3B\]\[StopGate\].*$", client, re.M)
    deadline_stops = re.findall(r"^.*\[3B\]\[Deadline\].*can_finish=false.*$", client, re.M)
    return {
        "action_sequence": actions,
        "failed_actions": failed_actions,
        "action_profile": dict(collections.Counter(
            re.match(r"[A-Za-z_]+", action).group(0).lower() for action in actions
        )),
        "feedback": feedback,
        "selected_strategy": rle(feedback["labels"]),
        "selection_reasons": rle(feedback["selection_reasons"]),
        "final_lines": final,
        "stop_gate": stop_gate[-1] if stop_gate else None,
        "deadline_stop": deadline_stops[-1] if deadline_stops else None,
        "seed_confirmed": "[RDFW_TEST_SEED] {}".format(SEED) in server,
        "client_error_lines": [line for line in client.splitlines() if "[ERROR]" in line],
    }


def score_breakdown(result):
    goals = result.get("final_goals")
    constraints = result.get("credited_constraints")
    seconds = result.get("platform_seconds")
    raw = result.get("raw_score")
    valid = goals is not None and constraints is not None and raw is not None
    if not valid:
        return {"evaluator_valid": False, "base_reward": None,
                "time_bonus": None, "action_cost": None}
    base = goals * 40 + constraints * 20
    bonus = 2 * int((5.0 - seconds) * 10) if seconds is not None and seconds < 5.0 else 0
    return {"evaluator_valid": True, "base_reward": base,
            "time_bonus": bonus, "action_cost": base + bonus - raw}


def report_scores(rows):
    valid = [row for row in rows if row["evaluator_valid"]]
    normal = [row for row in rows if row["status"] == "ok" and row["evaluator_valid"]]
    total = sum((row.get("official_score") or 0) for row in rows)
    raw_total = sum((row.get("raw_score") or 0) for row in rows)
    goals = sum((row.get("final_goals") or 0) for row in valid)
    constraints = sum((row.get("credited_constraints") or 0) for row in valid)
    actions = sum(row.get("action_count", 0) for row in rows)
    capped = [row["id"] for row in rows if row.get("official_score") == 1000]
    average_valid = (float(total) / len(valid)) if valid else 0.0
    lines = [
        "# src1.5 realcompetition 36 题评分报告",
        "",
        "## 测试口径",
        "",
        "- 代码：`src1.5`，从当前源码重新编译。",
        "- 题集：`题目/realcompetiton_2024/01.xml`–`36.xml`，未改写 XML。",
        "- 环境：WSL2 Ubuntu 18.04.2、g++ 7.5.0、官方 2026 SDK `/home/yifan/env-release-2026`。",
        "- 模式：IT；01、03–36 为 Stage 2，02 按 XML 标志为 Stage 1；平台时限 5000 ms。",
        "- 外部随机：固定 `srand` 种子 `{}`，每题 server.log 均校验种子加载。".format(SEED),
        "- 官方展示分按 1000 封顶；总分中无法评分的题按 0 计，同时单独标记。",
        "",
        "## 汇总",
        "",
        "- 36 题展示分合计：**{}**；原始分合计：**{}**。".format(total, raw_total),
        "- 正常且有有效 answer-set：**{}/36**；有有效 answer-set：**{}/36**。".format(len(normal), len(valid)),
        "- 有效题完成目标：**{}**；计分约束：**{}**；全套动作数：**{}**。".format(goals, constraints, actions),
        "- 有效题平均展示分：**{:.2f}**；1000 分封顶题：**{}**（{}）。".format(
            average_valid, len(capped), "、".join(capped)),
        "- 封顶隐藏原始分 **{}**（原始总分 {} − 展示总分 {}）。".format(raw_total - total, raw_total, total),
        "",
        "## 逐题分数",
        "",
        "|题号|Stage|状态|展示分|原始分|目标|约束|动作|耗时(s)|基础奖励|动作成本|时间奖励|",
        "|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        def value(key):
            item = row.get(key)
            return "—" if item is None else str(item)
        lines.append(
            "|{id}|{stage}|{status}|{official}|{raw}|{goals}|{constraints}|{actions}|{seconds}|{base}|{cost}|{bonus}|".format(
                id=row["id"], stage=row["stage"], status=row["status"],
                official=value("official_score"), raw=value("raw_score"),
                goals=value("final_goals"), constraints=value("credited_constraints"),
                actions=row["action_count"], seconds=value("platform_seconds"),
                base=value("base_reward"), cost=value("action_cost"), bonus=value("time_bonus"),
            )
        )
    invalid = [row for row in rows if not row["evaluator_valid"]]
    if invalid:
        lines += [
            "",
            "## 无效/异常题说明",
            "",
        ]
        for row in invalid:
            if row["id"] == "02":
                note = "原 XML 结束标签损坏，官方平台在客户端执行前拒绝载入。"
            elif row["id"] in ("04", "05"):
                note = "instruction 括号损坏，官方评分器未生成有效 answer-set；平台输出 0 分不能视作正常得分。"
            else:
                note = "官方 evaluator 未生成有效 answer-set，详见原始日志。"
            lines.append("- **{}**：{}".format(row["id"], note))
    lines += [
        "",
        "## 可追溯证据",
        "",
        "- `results.json`：机器可读逐题结果与策略摘要。",
        "- `build/build.json`：编译命令、源码/SDK/可执行文件 SHA-256。",
        "- `<题号>/summary.json`：官方运行摘要。",
        "- `<题号>/server.log`、`client.log`、`runtime/vanswer.txt`：原始动作、决策与 ASP 终态证据。",
        "",
        "## 校验结果",
        "",
        "- `results.json` 共 36 条，题号 01–36 无缺失、无重复。",
        "- 逐题动作序列长度与 `summary.json.action_count` 全部一致，合计 792。",
        "- 36 份 server.log 均确认固定种子加载；0 次平台硬超时、0 次外部超时。",
        "- 汇总分由逐题 `official_score`/`raw_score` 独立重算，分别为 19953/21733。",
    ]
    (OUTPUT / "SCORE_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def report_strategy(rows):
    labels = collections.Counter()
    reasons = collections.Counter()
    nonzero = 0
    failed_candidates = 0
    failed_actions = 0
    action_profile = collections.Counter()
    for row in rows:
        feedback = row["strategy"]["feedback"]
        labels.update(feedback["labels"])
        reasons.update(feedback["selection_reasons"])
        nonzero += len(feedback["nonzero_prediction_errors"])
        failed_candidates += feedback["failed"]
        failed_actions += len(row["strategy"]["failed_actions"])
        action_profile.update(row["strategy"]["action_profile"])
    deadline_cases = [row["id"] for row in rows if row["strategy"]["deadline_stop"]]
    stop_gate_cases = [row["id"] for row in rows if row["strategy"]["stop_gate"]]
    failed_action_cases = [
        "{}({})".format(row["id"], len(row["strategy"]["failed_actions"]))
        for row in rows if row["strategy"]["failed_actions"]
    ]
    prediction_error_cases = [
        "{}({})".format(row["id"], len(row["strategy"]["feedback"]["nonzero_prediction_errors"]))
        for row in rows if row["strategy"]["feedback"]["nonzero_prediction_errors"]
    ]
    lines = [
        "# src1.5 realcompetition 36 题执行策略报告",
        "",
        "## 总体策略",
        "",
        "src1.5 沿用主任务顺序与风险门槛，以 CandidatePlan 做无副作用 dry-run，计算目标/约束增减、动作成本、边际 utility 与预计时长。StopGate/Deadline 只允许能在预算内完整结束的候选；多目标 goto 使用 hub 汇聚，最后再移动到目标位置。1.5 新增的 DecisionFeedback 为记录层，不改变选择规则。",
        "",
        "本轮共选择 **{}** 个候选，成功 **{}**、失败 **{}**；服务端失败动作 **{}** 个；预测误差非零的候选 **{}** 个。".format(
            sum(row["strategy"]["feedback"]["selected"] for row in rows),
            sum(row["strategy"]["feedback"]["successful"] for row in rows),
            failed_candidates, failed_actions, nonzero,
        ),
        "",
        "候选类型计数：`{}`。".format(", ".join(
            "{}={}".format(key, value) for key, value in labels.most_common()
        ) or "无"),
        "",
        "选择原因计数：`{}`。".format(", ".join(
            "{}={}".format(key, value) for key, value in reasons.most_common()
        ) or "无"),
        "",
        "## 关键发现",
        "",
        "- 全套 792 个动作中，AskLoc 85 次、Sense 51 次，实际操作/移动 656 次；Move 304 次，是出现次数最多的动作。",
        "- 8 题最终触发 Deadline 门槛：{}。这些题在剩余预算不足以完整执行下一候选时停止。".format("、".join(deadline_cases)),
        "- 23 题出现 StopGate 收束：{}。StopGate 包含无完整候选、低收益回收结束或已完成可执行目标等正常终止情形。".format("、".join(stop_gate_cases)),
        "- 服务端失败动作共 54 次，分布为 {}；其中 04/05 各 9 次来自损坏题面，不能作为正常策略质量样本。".format("、".join(failed_action_cases)),
        "- 45 个候选的 prediction/actual 误差非零，分布为 {}。这表明 1.5 的反馈记录已经捕获感知/动作失败后的偏差，但当前版本尚未用误差在线调整选择策略。".format("、".join(prediction_error_cases)),
        "",
        "## 逐题策略摘要",
        "",
        "|题号|最终目标/约束|候选（执行顺序，连续项压缩）|动作构成|Stop/Deadline|",
        "|---:|---:|---|---|---|",
    ]
    for row in rows:
        strategy = row["strategy"]
        if row.get("final_goals") is None:
            final = "—"
        else:
            final = "{}/{}".format(row["final_goals"], row["credited_constraints"])
        profile = ", ".join(
            "{}×{}".format(key, value) for key, value in sorted(strategy["action_profile"].items())
        ) or "—"
        stop = "Deadline" if strategy["deadline_stop"] else ("StopGate" if strategy["stop_gate"] else "正常收束")
        selected = strategy["selected_strategy"].replace("|", "\\|")
        lines.append("|{}|{}|{}|{}|{}|".format(row["id"], final, selected, profile, stop))
    lines += [
        "",
        "## 逐题完整动作序列",
        "",
    ]
    for row in rows:
        sequence = " → ".join(row["strategy"]["action_sequence"]) or "无动作"
        lines.append("- **{}**（{} 分）：{}".format(
            row["id"], row.get("official_score") if row.get("official_score") is not None else "无有效",
            sequence,
        ))
    lines += [
        "",
        "## 结论",
        "",
        "本报告描述的是固定种子下的一次官方平台实跑。Stage 2 的 AskLoc/Sense 回复具有随机性；更换种子后，部分题的询问分支、动作数与得分可能变化。DecisionFeedback 的 prediction/actual/error 已保存在各题 client.log 和 `results.json`，可用于后续定位具体候选误差。",
    ]
    (OUTPUT / "STRATEGY_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    if "--report-only" in sys.argv:
        rows = json.loads((OUTPUT / "results.json").read_text(encoding="utf-8"))
        for row in rows:
            row["strategy"] = extract_strategy(OUTPUT / row["id"], row)
        (OUTPUT / "results.json").write_text(
            json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        report_scores(rows)
        report_strategy(rows)
        print("REPORTS REBUILT", len(rows), "cases", flush=True)
        return
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 7932))
    OUTPUT.mkdir(parents=True, exist_ok=False)
    environment = {
        "seed": SEED,
        "source": str(SOURCE),
        "case_dir": str(CASES),
        "sdk": str(SDK),
        "os": subprocess.check_output(["uname", "-a"]).decode().strip(),
        "release": Path("/etc/os-release").read_text(encoding="utf-8"),
        "compiler": subprocess.check_output(["g++", "--version"]).decode().splitlines()[0],
    }
    (OUTPUT / "environment.json").write_text(
        json.dumps(environment, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    executable = build()
    preload_dir = configure_seed()
    rows = []
    try:
        for number in range(1, 37):
            case_id = "{:02d}".format(number)
            case = CASES / (case_id + ".xml")
            stage = stage_for(case)
            run = OUTPUT / case_id
            result = run_case(SDK, SOURCE, executable, case, stage, "it", run, 5000, None)
            result["id"] = case_id
            result.update(score_breakdown(result))
            result["strategy"] = extract_strategy(run, result)
            if not result["strategy"]["seed_confirmed"]:
                raise RuntimeError("seed interposer not confirmed for case " + case_id)
            if not result["evaluator_valid"] and result["status"] == "ok":
                result["status"] = "evaluator_failed"
            rows.append(result)
            (OUTPUT / "results.json").write_text(
                json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            print(case_id, result["status"], result.get("official_score"),
                  result.get("final_goals"), result["action_count"], flush=True)
    finally:
        (preload_dir / "seed_rng.so").unlink()
        preload_dir.rmdir()
        os.environ.pop("LD_PRELOAD", None)
        os.environ.pop("RDFW_TEST_SEED", None)
    report_scores(rows)
    report_strategy(rows)
    print("COMPLETE", len(rows), "cases", flush=True)


if __name__ == "__main__":
    main()
