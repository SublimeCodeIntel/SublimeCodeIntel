import sys
import sublime

VERSION = sys.version_info[:2]  # Python version
PLATFORM = sublime.platform()  # String  Returns the platform, which may be "osx", "linux" or "windows"
ARCH = sublime.arch()  # String  Returns the CPU architecture, which may be "x32" or "x64"

platform = None

try:
    from _local_arch._SilverCity import *
    platform = "Local arch"
except ImportError:
    if VERSION >= (3, 3):
        if PLATFORM == 'osx':
            from _macosx_universal_py33._SilverCity import *
            platform = "MacOS X Universal"
        elif PLATFORM == 'linux':
            if ARCH == 'x64':
                from _linux_libcpp6_x86_64_py33._SilverCity import *
                platform = "Linux 64 bits"
            elif ARCH == 'x32':
                from _linux_libcpp6_x86_py33._SilverCity import *
                platform = "Linux 32 bits"
        elif PLATFORM == 'windows':
            if ARCH == 'x64':
                from _win64_py33._SilverCity import *
                platform = "Windows 64 bits"
            elif ARCH == 'x32':
                from _win32_py33._SilverCity import *
                platform = "Windows 32 bits"
    elif VERSION >= (2, 6):
        if PLATFORM == 'osx':
            from _macosx_universal_py26._SilverCity import *
            platform = "MacOS X Universal"
        elif PLATFORM == 'linux':
            if ARCH == 'x64':
                from _linux_libcpp6_x86_64_py26._SilverCity import *
                platform = "Linux 64 bits"
            elif ARCH == 'x32':
                from _linux_libcpp6_x86_py26._SilverCity import *
                platform = "Linux 32 bits"
        elif PLATFORM == 'windows':
            if ARCH == 'x64':
                from _win64_py26._SilverCity import *
                platform = "Windows 64 bits"
            elif ARCH == 'x32':
                from _win32_py26._SilverCity import *
                platform = "Windows 32 bits"

if not platform:
    raise ImportError("Could not find a suitable _SilverCity binary for your platform and architecture.")
