#!/usr/bin/env python2

# Win32 named pipe helper

from __future__ import absolute_import
from six.moves import range
__all__ = ["Win32Pipe"]

import sys
import ctypes
import logging
import random
from ctypes import POINTER as PTR
from ctypes.wintypes import (BOOL, DWORD, HANDLE, LPCWSTR, LPVOID, LPCVOID)
class OVERLAPPED(ctypes.Structure):
    class PointerUnion(ctypes.Union):
        class OffsetStruct(ctypes.Structure):
            _fields_ = [("Offset", DWORD),
                        ("OffsetHigh", DWORD)]
        _anonymous_ = ("s",)
        _fields_ = [("s", OffsetStruct),
                    ("Pointer", LPVOID)]
    _anonymous_ = ("u",)
    _fields_ = [("Internal", LPVOID),
                ("InternalHigh", LPVOID),
                ("u", PointerUnion),
                ("hEvent", HANDLE)]
    def __init__(self):
        super(OVERLAPPED, self).__init__(Offset=0, OffsetHigh=0,
                                         Pointer=0, Internal=0,
                                         InternalHigh=0, hEvent=None)
        self.hEvent = CreateEvent(None, True, False, None)
LPOVERLAPPED = ctypes.POINTER(OVERLAPPED)

log = logging.getLogger("py.win32_named_pipe")

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
def _decl(name, ret=None, args=()):
    fn = getattr(kernel32, name)
    fn.restype = ret
    fn.argtypes = args
    return fn

CloseHandle = _decl("CloseHandle", BOOL, (HANDLE,))
CreateEvent = _decl("CreateEventW", HANDLE, (LPVOID, BOOL, BOOL, LPCWSTR))
CreateFile = _decl("CreateFileW", HANDLE, (LPCWSTR, DWORD, DWORD,
                                           LPVOID, DWORD, DWORD, HANDLE))
CreateNamedPipe = _decl("CreateNamedPipeW", HANDLE,
                        (LPCWSTR, DWORD, DWORD, DWORD, DWORD, DWORD,
                         DWORD, LPVOID))
ConnectNamedPipe = _decl("ConnectNamedPipe", BOOL, (HANDLE, LPOVERLAPPED))
WriteFile = _decl("WriteFile", BOOL, (HANDLE, LPCVOID, DWORD,
                                      PTR(DWORD), PTR(OVERLAPPED)))
ReadFile = _decl("ReadFile", BOOL, (HANDLE, LPVOID, DWORD,
                                    PTR(DWORD), PTR(OVERLAPPED)))
GetOverlappedResult = _decl("GetOverlappedResult", BOOL,
                            (HANDLE, PTR(OVERLAPPED), PTR(DWORD), BOOL))
ERROR_ACCESS_DENIED = 5
ERROR_IO_PENDING = 997
FILE_FLAG_OVERLAPPED = 0x40000000
FILE_FLAG_FIRST_PIPE_INSTANCE = 0x00080000
GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
INVALID_HANDLE_VALUE = -1
OPEN_EXISTING = 3
PIPE_ACCESS_DUPLEX = 0x00000003
PIPE_READMODE_BYTE = 0x00000000
PIPE_REJECT_REMOTE_CLIENTS = 0x00000008
PIPE_TYPE_BYTE = 0x00000000

del _decl

