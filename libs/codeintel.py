# -*- coding: utf-8 -*-
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
# The Original Code is ActiveState Software Inc code.
# Portions created by German M. Bravo (Kronuz) are Copyright (C) 2015.
#
# Contributor(s):
#   German M. Bravo (Kronuz)
#   ActiveState Software Inc
#
# Portions created by ActiveState Software Inc are Copyright (C) 2000-2007
# ActiveState Software Inc. All Rights Reserved.
#
# Mostly based in Komodo Editor's koCodeIntel.py
# at commit 0fbca1d7f3190b93b5e56a42c7db0ad60c8cfc99
#
from __future__ import absolute_import, unicode_literals, print_function

import os
import sys

import json
import time
import threading
import logging
import socket
import weakref
import functools

try:
    import queue
except ImportError:
    import Queue as queue

# Priorities at which scanning requests can be scheduled.
PRIORITY_CONTROL = 0        # Special sentinal priority to control scheduler
PRIORITY_IMMEDIATE = 1      # UI is requesting info on this file now
PRIORITY_CURRENT = 2        # UI requires info on this file soon
PRIORITY_OPEN = 3           # UI will likely require info on this file soon
PRIORITY_BACKGROUND = 4     # info may be needed sometime

logger_name = 'CodeIntel.codeintel'

logging.getLogger(logger_name).setLevel(logging.INFO)


class CodeIntel(object):
    def __init__(self):
        self.log = logging.getLogger(logger_name + '.' + self.__class__.__name__)
        self.mgr = None
        self._mgr_lock = threading.Lock()
        self.buffers = {}
        self.languages = {}
        self._queue = queue.Queue()
        self._quit_application = False  # app is shutting down, don't try to respawn
        self._observers = weakref.WeakKeyDictionary()
        self._enabled = False

    def add_observer(self, obj):
        if hasattr(obj, 'observer'):
            self._observers[obj] = True

    def notify_observers(self, topic, data):
        """Observer calls must be called on the main thread"""
        if topic:
            for obj in self._observers.keys():
                obj.observer(topic, data)

    def _on_mgr_progress(self, mgr, message, state=None, response=None):
        topic = 'status_message'
        self.log.debug("Progress: %s", message)
        if state is CodeIntelManager.STATE_DESTROYED:
            self.log.debug("startup failed: %s", message)
            topic = 'error_message'
            message = "Startup failed: %s" % message
        elif state is CodeIntelManager.STATE_BROKEN:
            self.log.debug("db is broken, needs manual intervention")
            topic = 'error_message'
            message = "There is an error with your code intelligence database; it must be reset before it can be used."
        elif state is CodeIntelManager.STATE_ABORTED:
            self.log.debug("Got abort message")
            topic = 'error_message'
            message = "Code Intelligence Initialization Aborted"
        elif state is CodeIntelManager.STATE_WAITING:
            self.log.debug("Waiting for CodeIntel")
        elif state is CodeIntelManager.STATE_READY:
            self.log.debug("db is ready")
        if message:
            self.notify_observers(topic, dict(response or {}, message=message))
        else:
            self.log.debug("nothing to report")

    def _on_mgr_shutdown(self, mgr):
        # The codeintel manager is going away, drop the reference to it
        with self._mgr_lock:
            if self.mgr is mgr:
                self.mgr = None

    def activate(self, reset_db_as_necessary=False, codeintel_command=None, oop_mode=None, log_levels=None, env=None, prefs=None):
        self.log.debug("activating codeintel service")

        if self._quit_application:
            return  # don't ever restart after quit-application

        # clean up dead managers
        with self._mgr_lock:
            if self.mgr and not self.mgr.is_alive():
                self.mgr = None
            # create a new manager as necessary
            if not self.mgr:
                self.mgr = CodeIntelManager(
                    self,
                    progress_callback=self._on_mgr_progress,
                    shutdown_callback=self._on_mgr_shutdown,
                    codeintel_command=codeintel_command,
                    oop_mode=oop_mode,
                    log_levels=log_levels,
                    env=env,
                    prefs=prefs,
                )
                while True:
                    try:
                        # Tell the manager to deal with it; note that this request
                        # will get queued by the manager for now, since we haven't
                        # actually started the manager.
                        self.mgr.send(**self._queue.get(False))
                    except queue.Empty:
                        break  # no more items

                # new codeintel manager; update all the buffers to use this new one
                for buf in list(self.buffers.values()):
                    buf.mgr = self.mgr
            self._enabled = True
        try:
            # run the new manager
            self.mgr.start(reset_db_as_necessary)
        except RuntimeError:
            # thread already started
            pass

    @property
    def enabled(self):
        return self._enabled

    def deactivate(self):
        with self._mgr_lock:
            if self.mgr:
                self.mgr.shutdown()
                self.mgr = None
        self._enabled = False

    def cancel(self):
        mgr = self.mgr
        if mgr:
            mgr.abort()

    def is_cpln_lang(self, language):
        return language in self.get_cpln_langs()

    def get_cpln_langs(self):
        return self.mgr.cpln_langs if self.mgr else []

    def is_citadel_lang(self, language):
        return language in self.get_citadel_langs()

    def get_citadel_langs(self):
        return self.mgr.citadel_langs if self.mgr else []

    def is_xml_lang(self, language):
        return language in self.get_xml_langs()

    def get_xml_langs(self):
        return self.mgr.xml_langs if self.mgr else []

    @property
    def available_catalogs(self):
        return self.mgr.available_catalogs if self.mgr else []

    def update_catalogs(self, update_callback=None):
        if self.mgr:
            self.mgr.update_catalogs(update_callback=update_callback)

    def send(self, discardable=False, **kwargs):
        if not self._enabled:
            self.log.warn("send called when not enabled (ignoring command) %r", kwargs)
            return
        if self.mgr:
            self.mgr.send(**kwargs)
        elif not discardable:
            self._queue.put(kwargs)
            self.activate()
        else:
            self.log.debug("discarding request %r", kwargs)

    def collectReports(self, callback, closure):
        def on_have_report(request, response):
            for path, data in list(response.get('memory', {}).items()):
                amount = data.get('amount')
                if amount is None:
                    continue  # This value was unavailable
                units = data.get('units')  # bytes or count
                if path.startswith('explicit/'):
                    kind = 'heap'
                else:
                    kind = 'other'
                desc = data.get('desc', "No description available.")
                callback(path, kind, units, amount, desc)
            have_response.add(True)
        have_response = set()
        self.send(command='memory-report', callback=on_have_report)
        while not have_response:
            time.sleep(0.1)

    def buf_from_path(self, path):
        """
        Get an existing buffer given the path
        @note Prefer buf_from_view; this might be less accurate.
            (multiple buffers might have the same path.)
        """
        if not self.mgr or not path:
            return None
        path = CodeIntelBuffer.normpath(path)  # Fix case on Windows
        for vid, buf in list(self.buffers.items()):
            if CodeIntelBuffer.normpath(buf.path) == path:
                return buf
        return None


