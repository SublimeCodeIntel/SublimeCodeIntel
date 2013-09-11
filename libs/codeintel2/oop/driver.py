#!/usr/bin/env python2

try:
    # codeintel will attempt to import xpcom; make sure that's working by
    # explicitly importing xpcom._xpcom, otherwise xpcom.xpt will fail to
    # import
    import xpcom
    import xpcom._xpcom
except ImportError:
    pass

import codeintel2.accessor
import codeintel2.buffer
import codeintel2.common
import codeintel2.indexer
import codeintel2.udl
from codeintel2.database.database import Database, DatabaseError
import codeintel2.environment
import collections
import functools
import imp
import itertools
import json
import logging
import os.path
import Queue
import shutil
import sys
import threading
import traceback
import uuid
from . import controller
from os.path import abspath, normcase, normpath

log = logging.getLogger("codeintel.oop.driver")


class RequestFailure(Exception):
    """ An exception to indicate a request failure
    Raising this exception is equivalent of aborting the current (synchronous)
    request processing and calling Driver.fail().  All arguments are the same as
    when using Driver.fail().
    """
    def __init__(self, *args, **kwargs):
        Exception.__init__(self)
        self.args = args
        self.kwargs = kwargs


class CommandHandler(object):
    """Interface for a class that handles commands from the driver; this may
    choose to be stateless"""

    supportedCommands = []
    """Iterable of commands this handler supports; each item is a string naming
    the command to handle, e.g. "halt-and-catch-fire"."""

    def canHandleRequest(self, request):
        """Double-check if this handler can handle the given request.  This will
        only be called if multiple handlers claim to be able to handle the same
        command; might be useful, for example, if some handlers are language-
        specific.
        @param request {Request} The request to handle.
        @return {bool} Whether this handler can handle the given request.
        """
        raise NotImplementedError

    def handleRequest(self, request, driver):
        """Handle a given request.  No return value is expected; the handler
        should call driver.send() at some point to indicate handle completion
        (or one of the helpers that eventually call driver.send).
        @param request {Request} The request to handle; request.command will be
            a command this handler claims to be able to handle.
        @return None
        @note This is executed on a different thread than where communication
            happens; the implementation is expected to (but doesn't have to)
            block.  Exceptions here will be caught and communicated to the host
            process as a command failure.
        """
        raise NotImplementedError


class LoggingHandler(logging.Handler):
    """Log handler class to forward messages to the main process"""

    def __init__(self, driver):
        logging.Handler.__init__(self)
        self._driver = driver

    def emit(self, record):
        """Emit a record.  Do this over the driver's normal pipe."""
        try:
            if record.levelno < logging.WARNING:
                # Don't log info/debug records. We can look at codeinte.log for
                # those.  This gets especially bad when logging what's being
                # sent over the wire...
                return
            self._driver.send(request=None,
                              command="report-message",
                              type="logging",
                              name=record.name,
                              message=self.format(record),
                              level=record.levelno)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


