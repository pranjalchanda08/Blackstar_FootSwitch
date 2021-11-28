add_executable(${target}
    "main.c"
    "blackstar.c"
    "blackstar_def.c"
    )

target_include_directories(${target} PUBLIC
    "../inc"
    )

find_library(MYLIB hidapi-hidraw)
find_library(PTHREAD pthread)
find_library(WIREINGPI wiringPi)
target_link_libraries( ${target} PUBLIC 
                    ${PTHREAD}
                    ${MYLIB}
                    ${WIREINGPI})
