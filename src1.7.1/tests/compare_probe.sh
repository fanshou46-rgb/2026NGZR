#!/bin/bash
set -eu
TASK_TESTS=$(cd "$(dirname "$0")" && pwd)
exec python3 -B "$TASK_TESTS/run_probe_compare.py" "$@"
