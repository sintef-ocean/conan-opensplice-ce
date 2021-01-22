cmake_minimum_required(VERSION 3.13)
project(test)

include("${CMAKE_BINARY_DIR}/conan_paths.cmake")
find_package(OpenSplice REQUIRED)

set(idlGenDir "${CMAKE_BINARY_DIR}/idlgen")
OpenSplice_generate_isocpp2("${CMAKE_SOURCE_DIR}/Test.idl" "${idlGenDir}" ddsSources)

add_executable(test_prog test.cpp ${ddsSources})
target_link_libraries(test_prog PRIVATE "OpenSplice::isocpp2")
target_include_directories(test_prog PRIVATE "${idlGenDir}")
if(MSVC)
    # Suppress some warnings that we have no control over.
    target_compile_options(test_prog PRIVATE "/wd4251" "/wd4267")
endif()
