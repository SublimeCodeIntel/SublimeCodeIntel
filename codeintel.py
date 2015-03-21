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
from __future__ import absolute_import, unicode_literals, print_function

import os

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


class CodeIntel(object):
    def __init__(self):
        self.log = logging.getLogger(logger_name + '.' + self.__class__.__name__)
        self.mgr = None
        self._mgr_lock = threading.Lock()
        self.buffers = {}
        self._queue = queue.Queue()
        self._quit_application = False  # app is shutting down, don't try to respawn
        self._observers = weakref.WeakKeyDictionary()

    def add_observer(self, obj):
        if hasattr(obj, 'observer'):
            self._observers[obj] = True

    def notify_observers(self, topic, data):
        """Observer calls must be called on the main thread"""
        if topic:
            for obj in self._observers.keys():
                obj.observer(topic, data)

    def _on_mgr_init(self, mgr, message, progress=None):
        summary = None
        if progress == "(ABORTED)":
            summary = "Code Intelligence Initialization Aborted"
        elif not mgr or mgr.state is CodeIntelManager.STATE_DESTROYED:
            summary = "Startup failed: %s", message
        elif mgr.state is CodeIntelManager.STATE_BROKEN:
            summary = "There is an error with your code intelligence database; it must be reset before it can be used."
        elif mgr.state is CodeIntelManager.STATE_READY:
            pass  # nothing to report
        elif message is None and progress is None:
            pass  # nothing to report
        else:
            # progress update, not finished yet
            if isinstance(progress, (int, float)):
                self.notify_observers('progress', dict(message=message, progress=progress))
        if summary:
            self.notify_observers('error_message', dict(message=summary))
        elif message:
            self.notify_observers('status_message', dict(message=message))

    def _on_mgr_shutdown(self, mgr):
        # The codeintel manager is going away, drop the reference to it
        with self._mgr_lock:
            if self.mgr is mgr:
                self.mgr = None

    def activate(self, reset_db_as_necessary=False):
        self.log.debug("activating codeintel service: %r", reset_db_as_necessary)

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
                    init_callback=self._on_mgr_init,
                    shutdown_callback=self._on_mgr_shutdown,
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
        try:
            # run the new manager
            self.mgr.start(reset_db_as_necessary)
        except RuntimeError:
            # thread already started
            pass

    def deactivate(self):
        with self._mgr_lock:
            if self.mgr:
                self.mgr.shutdown()
                self.mgr = None

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
        assert self.mgr, \
            "CodeIntelManager.send() shouldn't be called when not enabled"
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
        path = os.path.normcase(path)  # Fix case on Windows
        for vid, buf in list(self.buffers.items()):
            if buf.path:
                continue
            if os.path.normcase(buf.path) == path:
                return buf
        return None


