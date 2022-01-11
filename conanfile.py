from conans import ConanFile, tools, __version__ as conan_version
from conans.client.conan_api import Conan
from conans.errors import ConanInvalidConfiguration
from conans.model.version import Version
from distutils.dir_util import copy_tree
import os
import shutil
import subprocess
import sys


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
    options = { "include_cs": [True, False] }
    default_options = {
        "include_cs": False,
        "cygwin_installer:additional_packages":
        "gcc-core,make,git,perl,bison,flex,gawk,zip,unzip",
        "cygwin_installer:with_pear": False
    }

    _build_script = "build-opensplice.sh"
    _build_android = "build-android.sh"
    _find_script = "FindOpenSplice.cmake"
    _source_subfolder = "source_subfolder"

    exports_sources = [_build_android, _build_script, _find_script, "patches/*", "setup/*"]

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

    def configure(self):
        if self.settings.compiler != "Visual Studio" and self.options.include_cs:
            raise ConanInvalidConfiguration("'include_cs' is only valid for compiler 'Visual Studio'")
        if self.settings.compiler != "Visual Studio":
            del self.options.include_cs
        if self.settings.os == "Android":
            if conan_version < Version("1.24"):
                raise ConanInvalidConfiguration(
                    "Building for Android requires conan >= 1.24")
            settings_build = getattr(self, 'settings_build', None)
            # TODO: this does not work:
            if settings_build and settings_build.os == "Windows":
                raise ConanInvalidConfiguration(
                    "Recipe not implemented for compilation of Android on Windows")
            if settings_build and settings_build.arch != "x86_64":
                raise ConanInvalidConfiguration(
                    "Recipe only implemented for x86_64 build platform for Android")

    def build_requirements(self):
        # Cygwin installer defective ATM!
        if self.settings.os == "Windows" and False:
            self.build_requires("cygwin_installer/2.9.0@bincrafters/stable")

        if self.settings.os == "Android":
            self.build_requires("android_ndk_installer/r21d@bincrafters/stable")

    def source(self):

        if self.settings.os == "Windows" and self.settings.compiler.version == 17:
            self.output.warn("Redistribute existing binary for this compiler")
            return

        revision = "OSPL_V" + self.version.replace(".", "_") + "OSS_RELEASE"
        url = "https://github.com/ADLINK-IST/opensplice/archive/" \
            + revision + ".tar.gz"
        tools.get(url)

        if(os.path.isdir(self._source_subfolder)):
            shutil.rmtree(self._source_subfolder)
        os.rename("opensplice-" + revision, self._source_subfolder)

        tools.replace_in_file(os.path.join(self._source_subfolder, 'setup',
                                           'x86_64.linux-default.mak'),
                              'c++0x', 'c++11')
        tools.replace_in_file(os.path.join(self._source_subfolder, 'setup',
                                           'x86_64.linux_clang-default.mak'),
                              'c++0x', 'c++11')
        tools.replace_in_file(os.path.join(self._source_subfolder, 'setup',
                                           'arm.linux_native-common.mak'),
                              'c++0x', 'c++11')

        # patch xtypes errors (remove if this gets fixed...)
        tools.patch(patch_file=os.path.join('patches', 'TypeKind.hpp.patch'),
                    base_path=self._source_subfolder)

        # fix for gcc10, https://github.com/ADLINK-IST/opensplice/issues/169
        patchGCC10 = '0001-GCC-10-enforces-usage-of-externs-for-global-variable.patch'
        tools.patch(patch_file=os.path.join('patches', patchGCC10),
                    base_path=self._source_subfolder)

        # Depend on build platform's odlpp and idlpp executables
        tools.replace_in_file(os.path.join(self._source_subfolder, 'bin',
                                           'configure_functions'),
                              'SPLICE_EXEC_PATH="${OSPL_HOME}/exec/${SPLICE_TARGET}"',
                              'SPLICE_EXEC_PATH="${OSPL_HOME}/exec/${SPLICE_HOST}"')

        # Disable shared memory stuff on android
        tools.replace_in_file(os.path.join(self._source_subfolder, 'src',
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
        path_to_patch = os.path.join(self._source_subfolder, 'src',
                                     'services', 'ddsi2e', 'core')
        tools.replace_in_file(
            os.path.join(path_to_patch, 'sysdeps.h'),
            'defined (OS_QNX_DEFS_H)',
            'defined (OS_QNX_DEFS_H) || defined(__ANDROID__)')

        tools.replace_in_file(
            os.path.join(path_to_patch, 'sysdeps.c'),
            '__GNUC_PATCHLEVEL__) < 40100)',
            '__GNUC_PATCHLEVEL__) < 40100) || defined(__ANDROID__)')


        tools.replace_in_file(
            os.path.join(self._source_subfolder, 'src', 'abstraction', 'os',
                         'posix', 'include', 'os_os_thread.h'),
            "#include <pthread.h>",
            '''#include <pthread.h>
int pthread_attr_setinheritsched (pthread_attr_t *attr, int inherit);''')

        # Add new configurations, such as Android
        if sys.version_info.major >= 3 and sys.version_info.minor >= 9:
            shutil.copytree('setup', os.path.join(self._source_subfolder, 'setup'),
                            dirs_exist_ok=True)
        else:
            src = 'setup'
            dst = os.path.join(self._source_subfolder, 'setup')
            copy_tree(src, dst)

    def build(self):

        if self.settings.os == "Windows" and self.settings.compiler.version == 17:
            self.output.warn("Downloading an existing binary artifact")
            conan, _, _ = Conan.factory()
            remote = os.environ.get('SINTEF_REMOTE', 'sintef-public')
            remotes = conan.remote_list()
            sintef_remote = [e for e in remotes if e.name == remote]
            if len(sintef_remote) == 0:
                self.output.error("sintef remote not found, set SINTEF_REMOTE")
            result = conan.search_packages(
                f"{ self.name }/{ self.version }@sintef/stable",
                query=f'os=Windows and compiler.version=16 and build_type={self.settings.build_type} and include_cs={self.options.include_cs}',
                remote_name=remote)
            ID = result['results'][0]['items'][0]['packages'][0]['id']
            artifact_url = sintef_remote[0].url.replace("api/conan/", "") + \
                f'/sintef/{ self.name }/{ self.version }/stable/0/package/{ ID }/0/conan_package.tgz'
            tools.get(artifact_url)
            return

        config = "dev" if self.settings.build_type == "Debug" else "release"
        if self.settings.os == "Windows":
            env_vars = tools.vcvars_dict(self)
            with tools.vcvars(self.settings):
                self.run("bash {} {} {} {} {} '{}' '{}' {}".format(
                    self._build_script,
                    self._source_subfolder,
                    self._ospl_platform + "-" + config,
                    tools.cpu_count(),
                    "msvc" if self.settings.compiler == "Visual Studio" else "",
                    env_vars["VSINSTALLDIR"],
                    env_vars["WindowsSdkDir"],
                    "yes" if self.options.include_cs else "no"),
                         win_bash=True,
                         subsystem="cygwin")
        elif self.settings.os == "Android":
            # Need to build for host first.
            self.run("bash {} {} x86_64.linux-tools {}".format(
                self._build_script,
                self._source_subfolder,
                tools.cpu_count()))

            # Hack to ensure that %idl.STAMP is run
            tools.replace_in_file(os.path.join(
                self._source_subfolder,
                'src', 'osplcore', 'makefile.mak'),
                                  'idl | build_tools_stage_idlpp', 'idl ')

            self.run(
                "bash {} {} {} {} $CC $CXX $RANLIB $AR $SYSROOT $ANDROID_ABI"
                .format(
                    self._build_android,
                    self._source_subfolder,
                    self._ospl_platform + "-" + config,
                    tools.cpu_count()),
                run_environment=True)
        else:
            self.run("bash {} {} {} {} {}".format(
                self._build_script,
                self._source_subfolder,
                self._ospl_platform + "-" + config,
                tools.cpu_count(),
                ""))

    def package(self):

        if self.settings.os == "Windows" and self.settings.compiler.version == 17:
            self.copy("*")
            return

        suffix = "-dev" if self.settings.build_type == "Debug" else ""
        srcDir = os.path.join(self._source_subfolder, "install", "HDE",
                              self._ospl_platform + suffix)
        self.copy("*", dst="include", src=os.path.join(srcDir, "include"))
        self.copy("*", dst="bin", src=os.path.join(srcDir, "bin"))
        self.copy("*", dst="lib", src=os.path.join(srcDir, "lib"))
        self.copy("*", dst="etc", src=os.path.join(srcDir, "etc"))
        self.copy("*", dst="share", src=os.path.join(srcDir, "tools"),
                  keep_path=True)
        self.copy("release.bat" if self.settings.os == "Windows"
                  else "release.com", dst="", src=srcDir)
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(self._find_script)

        if self.settings.os == "Android":
            # Copy idlpp tool and its dependency for generating source code
            srcDir = os.path.join(self._source_subfolder, "install", "HDE",
                                  'x86_64.linux')
            self.copy("idlpp*", dst="bin", src=os.path.join(srcDir, "bin"))
            self.copy("*ddshts*", dst="lib", src=os.path.join(srcDir, "lib"))

    def package_info(self):
        self.cpp_info.includedirs = [
            "include",
            "include/sys",
            "include/dcps/C++/isocpp2"
            "include/dcps/C++/SACPP",
        ]
        self.cpp_info.libs = [
            "ddskernel",
            "dcpsisocpp2",
            "dcpssacpp"
        ]
        self.env_info.PATH.append(
            os.path.join(self.package_folder, "bin"))
        self.env_info.LD_LIBRARY_PATH.append(
            os.path.join(self.package_folder, "lib"))
        self.env_info.DYLD_LIBRARY_PATH.append(
            os.path.join(self.package_folder, "lib"))

        # Extract OSPL_* environment variables from release script and add them
        # to self.env_info
        if (self.settings.os == "Windows"):
            envCmd = ["cmd.exe", "/C", "release.bat && set"]
        else:
            envCmd = ["bash", "-c", "source release.com && env"]
        proc = subprocess.run(envCmd, stdout=subprocess.PIPE, check=True,
                              universal_newlines=True)
        for line in proc.stdout.split('\n'):
            pair = line.split('=', 1)
            if len(pair) == 2 and pair[0].startswith("OSPL_"):
                self.env_info.__setattr__(pair[0], pair[1])
