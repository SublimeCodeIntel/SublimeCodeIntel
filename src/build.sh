#!/bin/bash
# In Linux, Sublime Text's Python is compiled with UCS4:
if [ $OSTYPE = "linux-gnu" ]; then
	export CFLAGS=-DPy_UNICODE_SIZE=4
fi

rm -rf cElementTree-1.0.5-20051216 &&\
rm -rf SilverCity-0.9.7 &&\
rm -rf scintilla &&\
rm -rf sgmlop-1.1.1-20040207 && \
unzip sgmlop-1.1.1-20040207.zip && \
cd sgmlop-1.1.1-20040207 && \
cat ../sgmlop*.patch | patch -sup1 && \
python setup.py build && \
cd .. && \
tar xzf scintilla210.tgz && \
find . -name "LexTCL*" | xargs rm
cd scintilla && \
cat ../scintilla.patch/*.patch | patch -sup0 && \
cp -f ../scintilla.patch/src/* src/ && \
cp -f ../scintilla.patch/include/* include/ && \
cd .. && \
tar xzf SilverCity-0.9.7.tar.gz && \
cd SilverCity-0.9.7 && \
cat ../SilverCity.patch/*.patch | patch -sup1 && \
cp -f ../SilverCity.patch/*.py PySilverCity/SilverCity/ && \
python setup.py build && \
cd .. && \
tar xzf cElementTree-1.0.5-20051216.tar.gz && \
cd cElementTree-1.0.5-20051216 && \
cat ../cElementTree-1.0.5-20051216.patch/*.patch | patch -sup1 && \
python setup.py build && \
cd .. && \
find . -type f -name sgmlop.so -exec cp {} ../libs/_local_arch \; && \
find . -type f -name _SilverCity.so -exec cp {} ../libs/_local_arch \; && \
find . -type f -name ciElementTree.so -exec cp {} ../libs/_local_arch \; && \
rm -rf cElementTree-1.0.5-20051216 && \
rm -rf SilverCity-0.9.7 && \
rm -rf scintilla && \
rm -rf sgmlop-1.1.1-20040207 && \
echo "Done!"
