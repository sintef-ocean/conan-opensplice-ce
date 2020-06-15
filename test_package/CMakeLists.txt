cmake_minimum_required(VERSION 3.11)
project(test)

include("${CMAKE_BINARY_DIR}/conan_paths.cmake")
find_package(OpenSplice REQUIRED)

set(idlGenDir "${CMAKE_BINARY_DIR}/idlgen")
OpenSplice_generate_isocpp2("${CMAKE_SOURCE_DIR}/Test.idl" "${idlGenDir}" ddsSources)

add_executable(test test.cpp ${ddsSources})
target_link_libraries(test PRIVATE "OpenSplice::isocpp2")
target_include_directories(test PRIVATE "${idlGenDir}")
if(MSVC)
    # Suppress some warnings that we have no control over.
    target_compile_options(test PRIVATE "/wd4251" "/wd4267")
endif()
