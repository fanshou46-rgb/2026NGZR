PROJECT(rdfw VERSION 1.7.6)
# 设置指定的C++编译器版本是必须的，如果不设置，或者为OFF，则指定版本不可用时，会使用上一版本。
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 指定为C++11 版本
set(CMAKE_CXX_STANDARD 11)

FILE(GLOB rdfw_SRCS
    rdfw.hpp
    debuglog.hpp
    parser.hpp
    deadline_manager.hpp
    terminal_checker.hpp
    score_evaluator.hpp
    candidate_plan.hpp
    belief_state.hpp
    task_group_search.hpp
    question_preflight.hpp
    state_mutation.cpp containment.cpp canonical_state.cpp rdfw.cpp probe_layer.cpp belief_state.cpp observation_model.cpp information_planner.cpp answer_planning.cpp joint_world.cpp
    deadline_manager.cpp
    terminal_checker.cpp
    legacy_priority.cpp
    score_evaluator.cpp
    candidate_plan.cpp
    task_group_search.cpp
    question_preflight.cpp
    main.cpp
    parser.cpp
)
SOURCE_GROUP("" FILES ${rdfw_SRCS})
ADD_EXECUTABLE(example ${rdfw_SRCS})

add_compile_options(-g  -Wall -O2)

ADD_DEPENDENCIES(example frame utility)
TARGET_LINK_LIBRARIES(example frame utility ${Boost_LIBRARIES})

option(BUILD_INPUT_SAFETY_TESTS "Build src1.6.6 input safety unit tests" OFF)
if(BUILD_INPUT_SAFETY_TESTS)
    ADD_EXECUTABLE(input_safety_tests
        tests/input_safety_tests.cpp
        state_mutation.cpp containment.cpp canonical_state.cpp rdfw.cpp probe_layer.cpp belief_state.cpp observation_model.cpp information_planner.cpp answer_planning.cpp joint_world.cpp parser.cpp deadline_manager.cpp terminal_checker.cpp legacy_priority.cpp
        score_evaluator.cpp candidate_plan.cpp task_group_search.cpp question_preflight.cpp)
    TARGET_INCLUDE_DIRECTORIES(input_safety_tests PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
    TARGET_LINK_LIBRARIES(input_safety_tests frame utility ${Boost_LIBRARIES})
endif()
