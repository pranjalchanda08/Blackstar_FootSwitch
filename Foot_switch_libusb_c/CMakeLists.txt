cmake_minimum_required(VERSION 3.10)
# set(CMAKE_CXX_STANDARD 17)
# set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_C_COMPILER "/usr/bin/gcc")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall" CACHE STRING "Default CXX options" FORCE)

project (blackstar_foot_switch VERSION 1.0)
set(target "footswitch")

add_subdirectory(src)