class _Connection(object):
    def get_commandline_args(self):
        """Return list of command line args to pass to child"""
        raise NotImplementedError()

    def get_stream(self):
        """Return file-like object for read/write"""
        raise NotImplementedError()

    def cleanup(self):
        """Do any cleanup required"""


class _TCPConnection(_Connection):
    """A connection using TCP sockets"""

    _read = None
    _write = None

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('127.0.0.1', 0))
        self.sock.listen(0)

    def get_commandline_args(self):
        return ['--tcp', '%s:%s' % self.sock.getsockname()]

    def get_stream(self):
        conn = self.sock.accept()
        self._read = conn[0].makefile('rb', 0)
        self._write = conn[0].makefile('wb', 0)
        return self

    def read(self, count):
        return self._read.read(count)

    def write(self, data):
        return self._write.write(data)

    def cleanup(self):
        if self.sock:
            self.sock.close()


class _ServerConnection(_Connection):
    """A connection using TCP sockets"""

    sock = None
    _read = None
    _write = None

    def __init__(self, host='127.0.0.1', port=9999):
        self.host = host
        self.port = port

    def get_commandline_args(self):
        return ['--server', '%s:%s' % (self.host, self.port)]

    def get_stream(self):
        conn = socket.create_connection((self.host, self.port))
        self._read = conn.makefile('rb', 0)
        self._write = conn.makefile('wb', 0)
        self.sock = conn
        return self

    def read(self, count):
        return self._read.read(count)

    def write(self, data):
        return self._write.write(data)

    def cleanup(self):
        if self.sock:
            self.sock.close()


if sys.platform.startswith("win"):
    from win32_named_pipe import Win32Pipe

    class _PipeConnection(Win32Pipe):
        """This is a wrapper around our Win32Pipe class to expose the expected
        API"""
        pipe_prefix = "codeintel-"

        def get_commandline_args(self):
            return ['--pipe', self.name]

        def get_stream(self):
            self._ensure_stream()
            return self

        def cleanup(self):
            return
    del Win32Pipe
else:
    # posix pipe class
    class _PipeConnection(_Connection):
        _dir = None
        _read = None
        _write = None

        def get_commandline_args(self):
            import tempfile
            self._dir = tempfile.mkdtemp(prefix='codeintel-', suffix='-oop-pipes')
            os.mkfifo(os.path.join(self._dir, 'in'), 0o600)
            os.mkfifo(os.path.join(self._dir, 'out'), 0o600)
            return ['--pipe', self._dir]

        def get_stream(self):
            # Open the write end first, so that the child doesn't hang
            self._read = open(os.path.join(self._dir, 'out'), 'rb', 0)
            self._write = open(os.path.join(self._dir, 'in'), 'wb', 0)
            return self

        def read(self, count):
            return self._read.read(count)

        def write(self, data):
            return self._write.write(data)

        def cleanup(self):
            # don't close the streams here, but remove the files.  The fds are
            # left open so we can communicate through them, but we no longer
            # need the file names around.
            os.remove(self._read.name)
            os.remove(self._write.name)
            try:
                os.rmdir(self._dir)
            except OSError:
                pass

        def close(self):
            try:
                self.cleanup()
            except Exception as e:
                pass
            self._read.close()
            self._write.close()


