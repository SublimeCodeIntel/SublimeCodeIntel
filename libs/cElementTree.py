import sys
import struct

VERSION = sys.version_info[:2]
PLATFORM = sys.platform
ARCH = 'x%d' % (struct.calcsize('P') * 8)

platform = None

try:
    from _local_arch.cElementTree import *
    platform = "Local arch"
except ImportError:
    if VERSION >= (3, 3):
        if PLATFORM == 'darwin':
            from _macosx_universal_py33.cElementTree import *
            platform = "MacOS X Universal"
        elif PLATFORM == 'linux2':
            if ARCH == 'x64':
                from _linux_libcpp6_x86_64_py33.cElementTree import *
                platform = "Linux 64 bits"
            elif ARCH == 'x32':
                from _linux_libcpp6_x86_py33.cElementTree import *
                platform = "Linux 32 bits"
        elif PLATFORM == 'windows':
            if ARCH == 'x64':
                from _win64_py33.cElementTree import *
                platform = "Windows 64 bits"
            elif ARCH == 'x32':
                from _win32_py33.cElementTree import *
                platform = "Windows 32 bits"
    elif VERSION >= (2, 6):
        if PLATFORM == 'darwin':
            from _macosx_universal_py26.cElementTree import *
            platform = "MacOS X Universal"
        elif PLATFORM == 'linux2':
            if ARCH == 'x64':
                from _linux_libcpp6_x86_64_py26.cElementTree import *
                platform = "Linux 64 bits"
            elif ARCH == 'x32':
                from _linux_libcpp6_x86_py26.cElementTree import *
                platform = "Linux 32 bits"
        elif PLATFORM == 'windows':
            if ARCH == 'x64':
                from _win64_py26.cElementTree import *
                platform = "Windows 64 bits"
            elif ARCH == 'x32':
                from _win32_py26.cElementTree import *
                platform = "Windows 32 bits"

if not platform:
    raise ImportError("Could not find a suitable cElementTree binary for your platform and architecture.")
