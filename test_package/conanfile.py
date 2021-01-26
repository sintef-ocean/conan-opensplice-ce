from conans import ConanFile, CMake
import os


class OpenSpliceTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake_paths", "virtualenv"

    def build_requirements(self):
        if self.settings.os == "Android":
            self.build_requires("android_ndk_installer/r21d@bincrafters/stable")

    def build(self):
        cmake = CMake(self)
        cmake.verbose = True
        if self.settings.os == "Android":
            cmake.definitions["CMAKE_TOOLCHAIN_FILE"] = os.environ['CONAN_CMAKE_TOOLCHAIN_FILE']
            cmake.definitions["ANDROID_ABI"] = os.environ['ANDROID_ABI']
            cmake.definitions["ANDROID_NATIVE_API_LEVEL"] = os.environ['ANDROID_NATIVE_API_LEVEL']
        cmake.configure()
        cmake.build()

    def test(self):
        if self.settings.compiler == "Visual Studio":
            self.run("activate.bat && " + str(self.settings.build_type) + "\\test_prog.exe")
        elif self.settings.os == "Android":
            print("Test with Android is not implemented. If it compiles, it runs..?")
        else:
            self.run(". ./activate.sh && ./test_prog")
