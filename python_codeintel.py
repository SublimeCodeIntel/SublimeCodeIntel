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
# The Original Code is SublimeCodeIntel code.
#
# The Initial Developer of the Original Code is German M. Bravo (Kronuz).
# Portions created by German M. Bravo (Kronuz) are Copyright (C) 2011
# German M. Bravo (Kronuz). All Rights Reserved.
#
# Contributor(s):
#   German M. Bravo (Kronuz)
#   ActiveState Software Inc
#
# Portions created by ActiveState Software Inc are Copyright (C) 2000-2007
# ActiveState Software Inc. All Rights Reserved.
#
"""
CodeIntel is a plugin intended to display "code intelligence" information.
The plugin is based in code from the Open Komodo Editor and has a MPL license.
Port by German M. Bravo (Kronuz). May 30, 2011

For Manual autocompletion:
    User Key Bindings are setup like this:
        { "keys": ["super+j"], "command": "code_intel_auto_complete" }

For "Jump to symbol declaration":
    User Key Bindings are set up like this
        { "keys": ["super+f3"], "command": "goto_python_definition" }
    ...and User Mouse Bindings as:
        { "button": "button1", "modifiers": ["alt"], "command": "goto_python_definition", "press_command": "drag_select" }

Configuration files (`~/.codeintel/config' or `project_root/.codeintel/config'). All configurations are optional. Example:
    {
        "PHP": {
            "php": '/usr/bin/php',
            "phpExtraPaths": [],
            "phpConfigFile": 'php.ini'
        },
        "JavaScript": {
            "javascriptExtraPaths": []
        },
        "Perl": {
            "perl": "/usr/bin/perl",
            "perlExtraPaths": []
        },
        "Ruby": {
            "ruby": "/usr/bin/ruby",
            "rubyExtraPaths": []
        },
        "Python": {
            "python": '/usr/bin/python',
            "pythonExtraPaths": []
        },
        "Python3": {
            "python": '/usr/bin/python3',
            "pythonExtraPaths": []
        }
    }
"""
import os, sys, stat, time, datetime, collections
import sublime_plugin, sublime
import threading
import logging
from cStringIO import StringIO

CODEINTEL_HOME_DIR = os.path.expanduser(os.path.join('~', '.codeintel'))
__file__ = os.path.normpath(os.path.abspath(__file__))
__path__ = os.path.dirname(__file__)
libs_path = os.path.join(__path__, 'libs')
if libs_path not in sys.path:
    sys.path.insert(0, libs_path)

from codeintel2.common import *
from codeintel2.manager import Manager
from codeintel2.citadel import CitadelBuffer
from codeintel2.environment import SimplePrefsEnvironment
from codeintel2.util import guess_lang_from_path


QUEUE = {}  # views waiting to be processed by linter


# Setup the complex logging (status bar gets stuff from there):
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
codeintel_hdlr = NullHandler()
codeintel_hdlr.setFormatter(logging.Formatter("%(name)s: %(levelname)s: %(message)s"))
stderr_hdlr = logging.StreamHandler(sys.stderr)
stderr_hdlr.setFormatter(logging.Formatter("%(name)s: %(levelname)s: %(message)s"))
codeintel_log = logging.getLogger("codeintel")
condeintel_log_file = ''
log = logging.getLogger("SublimeCodeIntel")
codeintel_log.handlers = [codeintel_hdlr]
log.handlers = [stderr_hdlr]
codeintel_log.setLevel(logging.INFO)  # INFO/ERROR
logging.getLogger("codeintel.db").setLevel(logging.INFO)  # INFO
for lang in ('css', 'django', 'html', 'html5', 'javascript', 'mason', 'nodejs',
             'perl', 'php', 'python', 'python3', 'rhtml', 'ruby', 'smarty',
             'tcl', 'templatetoolkit', 'xbl', 'xml', 'xslt', 'xul'):
    logging.getLogger("codeintel." + lang).setLevel(logging.DEBUG)  # DEBUG
log.setLevel(logging.ERROR)  # ERROR

