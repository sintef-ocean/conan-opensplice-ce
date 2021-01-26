#!/bin/bash
# Usage: build-opensplice.sh <src_dir> <config> <cpus> CC CXX RANLIB AR SYSROOT ABI
#
# <src_dir>   = OSPL source directory
# <config>    = OSPL config, e.g. "x86_64.linux-release"
# <cpus>      = Max. number of parallel jobs
# CC          = Path to c compiler
# CXX         = C++ compiler
# RANLIB      =
# AR          =
# SYSROOT     = cross compile system root
# ABI         = android abi e.g. x86_64

cd "$1"

CC=$4
CXX=$5
RANLIB=$6
AR=$7
SYSROOT=$8
ANDROID_ABI=$9


OVERRIDE_INCLUDE_JAVA=no
OVERRIDE_INCLUDE_CS=no
OVERRIDE_INCLUDE_ORB=no
export OSPL_DOCS=none
export OSPL_USE_CXX11=yes

source configure "$2" && \
    (make CC=$CC CXX=$CXX RANLIB=$RANLIB \
          AR=$AR TARGETSYSROOT=$SYSROOT ANDROID_ABI=$ANDROID_ABI \
          -j$3 || \
     make CC=$CC CXX=$CXX RANLIB=$RANLIB \
          AR=$AR TARGETSYSROOT=$SYSROOT ANDROID_ABI=$ANDROID_ABI) \
    && make install
