"""
Memory reporting command handler
"""

import ctypes
import logging
import sys
from .driver import CommandHandler

log = logging.getLogger("codeintel.oop.memory-reporter")


class _BaseMemoryCommandHandler(CommandHandler):
    """Base memory report handler
    This handler supports a single command, "memory-report"; this command takes
    no arguments, and returns a single value, "memory"; this is a dictionary.
    Each key of the dictionary is a path of the memory being reported, and the
    value is yet another dictionary with the keys:
        "amount" (int): The amount being reported.
        "units" (str): Either "bytes" or "count"; quantifies the amount.
        "desc" (str): A description of this value.  Must be a sentence.
    """

    supportedCommands = ("memory-report",)

    def canHandleRequest(self, request):
        return request["command"] == "memory-report"

    def handleRequest(self, request, driver):
        assert request["command"] == "memory-report", "Invalid command"
        self.do_memory_report(request, driver)

    def do_memory_report(self, request, driver):
        log.debug("collecting memory reports")
        driver.send(memory=self._get_memory_report(driver))

    def _get_memory_report(self, driver):
        import gc
        import memutils
        gc.collect()
        total = memutils.memusage(gc.get_objects())

        def try_call(method):
            try:
                return method()
            except Exception as ex:
                log.exception(ex)
                return None

        results = {}
        for zone in driver.mgr.db.get_all_zones():
            try:
                results.update(zone.reportMemory())
            except:
                log.exception("Failed to report memory for zone %r", zone)

        for path, data in results.items():
            if path.startswith("explicit/python"):
                if data["units"] == "bytes":
                    total -= data["amount"]

        results["explicit/python/unclassified-objects"] = {
            "amount": total,
            "units": "bytes",
            "desc": "Total bytes used by Python objects.",
        }
        results["vsize"] = {
            "amount": try_call(self._get_virtual_size),
            "units": "bytes",
            "desc": "Memory mapped by the code intelligence process.",
        }
        results["resident"] = {
            "amount": try_call(self._get_resident_size),
            "units": "bytes",
            "desc": "Resident set size in the code intelligence process.",
        }
        results["heap-allocated"] = {
            "amount": try_call(self._get_heap_size),
            "units": "bytes",
            "desc": "The total size of the heap."
        }

        return results

    def _get_virtual_size(self):
        """Get the virual size of this process (everything mapped).
        @returns {long} The vsize, in bytes; or None if unavailable.
        """
        return None

    def _get_resident_size(self):
        """Get the resident set size; this is the subset of vsize that is in
        physical memory (and not mapped to a file on disk).
        @returns {long} The rss, in bytes; or None if unavailable.
        """
        return None

    def _get_heap_size(self):
        """Get the size of the heap.
        @returns {long} The size of the heap, in bytes; or None if unavailable.
        """
        return None

MemoryCommandHandler = _BaseMemoryCommandHandler

