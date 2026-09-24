cmake_minimum_required(VERSION 3.10)
project(rdfw_local_tests LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
enable_testing()
get_filename_component(SOURCE_DIR ".." ABSOLUTE)
add_library(rdfw_test_core STATIC
    ../rdfw.cpp ../parser.cpp ../deadline_manager.cpp ../terminal_checker.cpp
    ../score_evaluator.cpp ../candidate_plan.cpp ../question_preflight.cpp)
target_include_directories(rdfw_test_core PUBLIC stubs "${SOURCE_DIR}")
foreach(test_name input_safety_tests three_a_tests question_preflight_tests legal_preservation_tests)
    add_executable(${test_name} "${test_name}.cpp")
    target_link_libraries(${test_name} rdfw_test_core)
    # These fixtures use assert, including setup expressions.
    target_compile_options(${test_name} PRIVATE -UNDEBUG)
    add_test(NAME ${test_name} COMMAND ${test_name} "${SOURCE_DIR}/words.txt")
endforeach()
