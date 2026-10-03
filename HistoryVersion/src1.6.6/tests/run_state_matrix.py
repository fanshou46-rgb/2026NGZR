#!/usr/bin/env python3
"""Replay the preserved release matrix against an independently built 1.6.6."""
import argparse
import json
import sys
sys.dont_write_bytecode = True
from pathlib import Path

from run_guarded_compare import main as compare_main


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("matrix", choices=("full", "target", "off"))
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--current", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed-library", type=Path, required=True)
    parser.add_argument("--repeat", type=int, default=1)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    old = root / "src1.6.4/test-results/validation-20260927"
    rows = json.loads((old / (args.matrix + "-results.json")).read_text(encoding="utf-8"))
    cases = []
    for row in rows:
        if row["mode"] != "it" or row.get("repeat", 1) != args.repeat:
            continue
        case = Path(row["case"])
        if not case.exists():
            case = root / "题目/OurTest" / case.parent.name / case.name
        assert case.exists(), case
        cases.append(str(row["stage"]) + ":" + str(case))
    assert cases
    sys.argv = [sys.argv[0], "--sdk", "/home/yifan/env-release-2026",
                "--runner", str(root / "HistoryVersion/src1.1.2 (x)/tools/baseline.py"),
                "--baseline", str(args.baseline), "--current", str(args.current),
                "--words", str(root / "src1.6.6/words.txt"),
                "--output", str(args.output), "--seed-library", str(args.seed_library),
                "--seed", "20260924", "--baseline-mode", "guarded",
                "--current-mode", "off" if args.matrix == "off" else "guarded"] + cases + ["--modes", "it", "nt"]
    if args.matrix == "off":
        sys.argv[sys.argv.index("--baseline-mode") + 1] = "off"
    compare_main()


if __name__ == "__main__":
    main()