cpln_fillup_chars = {
    'Ruby': "~`@#$%^&*(+}[]|\\;:,<>/ ",
    'Python': "~`!@#$%^&()-=+{}[]|\\;:'\",.<>?/ ",
    'PHP': "~`%^&*()-+{}[]|;'\",.< ",
    'Perl': "~`!@#$%^&*(=+}[]|\\;'\",.<>?/ ",
    'CSS': " '\";},/",
    'JavaScript': "~`!#%^&*()-=+{}[]|\\;:'\",.<>?/",
}
cpln_stop_chars = {
    'Ruby': "~`@#$%^&*(+}[]|\\;:,<>/ '\".",
    'Python': "~`!@#$%^&*()-=+{}[]|\\;:'\",.<>?/ ",
    'PHP': "~`@%^&*()=+{}]|\\;:'\",.<>?/ ",
    'Perl': "-~`!@#$%^&*()=+{}[]|\\;:'\",.<>?/ ",
    'CSS': " ('\";{},.>/",
    'JavaScript': "~`!@#%^&*()-=+{}[]|\\;:'\",.<>?/ ",
}

old_pos = None
despair = 0
despaired = False

completions = {}
sentinel = {}
status_msg = {}
status_lineno = {}
status_lock = threading.Lock()

HISTORY_SIZE = 64
jump_history_by_window = {}  # map of window id -> collections.deque([], HISTORY_SIZE)


def pos2bytes(content, pos):
    return len(content[:pos].encode('utf-8'))


def calltip(view, type, msg=None, timeout=None, delay=0, id='CodeIntel', logger=None):
    if timeout is None:
        timeout = {None: 3000, 'error': 3000, 'warning': 5000, 'info': 10000, 'event': 10000, 'tip': 15000}.get(type)
    if msg is None:
        msg, type = type, 'debug'
    msg = msg.strip()
    status_msg.setdefault(id, [None, None, 0])
    if msg == status_msg[id][1]:
        return
    status_lock.acquire()
    try:
        status_msg[id][2] += 1
        order = status_msg[id][2]
    finally:
        status_lock.release()

    def _calltip_erase():
        status_lock.acquire()
        try:
            if msg == status_msg.get(id, [None, None, 0])[1]:
                view.erase_status(id)
                status_msg[id][1] = None
                if id in status_lineno:
                    del status_lineno[id]
        finally:
            status_lock.release()

    def _calltip_set():
        lineno = view.line(view.sel()[0])
        status_lock.acquire()
        try:
            current_type, current_msg, current_order = status_msg.get(id, [None, None, 0])
            if msg != current_msg and order == current_order:
                if msg:
                    view.set_status(id, "%s: %s" % (type.capitalize(), msg))
                    (logger or log.info)(msg)
                else:
                    view.erase_status(id)
                status_msg[id][0] = [type, msg, order]
                if 'warning' not in id and msg:
                    status_lineno[id] = lineno
                elif id in status_lineno:
                    del status_lineno[id]
        finally:
            status_lock.release()
    try:
        if delay and delay is not None:
            sublime.set_timeout(_calltip_set, delay)
        else:
            _calltip_set()
    except:
        sublime.set_timeout(_calltip_set, delay)
    if msg:
        sublime.set_timeout(_calltip_erase, timeout)


def logger(view, type, msg=None, timeout=None, delay=0, id='CodeIntel'):
    if msg is None:
        msg, type = type, 'info'
    calltip(view, type, msg, timeout=timeout, delay=delay, id=id + '-' + type, logger=getattr(log, type, None))


def autocomplete(view, timeout, busy_timeout, preemptive=False, args=[], kwargs={}):
    def _autocomplete_callback(view, path):
        id = view.id()
        content = view.substr(sublime.Region(0, view.size()))
        sel = view.sel()[0]
        pos = sel.end()
        try:
            next = content[pos].strip()
        except IndexError:
            next = ''
        if pos and content and content[view.line(sel).begin():pos].strip() and not next.isalnum() and next != '_':
            #TODO: For the sentinel to work, we need to send a prefix to the completions... but no show_completions() currently available
            #pos = sentinel[path] if sentinel[path] is not None else view.sel()[0].end()
            lang, _ = os.path.splitext(os.path.basename(view.settings().get('syntax')))

            def _trigger(cplns, calltips):
                if cplns is not None or calltips is not None:
                    codeintel_log.info("Autocomplete called (%s) [%s]", lang, ','.join(c for c in ['cplns' if cplns else None, 'calltips' if calltips else None] if c))
                if cplns:
                    # Show autocompletions:
                    completions[id] = sorted(
                        [('%s  (%s)' % (name, type), name) for type, name in cplns],
                        cmp=lambda a, b: a[1] < b[1] if a[1].startswith('_') and b[1].startswith('_') else False if a[1].startswith('_') else True if b[1].startswith('_') else a[1] < b[1]
                    )
                    view.run_command('auto_complete', {'disable_auto_insert': True})
                elif calltips is not None:
                    # Trigger a tooltip
                    calltip(view, 'tip', calltips[0])
            sentinel[path] = None
            codeintel(view, path, content, lang, pos, ('cplns', 'calltips'), _trigger)
    # If it's a fill char, queue using lower values and preemptive behavior
    queue(view, _autocomplete_callback, timeout, busy_timeout, preemptive, args=args, kwargs=kwargs)


