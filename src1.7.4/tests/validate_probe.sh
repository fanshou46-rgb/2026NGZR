#!/bin/bash
set -eu
TASK_ROOT=$(cd "$(dirname "$0")/.." && pwd)
TASK_BUILD=${1:-/tmp/rdfw171-unit-20261003}
cmake "-H$TASK_ROOT/tests" "-B$TASK_BUILD" -DCMAKE_BUILD_TYPE=Release -DOFFICIAL_SDK=/home/yifan/env-release-2026
cmake --build "$TASK_BUILD" -- -j3
(cd "$TASK_BUILD" && ctest --output-on-failure)
