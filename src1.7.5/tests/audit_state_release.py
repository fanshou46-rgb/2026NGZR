#!/usr/bin/env python3
"""Check final build, SDK, cases and LF word list against release evidence."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
release = root / "src1.6.6/test-results/validation-20260928"
build = json.loads((release / "build.json").read_text(encoding="utf-8"))
baseline = json.loads((root / "src1.6.5/test-results/validation-20260928/build.json").read_text(encoding="utf-8"))
digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
source = root / "src1.6.6"
source_matches = all(digest(source / name) == value for name, value in build["source_sha256"].items())
sdk_matches = build["sdk_sha256"] == baseline["sdk_sha256"]
baseline_binary = Path("/tmp/rdfw-165-closure/build-release/example")
current_binary = Path(build["command"][build["command"].index("-o") + 1])
baseline_binary_matches = digest(baseline_binary) == baseline["executable_sha256"]
current_binary_matches = digest(current_binary) == build["executable_sha256"]
words_lf = b"\r" not in (source / "words.txt").read_bytes()
immutable = json.loads((source / 'docs/BASELINE_SHA256.json').read_text(encoding='utf-8'))
baseline_source_unchanged = all(digest(root / path.replace('\\', '/')) == value for path,value in immutable.items())
baseline_source_matches_release = all(digest(root / 'src1.6.5' / name)==value for name,value in baseline['source_sha256'].items())
actual_sdk_unchanged = all(digest(Path('/home/yifan/env-release-2026') / path)==value for path,value in baseline['sdk_sha256'].items())
case_checks = []
for suite in ("full-release", "target-release-r1", "target-release-r2",
              "target-release-r3", "off-release"):
    rows = json.loads((release / (suite + "-results.json")).read_text(encoding="utf-8"))
    case_checks.extend(digest(Path(row["case"])) == row["case_sha256"] for row in rows)
audit = dict(source_matches_build=source_matches, sdk_matches_baseline=sdk_matches,
             baseline_source_unchanged=baseline_source_unchanged,
             baseline_source_matches_release=baseline_source_matches_release,
             actual_sdk_unchanged=actual_sdk_unchanged,
             baseline_binary_matches_release=baseline_binary_matches,
             current_binary_matches_build=current_binary_matches,
             words_lf=words_lf, case_hashes_valid=all(case_checks), cases=len(case_checks))
control_file=release / 'deadline-variation.json'
if control_file.exists():
    control=json.loads(control_file.read_text(encoding='utf-8'))
    controls_valid=(control['baseline_binary_sha256']==baseline['executable_sha256']
        and len(control['controls'])==3 and all(
            digest(Path(row['case']))==row['case_sha256'] and all(
                row[label]['status']=='ok' and row[label]['seed_confirmed']
                for label in ('baseline','current')) for row in control['controls']))
    audit['deadline_controls_verified']=controls_valid
    assert controls_valid
(release / "audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
print(audit)
assert all((source_matches, sdk_matches, baseline_source_unchanged, baseline_source_matches_release,
            actual_sdk_unchanged, baseline_binary_matches,
            current_binary_matches, words_lf, all(case_checks)))
