from conans import ConanFile, tools
import os, subprocess


class OpenSplice(ConanFile):
    name = "opensplice"
    version = "6.9.190705-OSS"
    license = "Apache-2.0"
    description = "Vortex OpenSplice Community Edition"
    url = "https://stash.code.sintef.no/projects/MOVE/repos/conan-opensplice/browse"
    homepage = "https://github.com/ADLINK-IST/opensplice"

    settings = "os", "compiler", "build_type", "arch"
    default_options = {
        "cygwin_installer:additional_packages": "git,perl,bison,flex,gawk,zip,unzip",
        "cygwin_installer:with_pear": False
    }
    generators = "cmake"

    _buildscript = "build-opensplice.sh"
    _source_subfolder = "source_subfolder"
    exports_sources = [ _buildscript ]

    @property
    def _ospl_target(self):
        arch = self.settings.arch.value.lower()
        if self.settings.os == "Windows":
            system = "win64" if arch == "x86_64" else "win32"
        else:
            system = self.settings.os.value.lower()
        config = "debug" if self.settings.build_type == "Debug" else "release"
        return "{}.{}-{}".format(arch, system, config)

    def build_requirements(self):
        if self.settings.os == "Windows":
            self.build_requires("cygwin_installer/2.9.0@bincrafters/stable")

    def source(self):
        revision = "OSPL_V" + self.version.replace(".", "_").replace("-", "") + "_RELEASE"
        url = "https://github.com/ADLINK-IST/opensplice/archive/" + revision + ".tar.gz"
        tools.get(url)
        os.rename("opensplice-" + revision, self._source_subfolder)

    def build(self):
        with tools.vcvars(self.settings):
            self.run(
                "bash {} {} {} {} {}".format(
                    self._buildscript,
                    self._source_subfolder,
                    self._ospl_target,
                    tools.cpu_count(),
                    "MSVC" if self.settings.compiler == "Visual Studio" else ""),
                win_bash=True)

    def package(self):
        srcDir = os.path.join(self._source_subfolder, "install", "HDE", self._ospl_target)
        self.copy("*", dst="include", src=os.path.join(srcDir, "include"))
        self.copy("*", dst="bin", src=os.path.join(srcDir, "bin"))
        self.copy("*", dst="lib", src=os.path.join(srcDir, "lib"))
        self.copy("*", dst="etc", src=os.path.join(srcDir, "etc"))
        self.copy("release.bat" if self.settings.os == "Windows" else "release.com", dst="", src=srcDir)

    def package_info(self):
        self.cpp_info.includedirs = [
            "include",
            "include/sys",
            "include/dcps/C++/SACPP",
            "include/dcps/C++/isocpp"
        ]
        self.cpp_info.libs = [
            "ddskernel",
            "dcpsisocpp",
            "dcpssacpp"
        ]
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.env_info.LD_LIBRARY_PATH.append(os.path.join(self.package_folder, "lib"))
        self.env_info.DYLD_LIBRARY_PATH.append(os.path.join(self.package_folder, "lib"))

        # Extract OSPL_* environment variables from release script and add them
        # to self.env_info
        if (self.settings.os == "Windows"):
            envCmd = ["cmd.exe", "/C", "release.bat && set"]
        else:
            envCmd = ["bash", "-c", "source release.com && env"]
        proc = subprocess.run(envCmd, stdout=subprocess.PIPE, check=True, universal_newlines=True)
        for line in proc.stdout.split('\n'):
            pair = line.split('=', 1)
            if len(pair) == 2 and pair[0].startswith("OSPL_"):
                self.env_info.__setattr__(pair[0], pair[1])