if sys.platform.startswith("win"):
    from ctypes import wintypes

    class Win32MemoryHandler(_BaseMemoryCommandHandler):
        def _get_virtual_size(self):
            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [("dwLength", wintypes.DWORD),
                            ("dwMemoryLoad", wintypes.DWORD),
                            ("ullTotalPhys", ctypes.c_uint64),
                            ("ullAvailPhys", ctypes.c_uint64),
                            ("ullTotalPageFile", ctypes.c_uint64),
                            ("ullAvailPageFile", ctypes.c_uint64),
                            ("ullTotalVirtual", ctypes.c_uint64),
                            ("ullAvailVirtual", ctypes.c_uint64),
                            ("ullAvailExtendedVirtual", ctypes.c_uint64)]

                def __init__(self):
                    ctypes.Structure.__init__(self)
                    self.dwLength = ctypes.sizeof(self)

            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            GlobalMemoryStatusEx = kernel32.GlobalMemoryStatusEx
            GlobalMemoryStatusEx.restype = wintypes.BOOL
            GlobalMemoryStatusEx.argtypes = [ctypes.POINTER(MEMORYSTATUSEX)]

            status = MEMORYSTATUSEX()
            if GlobalMemoryStatusEx(status):
                return status.ullTotalVirtual - status.ullAvailVirtual
            return None

        def _get_resident_size(self):
            class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
                _fields_ = [("cb", wintypes.DWORD),
                            ("PageFaultCount", wintypes.DWORD),
                            ("PeakWorkingSetSize", ctypes.c_size_t),
                            ("WorkingSetSize", ctypes.c_size_t),
                            ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                            ("QuotaPagedPoolUsage", ctypes.c_size_t),
                            ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                            ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                            ("PagefileUsage", ctypes.c_size_t),
                            ("PeakPagefileUsage", ctypes.c_size_t)]

                def __init__(self):
                    ctypes.Structure.__init__(self)
                    self.cb = ctypes.sizeof(self)

            psapi = ctypes.WinDLL("psapi", use_last_error=True)
            GetProcessMemoryInfo = psapi.GetProcessMemoryInfo
            GetProcessMemoryInfo.restype = wintypes.BOOL
            GetProcessMemoryInfo.argtypes = [wintypes.HANDLE,
                                             ctypes.POINTER(
                                                 PROCESS_MEMORY_COUNTERS),
                                             wintypes.DWORD]
            counters = PROCESS_MEMORY_COUNTERS()
            if GetProcessMemoryInfo(-1, counters, ctypes.sizeof(counters)):
                return counters.WorkingSetSize
            return None

        def _get_heap_size(self):
            class PROCESS_HEAP_ENTRY_BLOCK(ctypes.Structure):
                _fields_ = [("hMem", wintypes.HANDLE),
                            ("dwReserved", wintypes.DWORD * 3)]

            class PROCESS_HEAP_ENTRY_REGION(ctypes.Structure):
                _fields_ = [("dwCommittedSize", wintypes.DWORD),
                            ("dwUnCommittedSize", wintypes.DWORD),
                            ("lpFirstBlock", wintypes.LPVOID),
                            ("lpLastBlock", wintypes.LPVOID)]

            class PROCESS_HEAP_ENTRY_UNION(ctypes.Union):
                _fields_ = [("Block", PROCESS_HEAP_ENTRY_BLOCK),
                            ("Region", PROCESS_HEAP_ENTRY_REGION)]

            class PROCESS_HEAP_ENTRY (ctypes.Structure):
                _anonymous_ = ("u",)
                _fields_ = [("lpData", wintypes.LPVOID),
                            ("cbData", wintypes.DWORD),
                            ("cbOverhead", wintypes.BYTE),
                            ("iRegionIndex", wintypes.BYTE),
                            ("wFlags", wintypes.WORD),
                            ("u", PROCESS_HEAP_ENTRY_UNION)]

            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            GetProcessHeaps = kernel32.GetProcessHeaps
            GetProcessHeaps.restype = wintypes.DWORD
            GetProcessHeaps.argtypes = [wintypes.DWORD,
                                        ctypes.POINTER(wintypes.HANDLE)]
            HeapWalk = kernel32.HeapWalk
            HeapWalk.restype = wintypes.BOOL
            HeapWalk.argtypes = [
                wintypes.HANDLE, ctypes.POINTER(PROCESS_HEAP_ENTRY)]

            heapCount = GetProcessHeaps(0, None)
            if not heapCount:
                log.error(
                    "Failed to get heap count: %r", ctypes.get_last_error())
                return None  # Failed; don't care
            heaps = (wintypes.HANDLE * heapCount)()
            heapCount = GetProcessHeaps(len(heaps), heaps)
            if heapCount == 0:
                log.error("Failed to get heaps: %r", ctypes.get_last_error())

            total_data = 0
            total_overhead = 0

            for heap in heaps[:heapCount]:
                entry = PROCESS_HEAP_ENTRY()
                entry.lpData = None
                while HeapWalk(heap, entry):
                    total_data += entry.cbData
                    total_overhead += entry.cbOverhead

            return total_data + total_overhead

    MemoryCommandHandler = Win32MemoryHandler

elif sys.platform.startswith("linux"):
    class LinuxMemoryHandler(_BaseMemoryCommandHandler):
        def __init__(self):
            super(LinuxMemoryHandler, self).__init__()
            import ctypes.util
            self.libc = ctypes.CDLL(ctypes.util.find_library("c"))

        def _get_virtual_size(self):
            try:
                with open("/proc/self/statm", "r") as f:
                    vsize, rss = f.read().split()[:2]
                    return long(vsize, 10) * self.libc.getpagesize()
            except Exception as ex:
                log.exception("Failed to get vsize: %r", ex)

        def _get_resident_size(self):
            try:
                with open("/proc/self/statm", "r") as f:
                    vsize, rss = f.read().split()[:2]
                    return long(rss, 10) * self.libc.getpagesize()
            except Exception as ex:
                log.exception("Failed to get rss: %r", ex)

        def _get_mallinfo(self):
            class mallinfo_t(ctypes.Structure):
                _fields_ = [("arena", ctypes.c_int),
                            ("ordblks", ctypes.c_int),
                            ("smblks", ctypes.c_int),
                            ("hblks", ctypes.c_int),
                            ("hblkhd", ctypes.c_int),
                            ("usmblks", ctypes.c_int),
                            ("fsmblks", ctypes.c_int),
                            ("uordblks", ctypes.c_int),
                            ("fordblks", ctypes.c_int),
                            ("keepcost", ctypes.c_int)]
            mallinfo = self.libc.mallinfo
            mallinfo.restype = mallinfo_t
            mallinfo.argtypes = []
            return mallinfo()

        def _get_heap_size(self):
            return self._get_mallinfo().arena

        def _get_memory_report(self, driver):
            results = super(
                LinuxMemoryHandler, self)._get_memory_report(driver)
            info = self._get_mallinfo()
            results["explicit/heap-overhead"] = {
                "amount": info.arena - info.uordblks - info.fordblks,
                "units": "bytes",
                "desc": "This is the memory allocator overhead.",
            }
            return results

    MemoryCommandHandler = LinuxMemoryHandler

