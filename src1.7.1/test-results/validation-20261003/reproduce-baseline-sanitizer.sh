#!/bin/bash
set -eu
TASK_ROOT=$(pwd)
TASK_BUILD=/tmp/rdfw17-sanitizer-startup-reproduction-20261003
cmake "-H$TASK_ROOT/src1.7/tests" "-B$TASK_BUILD" -DCMAKE_BUILD_TYPE=Debug \
  '-DCMAKE_CXX_FLAGS=-fsanitize=address,undefined -fno-omit-frame-pointer' \
  '-DCMAKE_EXE_LINKER_FLAGS=-fsanitize=address,undefined'
cmake --build "$TASK_BUILD" -- -j3
(cd "$TASK_BUILD" && ASAN_OPTIONS=detect_leaks=1 UBSAN_OPTIONS=halt_on_error=1 ctest --output-on-failure)
