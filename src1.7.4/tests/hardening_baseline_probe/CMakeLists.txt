cmake_minimum_required(VERSION 3.10)
project(hardening_baseline LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 11)
get_filename_component(BASELINE "${CMAKE_CURRENT_SOURCE_DIR}/../../../src1.6.6" ABSOLUTE)
get_filename_component(CURRENT "${CMAKE_CURRENT_SOURCE_DIR}/../.." ABSOLUTE)
add_library(baseline_core STATIC
    ${BASELINE}/canonical_state.cpp ${BASELINE}/rdfw.cpp ${BASELINE}/parser.cpp
    ${BASELINE}/deadline_manager.cpp ${BASELINE}/terminal_checker.cpp
    ${BASELINE}/legacy_priority.cpp ${BASELINE}/score_evaluator.cpp
    ${BASELINE}/candidate_plan.cpp ${BASELINE}/task_group_search.cpp ${BASELINE}/question_preflight.cpp)
target_include_directories(baseline_core PUBLIC ${CURRENT}/tests/stubs ${BASELINE})
add_executable(mutation_failure_tests ../mutation_failure_tests.cpp)
target_compile_options(mutation_failure_tests PRIVATE -UNDEBUG)
target_link_libraries(mutation_failure_tests baseline_core)
file(COPY ${BASELINE}/words.txt DESTINATION ${CMAKE_CURRENT_BINARY_DIR})
add_executable(state_profile ../state_profile.cpp)
target_link_libraries(state_profile baseline_core)
target_compile_options(state_profile PRIVATE -UNDEBUG)
add_executable(deadline_sensitivity_tests ../deadline_sensitivity_tests.cpp)
target_link_libraries(deadline_sensitivity_tests baseline_core)
target_compile_options(deadline_sensitivity_tests PRIVATE -UNDEBUG)
