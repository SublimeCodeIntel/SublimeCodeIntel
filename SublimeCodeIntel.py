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
            "php": "/usr/bin/php",
            "phpConfigFile": "php.ini",
            "phpExtraPaths": []
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
            "python": "/usr/bin/python",
            "pythonExtraPaths": []
        },
        "Python3": {
            "python": "/usr/bin/python3",
            "pythonExtraPaths": []
        }
    }
"""
from __future__ import print_function

VERSION = "2.0.5"

import os
import re
import sys
import stat
import time
import datetime
import collections
import sublime
import sublime_plugin
import threading
import logging
from io import StringIO

CODEINTEL_HOME_DIR = os.path.expanduser(os.path.join('~', '.codeintel'))
__file__ = os.path.normpath(os.path.abspath(__file__))
__path__ = os.path.dirname(__file__)

libs_path = os.path.join(__path__, 'libs')
if libs_path not in sys.path:
    sys.path.insert(0, libs_path)

arch_path = os.path.join(__path__, 'arch')
if arch_path not in sys.path:
    sys.path.insert(0, arch_path)

from codeintel2.common import CodeIntelError, EvalTimeout, LogEvalController, TRG_FORM_CPLN, TRG_FORM_CALLTIP, TRG_FORM_DEFN
from codeintel2.manager import Manager
from codeintel2.citadel import CitadelBuffer
from codeintel2.environment import SimplePrefsEnvironment
from codeintel2.util import guess_lang_from_path


QUEUE = {}  # views waiting to be processed by codeintel


# Setup the complex logging (status bar gets stuff from there):
class NullHandler(logging.Handler):
    def emit(self, record):
        pass

codeintel_hdlr = NullHandler()
codeintel_hdlr.setFormatter(logging.Formatter("%(name)s: %(levelname)s: %(message)s"))
stderr_hdlr = logging.StreamHandler(sys.stderr)
stderr_hdlr.setFormatter(logging.Formatter("%(name)s: %(levelname)s: %(message)s"))
codeintel_log = logging.getLogger("codeintel")
condeintel_log_filename = ''
condeintel_log_file = None
log = logging.getLogger("SublimeCodeIntel")
codeintel_log.handlers = [codeintel_hdlr]
log.handlers = [stderr_hdlr]
codeintel_log.setLevel(logging.INFO)  # INFO
for logger in ('codeintel.db', 'codeintel.pythoncile'):
    logging.getLogger(logger).setLevel(logging.WARNING)  # WARNING
for logger in ('css', 'django', 'html', 'html5', 'javascript', 'mason', 'nodejs',
             'perl', 'php', 'python', 'python3', 'rhtml', 'ruby', 'smarty',
             'tcl', 'templatetoolkit', 'xbl', 'xml', 'xslt', 'xul'):
    logging.getLogger("codeintel." + logger).setLevel(logging.INFO)  # WARNING
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
languages = {}

status_msg = {}
status_lineno = {}
status_lock = threading.Lock()

HISTORY_SIZE = 64
jump_history_by_window = {}  # map of window id -> collections.deque([], HISTORY_SIZE)


def pos2bytes(content, pos):
    return len(content[:pos].encode('utf-8'))


def calltip(view, ltype, msg=None, timeout=None, delay=0, lid='CodeIntel', logger=None):
    if timeout is None:
        timeout = {'error': 3000, 'warning': 5000, 'info': 10000,
                    'event': 10000, 'tip': 15000}.get(ltype, 3000)

    if msg is None:
        msg, ltype = ltype, 'debug'
    msg = msg.strip()

    status_lock.acquire()
    try:
        status_msg.setdefault(lid, [None, None, 0])
        if msg == status_msg[lid][1]:
            return
        status_msg[lid][2] += 1
        order = status_msg[lid][2]
    finally:
        status_lock.release()

    def _calltip_set():
        view_sel = view.sel()
        lineno = view.rowcol(view_sel[0].end())[0] if view_sel else 0
        status_lock.acquire()
        try:
            current_type, current_msg, current_order = status_msg.get(lid, [None, None, 0])
            if msg != current_msg and order == current_order:
                if msg:
                    print("+", "%s: %s" % (ltype.capitalize(), msg), file=condeintel_log_file)
                    (logger or log.info)(msg)
                    if ltype != 'debug':
                        view.set_status(lid, "%s: %s" % (ltype.capitalize(), msg))
                        status_msg[lid] = [ltype, msg, order]
                    if 'warning' not in lid:
                        status_lineno[lid] = lineno
                else:
                    view.erase_status(lid)
                    status_msg[lid][1] = None
                    if lid in status_lineno:
                        del status_lineno[lid]
        finally:
            status_lock.release()

    def _calltip_erase():
        status_lock.acquire()
        try:
            if msg == status_msg.get(lid, [None, None, 0])[1]:
                view.erase_status(lid)
                status_msg[lid][1] = None
                if lid in status_lineno:
                    del status_lineno[lid]
        finally:
            status_lock.release()

    sublime.set_timeout(_calltip_set, delay or 0)

    if msg:
        sublime.set_timeout(_calltip_erase, timeout)


def logger(view, ltype, msg=None, timeout=None, delay=0, lid='CodeIntel'):
    if msg is None:
        msg, ltype = ltype, 'info'
    calltip(view, ltype, msg, timeout=timeout, delay=delay, lid=lid + '-' + ltype, logger=getattr(log, ltype, None))


def guess_lang(view=None, path=None):
    if not view or not codeintel_enabled(view):
        return None

    syntax = None
    if view:
        syntax = os.path.splitext(os.path.basename(view.settings().get('syntax')))[0]

    vid = view.id()
    _k_ = '%s::%s' % (syntax, path)
    try:
        return languages[vid][_k_]
    except KeyError:
        pass
    languages.setdefault(vid, {})

    lang = None
    _codeintel_syntax_map = dict((k.lower(), v) for k, v in view.settings().get('codeintel_syntax_map', {}).items())
    _lang = lang = syntax and _codeintel_syntax_map.get(syntax.lower(), syntax)

    folders = getattr(view.window(), 'folders', lambda: [])()  # FIXME: it's like this for backward compatibility (<= 2060)
    folders_id = str(hash(frozenset(folders)))
    mgr = codeintel_manager(folders_id)

    if not mgr.is_citadel_lang(lang) and not mgr.is_cpln_lang(lang):
        lang = None
        if mgr.is_citadel_lang(syntax) or mgr.is_cpln_lang(syntax):
            _lang = lang = syntax
        else:
            if view and not path:
                path = view.file_name()
            if path:
                try:
                    _lang = lang = guess_lang_from_path(path)
                except CodeIntelError:
                    languages[vid][_k_] = None
                    return

    _codeintel_enabled_languages = [l.lower() for l in view.settings().get('codeintel_enabled_languages', [])]
    if lang and lang.lower() not in _codeintel_enabled_languages:
        languages[vid][_k_] = None
        return None

    if not lang and _lang and _lang in ('Console', 'Plain text'):
        if mgr:
            logger(view, 'debug', "Invalid language: %s. Available: %s" % (_lang, ', '.join(set(mgr.get_citadel_langs() + mgr.get_cpln_langs()))))
        else:
            logger(view, 'debug', "Invalid language: %s" % _lang)

    languages[vid][_k_] = lang
    return lang


def autocomplete(view, timeout, busy_timeout, forms, preemptive=False, args=[], kwargs={}):
    def _autocomplete_callback(view, path, original_pos, lang):
        view_sel = view.sel()
        if not view_sel:
            return

        sel = view_sel[0]
        pos = sel.end()
        if not pos or pos != original_pos:
            return

        lpos = view.line(sel).begin()
        text = view.substr(sublime.Region(lpos, pos + 1))
        next = text[-1] if len(text) == pos + 1 - lpos else None

        if not next or next != '_' and not next.isalnum():
            vid = view.id()
            content = view.substr(sublime.Region(0, view.size()))

            def _trigger(calltips, cplns=None):
                view_settings = view.settings()
                if cplns is not None or calltips is not None:
                    codeintel_log.info("Autocomplete called (%s) [%s]", lang, ','.join(c for c in ['cplns' if cplns else None, 'calltips' if calltips else None] if c))

                if cplns is not None:
                    function = None if 'import ' in text else 'function'
                    _completions = sorted(
                        [('%s  (%s)' % (n, t), n + ('($0)' if t == function else '')) for t, n in cplns],
                        key=lambda o: o[1]
                    )
                    if _completions:
                        # Show autocompletions:
                        completions[vid] = _completions
                        view.run_command('auto_complete', {
                            'disable_auto_insert': True,
                            'api_completions_only': True,
                            'next_completion_if_showing': False,
                            'auto_complete_commit_on_tab': True,
                        })

                if calltips is None:
                    return
                tip_info = calltips[0].split('\n')
                tooltip = ' '.join(tip_info[1:])

                # Insert function call snippets:
                if view_settings.get('codeintel_snippets', True):
                    # Insert parameters as snippet:
                    if content[sel.begin() - 1] == '(' and content[sel.begin()] == ')':
                        m = re.search(r'([^\s]+)\(([^\[\(\)]*)', tip_info[0])
                        if m:
                            params = [p.strip() for p in m.group(2).split(',')]
                            if params:
                                snippet = []
                                for i, p in enumerate(params):
                                    if p:
                                        var, _, _ = p.partition('=')
                                        if ' ' in var:
                                            var = var.split(' ')[1]
                                        if var[0] == '$':
                                            var = var[1:]
                                        snippet.append('${%s:%s}' % (i + 1, var))
                                contents = ', '.join(snippet)
                                # func = m.group(1)
                                # scope = view.scope_name(pos)
                                # view.run_command('new_snippet', {'contents': contents, 'tab_trigger': func, 'scope': scope})  # FIXME: Doesn't add the new snippet... is it possible to do so?
                                def _insert_snippet():
                                    # Check to see we are still at a position where the snippet is wanted:
                                    view_sel = view.sel()
                                    if not view_sel:
                                        return
                                    sel = view_sel[0]
                                    pos = sel.end()
                                    if not pos or pos != original_pos:
                                        return
                                    view.run_command('insert_snippet', {'contents': contents})
                                sublime.set_timeout(_insert_snippet, 500)  # Delay snippet insertion a bit... it's annoying some times
                            tooltip += ' - ' + tip_info[0]  # Add function to the end
                        else:
                            tooltip = tip_info[0] + ' ' + tooltip  # No function match, just add the first line
                # Trigger a tooltip
                calltip(view, 'tip', tooltip)
            codeintel(view, path, content, lang, pos, forms, _trigger)
    # If it's a fill char, queue using lower values and preemptive behavior
    queue(view, _autocomplete_callback, timeout, busy_timeout, preemptive, args=args, kwargs=kwargs)


_ci_envs_ = {}
_ci_next_scan_ = {}
_ci_mgr_ = {}

_ci_next_savedb_ = 0
_ci_next_cullmem_ = 0

################################################################################
# Queue dispatcher system:

MAX_DELAY = -1  # Does not apply
queue_thread_name = "codeintel callbacks"


def queue_dispatcher(force=False):
    """
    Default implementation of queue dispatcher (just clears the queue)
    """
    __lock_.acquire()
    try:
        QUEUE.clear()
    finally:
        __lock_.release()


def queue_loop():
    """An infinite loop running the codeintel in a background thread meant to
        update the view after user modifies it and then does no further
        modifications for some time as to not slow down the UI with autocompletes."""
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
__active_codeintel_thread = threading.Thread(target=queue_loop, name=queue_thread_name)
__active_codeintel_thread.__semaphore_ = __semaphore_
__active_codeintel_thread.start()

################################################################################

if not __pre_initialized_:
    # Start a timer
    def _signal_loop():
        __semaphore_.release()
        sublime.set_timeout(_signal_loop, 20000)
    _signal_loop()


def codeintel_callbacks(force=False):
    global _ci_next_savedb_, _ci_next_cullmem_
    __lock_.acquire()
    try:
        views = list(QUEUE.values())
        QUEUE.clear()
    finally:
        __lock_.release()
    for view, callback, args, kwargs in views:
        def _callback():
            callback(view, *args, **kwargs)
        sublime.set_timeout(_callback, 0)
    # saving and culling cached parts of the database:
    for folders_id in list(_ci_mgr_.keys()):
        mgr = codeintel_manager(folders_id)
        now = time.time()
        if now >= _ci_next_savedb_ or force:
            if _ci_next_savedb_:
                log.debug('Saving database')
                mgr.db.save()  # Save every 6 seconds
            _ci_next_savedb_ = now + 6
        if now >= _ci_next_cullmem_ or force:
            if _ci_next_cullmem_:
                log.debug('Culling memory')
                mgr.db.cull_mem()  # Every 30 seconds
            _ci_next_cullmem_ = now + 30
queue_dispatcher = codeintel_callbacks


def codeintel_cleanup(id):
    if id in _ci_envs_:
        del _ci_envs_[id]
    if id in _ci_next_scan_:
        del _ci_next_scan_[id]


def codeintel_manager(folders_id):
    folders_id = None
    global _ci_mgr_, condeintel_log_filename, condeintel_log_file
    mgr = _ci_mgr_.get(folders_id)
    if mgr is None:
        for thread in threading.enumerate():
            if thread.name == "CodeIntel Manager":
                thread.finalize()  # this finalizes the index, citadel and the manager and waits them to end (join)
        mgr = Manager(
            extra_module_dirs=None,
            db_base_dir=None,  # os.path.expanduser(os.path.join('~', '.codeintel', 'databases', folders_id)),
            db_catalog_dirs=[],
            db_import_everything_langs=None,
        )
        mgr.upgrade()
        mgr.initialize()

        # Connect the logging file to the handler
        condeintel_log_filename = os.path.join(mgr.db.base_dir, 'codeintel.log')
        condeintel_log_file = open(condeintel_log_filename, 'w', 1)
        codeintel_log.handlers = [logging.StreamHandler(condeintel_log_file)]
        msg = "Starting logging SublimeCodeIntel v%s rev %s (%s) on %s" % (VERSION, get_revision()[:12], os.stat(__file__)[stat.ST_MTIME], datetime.datetime.now().ctime())
        print("%s\n%s" % (msg, "=" * len(msg)), file=condeintel_log_file)

        _ci_mgr_[folders_id] = mgr
    return mgr


def codeintel_scan(view, path, content, lang, callback=None, pos=None, forms=None):
    global despair
    for thread in threading.enumerate():
        if thread.isAlive() and thread.name == "scanning thread":
            logger(view, 'info', "Updating indexes... The first time this can take a while. Do not despair!", timeout=20000, delay=despair)
            despair = 0
            return
    logger(view, 'info', "processing `%s': please wait..." % lang)
    is_scratch = view.is_scratch()
    is_dirty = view.is_dirty()
    vid = view.id()
    folders = getattr(view.window(), 'folders', lambda: [])()  # FIXME: it's like this for backward compatibility (<= 2060)
    folders_id = str(hash(frozenset(folders)))
    view_settings = view.settings()
    codeintel_config = view_settings.get('codeintel_config', {})
    _codeintel_max_recursive_dir_depth = view_settings.get('codeintel_max_recursive_dir_depth', 10)
    _codeintel_scan_files_in_project = view_settings.get('codeintel_scan_files_in_project', True)
    _codeintel_selected_catalogs = view_settings.get('codeintel_selected_catalogs', [])

    def _codeintel_scan():
        global despair, despaired
        env = None
        mtime = None
        catalogs = []
        now = time.time()

        mgr = codeintel_manager(folders_id)
        mgr.db.event_reporter = lambda m: logger(view, 'event', m)

        try:
            env = _ci_envs_[vid]
            if env._folders != folders:
                raise KeyError
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
                for folder_path in folders + [path]:
                    if folder_path:
                        # Try to find a suitable project directory (or best guess):
                        for folder in ['.codeintel', '.git', '.hg', '.svn', 'trunk']:
                            project_dir = find_back(folder_path, folder)
                            if project_dir:
                                if folder == '.codeintel':
                                    if project_dir == CODEINTEL_HOME_DIR or os.path.exists(os.path.join(project_dir, 'databases')):
                                        continue
                                if folder.startswith('.'):
                                    project_base_dir = os.path.abspath(os.path.join(project_dir, '..'))
                                else:
                                    project_base_dir = project_dir
                                break
                        if project_base_dir:
                            break
                if not (project_dir and os.path.exists(project_dir)):
                    project_dir = None
                config_file = project_dir and folder == '.codeintel' and os.path.join(project_dir, 'config')
                if not (config_file and os.path.exists(config_file)):
                    config_file = None

            valid = True
            if not mgr.is_citadel_lang(lang) and not mgr.is_cpln_lang(lang):
                if lang in ('Console', 'Plain text'):
                    msg = "Invalid language: %s. Available: %s" % (lang, ', '.join(set(mgr.get_citadel_langs() + mgr.get_cpln_langs())))
                    log.debug(msg)
                    codeintel_log.warning(msg)
                valid = False

            codeintel_config_lang = codeintel_config.get(lang, {})
            codeintel_max_recursive_dir_depth = codeintel_config_lang.get('codeintel_max_recursive_dir_depth', _codeintel_max_recursive_dir_depth)
            codeintel_scan_files_in_project = codeintel_config_lang.get('codeintel_scan_files_in_project', _codeintel_scan_files_in_project)
            codeintel_selected_catalogs = codeintel_config_lang.get('codeintel_selected_catalogs', _codeintel_selected_catalogs)

            avail_catalogs = mgr.db.get_catalogs_zone().avail_catalogs()

            # Load configuration files:
            all_catalogs = []
            for catalog in avail_catalogs:
                all_catalogs.append("%s (for %s: %s)" % (catalog['name'], catalog['lang'], catalog['description']))
                if catalog['lang'] == lang:
                    if catalog['name'] in codeintel_selected_catalogs:
                        catalogs.append(catalog['name'])
            msg = "Avaliable catalogs: %s" % ', '.join(all_catalogs) or None
            log.debug(msg)
            codeintel_log.debug(msg)

            config = {
                'codeintel_max_recursive_dir_depth': codeintel_max_recursive_dir_depth,
                'codeintel_scan_files_in_project': codeintel_scan_files_in_project,
                'codeintel_selected_catalogs': catalogs,
            }
            config.update(codeintel_config_lang)

            _config = {}
            try:
                tryReadDict(config_default_file, _config)
            except Exception as e:
                msg = "Malformed configuration file '%s': %s" % (config_default_file, e)
                log.error(msg)
                codeintel_log.error(msg)
            try:
                tryReadDict(config_file, _config)
            except Exception as e:
                msg = "Malformed configuration file '%s': %s" % (config_default_file, e)
                log.error(msg)
                codeintel_log.error(msg)
            config.update(_config.get(lang, {}))

            for conf in ['pythonExtraPaths', 'rubyExtraPaths', 'perlExtraPaths', 'javascriptExtraPaths', 'phpExtraPaths']:
                v = [p.strip() for p in config.get(conf, []) + folders if p.strip()]
                config[conf] = os.pathsep.join(set(p if p.startswith('/') else os.path.expanduser(p) if p.startswith('~') else os.path.abspath(os.path.join(project_base_dir, p)) if project_base_dir else p for p in v if p.strip()))
            for conf, p in config.items():
                if isinstance(p, str) and p.startswith('~'):
                    config[conf] = os.path.expanduser(p)

            # Setup environment variables
            env = config.get('env', {})
            _environ = dict(os.environ)
            for k, v in env.items():
                _old = None
                while '$' in v and v != _old:
                    _old = v
                    v = os.path.expandvars(v)
                _environ[k] = v
            config['env'] = _environ

            env = SimplePrefsEnvironment(**config)
            env._valid = valid
            env._mtime = mtime or max(tryGetMTime(config_file), tryGetMTime(config_default_file))
            env._folders = folders
            env._config_default_file = config_default_file
            env._project_dir = project_dir
            env._project_base_dir = project_base_dir
            env._config_file = config_file
            env.__class__.get_proj_base_dir = lambda self: project_base_dir
            _ci_envs_[vid] = env
        env._time = now + 5  # don't check again in less than five seconds

        msgs = []
        if env._valid:
            if forms:
                calltip(view, 'tip', "")
                calltip(view, 'event', "")
                msg = "CodeIntel(%s) for %s@%s [%s]" % (', '.join(forms), path, pos, lang)
                msgs.append(('info', "\n%s\n%s" % (msg, "-" * len(msg))))

            if catalogs:
                msg = "New env with catalogs for '%s': %s" % (lang, ', '.join(catalogs) or None)
                log.debug(msg)
                codeintel_log.warning(msg)
                msgs.append(('info', msg))

            buf = mgr.buf_from_content(content, lang, env, path or "<Unsaved>", 'utf-8')

            now = datetime.datetime.now()
            if not _ci_next_scan_.get(vid) or now > _ci_next_scan_[vid]:
                _ci_next_scan_[vid] = now + datetime.timedelta(seconds=10)
                if isinstance(buf, CitadelBuffer):
                    despair = 0
                    despaired = False
                    msg = "Updating indexes for '%s'... The first time this can take a while." % lang
                    print(msg, file=condeintel_log_file)
                    logger(view, 'info', msg, timeout=20000, delay=1000)
                    if not path or is_scratch:
                        buf.scan()  # FIXME: Always scanning unsaved files (since many tabs can have unsaved files, or find other path as ID)
                    else:
                        if is_dirty:
                            mtime = 1
                        else:
                            mtime = os.stat(path)[stat.ST_MTIME]
                        buf.scan(mtime=mtime, skip_scan_time_check=is_dirty)
        else:
            buf = None
        if callback:
            msg = "Doing CodeIntel for '%s' (hold on)..." % lang
            print(msg, file=condeintel_log_file)
            logger(view, 'info', msg, timeout=20000, delay=1000)
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
            logger(view, 'warning', "`%s' (%s) is not a language that uses CIX" % (path, lang))
            return [None] * len(forms)

        try:
            trg = getattr(buf, 'preceding_trg_from_pos', lambda p: None)(pos2bytes(content, pos), pos2bytes(content, pos))
            defn_trg = getattr(buf, 'defn_trg_from_pos', lambda p: None)(pos2bytes(content, pos))
        except (CodeIntelError):
            codeintel_log.exception("Exception! %s:%s (%s)" % (path or '<Unsaved>', pos, lang))
            logger(view, 'info', "Error indexing! Please send the log file: '%s" % condeintel_log_filename)
            trg = None
            defn_trg = None
        except:
            codeintel_log.exception("Exception! %s:%s (%s)" % (path or '<Unsaved>', pos, lang))
            logger(view, 'info', "Error indexing! Please send the log file: '%s" % condeintel_log_filename)
            raise
        else:
            eval_log_stream = StringIO()
            _hdlrs = codeintel_log.handlers
            hdlr = logging.StreamHandler(eval_log_stream)
            hdlr.setFormatter(logging.Formatter("%(name)s: %(levelname)s: %(message)s"))
            codeintel_log.handlers = list(_hdlrs) + [hdlr]
            ctlr = LogEvalController(codeintel_log)
            try:
                if 'cplns' in forms and trg and trg.form == TRG_FORM_CPLN:
                    cplns = buf.cplns_from_trg(trg, ctlr=ctlr, timeout=20)
                if 'calltips' in forms and trg and trg.form == TRG_FORM_CALLTIP:
                    calltips = buf.calltips_from_trg(trg, ctlr=ctlr, timeout=20)
                if 'defns' in forms and defn_trg and defn_trg.form == TRG_FORM_DEFN:
                    defns = buf.defns_from_trg(defn_trg, ctlr=ctlr, timeout=20)
            except EvalTimeout:
                logger(view, 'info', "Timeout while resolving completions!")
            finally:
                codeintel_log.handlers = _hdlrs
            logger(view, 'warning', "")
            logger(view, 'event', "")
            result = False
            merge = ''
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
                    merge = ''
                    if not result and msg.startswith('evaluating '):
                        calltip(view, 'warning', msg)
                        result = True

        ret = []
        for f in forms:
            if f == 'cplns':
                ret.append(cplns)
            elif f == 'calltips':
                ret.append(calltips)
            elif f == 'defns':
                ret.append(defns)

        total = (time.time() - start) * 1000
        if total > 1000:
            timestr = "~%ss" % int(round(total / 1000))
        else:
            timestr = "%sms" % int(round(total))
        if not despaired or total < timeout:
            msg = "Done '%s' CodeIntel! Full CodeIntel took %s" % (lang, timestr)
            print(msg, file=condeintel_log_file)

            def _callback():
                view_sel = view.sel()
                if view_sel and view.line(view_sel[0]) == view.line(pos):
                    callback(*ret)
            logger(view, 'info', "")
            sublime.set_timeout(_callback, 0)
        else:
            msg = "Just finished indexing '%s'! Please try again. Full CodeIntel took %s" % (lang, timestr)
            print(msg, file=condeintel_log_file)
            logger(view, 'info', msg, timeout=3000)
    codeintel_scan(view, path, content, lang, _codeintel, pos, forms)


def find_back(start_at, look_for):
    root = os.path.realpath('/')
    start_at = os.path.abspath(start_at)
    if not os.path.isdir(start_at):
        start_at = os.path.dirname(start_at)
    if start_at == root:
        return None
    while True:
        if look_for in os.listdir(start_at):
            return os.path.join(start_at, look_for)
        continue_at = os.path.abspath(os.path.join(start_at, '..'))
        if continue_at == start_at or continue_at == root:
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


def get_revision(path=None):
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


ALL_SETTINGS = [
    'codeintel',
    'codeintel_snippets',
    'codeintel_enabled_languages',
    'codeintel_live',
    'codeintel_live_enabled_languages',
    'codeintel_max_recursive_dir_depth',
    'codeintel_scan_files_in_project',
    'codeintel_selected_catalogs',
    'codeintel_syntax_map',
    'codeintel_scan_exclude_dir',
    'codeintel_config',
    'sublime_auto_complete',
]


def settings_changed():
    for window in sublime.windows():
        for view in window.views():
            reload_settings(view)


def reload_settings(view):
    '''Restores user settings.'''
    settings_name = 'SublimeCodeIntel'
    settings = sublime.load_settings(settings_name + '.sublime-settings')
    settings.clear_on_change(settings_name)
    settings.add_on_change(settings_name, settings_changed)

    view_settings = view.settings()

    for setting_name in ALL_SETTINGS:
        if settings.get(setting_name) is not None:
            setting = settings.get(setting_name)
            view_settings.set(setting_name, setting)

    if view_settings.get('codeintel') is None:
        view_settings.set('codeintel', True)

    path = view.file_name()
    lang = guess_lang(view, path)
    if lang and lang.lower() in [l.lower() for l in view.settings().get('codeintel_live_enabled_languages', [])]:
        if not view_settings.get('sublime_auto_complete'):
            view_settings.set('auto_complete', False)

    return view_settings


def codeintel_enabled(view, default=None):
    if view.settings().get('codeintel') is None:
        reload_settings(view)
    return view.settings().get('codeintel', default)


class PythonCodeIntel(sublime_plugin.EventListener):
    def on_close(self, view):
        vid = view.id()
        if vid in completions:
            del completions[vid]
        if vid in languages:
            del languages[vid]
        codeintel_cleanup(view.file_name())

    def on_modified(self, view):
        if not view.settings().get('codeintel_live', True):
            return

        path = view.file_name()
        lang = guess_lang(view, path)
        if not lang or lang.lower() not in [l.lower() for l in view.settings().get('codeintel_live_enabled_languages', [])]:
            return

        view_sel = view.sel()
        if not view_sel:
            return

        sel = view_sel[0]
        pos = sel.end()
        text = view.substr(sublime.Region(pos - 1, pos))
        is_fill_char = (text and text[-1] in cpln_fillup_chars.get(lang, ''))

        # print('on_modified', view.command_history(1), view.command_history(0), view.command_history(-1))
        if (not hasattr(view, 'command_history') or view.command_history(1)[1] is None and (
                view.command_history(0)[0] == 'insert' or
                view.command_history(-1)[0] in ('insert', 'paste') and (
                    view.command_history(0)[0] == 'commit_completion' or
                    view.command_history(0)[0] == 'insert_snippet' and view.command_history(0)[1]['contents'] == '($0)'
                )
        )):
            if view.command_history(0)[0] == 'commit_completion':
                forms = ('calltips',)
            else:
                forms = ('calltips', 'cplns')
            autocomplete(view, 0 if is_fill_char else 200, 50 if is_fill_char else 600, forms, is_fill_char, args=[path, pos, lang])
        else:
            view.run_command('hide_auto_complete')

    def on_selection_modified(self, view):
        global despair, despaired, old_pos
        delay_queue(600)  # on movement, delay queue (to make movement responsive)
        view_sel = view.sel()
        if not view_sel:
            return
        rowcol = view.rowcol(view_sel[0].end())
        if old_pos != rowcol:
            vid = view.id()
            old_pos = rowcol
            despair = 1000
            despaired = True
            status_lock.acquire()
            try:
                slns = [sid for sid, sln in status_lineno.items() if sln != rowcol[0]]
            finally:
                status_lock.release()
            for vid in slns:
                calltip(view, "", lid=vid)

    def on_query_completions(self, view, prefix, locations):
        vid = view.id()
        if vid in completions:
            _completions = completions[vid]
            del completions[vid]
            return _completions
        return []


class CodeIntelAutoComplete(sublime_plugin.TextCommand):
    def run(self, edit, block=False):
        view = self.view
        view_sel = view.sel()
        if not view_sel:
            return
        sel = view_sel[0]
        pos = sel.end()
        path = view.file_name()
        lang = guess_lang(view, path)
        if lang:
            autocomplete(view, 0, 0, ('calltips', 'cplns'), True, args=[path, pos, lang])


class GotoPythonDefinition(sublime_plugin.TextCommand):
    def run(self, edit, block=False):
        view = self.view
        path = view.file_name()
        lang = guess_lang(view, path)
        if lang:
            view_sel = view.sel()
            if not view_sel:
                return
            sel = view_sel[0]
            pos = sel.end()
            content = view.substr(sublime.Region(0, view.size()))
            file_name = view.file_name()

            def _trigger(defns):
                if defns is not None:
                    defn = defns[0]
                    if defn.name and defn.doc:
                        msg = "%s: %s" % (defn.name, defn.doc)
                        logger(view, 'info', msg, timeout=3000)

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
                            row, col = view.rowcol(view_sel[0].begin())
                            current_location = "%s:%d" % (file_name, row + 1)
                            jump_history.append(current_location)

                            window.open_file(path, sublime.ENCODED_POSITION)
                            window.open_file(path, sublime.ENCODED_POSITION)
                    elif defn.name:
                        msg = 'Cannot find jumping point to: %s' % defn.name
                        log.debug(msg)
                        codeintel_log.debug(msg)

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


class CodeintelCommand(sublime_plugin.TextCommand):
    """command to interact with codeintel"""

    def __init__(self, view):
        self.view = view
        self.help_called = False

    def run_(self, action):
        """method called by default via view.run_command;
           used to dispatch to appropriate method"""
        if not action:
            return

        try:
            lc_action = action.lower()
        except AttributeError:
            return
        if lc_action == 'reset':
            self.reset()
        elif lc_action == 'enable':
            self.enable(True)
        elif lc_action == 'disable':
            self.enable(False)
        elif lc_action == 'on':
            self.on_off(True)
        elif lc_action == 'off':
            self.on_off(False)
        elif lc_action == 'lang-on':
            self.on_off(True, guess_lang(self.view, self.view.file_name()))
        elif lc_action == 'lang-off':
            self.on_off(False, guess_lang(self.view, self.view.file_name()))

    def reset(self):
        """Restores user settings."""
        reload_settings(self.view)
        logger(self.view, 'info', "SublimeCodeIntel Reseted!")

    def enable(self, enable):
        self.view.settings().set('codeintel', enable)
        logger(self.view, 'info', "SublimeCodeIntel %s" % ("Enabled!" if enable else "Disabled",))

    def on_off(self, enable, lang=None):
        """Turns live autocomplete on or off."""
        if lang:
            _codeintel_live_enabled_languages = self.view.settings().get('codeintel_live_enabled_languages', [])
            if lang.lower() in [l.lower() for l in _codeintel_live_enabled_languages]:
                if not enable:
                    _codeintel_live_enabled_languages = [l for l in _codeintel_live_enabled_languages if l.lower() != lang.lower()]
                    self.view.settings().set('codeintel_live_enabled_languages', _codeintel_live_enabled_languages)
                    logger(self.view, 'info', "SublimeCodeIntel Live Autocompletion for %s %s" % (lang, "Enabled!" if enable else "Disabled"))
            else:
                if enable:
                    _codeintel_live_enabled_languages.append(lang)
                    self.view.settings().set('codeintel_live_enabled_languages', _codeintel_live_enabled_languages)
                    logger(self.view, 'info', "SublimeCodeIntel Live Autocompletion for %s %s" % (lang, "Enabled!" if enable else "Disabled"))
        else:
            self.view.settings().set('codeintel_live', enable)
            logger(self.view, 'info', "SublimeCodeIntel Live Autocompletion %s" % ("Enabled!" if enable else "Disabled",))
            # logger(view, 'info', "skip `%s': disabled language" % lang)


class SublimecodeintelWindowCommand(sublime_plugin.WindowCommand):
    def is_enabled(self):
        view = self.window.active_view()
        return bool(view)

    def run_(self, args):
        pass


class SublimecodeintelCommand(SublimecodeintelWindowCommand):
    def is_enabled(self, active=None):
        enabled = super(SublimecodeintelCommand, self).is_enabled()

        if active is not None:
            view = self.window.active_view()
            enabled = enabled and codeintel_enabled(view, True) == active

        return bool(enabled)

    def run_(self, args={}):
        view = self.window.active_view()
        action = args.get('action', '')

        if view and action:
            view.run_command('codeintel', action)


class SublimecodeintelEnableCommand(SublimecodeintelCommand):
    def is_enabled(self):
        return super(SublimecodeintelEnableCommand, self).is_enabled(False)


class SublimecodeintelDisableCommand(SublimecodeintelCommand):
    def is_enabled(self):
        return super(SublimecodeintelDisableCommand, self).is_enabled(True)


class SublimecodeintelResetCommand(SublimecodeintelCommand):
    def is_enabled(self):
        return super(SublimecodeintelResetCommand, self).is_enabled()


class SublimecodeintelLiveCommand(SublimecodeintelCommand):
    def is_enabled(self, active=True, onlylang=False):
        enabled = super(SublimecodeintelLiveCommand, self).is_enabled(True)

        if active is not None:
            view = self.window.active_view()

            if onlylang:
                enabled = enabled and view.settings().get('codeintel_live', True) is True
                lang = guess_lang(view)
                enabled = enabled and lang and (lang.lower() in [l.lower() for l in view.settings().get('codeintel_live_enabled_languages', [])]) == active
            else:
                enabled = enabled and view.settings().get('codeintel_live', True) == active

        return bool(enabled)


class SublimecodeintelEnableLiveCommand(SublimecodeintelLiveCommand):
    def is_enabled(self):
        return super(SublimecodeintelEnableLiveCommand, self).is_enabled(False, False)


class SublimecodeintelDisableLiveCommand(SublimecodeintelLiveCommand):
    def is_enabled(self):
        return super(SublimecodeintelDisableLiveCommand, self).is_enabled(True, False)


class SublimecodeintelEnableLiveLangCommand(SublimecodeintelLiveCommand):
    def is_enabled(self):
        return super(SublimecodeintelEnableLiveLangCommand, self).is_enabled(False, True)


class SublimecodeintelDisableLiveLangCommand(SublimecodeintelLiveCommand):
    def is_enabled(self):
        return super(SublimecodeintelDisableLiveLangCommand, self).is_enabled(True, True)
