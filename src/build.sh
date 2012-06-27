#!/bin/bash

reset() {
	rm -rf /tmp/pcre-8.21
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

# In Linux, Sublime Text's Python is compiled with UCS4:
if [ $OSTYPE = "linux-gnu" ]; then
	if [ `uname -m` == 'x86_64' ]; then
		export CFLAGS="-fPIC -DPy_UNICODE_SIZE=4 -I /tmp/pcre-8.21 $CFLAGS"
	else
		export CFLAGS="-DPy_UNICODE_SIZE=4 -I /tmp/pcre-8.21 $CFLAGS"
	fi
	export LDFLAGS="-L/tmp/pcre-8.21/.libs $LDFLAGS"
else
	export ARCHFLAGS="-arch i386 -arch x86_64 $ARCHFLAGS"
	export CXXFLAGS="-arch i386 -arch x86_64 $CXXFLAGS"
	export CFLAGS="-arch i386 -arch x86_64 $CFLAGS"
	export LDFLAGS="-arch i386 -arch x86_64 -L/tmp/pcre-8.21/.libs $LDFLAGS"
fi

echo "Building PCRE...";
tar xzf pcre-8.21.tar.gz -C /tmp/ && \
cd /tmp/pcre-8.21 && \
./configure --disable-shared --disable-dependency-tracking --enable-utf8 --enable-unicode-properties > "$LOGDIR/PCRE.log" 2>&1 && \
mkdir .libs && \
make >> "$LOGDIR/pcre.log" 2>&1 && \
cd "$CURRENT_PATH" && \

echo "Building Sgmlop..." && \
unzip sgmlop-1.1.1-20040207.zip > /dev/null && \
cd sgmlop-1.1.1-20040207 && \
cat ../sgmlop*.patch | patch -sup1 && \
python setup.py build > "$LOGDIR/Sgmlop.log" 2>&1 && \
cd "$CURRENT_PATH" && \

echo "Patching Scintilla..." && \
tar xzf scintilla.tar.gz && \
find . -name "LexTCL*" -delete && \
cd scintilla && \
cat ../scintilla.patch/*.patch | patch -sup0 && \
cp -f ../scintilla.patch/lexers/* lexers/ && \
cd include && python HFacer.py > /dev/null && \
cd "$CURRENT_PATH" && \

echo "Building SilverCity..." && \
tar xzf silvercity.tar.gz && \
cp -f /tmp/pcre-8.21/.libs/* silvercity/ && \
cd silvercity && \
cat ../SilverCity.patch/*.patch | patch -sup1 && \
cp -f ../SilverCity.patch/*.py PySilverCity/SilverCity/ && \
python setup.py build > "$LOGDIR/SilverCity.log" 2>&1 && \
cd "$CURRENT_PATH" && \

echo "Building cElementTree..." && \
tar xzf cElementTree-1.0.5-20051216.tar.gz && \
cd cElementTree-1.0.5-20051216 && \
cat ../cElementTree-1.0.5-20051216.patch/*.patch | patch -sup1 && \
python setup.py build > "$LOGDIR/cElementTree.log" 2>&1 && \
cd "$CURRENT_PATH" && \

find . -type f -name sgmlop.so -exec cp {} ../libs/_local_arch \; && \
find . -type f -name _SilverCity.so -exec cp {} ../libs/_local_arch \; && \
find . -type f -name ciElementTree.so -exec cp {} ../libs/_local_arch \; && \

reset && \
echo "Done!" || \
echo "Build Failed!"

strip ../libs/_local_arch/*.so > /dev/null 2>&1
