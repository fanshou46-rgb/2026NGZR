#!/usr/bin/env python3
"""Summarize paired official scores, actions, timeouts and action costs."""
import argparse
import json
import re
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    root = args.run
    rows = json.loads((root / "results.json").read_text(encoding="utf-8"))
    summary = dict(pairs=len(rows), identical_base=0, identical_actions=0,
                   identical_goals=0, identical_constraints=0,
                   official_score_differences=0, hard_timeouts=0,
                   action_cost_mismatches=0, action_cost_checks=0,
                   invalid=0, differences=[], official_differences=[])
    for row in rows:
        b, c = row["baseline"], row["current"]
        summary["identical_base"] += b["base"] == c["base"]
        summary["identical_actions"] += b["action_sequence"] == c["action_sequence"]
        summary["identical_goals"] += b["goals"] == c["goals"]
        summary["identical_constraints"] += b["constraints"] == c["constraints"]
        summary["official_score_differences"] += b["official"] != c["official"]
        if b["official"] != c["official"]:
            summary["official_differences"].append(dict(case=row["case"],
                stage=row["stage"], mode=row["mode"],
                official=[b["official"],c["official"]], base=[b["base"],c["base"]],
                seconds=[b["platform_seconds"],c["platform_seconds"]]))
        summary["hard_timeouts"] += bool(b["timed_out"]) + bool(c["timed_out"])
        summary["invalid"] += b["status"] != "ok" or c["status"] != "ok"
        for label, result in (("baseline", b), ("current", c)):
            client = (root / (Path(row["case"]).stem + "-s" + str(row["stage"]) +
                              "-" + row["mode"] + "-" + label) / "client.log")
            text = client.read_text(encoding="utf-8", errors="replace")
            costs = re.findall(r"\[3A\]\[final\][^\n]*action_cost=(\d+)", text)
            if costs and result["base"] is not None and result["goals"] is not None:
                summary["action_cost_checks"] += 1
                official_cost = 40 * result["goals"] + (
                    20 * result["constraints"] if result["goals"] else 0) - result["base"]
                summary["action_cost_mismatches"] += int(costs[-1]) != official_cost
        if b["base"] != c["base"] or b["action_sequence"] != c["action_sequence"]:
            actions_b, actions_c = b["action_sequence"], c["action_sequence"]
            prefix = 0
            for a, d in zip(actions_b, actions_c):
                if a != d:
                    break
                prefix += 1
            summary["differences"].append(dict(case=row["case"], stage=row["stage"],
                mode=row["mode"], base=[b["base"], c["base"]],
                common_action_prefix=prefix, action_counts=[len(actions_b), len(actions_c)],
                seconds=[b["platform_seconds"], c["platform_seconds"]]))
    (root / "summary.json").write_text(json.dumps(summary, indent=2,
        ensure_ascii=False), encoding="utf-8")
    assert summary["action_cost_checks"] == 2 * summary["pairs"]
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