class CodeIntelManager(threading.Thread):
    STATE_UNINITIALIZED = ("uninitialized",)  # not initialized
    STATE_CONNECTED = ("connected",)  # child process spawned, connection up; not ready
    STATE_BROKEN = ("broken",)  # database is broken and needs to be reset
    STATE_READY = ("ready",)  # ready for use
    STATE_QUITTING = ("quitting",)  # shutting down
    STATE_DESTROYED = ("destroyed",)  # connection shut down, child process dead

    _state = STATE_UNINITIALIZED
    _send_request_thread = None  # background thread to send unsent requests
    _reset_db_as_necessary = False  # whether to reset the db if it's broken
    _watchdog_thread = None  # background thread to watch for process termination
    proc = None

    cpln_langs = []
    citadel_langs = []
    xml_langs = []
    stdlib_langs = []  # languages which support standard libraries
    languages = {}
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

    def __init__(self, service, init_callback=None, shutdown_callback=None):
        self.log = logging.getLogger(logger_name + '.' + self.__class__.__name__)
        self.service = service
        self._abort = set()
        self._next_id = 0
        self._init_callback = init_callback
        self._shutdown_callback = shutdown_callback
        self._state_condvar = threading.Condition()
        self.requests = {}  # keyed by request id; value is tuple (callback, request data, time sent) requests will time out at some point...
        self.unsent_requests = queue.Queue()
        threading.Thread.__init__(self, name="Codeintel Manager %s" % (id(self)))

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
        self.abort = True
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

    def kill(self):
        """
        Kill the subprocess. This may be safely called when the process has
        already exited.  This should *always* be called no matter how the
        process exits, in order to maintain the correct state.
        """
        try:
            self.proc.kill()
        except:
            pass
        try:
            self.pipe.close()
        except:
            pass  # The other end is dead, this is kinda pointless
        try:
            # Shut down the request sending thread (self._send_request_thread)
            self.unsent_requests.put((None, None))
        except:
            pass  # umm... no idea?
        self.state = CodeIntelManager.STATE_DESTROYED
        self.pipe = None
        self._shutdown_callback(self)

    def init_child(self):
        import process
        assert threading.current_thread().name != "MainThread", \
            "CodeIntelManager.init_child should run on background thread!"
        self.log.debug("initializing child process")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(("127.0.0.1", 0))
            sock.listen(0)

            db_base_dir = os.path.expanduser('~/.codeintel')
            connect = "%s:%s" % sock.getsockname()

            log_file = os.path.join(db_base_dir, 'codeintel.log')
            args = [db_base_dir, connect, 'WARNING', log_file]

            codeintel_exec = "/usr/local/bin/codeintel"
            if not os.path.exists(codeintel_exec):
                codeintel_exec = "codeintel"
            cmd = [codeintel_exec] + args

            self.log.debug("Running OOP: [%s]", ", ".join('"' + c + '"' for c in cmd))
            self.proc = process.ProcessOpen(cmd, cwd=None, env=None)
            assert self.proc.returncode is None, "Early process death!"

            self._watchdog_thread = threading.Thread(
                target=self._watchdog_thread,
                name="CodeIntel Subprocess Watchdog",
                args=(self.proc,),
            )
            self._watchdog_thread.start()

            self.conn = sock.accept()
            sock.close()  # no need to keep listening
            self.pipe = self.conn[0].makefile('rwb', 0)
            self.state = CodeIntelManager.STATE_CONNECTED
        except Exception as e:
            message = "Error initing child: %s", e
            self.log.debug(message)
            self.pipe = None
            self.kill()
            self._init_callback(self, message)
        else:
            self._send_init_requests()

    def _watchdog_thread(self, proc):
        self.log.debug("Waiting for process to die...")
        if hasattr(proc, 'wait'):
            proc.wait()
        elif hasattr(proc, 'join'):
            proc.join()
        self.log.debug("Child process died!")
        try:
            self.kill()
        except:
            pass  # At app shutdown this can die uncleanly

    def _send_init_requests(self):
        assert threading.current_thread().name != "MainThread", \
            "CodeIntelManager._send_init_requests should run on background thread!"
        self.log.debug("sending internal initial requests")

        outstanding_cpln_langs = set()

        def update(message, response=None, state=CodeIntelManager.STATE_DESTROYED, progress=None):
            if state in (CodeIntelManager.STATE_DESTROYED, CodeIntelManager.STATE_BROKEN):
                self.kill()
            if state is not None:
                self.state = state
            self._init_callback(self, message, progress)

        def get_citadel_langs(request, response):
            if not response.get('success', False):
                update("Failed to get citadel languages:", response)
                return
            self.citadel_langs = sorted(response.get('languages'))

        def get_xml_langs(request, response):
            if not response.get('success', False):
                update("Failed to get XML languages:", response)
                return
            self.xml_langs = sorted(response.get('languages'))

        def get_stdlib_langs(request, response):
            if not response.get('success', False):
                update("Failed to get languages which support standard libraries:", response)
                return
            self.stdlib_langs = sorted(response.get('languages'))

        def get_cpln_langs(request, response):
            if not response.get('success', False):
                update("Failed to get completion languages:", response)
                return
            self.cpln_langs = sorted(response.get('languages'))
            for lang in self.cpln_langs:
                outstanding_cpln_langs.add(lang)
                self._send(callback=get_lang_info, command='get-language-info', language=lang)

        def get_lang_info(request, response):
            lang = request['language']
            if not response.get('success', False):
                update("Failed to get information for %s:" % (lang,), response)
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
                update("Codeintel startup aborted", progress="(ABORTED)")
                return

            update(response.get('message'), state=None, progress=response.get('progress'))

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
                self._send(callback=fixup_db, command="database-preload", languages=langs)
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
            self._send_request_thread = threading.Thread(
                target=self._send_queued_requests,
                name="Codeintel Manager Request Sending Thread")
            self._send_request_thread.daemon = True
            self._send_request_thread.start()
            update("Codeintel ready.", state=CodeIntelManager.STATE_READY)

        self._send(callback=get_cpln_langs, command='get-languages', type='cpln')
        self._send(callback=get_citadel_langs, command='get-languages', type='citadel')
        self._send(callback=get_xml_langs, command='get-languages', type='xml')
        self._send(callback=get_stdlib_langs, command='get-languages', type='stdlib-supported')

        self.set_global_environment(self.env, self.prefs)

        def update_callback(response):
            if not response.get("success", False):
                update("Failed to get available catalogs:", response)
        self.update_catalogs(update_callback=update_callback)

    def set_global_environment(self, env, prefs):
        self.env = env
        self.prefs = prefs
        self._send(
            command='set-environment',
            env=self.env,
            prefs=self.prefs,
        )

    def update_catalogs(self, update_callback=None):
        def get_available_catalogs(request, response):
            if response.get("success", False):
                self.available_catalogs = response.get('catalogs', [])
            update_callback(response)
        if not update_callback:
            update_callback = lambda *args, **kwargs: None
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
        if self.state is CodeIntelManager.STATE_QUITTING:
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
        self.pipe.write(buf)

    def run(self):
        """Event loop for the codeintel manager background thread"""
        assert threading.current_thread().name != "MainThread", \
            "CodeIntelManager.run should run on background thread!"

        self.init_child()
        if not self.proc:
            return  # init child failed

        first_buf = True
        discard_time = 0.0
        try:
            buf = b''
            while self.proc and self.pipe:
                # Loop to read from the pipe
                ch = self.pipe.read(1)
                if ch == b'{':
                    length = int(buf)
                    buf = ch
                    while len(buf) < length:
                        last_size = len(buf)
                        buf += self.pipe.read(length - len(buf))
                        if len(buf) == last_size:
                            # nothing read, EOF
                            raise IOError("Failed to read frame from socket")
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
                            except:
                                self.log.exception("Failed timing out request")
                            else:
                                self.log.debug("Discarding request %r", request)
                            del self.requests[req_id]
        except Exception as ex:
            if isinstance(ex, IOError) and self.state in (CodeIntelManager.STATE_QUITTING, CodeIntelManager.STATE_DESTROYED):
                return  # this is intentional
            self.log.exception("Error reading data from codeintel")
            self.kill()

    def handle(self, response):
        """Handle a response from the codeintel process"""
        self.log.debug("handling: %r", response)
        req_id = response.get('req_id')
        response_command = response.get('command', '')
        if req_id is None:
            # unsolicited response, look for a handler
            try:
                if not response_command:
                    raise ValueError("Invalid response frame %r" % response)
                meth = getattr(self, 'do_' + response_command.replace('-', '_'), None)
                if not meth:
                    raise ValueError("Unknown unsolicited response \"%s\"" % response_command)
                meth(response)
            except:
                self.log.exception("Error handling unsolicited response")
            return
        callback, request, sent_time = self.requests.get(req_id, (None, None, None))
        if not request:
            self.log.error("Discard response for unknown request %s (command %s): have %s",
                      req_id, response_command or '%r' % response, sorted(self.requests.keys()))
            return
        request_command = request.get('command', '')
        self.log.info("Request %s (command %s) took %0.2f seconds", req_id, request_command or '<unknown>', time.time() - sent_time)
        # assert response.get('command', request_command) == request_command, \
        #     "Got unexpected response command %s from request %s" % (response_command, request_command)
        if 'success' in response:
            # remove completed request
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
        env = dict(self.service.mgr.env or {})
        env.update(self._env or {})
        return env

    @env.setter
    def env(self, env):
        self._env = env

    @property
    def prefs(self):
        prefs = list(self.service.mgr.prefs or [])
        for pref in self._prefs or []:
            if pref not in prefs:
                prefs.append(pref)
        return prefs

    @prefs.setter
    def prefs(self, prefs):
        self._prefs = [prefs] if isinstance(prefs, dict) else prefs

    @property
    def cpln_fillup_chars(self):
        return self.service.mgr.languages[self.lang]['cpln_fillup_chars']

    @property
    def cpln_stop_chars(self):
        return self.service.mgr.languages[self.lang]['cpln_stop_chars']

    def scan_document(self, handler, lines_added, file_mtime=False):
        def callback(request, response):
            if not response.get('success'):
                msg = response.get('message')
                if not msg:
                    msg = "scan_document: Can't scan document"
                try:
                    handler.set_status_message(self, msg)
                except:
                    self.log.exception("Error reporting scan_document error: %s", response.get('message', "<error not available>"))
                    pass
                return
            try:
                handler.on_document_scanned(self)
            except:
                self.log.exception("Error calling scan_document callback")
                pass

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
            callback=callback,
        )

    def _post_trg_from_pos_handler(self, handler, context, request, response):
        # This needs to be proxied to the main thread for the callback invocation
        if not response.get('success'):
            msg = response.get('message')
            if not msg:
                msg = "%s: Can't get a trigger for position %s" % (context, request.get("pos", "<unknown position>"))
            try:
                handler.set_status_message(self, msg)
            except:
                self.log.exception("Error reporting scan_document error: %s", response.get('message', "<error not available>"))
                pass
            return
        else:
            trg = response['trg']
        try:
            if trg:
                handler.on_trg_from_pos(self, context, trg)
        except:
            self.log.exception("Error calling %s callback", context)
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
            if not response.get('success'):
                try:
                    handler.set_status_message(self, response.get('message', ""), response.get('highlight', False))
                except:
                    self.log.exception("Error reporting async_eval_at_trg error: %s", response.get("message", "<error not available>"))
                    pass
                return

            if 'retrigger' in response:
                trg['retriggerOnCompletion'] = response['retrigger']

            if 'cplns' in response:
                # split into separate lists
                cplns = response['cplns']
                try:
                    handler.set_auto_complete_info(self, cplns, trg)
                except:
                    self.log.exception("Error calling set_auto_complete_info")
                    pass
            elif 'calltip' in response:
                try:
                    handler.set_call_tip_info(self, response['calltip'], request.get('explicit', False), trg)
                except Exception:
                    self.log.exception("Error calling set_call_tip_info")
                    pass
            elif 'defns' in response:
                handler.set_definitions_info(self, response['defns'], trg)

        self.service.send(
            command='eval',
            trg=trg,
            silent=silent,
            keep_existing=keep_existing,
            callback=callback,
        )

    def get_calltip_arg_range(self, handler, trg_pos, calltip, curr_pos):
        def callback(request, response):
            if not response.get('success'):
                msg = response.get('message')
                if not msg:
                    msg = "get_calltip_arg_range: Can't get a calltip at position %d" % curr_pos
                try:
                    handler.set_status_message(self, msg)
                except:
                    self.log.exception("Error reporting get_calltip_arg_range error: %s", response.get('message', "<error not available>"))
                    pass
                return
            start = response.get('start', -1)
            end = response.get('end', -1)
            try:
                handler.on_get_calltip_range(self, start, end)
            except:
                self.log.exception("Error calling get_calltip_arg_range callback")
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
