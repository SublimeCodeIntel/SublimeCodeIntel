try:
    from _local_arch.cElementTree import *
    platform = "Local arch"
except ImportError:
    try:
        from _linux_libcpp6_x86_64.cElementTree import *
        platform = "Linux 64 bits"
    except ImportError:
        try:
            from _linux_libcpp6_x86.cElementTree import *
            platform = "Linux 32 bits"
        except ImportError:
            try:
                from _win64.cElementTree import *
                platform = "Windows 64 bits"
            except ImportError:
                try:
                    from _win32.cElementTree import *
                    platform = "Windows 32 bits"
                except ImportError:
                    try:
                        from _macosx_universal.cElementTree import *
                        platform = "MacOS X Universal"
                    except ImportError:
                        raise ImportError("Could not find a suitable cElementTree binary for your platform and architecture.")
