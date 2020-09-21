#!/bin/bash
# Usage: build-opensplice.sh <src_dir> <config> <cpus> [msvc]
#
# <src_dir>   = OSPL source directory
# <config>    = OSPL config, e.g. "x86_64.linux-release"
# <cpus>      = Max. number of parallel jobs
# "msvc"      = Toolchain is MSVC

cd "$1"

OVERRIDE_INCLUDE_CS=no

if [ "$4" = "msvc" ]; then
    export VS_HOME="$(cygpath "$5")"
    export WINDOWSSDKDIR="$(cygpath "$6")"
    OVERRIDE_INCLUDE_CS="$7"
    unset tmp
    unset temp
    unset TMP
    unset TEMP

    if [ $(which python) ]; then
        export PYTHON3_HOME=$(which python)
    fi

    export DISTUTILS_USE_SDK=1
    echo $WINDOWSSDKDIR

fi

OVERRIDE_INCLUDE_JAVA=no
OVERRIDE_INCLUDE_ORB=no
export OSPL_DOCS=none
export OSPL_USE_CXX11=yes

source configure "$2" && (make -j$3 || make) && make install
