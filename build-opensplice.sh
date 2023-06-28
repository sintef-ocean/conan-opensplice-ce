#!/bin/bash
# Usage: build-opensplice.sh <src_dir> <config> <cpus> [msvc]
#
# <src_dir>   = OSPL source directory
# <config>    = OSPL config, e.g. "x86_64.linux-release"
# <cpus>      = Max. number of parallel jobs
# [msvc]      = Set if visual studio

cd "$1"

if [ "$4" == "msvc" ]; then
  export VS_HOME="$(cygpath "$VCToolsInstallDir")" #"$(cygpath "$VSINSTALLDIR")"
  export WINDOWSSDKDIR="$(cygpath "$WindowsSdkDir")"
fi

source configure "$2" && (make -j$3 || make) && make install
