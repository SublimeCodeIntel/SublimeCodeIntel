# ******************************************************************************
# PCRE Command Line Makefile for Microsoft Visual Studio 
# Contributed by Tom Fortmann on April 25th, 2011
#
# Building PCRE library on Windows with Visual Studio 2005:
#
# 1) copy config.h.generic config.h
# 2) copy pcre.h.generic pcre.h
# 3) Edit config.h with the following changes.  These I believe are required
#    for all builds under Visual Studio.
#
#     #undef HAVE_DIRENT_H
#     #undef HAVE_INTTYPES_H
#     #undef HAVE_STDINT_H
#     #undef HAVE_UNISTD_H
#     #define HAVE_WINDOWS_H 1
#     #define SUPPORT_UCP
#     #define SUPPORT_UTF8
#
# 4) Update this make file as needed - this was based on the 8.12 release.
# 5) Run 'nmake -f winpcre.mak [DEBUG=1] [DLLBUILD=1] clean all test'
#
# Notes:
#
# I'm building from a DOS command line using nmake and the Visual Studio 2005
# compiler.  Other Windows compilers, and other releases of Visual Studio may
# require additional changes to config.h and this make file.
#
# A 'DEBUG=1' definition may be added to the nmake command line to add debugging
# options to the cl command line.  For release builds I have a fairly safe /Ot
# (favor speed) optimization enabled.  You can change this to suite your needs.
#
# For my application I just wanted a static library, but you can add the  
# 'DLLBUILD=1' definition to the nmake command line to build a DLL library.
# However, be aware that the locale test (3) on my system is failing with the
# DLL build!  I strongly suspect this is a Windows and/or environment issue and 
# NOT a code bug.  Unfortunately, I have not had a chance to chase this one down.
#
# By default the match() function is highly recursive.  On my system pcretest 
# required an 8mb stack to pass testinput2 without a stack overflow exception.
# So, you either need to increase the stack size by adding a /F8000000 to the 
# cl command, or disable recursion with the /DNO_RECURSE option.  For my 
# application disabling recursion was a simple acceptable solution, but you can 
# change this below.
# 
# And a few disclaimers...
#
# First I'm a UNIX guy living in a Windows world - which is evident by the 
# number of times I've cursored nmake while writing this make file.  
# So, please be kind as you cleanup/fix things.  
# 
# I'm contributing this make file in the hopes that it will save the next 
# developer some time, but it is provided without any explicit or implied
# warranty.  Please use it as you see fit.  
#
# If you update this file please don't misrepresent it as my original work.  
# Please remove my name from above and/or add your own attribution.
#
# Thanks and enjoy!
#
# ******************************************************************************

# Set the base compile options
CFLAGS = /nologo /W3 /D_CRT_SECURE_NO_DEPRECATE 

# Set release or debug build options
!ifdef DEBUG
CFLAGS = $(CFLAGS) /Od /Zi	# debug build options
!else
CFLAGS = $(CFLAGS) /Ot		# release build options 
!endif

# Required to include our config.h modifications
CFLAGS = $(CFLAGS) /DHAVE_CONFIG_H

# For static libraries add the required PCRE_STATIC define
!ifndef DLLBUILD
CFLAGS = $(CFLAGS) /DPCRE_STATIC=1 
!endif

# Disable recursion in match() (see note above)
CFLAGS = $(CFLAGS) /DNO_RECURSE=1
#CFLAGS = $(CFLAGS) /F8000000


# Define the output file targets
TARGETS = \
	dftables.exe \
	pcre_chartables.c \
	libpcre.lib \
	libpcreposix.lib \
	pcretest.exe \
	pcregrep.exe

!ifdef DLLBUILD
TARGETS = $(TARGETS) libpcre.dll libpcreposix.dll
!endif

# Define the libpcre.lib objects
LIB_OBJS = \
	pcre_chartables.obj \
	pcre_compile.obj \
	pcre_config.obj \
	pcre_dfa_exec.obj \
	pcre_exec.obj \
	pcre_fullinfo.obj \
	pcre_get.obj \
	pcre_globals.obj \
	pcre_info.obj \
	pcre_maketables.obj \
	pcre_newline.obj \
	pcre_ord2utf8.obj \
	pcre_refcount.obj \
	pcre_study.obj \
	pcre_tables.obj \
	pcre_try_flipped.obj \
	pcre_ucd.obj \
	pcre_valid_utf8.obj \
	pcre_version.obj \
	pcre_xclass.obj

.c.obj:
	$(CC) $(CFLAGS) /c $*.c


# Build all targets
all: $(TARGETS)


#Clean all target and intermediary files
clean:
	del /Q *.obj *.pdb *.exp $(TARGETS)


# Run validation test suite
test: pcretest.exe
	RunTest 1 2 3 4 5 6 7 8 9 10 11 12


# Generate the character table source file
dftables.exe: $*.c config.h pcre_internal.h pcre_maketables.c
	$(CC) $(CFLAGS) /DPCRE_STATIC $*.c

pcre_chartables.c: dftables.exe
	dftables.exe $@


# Build the PCRE libraries
libpcre.lib: $(LIB_OBJS)
!ifndef DLLBUILD
	lib /nologo /OUT:$@ $**
!else
	lib /nologo /NAME:$*.dll /DEF /out:$@ $**
!endif


libpcreposix.lib: pcreposix.obj
!ifndef DLLBUILD
	lib /nologo /OUT:$@ $**
!else
	lib /nologo /NAME:$*.dll /DEF /out:$@ $**
!endif


# Optionally build DLL libraries
!ifdef DLLBUILD
libpcre.dll: $(LIB_OBJS)
	link /nologo /DLL /OUT:$*.dll $**

libpcreposix.dll: pcreposix.obj
	link /nologo /DLL /OUT:$*.dll $** libpcre.lib
!endif


# Build the pcretest validation program
pcretest.exe: $*.c libpcre.lib libpcreposix.lib
	$(CC) $(CFLAGS) $*.c libpcre.lib libpcreposix.lib


# Build the pcregrep utility
pcregrep.exe: $*.c libpcre.lib
	$(CC) $(CFLAGS) $*.c libpcre.lib
