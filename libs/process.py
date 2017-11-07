from __future__ import absolute_import
# ***** BEGIN LICENSE BLOCK *****
# Version: MPL 1.1/GPL 2.0/LGPL 2.1
# 
# The contents of this file are subject to the Mozilla Public License
# Version 1.1 (the "License"); you may not use this file except in
# compliance with the License. You may obtain a copy of the License at
# http://www.mozilla.org/MPL/
# 
# Software distributed under the License is distributed on an "AS IS"
# basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See the
# License for the specific language governing rights and limitations
# under the License.
# 
# The Original Code is Komodo code.
# 
# The Initial Developer of the Original Code is ActiveState Software Inc.
# Portions created by ActiveState Software Inc are Copyright (C) 2000-2007
# ActiveState Software Inc. All Rights Reserved.
# 
# Contributor(s):
#   ActiveState Software Inc
# 
# Alternatively, the contents of this file may be used under the terms of
# either the GNU General Public License Version 2 or later (the "GPL"), or
# the GNU Lesser General Public License Version 2.1 or later (the "LGPL"),
# in which case the provisions of the GPL or the LGPL are applicable instead
# of those above. If you wish to allow use of your version of this file only
# under the terms of either the GPL or the LGPL, and not to allow others to
# use your version of this file under the terms of the MPL, indicate your
# decision by deleting the provisions above and replace them with the notice
# and other provisions required by the GPL or the LGPL. If you do not delete
# the provisions above, a recipient may use your version of this file under
# the terms of any one of the MPL, the GPL or the LGPL.
# 
# ***** END LICENSE BLOCK *****

import os
import sys
import time
import types
if sys.platform != "win32":
    import signal  # used by kill() method on Linux/Mac
import logging
import threading
import warnings

PY2 = sys.version_info[0] == 2
if PY2:
    string_types = basestring
else:
    string_types = str

#-------- Globals -----------#

log = logging.getLogger("process")
#log.setLevel(logging.DEBUG)

try:
    from subprocess32 import Popen, PIPE
except ImportError:
    # Not available on Windows - fallback to using regular subprocess module.
    from subprocess import Popen, PIPE
    if sys.platform != "win32" and sys.version_info[0] != 3:
        log.warn("Could not import subprocess32 module, falling back to subprocess module")

try:
    from xpcom import components
except ImportError as e:
    class components:
        @staticmethod
        def ProxyToMainThread(fn):
            return fn

CREATE_NEW_CONSOLE = 0x10 # same as win32process.CREATE_NEW_CONSOLE
CREATE_NEW_PROCESS_GROUP = 0x200 # same as win32process.CREATE_NEW_PROCESS_GROUP
CREATE_NO_WINDOW = 0x8000000 # same as win32process.CREATE_NO_WINDOW
CTRL_BREAK_EVENT = 1 # same as win32con.CTRL_BREAK_EVENT
WAIT_TIMEOUT = 258 # same as win32event.WAIT_TIMEOUT


#-------- Classes -----------#

# XXX - TODO: Work out what exceptions raised by SubProcess and turn into
#       ProcessError?
class ProcessError(Exception):
    def __init__(self, msg, errno=-1):
        Exception.__init__(self, msg)
        self.errno = errno


if sys.platform.startswith("win"):
    import subprocess

    # In Python 3 on Windows, a lot of the functions previously
    # in _subprocess moved to _winapi
    _subprocess = getattr(subprocess, '_subprocess', None)
    _winapi = getattr(subprocess, '_winapi', None)

    def subprocess_import(attr):
        for mod in (subprocess, _subprocess, _winapi):
            value = getattr(mod, attr, None)
            if value is not None:
                return value
        raise ImportError

    GetStdHandle = subprocess_import('GetStdHandle')
    STD_INPUT_HANDLE = subprocess_import('STD_INPUT_HANDLE')
    STD_OUTPUT_HANDLE = subprocess_import('STD_OUTPUT_HANDLE')
    STD_ERROR_HANDLE = subprocess_import('STD_ERROR_HANDLE')

    # Python 3 has Handle and CloseHandle
    try:
        Handle = subprocess_import('Handle')
        CloseHandle = subprocess_import('CloseHandle')
    except ImportError:
        pass