elif sys.platform == "darwin":
    class DarwinMemoryHandler(_BaseMemoryCommandHandler):
        def _get_taskinfo(self):
            integer_t = ctypes.c_int
            natural_t = ctypes.c_uint
            vm_size_t = ctypes.c_ulong

            class time_value_t(ctypes.Structure):
                _fields_ = [("seconds", integer_t),
                            ("microseconds", integer_t)]

                def __repr__(self):
                    return "%s.%s" % (self.seconds, self.microseconds)

            policy_t = ctypes.c_int

            class task_basic_info(ctypes.Structure):
                _pack_ = 4
                _fields_ = [("suspend_count", integer_t),
                            ("virtual_size", vm_size_t),
                            ("resident_size", vm_size_t),
                            ("user_time", time_value_t),
                            ("system_time", time_value_t),
                            ("policy", policy_t)]

                def __repr__(self):
                    return repr(dict((key, getattr(self, key))
                                     for key in dir(self)
                                     if not key.startswith("_")))

            kern_return_t = ctypes.c_int
            mach_port_t = natural_t
            task_name_t = ctypes.c_uint
            task_flavor_t = ctypes.c_uint
            task_info_t = ctypes.POINTER(ctypes.c_int)
            mach_msg_type_number_t = natural_t
            TASK_BASIC_INFO_COUNT = ctypes.sizeof(
                task_basic_info) / ctypes.sizeof(natural_t)
            TASK_BASIC_INFO = 5
            KERN_SUCCESS = 0

            libkern = ctypes.CDLL("/usr/lib/system/libsystem_kernel.dylib")
            task_info = libkern.task_info
            task_info.restype = kern_return_t
            task_info.argtypes = [task_name_t,
                                  task_flavor_t,
                                  ctypes.POINTER(task_basic_info),
                                  ctypes.POINTER(mach_msg_type_number_t)]

            mach_task_self = libkern.mach_task_self
            mach_task_self.restype = mach_port_t
            mach_task_self.argtypes = []

            ti = task_basic_info()

            count = mach_msg_type_number_t(TASK_BASIC_INFO_COUNT)
            kr = task_info(mach_task_self(), TASK_BASIC_INFO,
                           ctypes.byref(ti),
                           ctypes.byref(count))
            if kr != KERN_SUCCESS:
                return None
            return ti

        def _get_virtual_size(self):
            ti = self._get_taskinfo()
            return ti.virtual_size or None if ti else None

        def _get_resident_size(self):
            ti = self._get_taskinfo()
            return ti.resident_size or None if ti else None

        def _get_heap_size(self):
            # Unforunately, I haven't found any sane ways of figuring out our
            # heap size; asking vmmap for data gives us an approximation (though
            # I'm pretty sure it's not the number we want).
            import os
            import subprocess
            stdout = subprocess.check_output(["/usr/bin/vmmap",
                                              "-pages", "-wide",
                                              str(os.getpid())])
            log.debug("stdout:\n%s", stdout)
            lines = iter(stdout.splitlines())
            header = ["MALLOC", "ZONE", "PAGES",
                      "COUNT", "ALLOCATED", "%", "FULL"]
            while lines.next().split() != header:
                pass
            for line in lines:
                if line.startswith("TOTAL "):
                    size = line.split()[3]
                    suffixes = {"B": 1,
                                "K": 1024,
                                "M": 1024 ** 2,
                                "G": 1024 ** 3,
                                "T": 1024 ** 4}
                    if size[-1] in suffixes:
                        size = float(size[:-1]) * suffixes[size[-1]]
                    else:
                        size = float(size)
                    return size

    MemoryCommandHandler = DarwinMemoryHandler
