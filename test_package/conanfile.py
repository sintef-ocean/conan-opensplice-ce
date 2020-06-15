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
        if self.settings.os == "Windows":
            self.run("activate.bat && bin\\test.exe")
        else:
            self.run(". ./activate.sh && bin/test")
