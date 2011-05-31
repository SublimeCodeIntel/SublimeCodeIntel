"""
CodeIntel is a plugin intended to display "code intelligence" information.
The plugin is based in code from the Open Komodo Editor and has a MPL license.
Port by German M. Bravo (Kronuz). May 30, 2011

For "Jump to symbol declaration":
    Setup in User Key Bindings:
        { "keys": ["super+f3"], "command": "goto_python_definition" }
    ...or in User Mouse Bindings (super + click):
        { "button": "button1", "modifiers": ["super"], "command": "goto_python_definition" }

Configuration files (`~/.codeintel/config' or `project_root/.codeintel/config'). Example:
    {
        "PHP": {
            "php": '/usr/bin/php',
            "phpExtraPaths": [],
            "phpConfigFile": 'php.ini',
        },
        "JavaScript": {
            "javascriptExtraPaths": [],
        },
        "Perl": {
            "perl": "/usr/bin/perl",
            "perlExtraPaths": [],
        },
        "Perl": {
            "ruby": "/usr/bin/ruby",
            "rubyExtraPaths": [],
        },
        "Python": {
            "python": '/usr/bin/python',
            "pythonExtraPaths": [],
        },
        "Python3": {
            "python": '/usr/bin/python3',
            "pythonExtraPaths": [],
        },
    }

"""
import os, sys
import sublime_plugin, sublime
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

codeintel_logger = logging.getLogger("codeintel")
codeintel_logger.addHandler(logging.StreamHandler(sys.stderr))

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
def calltip(view, tip, delay=0, timeout=10000, id='CodeIntel'):
    global status_msg
    status_msg[id] = tip
    def _calltip_erase():
        if tip == status_msg.get(id):
            view.erase_status(id)
    def _calltip_set():
        status_lineno[id] = view.rowcol(view.sel()[0].end())[0]
        if tip == status_msg.get(id):
            if tip:
                view.set_status(id, tip)
            else:
                view.erase_status(id)
    try:
        if delay:
            sublime.set_timeout(_calltip_set, delay)
        else:
            _calltip_set()
    except:
        sublime.set_timeout(_calltip_set, delay)
    if tip:
        sublime.set_timeout(_calltip_erase, timeout)

def logger(view, type, msg=None, delay=0, timeout=None, id='CodeIntel'):
    if msg is None:
        msg, type = type, "Info"
    if timeout is None:
        timeout = { None: 3000, "Error": 3000, "Warning": 5000, "Info": 500 }.get(type)
    calltip(view, '%s: %s' % (type, msg), delay, timeout, id + '-' + type)

class PythonCodeIntel(sublime_plugin.EventListener):
    def on_close(self, view):
        path = view.file_name() or "<Unsaved>"
        codeintel_cleanup(path)

    def on_modified(self, view):
        pos = view.sel()[0].end()
        text = view.substr(sublime.Region(pos-7, pos))

        path = view.file_name() or "<Unsaved>"
        lang, _ = os.path.splitext(os.path.basename(view.settings().get('syntax')))
        try:
            lang = lang or guess_lang_from_path(path)
        except CodeIntelError:
            pass

        if text and text[-1] in cpln_fillup_chars.get(lang, ''):
            path = view.file_name() or "<Unsaved>"
            content = view.substr(sublime.Region(0, view.size()))
            lang, _ = os.path.splitext(os.path.basename(view.settings().get('syntax')))
            pos = view.sel()[0].end()
            cplns, calltips = codeintel(view, path, content, lang, pos, forms=('cplns', 'calltips'))
            if cplns is not None:
                # Show autocompletions:
                self.completions = sorted(
                    [ ('%s  (%s)' % (name, type), name) for type, name in cplns ], 
                    cmp=lambda a, b: a[1] < b[1] if a[1].startswith('_') and b[1].startswith('_') else False if a[1].startswith('_') else True if b[1].startswith('_') else a[1] < b[1]
                )
                view.run_command('auto_complete')
            elif calltips is not None:
                # Triger a tooltip
                calltip(view, calltips[0])

    def on_selection_modified(self, view):
        lineno = view.rowcol(view.sel()[0].end())[0]
        for id, sln in status_lineno.items():
            if lineno != sln:
                calltip(view, "", id=id)

    def on_query_completions(self, view, prefix, locations):
        completions = getattr(self, 'completions', [])
        self.completions = []
        return completions


