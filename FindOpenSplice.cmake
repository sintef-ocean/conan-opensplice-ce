# Find module for Vortex OpenSplice DDS (OSS edition)
#
# If successful, the script defines the following entities.
#
# IMPORTED targets:
#
#     OpenSplice::isocpp2
#
# Variables:
#
#     OpenSplice_FOUND
#     OpenSplice_IDLPP_BINARY
#     OpenSplice_INCLUDE_DIRS
#     OpenSplice_LIBRARIES     (= "OpenSplice::isocpp2")
#     OpenSplice_VERSION
#
# Functions:
#
#     OpenSplice_generate_isocpp2(<IDL file> <output directory> <variable for source file names>)
#
# ==============================================================================

# Checks that `osplHomeDir` is an OpenSplice installation directory for
# build configuration `config`, and if so, returns the OpenSplice version
# in a variable whose name is given by `versionVar`.
function(OpenSplice_check_dir osplHomeDir config versionVar)
    if(WIN32)
        set(releaseScript "release.bat")
    else()
        set(releaseScript "release.com")
    endif()
    file(READ "${osplHomeDir}/${releaseScript}" releaseScriptContents)
    string(REGEX MATCH
        "OpenSplice HDE Release ([0-9]+\\.[0-9]+\\.[0-9]+)OSS For ([a-z0-9_]+\\.[a-z0-9_]+(-[a-z0-9_]+)?),"
        match
        "${releaseScriptContents}")
    if("${CMAKE_MATCH_2}" STREQUAL "${config}")
        set(${versionVar} "${CMAKE_MATCH_1}" PARENT_SCOPE)
    else()
        set(${versionVar} "NOTFOUND" PARENT_SCOPE)
    endif()
endfunction()

# Configures all targets for build configuration `config`, assuming that
# `homeDir` actually contains the installed files for this configuration.
function(OpenSplice_configure_targets config homeDir)
    string(TOUPPER "${config}" configUpper)
    set(suffix "_${configUpper}")

    if(NOT TARGET "OpenSplice::isocpp2")
        add_library("OpenSplice::isocpp2" SHARED IMPORTED)
        set_property(TARGET "OpenSplice::isocpp2" PROPERTY INTERFACE_INCLUDE_DIRECTORIES
            "${homeDir}/include"
            "${homeDir}/include/sys"
            "${homeDir}/include/dcps/C++/isocpp2"
            "${homeDir}/include/dcps/C++/SACPP")
    endif()
    set_property(TARGET "OpenSplice::isocpp2" APPEND PROPERTY IMPORTED_CONFIGURATIONS "${configUpper}")
    if(WIN32)
        set_target_properties("OpenSplice::isocpp2" PROPERTIES
            IMPORTED_IMPLIB${SUFFIX} "${homeDir}/lib/dcpsisocpp2.lib"
            IMPORTED_LOCATION${SUFFIX} "${homeDir}/bin/dcpsisocpp2.dll")
    else()
        set_target_properties("OpenSplice::isocpp2" PROPERTIES
            IMPORTED_LOCATION${SUFFIX} "${homeDir}/lib/libdcpsisocpp2.so"
            IMPORTED_NO_SONAME${SUFFIX} TRUE)
        set_property(TARGET "OpenSplice::isocpp2" APPEND PROPERTY INTERFACE_LINK_LIBRARIES
            $<$<CONFIG:${config}>:"ddskernel">)
    endif()
endfunction()


if(NOT DEFINED OSPL_HOME)
    if(DEFINED ENV{OSPL_HOME})
        file(TO_CMAKE_PATH $ENV{OSPL_HOME} OSPL_HOME)
    endif(DEFINED ENV{OSPL_HOME})
endif(NOT DEFINED OSPL_HOME)

if(WIN32)
    if(CMAKE_SIZEOF_VOID_P EQUAL 8)
        set(OpenSplice_config "x86_64.win64")
    else()
        set(OpenSplice_config "x86.win32")
    endif()
