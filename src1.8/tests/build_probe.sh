#!/bin/bash
set -eu
TASK_ROOT=$(cd "$(dirname "$0")/.." && pwd)
TASK_OUTPUT=${1:-/tmp/rdfw18-product-new}
TASK_SDK=${2:-/home/yifan/env-release-2026}
if [ -e "$TASK_OUTPUT" ]; then
  echo "Output already exists: $TASK_OUTPUT" >&2
  exit 1
fi
mkdir -p "$(dirname "$TASK_OUTPUT")"
g++ -std=c++11 -O2 -g -Wall -Wextra -I"$TASK_ROOT" \
  -I"$TASK_SDK/include" -I"$TASK_SDK/src" "$TASK_ROOT"/*.cpp \
  -L"$TASK_SDK/lib" -lframe -lutility -lboost_thread -lboost_system \
  -lboost_chrono -lboost_date_time -lboost_regex -lpthread -ldl -o "$TASK_OUTPUT"
echo "Built: $TASK_OUTPUT"