class Driver(threading.Thread):
    """
    Out-of-process codeintel2 driver
    This class implements the main loop of the codeintel worker process
    This should be a singleton object
    """

    # static
    _instance = None
    _command_handler_map = collections.defaultdict(list)
    """Registered command handlers; the key is the command name (a str), and the
    value is a list of command handler instances or (for lazy handlers) a
    single-element tuple containing the callable to get the real handler."""
    _default_handler = None
    """The default (core) command handler; instance of a CoreHandler"""
    _builtin_commands = {}
    """Built-in commands that cannot be overridden"""

    def __init__(self, db_base_dir=None, fd_in=sys.stdin, fd_out=sys.stdout):
        threading.Thread.__init__(self, name="Codeintel OOP Driver")
        assert Driver._instance is None, "Driver should be a singleton"
        Driver._instance = self
        logging.root.addHandler(LoggingHandler(self))
        self.daemon = True

        self.fd_in = fd_in
        self.fd_out = fd_out
        self.abort = None
        self.quit = False
        self.buffers = {}  # path to Buffer objects
        self.next_buffer = 0
        self.active_request = None

        self.send_queue = Queue.Queue()
        self.send_thread = threading.Thread(target=self._send_proc)
        self.send_thread.daemon = True
        self.send_thread.start()

        self.queue = collections.deque()
        self.queue_cv = threading.Condition()
        self.env = Environment(name="global",
                               send_fn=functools.partial(self.send, request=None))

        # Fill out the non-overridable build-in commands
        self._builtin_commands = {}
        for attr in dir(self):
            # Note that we check startswith first to avoid getters etc.
            if attr.startswith("do_") and callable(getattr(self, attr)):
                command = attr[len("do_"):].replace("_", "-")
                self._builtin_commands[command] = getattr(self, attr)

        from codeintel2.manager import Manager
        log.debug("using db base dir %s", db_base_dir)
        self.mgr = Manager(db_base_dir=db_base_dir,
                           db_catalog_dirs=[],
                           db_event_reporter=self._DBEventReporter(self),
                           env=self.env,
                           on_scan_complete=self._on_scan_complete)
        self.mgr.initialize()

    def _on_scan_complete(self, scan_request):
        if scan_request.status in ("changed", "skipped"):
            # Send unsolicited response about the completed scan
            buf = scan_request.buf
            self.send(request=None,
                      path=buf.path,
                      language=buf.lang,
                      command="scan-complete")

    class _DBEventReporter(object):
        def __init__(self, driver):
            self.driver = driver
            self.log = log.getChild("DBEventReporter")
            self.debug = self.log.debug

            # directories being scanned (completed or not)
            # key is unicode path, value is number of times it's active
            self._dirs = collections.defaultdict(int)
            # directories which are complete (unicode path)
            self._completed_dirs = set()

        def send(self, **kwargs):
            self.driver.send(request=None, command="report-message", **kwargs)

        def __call__(self, message):
            """Old-style status messages before long-running jobs
            @param msg {str or None} The message to display
            """
            if len(self._dirs):
                return  # ignore old-style db events if we're doing a scan
            self.debug("db event: %s", message)
            self.send(message=message)

        def onScanStarted(self, description, dirs=set()):
            """Called when a directory scan is about to start
            @param description {unicode} A string suitable for showing the user
                about the upcoming operation
            @param dirs {set of unicode} The directories about to be scanned
            """
            self.debug("scan started: %s (%s dirs)", description, len(dirs))

            assert dirs, "onScanStarted expects non-empty directories"
            if not dirs:  # empty set - we shouldn't have gotten here, but be nice
                return
            for dir_path in dirs:
                self._dirs[dir_path] += 1
            self.send(type="scan-progress", message=description,
                      completed=len(self._completed_dirs),
                      total=len(self._dirs))

        def onScanDirectory(self, description, dir_path, current=None, total=None):
            """Called when a directory is being scanned (out of possibly many)
            @param description {unicode} A string suitable for showing the user
                    regarding the progress
            @param dir {unicode} The directory currently being scanned
            @param current {int} The current progress
            @param total {int} The total number of directories to scan in this
                    request
            """
            self.debug("scan directory: %s (%s %s/%s)",
                       description, dir_path, current, total)

            assert dir_path, "onScanDirectory got no directory"
            if dir_path:
                self._completed_dirs.add(dir_path)
            self.send(type="scan-progress", message=description,
                      completed=len(self._completed_dirs),
                      total=len(self._dirs))

        def onScanComplete(self, dirs=set(), scanned=set()):
            """Called when a scan operation is complete
            @param dirs {set of unicode} The directories that were intially
                   requested to be scanned (as pass in onScanStarted)
            @param scanned {set of unicode} Directories which were successfully
                   scanned.  This may be a subset of dirs if the scan was
                   aborted.
            """
            self.debug("scan complete: scanned %r/%r dirs",
                       len(scanned), len(dirs))

            for dir_path in dirs:
                self._dirs[dir_path] -= 1
                if not self._dirs[dir_path]:
                    del self._dirs[dir_path]
                    self._completed_dirs.discard(dir_path)
            self.send(
                type="scan-progress", completed=len(self._completed_dirs),
                total=len(self._dirs))

    REQUEST_DEFAULT = object()

    def send(self, request=REQUEST_DEFAULT, **kwargs):
        """
        Send a response
        """
        data = dict(kwargs)
        if request is Driver.REQUEST_DEFAULT:
            request = self.active_request
        if request:
            data["req_id"] = request.id
        if "success" not in data:
            data["success"] = True
        elif data["success"] is None:
            del data["success"]
        buf = json.dumps(data, separators=(',', ':'))
        buf_len = str(len(buf))
        log.debug("sending: %s:[%s]", buf_len, buf)
        self.send_queue.put(buf)

    def _send_proc(self):
        while True:
            buf = self.send_queue.get()
            try:
                buf_len = str(len(buf))
                self.fd_out.write(buf_len)
                self.fd_out.write(buf)
            finally:
                self.send_queue.task_done()

    def fail(self, request=REQUEST_DEFAULT, **kwargs):
        kwargs = kwargs.copy()
        if not "command" in kwargs and request:
            try:
                kwargs["command"] = request["command"]
            except KeyError:
                pass
        return self.send(request=request, success=False, **kwargs)

    def exception(self, request=REQUEST_DEFAULT, **kwargs):
        return self.fail(request=request, stack=traceback.format_exc(), **kwargs)

    def get_buffer(self, request=REQUEST_DEFAULT, path=None):
        if request is Driver.REQUEST_DEFAULT:
            request = self.active_request
        if path is None:
            if not "path" in request:
                raise RequestFailure(message="No path given to locate buffer")
            path = request.path
        if abspath(path) == path:
            # this is an actual file path, not a URL or whatever
            path = normcase(normpath(path))
        try:
            buf = self.buffers[path]
        except KeyError:
            buf = None
        else:
            if "language" in request and buf.lang != request.language:
                buf = None  # language changed, re-scan

        if not buf:
            # Need to construct a new buffer
            lang = request.get("language")
            if request.get("text") is not None:
                # pass no content; we'll reset it later
                buf = self.mgr.buf_from_content("", lang, path=path)
            else:
                # read from file
                try:
                    buf = self.mgr.buf_from_path(path, lang,
                                                 encoding=request.get("encoding"))
                except OSError:
                    # Can't read the file
                    buf = self.mgr.buf_from_content("", lang, path=path)
                assert not request.path.startswith("<"), \
                    "Can't create an unsaved buffer with no text"

        if request.get("text") is not None:
            # overwrite the buffer contents if we have new ones
            buf.accessor.reset_content(request.text)

        try:
            env = request["env"]
        except KeyError:
            pass  # no environment set, use current environment
        else:
            if env.get("env", {}) is None and env.get("prefs", []) is None:
                buf._env = None  # explicitly clearing environment
            elif buf._env:
                buf._env.update(env)
            else:
                buf._env = Environment(env, name=os.path.basename(path))

        # log.debug("Got buffer %r: [%s]", buf, buf.accessor.content)
        log.debug("Got buffer %r", buf)

        self.buffers[path] = buf
        return buf

    def do_abort(self, request):
        try:
            req_id = request["id"]
            with self.queue_cv:
                for item in self.queue:
                    if queue.get("req_id") == req_id:
                        self.queue.remove(queue)
                        self.send(request=request)
                        break
                else:
                    self.abort = req_id
                    if self.active_request and self.active_request.id == req_id:
                        # need to wait a bit...
                        self.send(request=request)
                    else:
                        self.fail(request=request,
                                  message="Request %s not found" % (req_id,))
        except RequestFailure as e:
            self.fail(request=request, *e.args, **e.kwargs)
        except Exception as e:
            log.exception(e.message)
            self.exception(request=request, message=e.message)

    def do_add_dirs(self, request):
        catalog_dirs = request.get("catalog-dirs", None)
        if catalog_dirs is not None:
            self.mgr.db.catalog_dirs.extend(catalog_dirs)
            catalog_dirs = self.mgr.db.catalog_dirs
        lexer_dirs = request.get("lexer-dirs", [])
        codeintel2.udl.UDLLexer.add_extra_lexer_dirs(lexer_dirs)
        module_dirs = request.get("module-dirs", [])
        if module_dirs:
            self.mgr._register_modules(module_dirs)
        if catalog_dirs is not None:
            self.mgr.db.get_catalogs_zone().catalog_dirs = catalog_dirs

    def do_load_extension(self, request):
        """Load an extension that, for example, might provide additional
        command handlers"""
        path = request.get("module-path", None)
        if not path:
            raise RequestFailure(msg="load-extension requires a module-path")
        name = request.get("module-name", None)
        if not name:
            raise RequestFailure(msg="load-extension requires a module-name")
        iinfo = imp.find_module(name, [path])
        try:
            module = imp.load_module(name, *iinfo)
        finally:
            if iinfo and iinfo[0]:
                iinfo[0].close()
        callback = getattr(module, "registerExtension", None)
        if not callback:
            raise RequestFailure(msg="load-extension module %s should "
                                     "have a 'registerExtension' method "
                                     "taking no arguments" % (name,))
        callback()
        self.send()  # success, finally

    def do_quit(self, request):
        self.quit = True
        self.send(command="quit")

    def report_error(self, message):
        self.send(request=None,
                  command="report-error",
                  message=unicode(message))

    def start(self):
        """Start reading from the socket and dump requests into the queue"""
        log.info("Running codeintel driver...")
        buf = ""
        self.send(success=None)
        self.daemon = True
        threading.Thread.start(self)
        while not self.quit:
            try:
                ch = self.fd_in.read(1)
            except IOError:
                log.debug(
                    "Failed to read frame length, assuming connection died")
                self.quit = True
                break
            if len(ch) == 0:
                log.debug("Input was closed")
                self.quit = True
                break
            if ch == "{":
                size = int(buf, 10)
                try:
                    buf = ch + self.fd_in.read(
                        size - 1)  # exclude already-read {
                except IOError:
                    log.debug(
                        "Failed to read frame data, assuming connection died")
                    self.quit = True
                    break
                try:
                    buf = buf.decode("utf-8")
                except UnicodeDecodeError:
                    pass  # what :(
                try:
                    data = json.loads(buf)
                    request = Request(data)
                except Exception as e:
                    log.exception(e)
                    self.exception(message=e.message, request=None)
                    continue
                finally:
                    buf = ""
                if request.get("command") == "abort":
                    self.do_abort(request=request)
                else:
                    log.debug("queuing request %r", request)
                    with self.queue_cv:
                        self.queue.appendleft(request)
                        self.queue_cv.notify()
            elif ch in "0123456789":
                buf += ch
            else:
                raise ValueError("Invalid request data: " + ch.encode("hex"))

    def run(self):
        """Evaluate and send results back"""
        log.info("Running codeintel eval thread...")
        buf = ""
        log.debug("default supported commands: %s",
                  ", ".join(self._default_handler.supportedCommands))
        while True:
            with self.queue_cv:
                try:
                    request = self.queue.pop()
                except IndexError:
                    self.queue_cv.wait()
                    continue
            log.debug("doing request %r", request)
            try:
                self.active_request = request
                command = request.command
                # First, check abort and quit; don't allow those to be
                # overridden
                try:
                    builtin = self._builtin_commands[command]
                except KeyError:
                    pass
                else:
                    builtin(request)
                    continue
                handlers = self._command_handler_map.get(command, [])[:]
                if command in self._default_handler.supportedCommands:
                    # The default handler can deal with this, put it at the end
                    handlers.append(self._default_handler)
                for handler in handlers:
                    if isinstance(handler, tuple):
                        try:
                            real_handler = handler[0]()
                        except Exception as ex:
                            log.exception(
                                "Failed to get lazy handler for %s", command)
                            real_handler = None
                        if real_handler is None:
                            # Handler failed to instantiate, drop it
                            try:
                                self._command_handler_map[
                                    "command"].remove(handler)
                            except ValueError:
                                pass  # ... shouldn't happen, but tolerate it
                            continue
                        for handlers in self._command_handler_map.values():
                            try:
                                handlers[handlers.index(
                                    handler)] = real_handler
                            except ValueError:
                                pass  # handler not in this list
                        handler = real_handler
                    if handler.canHandleRequest(request):
                        handler.handleRequest(request, self)
                        break
                else:
                    self.fail(request=request,
                              msg="Don't know how to handle command %s" % (command,))

            except RequestFailure as e:
                self.fail(request=request, *e.args, **e.kwargs)
            except Exception as e:
                log.exception(e.message)
                self.exception(request=request, message=e.message)
            finally:
                self.active_request = None

    @classmethod
    def registerCommandHandler(cls, handlerInstance):
        """Register a command handler"""
        for command in handlerInstance.supportedCommands:
            cls._command_handler_map[command].append(handlerInstance)

    @classmethod
    def registerLazyCommandHandler(cls, supported_commands, constructor):
        """Register a lazy command handler
        @param supported_commands {iterable} The commands to handle; each
            element should be a str of the command name.
        @param constructor {callable} Function to be called to get the real
            command handler; it should take no arguments and return a command
            handler instance.  It may return None if the command is not
            available; it will not be asked again.
        """
        for command in supported_commands:
            cls._command_handler_map[command].append((constructor,))

    @classmethod
    def getInstance(cls):
        """Get the singleton instance of the driver"""
        return Driver._instance


