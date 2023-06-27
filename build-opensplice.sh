#!/bin/bash
# Usage: build-opensplice.sh <src_dir> <config> <cpus>
#
# <src_dir>   = OSPL source directory
# <config>    = OSPL config, e.g. "x86_64.linux-release"
# <cpus>      = Max. number of parallel jobs

cd "$1"

source configure "$2" && (make -j$3 || make) && make install
