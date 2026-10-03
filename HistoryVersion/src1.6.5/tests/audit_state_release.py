#!/usr/bin/env python3
"""Check final build, SDK, cases and LF word list against release evidence."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
release = root / "src1.6.5/test-results/validation-20260928"
build = json.loads((release / "build.json").read_text(encoding="utf-8"))
baseline = json.loads((root / "src1.6.4/test-results/validation-20260927/src1.6.4-build.json").read_text(encoding="utf-8"))
digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
source = root / "src1.6.5"
source_matches = all(digest(source / name) == value for name, value in build["source_sha256"].items())
sdk_matches = build["sdk_sha256"] == baseline["sdk_sha256"]
baseline_binary = Path("/tmp/rdfw-164-release-final-prebuild/build-src1.6.4/example")
current_binary = Path(build["command"][build["command"].index("-o") + 1])
baseline_binary_matches = digest(baseline_binary) == baseline["executable_sha256"]
current_binary_matches = digest(current_binary) == build["executable_sha256"]
words_lf = b"\r" not in (source / "words.txt").read_bytes()
case_checks = []
for suite in ("full-release", "target-release-r1", "target-release-r2",
              "target-release-r3", "off-release"):
    rows = json.loads((release / (suite + "-results.json")).read_text(encoding="utf-8"))
    case_checks.extend(digest(Path(row["case"])) == row["case_sha256"] for row in rows)
audit = dict(source_matches_build=source_matches, sdk_matches_baseline=sdk_matches,
             baseline_binary_matches_release=baseline_binary_matches,
             current_binary_matches_build=current_binary_matches,
             words_lf=words_lf, case_hashes_valid=all(case_checks), cases=len(case_checks))
(release / "audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
print(audit)
assert all((source_matches, sdk_matches, baseline_binary_matches,
            current_binary_matches, words_lf, all(case_checks)))