class CoreHandler(CommandHandler):
    """The default command handler for core commands.
    This class is a stateless singleton.  (Other command handlers don't have to
    be)."""

    _stdlib_langs = None

    def __init__(self):
        supportedCommands = set()
        for prop in dir(self):
            if prop.startswith("do_") and callable(getattr(self, prop)):
                supportedCommands.add(prop[len("do_"):].replace("_", "-"))
        self.supportedCommands = list(supportedCommands)

    def canHandleRequest(self, request):
        return True  # we can handle any request we are registered to handle

    def handleRequest(self, request, driver):
        meth = getattr(self, "do_" + request.command.replace("-", "_"))
        meth(request, driver)

    def do_database_info(self, request, driver):
        """Figure out what kind of state the codeintel database is in"""
        try:
            if not os.path.exists(os.path.join(driver.mgr.db.base_dir, "VERSION")):
                log.debug("Database does not exist")
                driver.send(state="preload-needed")
                return
            if not os.path.isdir(os.path.join(driver.mgr.db.base_dir, "db", "stdlibs")):
                log.debug("Database does not have stdlibs")
                driver.send(state="preload-needed")
                return
            driver.mgr.db.check()
            state, details = driver.mgr.db.upgrade_info()
            if state == Database.UPGRADE_NOT_NECESSARY:
                # we _might_ need to deal with the stdlib stuff.
                # assume that having one stdlib per language is good enough
                std_libs = driver.mgr.db.get_stdlibs_zone()
                std_lib_langs = set()
                for lang in self._get_stdlib_langs(driver):
                    for ver, name in std_libs.vers_and_names_from_lang(lang):
                        lib_path = os.path.join(std_libs.base_dir, name)
                        if os.path.exists(lib_path):
                            break
                    else:
                        log.debug("no stdlib found for %s", lang)
                        driver.send(state="preload-needed")
                        break
                else:
                    driver.send(state="ready")
            elif state == Database.UPGRADE_NECESSARY:
                driver.send(state="upgrade-needed")
            elif state == Database.UPGRADE_NOT_POSSIBLE:
                driver.send(state="upgrade-blocked", **{
                            "state-detail": details})
        except Exception:
            log.exception("Error looking up database info")
            driver.send(state="broken",
                        state_detail="Unexpected error getting DB upgrade info")

    def do_database_reset(self, request, driver):
        driver.mgr.db.reset(backup=False)
        driver.send()

    def do_database_upgrade(self, request):
        """Upgrade the database to the current version"""
        try:
            driver.mgr.db.upgrade()
        except DatabaseError as ex:
            errmsg = ("Could not upgrade your Code Intelligence Database "
                      "because: %s. Your database will be backed up "
                      "and a new empty database will be created." % ex)
            driver.exception(message=errmsg)
        except:
            errmsg = ("Unexpected error upgrading your database. "
                      "Your database will be backed up "
                      "and a new empty database will be created.")
            driver.exception(message=errmsg, detail=traceback.format_exc())
        else:
            driver.send()

    def do_database_preload(self, request, driver):
        if not os.path.exists(os.path.join(driver.mgr.db.base_dir, "VERSION")):
            shutil.rmtree(driver.mgr.db.base_dir, ignore_errors=True)
            driver.mgr.db.create()

        progress_base = 0  # progress base for current step
        progress_max = 0  # progress max for current step

        def progress_callback(message, value):
            """Progress callback for codeintel
            @param message {str} A message to display
            @param value {int} Some number between 0 and 100"""
            progress_offset = value * (progress_max - progress_base) / 100.0
            driver.send(success=None, total=100, message=message,
                        progress=(progress_offset + progress_base))

        # Stage 1: stdlibs zone
        # Currently updates the stdlibs for languages that Komodo is
        # configured to use (first found on the PATH or set in prefs).
        driver.send(success=None, progress=0, total=100,
                    message="Pre-loading standard library data...")
        stdlibs_zone = driver.mgr.db.get_stdlibs_zone()
        if stdlibs_zone.can_preload():
            progress_max = 80
            stdlibs_zone.preload(progress_callback)
        else:
            langs = request.get("languages", None)
            if not langs:
                langs = dict(zip(self._get_stdlib_langs(driver),
                                 itertools.repeat(None)))
            progress_base = 5
            progress_incr = (80 - progress_base) / len(
                langs)  # stage 1 goes up to 80%
            for lang, version in sorted(langs.items()):
                if driver.abort == request.id:
                    raise RequestFailure(msg="Aborted", abort=True)
                progress_max = progress_base + progress_incr
                if not version:
                    # Update everything for this language
                    driver.send(
                        success=None, progress=progress_base, total=100,
                        message="%s standard library..." % (lang,))
                    stdlibs_zone.update_lang(lang, ver=None,
                                             progress_cb=progress_callback)
                else:
                    driver.send(
                        success=None, progress=progress_base, total=100,
                        message="%s %s standard library..." % (lang, version))
                    stdlibs_zone.update_lang(lang, ver=version,
                                             progress_cb=progress_callback)
                progress_base = progress_max

        # Stage 2: catalog zone
        # Preload catalogs that are enabled by default (or perhaps
        # more than that). For now we preload all of them.
        driver.send(success=None, progress=80, total=100,
                    message="Pre-loading catalogs...")
        progress_base = 80
        progress_max = 100
        catalogs_zone = driver.mgr.db.get_catalogs_zone()
        catalogs = request.get("catalogs",
                               driver.env.get_pref("codeintel_selected_catalogs", None))
        catalogs_zone.update(request.get("catalogs"),
                             progress_cb=progress_callback)

        driver.send(message="Code intelligence database pre-loaded.")

    def do_get_languages(self, request, driver):
        typ = request.get("type")
        if typ == "cpln":
            driver.send(languages=driver.mgr.get_cpln_langs())
        elif typ == "citadel":
            driver.send(languages=driver.mgr.get_citadel_langs())
        elif typ == "xml":
            driver.send(languages=filter(driver.mgr.is_xml_lang,
                                         driver.mgr.buf_class_from_lang.keys()))
        elif typ == "multilang":
            driver.send(languages=filter(driver.mgr.is_multilang,
                                         driver.mgr.buf_class_from_lang.keys()))
        elif typ == "stdlib-supported":
            driver.send(languages=self._get_stdlib_langs(driver))
        else:
            raise RequestFailure(message="Unknown language type %s" % (typ,))

    def _get_stdlib_langs(self, driver):
        if self._stdlib_langs is None:
            stdlibs_zone = driver.mgr.db.get_stdlibs_zone()
            langs = set()
            for lang in driver.mgr.buf_class_from_lang.keys():
                if stdlibs_zone.vers_and_names_from_lang(lang):
                    langs.add(lang)
            self._stdlib_langs = sorted(langs)
        return self._stdlib_langs

    def do_get_language_info(self, request, driver):
        try:
            language = request.language
        except AttributeError:
            raise RequestFailure(message="No language supplied")
        try:
            cls = driver.mgr.buf_class_from_lang[language]
        except KeyError:
            raise RequestFailure(message="Unknown language %s" % (language,))
        driver.send(**{"completion-fillup-chars": cls.cpln_fillup_chars,
                       "completion-stop-chars": cls.cpln_stop_chars})

    def do_get_available_catalogs(self, request, driver):
        zone = driver.mgr.db.get_catalogs_zone()
        catalogs = []
        for catalog in zone.avail_catalogs():
            catalogs.append({"name": catalog["name"],
                             "lang": catalog["lang"],
                             "description": catalog["description"],
                             "cix_path": catalog["cix_path"],
                             "selection": catalog.get("selection") or
                             catalog["name"] or
                             catalog["cix_path"],
                             })
        driver.send(catalogs=catalogs)

    def do_set_environment(self, request, driver):
        try:
            env = request["env"]
        except KeyError:
            pass
        else:
            driver.env.override_env(env)
        try:
            prefs = request["prefs"]
        except KeyError:
            pass
        else:
            driver.env.override_prefs(prefs)
        driver.send()

    def do_scan_document(self, request, driver):
        buf = driver.get_buffer(request)
        if not driver.mgr.is_citadel_lang(buf.lang):
            driver.send()  # Nothing to do here
            return
        if not hasattr(buf, "scan"):
            driver.send()  # Can't scan this buffer (e.g. Text)
            return
        priority = request.get("priority", codeintel2.common.PRIORITY_CURRENT)
        mtime = request.get("mtime")
        if mtime is not None:
            mtime = long(mtime)

        def on_complete():
            driver.send(request=request)

        assert buf.accessor.text is not None, \
            "No text!"

        scan_request = codeintel2.indexer.ScanRequest(buf,
                                                      priority,
                                                      mtime=mtime,
                                                      on_complete=on_complete)
        if priority <= codeintel2.common.PRIORITY_IMMEDIATE:
            delay = 0
        else:
            delay = 1.5
        driver.mgr.idxr.stage_request(scan_request, delay)

    def do_trg_from_pos(self, request, driver):
        try:
            pos = int(request.pos)
        except AttributeError:
            raise RequestFailure(message="No position given for trigger")
        buf = driver.get_buffer(request)
        if "curr-pos" in request:
            trg = buf.preceding_trg_from_pos(pos, int(request["curr-pos"]))
        elif request.get("type", None) == "defn":
            trg = buf.defn_trg_from_pos(pos, lang=None)
        else:
            trg = buf.trg_from_pos(pos, request.get("implicit", True))
        if not trg:
            driver.send(trg=None)
        else:
            data = trg.to_dict()
            data["path"] = buf.path
            driver.send(trg=data)

    def do_eval(self, request, driver):
        if not "trg" in request:
            raise RequestFailure(msg="No trigger given in request")
        buf = driver.get_buffer(request, path=request.trg["path"])
        try:
            log.debug("trigger data: %s", request.trg)
            data = dict(request.trg)
            del data["retriggerOnCompletion"]
            del data["path"]  # we tacked this on in do_trg_from_pos
            trg = codeintel2.common.Trigger(**data)
        except AttributeError:
            driver.fail(message="No trigger to evaluate")
            return
        ctlr = controller.OOPEvalController(driver, request, trg)
        log.debug("evaluating trigger: %s", trg.to_dict())
        buf.async_eval_at_trg(trg, ctlr)

    def do_calltip_arg_range(self, request, driver):
        buf = driver.get_buffer(request)
        start, end = buf.curr_calltip_arg_range(request.trg_pos,
                                                request.calltip,
                                                request.curr_pos)
        driver.send(start=start, end=end)

    def do_set_xml_catalogs(self, request, driver):
        catalogs = request["catalogs"]
        import koXMLDatasetInfo
        datasetHandler = koXMLDatasetInfo.getService()
        datasetHandler.setCatalogs(catalogs)
        driver.send(request=request)

    def do_get_xml_catalogs(self, request, driver):
        import koXMLDatasetInfo
        public = set()
        system = set()
        datasetHandler = koXMLDatasetInfo.getService()
        for catalog in datasetHandler.resolver.catalogMap.values():
            public.update(catalog.public.keys())
            system.update(catalog.system.keys())
        namespaces = datasetHandler.resolver.getWellKnownNamspaces().keys()
        driver.send(request=request,
                    public=sorted(public),
                    system=sorted(system),
                    namespaces=sorted(namespaces))

