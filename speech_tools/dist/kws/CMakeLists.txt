cmake_minimum_required(VERSION 3.1)

project(KaldiLattice)

set(CMAKE_CXX_STANDARD 98)
set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -s")
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR})

set(SOURCE_FILES src/iterate_all.cpp src/lattice.cpp src/Lexicon.cpp src/main.cpp)

add_executable(KaldiLattice ${SOURCE_FILES})
set_target_properties(KaldiLattice PROPERTIES LINK_FLAGS "-static")

