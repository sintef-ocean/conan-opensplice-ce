from os.path import join
from conan import ConanFile, conan_version
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import supported_cppstd
from conan.tools.env import Environment
from conan.tools.microsoft import VCVars
from conan.tools.files import copy, get, replace_in_file
from conan.tools.files import apply_conandata_patches, export_conandata_patches
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
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
        export_conandata_patches(self)
        copy(self, '*', join(self.recipe_folder, "patches"), join(self.export_sources_folder, "patches"))
        copy(self, '*', join(self.recipe_folder, "setup"), join(self.export_sources_folder, "setup"))
        copy(self, self._build_script, self.recipe_folder, self.export_sources_folder)
        copy(self, "OpenSpliceHelpers.cmake", self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os != "Windows" and not is_msvc(self):
            del self.options.include_cs
        if self._settings_build.os == "Windows":
            self.win_bash = True

    def compatibility(self):

        cppstds = supported_cppstd(self)

        if self.settings.compiler == "msvc":
            com_ver = self.settings.compiler.version
            candidates = ("190", "191", "192", "193")
            greater_eq = []
            for c in candidates:
                if Version(com_ver) >= Version(c):
                    greater_eq.append(c)

            return [{"settings": [("compiler.version", v), ("compiler.cppstd", w)]}
                    for v in greater_eq for w in cppstds]

        if Version(conan_version).major < 2 and self.settings.compiler == "Visual Studio":
            com_ver = str(self.settings.compiler.toolset).replace("v", "")
            candidates = ("140", "141", "142", "143")
            greater_eq = []
            for c in candidates:
                if Version(com_ver) >= Version(c):
                    greater_eq.append("v" + c)
            # Do not handle cppstd in conan 1
            return [{"settings": [("compiler.toolset", v)]}
                    for v in greater_eq]

    def layout(self):
        basic_layout(self, src_folder="src")

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
        if self._settings_build.os == "Linux":
            self.tool_requires("flex/2.6.4")
            self.tool_requires("bison/3.8.2")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

        # Do not check for Java
        replace_in_file(self, join(self.source_folder, "bin", "checkconf"),
                        'echo -n "JAVAC: "',
                        'echo -n "JAVAC: Skipping Java. "\n    no_javac\n    return $?')

        # Use a Dotnet version that might be installed on build server
        replace_in_file(self, join(self.source_folder, "bin", "checkconf"),
                        '4.6.1', '4.6.2')

        # Add new configurations
        copy(self, "*", join(self.export_sources_folder, "setup"),
             join(self.source_folder, "setup"))

    def generate(self):

        if is_msvc(self):
            ms = VCVars(self)
            ms.generate()

        yes_no = lambda v: "yes" if v else "no"

        env = Environment()
        env.define("OVERRIDE_INCLUDE_JAVA", "no")
        env.define("OVERRIDE_INCLUDE_ORB", "no")
        env.define("OVERRIDE_INCLUDE_CS", "no")
        env.define("OSPL_DOCS", "none")
        env.define("OSPL_USE_CXX11", "yes")

        if is_msvc(self):
            env.define("DISTUTILS_USE_SDK", "1")
            env.define("OVERRIDE_INCLUDE_CS", yes_no(self.options.include_cs))
            env.unset("tmp")
            env.unset("temp")
            env.unset("TMP")
            env.unset("TEMP")
            # A hack to avoid issue with idlpp not finding dlls, probably because PATH has too many characters(?)
            if self.settings.build_type == "Release":
                env.prepend_path("PATH", join(self.source_folder, "lib", "x86_64.win64-release"))
            elif self.settings.build_type == "Debug":
                env.prepend_path("PATH", join(self.source_folder, "lib", "x86_64.win64-dev"))

        env.vars(self).save_script("conanbuild_custom")

    def build(self):

        config = "dev" if self.settings.build_type == "Debug" else "release"
        jobs = self.conf.get('tools.build:jobs')
        if not jobs:
            jobs = os.cpu_count()

        source = self.source_folder
        if self.settings.os == "Windows":
            source = str(source).replace('\\', '/')
        else:
            os.chmod(join(self.export_sources_folder, self._build_script), 0o755)
        msvc = "msvc" if is_msvc(self) else ""

        self.run(f"./{self._build_script} {source} {self._ospl_platform}-{config} {jobs} {msvc}", cwd=self.export_sources_folder)

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
