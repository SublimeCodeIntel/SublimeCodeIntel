# -*- coding: UTF-8 -*-
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
Port by Germán M. Bravo (Kronuz). May 30, 2011

For "Jump to symbol declaration":
    Setup in User Key Bindings (Packages/User/Default.sublime-keymap):
        { "keys": ["super+f3"], "command": "goto_python_definition" }
    ...or in User Mouse Bindings (Packages/User/Default.sublime-mousemap):
        { "button": "button1", "modifiers": ["super"], "command": "goto_python_definition", "press_command": "drag_select" }

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
        "Perl": {
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
import os, sys, stat, time
import sublime_plugin, sublime
import threading
import logging
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

CODEINTEL_HOME_DIR = os.path.expanduser(os.path.join('~', '.codeintel'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'libs'))

from codeintel2.common import *
from codeintel2.manager import Manager
from codeintel2.citadel import CitadelBuffer
from codeintel2.environment import SimplePrefsEnvironment
from codeintel2.util import guess_lang_from_path

# Setup the complex logging (status bar gets stuff from there):
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
codeintel_hdlr = NullHandler()
codeintel_hdlr.setFormatter(logging.Formatter("%(name)s: %(levelname)s: %(message)s"))
stderr_hdlr = logging.StreamHandler(sys.stderr)
stderr_hdlr.setFormatter(logging.Formatter("%(name)s: %(levelname)s: %(message)s"))
codeintel_log = logging.getLogger("codeintel")
log = logging.getLogger("SublimeCodeIntel")
codeintel_log.handlers = [ codeintel_hdlr ]
log.handlers = [ stderr_hdlr ]
codeintel_log.setLevel(logging.INFO)
logging.getLogger("codeintel.db").setLevel(logging.INFO)
log.setLevel(logging.ERROR)

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

def pos2bytes(content, pos):
    return len(content[:pos].encode('utf-8'))

status_msg = {}
status_lineno ={}
status_lock = threading.Lock()
def calltip(view, type, msg=None, timeout=None, delay=0, id='CodeIntel', logger=None):
    if timeout is None:
        timeout = { None: 3000, 'error': 3000, 'warning': 5000, 'info': 10000, 'tip': 15000 }.get(type)
    if msg is None:
        msg, type = type, 'debug'
    msg = msg.strip()
    status_msg.setdefault(id, [ None, None, 0 ])
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
            if msg == status_msg.get(id, [ None, None, 0 ])[1]:
                view.erase_status(id)
                status_msg[id][1] = None
                if id in status_lineno:
                    del status_lineno[id]
        finally:
            status_lock.release()
    def _calltip_set():
        lineno = view.rowcol(view.sel()[0].end())[0]
        status_lock.acquire()
        try:
            current_type, current_msg, current_order = status_msg.get(id, [ None, None, 0 ])
            if msg != current_msg and order == current_order:
                if msg:
                    view.set_status(id, "%s: %s" % (type.capitalize(), msg))
                    (logger or log.debug)(msg)
                else:
                    view.erase_status(id)
                status_msg[id][0] = [ type, msg, order ]
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

class PythonCodeIntel(sublime_plugin.EventListener):
    def on_close(self, view):
        path = view.file_name()
        codeintel_cleanup(path)

    def on_modified(self, view):
        pos = view.sel()[0].end()
        text = view.substr(sublime.Region(pos-7, pos))

        path = view.file_name()

        lang, _ = os.path.splitext(os.path.basename(view.settings().get('syntax')))
        try:
            lang = lang or guess_lang_from_path(path)
        except CodeIntelError:
            pass

        if text and text[-1] in cpln_fillup_chars.get(lang, ''):
            content = view.substr(sublime.Region(0, view.size()))
            lang, _ = os.path.splitext(os.path.basename(view.settings().get('syntax')))
            pos = view.sel()[0].end()
            def _trigger(cplns, calltips):
                if cplns is not None:
                    # Show autocompletions:
                    self.completions = sorted(
                        [ ('%s  (%s)' % (name, type), name) for type, name in cplns ], 
                        cmp=lambda a, b: a[1] < b[1] if a[1].startswith('_') and b[1].startswith('_') else False if a[1].startswith('_') else True if b[1].startswith('_') else a[1] < b[1]
                    )
                    sublime.set_timeout(lambda: view.run_command('auto_complete'), 0)
                elif calltips is not None:
                    # Triger a tooltip
                    calltip(view, 'tip', calltips[0])
            calltip(view, 'tip', "")
            codeintel(view, path, content, lang, pos, ('cplns', 'calltips'), _trigger)
        else:
            def save_callback(path):
                content = view.substr(sublime.Region(0, view.size()))
                lang, _ = os.path.splitext(os.path.basename(view.settings().get('syntax')))
                codeintel_scan(view, path, content, lang)
            _ci_save_callbacks_[path] = save_callback

    def on_selection_modified(self, view):
        lineno = view.rowcol(view.sel()[0].end())[0]
        status_lock.acquire()
        try:
            slns = [ id for id, sln in status_lineno.items() if sln != lineno ]
        finally:
            status_lock.release()
        for id in slns:
            calltip(view, "", id=id)

    def on_query_completions(self, view, prefix, locations):
        completions = getattr(self, 'completions', [])
        self.completions = []
        return completions

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
                        log.debug('Jumping to: %s', path)
                        def __trigger():
                            window = sublime.active_window()
                            window.open_file(path, sublime.ENCODED_POSITION)
                            window.open_file(path, sublime.ENCODED_POSITION)
                        sublime.set_timeout(__trigger, 0)
        calltip(view, 'tip', "")
        codeintel(view, path, content, lang, pos, ('defns',), _trigger)

_ci_mgr_ = None
_ci_envs_ = {}
_ci_db_base_dir_ = None
_ci_db_catalog_dirs_ = []
_ci_db_import_everything_langs = None
_ci_extra_module_dirs_ = None
_ci_save_callbacks_ = {}
_ci_next_save_ = 0
_ci_next_savedb_ = 0
_ci_next_cullmem_ = 0

def codeintel_save(force=False):
    global _ci_next_save_, _ci_next_savedb_, _ci_next_cullmem_
    now = time.time()
    if now >= _ci_next_save_:
        if _ci_next_save_:
            for path, callback in _ci_save_callbacks_.items():
                del _ci_save_callbacks_[path]
                callback(path)
        _ci_next_save_ = now + 3
    # saving and culling cached parts of the database:
    if _ci_mgr_:
        if now >= _ci_next_savedb_:
            if _ci_next_savedb_:
                log.debug('Saving database')
                _ci_mgr_.db.save() # Save every 6 seconds
            _ci_next_savedb_ = now + 6
        if now >= _ci_next_cullmem_:
            if _ci_next_cullmem_:
                log.debug('Culling memory')
                _ci_mgr_.db.cull_mem() # Every 30 seconds
            _ci_next_cullmem_ = now + 30
    if not force:
        sublime.set_timeout(codeintel_save, 3100)
sublime.set_timeout(codeintel_save, 3100)

def codeintel_cleanup(path):
    global _ci_mgr_
    if _ci_envs_.pop(path, None):
        if not _ci_envs_:
            codeintel_save(True)
            _ci_mgr_.finalize()
            _ci_mgr_ = None

def codeintel_scan(view, path, content, lang, callback=None):
    for thread in threading.enumerate():
        if thread.isAlive() and thread.name == "scanning thread":
            logger(view, 'info', "Updating indexes... The first time this can take a while. Do not despair!", timeout=20000, delay=1000)
            return
    try:
        lang = lang or guess_lang_from_path(path)
    except CodeIntelError:
        logger(view, 'warning', "skip `%s': couldn't determine language" % path)
        return
    is_scratch = view.is_scratch()
    is_dirty = view.is_dirty()
    def _codeintel_scan():
        global _ci_mgr_
        try:
            env = _ci_envs_[path]
            mgr = _ci_mgr_
        except KeyError:
            if _ci_mgr_:
                mgr = _ci_mgr_
            else:
                for thread in threading.enumerate():
                    if thread.name == "CodeIntel Manager":
                        thread.finalize() # this finalizes the index, citadel and the manager and waits them to end (join)
                mgr = Manager(
                    extra_module_dirs = _ci_extra_module_dirs_,
                    db_base_dir = _ci_db_base_dir_,
                    db_catalog_dirs = _ci_db_catalog_dirs_,
                    db_import_everything_langs = _ci_db_import_everything_langs,
                    db_event_reporter = lambda m: logger(view, m),
                )
                mgr.upgrade()
                mgr.initialize()

                # Connect the logging file to the handler
                codeintel_log.handlers = [ logging.StreamHandler(open(os.path.join(mgr.db.base_dir, 'codeintel.log'), 'w', 0)) ]

                _ci_mgr_ = mgr

            # Load configuration files:
            catalogs = []
            for catalog in mgr.db.get_catalogs_zone().avail_catalogs():
                if catalog['lang'] == lang:
                    catalogs.append(catalog['name'])
            codeintel_log.info("Catalogs for '%s': %s", lang, ', '.join(catalogs) or None)
            config = {
                "codeintel_selected_catalogs": catalogs,
                "codeintel_max_recursive_dir_depth": 10,
                "codeintel_scan_files_in_project": True,
            }
            _config = {}
            tryReadCodeIntelDict(os.path.join(CODEINTEL_HOME_DIR, 'config'), _config)
            project_dir = path and find_folder(path, '.codeintel')
            if project_dir:
                tryReadCodeIntelDict(os.path.join(project_dir, 'config'), _config)
            config.update(_config.get(lang, {}))
            for conf in [ 'pythonExtraPaths', 'rubyExtraPaths', 'perlExtraPaths', 'javascriptExtraPaths', 'phpExtraPaths' ]:
                v = config.get(conf)
                if v and isinstance(v, (list, tuple)):
                    v = [ p.strip() for p in v if p.strip() ]
                    config[conf] = os.pathsep.join(p if p.startswith('/') else os.path.expanduser(p) if p.startswith('~') else os.path.abspath(os.path.join(project_dir, '..', p)) for p in v if p.strip())

            env = SimplePrefsEnvironment(**config)
            _ci_envs_[path] = env

        buf = mgr.buf_from_content(content.encode('utf-8'), lang, env, path or "<Unsaved>", 'utf-8')
        if isinstance(buf, CitadelBuffer):
            logger(view, 'info', "Updating indexes... The first time this can take a while.", timeout=20000, delay=2000)
            if not path or is_scratch:
                buf.scan() #FIXME: Always scanning unsaved files (since many tabs can have unsaved files, or find other path as ID)
            else:
                if is_dirty:
                    mtime = 1
                else:
                    mtime = os.stat(path)[stat.ST_MTIME]
                buf.scan(mtime=mtime, skip_scan_time_check=is_dirty)
        if callback:
            callback(buf)
        else:
            logger(view, 'info', "")
    threading.Thread(target=_codeintel_scan, name="scanning thread").start()

def codeintel(view, path, content, lang, pos, forms, callback=None, timeout=4000):
    start = time.time()
    def _codeintel(buf):
        cplns = None
        calltips = None
        defns = None

        if not buf:
            logger(view, 'warning', "`%s' (%s) is not a language that uses CIX" % (path, buf.lang))
            return [None] * len(forms)

        try:
            trg = buf.trg_from_pos(pos2bytes(content, pos))
            defn_trg = buf.defn_trg_from_pos(pos2bytes(content, pos))
        except CodeIntelError:
            trg = None
            defn_trg = None
        else:
            eval_log_stream = StringIO()
            hdlr = logging.StreamHandler(eval_log_stream)
            hdlr.setFormatter(logging.Formatter("%(message)s"))
            codeintel_log.addHandler(hdlr)
            ctlr = LogEvalController(codeintel_log)
            try:
                if 'cplns' in forms and trg and trg.form == TRG_FORM_CPLN:
                    cplns = buf.cplns_from_trg(trg, ctlr=ctlr)
                if 'calltips' in forms and trg and trg.form == TRG_FORM_CALLTIP:
                    calltips = buf.calltips_from_trg(trg, ctlr=ctlr)
                if 'defns' in forms and defn_trg and defn_trg.form == TRG_FORM_DEFN:
                    defns = buf.defns_from_trg(defn_trg, ctlr=ctlr)
            finally:
                codeintel_log.removeHandler(hdlr)
            logger(view, 'warning', "")
            msg = eval_log_stream.getvalue()
            msgs = msg.strip().split('\n')
            for msg in reversed(msgs):
                if msg and msg.startswith('evaluating '):
                    calltip(view, 'warning', msg)
                    break

        ret = []
        l = locals()
        for f in forms:
            ret.append(l.get(f))
        total = (time.time() - start)
        if total * 1000 < timeout:
            logger(view, 'info', "")
            callback(*ret)
        else:
            logger(view, 'info', "Just finished indexing! Please try again. Scan took %s" % total, timeout=3000)
    codeintel_scan(view, path, content, lang, _codeintel)

def find_folder(start_at, look_for):
    start_at = os.path.abspath(start_at)
    if not os.path.isdir(start_at):
        start_at = os.path.dirname(start_at)
    while True:
        if look_for in os.listdir(start_at):
            return os.path.join(start_at, look_for)
        continue_at =  os.path.abspath(os.path.join(start_at, '..'))
        if continue_at == start_at:
            return None
        start_at = continue_at

def updateCodeIntelDict(master, partial):
    for key, value in partial.items():
        if isinstance(value, dict):
            master.setdefault(key, {}).update(value)
        elif isinstance(value, (list, tuple)):
            master.setdefault(key, []).extend(value)

def tryReadCodeIntelDict(filename, dictToUpdate):
    if os.path.exists(filename):
        file = open(filename, 'r')
        try:
            updateCodeIntelDict(dictToUpdate, eval(file.read()))
        finally:
            file.close()