class PythonCodeIntel(sublime_plugin.EventListener):

    def on_close(self, view):
        path = view.file_name()
        status_lock.acquire()
        try:
            if path in sentinel:
                del sentinel[path]
            if path in status_msg:
                del status_msg[path]
            if path in status_lineno:
                del status_lineno[path]
        finally:
            status_lock.release()
        codeintel_cleanup(path)

    def on_modified(self, view):
        path = view.file_name()
        lang, _ = os.path.splitext(os.path.basename(view.settings().get('syntax')))
        try:
            lang = lang or guess_lang_from_path(path)
        except CodeIntelError:
            pass
        live = view.settings().get('codeintel_live', True)
        pos = view.sel()[0].end()
        text = view.substr(sublime.Region(pos - 1, pos))
        _sentinel = sentinel.get(path)
        is_fill_char = (text and text[-1] in cpln_fillup_chars.get(lang, ''))
        sentinel[path] = _sentinel if _sentinel is not None else pos if is_fill_char else None
        if not live and text and sentinel[path] is not None:
            live = True
        if live:
            if not hasattr(view, 'command_history') or view.command_history(0)[0] == 'insert':
                autocomplete(view, 0 if is_fill_char else 200, 50 if is_fill_char else 600, is_fill_char, args=[path])
            else:
                view.run_command('hide_auto_complete')
        else:
            def _scan_callback(view, path):
                content = view.substr(sublime.Region(0, view.size()))
                lang, _ = os.path.splitext(os.path.basename(view.settings().get('syntax')))
                codeintel_scan(view, path, content, lang)
            queue(view, _scan_callback, 3000, args=[path])

    def on_selection_modified(self, view):
        global despair, despaired, old_pos
        delay_queue(600)  # on movement, delay queue (to make movement responsive)

        rowcol = view.rowcol(view.sel()[0].end())
        if old_pos != rowcol:
            old_pos = rowcol
            despair = 1000
            despaired = True
            status_lock.acquire()
            try:
                slns = [id for id, sln in status_lineno.items() if sln != rowcol[0]]
            finally:
                status_lock.release()
            for id in slns:
                calltip(view, "", id=id)

    def on_query_completions(self, view, prefix, locations):
        id = view.id()
        if id in completions:
            _completions = completions[id]
            del completions[id]
            return _completions
        return []


class CodeIntelAutoComplete(sublime_plugin.TextCommand):
    def run(self, edit, block=False):
        view = self.view
        path = view.file_name()
        autocomplete(view, 0, 0, True, args=[path])


class GotoPythonDefinition(sublime_plugin.TextCommand):
    def run(self, edit, block=False):
        view = self.view
        path = view.file_name()
        content = view.substr(sublime.Region(0, view.size()))
        lang, _ = os.path.splitext(os.path.basename(view.settings().get('syntax')))
        pos = view.sel()[0].end()
        file_name = view.file_name()

        def _trigger(defns):
            if defns is not None:
                defn = defns[0]
                if defn.path and defn.line:
                    if defn.line != 1 or defn.path != file_name:
                        path = defn.path + ':' + str(defn.line)
                        msg = 'Jumping to: %s' % path
                        log.debug(msg)
                        codeintel_log.debug(msg)

                        window = sublime.active_window()
                        if window.id() not in jump_history_by_window:
                            jump_history_by_window[window.id()] = collections.deque([], HISTORY_SIZE)
                        jump_history = jump_history_by_window[window.id()]

                        # Save current position so we can return to it
                        row, col = view.rowcol(view.sel()[0].begin())
                        current_location = "%s:%d" % (file_name, row + 1)
                        jump_history.append(current_location)

                        window.open_file(path, sublime.ENCODED_POSITION)
                        window.open_file(path, sublime.ENCODED_POSITION)

        codeintel(view, path, content, lang, pos, ('defns',), _trigger)


