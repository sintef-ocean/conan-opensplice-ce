PROC     = $(ANDROID_ABI)
# ANDROID_ABI provided by call to make make ANDROID_ABI=$ANDROID_ABI e.g. x86_64
OS       = linux
OS_REV   =

#CC		 = PROVIDED BY CALL TO MAKE: make CC=$CC CXX=..
#CXX		 = PROVIDED BY CALL TO MAKE: make CXX=$CXX CC=..
CSC		 = gmcs

    # Binary used for linking
LD_SO            = $(CC)
    # Binary used for linking executables
LD_EXE           = $(CC)
LD_CXX           = $(CXX)
	# GNU yacc
YACC		 = bison
	# GNU lex
LEX		 = flex
	# GNU make
MAKE		 = make
	# native touch
TOUCH		 = touch
	# Tool used for creating soft/hard links.
LN               = ln -s
	# Archiving
#AR               = PROVIDED BY CALL TO MAKE: make AR=$AR CC=..
AR_CMDS          = rv
	# preprocessor
MAKEDEPFLAGS     = -M
CPP		 = $(CC)
GCPP		 = $(CXX) -E
	# gcov
GCOV		 = gcov

	#Javac
JCC              = javac
JCFLAGS_JACORB   = -endorseddirs "$(JACORB_HOME)/lib/endorsed"
JACORB_INC       =

ifdef JAVA_COMPATJAR
ifneq (,$(JAVA_COMPATJAR))
JCFLAGS_COMPAT   = -source 1.6 -target 1.6 -bootclasspath "$(JAVA_COMPATJAR)"
endif
endif

	#JAR
JAR		 = jar

#JAVAH
JAVAH            = javah
JAVAH_FLAGS      = -force

	#Java
JAVA		 = java
JAVA_SRCPATH_SEP = :
JAVA_LDFLAGS	 = -L"$(JAVA_HOME)/jre/lib/i386"
JAVA_LDFLAGS	 += -L"$(JAVA_HOME)/jre/lib/i386/client"
JAVA_LDFLAGS	 += -L"$(JAVA_HOME)/jre/lib/i386/native_threads"
JAVA_INCLUDE	 = -I"$(JAVA_HOME)/include"
JAVA_INCLUDE	 += -I"$(JAVA_HOME)/include/linux"

	#soapcpp
SOAPCPP		= soapcpp2

# Identify compiler flags for building shared libraries
SHCFLAGS         = -fPIC

# Values of compiler flags can be overruled
CFLAGS_OPT       = -O3 -DNDEBUG #-DLITE
CFLAGS_DEBUG     = -D_TYPECHECK_
CFLAGS_STRICT	 = -Wall -W -pedantic -Wno-long-long
# Only for 32 bit, which we don't care about: -Wno-long-long

ifneq ($(TARGETSYSROOT),)
SYSROOTFLAGS=--sysroot=$(TARGETSYSROOT)
else
SYSROOTFLAGS=
endif

# Set compiler options
CFLAGS		 = $(CFLAGS_OPT) $(CFLAGS_DEBUG) $(CFLAGS_STRICT) $(MTCFLAGS) -I$(ZLIB_HOME)/include $(SYSROOTFLAGS)

CXXFLAGS	 = $(CFLAGS_OPT) $(CINCS) $(CFLAGS_DEBUG) $(MTCFLAGS) -fexceptions
CSFLAGS	     = -noconfig -nowarn:1701,1702 -warn:4 $(CSFLAGS_DEBUG) -optimize-

# For Linux, this version supports symbolic names instead of IP addresses
CFLAGS      += -DDO_HOST_BY_NAME

# Set CPP flags
CPPFLAGS	 = -DOSPL_ENV_$(SPECIAL) -D_GNU_SOURCE $(SYSROOTFLAGS)
ifeq (,$(wildcard /etc/gentoo-release))
CPPFLAGS	 += -D_XOPEN_SOURCE=500
endif

# For isocpp2 use c++11 compiler option
ifeq ($(GCC_SUPPORTS_CPLUSPLUS11),1)
ISOCPP2_CXX_FLAGS=-std=c++11
endif

# Disable licensing because RLM not available on ARM
CPPFLAGS += -DOSPL_NO_LICENSING
CFLAGS += -DOSPL_NO_LICENSING
# Set compiler options for multi threaded process
	# notify usage of posix threads
MTCFLAGS	 = -D_POSIX_PTHREAD_SEMANTICS -D_REENTRANT

# Set linker options
LDFLAGS		 = -L$(SPLICE_LIBRARY_PATH) $(SYSROOTFLAGS)

# Identify linker options for building shared libraries
SHLDFLAGS	 = -fPIC -shared
#-dynamiclib

# Set library context
LDLIBS           = -lc -lm -ldl

# Set library context for building shared libraries
SHLDLIBS	 =

# Set component specific libraries that are platform dependent
LDLIBS_CXX = -lstdc++
LDLIBS_NW =
LDLIBS_OS = -ldl -lm
LDLIBS_CMS =
LDLIBS_JAVA = -ljvm -ljava -lverify -lhpi
LDLIBS_ODBC= -lodbc

#set platform specific pre- and postfixes for the names of libraries and executables
OBJ_POSTFIX = .o
SLIB_PREFIX = lib
SLIB_POSTFIX = .a
DLIB_PREFIX = lib
DLIB_POSTFIX = .so
EXEC_PREFIX =
EXEC_POSTFIX =
EXEC_LD_POSTFIX =
INLINESRC_POSTFIX = .i

# Identify linker options for building shared C# libraries and or executables.
CSLIB_PREFIX =
CSLIB_POSTFIX = .dll
CSMOD_PREFIX =
CSMOD_POSTFIX = .netmodule
CSEXEC_PREFIX =
CSEXEC_POSTFIX = .exe
CSDBG_PREFIX =
CSEXEC_DBG_POSTFIX = .exe.mdb
CSMOD_DBG_POSTFIX = .netmodule.mdb
CSLIB_DBG_POSTFIX = .dll.mdb
CS_LIBPATH_SEP = ,

CSTARGET_LIB = -target:library
CSTARGET_MOD = -t:module
CSTARGET_EXEC = -target:exe