class CodeIntelManager(threading.Thread):
    STATE_UNINITIALIZED = ("uninitialized",)  # not initialized
    STATE_CONNECTED = ("connected",)  # child process spawned, connection up; not ready
    STATE_BROKEN = ("broken",)  # database is broken and needs to be reset
    STATE_WAITING = ("waiting",)  # waiting for CodeIntel
    STATE_READY = ("ready",)  # ready for use
    STATE_QUITTING = ("quitting",)  # shutting down
    STATE_DESTROYED = ("destroyed",)  # connection shut down, child process dead
    STATE_ABORTED = ("aborted",)

    _codeintel_command = '/usr/local/bin/codeintel'
    _oop_mode = 'pipe'
    _log_levels = ['WARNING']
    _state = STATE_UNINITIALIZED
    _send_request_thread = None  # background thread to send unsent requests
    _reset_db_as_necessary = False  # whether to reset the db if it's broken
    _watchdog_thread = None  # background thread to watch for process termination
    _memory_error_restart_count = 0
    _cmd_messge = True
    proc = None
    pipe = None

    cpln_langs = []
    citadel_langs = []
    xml_langs = []
    stdlib_langs = []  # languages which support standard libraries
    available_catalogs = []  # see get-available-catalogs command
    env = dict(os.environ)
    prefs = [
        {
            'codeintel_max_recursive_dir_depth': 10,
            'codeintel_scan_files_in_project': True,
            'codeintel_selected_catalogs': [],
            'defaultHTML5Decl': '-//W3C//DTD HTML 5//EN',
            'defaultHTMLDecl': '-//W3C//DTD HTML 5//EN',
            'javascriptExtraPaths': '',
            'nodejsDefaultInterpreter': '',
            'nodejsExtraPaths': '',
            'perl': '',
            'perlExtraPaths': '',
            'php': '',
            'phpConfigFile': '',
            'phpExtraPaths': '',
            'python': '',
            'python3': '',
            'python3ExtraPaths': '',
            'pythonExtraPaths': '',
            'ruby': '',
            'rubyExtraPaths': '',
        },
    ]

    def __init__(self, service, progress_callback=None, shutdown_callback=None, codeintel_command=None, oop_mode=None, log_levels=None, env=None, prefs=None):
        self.log = logging.getLogger(logger_name + '.' + self.__class__.__name__)
        self.service = service
        self.languages = service.languages
        self._abort = set()
        self._next_id = 0
        self._progress_callback = progress_callback
        self._shutdown_callback = shutdown_callback
        if codeintel_command is not None:
            self._codeintel_command = codeintel_command
        if oop_mode is not None:
            self._oop_mode = oop_mode
        if log_levels is not None:
            self._log_levels = log_levels
        if prefs is not None:
            self.prefs = [prefs] if isinstance(prefs, dict) else prefs
        if env is not None:
            self.env = env
        self._state_condvar = threading.Condition()
        self.requests = {}  # keyed by request id; value is tuple (callback, request data, time sent) requests will time out at some point...
        self.unsent_requests = queue.Queue()
        threading.Thread.__init__(self, name="CodeIntel Manager Thread")

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        with self._state_condvar:
            self._state = state
            self._state_condvar.notifyAll()

    def start(self, reset_db_as_necessary=False):
        self._reset_db_as_necessary = reset_db_as_necessary
        threading.Thread.start(self)

    def shutdown(self):
        """Abort any outstanding requests and shut down gracefully"""
        self.abort()
        if self.state is CodeIntelManager.STATE_DESTROYED:
            return  # already dead
        if not self.pipe:
            # not quite dead, but already disconnected... ungraceful shutdown
            self.kill()
            return
        self._send(command='quit', callback=self.do_quit)
        self.state = CodeIntelManager.STATE_QUITTING

    def abort(self):
        """Abort all running requests"""
        for req in list(self.requests.keys()):
            self._abort.add(req)
            self._send(
                command='abort',
                id=req,
                callback=lambda request, response: None,
            )

    def close(self):
        try:
            self.pipe.close()
        except Exception as e:
            pass  # The other end is dead, this is kinda pointless
        self.pipe = None

    def kill(self):
        """
        Kill the subprocess. This may be safely called when the process has
        already exited.  This should *always* be called no matter how the
        process exits, in order to maintain the correct state.
        """
        with self.service._mgr_lock:
            if self.state == CodeIntelManager.STATE_DESTROYED:
                return
            # It's destroying time.
            self.state = CodeIntelManager.STATE_DESTROYED
        try:
            self.proc.kill()
        except Exception as e:
            pass
        self.close()
        try:
            # Shut down the request sending thread (self._send_request_thread)
            self.unsent_requests.put((None, None))
        except Exception as e:
            pass  # umm... no idea?
        if self._shutdown_callback:
            self._shutdown_callback(self)

    def init_child(self):
        import process
        assert threading.current_thread().name != "MainThread", \
            "CodeIntelManager.init_child should run on background thread!"
        self.log.debug("initializing child process")
        conn = None
        try:
            _codeintel_command = self._codeintel_command
            if not os.path.exists(_codeintel_command):
                _codeintel_command = os.path.basename(_codeintel_command)
            cmd = [_codeintel_command]

            database_dir = os.path.expanduser('~/.codeintel')
            cmd += ['--log-file', os.path.join(database_dir, 'codeintel.log')]
            for log_level in self._log_levels:
                cmd += ['--log-level', log_level]

            cmd += ['oop']

            cmd += ['--database-dir', database_dir]
            _oop_mode = self._oop_mode
            if _oop_mode == 'pipe':
                conn = _PipeConnection()
            elif _oop_mode == 'tcp':
                conn = _TCPConnection()
            elif _oop_mode == 'server':
                conn = _ServerConnection()
            else:
                self.log.warn("Unknown codeintel oop mode %s, falling back to pipes", _oop_mode)
                conn = _PipeConnection()
            cmd += conn.get_commandline_args()

            if _oop_mode == 'server':
                if self._cmd_messge:
                    self._cmd_messge = False
                    self.log.warn("Please start OOP server with command: %s", " ".join(cmd))
                self.proc = True
            else:
                self.log.debug("Running OOP: %s", " ".join(cmd))
                self.proc = process.ProcessOpen(cmd, cwd=None, env=None)
                assert self.proc.returncode is None, "Early process death!"

                self._watchdog_thread = threading.Thread(
                    target=self._run_watchdog_thread,
                    name="CodeIntel Subprocess Watchdog Thread",
                    args=(self.proc,),
                )
                self._watchdog_thread.start()

            try:
                self.pipe = conn.get_stream()
                self._cmd_messge = True
                self.log.info("Successfully connected with OOP CodeIntel!")
            except Exception:
                self.pipe = None

            conn.cleanup()  # This will remove the filesystem files (it keeps the fds open)

            self.state = CodeIntelManager.STATE_CONNECTED
        except Exception as e:
            self.kill()
            message = "Error initing child: %s" % e
            self.log.error(message)
            self._progress_callback(self, message)
        else:
            self._send_init_requests()

    def _run_watchdog_thread(self, proc):
        self.log.debug("Watchdog witing for OOP codeintel process to die...")
        if hasattr(proc, 'wait'):
            proc.wait()
        elif hasattr(proc, 'join'):
            proc.join()
        self.log.info("Child OOP CodeIntel process died!")
        self.state = CodeIntelManager.STATE_WAITING
        self.close()

    def _send_init_requests(self):
        assert threading.current_thread().name != "MainThread", \
            "CodeIntelManager._send_init_requests should run on background thread!"
        self.log.debug("sending internal initial requests")

        outstanding_cpln_langs = set()

        def update(message=None, state=None, response=None):
            if state in (CodeIntelManager.STATE_DESTROYED, CodeIntelManager.STATE_BROKEN):
                self.kill()
            if state is not None:
                self.state = state
            if response is not None:
                if message:
                    message += "\n"
                else:
                    message = ""
                message += response.get('message', "(No further information available)")
            if any(x is not None for x in (message, state)):
                # don't do anything if everything we have is just none
                self._progress_callback(self, message, state, response)

        def get_citadel_langs(request, response):
            if not response.get('success', False):
                update("Failed to get citadel languages:", state=CodeIntelManager.STATE_DESTROYED, response=response)
                return
            self.citadel_langs = sorted(response.get('languages'))

        def get_xml_langs(request, response):
            if not response.get('success', False):
                update("Failed to get XML languages:", state=CodeIntelManager.STATE_DESTROYED, response=response)
                return
            self.xml_langs = sorted(response.get('languages'))

        def get_stdlib_langs(request, response):
            if not response.get('success', False):
                update("Failed to get languages which support standard libraries:", state=CodeIntelManager.STATE_DESTROYED, response=response)
                return
            self.stdlib_langs = sorted(response.get('languages'))

        def get_cpln_langs(request, response):
            if not response.get('success', False):
                update("Failed to get completion languages:", state=CodeIntelManager.STATE_DESTROYED, response=response)
                return
            self.cpln_langs = sorted(response.get('languages'))
            self.languages.clear()
            for lang in self.cpln_langs:
                outstanding_cpln_langs.add(lang)
                self._send(callback=get_lang_info, command='get-language-info', language=lang)

        def get_lang_info(request, response):
            lang = request['language']
            if not response.get('success', False):
                update("Failed to get information for %s:" % (lang,), state=CodeIntelManager.STATE_DESTROYED, response=response)
                return
            self.languages[lang] = dict(
                cpln_fillup_chars=response['completion-fillup-chars'],
                cpln_stop_chars=response['completion-stop-chars'],
            )
            outstanding_cpln_langs.discard(lang)
            if not outstanding_cpln_langs:
                fixup_db({}, {'success': True})

        def fixup_db(request, response):
            command = request.get('command')
            previous_command = request.get('previous-command')
            state = response.get('state')
            req_id = response.get('req_id')

            if req_id in self._abort:
                self.log.debug("Aborting startup")
                update("Codeintel startup aborted", state=CodeIntelManager.STATE_ABORTED)
                return

            update(response=response)

            if 'success' not in response:
                # status update
                return

            if command != 'database-info':
                if response.get("abort", False):
                    # The request was aborted, don't retry
                    return
                # We just ran some sort of db-fixing command; check current status
                self._send(callback=fixup_db, command='database-info', previous_command=command)
                return

            # Possible db progression:
            # preload-needed -> (preload) -> ready
            # upgrade-needed -> (upgrade) -> preload-needed -> (preload) -> ready
            # upgrade-blocked -> (reset) -> preload-needed -> (preload) -> ready
            # broken -> (reset) -> preload-needed -> (preload) -> ready

            if state == 'ready':
                # db is fine
                initialization_completed()
                return

            if state == 'preload-needed':
                # database needs preloading
                if previous_command not in (None, 'database-reset'):
                    update("Unexpected empty database after %s" % (previous_command,), state=CodeIntelManager.STATE_BROKEN)
                    return
                langs = {}
                for lang in self.stdlib_langs:
                    ver = None
                    print("Language %s needs version resolving!" % lang)
                    # Get the version for the language here ([0-9]+.[0-9]+)
                    langs[lang] = ver
                self._send(callback=fixup_db, command='database-preload', languages=langs)
                return

            if state == 'upgrade-needed':
                # database needs to be upgraded
                if previous_command is not None:
                    update("Unexpected database upgrade needed after %s" % (previous_command,), state=CodeIntelManager.STATE_BROKEN)
                self._send(callback=fixup_db, command='database-upgrade')
                return

            if state == 'upgrade-blocked' or state == 'broken':
                # database can't be upgraded but can't be used either
                if previous_command is not None:
                    update("Unexpected database requires wiping after %s" % (previous_command,), state=CodeIntelManager.STATE_BROKEN)
                if self._reset_db_as_necessary:
                    self._send(callback=fixup_db, command='database-reset')
                else:
                    update("Database is broken and must be reset", state=CodeIntelManager.STATE_BROKEN)
                return

            update("Unexpected database state %s" % (state,), state=CodeIntelManager.STATE_BROKEN)

        def initialization_completed():
            self.log.debug("internal initial requests completed")
            if not self._send_request_thread:
                self._send_request_thread = threading.Thread(
                    target=self._send_queued_requests,
                    name="CodeIntel Manager Request Sending Thread")
                self._send_request_thread.daemon = True
                self._send_request_thread.start()
            update("CodeIntel ready.", state=CodeIntelManager.STATE_READY)

        self._send(callback=get_cpln_langs, command='get-languages', type='cpln')
        self._send(callback=get_citadel_langs, command='get-languages', type='citadel')
        self._send(callback=get_xml_langs, command='get-languages', type='xml')
        self._send(callback=get_stdlib_langs, command='get-languages', type='stdlib-supported')

        self.set_global_environment(self.env, self.prefs)

        def update_callback(response):
            if not response.get("success", False):
                update("Failed to get available catalogs:", state=CodeIntelManager.STATE_DESTROYED, response=response)
        self.update_catalogs(update_callback=update_callback)

        self.send(command="set-xml-catalogs")

    def set_global_environment(self, env, prefs):
        self.env = env
        self.prefs = [prefs] if isinstance(prefs, dict) else prefs
        self._send(
            command='set-environment',
            env=self.env,
            prefs=self.prefs,
        )

    def update_catalogs(self, update_callback=None):
        def get_available_catalogs(request, response):
            if response.get("success", False):
                self.available_catalogs = response.get('catalogs', [])
            if update_callback:
                update_callback(response)
        self._send(callback=get_available_catalogs, command='get-available-catalogs')

    def send(self, callback=None, **kwargs):
        """Public API for sending a request.
        Requests are expected to be well-formed (has a command, etc.)
        The callback recieves two arguments, the request and the response,
        both as dicts.
        @note The callback is invoked on a background thread; proxy it to
        the main thread if desired."""
        if self.state is CodeIntelManager.STATE_DESTROYED:
            raise RuntimeError("Manager already shut down")
        self.unsent_requests.put((callback, kwargs))

    def _send_queued_requests(self):
        """Worker to send unsent requests"""
        while True:
            with self._state_condvar:
                if self.state is CodeIntelManager.STATE_DESTROYED:
                    break  # Manager already shut down
                if self.state is not CodeIntelManager.STATE_READY:
                    self._state_condvar.wait()
                    continue  # wait...
            callback, kwargs = self.unsent_requests.get()
            if callback is None and kwargs is None:
                # end of queue (shutting down)
                break
            self._send(callback, **kwargs)

    def _send(self, callback=None, **kwargs):
        """
        Private API for sending; ignores the current state of the manager and
        just dumps things over.  The caller should check that it things are in
        the expected state_ (Used for initialization.)  This will block the
        calling thread until the data has been written (though possibly not yet
        received on the other end).
        """
        if not self.pipe or self.state is CodeIntelManager.STATE_QUITTING:
            return  # Nope, eating all commands during quit
        req_id = hex(self._next_id)
        kwargs['req_id'] = req_id
        text = json.dumps(kwargs, separators=(',', ':'))
        # Keep the request parameters so the handler can examine it; however,
        # drop the text and env, because those are huge and usually useless
        kwargs.pop('text', None)
        kwargs.pop('env', None)
        self.requests[req_id] = (callback, kwargs, time.time())
        self._next_id += 1
        self.log.debug("sending frame: %s", text)
        text = text.encode('utf-8')
        length = "%i" % len(text)
        length = length.encode('utf-8')
        buf = length + text
        try:
            self.pipe.write(buf)
        except Exception as e:
            message = "Error writing data to OOP CodeIntel: %s" % e
            self.log.error(message)
            self._progress_callback(self, message)
            self.close()

    def run(self):
        """Event loop for the codeintel manager background thread"""
        assert threading.current_thread().name != "MainThread", \
            "CodeIntelManager.run should run on background thread!"

        self.log.debug("CodeIntelManager thread started...")

        while True:
            self.init_child()
            if not self.proc:
                break  # init child failed

            first_buf = True
            discard_time = 0.0
            try:
                buf = b''
                while self.proc and self.pipe:
                    # Loop to read from the pipe
                    ch = self.pipe.read(1)
                    if not ch:
                        # nothing read, EOF
                        raise IOError("Failed to read from socket")
                    if ch == b'{':
                        length = int(buf)
                        buf = ch
                        while len(buf) < length:
                            data = self.pipe.read(length - len(buf))
                            if not data:
                                # nothing read, EOF
                                raise IOError("Failed to read from socket")
                            buf += data
                        self.log.debug("Got codeintel response: %r" % buf)
                        if first_buf and buf == b'{}':
                            first_buf = False
                            buf = b''
                            continue
                        response = json.loads(buf.decode('utf-8'))
                        self.handle(response)  # handle runs asynchronously and shouldn't raise exceptions
                        buf = b''
                    else:
                        if ch not in b'0123456789':
                            raise ValueError("Invalid frame length character: %r" % ch)
                        buf += ch

                    now = time.time()
                    if now - discard_time > 60:  # discard some stale results
                        for req_id, (callback, request, sent_time) in list(self.requests.items()):
                            if sent_time < now - 5 * 60:
                                # sent 5 minutes ago - it's irrelevant now
                                try:
                                    if callback:
                                        callback(request, {})
                                except Exception as e:
                                    self.log.error("Failed timing out request")
                                else:
                                    self.log.debug("Discarding request %r", request)
                                del self.requests[req_id]

            except Exception as e:
                if self.state in (CodeIntelManager.STATE_QUITTING, CodeIntelManager.STATE_DESTROYED):
                    self.log.debug("IOError in codeintel during shutdown; ignoring")
                    break  # this is intentional
                message = "Error reading data from OOP CodeIntel: %s" % e
                self.log.error(message)
                self._progress_callback(self, message)
                self.state = CodeIntelManager.STATE_WAITING
                self.close()

            if self.proc is True:
                time.sleep(3)

        self.log.debug("CodeIntelManager thread ended!")

    def handle(self, response):
        """Handle a response from the codeintel process"""
        self.log.debug("handling: %r", response)
        req_id = response.get('req_id')
        callback, request, sent_time = self.requests.get(req_id, (None, None, None))
        request_command = request.get('command', '') if request else None
        response_command = response.get('command', request_command)
        if req_id is None or request_command != response_command:
            # unsolicited response, look for a handler
            try:
                if not response_command:
                    self.log.error("No 'command' in response %r", response)
                    raise ValueError("Invalid response frame %r" % response)
                meth = getattr(self, 'do_' + response_command.replace('-', '_'), None)
                if not meth:
                    self.log.error("Unknown command %r, response %r", response_command, response)
                    raise ValueError("Unknown unsolicited response \"%s\"" % response_command)
                meth(response)
            except Exception as e:
                self.log.error("Error handling unsolicited response")
            return
        if not request:
            self.log.error("Discard response for unknown request %s (command %s): have %s",
                      req_id, response_command or '%r' % response, sorted(self.requests.keys()))
            return
        self.log.debug("Request %s (command %s) took %0.2f seconds", req_id, request_command or '<unknown>', time.time() - sent_time)
        if 'success' in response:
            # remove completed request
            self.log.debug("Removing completed request %s", req_id)
            del self.requests[req_id]
        else:
            # unfinished response; update the sent time so it doesn't time out
            self.requests[req_id] = (callback, request, time.time())
        if callback:
            callback(request, response)

    def do_scan_complete(self, response):
        """Scan complete unsolicited response"""
        path = response.get('path')
        if path:
            buf = self.service.buf_from_path(path)
            self.service.notify_observers('codeintel_buffer_scanned', buf)

    def do_report_message(self, response):
        """Report a message from codeintel (typically, scan status) unsolicited response"""
        if response.get('type') == 'logging':
            message = response.get('message')
            if message.strip().endswith("MemoryError") and "Traceback (most recent call last):" in message:
                # Python memory error - kill the process (it will restart itself) - bug 103067.
                if self._memory_error_restart_count < 20:
                    self.log.fatal("Out-of-process ran out of memory - killing process")
                    self.kill()
                    self._memory_error_restart_count += 1
                return
        self.service.notify_observers('status_message', response)

    def do_report_error(self, response):
        """Report a codeintel error into the error log"""
        self.service.notify_observers('error_message', response)

    def do_quit(self, request, response):
        """Quit successful"""
        assert threading.current_thread().name == "MainThread", \
            "CodeIntelManager.activate::do_quit() should run on main thread!"
        self.kill()
        if self.is_alive():
            self.join(1)