class BackToPythonDefinition(sublime_plugin.TextCommand):
    def run(self, edit, block=False):

        window = sublime.active_window()
        if window.id() in jump_history_by_window:
            jump_history = jump_history_by_window[window.id()]

            if len(jump_history) > 0:
                previous_location = jump_history.pop()
                window = sublime.active_window()
                window.open_file(previous_location, sublime.ENCODED_POSITION)

_ci_envs_ = {}
_ci_mgr_ = None
_ci_db_base_dir_ = None
_ci_db_catalog_dirs_ = []
_ci_db_import_everything_langs = None
_ci_extra_module_dirs_ = None

_ci_next_savedb_ = 0
_ci_next_cullmem_ = 0


def codeintel_callbacks(force=False):
    global _ci_next_savedb_, _ci_next_cullmem_
    __lock_.acquire()
    try:
        views = QUEUE.values()
        QUEUE.clear()
    finally:
        __lock_.release()
    for view, callback, args, kwargs in views:
        def _callback():
            callback(view, *args, **kwargs)
        sublime.set_timeout(_callback, 0)
    # saving and culling cached parts of the database:
    if _ci_mgr_:
        now = time.time()
        if now >= _ci_next_savedb_ or force:
            if _ci_next_savedb_:
                log.debug('Saving database')
                _ci_mgr_.db.save()  # Save every 6 seconds
            _ci_next_savedb_ = now + 6
        if now >= _ci_next_cullmem_ or force:
            if _ci_next_cullmem_:
                log.debug('Culling memory')
                _ci_mgr_.db.cull_mem()  # Every 30 seconds
            _ci_next_cullmem_ = now + 30

################################################################################
# Queue dispatcher system:

queue_dispatcher = codeintel_callbacks
queue_thread_name = "codeintel callbacks"
MAX_DELAY = -1  # Does not apply


def queue_loop():
    '''An infinite loop running the linter in a background thread meant to
        update the view after user modifies it and then does no further
        modifications for some time as to not slow down the UI with linting.'''
    global __signaled_, __signaled_first_
    while __loop_:
        #print 'acquire...'
        __semaphore_.acquire()
        __signaled_first_ = 0
        __signaled_ = 0
        #print 'DISPATCHING!', len(QUEUE)
        queue_dispatcher()


def queue(view, callback, timeout, busy_timeout=None, preemptive=False, args=[], kwargs={}):
    global __signaled_, __signaled_first_
    now = time.time()
    __lock_.acquire()
    try:
        QUEUE[view.id()] = (view, callback, args, kwargs)
        if now < __signaled_ + timeout * 4:
            timeout = busy_timeout or timeout

        __signaled_ = now
        _delay_queue(timeout, preemptive)
        if not __signaled_first_:
            __signaled_first_ = __signaled_
            #print 'first',
        #print 'queued in', (__signaled_ - now)
    finally:
        __lock_.release()


def _delay_queue(timeout, preemptive):
    global __signaled_, __queued_
    now = time.time()
    if not preemptive and now <= __queued_ + 0.01:
        return  # never delay queues too fast (except preemptively)
    __queued_ = now
    _timeout = float(timeout) / 1000
    if __signaled_first_:
        if MAX_DELAY > 0 and now - __signaled_first_ + _timeout > MAX_DELAY:
            _timeout -= now - __signaled_first_
            if _timeout < 0:
                _timeout = 0
            timeout = int(round(_timeout * 1000, 0))
    new__signaled_ = now + _timeout - 0.01
    if __signaled_ >= now - 0.01 and (preemptive or new__signaled_ >= __signaled_ - 0.01):
        __signaled_ = new__signaled_
        #print 'delayed to', (preemptive, __signaled_ - now)

        def _signal():
            if time.time() < __signaled_:
                return
            __semaphore_.release()
        sublime.set_timeout(_signal, timeout)


def delay_queue(timeout):
    __lock_.acquire()
    try:
        _delay_queue(timeout, False)
    finally:
        __lock_.release()


# only start the thread once - otherwise the plugin will get laggy
# when saving it often.
__semaphore_ = threading.Semaphore(0)
__lock_ = threading.Lock()
__queued_ = 0
__signaled_ = 0
__signaled_first_ = 0

