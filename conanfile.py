from conans import ConanFile, tools
import os, subprocess


class OpenSpliceConan(ConanFile):
    name = "opensplice-ce"
    version = "6.9.190925"
    license = "Apache-2.0"
    description = "Vortex OpenSplice Community Edition, an open-source implementation of the OMG DDS standard"
    homepage = "https://github.com/ADLINK-IST/opensplice"
    url = "https://github.com/sintef-ocean/conan-opensplice.git"
    author = "SINTEF Ocean"

    settings = "os", "compiler", "build_type", "arch"
    default_options = {
        "cygwin_installer:additional_packages": "git,perl,bison,flex,gawk,zip,unzip",
        "cygwin_installer:with_pear": False
    }

    _build_script = "build-opensplice.sh"
    _find_script = "FindOpenSplice.cmake"
    _source_subfolder = "source_subfolder"

    exports_sources = [ _build_script, _find_script ]

    @property
    def _ospl_platform(self):
        arch = self.settings.arch.value.lower()
        if self.settings.os == "Windows":
            system = "win64" if arch == "x86_64" else "win32"
        else:
            system = self.settings.os.value.lower()
        return arch + "." + system

    def build_requirements(self):
        if self.settings.os == "Windows":
            self.build_requires("cygwin_installer/2.9.0@bincrafters/stable")

    def source(self):
        revision = "OSPL_V" + self.version.replace(".", "_") + "OSS_RELEASE"
        url = "https://github.com/ADLINK-IST/opensplice/archive/" + revision + ".tar.gz"
        tools.get(url)
        os.rename("opensplice-" + revision, self._source_subfolder)

    def build(self):
        config = "debug" if self.settings.build_type == "Debug" else "release"
        with tools.vcvars(self.settings):
            self.run(
                "bash {} {} {} {} {}".format(
                    self._build_script,
                    self._source_subfolder,
                    self._ospl_platform + "-" + config,
                    tools.cpu_count(),
                    "msvc" if self.settings.compiler == "Visual Studio" else ""),
                win_bash=(self.settings.os == "Windows"))

    def package(self):
        suffix = "-debug" if self.settings.build_type == "Debug" else ""
        srcDir = os.path.join(self._source_subfolder, "install", "HDE", self._ospl_platform + suffix)
        self.copy("*", dst="include", src=os.path.join(srcDir, "include"))
        self.copy("*", dst="bin", src=os.path.join(srcDir, "bin"))
        self.copy("*", dst="lib", src=os.path.join(srcDir, "lib"))
        self.copy("*", dst="etc", src=os.path.join(srcDir, "etc"))
        self.copy("release.bat" if self.settings.os == "Windows" else "release.com", dst="", src=srcDir)
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(self._find_script)

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