# Check if this is Windows NT and above.
if sys.platform == "win32" and sys.getwindowsversion()[3] == 2:
    try:
        from . import winprocess
    except:
        import winprocess

    try:
        # These subprocess variables have moved around between Python versions.
        list2cmdline = subprocess_import('list2cmdline')
        STARTUPINFO = subprocess_import('STARTUPINFO')
        SW_HIDE = subprocess_import('SW_HIDE')
        STARTF_USESTDHANDLES = subprocess_import('STARTF_USESTDHANDLES')
        STARTF_USESHOWWINDOW = subprocess_import('STARTF_USESHOWWINDOW')
        GetVersion = subprocess_import('GetVersion')
        CreateProcess = subprocess_import('CreateProcess')
    except ImportError:
        pass
    else:

        # This fix is for killing child processes on windows, based on:
        #   http://www.microsoft.com/msj/0698/win320698.aspx
        # It works by creating a uniquely named job object that will contain our
        # process(es), starts the process in a suspended state, maps the process
        # to a specific job object, resumes the process, from now on every child
        # it will create will be assigned to the same job object. We can then
        # later terminate this job object (and all of it's child processes).
        #
        # This code is based upon Benjamin Smedberg's killableprocess, see:
        #   http://benjamin.smedbergs.us/blog/2006-12-11/killableprocesspy/

        class WindowsKillablePopen(Popen):

            _job = None

            if sys.version_info[:2] == (2, 6):

                def _execute_child(self, args, executable, preexec_fn, close_fds,
                                cwd, env, universal_newlines,
                                startupinfo, creationflags, shell,
                                p2cread, p2cwrite,
                                c2pread, c2pwrite,
                                errread, errwrite):
                    """Execute program (MS Windows version)"""

                    if not isinstance(args, string_types):
                        args = list2cmdline(args)

                    # Process startup details
                    if startupinfo is None:
                        startupinfo = STARTUPINFO()
                    if None not in (p2cread, c2pwrite, errwrite):
                        startupinfo.dwFlags |= STARTF_USESTDHANDLES
                        startupinfo.hStdInput = p2cread
                        startupinfo.hStdOutput = c2pwrite
                        startupinfo.hStdError = errwrite

                    if shell:
                        startupinfo.dwFlags |= STARTF_USESHOWWINDOW
                        startupinfo.wShowWindow = SW_HIDE
                        comspec = os.environ.get("COMSPEC", "cmd.exe")
                        args = comspec + " /c " + args
                        if (GetVersion() >= 0x80000000 or
                                os.path.basename(comspec).lower() == "command.com"):
                            # Win9x, or using command.com on NT. We need to
                            # use the w9xpopen intermediate program. For more
                            # information, see KB Q150956
                            # (http://web.archive.org/web/20011105084002/http://support.microsoft.com/support/kb/articles/Q150/9/56.asp)
                            w9xpopen = self._find_w9xpopen()
                            args = '"%s" %s' % (w9xpopen, args)
                            # Not passing CREATE_NEW_CONSOLE has been known to
                            # cause random failures on win9x.  Specifically a
                            # dialog: "Your program accessed mem currently in
                            # use at xxx" and a hopeful warning about the
                            # stability of your system.  Cost is Ctrl+C wont
                            # kill children.
                            creationflags |= CREATE_NEW_CONSOLE

                        # We create a new job for this process, so that we can kill
                        # the process and any sub-processes
                        self._job = winprocess.CreateJobObject()
                        creationflags |= winprocess.CREATE_SUSPENDED
                        # Vista will launch Komodo in a job object itself, so we need
                        # to specify that the created process is not part of the Komodo
                        # job object, but instead specify that it will be using a
                        # separate breakaway job object, bug 83001.
                        creationflags |= winprocess.CREATE_BREAKAWAY_FROM_JOB

                    # Start the process
                    try:
                        hp, ht, pid, tid = CreateProcess(executable, args,
                                                # no special security
                                                None, None,
                                                int(not close_fds),
                                                creationflags,
                                                env,
                                                cwd,
                                                startupinfo)
                    except IOError as e:  # From 2.6 on, pywintypes.error was defined as IOError
                        # Translate pywintypes.error to WindowsError, which is
                        # a subclass of OSError.  FIXME: We should really
                        # translate errno using _sys_errlist (or similar), but
                        # how can this be done from Python?
                        raise WindowsError(*e.args)
                    except WindowsError:
                        log.error("process.py: can't execute %r (%s)", executable, args)
                        raise
                    finally:
                        # Child is launched. Close the parent's copy of those pipe
                        # handles that only the child should have open.  You need
                        # to make sure that no handles to the write end of the
                        # output pipe are maintained in this process or else the
                        # pipe will not close when the child process exits and the
                        # ReadFile will hang.
                        if p2cread is not None:
                            p2cread.Close()
                        if c2pwrite is not None:
                            c2pwrite.Close()
                        if errwrite is not None:
                            errwrite.Close()

                    # Retain the process handle, but close the thread handle
                    self._child_created = True
                    self._handle = hp
                    self.pid = pid
                    if self._job:
                        # Resume the thread.
                        winprocess.AssignProcessToJobObject(self._job, int(hp))
                        winprocess.ResumeThread(int(ht))
                    ht.Close()

            elif sys.version_info[:2] == (2, 7):

                def _execute_child(self, args, executable, preexec_fn, close_fds,
                                cwd, env, universal_newlines,
                                startupinfo, creationflags, shell, to_close,
                                p2cread, p2cwrite,
                                c2pread, c2pwrite,
                                errread, errwrite):
                    """Execute program (MS Windows version)"""

                    if not isinstance(args, string_types):
                        args = list2cmdline(args)

                    # Process startup details
                    if startupinfo is None:
                        startupinfo = STARTUPINFO()
                    if None not in (p2cread, c2pwrite, errwrite):
                        startupinfo.dwFlags |= STARTF_USESTDHANDLES
                        startupinfo.hStdInput = p2cread
                        startupinfo.hStdOutput = c2pwrite
                        startupinfo.hStdError = errwrite

                    if shell:
                        startupinfo.dwFlags |= STARTF_USESHOWWINDOW
                        startupinfo.wShowWindow = SW_HIDE
                        comspec = os.environ.get("COMSPEC", "cmd.exe")
                        args = '{} /c "{}"'.format(comspec, args)
                        if (GetVersion() >= 0x80000000 or
                                os.path.basename(comspec).lower() == "command.com"):
                            # Win9x, or using command.com on NT. We need to
                            # use the w9xpopen intermediate program. For more
                            # information, see KB Q150956
                            # (http://web.archive.org/web/20011105084002/http://support.microsoft.com/support/kb/articles/Q150/9/56.asp)
                            w9xpopen = self._find_w9xpopen()
                            args = '"%s" %s' % (w9xpopen, args)
                            # Not passing CREATE_NEW_CONSOLE has been known to
                            # cause random failures on win9x.  Specifically a
                            # dialog: "Your program accessed mem currently in
                            # use at xxx" and a hopeful warning about the
                            # stability of your system.  Cost is Ctrl+C wont
                            # kill children.
                            creationflags |= CREATE_NEW_CONSOLE

                        # We create a new job for this process, so that we can kill
                        # the process and any sub-processes
                        self._job = winprocess.CreateJobObject()
                        creationflags |= winprocess.CREATE_SUSPENDED
                        # Vista will launch Komodo in a job object itself, so we need
                        # to specify that the created process is not part of the Komodo
                        # job object, but instead specify that it will be using a
                        # separate breakaway job object, bug 83001.
                        creationflags |= winprocess.CREATE_BREAKAWAY_FROM_JOB

                    def _close_in_parent(fd):
                        fd.Close()
                        to_close.remove(fd)

                    # Start the process
                    try:
                        hp, ht, pid, tid = CreateProcess(executable, args,
                                                # no special security
                                                None, None,
                                                int(not close_fds),
                                                creationflags,
                                                env,
                                                cwd,
                                                startupinfo)
                    except IOError as e:  # From 2.6 on, pywintypes.error was defined as IOError
                        # Translate pywintypes.error to WindowsError, which is
                        # a subclass of OSError.  FIXME: We should really
                        # translate errno using _sys_errlist (or similar), but
                        # how can this be done from Python?
                        raise WindowsError(*e.args)
                    except WindowsError:
                        log.error("process.py: can't execute %r (%s)", executable, args)
                        raise
                    finally:
                        # Child is launched. Close the parent's copy of those pipe
                        # handles that only the child should have open.  You need
                        # to make sure that no handles to the write end of the
                        # output pipe are maintained in this process or else the
                        # pipe will not close when the child process exits and the
                        # ReadFile will hang.
                        if p2cread is not None:
                            _close_in_parent(p2cread)
                        if c2pwrite is not None:
                            _close_in_parent(c2pwrite)
                        if errwrite is not None:
                            _close_in_parent(errwrite)

                    # Retain the process handle, but close the thread handle
                    self._child_created = True
                    self._handle = hp
                    self.pid = pid
                    if self._job:
                        # Resume the thread.
                        winprocess.AssignProcessToJobObject(self._job, int(hp))
                        winprocess.ResumeThread(int(ht))
                    ht.Close()

            else:

                def _execute_child(self, args, executable, preexec_fn, close_fds,
                                pass_fds, cwd, env,
                                startupinfo, creationflags, shell,
                                p2cread, p2cwrite,
                                c2pread, c2pwrite,
                                errread, errwrite,
                                unused_restore_signals, unused_start_new_session):
                    """Execute program (MS Windows version)"""

                    assert not pass_fds, "pass_fds not supported on Windows."

                    if not isinstance(args, str):
                        args = list2cmdline(args)

                    # Process startup details
                    if startupinfo is None:
                        startupinfo = STARTUPINFO()
                    if -1 not in (p2cread, c2pwrite, errwrite):
                        startupinfo.dwFlags |= STARTF_USESTDHANDLES
                        startupinfo.hStdInput = p2cread
                        startupinfo.hStdOutput = c2pwrite
                        startupinfo.hStdError = errwrite

                    if shell:
                        startupinfo.dwFlags |= STARTF_USESHOWWINDOW
                        startupinfo.wShowWindow = SW_HIDE
                        comspec = os.environ.get("COMSPEC", "cmd.exe")
                        args = '{} /c "{}"'.format(comspec, args)

                        # We create a new job for this process, so that we can kill
                        # the process and any sub-processes
                        self._job = winprocess.CreateJobObject()
                        creationflags |= winprocess.CREATE_SUSPENDED
                        # Vista will launch Komodo in a job object itself, so we need
                        # to specify that the created process is not part of the Komodo
                        # job object, but instead specify that it will be using a
                        # separate breakaway job object, bug 83001.
                        creationflags |= winprocess.CREATE_BREAKAWAY_FROM_JOB

                    # Start the process
                    try:
                        hp, ht, pid, tid = CreateProcess(executable, args,
                                                # no special security
                                                None, None,
                                                int(not close_fds),
                                                creationflags,
                                                env,
                                                os.fspath(cwd) if cwd is not None else None,
                                                startupinfo)
                    except WindowsError:
                        log.error("process.py: can't execute %r (%s)", executable, args)
                        raise
                    finally:
                        # Child is launched. Close the parent's copy of those pipe
                        # handles that only the child should have open.  You need
                        # to make sure that no handles to the write end of the
                        # output pipe are maintained in this process or else the
                        # pipe will not close when the child process exits and the
                        # ReadFile will hang.
                        if p2cread != -1:
                            p2cread.Close()
                        if c2pwrite != -1:
                            c2pwrite.Close()
                        if errwrite != -1:
                            errwrite.Close()
                        if hasattr(self, '_devnull'):
                            os.close(self._devnull)
                        # Prevent a double close of these handles/fds from __init__
                        # on error.
                        self._closed_child_pipe_fds = True

                    # Retain the process handle, but close the thread handle
                    self._child_created = True
                    self._handle = Handle(hp)
                    self.pid = pid
                    if self._job:
                        # Resume the thread.
                        winprocess.AssignProcessToJobObject(self._job, int(hp))
                        winprocess.ResumeThread(int(ht))
                    CloseHandle(ht)

            def terminate(self):
                """Terminates the process"""
                # Don't terminate a process that we know has already died.
                if self.returncode is not None:
                    return
                if self._job:
                    winprocess.TerminateJobObject(self._job, 127)
                    self.returncode = 127
                else:
                    Popen.terminate(self)

            kill = terminate

        # Use our own killable process instead of the regular Popen.
        Popen = WindowsKillablePopen


