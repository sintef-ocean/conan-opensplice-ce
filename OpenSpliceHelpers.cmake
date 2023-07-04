
if(DEFINED ENV{OSPL_HOME})
  set(OSPL_HOME "$ENV{OSPL_HOME}")
else()
  message(${OpenSplice_MESSAGE_MODE} "Conan: OpenSplice: Did you forget to include VirtualBuildEnv in your conanfile?")
  get_filename_component(OSPL_HOME "${CMAKE_CURRENT_LIST_DIR}/../" ABSOLUTE)
endif()

if(EXISTS "${OSPL_HOME}/bin/dcpssacsAssembly.dll")
  if(NOT TARGET "OpenSplice::sacs")
    add_library("OpenSplice::sacs" SHARED IMPORTED)
    message(${OpenSplice_MESSAGE_MODE} "Conan: Component target declared 'OpenSplice::sacs'")
  endif()
  string(TOUPPER ${CMAKE_BUILD_TYPE} SUFFIX) # Does not handle multiconfig!
  set_target_properties("OpenSplice::sacs" PROPERTIES
    IMPORTED_COMMON_LANGUAGE_RUNTIME_${SUFFIX} "CSharp"
    IMPORTED_LOCATION_${SUFFIX} "${OSPL_HOME}/bin/dcpssacsAssembly.dll")
endif()

if(NOT TARGET "OpenSplice:idlpp")
  add_executable("OpenSplice::idlpp" IMPORTED)
  set_property(TARGET "OpenSplice::idlpp" PROPERTY
    IMPORTED_LOCATION "${OSPL_HOME}/bin/idlpp")
 message(${OpenSplice_MESSAGE_MODE} "Conan: Executable target declared 'OpenSplice::idlpp'")
endif()

function(OpenSplice_generate_isocpp idlFile outputDir sourceFilesVar)
  get_filename_component(baseName "${idlFile}" NAME_WE)
  set(sourceFiles
    "${outputDir}/${baseName}.cpp"
    "${outputDir}/${baseName}.h"
    "${outputDir}/${baseName}Dcps.cpp"
    "${outputDir}/${baseName}Dcps.h"
    "${outputDir}/${baseName}Dcps_impl.cpp"
    "${outputDir}/${baseName}Dcps_impl.h"
    "${outputDir}/${baseName}SplDcps.cpp"
    "${outputDir}/${baseName}SplDcps.h"
    "${outputDir}/${baseName}_DCPS.hpp")
  add_custom_command(
    OUTPUT ${sourceFiles}
    COMMAND "OpenSplice::idlpp" "-S" "-l" "isocpp" "-d" "${outputDir}" "${idlFile}"
    MAIN_DEPENDENCY "${idlFile}"
    VERBATIM)
  set(${sourceFilesVar} ${sourceFiles} PARENT_SCOPE)
endfunction()

function(OpenSplice_generate_isocpp2 idlFile outputDir sourceFilesVar)
  get_filename_component(baseName "${idlFile}" NAME_WE)
  set(sourceFiles
    "${outputDir}/${baseName}.cpp"
    "${outputDir}/${baseName}.h"
    "${outputDir}/${baseName}SplDcps.cpp"
    "${outputDir}/${baseName}SplDcps.h"
    "${outputDir}/${baseName}_DCPS.hpp")
  add_custom_command(
    OUTPUT ${sourceFiles}
    COMMAND "OpenSplice::idlpp" "-S" "-l" "isocpp2" "-d" "${outputDir}" "${idlFile}"
    MAIN_DEPENDENCY "${idlFile}"
    VERBATIM)
  set(${sourceFilesVar} ${sourceFiles} PARENT_SCOPE)
endfunction()

if(TARGET "OpenSplice::sacs")
  function(OpenSplice_generate_sacs idlFile outputDir sourceFilesVar)
    get_filename_component(baseName "${idlFile}" NAME_WE)
    set(sourceFiles
      "${outputDir}/${baseName}.cs"
      "${outputDir}/I${baseName}Dcps.cs"
      "${outputDir}/${baseName}Dcps.cs"
      "${outputDir}/${baseName}SplDcps.cs")
    add_custom_command(
      OUTPUT ${sourceFiles}
      COMMAND "OpenSplice::idlpp" "-S" "-l" "cs" "-d" "${outputDir}" "${idlFile}"
      MAIN_DEPENDENCY "${idlFile}"
      VERBATIM)
    set(${sourceFilesVar} ${sourceFiles} PARENT_SCOPE)
  endfunction()
endif()