# First finalize old standing threads:
__loop_ = False
__pre_initialized_ = False


def queue_finalize(timeout=None):
    global __pre_initialized_
    for thread in threading.enumerate():
        if thread.isAlive() and thread.name == queue_thread_name:
            __pre_initialized_ = True
            thread.__semaphore_.release()
            thread.join(timeout)
queue_finalize()

# Initialize background thread:
__loop_ = True
__active_linter_thread = threading.Thread(target=queue_loop, name=queue_thread_name)
__active_linter_thread.__semaphore_ = __semaphore_
__active_linter_thread.start()

################################################################################

if not __pre_initialized_:
    # Start a timer
    def _signal_loop():
        __semaphore_.release()
        sublime.set_timeout(_signal_loop, 20000)
    _signal_loop()


def codeintel_cleanup(path):
    if path in _ci_envs_:
        del _ci_envs_[path]


def codeintel_scan(view, path, content, lang, callback=None, pos=None, forms=None):
    global despair
    for thread in threading.enumerate():
        if thread.isAlive() and thread.name == "scanning thread":
            logger(view, 'info', "Updating indexes... The first time this can take a while. Do not despair!", timeout=20000, delay=despair)
            despair = 0
            return
    try:
        lang = lang or guess_lang_from_path(path)
    except CodeIntelError:
        logger(view, 'warning', "skip `%s': couldn't determine language" % path)
        return
    if lang.lower() in [l.lower() for l in view.settings().get('codeintel_disabled_languages', [])]:
        return
    is_scratch = view.is_scratch()
    is_dirty = view.is_dirty()
    folders = getattr(view.window(), 'folders', lambda: [])()  # FIXME: it's like this for backward compatibility (<= 2060)

    def _codeintel_scan():
        global _ci_mgr_, despair, despaired
        env = None
        mtime = None
        catalogs = []
        now = time.time()
        try:
            env = _ci_envs_[path]
            if env._folders != folders:
                raise KeyError
            mgr = _ci_mgr_
            if now > env._time:
                mtime = max(tryGetMTime(env._config_file), tryGetMTime(env._config_default_file))
                if env._mtime < mtime:
                    raise KeyError
        except KeyError:
            if env is not None:
                config_default_file = env._config_default_file
                project_dir = env._project_dir
                project_base_dir = env._project_base_dir
                config_file = env._config_file
            else:
                config_default_file = os.path.join(CODEINTEL_HOME_DIR, 'config')
                if not (config_default_file and os.path.exists(config_default_file)):
                    config_default_file = None
                project_dir = None
                project_base_dir = None
                if path:
                    # Try to find a suitable project directory (or best guess):
                    for folder in ['.codeintel', '.git', '.hg', 'trunk']:
                        project_dir = find_folder(path, folder)
                        if project_dir and (folder != '.codeintel' or not os.path.exists(os.path.join(project_dir, 'db'))):
                            if folder.startswith('.'):
                                project_base_dir = os.path.abspath(os.path.join(project_dir, '..'))
                            else:
                                project_base_dir = project_dir
                            break
                if not (project_dir and os.path.exists(project_dir)):
                    project_dir = None
                config_file = project_dir and folder == '.codeintel' and os.path.join(project_dir, 'config')
                if not (config_file and os.path.exists(config_file)):
                    config_file = None
            if _ci_mgr_:
                mgr = _ci_mgr_
            else:
                for thread in threading.enumerate():
                    if thread.name == "CodeIntel Manager":
                        thread.finalize()  # this finalizes the index, citadel and the manager and waits them to end (join)
                mgr = Manager(
                    extra_module_dirs=_ci_extra_module_dirs_,
                    db_base_dir=_ci_db_base_dir_,
                    db_catalog_dirs=_ci_db_catalog_dirs_,
                    db_import_everything_langs=_ci_db_import_everything_langs,
                    db_event_reporter=lambda m: logger(view, 'event', m),
                )
                mgr.upgrade()
                mgr.initialize()

                # Connect the logging file to the handler
                condeintel_log_file = os.path.join(mgr.db.base_dir, 'codeintel.log')
                codeintel_log.handlers = [logging.StreamHandler(open(condeintel_log_file, 'w', 1))]
                msg = "Starting logging SublimeCodeIntel rev %s (%s) on %s" % (get_git_revision()[:12], os.stat(__file__)[stat.ST_MTIME], datetime.datetime.now().ctime())
                codeintel_log.info("%s\n%s" % (msg, "=" * len(msg)))

                _ci_mgr_ = mgr

            # Load configuration files:
            for catalog in mgr.db.get_catalogs_zone().avail_catalogs():
                if catalog['lang'] == lang:
                    catalogs.append(catalog['name'])
            config = {
                "codeintel_selected_catalogs": catalogs,
                "codeintel_max_recursive_dir_depth": 10,
                "codeintel_scan_files_in_project": True,
            }

            _config = {}
            try:
                tryReadDict(config_default_file, _config)
            except Exception, e:
                msg = "Malformed configuration file '%s': %s" % (config_default_file, e)
                log.error(msg)
                codeintel_log.error(msg)
            try:
                tryReadDict(config_file, _config)
            except Exception, e:
                msg = "Malformed configuration file '%s': %s" % (config_default_file, e)
                log.error(msg)
                codeintel_log.error(msg)
            config.update(_config.get(lang, {}))
            for conf in ['pythonExtraPaths', 'rubyExtraPaths', 'perlExtraPaths', 'javascriptExtraPaths', 'phpExtraPaths']:
                v = [p.strip() for p in config.get(conf, []) + folders if p.strip()]
                config[conf] = os.pathsep.join(set(p if p.startswith('/') else os.path.expanduser(p) if p.startswith('~') else os.path.abspath(os.path.join(project_base_dir, p)) if project_base_dir else p for p in v if p.strip()))

            env = SimplePrefsEnvironment(**config)
            env._mtime = mtime or max(tryGetMTime(config_file), tryGetMTime(config_default_file))
            env._folders = folders
            env._config_default_file = config_default_file
            env._project_dir = project_dir
            env._project_base_dir = project_base_dir
            env._config_file = config_file
            env.__class__.get_proj_base_dir = lambda self: project_base_dir
            _ci_envs_[path] = env
        env._time = now + 5  # don't check again in less than five seconds

        msgs = []
        if forms:
            calltip(view, 'tip', "")
            calltip(view, 'event', "")
            msg = "CodeIntel(%s) for %s@%s [%s]" % (', '.join(forms), path, pos, lang)
            msgs.append(('info', "\n%s\n%s" % (msg, "-" * len(msg))))

        if catalogs:
            msgs.append(('info', "New env with atalogs for '%s': %s" % (lang, ', '.join(catalogs) or None)))

        buf = mgr.buf_from_content(content.encode('utf-8'), lang, env, path or "<Unsaved>", 'utf-8')
        if isinstance(buf, CitadelBuffer):
            despair = 0
            despaired = False
            logger(view, 'info', "Updating indexes... The first time this can take a while.", timeout=20000, delay=1000)
            if not path or is_scratch:
                buf.scan()  # FIXME: Always scanning unsaved files (since many tabs can have unsaved files, or find other path as ID)
            else:
                if is_dirty:
                    mtime = 1
                else:
                    mtime = os.stat(path)[stat.ST_MTIME]
                try:
                    buf.scan(mtime=mtime, skip_scan_time_check=is_dirty)
                except KeyError:
                    msg = "Invalid language: %s. Available: %s" % (lang, ', '.join(mgr.citadel._cile_driver_from_lang))
                    log.debug(msg)
                    codeintel_log.debug(msg)
        if callback:
            callback(buf, msgs)
        else:
            logger(view, 'info', "")
    threading.Thread(target=_codeintel_scan, name="scanning thread").start()


