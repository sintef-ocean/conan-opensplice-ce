Vortex OpenSplice DDS package recipe for Conan
==============================================

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

By default, two Conan generators are enabled (though you can of course
specify others with the `--generator` switch when running `conan install`):

  - [`cmake`]: This generator is useful at compile time, because it creates
    scripts that enable CMake to find the OpenSplice headers and libraries.
  - [`virtualenv`]: This generator is useful at run time, because it creates
    scripts that set up the environment variables needed by OpenSplice, for
    example `OSPL_HOME`.  Sourcing the `activate.sh` script it generates is
    equivalent to using the `release.com`/`release.bat` scripts provided by
    a standard OpenSplice distribution.  (Note that these are also available
    in the Conan package directory in case you need them.)


[`cmake`]: https://docs.conan.io/en/latest/reference/generators/cmake.html
[`conanfile.py`]: ./conanfile.py
[`cygwin_installer`]: https://docs.conan.io/en/latest/systems_cross_building/windows_subsystems.html
[`virtualenv`]: https://docs.conan.io/en/latest/reference/generators/virtualenv.html
