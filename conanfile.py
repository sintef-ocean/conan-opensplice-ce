from conans import ConanFile, tools

buildScript = "build-opensplice.sh"

class OpenSplice(ConanFile):
    name = "opensplice"
    version = "6.9.190705-OSS"
    license = "Apache-2.0"
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

    def ospl_target(self):
        return "{}.{}-{}".format(
            self.settings.arch.value.lower(),
            self.settings.os.value.lower(),
            "debug" if self.settings.build_type == "Debug" else "release")

    def build(self):
        self.run("bash {} {}".format(buildScript, self.ospl_target()))

    def package(self):
        srcDir = "opensplice/install/HDE/" + self.ospl_target()
        self.copy("*", dst="include", src=srcDir+"/include")
        self.copy("*", dst="bin", src=srcDir+"/bin")
        self.copy("*", dst="lib", src=srcDir+"/lib")

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
