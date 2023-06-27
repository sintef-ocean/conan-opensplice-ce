[![Linux GCC](https://github.com/sintef-ocean/conan-opensplice-ce/workflows/Linux%20GCC/badge.svg)](https://github.com/sintef-ocean/conan-opensplice-ce/actions?query=workflow%3A"Linux+GCC")
[![Linux Clang](https://github.com/sintef-ocean/conan-opensplice-ce/workflows/Linux%20Clang/badge.svg)](https://github.com/sintef-ocean/conan-opensplice-ce/actions?query=workflow%3A"Linux+Clang")
[![Windows MSVC](https://github.com/sintef-ocean/conan-opensplice-ce/workflows/Windows%20MSVC/badge.svg)](https://github.com/sintef-ocean/conan-opensplice-ce/actions?query=workflow%3A"Windows+MSVC")

[Conan.io](https://conan.io) recipe for [opensplice-ce](https://github.com/ADLINK-IST/opensplice).

## How to use this package

1. Add remote to conan's package [remotes](https://docs.conan.io/2/reference/commands/remote.html)

   ```bash
   $ conan remote add sintef https://artifactory.smd.sintef.no/artifactory/api/conan/conan-local
   ```

2. Using [*conanfile.txt*](https://docs.conan.io/2/reference/conanfile_txt.html) and *cmake* in your project.

   Add *conanfile.txt*:
   ```
   [requires]
   opensplice-ce/[>=6.9]@sintef/stable

   [tool_requires]
   cmake/[>=3.25.0]

   [options]

   [layou]
   cmake_layout

   [generators]
   CMakeDeps
   CMakeToolchain
   VirtualBuildEnv
   ```

   Insert into your *CMakeLists.txt* something like the following lines:
   ```cmake
   cmake_minimum_required(VERSION 3.15)
   project(TheProject CXX)

   find_package(OpenSplice CONFIG REQUIRED)

   add_executable(the_executor code.cpp)
   target_link_libraries(the_executor OpenSplice::isocpp2) # or OpenSplice::isocpp, or OpenSplice::OpenSplice
   ```
   Install and build e.g. a Release configuration:
   ```bash
   $ conan install . -s build_type=Release -pr:b=default
   $ source build/Release/generators/conanbuild.sh
   $ cmake --preset conan-release
   $ cmake --build build/Release
   $ source build/Release/generators/deactivate_conanbuild.sh
   ```

## Package options

| Option        | Allowed values    | Default value     |
| ------------- | ----------------- | ----------------- |
| inclue_cs     | [True, False]     | False             |


## Known recipe issues

**Note**: You need [Cygwin](https://www.cygwin.com/) to build this
package. Currently, this recipe does not install it for you, so you need
to install it manually. The following additional Cygwin packages are
needed: `gcc-core, make, git, perl, bison, flex, gawk, zip, unzip`. If
you have [Chocolatey](https://chocolatey.org/%20) installed you can run
the following commands:

``` shell
choco install cygwin
choco install cyg-get
cyg-get gcc-core make git perl bison flex gawk zip unzip
```

You may also need to specify the path for cygwin bash to help Conan,
e.g. in `cmd`: `set CONAN_BASH_PATH="C:\tools\cygwin\bin\bash.exe"`
