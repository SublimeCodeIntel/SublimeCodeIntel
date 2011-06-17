#!/bin/sh
# In Linux, Sublime Text's Python is compiled with UCS4, add:
# CFLAGS=-DPy_UNICODE_SIZE 4
unzip sgmlop-1.1.1-20040207.zip && \
cd sgmlop-1.1.1-20040207 && \
cat ../sgmlop*.patch | patch -sup1 && \
python setup.py build && \
cd .. && \
tar xzf scintilla210.tgz && \
cd scintilla && \
cat ../scintilla*.patch | patch -sup1 && \
cd .. && \
tar xzf SilverCity-0.9.7.tar.gz && \
cd SilverCity-0.9.7 && \
cat ../SilverCity*.patch | patch -sup1 && \
python setup.py build && \
cd .. && \
tar xzf cElementTree-1.0.5-20051216.tar.gz && \
cd cElementTree-1.0.5-20051216 && \
cat ../cElementTree-1.0.5-20051216.patch/*.patch | patch -sup1 && \
python setup.py build && \
cd .. && \
find . -type f -name sgmlop.so -exec cp {} ../libs/_local_arch \; && \
find . -type f -name _SilverCity.so -exec cp {} ../libs/_local_arch \; && \
find . -type f -name ciElementTree.so -exec cp {} ../libs/_local_arch \; &&\
rm -rf cElementTree-1.0.5-20051216 &&\
rm -rf SilverCity-0.9.7 &&\
rm -rf scintilla
