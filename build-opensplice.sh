cd opensplice

OVERRIDE_INCLUDE_JAVA=no
OVERRIDE_INCLUDE_CS=no
OVERRIDE_INCLUDE_ORB=no
source configure "$1"

export OSPL_DOCS=none
make

make install
