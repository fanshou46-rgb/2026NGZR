#!/usr/bin/env python3
"""Copy final validation summaries and bounded raw evidence into this version."""
import argparse
import json
import shutil
import zipfile
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=Path, required=True)
    parser.add_argument("--unit", type=Path, required=True)
    parser.add_argument("--asan", type=Path, required=True)
    parser.add_argument("--unit-summary", type=Path, required=True)
    parser.add_argument("--asan-summary", type=Path, required=True)
    args = parser.parse_args()
    destination = Path(__file__).resolve().parents[1] / "test-results/validation-20260928"
    destination.mkdir(parents=True, exist_ok=True)
    suites = ["full-release", "target-release-r1", "target-release-r2",
              "target-release-r3", "off-release", "perf-target"]
    for suite in suites:
        source = args.runs / suite
        for name in ("results.json", "summary.json", "performance-summary.json"):
            item = source / name
            if item.exists():
                shutil.copy2(str(item), str(destination / (suite + "-" + name)))
        with zipfile.ZipFile(str(destination / (suite + "-evidence.zip")), "w",
                             compression=zipfile.ZIP_DEFLATED) as archive:
            for name in ("server.log", "client.log", "runtime/vanswer.txt"):
                for item in sorted(source.glob("*/" + name)):
                    archive.write(str(item), str(item.relative_to(source)))
    for name, source in (("build.json", args.runs / "build-release/build.json"),
                         ("build.log", args.runs / "build-release/build.log"),
                         ("ctest-summary.log", args.unit_summary),
                         ("asan-summary.log", args.asan_summary),
                         ("ctest.log", args.unit / "Testing/Temporary/LastTest.log"),
                         ("asan-ctest.log", args.asan / "Testing/Temporary/LastTest.log")):
        shutil.copy2(str(source), str(destination / name))
    summaries = [json.loads((destination / (suite + "-summary.json")).read_text(
        encoding="utf-8")) for suite in suites[:5]]
    combined = {"pairs": sum(s["pairs"] for s in summaries),
                "identical_base": sum(s["identical_base"] for s in summaries),
                "identical_actions": sum(s["identical_actions"] for s in summaries),
                "identical_goals": sum(s["identical_goals"] for s in summaries),
                "identical_constraints": sum(s["identical_constraints"] for s in summaries),
                "invalid": sum(s["invalid"] for s in summaries),
                "official_score_differences": sum(s["official_score_differences"] for s in summaries),
                "hard_timeouts": sum(s["hard_timeouts"] for s in summaries),
                "action_cost_mismatches": sum(s["action_cost_mismatches"] for s in summaries),
                "action_cost_checks": sum(s["action_cost_checks"] for s in summaries)}
    (destination / "summary.json").write_text(json.dumps(combined, indent=2),
                                                encoding="utf-8")
    print(destination, combined)


if __name__ == "__main__":
    main()
