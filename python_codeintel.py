"""
CodeIntel is a plugin intended to display "code intelligence" information.
The plugin is based in code from the Open Komodo Editor and has a MPL license.
Port by German M. Bravo (Kronuz). May 30, 2011

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

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'libs'))

from codeintel2.common import *
from codeintel2.manager import Manager
from codeintel2.citadel import CitadelBuffer
from codeintel2.environment import SimplePrefsEnvironment
from codeintel2.util import guess_lang_from_path


class NullHandler(logging.Handler):
    def emit(self, record):
        pass
stderr_hdlr = logging.StreamHandler(sys.stderr)
stderr_hdlr.setFormatter(logging.Formatter("%(name)s: %(levelname)s: %(message)s"))
codeintel_log = logging.getLogger("codeintel")
log = logging.getLogger("SublimeCodeIntel")
codeintel_log.handlers = [ NullHandler() ]
log.handlers = [ stderr_hdlr ]

codeintel_log.setLevel(logging.DEBUG)
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

status_msg = {}
status_lineno ={}
status_lock = threading.Lock()
def calltip(view, type, msg=None, timeout=15000, delay=0, id='CodeIntel', logger=None):
    global status_msg
    if msg is None:
        msg, type = type, 'debug'
    msg = msg.strip()
    status_lock.acquire()
    try:
        status_msg[id] = (type, msg)
    finally:
        status_lock.release()
    def _calltip_erase():
        status_lock.acquire()
        try:
            if msg == status_msg.get(id, (None, None))[1]:
                view.erase_status(id)
        finally:
            status_lock.release()
    def _calltip_set():
        lineno = view.rowcol(view.sel()[0].end())[0]
        status_lock.acquire()
        try:
            if 'warning' not in id:
                status_lineno[id] = lineno
            current_tip = status_msg.get(id, (None, None))[1]
            if msg == current_tip:
                if msg:
                    view.set_status(id, "%s: %s" % (type.capitalize(), msg))
                    (logger or log.debug)(msg)
                else:
                    view.erase_status(id)
            elif current_tip:
                current_type = status_msg.get(id, (None, None))[0]
                if current_type and current_tip:
                    view.set_status(id, "%s: %s" % (current_type.capitalize(), current_tip))
                    (logger or log.debug)(current_tip)
            else:
                view.erase_status(id)
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
    if timeout is None:
        timeout = { None: 3000, 'error': 3000, 'warning': 5000, 'info': 10000 }.get(type)
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
        codeintel(view, path, content, lang, pos, ('defns',), _trigger)


_ci_mgr_ = None
_ci_envs_ = {}
_ci_db_base_dir_ = None
_ci_db_catalog_dirs_ = []
_ci_db_import_everything_langs = None
_ci_extra_module_dirs_ = None
_ci_save_callbacks_ = {}
_ci_save_ = 0

def codeintel_save(force=False):
    global _ci_save_
    print str(_ci_save_)+'.', force
    for path, callback in _ci_save_callbacks_.items():
        del _ci_save_callbacks_[path]
        callback(path)
    # saving and culling cached parts of the database:
    _ci_save_ -= 1
    if _ci_mgr_:
        if _ci_save_ % 2 == 0 or force:
            _ci_mgr_.db.save() # Save every 6 seconds
            if _ci_save_ == 0 or force:
                _ci_mgr_.db.cull_mem() # Every 30 seconds
    if _ci_save_ <= 0:
        _ci_save_ = 30
    if not force:
        sublime.set_timeout(codeintel_save, 3000)
sublime.set_timeout(codeintel_save, 3000)

def codeintel_cleanup(path):
    global _ci_mgr_
    if _ci_envs_.pop(path, None):
        if not _ci_envs_:
            codeintel_save(True)
            _ci_mgr_.finalize()
            _ci_mgr_ = None

def codeintel_scan(view, path, content, lang, callback=None):
    try:
        lang = lang or guess_lang_from_path(path)
    except CodeIntelError:
        logger(view, 'warning', "skip `%s': couldn't determine language" % path)
        return
    is_scratch = view.is_scratch()
    is_dirty = view.is_dirty()
    def _codeintel_scan():
        global _ci_mgr_
        current_thread = threading.current_thread()
        for thread in threading.enumerate():
            if thread.name == "scanning thread" and thread != current_thread:
                logger(view, 'info', "Updating indexes... The first time this can take a while. Do not despair!", timeout=20000)
                return
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
                _ci_mgr_ = mgr

            # Load configuration files:
            catalogs = []
            for catalog in mgr.db.get_catalogs_zone().avail_catalogs():
                if catalog['lang'] == lang:
                    catalogs.append(catalog['name'])
            log.debug("Catalogs for '%s': %s", lang, ', '.join(catalogs) or None)
            config = {
                "codeintel_selected_catalogs": catalogs,
                "codeintel_max_recursive_dir_depth": 10,
                "codeintel_scan_files_in_project": True,
            }
            _config = {}
            tryReadCodeIntelDict(os.path.expanduser(os.path.join('~', '.codeintel', 'config')), _config)
            project_dir = path and find_folder(path, '.codeintel')
            if project_dir:
                tryReadCodeIntelDict(os.path.join(project_dir, 'config'), _config)
            else:
                project_dir = os.path.expanduser(os.path.join('~', '.codeintel'))
            config.update(_config.get(lang, {}))
            for conf in [ 'pythonExtraPaths', 'rubyExtraPaths', 'perlExtraPaths', 'javascriptExtraPaths', 'phpExtraPaths' ]:
                v = config.get(conf)
                if v and isinstance(v, (list, tuple)):
                    v = [ p.strip() for p in v if p.strip() ]
                    config[conf] = os.pathsep.join(p if p.startswith('/') else os.path.expanduser(p) if p.startswith('~') else os.path.abspath(os.path.join(project_dir, '..', p)) for p in v if p.strip())

            env = SimplePrefsEnvironment(**config)

            _ci_envs_[path] = env

            calltip(view, "")

        encoding = None
        buf = mgr.buf_from_content(content, lang, env, path or "<Unsaved>", encoding)
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
            trg = buf.trg_from_pos(pos)
            defn_trg = buf.defn_trg_from_pos(pos)
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
            msg = eval_log_stream.getvalue()
            if msg:
                logger(view, 'warning', msg)

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
