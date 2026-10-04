#!/usr/bin/env python3
"""Aggregate the six instrumented 03/06/29 IT/NT platform runs."""
import json
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
rows = json.loads((root / "results.json").read_text(encoding="utf-8"))
summary = {}
for label in ("baseline", "current"):
    phases = {}
    for row in rows:
        path = root / (Path(row["case"]).stem + "-s" + str(row["stage"]) +
                       "-" + row["mode"] + "-" + label) / "client.log"
        text = path.read_text(encoding="utf-8", errors="replace")
        for name, calls, micros, maximum in re.findall(
                r"\[StageTiming\] phase=(\w+) calls=(\d+) us=(\d+) max_us=(\d+)", text):
            phase = phases.setdefault(name, dict(calls=0, microseconds=0,
                                                  max_microseconds=0))
            phase["calls"] += int(calls)
            phase["microseconds"] += int(micros)
            phase["max_microseconds"] = max(phase["max_microseconds"], int(maximum))
    summary[label] = phases
(root / "performance-summary.json").write_text(json.dumps(summary, indent=2),
                                                  encoding="utf-8")
for label, phases in summary.items():
    print(label, {name: phases.get(name) for name in
                  ("terminal", "projection", "state_update", "derived_invalidation")})
