Vortex OpenSplice DDS package recipe for Conan
==============================================

Supported platforms and features
--------------------------------
This package currently only supports the following platform and toolchain
settings:

  - `arch`: `x86` or `x86_64`
  - `os`: `Linux` or `Windows`
  - `compiler`: `gcc` on Linux or `Visual Studio` on Windows

Conan being primarily a C/C++ package manager, many of OpenSplice's
non-C/C++ features have been disabled for the sake of efficiency.
These are:

  - Java support (`OVERRIDE_INCLUDE_JAVA=no`)
  - C# support (`OVERRIDE_INCLUDE_CS=no`)
  - CORBA support (`OVERRIDE_INCLUDE_ORB=no`)

Furthermore, API documentation is not generated (`OSPL_DOCS=none`), because
people usually won't look for documentation in their Conan package cache.

Currently, the usage information provided by the package (i.e., include
directories and library paths) enables consumers to use OpenSplice's
[ISO C++ 2] API.  The other, older APIs are also built and available in the
package cache, but using them requires a bit more manual work.

Building the package
--------------------
After cloning this repository, run the following command to build and install
the package:

    conan create . move/development

On Windows, the package depends on [`cygwin_installer`], since OpenSplice
requires Cygwin for its build system.  This causes the Cygwin base system
to be installed along with some necessary packages.  It will not conflict
with any existing Cygwin installations, however, because it gets installed
in isolation within the Conan package cache.

Using the package
-----------------
The package is used like any other Conan package, i.e., by listing
`opensplice/<version>@move/development` as a dependency in your project's
Conanfile.  (Look in [`conanfile.py`] to find the current version.)

It is recommended to use the [`virtualenv`] generator in conjunction with
this package.  This generator will create scripts that set up the environment
variables needed by OpenSplice at run time, for example `OSPL_HOME`.
Sourcing the `activate.sh` script it generates is equivalent to using the
`release.com`/`release.bat` scripts provided in a standard OpenSplice
distribution.  (Note that these are also available in the Conan package
directory in case you need them.)


[ISO C++ 2]: http://download.prismtech.com/docs/Vortex/apis/ospl/isocpp2/html/index.html
[`conanfile.py`]: ./conanfile.py
[`cygwin_installer`]: https://docs.conan.io/en/latest/systems_cross_building/windows_subsystems.html
[`virtualenv`]: https://docs.conan.io/en/latest/reference/generators/virtualenv.html