Driver._default_handler = CoreHandler()


class Request(dict):
    """
    A request from the consumer
    """
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        if not "req_id" in self:
            raise ValueError("No request id found")
        if not "command" in self:
            raise ValueError("No command found")
        self.id = self["req_id"]

    def __getattr__(self, name):
        if name in self:
            return self[name]
        raise AttributeError

    def __repr__(self):
        return "Request(%s)" % (json.dumps(self, separators=(',', ':')),)


class Environment(codeintel2.environment.Environment):
    def __init__(self, request={}, send_fn=None, name=None):
        codeintel2.environment.Environment.__init__(self)
        log_name = filter(None, [self.__class__.__name__, name])
        self.log = log.getChild(".".join(log_name))
        self._env = dict(request.get("env", {}))
        self._prefs = [dict(level) for level in request.get("prefs", [])]
        self._observers = {}  # name -> observer
        self._send = send_fn

    def has_envvar(self, name):
        return name in self._env

    def get_envvar(self, name, default=None):
        return self._env.get(name, default)

    def get_all_envvars(self):
        return self._env.copy()

    def set_envvar(self, name, value):
        """Set an environment variable.
        @param name {str} The environment variable name
        @param value {str} The environment variable value
        """
        self._env[name] = value

    def override_env(self, env):
        """Replace the current environment with the new set
        @param env {dict} The new environment variables
        """
        self._env = env.copy()

    def has_pref(self, name):
        return any(name in level for level in self._prefs)

    def get_pref(self, name, default=None):
        for level in self._prefs:
            if name in level:
                return level[name]
        return default

    def get_all_prefs(self, name, default=None):
        return [level.get(name, default) for level in self._prefs]

    def override_prefs(self, prefs):
        """Replace the current prefs with the new set
        @param prefs {list of dict} The new preferences
        """
        changed_prefs = set()
        # All existing prefs will be removed
        changed_prefs.update(*(level.keys() for level in self._prefs))
        # Do the replacement (making a copy)
        self._prefs = [level.copy() for level in prefs]
        # All the new prefs are added
        changed_prefs.update(*(level.keys() for level in self._prefs))
        for pref in changed_prefs:
            self._notify_pref_observers(pref)

    def update(self, request):
        try:
            env = request["env"] or {}
        except KeyError:
            pass
        else:
            self.override_env(env)
        try:
            prefs = request["prefs"] or []
        except KeyError:
            pass
        else:
            self.override_prefs(prefs)

    def add_pref_observer(self, name, callback):
        self.log.debug("Adding pref observer for %s", name)
        try:
            self._observers[name].add(callback)
        except KeyError:
            self._observers[name] = set([callback])
            if self._send:
                self._send(command="global-prefs-observe",
                           add=[name])
            else:
                self.log.warn("Warning: no way to trigger new prefs")

    def remove_pref_observer(self, name, callback):
        self._observers[name].discard(callback)
        if not self._observers[name]:
            del self._observers[name]
            if self._send:
                self._send(command="global-prefs-observe",
                           remove=[name])

    def remove_all_pref_observers(self):
        if self._send:
            self._send(command="global-prefs-observe",
                       remove=self._observers.keys())
        self._observers.clear()

    def _notify_pref_observers(self, name):
        """Call pref observers for the given pref
        @param name {str} The preference name
        """
        # This operates on a snapshot of observers
        for callback in tuple(self._observers.get(name, [])):
            try:
                callback(self, name)
            except:
                log.exception("error in pref observer for pref '%s' change",
                              name)

    def __nonzero__(self):
        """This is considered not-empty if it has anything in either the
        environment or preferences.
        """
        return bool(self._env or self._prefs)


def _get_memory_reporter():
    from .memory_reporter import MemoryCommandHandler
    return MemoryCommandHandler()
Driver.registerLazyCommandHandler(("memory-report",), _get_memory_reporter)
del _get_memory_reporter
