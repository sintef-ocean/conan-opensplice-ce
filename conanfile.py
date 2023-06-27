from os.path import join
from conan import ConanFile, conan_version
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.microsoft import VCVars
from conan.tools.files import copy, get, replace_in_file, patch
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path
from conan.tools.scm import Version
import os
import subprocess

required_conan_version = ">=1.54.0"


class OpenSpliceConan(ConanFile):
    name = "opensplice-ce"
    version = "6.9.210323"
    license = "Apache-2.0"
    description = \
        "Vortex OpenSplice Community Edition, an open-source "\
        "implementation of the OMG DDS standard"
    homepage = "https://github.com/ADLINK-IST/opensplice"
    url = "https://github.com/sintef-ocean/conan-opensplice.git"
    author = "SINTEF Ocean"
    topics = ("dds", "opensplice", "publish-subscribe", "pub-sub", "communication")

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "include_cs": [True, False]
    }
    default_options = {
        "include_cs": False,
    }
    package_type = "shared-library"

    _build_script = "build-opensplice.sh"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _ospl_platform(self):
        arch = self.settings.arch.value.lower()
        if self.settings.os == "Windows":
            system = "win64" if arch == "x86_64" else "win32"
        elif self.settings.os == "Android":
            system = "linux_android"
        else:
            system = self.settings.os.value.lower()

        if self.settings.compiler == "clang":
            extra = "_clang"
        else:
            extra = ""

        if arch == "armv7" or arch == "armv6":
            arch += "l"

        return arch + "." + system + extra

    def export_sources(self):
        copy(self, '*', join(self.recipe_folder, "patches"), join(self.export_sources_folder, "patches"))
        copy(self, '*', join(self.recipe_folder, "setup"), join(self.export_sources_folder, "setup"))
        copy(self, self._build_script, self.recipe_folder, self.export_sources_folder)
        os.chmod(join(self.export_sources_folder, self._build_script), 0o755)
        copy(self, "OpenSpliceHelpers.cmake", self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os != "Windows" and not is_msvc(self):
            del self.options.include_cs

    def compatibility(self):
        if self.settings.compiler == "msvc":
            com_ver = self.settings.compiler.version
            candidates = ("190", "191", "192", "193")
            greater_eq = []
            for c in candidates:
                if Version(com_ver) <= Version(c):
                    greater_eq.append(c)
            return [{"settings": [("compiler.version", v)]}
                    for v in greater_eq]


        if Version(conan_version).major < 2 and self.settings.compiler == "Visual Studio":
            com_ver = str(self.settings.compiler.toolset).replace("v", "")
            candidates = ("140", "141", "142", "143")
            greater_eq = []
            for c in candidates:
                if Version(com_ver) <= Version(c):
                    greater_eq.append("v" + c)
            return [{"settings": [("compiler.toolset", v)]}
                    for v in greater_eq]

    def layout(self):
        basic_layout(self, src_folder="src")

    def build_requirements(self):
        #self.tool_requires("libtool/2.4.7") # maybe not necessary
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
        if is_msvc(self):
            self.tool_requires("automake/1.16.5")

        self.tool_requires("flex/2.6.4")
        self.tool_requires("bison/3.8.2")
        # perl, bison, flex, gawk, zip, unzip, git

    def source(self):

        get(self, **self.conan_data["sources"][self.version], strip_root=True)

        replace_in_file(self, join(self.source_folder, 'setup',
                                           'x86_64.linux-default.mak'),
                              'c++0x', 'c++11')
        replace_in_file(self, join(self.source_folder, 'setup',
                                           'x86_64.linux_clang-default.mak'),
                              'c++0x', 'c++11')
        replace_in_file(self, join(self.source_folder, 'setup',
                                           'arm.linux_native-common.mak'),
                              'c++0x', 'c++11')

        # patch xtypes errors (remove if this gets fixed...)
        patch(self, patch_file=join('patches', 'TypeKind.hpp.patch'),
                    base_path=self.source_folder)

        # fix for gcc10, https://github.com/ADLINK-IST/opensplice/issues/169
        patchGCC10 = '0001-GCC-10-enforces-usage-of-externs-for-global-variable.patch'
        patch(self, patch_file=join('patches', patchGCC10),
                    base_path=self.source_folder)

        # Depend on build platform's odlpp and idlpp executables
        replace_in_file(self, join(self.source_folder, 'bin',
                                           'configure_functions'),
                              'SPLICE_EXEC_PATH="${OSPL_HOME}/exec/${SPLICE_TARGET}"',
                              'SPLICE_EXEC_PATH="${OSPL_HOME}/exec/${SPLICE_HOST}"')

        # Disable shared memory stuff on android
        replace_in_file(self, join(self.source_folder, 'src',
                                           'abstraction', 'os', 'linux',
                                           'code', 'os_sharedmem.c'),
                              '#include "os__sharedmem.h"',
                              '''\
#ifdef __ANDROID__
#define OS_SHAREDMEM_FILE_DISABLE
#define OS_SHAREDMEM_SEG_DISABLE
#else
#include "os__sharedmem.h"
#endif''')

        # "execinfo.h" is not available on android
        path_to_patch = join(self.source_folder, 'src',
                                     'services', 'ddsi2e', 'core')
        replace_in_file(self,
            join(path_to_patch, 'sysdeps.h'),
            'defined (OS_QNX_DEFS_H)',
            'defined (OS_QNX_DEFS_H) || defined(__ANDROID__)')

        replace_in_file(self,
            join(path_to_patch, 'sysdeps.c'),
            '__GNUC_PATCHLEVEL__) < 40100)',
            '__GNUC_PATCHLEVEL__) < 40100) || defined(__ANDROID__)')

        replace_in_file(self,
            join(self.source_folder, 'src', 'abstraction', 'os',
                         'posix', 'include', 'os_os_thread.h'),
            "#include <pthread.h>",
            '''#include <pthread.h>
int pthread_attr_setinheritsched (pthread_attr_t *attr, int inherit);''')

        replace_in_file(self,
            join(self.source_folder, 'src', 'api', 'dcps',
                         'isocpp2', 'include', 'dds', 'sub', 'detail',
                         'TDataReaderImpl.hpp'),
            'params.size()',
            'static_cast<os_uint32>(params.size())')

        # Add new configurations
        copy(self, "*", join(self.export_sources_folder, "setup"),
             join(self.source_folder, "setup"))

    def generate(self):

        if is_msvc(self):
            ms = VCVars(self)
            ms.generate()

        benv = VirtualBuildEnv(self)
        benv.generate()

        yes_no = lambda v: "yes" if v else "no"

        env = Environment()
        env.define("OVERRIDE_INCLUDE_JAVA", "no")
        env.define("OVERRIDE_INCLUDE_ORB", "no")
        env.define("OVERRIDE_INCLUDE_CS", "no")
        env.define("OSPL_DOCS", "none")
        env.define("OSPL_USE_CXX11", "yes")

        if is_msvc(self):
            # get compile & ar-lib from automake (or eventually lib source code if available)
            # it's not always required to wrap CC, CXX & AR with these scripts, it depends on how much love was put in
            # upstream build files
            automake_conf = self.dependencies.build["automake"].conf_info
            compile_wrapper = unix_path(self, automake_conf.get("user.automake:compile-wrapper", check_type=str))
            ar_wrapper = unix_path(self, automake_conf.get("user.automake:lib-wrapper", check_type=str))
            env.define("CC", f"{compile_wrapper} cl -nologo")
            env.define("CXX", f"{compile_wrapper} cl -nologo")
            env.define("LD", "link -nologo")
            env.define("AR", f"{ar_wrapper} \"lib -nologo\"")
            env.define("NM", "dumpbin -symbols")
            env.define("OBJDUMP", ":")
            env.define("RANLIB", ":")
            env.define("STRIP", ":")
            env.define("DISTUTILS_USE_SDK", "1")
            env.define("OVERRIDE_INCLUDE_CS", yes_no(self.options.include_cs))
            env.unset("tmp")
            env.unset("temp")
            env.unset("TMP")
            env.unset("TEMP")

            benvvars = benv.vars(self, scope="build")
            env.define("VS_HOME", benvvars.get("VSINSTALLDIR"))
            env.define("WINDOWSSDKDIR", benvvars.get("WindowsSdkDir"))

        env.vars(self).save_script("conanbuild_custom")

    def build(self):

        config = "dev" if self.settings.build_type == "Debug" else "release"
        jobs = self.conf.get('tools.build:jobs')
        if not jobs:
            jobs = os.cpu_count()

        self.run(f"./{self._build_script} {self.source_folder} {self._ospl_platform}-{config} {jobs}", cwd=self.export_sources_folder)

    def package(self):

        suffix = "-dev" if self.settings.build_type == "Debug" else ""
        src_dir = join(self.source_folder, "install", "HDE", self._ospl_platform + suffix)

        to_package = [("include", "include"), ("bin", "bin"), ("lib", "lib"), ("etc", "etc"), ("share", "tools")]
        for item in to_package:
            copy(self, "*", dst=join(self.package_folder, item[0]), src=join(src_dir, item[1]))

        copy(self,
             "release.bat" if self.settings.os == "Windows" else "release.com",
             src=src_dir, dst=self.package_folder)
        copy(self, "LICENSE",
             src=self.source_folder,
             dst=join(self.package_folder, "licenses"))
        copy(self, "OpenSpliceHelpers.cmake",
             src=self.export_sources_folder,
             dst=join(self.package_folder, "cmake"))

    def package_info(self):

        self.cpp_info.set_property("cmake_file_name", "OpenSplice")
        self.cpp_info.set_property("cmake_target_name", "OpenSplice::OpenSplice")
        self.cpp_info.set_property("cmake_build_modules", [os.path.join("cmake", "OpenSpliceHelpers.cmake")])


        self.cpp_info.components["ddskernel"].includedirs = ["include", "include/sys"]
        self.cpp_info.components["ddskernel"].libs = ["ddskernel"]
        self.cpp_info.components["ddskernel"].set_property("cmake_target_name", "OpenSplice::ddskernel")
        self.cpp_info.components["ddskernel"].set_property("nosoname", True)
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["ddskernel"].system_libs = ["m", "dl", "pthread", "rt"]

        self.cpp_info.components["dcpssacpp"].includedirs = ["include/dcps/C++/SACPP"]
        self.cpp_info.components["dcpssacpp"].libs = ["dcpssacpp"]
        self.cpp_info.components["dcpssacpp"].set_property("cmake_target_name", "OpenSplice::dcpssacpp")
        self.cpp_info.components["dcpssacpp"].set_property("nosoname", True)
        self.cpp_info.components["dcpssacpp"].requires = ["ddskernel"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["dcpssacpp"].system_libs = ["m"]

        self.cpp_info.components["isocpp"].includedirs = ["include/dcps/C++/isocpp"]
        self.cpp_info.components["isocpp"].libs = ["dcpsisocpp"]
        self.cpp_info.components["isocpp"].set_property("cmake_target_name", "OpenSplice::isocpp")
        self.cpp_info.components["isocpp"].set_property("nosoname", True)
        self.cpp_info.components["isocpp"].requires = ["dcpssacpp"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["isocpp"].system_libs = ["m"]

        self.cpp_info.components["isocpp2"].includedirs = ["include/dcps/C++/isocpp2"]
        self.cpp_info.components["isocpp2"].libs = ["dcpsisocpp2"]
        self.cpp_info.components["isocpp2"].set_property("cmake_target_name", "OpenSplice::isocpp2")
        self.cpp_info.components["isocpp2"].set_property("nosoname", True)
        self.cpp_info.components["isocpp2"].requires = ["dcpssacpp"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["isocpp2"].system_libs = ["m"]


        # To be loaded with dlopen or similar
        modules = ["ddsi2", "spliced", "durability"]
        for module in modules:
            self.cpp_info.components[module].libs = [module]
            self.cpp_info.components[module].set_property("cmake_target_name", f"OpenSplice::{module}")
            # These target are defined to allow automatic bundling in downstream projects
            # Are IMPORTED_IMPLIB{CONFIG} is set properly on Windows?

        # Note: C-interface not added.
        # Note: CSharp OpenSplice::sacs is handled in OpenSpliceHelper.cmake, a build_module which is included by default

        envs = [
            ("PATH", join(self.package_folder, "bin"), "prepend_path"),
            ("LD_LIBRARY_PATH", join(self.package_folder, "lib"), "prepend_path"),
            ("DYLD_LIBRARY_PATH", join(self.package_folder, "lib"), "prepend_path"),
            ("OSPL_HOME", self.package_folder, "define"),
            ("OSPL_URI", "file://" + join(self.package_folder, "etc", "config", "ospl.xml"), "define"),
            ("OSPL_TMPL_PATH", join(self.package_folder, "etc", "idlpp"), "define")
        ]
        # prepend CPATH with? OSPL_HOME/{include, include/sys} ?

        for env in envs:
            if env[2] == "prepend_path":
                self.buildenv_info.prepend_path(env[0], env[1])
                # PATH, *LD_LIBRARY_PATH are automatically added to runenv_info
            if env[2] == "define":
                self.buildenv_info.define(env[0], env[1])
                self.runenv_info.define(env[0], env[1])
