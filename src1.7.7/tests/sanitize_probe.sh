#!/bin/bash
set -eu
TASK_ROOT=$(cd "$(dirname "$0")/.." && pwd)
TASK_BUILD=${1:-/tmp/rdfw177-sanitizer-nopie}
cmake "-H$TASK_ROOT/tests" "-B$TASK_BUILD" -DCMAKE_BUILD_TYPE=Debug \
  '-DCMAKE_CXX_FLAGS_DEBUG=-g -O2' \
  '-DCMAKE_CXX_FLAGS=-fsanitize=address,undefined -fno-omit-frame-pointer -fno-pie' \
  '-DCMAKE_EXE_LINKER_FLAGS=-fsanitize=address,undefined -no-pie'
cmake --build "$TASK_BUILD" -- -j3
(cd "$TASK_BUILD" && ASAN_OPTIONS=detect_leaks=1 UBSAN_OPTIONS=halt_on_error=1 ctest --output-on-failure)