def codeintel(view, path, content, lang, pos, forms, callback=None, timeout=7000):
    start = time.time()

    def _codeintel(buf, msgs):
        cplns = None
        calltips = None
        defns = None

        if not buf:
            logger(view, 'warning', "`%s' (%s) is not a language that uses CIX" % (path, buf.lang))
            return [None] * len(forms)

        try:
            trg = getattr(buf, 'trg_from_pos', lambda p: None)(pos2bytes(content, pos))
            defn_trg = getattr(buf, 'defn_trg_from_pos', lambda p: None)(pos2bytes(content, pos))
        except (CodeIntelError):
            codeintel_log.exception("Exception! %s:%s (%s)" % (path or '<Unsaved>', pos, lang))
            logger(view, 'info', "Error indexing! Please send the log file: '%s" % condeintel_log_file)
            trg = None
            defn_trg = None
        except:
            codeintel_log.exception("Exception! %s:%s (%s)" % (path or '<Unsaved>', pos, lang))
            logger(view, 'info', "Error indexing! Please send the log file: '%s" % condeintel_log_file)
            raise
        else:
            eval_log_stream = StringIO()
            _hdlrs = codeintel_log.handlers
            hdlr = logging.StreamHandler(eval_log_stream)
            hdlr.setFormatter(logging.Formatter("%(name)s: %(levelname)s: %(message)s"))
            codeintel_log.handlers = [hdlr]
            ctlr = LogEvalController(codeintel_log)
            try:
                if 'cplns' in forms and trg and trg.form == TRG_FORM_CPLN:
                    cplns = buf.cplns_from_trg(trg, ctlr=ctlr)
                if 'calltips' in forms and trg and trg.form == TRG_FORM_CALLTIP:
                    calltips = buf.calltips_from_trg(trg, ctlr=ctlr)
                if 'defns' in forms and defn_trg and defn_trg.form == TRG_FORM_DEFN:
                    defns = buf.defns_from_trg(defn_trg, ctlr=ctlr)
            finally:
                codeintel_log.handlers = _hdlrs
            logger(view, 'warning', "")
            logger(view, 'event', "")
            result = False
            merge = ''
            _msgs = []
            for msg in reversed(eval_log_stream.getvalue().strip().split('\n')):
                msg = msg.strip()
                if msg:
                    try:
                        name, levelname, msg = msg.split(':', 2)
                        name = name.strip()
                        levelname = levelname.strip().lower()
                        msg = msg.strip()
                    except:
                        merge = (msg + ' ' + merge) if merge else msg
                        continue
                    _msgs.append((levelname, name + ':' + ((msg + ' ' + merge) if merge else msg)))
                    merge = ''
                    if not result and msg.startswith('evaluating '):
                        calltip(view, 'warning', msg)
                        result = True
            if any((cplns, calltips, defns, result)):
                _msgs.reverse()
                for msg in msgs + _msgs:
                    getattr(codeintel_log, msg[0], codeintel_log.info)(msg[1])

        ret = []
        l = locals()
        for f in forms:
            ret.append(l.get(f))
        total = (time.time() - start)
        if not despaired or total * 1000 < timeout:
            def _callback():
                if view.line(view.sel()[0]) == view.line(pos):
                    callback(*ret)
            logger(view, 'info', "")
            sublime.set_timeout(_callback, 0)
        else:
            logger(view, 'info', "Just finished indexing! Please try again. Scan took %s" % total, timeout=3000)
    codeintel_scan(view, path, content, lang, _codeintel, pos, forms)


