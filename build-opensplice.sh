cd opensplice

OVERRIDE_INCLUDE_JAVA=no
OVERRIDE_INCLUDE_CS=no
OVERRIDE_INCLUDE_ORB=no
export OSPL_DOCS=none

source configure "$1" && make -j$2 && make install
