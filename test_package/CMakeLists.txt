cmake_minimum_required(VERSION 3.11)
project(test)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup()
message(STATUS "foo ${CMAKE_MODULE_PATH}")
find_package(OpenSplice REQUIRED)

set(idlGenDir "${CMAKE_BINARY_DIR}/idlgen")
OpenSplice_generate_isocpp2("${CMAKE_SOURCE_DIR}/Test.idl" "${idlGenDir}" ddsSources)

add_executable(test test.cpp ${ddsSources})
target_link_libraries(test PUBLIC "OpenSplice::isocpp2")
target_include_directories(test PUBLIC "${idlGenDir}")
