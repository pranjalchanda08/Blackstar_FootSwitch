cmake_minimum_required(VERSION 3.10)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

project (blackstar_foot_switch VERSION 1.0)
set(target footswitch)

add_executable(${target}
    blackstar.c
    )

target_include_directories(${target} PUBLIC
    ../inc
    )

find_library(MYLIB hidapi-hidraw)
target_link_libraries( ${target} PUBLIC ${MYLIB})
