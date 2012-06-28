#!/bin/bash

reset() {
	rm -rf /tmp/pcre-8.21
	rm -rf pcre-8.21
	rm -rf cElementTree-1.0.5-20051216
	rm -rf silvercity
	rm -rf scintilla
	rm -rf sgmlop-1.1.1-20040207
}

reset

rm -rf logs

CURRENT_PATH=`pwd`
LOGDIR="$CURRENT_PATH/logs"
mkdir logs

if [ $OSTYPE = "linux-gnu" ]; then
	# In Linux, Sublime Text's Python is compiled with UCS4:
	echo "Linux build!"
	if [ `uname -m` == 'x86_64' ]; then
		export CFLAGS="-fPIC -DPy_UNICODE_SIZE=4 -I /tmp/pcre-8.21 $CFLAGS"
	else
		export CFLAGS="-DPy_UNICODE_SIZE=4 -I /tmp/pcre-8.21 $CFLAGS"
	fi
	LIBPCRE="/tmp/pcre-8.21/.libs/libpcre.a"
	PYTHON="python"
	SO="so"
elif [ ${OSTYPE:0:6} = "darwin" ]; then
	echo "Mac OS X build!"
	export ARCHFLAGS="-arch i386 -arch x86_64 $ARCHFLAGS"
	export CXXFLAGS="-arch i386 -arch x86_64 $CXXFLAGS"
	export CFLAGS="-arch i386 -arch x86_64 $CFLAGS"
	export LDFLAGS="-arch i386 -arch x86_64 $LDFLAGS"
	LIBPCRE="/tmp/pcre-8.21/.libs/libpcre.a"
	PYTHON="python"
	SO="so"
else
	if [[ "$FRAMEWORKDIR" == *"Framework64"* ]]; then
		echo "Windows (amd64) build!"
		PYTHON="C:/Python26-x64/python"
	else
		echo "Windows (x86) build!"
		PYTHON="C:/Python26/python"
	fi
	ERR=" (You need to have Visual Studio and run this script from the Command Prompt. You also need the following tools: bash, patch, find and python 2.6 available from the command line)"
	LIBPCRE="pcre-8.21/libpcre.lib"
	OSTYPE=""
	SO="pyd"
fi

([ "$OSTYPE" == "" ] || (echo "Building PCRE (*nix)..." && \
	tar xzf pcre-8.21.tar.gz -C /tmp/ && \
	cd /tmp/pcre-8.21 && \
	./configure --disable-shared --disable-dependency-tracking --enable-utf8 --enable-unicode-properties > "$LOGDIR/PCRE.log" 2>&1 && \
	mkdir .libs && \
	make >> "$LOGDIR/PCRE.log" 2>&1 && \
	cd "$CURRENT_PATH"
)) && \

([ "$OSTYPE" != "" ] || (echo "Building PCRE (win)..." && \
	tar xzf pcre-8.21.tar.gz && \
	cd pcre-8.21 && \
	cp pcre.h.generic pcre.h && \
	cp config.h.generic config.h && \
	echo "#undef HAVE_DIRENT_H" >> config.h && \
	echo "#undef HAVE_INTTYPES_H" >> config.h && \
	echo "#undef HAVE_STDINT_H" >> config.h && \
	echo "#undef HAVE_UNISTD_H" >> config.h && \
	echo "#define HAVE_WINDOWS_H 1" >> config.h && \
	echo "#define SUPPORT_UCP" >> config.h && \
	echo "#define SUPPORT_UTF8" >> config.h && \
	nmake -f ../winpcre.mak clean libpcre.lib >> "$LOGDIR/PCRE.log" 2>&1 && \
	cd "$CURRENT_PATH"
)) && \

(echo "Building Sgmlop..." && \
	unzip sgmlop-1.1.1-20040207.zip > /dev/null && \
	cd sgmlop-1.1.1-20040207 && \
	cat ../sgmlop*.patch | patch -sup1 --binary && \
	$PYTHON setup.py build > "$LOGDIR/Sgmlop.log" 2>&1 && \
cd "$CURRENT_PATH"
) && \

(echo "Patching Scintilla..." && \
	tar xzf scintilla.tar.gz && \
	find . -name "LexTCL*" -exec rm {} \; && \
	cd scintilla && \
	cat ../scintilla.patch/*.patch | patch -sup0 --binary && \
	cp -f ../scintilla.patch/lexers/* lexers/ && \
	cd include && $PYTHON HFacer.py > /dev/null && \
	cd "$CURRENT_PATH"
) && \

(echo "Building SilverCity..." && \
	tar xzf silvercity.tar.gz && \
	cp -f "$LIBPCRE" silvercity/ && \
	cd silvercity && \
	cat ../SilverCity.patch/*.patch | patch -sup1 --binary && \
	cp -f ../SilverCity.patch/*.py PySilverCity/SilverCity/ && \
	$PYTHON setup.py build > "$LOGDIR/SilverCity.log" 2>&1 && \
	cd "$CURRENT_PATH"
) && \

(echo "Building cElementTree..." && \
	tar xzf cElementTree-1.0.5-20051216.tar.gz && \
	cd cElementTree-1.0.5-20051216 && \
	cat ../cElementTree-1.0.5-20051216.patch/*.patch | patch -sup1 --binary && \
	$PYTHON setup.py build > "$LOGDIR/cElementTree.log" 2>&1 && \
	cd "$CURRENT_PATH"
) && \

find . -type f -name "sgmlop.$SO" -exec cp {} ../libs/_local_arch \; && \
find . -type f -name "_SilverCity.$SO" -exec cp {} ../libs/_local_arch \; && \
find . -type f -name "ciElementTree.$SO" -exec cp {} ../libs/_local_arch \; && \

reset && \
echo "Done!" || \
echo "Build Failed!$ERR"

strip ../libs/_local_arch/*.so > /dev/null 2>&1