class ProcessOpen(Popen):

    @components.ProxyToMainThread
    def __init__(self, cmd, cwd=None, env=None, flags=None,
                 stdin=PIPE, stdout=PIPE, stderr=PIPE,
                 universal_newlines=True):
        """Create a child process.

        "cmd" is the command to run, either a list of arguments or a string.
        "cwd" is a working directory in which to start the child process.
        "env" is an environment dictionary for the child.
        "flags" are system-specific process creation flags. On Windows
            this can be a bitwise-OR of any of the win32process.CREATE_*
            constants (Note: win32process.CREATE_NEW_PROCESS_GROUP is always
            OR'd in). On Unix, this is currently ignored.
        "stdin", "stdout", "stderr" can be used to specify file objects
            to handle read (stdout/stderr) and write (stdin) events from/to
            the child. By default a file handle will be created for each
            io channel automatically, unless set explicitly to None. When set
            to None, the parent io handles will be used, which can mean the
            output is redirected to Komodo's log files.
        "universal_newlines": On by default (the opposite of subprocess).
        """
        self.__use_killpg = False
        auto_piped_stdin = False
        preexec_fn = None
        shell = False
        if not isinstance(cmd, (list, tuple)):
            # The cmd is the already formatted, ready for the shell. Otherwise
            # subprocess.Popen will treat this as simply one command with
            # no arguments, resulting in an unknown command.
            shell = True
        if sys.platform.startswith("win"):
            # On Windows, cmd requires some special handling of multiple quoted
            # arguments, as this is what cmd will do:
            #    See if the first character is a quote character and if so,
            #    strip the leading character and remove the last quote character
            #    on the command line, preserving any text after the last quote
            #    character.
            if cmd and shell and cmd.count('"') > 2:
                if not cmd.startswith('""') or not cmd.endswith('""'):
                    # Needs to be a re-quoted with additional double quotes.
                    # http://bugs.activestate.com/show_bug.cgi?id=75467
                    cmd = '"%s"' % (cmd, )

            # Environment variables on Python 2 + Windows must be str.
            # XXX - subprocess needs to be updated to use the wide string API.
            # subprocess uses a Windows API that does not accept unicode, so
            # we need to convert all the environment variables to strings
            # before we make the call. Temporary fix to bug:
            #   http://bugs.activestate.com/show_bug.cgi?id=72311
            if env and PY2:
                encoding = sys.getfilesystemencoding()
                _enc_env = {}
                for key, value in env.items():
                    try:
                        if not isinstance(key, str):
                            key = key.encode(encoding)
                        if not isinstance(value, str):
                            value = value.encode(encoding)
                        _enc_env[key] = value
                    except UnicodeEncodeError:
                        # Could not encode it, warn we are dropping it.
                        log.warn("Could not encode environment variable %r "
                                 "so removing it", key)
                env = _enc_env

            if flags is None:
                flags = CREATE_NO_WINDOW

            # If we don't have standard handles to pass to the child process
            # (e.g. we don't have a console app), then
            # `subprocess.GetStdHandle(...)` will return None. `subprocess.py`
            # handles that (http://bugs.python.org/issue1124861)
            #
            # However, if Komodo is started from the command line, then
            # the shell's stdin handle is inherited, i.e. in subprocess.py:
            #      p2cread = GetStdHandle(STD_INPUT_HANDLE)   # p2cread == 3
            # A few lines later this leads to:
            #    Traceback (most recent call last):
            #      ...
            #      File "...\lib\mozilla\python\komodo\process.py", line 130, in __init__
            #        creationflags=flags)
            #      File "...\lib\python\lib\subprocess.py", line 588, in __init__
            #        errread, errwrite) = self._get_handles(stdin, stdout, stderr)
            #      File "...\lib\python\lib\subprocess.py", line 709, in _get_handles
            #        p2cread = self._make_inheritable(p2cread)
            #      File "...\lib\python\lib\subprocess.py", line 773, in _make_inheritable
            #        DUPLICATE_SAME_ACCESS)
            #    WindowsError: [Error 6] The handle is invalid
            #
            # I suspect this indicates that the stdin handle inherited by
            # the subsystem:windows komodo.exe process is invalid -- perhaps
            # because of mis-used of the Windows API for passing that handle
            # through. The same error can be demonstrated in PythonWin:
            #   from _subprocess import *
            #   from subprocess import *
            #   h = GetStdHandle(STD_INPUT_HANDLE)
            #   p = Popen("python -c '1'")
            #   p._make_interitable(h)
            #
            # I don't understand why the inherited stdin is invalid for
            # `DuplicateHandle`, but here is how we are working around this:
            # If we detect the condition where this can fail, then work around
            # it by setting the handle to `subprocess.PIPE`, resulting in
            # a different and workable code path.
            if self._needToHackAroundStdHandles() \
              and not (flags & CREATE_NEW_CONSOLE):
                if not self._isFileObjInheritable(stdin, "stdin"):
                    stdin = PIPE
                    auto_piped_stdin = True
                if not self._isFileObjInheritable(stdout, "stdout"):
                    stdout = PIPE
                if not self._isFileObjInheritable(stderr, "stderr"):
                    stderr = PIPE
        else:
            # Set flags to 0, subprocess raises an exception otherwise.
            flags = 0
            # Set a preexec function, this will make the sub-process create it's
            # own session and process group - bug 80651, bug 85693.
            preexec_fn = os.setsid
            # Mark as requiring progressgroup killing. This will allow us to
            # later kill both the spawned shell and the sub-process in one go
            # (see the kill method) - bug 85693.
            self.__use_killpg = True

        # Internal attributes.
        self.__cmd = cmd
        self.__retval = None
        self.__hasTerminated = threading.Condition()

        # Launch the process.
        #print "Process: %r in %r" % (cmd, cwd)
        Popen.__init__(self, cmd, cwd=cwd, env=env, shell=shell,
                       stdin=stdin, stdout=stdout, stderr=stderr,
                       preexec_fn=preexec_fn,
                       universal_newlines=universal_newlines,
                       creationflags=flags)
        if auto_piped_stdin:
            self.stdin.close()

    __needToHackAroundStdHandles = None
    @classmethod
    def _needToHackAroundStdHandles(cls):
        if cls.__needToHackAroundStdHandles is None:
            if sys.platform != "win32":
                cls.__needToHackAroundStdHandles = False
            else:
                stdin_handle = GetStdHandle(STD_INPUT_HANDLE)
                if stdin_handle is not None:
                    cls.__needToHackAroundStdHandles = True
                else:
                    cls.__needToHackAroundStdHandles = False
        return cls.__needToHackAroundStdHandles

    def _isFileObjInheritable(self, fileobj, stream_name):
        """Check if a given file-like object (or whatever else subprocess.Popen
        takes as a handle/stream) can be correctly inherited by a child process.
        This just duplicates the code in subprocess.Popen._get_handles to make
        sure we go down the correct code path; this to catch some non-standard
        corner cases.

        @param fileobj The object being used as a fd/handle/whatever
        @param stream_name The name of the stream, "stdin", "stdout", or "stderr"
        """
        import ctypes
        import msvcrt
        new_handle = None

        # Things that we know how to reset (i.e. not custom fds)
        valid_list = {
            "stdin": (sys.stdin, sys.__stdin__, 0),
            "stdout": (sys.stdout, sys.__stdout__, 1),
            "stderr": (sys.stderr, sys.__stderr__, 2),
        }[stream_name]

        try:
            if fileobj is None:
                std_handle = {
                    "stdin": STD_INPUT_HANDLE,
                    "stdout": STD_OUTPUT_HANDLE,
                    "stderr": STD_ERROR_HANDLE,
                }[stream_name]
                handle = GetStdHandle(std_handle)
                if handle is None:
                    # subprocess.Popen._get_handles creates a new pipe here
                    # we don't have to worry about things we create
                    return True
            elif fileobj == subprocess.PIPE:
                # We're creating a new pipe; newly created things are inheritable
                return True
            elif fileobj not in valid_list:
                # We are trying to use a custom fd; don't do anything fancy here,
                # we don't want to actually use subprocess.PIPE
                return True
            elif isinstance(fileobj, int):
                handle = msvcrt.get_osfhandle(fileobj)
            else:
                # Assuming file-like object
                handle = msvcrt.get_osfhandle(fileobj.fileno())
            new_handle = self._make_inheritable(handle)
            return True
        except:
            return False
        finally:
            CloseHandle = ctypes.windll.kernel32.CloseHandle
            if new_handle is not None:
                CloseHandle(new_handle)

    # Override the returncode handler (used by subprocess.py), this is so
    # we can notify any listeners when the process has finished.
    def _getReturncode(self):
        return self.__returncode
    def _setReturncode(self, value):
        self.__returncode = value
        if value is not None:
            # Notify that the process is done.
            self.__hasTerminated.acquire()
            self.__hasTerminated.notifyAll()
            self.__hasTerminated.release()
    returncode = property(fget=_getReturncode, fset=_setReturncode)

    # Setup the retval handler. This is a readonly wrapper around returncode.
    def _getRetval(self):
        # Ensure the returncode is set by subprocess if the process is finished.
        self.poll()
        return self.returncode
    retval = property(fget=_getRetval)

    def wait(self, timeout=None):
        """Wait for the started process to complete.
        
        "timeout" is a floating point number of seconds after
            which to timeout.  Default is None, which is to never timeout.

        If the wait time's out it will raise a ProcessError. Otherwise it
        will return the child's exit value. Note that in the case of a timeout,
        the process is still running. Use kill() to forcibly stop the process.
        """
        if timeout is None or timeout < 0:
            # Use the parent call.
            try:
                return Popen.wait(self)
            except OSError as ex:
                # If the process has already ended, that is fine. This is
                # possible when wait is called from a different thread.
                if ex.errno != 10: # No child process
                    raise
                return self.returncode

        # We poll for the retval, as we cannot rely on self.__hasTerminated
        # to be called, as there are some code paths that do not trigger it.
        # The accuracy of this wait call is between 0.1 and 1 second.
        time_now = time.time()
        time_end = time_now + timeout
        # These values will be used to incrementally increase the wait period
        # of the polling check, starting from the end of the list and working
        # towards the front. This is to avoid waiting for a long period on
        # processes that finish quickly, see bug 80794.
        time_wait_values = [1.0, 0.5, 0.2, 0.1]
        while time_now < time_end:
            result = self.poll()
            if result is not None:
                return result
            # We use hasTerminated here to get a faster notification.
            self.__hasTerminated.acquire()
            if time_wait_values:
                wait_period = time_wait_values.pop()
            self.__hasTerminated.wait(wait_period)
            self.__hasTerminated.release()
            time_now = time.time()
        # last chance
        result = self.poll()
        if result is not None:
            return result

        raise ProcessError("Process timeout: waited %d seconds, "
                           "process not yet finished." % (timeout,),
                           WAIT_TIMEOUT)

    # For backward compatibility with older process.py
    def close(self):
        pass

    # For backward compatibility with older process.py
    def kill(self, exitCode=-1, gracePeriod=None, sig=None):
        """Kill process.
        
        "exitCode" this sets what the process return value will be.
        "gracePeriod" [deprecated, not supported]
        "sig" (Unix only) is the signal to use to kill the process. Defaults
            to signal.SIGKILL. See os.kill() for more information.
        """
        if gracePeriod is not None:
            import warnings
            warnings.warn("process.kill() gracePeriod is no longer used",
                          DeprecationWarning)

        # Need to ensure stdin is closed, makes it easier to end the process.
        if self.stdin is not None:
            self.stdin.close()

        if sys.platform.startswith("win"):
            # TODO: 1) It would be nice if we could give the process(es) a
            #       chance to exit gracefully first, rather than having to
            #       resort to a hard kill.
            #       2) May need to send a WM_CLOSE event in the case of a GUI
            #       application, like the older process.py was doing.
            Popen.kill(self)
        else:
            if sig is None:
                sig = signal.SIGKILL
            try:
                if self.__use_killpg:
                    os.killpg(self.pid, sig)
                else:
                    os.kill(self.pid, sig)
            except OSError as ex:
                if ex.errno != 3:
                    # Ignore:   OSError: [Errno 3] No such process
                    raise
            self.returncode = exitCode



