cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(OpenSplice CONFIG REQUIRED)

set(idlGenDir "${CMAKE_BINARY_DIR}/idlgen")
OpenSplice_generate_isocpp2("${CMAKE_SOURCE_DIR}/Testing.idl" "${idlGenDir}" ddsSources)

add_executable(test_prog tester.cpp ${ddsSources})

target_link_libraries(test_prog PRIVATE OpenSplice::OpenSplice)
#target_compile_definitions(test_prog PRIVATE OSPL_DDS_CXX11)

target_include_directories(test_prog PRIVATE "${idlGenDir}")
if(MSVC)
    # Suppress some warnings that we have no control over.
    target_compile_options(test_prog PRIVATE "/wd4251" "/wd4267")
endif()
