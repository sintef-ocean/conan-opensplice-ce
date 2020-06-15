from conans import ConanFile, CMake
import os

class OpenSpliceTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake_paths", "virtualenv"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if self.settings.compiler == "Visual Studio":
            self.run("activate.bat && " + str(self.settings.build_type) + "\\test.exe")
        else:
            self.run(". ./activate.sh && ./test")