class AbortableProcessHelper(object):
    """A helper class that is able to run a process and have the process be
    killed/aborted (possibly by another thread) if it is still running.
    """
    STATUS_INITIALIZED = 0         # Ready to run.
    STATUS_RUNNING = 1             # A process is running.
    STATUS_FINISHED_NORMALLY = 2   # The command/process finished normally.
    STATUS_ABORTED = 3             # The command/process was aborted.

    def __init__(self):
        self._process = None
        self._process_status = self.STATUS_INITIALIZED
        self._process_status_lock = threading.Lock()

    def ProcessOpen(self, *args, **kwargs):
        """Create a new process and return it."""
        self._process_status_lock.acquire()
        try:
            self._process_status = self.STATUS_RUNNING
            self._process = ProcessOpen(*args, **kwargs)
            return self._process
        finally:
            self._process_status_lock.release()

    def ProcessDone(self):
        """Mark the process as being completed, does not need to be aborted."""
        self._process_status_lock.acquire()
        try:
            self._process = None
            self._process_status = self.STATUS_FINISHED_NORMALLY
        finally:
            self._process_status_lock.release()

    def ProcessAbort(self):
        """Kill the process if it is still running."""
        self._process_status_lock.acquire()
        try:
            self._process_status = self.STATUS_ABORTED
            if self._process:
                self._process.kill()
                self._process = None
        finally:
            self._process_status_lock.release()



## Deprecated process classes ##

class Process(ProcessOpen):
    def __init__(self, *args, **kwargs):
        warnings.warn("'process.%s' is now deprecated. Please use 'process.ProcessOpen'." % (self.__class__.__name__))
        ProcessOpen.__init__(self, *args, **kwargs)

class ProcessProxy(Process):
    pass