else()
    if(CMAKE_SIZEOF_VOID_P EQUAL 8)
	    set(OpenSplice_config "x86_64.linux")
    else()
	    set(OpenSplice_config "x86.linux")
    endif()
endif(WIN32)

find_path(OpenSplice_HOME_RELEASE
    NAMES
        "include/dcps/C++/isocpp2/dds/dds.hpp"
    HINTS
        "${OSPL_HOME}"
    PATH_SUFFIXES
        "${OpenSplice_config}"
        "OpenSplice/${OpenSplice_config}"
)
mark_as_advanced(OpenSplice_HOME_RELEASE)
find_path(OpenSplice_HOME_DEBUG
    NAMES
        "include/dcps/C++/isocpp2/dds/dds.hpp"
    HINTS
        "${OSPL_HOME}"
    PATH_SUFFIXES
        "${OpenSplice_config}-debug"
        "OpenSplice/${OpenSplice_config}-debug"
)
mark_as_advanced(OpenSplice_HOME_DEBUG)
OpenSplice_check_dir("${OpenSplice_HOME_RELEASE}" "${OpenSplice_config}" OpenSplice_versionRelease)
OpenSplice_check_dir("${OpenSplice_HOME_DEBUG}" "${OpenSplice_config}-debug" OpenSplice_versionDebug)

if(OpenSplice_versionRelease OR OpenSplice_versionDebug)
    if(OpenSplice_versionRelease)
        OpenSplice_configure_targets("release" "${OpenSplice_HOME_RELEASE}")
        if(OpenSplice_versionDebug STREQUAL OpenSplice_versionRelease)
            OpenSplice_configure_targets("debug" "${OpenSplice_HOME_DEBUG}")
        endif()
        set(OpenSplice_VERSION "${OpenSplice_versionRelease}")
        set(OpenSplice_home "${OpenSplice_HOME_RELEASE}")
    else() # OpenSplice_versionDebug is set
        OpenSplice_configure_targets("debug" "${OpenSplice_HOME_DEBUG}")
        set(OpenSplice_VERSION "${OpenSplice_versionDebug}")
        set(OpenSplice_home "${OpenSplice_HOME_DEBUG}")
    endif()
    get_property(
        OpenSplice_INCLUDE_DIRS
        TARGET "OpenSplice::isocpp2"
        PROPERTY INTERFACE_INCLUDE_DIRECTORIES)
    set(OpenSplice_LIBRARIES "OpenSplice::isocpp2")
    set(OpenSplice_IDLPP_BINARY "${OpenSplice_home}/bin/idlpp")

    function(OpenSplice_generate_isocpp2 idlFile outputDir sourceFilesVar)
        get_filename_component(baseName "${idlFile}" NAME_WE)
        set(sourceFiles
            "${outputDir}/${baseName}.cpp"
            "${outputDir}/${baseName}.h"
            "${outputDir}/${baseName}SplDcps.cpp"
            "${outputDir}/${baseName}SplDcps.h"
            "${outputDir}/${baseName}_DCPS.hpp")
        
        if(WIN32)
            set(shell "cmd.exe")
            set(shellSwitch "/C")
            set(envCommand "\"${OpenSplice_home}/release.bat\"")
        else()
            set(shell "bash")
            set(shellSwitch "-c")
            set(envCommand "source \"${OpenSplice_home}/release.com\"")
        endif()
        set(idlppCommand "\"${OpenSplice_IDLPP_BINARY}\" -S -l isocpp2 -d \"${outputDir}\" \"${idlFile}\"")
        add_custom_command(
            OUTPUT ${sourceFiles}
            COMMAND "${shell}" "${shellSwitch}" "${envCommand} && ${idlppCommand}"
            MAIN_DEPENDENCY "${idlFile}"
            VERBATIM)
        set(${sourceFilesVar} ${sourceFiles} PARENT_SCOPE)
    endfunction()
endif()

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(OpenSplice DEFAULT_MSG
    OpenSplice_IDLPP_BINARY
    OpenSplice_INCLUDE_DIRS
    OpenSplice_LIBRARIES
    OpenSplice_VERSION)