class GotoPythonDefinition(sublime_plugin.TextCommand):
    def run(self, edit, block=False):
        path = self.view.file_name() or '<Unsaved>'
        content = self.view.substr(sublime.Region(0, self.view.size()))
        lang, _ = os.path.splitext(os.path.basename(self.view.settings().get('syntax')))
        pos = self.view.sel()[0].end()
        defns, = codeintel(self.view, path, content, lang, pos, forms=('defns',))
        if defns is not None:
            defn = defns[0]
            path = defn.path
            if path:
                if defn.line:
                    path += ':' + str(defn.line)
                window = sublime.active_window()
                window.open_file(path, sublime.ENCODED_POSITION)
                window.open_file(path, sublime.ENCODED_POSITION)


_codeintel_ = {}
_ci_db_base_dir_ = None
_ci_db_catalog_dirs_ = []
_ci_db_import_everything_langs = None
_ci_extra_module_dirs_ = None

def codeintel_cleanup(path):
    if path in _codeintel_:
        mgr, env = _codeintel_[path]
        mgr.finalize()
        del _codeintel_[path]

def codeintel(view, path, content, lang, pos, forms):
    cplns = None
    calltips = None
    defns = None
    
    try:
        lang = lang or guess_lang_from_path(path)
    except CodeIntelError:
        logger(view, "Warning", "skip `%s': couldn't determine language" % path)
        return [None] * len(forms)
    encoding = None

    try:
        mgr, env = _codeintel_[path]
        print 'reused!'
    except KeyError:
        print 'created!'
        calltip(view, "About to update indexes. The first time this can take a while. Do not despair!", delay=1000)
        
        mgr = Manager(
            extra_module_dirs = _ci_extra_module_dirs_,
            db_base_dir = _ci_db_base_dir_,
            db_catalog_dirs = _ci_db_catalog_dirs_,
            db_import_everything_langs = _ci_db_import_everything_langs,
            db_event_reporter = lambda m: logger(view, m),
        )
        catalogs = []
        for catalog in mgr.db.get_catalogs_zone().avail_catalogs():
            if catalog['lang'] == lang:
                catalogs.append(catalog['name'])
        config = {
            "codeintel_selected_catalogs": catalogs,
            "codeintel_max_recursive_dir_depth": 10,
            "codeintel_scan_files_in_project": True,
        }
        _config = {}
        tryReadCodeIntelDict(os.path.expanduser(os.path.join('~', '.codeintel', 'config')), _config)
        project_dir = find_ropeproject(path, '.codeintel')
        if project_dir:
            tryReadCodeIntelDict(os.path.join(project_dir, 'config'), _config)
        config.update(_config.get(lang, {}))
        for conf in [ 'pythonExtraPaths', 'rubyExtraPaths', 'perlExtraPaths', 'javascriptExtraPaths', 'phpExtraPaths' ]:
            v = config.get(conf)
            if v and isinstance(v, (list, tuple)):
                config[conf] = os.pathsep.join(v)

        env = SimplePrefsEnvironment(**config)

        mgr.env = env
        mgr.upgrade()
        mgr.initialize()

        _codeintel_[path] = (mgr, env)

        calltip(view, "")

    buf = mgr.buf_from_content(content, lang, env, path, encoding)
    if not isinstance(buf, CitadelBuffer):
        logger(view, "Error", "`%s' (%s) is not a language that uses CIX" % (path, buf.lang))
        return [None] * len(forms)
        
    if 'cplns' in forms or 'calltips' in forms or 'defns' in forms:
        try:
            trg = buf.trg_from_pos(pos)
            defn_trg = buf.defn_trg_from_pos(pos)
        except CodeIntelError:
            trg = None
            defn_trg = None
        else:
            eval_log_stream = StringIO()
            hdlr = logging.StreamHandler(eval_log_stream)
            fmtr = logging.Formatter("%(name)s: %(levelname)s: %(message)s")
            hdlr.setFormatter(fmtr)
            codeintel_logger.addHandler(hdlr)
            ctlr = LogEvalController(codeintel_logger)
            try:
                if 'cplns' in forms and trg and trg.form == TRG_FORM_CPLN:
                    cplns = buf.cplns_from_trg(trg, ctlr=ctlr)
                if 'calltips' in forms and trg and trg.form == TRG_FORM_CALLTIP:
                    calltips = buf.calltips_from_trg(trg, ctlr=ctlr)
                if 'defns' in forms and defn_trg and defn_trg.form == TRG_FORM_DEFN:
                    defns = buf.defns_from_trg(defn_trg, ctlr=ctlr)
            finally:
                codeintel_logger.removeHandler(hdlr)
            msg = eval_log_stream.getvalue()
            if msg:
                logger(view, "Error", msg)

    ret = []
    l = locals()
    for f in forms:
        ret.append(l.get(f))
    return ret

def find_ropeproject(start_at, look_for):
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
