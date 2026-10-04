cmake_minimum_required(VERSION 3.10)
project(canonical_baseline_probe LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 11)
enable_testing()
get_filename_component(BASELINE "${CMAKE_CURRENT_SOURCE_DIR}/../../../src1.6.5" ABSOLUTE)
get_filename_component(CURRENT "${CMAKE_CURRENT_SOURCE_DIR}/../.." ABSOLUTE)
add_library(probe_core STATIC
    ${BASELINE}/rdfw.cpp ${BASELINE}/parser.cpp ${BASELINE}/deadline_manager.cpp
    ${BASELINE}/terminal_checker.cpp ${BASELINE}/legacy_priority.cpp
    ${BASELINE}/score_evaluator.cpp ${BASELINE}/candidate_plan.cpp
    ${BASELINE}/task_group_search.cpp ${BASELINE}/question_preflight.cpp)
target_include_directories(probe_core PUBLIC ${CURRENT}/tests/stubs ${BASELINE})
add_executable(canonical_baseline_probe ../canonical_baseline_probe.cpp)
target_link_libraries(canonical_baseline_probe probe_core)
target_compile_options(canonical_baseline_probe PRIVATE -UNDEBUG)
file(COPY ${BASELINE}/words.txt DESTINATION ${CMAKE_CURRENT_BINARY_DIR})
foreach(case RANGE 0 13)
    add_test(NAME baseline_canonical_${case} COMMAND canonical_baseline_probe "${CMAKE_CURRENT_BINARY_DIR}/words.txt" ${case})
endforeach()
