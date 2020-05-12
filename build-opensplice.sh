#!/bin/bash
# Usage: build-opensplice.sh <src_dir> <config> <cpus> [<toolchain>]
#
# <src_dir>   = OSPL source directory
# <config>    = OSPL config, e.g. "x86_64.linux-release"
# <cpus>      = Max. number of parallel jobs
# <toolchain> = "MSVC" or unspecified

cd "$1"

if [ "$4" = "MSVC" ]; then
    export VS_HOME="$(cygpath "$VSINSTALLDIR")"
    export WINDOWSSDKDIR="$(cygpath "$WINDOWSSDKDIR")"
    unset tmp
    unset temp
    unset TMP
    unset TEMP
fi

OVERRIDE_INCLUDE_JAVA=no
OVERRIDE_INCLUDE_CS=no
OVERRIDE_INCLUDE_ORB=no
export OSPL_DOCS=none

source configure "$2" && make -j$3 && make install
