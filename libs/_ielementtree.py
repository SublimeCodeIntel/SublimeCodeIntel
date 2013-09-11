import sys
import struct

VERSION = sys.version_info[:2]
PLATFORM = sys.platform
ARCH = 'x%d' % (struct.calcsize('P') * 8)

if VERSION >= (3, 3):
    platform = None

    try:
        from _local_arch._ielementtree import *
        platform = "Local arch"
    except ImportError:
        if PLATFORM == 'darwin':
            from _macosx_universal_py33._ielementtree import *
            platform = "MacOS X Universal"
        elif PLATFORM.startswith('linux'):
            if ARCH == 'x64':
                from _linux_libcpp6_x86_64_py33._ielementtree import *
                platform = "Linux 64 bits"
            elif ARCH == 'x32':
                from _linux_libcpp6_x86_py33._ielementtree import *
                platform = "Linux 32 bits"
        elif PLATFORM.startswith('win'):
            if ARCH == 'x64':
                from _win64_py33._ielementtree import *
                platform = "Windows 64 bits"
            elif ARCH == 'x32':
                from _win32_py33._ielementtree import *
                platform = "Windows 32 bits"
    if not platform:
        raise ImportError("Could not find a suitable _ielementtree binary for your platform and architecture.")
elif VERSION >= (2, 6):
    from ciElementTree import *
    from ciElementTree import _patched_for_komodo_