class CodeIntelBuffer(object):
    """A buffer-like object for codeintel; this is specific to a
    CodeIntelManager instance."""

    def __init__(self, service, vid, lang=None, path=None, text=None, env=None, prefs=None):
        self.log = logging.getLogger(logger_name + '.' + self.__class__.__name__)
        self.service = service
        self.vid = vid
        self.lang = lang
        self.path = path
        self.text = text
        self._env = env
        self._prefs = [prefs] if isinstance(prefs, dict) else prefs

    @property
    def env(self):
        env = dict(self.service.mgr and self.service.mgr.env or {})
        env.update(self._env or {})
        return env

    @env.setter
    def env(self, env):
        self._env = env

    @property
    def prefs(self):
        prefs = list(self.service.mgr and self.service.mgr.prefs or [])
        for pref in self._prefs or []:
            if pref not in prefs:
                prefs.append(pref)
        return prefs

    @prefs.setter
    def prefs(self, prefs):
        self._prefs = [prefs] if isinstance(prefs, dict) else prefs

    @staticmethod
    def normpath(path):
        """Routine to normalize the path used for codeintel buffers
        @note See also codeintel/lib/oop/driver.py::Driver.normpath
        """
        return os.path.normcase(path)

    @property
    def cpln_fillup_chars(self):
        return self.service.languages[self.lang]['cpln_fillup_chars']

    @property
    def cpln_stop_chars(self):
        return self.service.languages[self.lang]['cpln_stop_chars']

    def scan_document(self, handler, lines_added, file_mtime=False, callback=None):
        def invoke_callback(request, response):
            if not response.get('success'):
                msg = response.get('message')
                if not msg:
                    msg = "scan_document: Can't scan document"
                try:
                    handler.set_status_message(self, msg)
                except Exception as e:
                    self.log.error("Error reporting scan_document error: %s", response.get('message', e))
                    pass
                return
            try:
                handler.on_document_scanned(self)
            except Exception as e:
                self.log.error("Error calling scan_document callback: %s", e)
                pass
            if callback is not None:
                callback(request, response)

        mtime = None if file_mtime else time.time()

        self.service.send(
            command='scan-document',
            path=self.path,
            language=self.lang,
            env={
                'env': self.env,
                'prefs': self.prefs,
            },
            text=self.text,
            encoding='utf-8',
            discardable=True,
            priority=PRIORITY_IMMEDIATE if lines_added else PRIORITY_CURRENT,
            mtime=mtime,
            callback=invoke_callback,
        )

    def _post_trg_from_pos_handler(self, handler, context, request, response):
        # This needs to be proxied to the main thread for the callback invocation
        if not response.get('success'):
            msg = response.get('message')
            if not msg:
                msg = "%s: Can't get a trigger for position %s" % (context, request.get("pos", "<unknown position>"))
            try:
                handler.set_status_message(self, msg)
            except Exception as e:
                self.log.error("Error reporting scan_document error: %s", response.get('message', e))
                pass
            return
        else:
            trg = response['trg']
        try:
            if trg:
                handler.on_trg_from_pos(self, context, trg)
        except Exception as e:
            self.log.error("Error calling %s callback: %s", context, e)
            pass

    def trg_from_pos(self, handler, implicit, pos=None):
        self.service.send(
            command='trg-from-pos',
            path=self.path,
            language=self.lang,
            pos=self.pos if pos is None else pos,
            env={
                'env': self.env,
                'prefs': self.prefs,
            },
            implicit=implicit,
            text=self.text,
            encoding='utf-8',
            callback=functools.partial(self._post_trg_from_pos_handler, handler, 'trg_from_pos')
        )

    def preceding_trg_from_pos(self, handler, curr_pos, pos=None):
        self.service.send(
            command='trg-from-pos',
            path=self.path,
            language=self.lang,
            pos=self.pos if pos is None else pos,
            env={
                'env': self.env,
                'prefs': self.prefs,
            },
            text=self.text,
            encoding='utf-8',
            callback=functools.partial(self._post_trg_from_pos_handler, handler, 'preceding_trg_from_pos'),
            **{'curr-pos': curr_pos}
        )

    def defn_trg_from_pos(self, handler, pos=None):
        self.service.send(
            command='trg-from-pos',
            type='defn',
            path=self.path,
            language=self.lang,
            pos=self.pos if pos is None else pos,
            env={
                'env': self.env,
                'prefs': self.prefs,
            },
            text=self.text,
            encoding='utf-8',
            callback=functools.partial(self._post_trg_from_pos_handler, handler, 'defn_trg_from_pos')
        )

    def async_eval_at_trg(self, handler, trg, silent=False, keep_existing=False):
        def callback(request, response):
            try:
                if not response.get('success'):
                    try:
                        handler.set_status_message(self, response.get('message', ""), response.get('highlight', False))
                    except Exception as e:
                        self.log.error("Error reporting async_eval_at_trg error: %s", response.get("message", e))
                        pass
                    return

                if 'retrigger' in response:
                    trg['retriggerOnCompletion'] = response['retrigger']

                if 'cplns' in response:
                    # split into separate lists
                    cplns = response['cplns']
                    try:
                        handler.set_auto_complete_info(self, cplns, trg)
                    except Exception as e:
                        self.log.error("Error calling set_auto_complete_info: %s", e)
                        pass
                elif 'calltip' in response:
                    try:
                        handler.set_call_tip_info(self, response['calltip'], request.get('explicit', False), trg)
                    except Exception as e:
                        self.log.error("Error calling set_call_tip_info: e", e)
                        pass
                elif 'defns' in response:
                    handler.set_definitions_info(self, response['defns'], trg)
            finally:
                handler.done()

        self.service.send(
            command='eval',
            trg=trg,
            silent=silent,
            keep_existing=keep_existing,
            callback=callback,
        )

    def to_html_async(self, callback, flags=None, title=None):
        def invoke_callback(request, response):
            try:
                if response.get('success'):
                    RESULT_SUCCESSFUL = True
                    callback(RESULT_SUCCESSFUL, response.get('html'))
                else:
                    RESULT_ERROR = False
                    callback(RESULT_ERROR, None)
            except Exception as e:
                self.log.error("Error calling to_html callback: %s", e)

        flag_dict = {
            'include_styling': True,
            'include_html': True,
            'do_trg': True,
            'do_eval': True,
        }
        if flags is not None:
            flag_dict.update(flags)

        self.service.send(
            command='buf-to-html',
            path=self.path,
            language=self.lang,
            text=self.text,
            env={
                'env': self.env,
                'prefs': self.prefs,
            },
            title=title,
            flags=flag_dict,
            callback=invoke_callback,
        )

    def get_calltip_arg_range(self, handler, trg_pos, calltip, curr_pos):
        def callback(request, response):
            if not response.get('success'):
                msg = response.get('message')
                if not msg:
                    msg = "get_calltip_arg_range: Can't get a calltip at position %d" % curr_pos
                try:
                    handler.set_status_message(self, msg)
                except Exception as e:
                    self.log.error("Error reporting get_calltip_arg_range error: %s", response.get('message', e))
                    pass
                return
            start = response.get('start', -1)
            end = response.get('end', -1)
            try:
                handler.on_get_calltip_range(self, start, end)
            except Exception as e:
                self.log.error("Error calling get_calltip_arg_range callback: %s", e)
                pass

        self.service.send(
            command='calltip-arg-range',
            path=self.path,
            language=self.lang,
            text=self.text,
            encoding='utf-8',
            trg_pos=trg_pos,
            calltip=calltip,
            curr_pos=curr_pos,
            env={
                'env': self.env,
                'prefs': self.prefs,
            },
            callback=callback,
        )