def find_folder(start_at, look_for):
    start_at = os.path.abspath(start_at)
    if not os.path.isdir(start_at):
        start_at = os.path.dirname(start_at)
    while True:
        if look_for in os.listdir(start_at):
            return os.path.join(start_at, look_for)
        continue_at = os.path.abspath(os.path.join(start_at, '..'))
        if continue_at == start_at:
            return None
        start_at = continue_at


def updateCodeIntelDict(master, partial):
    for key, value in partial.items():
        if isinstance(value, dict):
            master.setdefault(key, {}).update(value)
        elif isinstance(value, (list, tuple)):
            master.setdefault(key, []).extend(value)


def tryReadDict(filename, dictToUpdate):
    if filename:
        file = open(filename, 'r')
        try:
            updateCodeIntelDict(dictToUpdate, eval(file.read()))
        finally:
            file.close()


def tryGetMTime(filename):
    if filename:
        return os.stat(filename)[stat.ST_MTIME]
    return 0


def _get_git_revision(path):
    path = os.path.join(path, '.git')
    if os.path.exists(path):
        revision_file = os.path.join(path, 'refs', 'heads', 'master')
        if os.path.isfile(revision_file):
            fh = open(revision_file, 'r')
            try:
                return fh.read().strip()
            finally:
                fh.close()


def get_git_revision(path=None):
    """
    :returns: Revision number of this branch/checkout, if available. None if
        no revision number can be determined.
    """
    path = os.path.abspath(os.path.normpath(__path__ if path is None else path))
    while path and path != '/' and path != '\\':
        rev = _get_git_revision(path)
        if rev:
            return u'GIT-%s' % rev
        uppath = os.path.abspath(os.path.join(path, '..'))
        if uppath != path:
            path = uppath
        else:
            break
    return u'GIT-unknown'