class Win32Pipe(object):
    """This class implements a Win32 named pipe; it has a file-like API.  It is
    oriented towards byte streams.

    Usage:
        pipe = Win32Pipe() # Create a new pipe with a randomly generated name
        pipe = Win32Pipe("name") # Create a new pipe, \\.\pipe\name
        pipe = Win32Pipe("name", client=True) # Connect to an existing pipe
    """

    name = None ###< The name of the pipe
    _has_stream = False ###< Whether we have connected to the other end yet
    _pipe = None ###< The underlying Win32 handle
    pipe_prefix = None ###< Prefix to place before randomly generated pipe names

    def __init__(self, name=None, client=False):
        if client:
            self._connect_to_existing(name=name)
        else:
            self._create(name=name)

    def _create(self, name=None):
        """Create a new pipe as a server, with the given name"""
        self._has_stream = False
        flags = (PIPE_ACCESS_DUPLEX |
                 FILE_FLAG_FIRST_PIPE_INSTANCE |
                 FILE_FLAG_OVERLAPPED)

        mode = PIPE_TYPE_BYTE | PIPE_READMODE_BYTE
        # Windows XP, version (5, 1) doesn't support PIPE_REJECT_REMOTE_CLIENTS
        # see bug 104569.
        if sys.getwindowsversion() >= (5, 2):
            mode |= PIPE_REJECT_REMOTE_CLIENTS

        pipe_prefix = "\\\\.\\pipe\\"
        if name is not None:
            if not name.lower().startswith(pipe_prefix):
                name = pipe_prefix + name
            log.debug("Creating new named pipe %s", name)
            self._pipe = CreateNamedPipe(name, flags, mode, 1, 0x1000, 0x1000,
                                         0, None)
            if self._pipe == INVALID_HANDLE_VALUE:
                self._pipe = None
                raise ctypes.WinError(ctypes.get_last_error())
        else:
            bits = min((256, (255 - len(pipe_prefix)) * 4))
            start = random.getrandbits(bits)
            log.debug("Trying to create pipe with randomness %s",
                      hex(start))
            # Try a few variations on the name in case it's somehow taken
            for i in range(1024):
                name = (pipe_prefix + (self.pipe_prefix or "") +
                        hex(start + i)[2:-1])
                assert len(name) <= 256
                # Unfortuantely, it is more reliable to create a nowait pipe
                # and poll for it than it is to create a blocking pipe.
                self._pipe = CreateNamedPipe(name, flags, mode, 1, 0x1000,
                                             0x1000, 0, None)
                if self._pipe != INVALID_HANDLE_VALUE:
                    break
                self._pipe = None
                errno = ctypes.get_last_error()
                if errno != ERROR_ACCESS_DENIED:
                    # we get access denied on a name collision
                    raise ctypes.WinError(errno)
            else:
                raise ctypes.WinError(ctypes.get_last_error())
        self.name = name

    def _connect_to_existing(self, name):
        self._has_stream = False
        pipe_prefix = "\\\\.\\pipe\\"
        if not name.lower().startswith(pipe_prefix):
            name = pipe_prefix + name
        log.debug("Connecting to existing named pipe %s", name)
        self._pipe = CreateFile(name,
                                GENERIC_READ | GENERIC_WRITE,
                                0,
                                None,
                                OPEN_EXISTING,
                                FILE_FLAG_OVERLAPPED,
                                None)
        if self._pipe == INVALID_HANDLE_VALUE:
            self._pipe = None
            error = ctypes.WinError(ctypes.get_last_error())
            log.debug("Failed to open pipe %s: %s", name, error)
            raise error
        self._has_stream = True

    def _ensure_stream(self, action="open"):
        if self._pipe is None:
            raise IOError("Cannot %s closed pipe" % (action,))
        if self._has_stream:
            return
        overlapped = OVERLAPPED()
        try:
            if not ConnectNamedPipe(self._pipe, overlapped):
                errno = ctypes.get_last_error()
                if errno != ERROR_IO_PENDING:
                    raise ctypes.WinError(errno)
            if not GetOverlappedResult(self._pipe, overlapped,
                                       ctypes.byref(DWORD(0)), True):
                raise ctypes.WinError(ctypes.get_last_error())
            self._has_stream = True
        finally:
            CloseHandle(overlapped.hEvent)

    def write(self, data):
        self._ensure_stream("write to")
        overlapped = OVERLAPPED()
        try:
            if not WriteFile(self._pipe, data, len(data), None,
                             ctypes.byref(overlapped)):
                errno = ctypes.get_last_error()
                if errno != ERROR_IO_PENDING:
                    raise ctypes.WinError(errno)
            written = DWORD(0)
            if not GetOverlappedResult(self._pipe,
                                       ctypes.byref(overlapped),
                                       ctypes.byref(written),
                                       True):
                raise ctypes.WinError(ctypes.get_last_error())
            assert written.value == len(data), "Incomplete write"
        finally:
            CloseHandle(overlapped.hEvent)

    def read(self, count):
        self._ensure_stream("read from")
        overlapped = OVERLAPPED()
        try:
            buf = ctypes.create_string_buffer(count)
            if not ReadFile(self._pipe, ctypes.byref(buf), count,
                            None, ctypes.byref(overlapped)):
                errno = ctypes.get_last_error()
                if errno != ERROR_IO_PENDING:
                    raise ctypes.WinError(errno)
            read = DWORD(0)
            if not GetOverlappedResult(self._pipe,
                                       ctypes.byref(overlapped),
                                       ctypes.byref(read),
                                       True):
                raise ctypes.WinError(ctypes.get_last_error())
            assert read.value == count
            return str(buf.value)
        finally:
            CloseHandle(overlapped.hEvent)

    def close(self):
        CloseHandle(self._pipe)
        self._pipe = None

