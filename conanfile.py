from conans import ConanFile, tools
import os

buildScript = "build-opensplice.sh"

class OpenSplice(ConanFile):
    name = "opensplice"
    version = "6.9.190705-OSS"
    license = "Apache-2.0"
    url = "https://stash.code.sintef.no/projects/MOVE/repos/conan-opensplice/browse"
    description = "Vortex OpenSplice Community Edition"
    homepage = "https://github.com/ADLINK-IST/opensplice"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    scm = {
        "type": "git",
        "subfolder": "opensplice",
        "url": "https://github.com/ADLINK-IST/opensplice.git",
        "revision": "OSPL_V6_9_190705OSS_RELEASE"
    }
    exports_sources = [ buildScript ]

    def _ospl_target(self):
        return "{}.{}-{}".format(
            self.settings.arch.value.lower(),
            self.settings.os.value.lower(),
            "debug" if self.settings.build_type == "Debug" else "release")

    def build(self):
        self.run("bash {} {} {}".format(buildScript, self._ospl_target(), tools.cpu_count()))

    def package(self):
        srcDir = os.path.join("opensplice", "install", "HDE", self._ospl_target())
        self.copy("*", dst="include", src=os.path.join(srcDir, "include"))
        self.copy("*", dst="bin", src=os.path.join(srcDir, "bin"))
        self.copy("*", dst="lib", src=os.path.join(srcDir, "lib"))
        self.copy("*", dst="etc", src=os.path.join(srcDir, "etc"))
        self.copy("release.com", dst="", src=srcDir)

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
