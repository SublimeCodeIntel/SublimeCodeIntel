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
            "phpConfigFile": "php.ini"
        },
        "Perl": {
            "perl": "/usr/bin/perl"
        },
        "Ruby": {
            "ruby": "/usr/bin/ruby"
        },
        "Python": {
            "python": "/usr/bin/python"
        },
        "Python3": {
            "python3": "/usr/bin/python3"
        }
    }
"""
from __future__ import print_function, unicode_literals

VERSION = "2.2.0"

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
import json

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

try:
    from io import StringIO
    string_types = str
except ImportError:
    from cStringIO import StringIO
    string_types = basestring


CODEINTEL_HOME_DIR = os.path.expanduser(os.path.join('~', '.codeintel'))
__file__ = os.path.normpath(os.path.abspath(__file__))
__path__ = os.path.dirname(__file__)

libs_path = os.path.join(__path__, 'libs')
if libs_path not in sys.path:
    sys.path.insert(0, libs_path)

arch_path = os.path.join(__path__, 'arch')
if arch_path not in sys.path:
    sys.path.insert(0, arch_path)

cplns_were_empty = None
last_trigger_name = None
last_citdl_expr = None

from codeintel2.common import CodeIntelError, EvalTimeout, LogEvalController, TRG_FORM_CPLN, TRG_FORM_CALLTIP, TRG_FORM_DEFN
from codeintel2.manager import Manager
from codeintel2.environment import SimplePrefsEnvironment
from codeintel2.util import guess_lang_from_path


QUEUE = {}  # views waiting to be processed by codeintel


# Setup the complex logging (status bar gets stuff from there):
# http://docs.python.org/3.3/howto/logging.html#logging-basic-tutorial
class NullHandler(logging.Handler):
    def emit(self, record):
        pass

condeintel_log_filename = ''
condeintel_log_file = None

stderr_hdlr = logging.StreamHandler(sys.stderr)
stderr_hdlr.setFormatter(logging.Formatter("%(name)s: %(levelname)s: %(message)s"))

codeintel_hdlr = NullHandler()
codeintel_hdlr.setFormatter(logging.Formatter("%(name)s: %(levelname)s: %(message)s"))

# Logging for this file / send to the sublime console
log = logging.getLogger("SublimeCodeIntel")
log.handlers = [stderr_hdlr]
log.setLevel(logging.ERROR)  # ERROR

# the parent-logger for the rest of the plugin / send to the codeintel.log file in database dir
codeintel_log = logging.getLogger("codeintel")
codeintel_log.handlers = [codeintel_hdlr]
codeintel_log.setLevel(logging.INFO)  # INFO

# create all the child-loggers for various parts of the plugin
for logger in ('codeintel.db', 'codeintel.pythoncile'):
    logging.getLogger(logger).setLevel(logging.WARNING)  # WARNING
for logger in ('citadel', 'css', 'django', 'html', 'html5', 'javascript', 'mason', 'nodejs',
               'perl', 'php', 'python', 'python3', 'rhtml', 'ruby', 'smarty',
               'tcl', 'templatetoolkit', 'xbl', 'xml', 'xslt', 'xul'):
    logging.getLogger("codeintel." + logger).setLevel(logging.WARNING)  # WARNING

cpln_fillup_chars = {
    # These are characters that select the first item in an open autocomplete window when pressed.
    # (autocompete_on_fillup should be a configuration and fillup chars take precedence over stop chars)
    'Ruby': "~`@#$%^&*(+}[]|\\;:,<>/ ",
    'PHP': "~`%^&*()-+{}[]|;'\",.< ",
    'Python': "~`!@#$%^&()-=+{}[]|\\;:'\",.<>?/ ",
    'Python3': "~`!@#$%^&()-=+{}[]|\\;:'\",.<>?/ ",
    'Perl': "~`!@#$%^&*(=+}[]|\\;'\",.<>?/ ",
    'CSS': " '\";},/",
    'JavaScript': "~`!#%^&*()-=+{}[]|\\;:'\",.<>?/",
}

cpln_stop_chars = {
    # These are characters that close the autocomplete window when pressed.
    'Ruby': "~`@#$%^&*(+}[]|\\;:,<>/ '\".",
    'PHP': "~`@%^&*()=+{}]|\\;:'\",.<>?/ ",
    'Python': "~`!@#$%^&*()-=+{}[]|\\;:'\",.<>?/ ",
    'Python3': "~`!@#$%^&*()-=+{}[]|\\;:'\",.<>?/ ",
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


class TooltipOutputCommand(sublime_plugin.TextCommand):
    def run(self, edit, output='', clear=True):
        if clear:
            region = sublime.Region(0, self.view.size())
            self.view.erase(edit, region)
        self.view.insert(edit, 0, output)


def hide_auto_complete(view):
    view.run_command('hide_auto_complete')


def show_auto_complete(view, on_query_info,
                       disable_auto_insert=True, api_completions_only=True,
                       next_completion_if_showing=False, auto_complete_commit_on_tab=True):
    # Show autocompletions:
    def _show_auto_complete():
        view.run_command('auto_complete', {
            'disable_auto_insert': disable_auto_insert,
            'api_completions_only': api_completions_only,
            'next_completion_if_showing': next_completion_if_showing,
            'auto_complete_commit_on_tab': auto_complete_commit_on_tab,
        })
    completions[view.id()] = on_query_info
    sublime.set_timeout(_show_auto_complete, 0)


def tooltip_popup(view, snippets):
    show_auto_complete(view, {
        'params': ("tooltips", "none", "", None, None, False),
        'cplns': snippets,
    })


def tooltip(view, calltips, text_in_current_line, original_pos, lang):
    codeintel_snippets = settings_manager.get('codeintel_snippets', default=True, language=lang)
    codeintel_tooltips = settings_manager.get('codeintel_tooltips', default='popup', language=lang)

    snippets = []
    for calltip in calltips:
        tip_info = calltip.split('\n')
        text = ' '.join(tip_info[1:])
        snippet = None
        # TODO: This snippets are based and work for Python language.
        # Other languages might need different treatment.
        # Insert parameters as snippet:
        m = re.search(r'([^\s]+)\(([^\[\(\)]*)', tip_info[0])
        # Figure out how many arguments are there already:
        text_in_current_line = text_in_current_line[:-1]  # Remove next char after cursor
        arguments = text_in_current_line.rpartition('(')[2].replace(' ', '').strip() or 0
        if arguments:
            initial_separator = ''
            if arguments[-1] == ',':
                arguments = arguments[:-1]
            else:
                initial_separator += ','
            if not text_in_current_line.endswith(' '):
                initial_separator += ' '
            arguments = arguments.count(',') + 1 if arguments else 0
        if m:
            params = [p.strip() for p in m.group(2).split(',')]
            if params:
                n = 1
                snippet = []
                for i, p in enumerate(params):
                    if p and i >= arguments:
                        var, _, _ = p.partition('=')
                        var = var.strip()
                        if ' ' in var:
                            var = var.split(' ')[1]
                        if var[0] == '$':
                            var = var[1:]
                        snippet.append('${%s:%s}' % (n, var))
                        n += 1
                snippet = ', '.join(snippet)
                if arguments and snippet:
                    snippet = initial_separator + snippet
            text += ' - ' + tip_info[0]  # Add function to the end
        else:
            text = tip_info[0] + ' ' + text  # No function match, just add the first line
        if not codeintel_snippets:
            snippet = None

        # Wrap lines that are too long:
        max_line_length = 80
        measured_tips = []
        for tip in tip_info:
            if len(tip) > max_line_length:
                chunks = len(tip)
                for i in range(0, chunks, max_line_length):
                    measured_tips.append(tip[i:i + max_line_length])
            else:
                measured_tips.append(tip)

        # Insert tooltip snippet
        snippets.extend((('  ' if i > 0 else '') + l, snippet or '${0}') for i, l in enumerate(measured_tips))

    if codeintel_tooltips == 'popup':
        tooltip_popup(view, snippets)
    elif codeintel_tooltips in ('status', 'panel'):
        if codeintel_tooltips == 'status':
            set_status(view, 'tip', text, timeout=15000)
        else:
            window = view.window()
            output_panel = window.get_output_panel('tooltips')
            output_panel.set_read_only(False)
            text = '\n'.join(list(zip(*snippets))[0])
            output_panel.run_command('tooltip_output', {'output': text})
            output_panel.set_read_only(True)
            window.run_command('show_panel', {'panel': 'output.tooltips'})
            sublime.set_timeout(lambda: window.run_command('hide_panel', {'panel': 'output.tooltips'}), 15000)

        if snippets and codeintel_snippets:
            # Insert function call snippets:
            # func = m.group(1)
            # scope = view.scope_name(pos)
            # view.run_command('new_snippet', {'contents': snippets[0][0], 'tab_trigger': func, 'scope': scope})  # FIXME: Doesn't add the new snippet... is it possible to do so?
            def _insert_snippet():
                # Check to see we are still at a position where the snippet is wanted:
                view_sel = view.sel()
                if not view_sel:
                    return
                sel = view_sel[0]
                pos = sel.end()
                if not pos or pos != original_pos:
                    return
                view.run_command('insert_snippet', {'contents': snippets[0][0]})
            sublime.set_timeout(_insert_snippet, 500)  # Delay snippet insertion a bit... it's annoying some times


def set_status(view, ltype, msg=None, timeout=None, delay=0, lid='CodeIntel', logger=None):
    if timeout is None:
        timeout = {'error': 3000, 'warning': 5000, 'info': 10000,
                   'event': 10000}.get(ltype, 3000)

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

    def _set_status():
        is_warning = 'warning' in lid
        if not is_warning:
            view_sel = view.sel()
            lineno = view.rowcol(view_sel[0].end())[0] if view_sel else 0
        status_lock.acquire()
        try:
            current_type, current_msg, current_order = status_msg.get(lid, [None, None, 0])
            if msg != current_msg and order == current_order:
                print("+", "%s: %s" % (ltype.capitalize(), msg), file=condeintel_log_file)
                (logger or log.info)(msg)
                if ltype != 'debug':
                    view.set_status(lid, "%s: %s" % (ltype.capitalize(), msg))
                    status_msg[lid] = [ltype, msg, order]
                if not is_warning:
                    status_lineno[lid] = lineno
        finally:
            status_lock.release()

    def _erase_status():
        status_lock.acquire()
        try:
            if msg == status_msg.get(lid, [None, None, 0])[1]:
                view.erase_status(lid)
                status_msg[lid][1] = None
                if lid in status_lineno:
                    del status_lineno[lid]
        finally:
            status_lock.release()

    if msg:
        sublime.set_timeout(_set_status, delay or 0)
        sublime.set_timeout(_erase_status, timeout)
    else:
        sublime.set_timeout(_erase_status, delay or 0)


def logger(view, ltype, msg=None, timeout=None, delay=0, lid='CodeIntel'):
    if msg is None:
        msg, ltype = ltype, 'info'
    set_status(view, ltype, msg, timeout=timeout, delay=delay, lid=lid + '-' + ltype, logger=getattr(log, ltype, None))


def getSublimeScope(view):
    view_sel = view.sel()
    if not view_sel:
        sublime.message_dialog("NO VIEW SELECTION IN getSublimeScope()")
        return

    sel = view_sel[0]
    pos = sel.end()

    return view.scope_name(pos)


source_scopes = {
    "json": "JSON",
    "js": "JavaScript",
    "python.3": "Python3",
    "python": "Python",
    "php": "PHP",
    "perl": "Perl",
    "ruby": "Ruby"
}

# order is important - longest keys first
ordered_checks = OrderedDict(sorted(source_scopes.items(), key=lambda t: len(t[0]), reverse=True))


def guess_lang(view=None, path=None, sublime_scope=None):
    if not view:
        return None

    #######################################
    # try to guess lang using sublime scope

    scopes = sublime_scope if sublime_scope else getSublimeScope(view)
    if scopes:
        for scope in scopes.split(" "):
            if "source" in scope:
                for check in ordered_checks:
                    if scope[7:].startswith(check):
                        return source_scopes[check]

    if 'text.plain' in scopes:
        return None

    if not codeintel_enabled(view):
        return None

    # check for html
    if "text.html" in scopes:
        return "HTML"

    ###################################################################
    # try to guess lang by sublime syntax setting (see your status bar)

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
    _codeintel_syntax_map = dict((k.lower(), v) for k, v in settings_manager.get('codeintel_syntax_map', {}).items())
    _lang = lang = syntax and _codeintel_syntax_map.get(syntax.lower(), syntax)

    # folders = getattr(view.window(), 'folders', lambda: [])()  # FIXME: it's like this for backward compatibility (<= 2060)
    # folders_id = str(hash(frozenset(folders)))
    mgr = None if settings_manager._settings_id is None else codeintel_manager()

    if mgr and not mgr.is_citadel_lang(lang) and not mgr.is_cpln_lang(lang):
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


# timeout, busy_timeout are shorter for fill chars
# premptive is true for fillchars
def autocomplete(view, timeout, busy_timeout, forms, preemptive=False, args=[], kwargs={}):
    def _autocomplete_callback(view, path, original_pos, lang, caller=None):
        view_sel = view.sel()
        if not view_sel:
            return

        # Figure out if we're still at the same position when the autocomplete was called, or abort
        sel = view_sel[0]
        pos = sel.end()
        if not pos or pos != original_pos:
            return

        lpos = view.line(sel).begin()
        text_in_current_line = view.substr(sublime.Region(lpos, pos + 1))

        def _trigger(trigger, citdl_expr, calltips=None, cplns=None):
            global cplns_were_empty, last_trigger_name, last_citdl_expr

            add_word_completions = settings_manager.get("codeintel_word_completions", language=lang)

            if cplns is not None or calltips is not None:
                codeintel_log.info("Autocomplete called (%s) [%s]", lang, ','.join(c for c in ['cplns' if cplns else None, 'calltips' if calltips else None] if c))

            # under certain circumstances we have to close before reopening
            # the currently open completions-panel

            # completions are available now, but were empty on last round,
            # we have to close and reopen the completions tab to show them
            cplns_are_empty = cplns is None
            if cplns_were_empty and not cplns_are_empty:
                hide_auto_complete(view)
            cplns_were_empty = cplns_are_empty

            # citdl_expr changed, so might the completions!
            if citdl_expr != last_citdl_expr:
                if not (not citdl_expr and not last_citdl_expr):
                    log.debug("hiding automplete-panel, b/c CITDL_EXPR CHANGED: FROM %r TO %r" % (last_citdl_expr, citdl_expr))
                    hide_auto_complete(view)
            last_citdl_expr = citdl_expr

            # the trigger changed, so will the completions!
            current_trigger_name = trigger.name if trigger else None
            if trigger is None and last_trigger_name is not None or last_trigger_name != current_trigger_name:
                log.debug("hiding automplete-panel, b/c trigger changed: FROM %r TO %r " % (last_trigger_name, (trigger.name if trigger else 'None')))
                hide_auto_complete(view)
            last_trigger_name = current_trigger_name

            api_completions_only = False
            if trigger:
                log.debug("current triggername: %r" % trigger.name)
                print("current triggername: %r" % trigger.name)
                api_cplns_only_trigger = [
                    "php-complete-static-members",
                    "php-complete-object-members",
                    "python3-complete-module-members",
                    "python3-complete-object-members",
                    "python3-complete-available-imports",
                    "javascript-complete-object-members"
                ]
                if cplns is not None and trigger.name in api_cplns_only_trigger:
                    api_completions_only = True
                    add_word_completions = "None"

            show_auto_complete(view, {
                'params': ("cplns", add_word_completions, text_in_current_line, lang, trigger, False),
                'cplns': cplns,
            }, api_completions_only=api_completions_only)

            if calltips:
                tooltip(view, calltips, text_in_current_line, original_pos, lang)

        content = view.substr(sublime.Region(0, view.size()))
        codeintel(view, path, content, lang, pos, forms, _trigger, caller=caller)
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
    """An infinite loop running the codeintel in a background thread, meant to
        update the view after user modifies it and then does no further
        modifications for some time as to not slow down the UI with autocompletes."""
    global __signaled_, __signaled_first_
    while __loop_:
        # print('acquire...')
        __semaphore_.acquire()
        __signaled_first_ = 0
        __signaled_ = 0
        # print("DISPATCHING!", len(QUEUE))
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
            # print('first',)
        # print('queued in', (__signaled_ - now))
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
        # print('delayed to', (preemptive, __signaled_ - now))

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
            print("thread finalize")
            thread.__semaphore_.release()
            thread.join(timeout)
queue_finalize()

# Initialize background thread:
__loop_ = True
# is this the replacement for the manager???
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


# queue_dispatcher
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
    for manager_id in list(_ci_mgr_.keys()):
        mgr = codeintel_manager(manager_id)
        if mgr is None:
            del _ci_mgr_[manager_id]
            print("NO MANAGER")
            return
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

queue_dispatcher = codeintel_callbacks  # NOQA


def codeintel_cleanup(id):
    if id in _ci_envs_:
        del _ci_envs_[id]
    if id in _ci_next_scan_:
        del _ci_next_scan_[id]


def codeintel_manager(manager_id=None):
    global _ci_mgr_, condeintel_log_filename, condeintel_log_file

    if manager_id is not None:
        mgr = _ci_mgr_.get(manager_id, None)
        return mgr

    manager_id = settings_manager._settings_id
    mgr = _ci_mgr_.get(manager_id, None)

    if mgr is None:
        codeintel_database_dir = os.path.expanduser(settings_manager.get("codeintel_database_dir"))

        for thread in threading.enumerate():
            if thread.name == "CodeIntel Manager":
                thread.finalize()  # this finalizes the index, citadel and the manager and waits them to end (join)
        mgr = Manager(
            extra_module_dirs=None,
            db_base_dir=codeintel_database_dir,  # os.path.expanduser(os.path.join('~', '.codeintel', 'databases', folders_id)),
            db_catalog_dirs=[],
            db_import_everything_langs=None,
        )
        mgr.upgrade()
        mgr.initialize()

        # Connect the logging file to the handler
        condeintel_log_filename = os.path.join(codeintel_database_dir, 'codeintel.log')
        condeintel_log_file = open(condeintel_log_filename, 'w', 1)
        codeintel_log.handlers = [logging.StreamHandler(condeintel_log_file)]
        msg = "Starting logging SublimeCodeIntel v%s rev %s (%s) on %s" % (VERSION, get_revision()[:12], os.stat(__file__)[stat.ST_MTIME], datetime.datetime.now().ctime())
        print("%s\n%s" % (msg, "=" * len(msg)), file=condeintel_log_file)

        _ci_mgr_ = {}
        _ci_mgr_[manager_id] = mgr
    return mgr


def codeintel_scan(view, path, content, lang, callback=None, pos=None, forms=None, caller=None):
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

    # load settings for this language
    config = settings_manager.getSettings(lang)

    def _codeintel_scan():
        global despair, despaired
        env = None
        mtime = None
        catalogs = []
        now = time.time()

        mgr = codeintel_manager()
        mgr.db.event_reporter = lambda m: logger(view, 'event', m)

        # config values are provided per view(!) and are stored in an
        # Environment Object
        try:
            env = _ci_envs_[vid]
            if env._folders != folders:
                raise KeyError
            if env._lang != lang:
                # if the language changes within one view (HTML/PHP) we need to
                # update our Environment Object on each change!
                raise KeyError
            if env._mtime != settings_manager._settings_id:
                raise KeyError
        except KeyError:
            # Generate new Environment
            env = generateEnvironment(config, mgr, lang, folders)
            _ci_envs_[vid] = env
        # env._time = now + 5  # don't check again in less than five seconds

        # this happens in any case:
        msgs = []
        buf = None
        if env._valid:
            # is citadel language or other supported language
            if forms:
                set_status(view, 'tip', "")
                set_status(view, 'event', "")
                msg = "CodeIntel(%s) for %s@%s [%s]" % (', '.join(forms), path, pos, lang)
                msgs.append(('info', "\n%s\n%s" % (msg, "-" * len(msg))))

            if catalogs:
                msg = "New env with catalogs for '%s': %s" % (lang, ', '.join(catalogs) or None)
                log.debug(msg)
                codeintel_log.warning(msg)
                msgs.append(('info', msg))

            if mgr.is_citadel_lang(lang):
                buf = mgr.buf_from_content(content, lang, env, path or "<Unsaved>", 'utf-8')
                buf.caller = caller
                buf.orig_pos = pos

                now = datetime.datetime.now()
                if not _ci_next_scan_.get(vid) or now > _ci_next_scan_[vid]:
                    _ci_next_scan_[vid] = now + datetime.timedelta(seconds=10)
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
        if callback:
            msg = "Doing CodeIntel for '%s' (hold on)..." % lang
            print(msg, file=condeintel_log_file)
            logger(view, 'info', msg, timeout=20000, delay=1000)
            callback(buf, msgs)
        else:
            logger(view, 'info', "")
    threading.Thread(target=_codeintel_scan, name="scanning thread").start()


def codeintel(view, path, content, lang, pos, forms, callback, timeout=7000, caller=None):
    start = time.time()

    def _codeintel(buf, msgs):
        cplns = None
        calltips = None
        defns = None

        if not buf:
            logger(view, 'warning', "`%s' (%s) is not a language that uses CIX" % (path, lang))
            return [None] * len(forms)

        def get_trg(type, *args):
            try:
                trg = getattr(buf, type, lambda *a: None)(*args)
            except CodeIntelError:
                codeintel_log.exception("Exception! %s:%s (%s)" % (path or '<Unsaved>', pos, lang))
                logger(view, 'info', "Error indexing! Please send the log file: '%s" % condeintel_log_filename)
                trg = None
            except:
                codeintel_log.exception("Exception! %s:%s (%s)" % (path or '<Unsaved>', pos, lang))
                logger(view, 'info', "Error indexing! Please send the log file: '%s" % condeintel_log_filename)
                raise
            return trg

        bpos = pos2bytes(content, pos)
        if caller == 'on_modified':
            trg = get_trg('trg_from_pos', bpos)  # Use fast trg_from_pos
        else:
            trg = get_trg('preceding_trg_from_pos', bpos, bpos)  # Use more precise preceding_trg_from_pos
        defn_trg = get_trg('defn_trg_from_pos', bpos) if 'defns' in forms else None

        eval_log_stream = StringIO()
        _hdlrs = codeintel_log.handlers
        hdlr = logging.StreamHandler(eval_log_stream)
        hdlr.setFormatter(logging.Formatter("%(name)s: %(levelname)s: %(message)s"))
        codeintel_log.handlers = list(_hdlrs) + [hdlr]
        ctlr = LogEvalController(codeintel_log)
        try:
            if 'cplns' in forms:
                if trg and trg.form == TRG_FORM_CPLN:
                    cplns = buf.cplns_from_trg(trg, ctlr=ctlr, timeout=20)
            if 'calltips' in forms:
                if trg and trg.form == TRG_FORM_CALLTIP:
                    calltips = buf.calltips_from_trg(trg, ctlr=ctlr, timeout=20)
            if 'defns' in forms:
                if defn_trg and defn_trg.form == TRG_FORM_DEFN:
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
                    set_status(view, 'warning', msg)
                    result = True

        # collect citdl_expr from this run
        citdl_expr = buf.last_citdl_expr

        ret = {
            "trigger": trg,
            "citdl_expr": citdl_expr
        }
        for f in forms:
            if f == 'cplns':
                ret["cplns"] = cplns
            elif f == 'calltips':
                ret["calltips"] = calltips
            elif f == 'defns':
                ret["defns"] = defns

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
                    callback(**ret)
            logger(view, 'info', "")
            sublime.set_timeout(_callback, 0)
        else:
            msg = "Just finished indexing '%s'! Please try again. Full CodeIntel took %s" % (lang, timestr)
            print(msg, file=condeintel_log_file)
            logger(view, 'info', msg, timeout=3000)
    codeintel_scan(view, path, content, lang, _codeintel, pos, forms, caller=caller)


def generateEnvironment(config, mgr, lang, folders):
    catalogs = []
    valid = True
    if not mgr.is_citadel_lang(lang) and not mgr.is_cpln_lang(lang):
        if lang in ('Console', 'Plain text'):
            msg = "Invalid language: %s. Available: %s" % (lang, ', '.join(set(mgr.get_citadel_langs() + mgr.get_cpln_langs())))
            log.debug(msg)
            codeintel_log.warning(msg)
        valid = False

    codeintel_selected_catalogs = config.get('codeintel_selected_catalogs')

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

    # scan_extra_dir
    if config.get('codeintel_scan_files_in_project', True):
        scan_extra_dir = list(folders)
    else:
        scan_extra_dir = []

    scan_extra_dir.extend(config.get("codeintel_scan_extra_dir", []))
    config["codeintel_scan_extra_dir"] = scan_extra_dir

    for conf, p in config.items():
        if isinstance(p, string_types) and p.startswith('~'):
            config[conf] = os.path.expanduser(p)

    # Setup environment variables
    # lang env settings
    env = config.get('env', {})
    # basis is os environment
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
    env._mtime = settings_manager._settings_id
    env._lang = lang
    env._folders = folders

    return env


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


def triggerWordCompletions(view, lang, codeintel_word_completions):
    # fast triggering
    global last_trigger_name, last_citdl_expr
    last_citdl_expr = None
    last_trigger_name = None

    show_auto_complete(view, {
        'params': ("cplns", codeintel_word_completions, "", None, None, True),
        'cplns': None,
    }, api_completions_only=False)


# thanks to https://github.com/alienhard
# and his SublimeAllAutocomplete
class WordCompletionsFromBuffer():
    # limits to prevent bogging down the system
    MIN_WORD_SIZE = 3
    MAX_WORD_SIZE = 50

    MAX_VIEWS = 20
    MAX_WORDS_PER_VIEW = 500
    MAX_FIX_TIME_SECS_PER_VIEW = 0.01

    def getCompletions(self, view, prefix, locations, add_word_completions):
        # words from buffer
        words = []
        if add_word_completions == "buffer":
            words = view.extract_completions(prefix, locations[0])
        if add_word_completions == "all":
            views = sublime.active_window().views()
            views = views[0:self.MAX_VIEWS]
            for v in views:
                words += v.extract_completions(prefix)

        words = self.filter_words(words)
        words = self.fix_truncation(view, words)
        words = self.without_duplicates(words)
        matches = [(w, w.replace('$', '\\$')) for w in words]

        return matches

    def filter_words(self, words):
        words = words[0:self.MAX_WORDS_PER_VIEW]
        return [w for w in words if self.MIN_WORD_SIZE <= len(w) <= self.MAX_WORD_SIZE]

    # keeps first instance of every word and retains the original order
    # (n^2 but should not be a problem as len(words) <= MAX_VIEWS*MAX_WORDS_PER_VIEW)
    def without_duplicates(self, words):
        result = []
        for w in words:
            if w not in result:
                result.append(w)
        return result

    # Ugly workaround for truncation bug in Sublime when using view.extract_completions()
    # in some types of files.
    def fix_truncation(self, view, words):
        fixed_words = []
        start_time = time.time()

        for i, w in enumerate(words):
            # The word is truncated if and only if it cannot be found with a word boundary before and after
            # this fails to match strings with trailing non-alpha chars, like
            # 'foo?' or 'bar!', which are common for instance in Ruby.
            match = view.find(r'\b' + re.escape(w) + r'\b', 0)
            truncated = self.is_empty_match(match)
            if truncated:
                # Truncation is always by a single character, so we extend the
                # word by one word character before a word boundary
                extended_words = []
                view.find_all(r'\b' + re.escape(w) + r'\w\b', 0, "$0", extended_words)
                if len(extended_words) > 0:
                    fixed_words += extended_words
                else:
                    # to compensate for the missing match problem mentioned above, just
                    # use the old word if we didn't find any extended matches
                    fixed_words.append(w)
            else:
                # Pass through non-truncated words
                fixed_words.append(w)

            # if too much time is spent in here, bail out,
            # and don't bother fixing the remaining words
            if time.time() - start_time > self.MAX_FIX_TIME_SECS_PER_VIEW:
                return fixed_words + words[i + 1:]

        return fixed_words

    def is_empty_match(self, match):
        return match is None or match.empty()


class SettingsManager():
    # name of the *.sublime-settings file
    SETTINGS_FILE_NAME = 'SublimeCodeIntel'

    # you can set these in your *.sublime-project file
    CORE_SETTINGS = [
        'codeintel',
        'codeintel_database_dir',
        'codeintel_enabled_languages',
        'codeintel_syntax_map'
    ]

    # these settings can be overriden "per language"
    OVERRIDE_SETTINGS = [
        'codeintel_exclude_scopes_from_complete_triggers',
        'codeintel_language_settings',
        'codeintel_live',
        'codeintel_max_recursive_dir_depth',
        'codeintel_scan_exclude_dir',
        'codeintel_scan_files_in_project',
        'codeintel_selected_catalogs',
        'codeintel_snippets',
        'codeintel_tooltips',
        'codeintel_word_completions'
    ]

    def __init__(self):
        self._settings = {}
        self.language_settings = {}
        self.settings_id = None
        self.projectfile_mtime = 0
        self.needs_update = True
        self.ALL_SETTINGS = list(self.CORE_SETTINGS + self.OVERRIDE_SETTINGS)
        self.user_settings_file = None
        self.sublime_settings_file = None
        self.sublime_auto_complete = None
        self.project_file_names = {}

    def loadSublimeSettings(self):
        self.sublime_settings_file = sublime.load_settings('Preferences.sublime-settings')
        self.sublime_auto_complete = self.sublime_settings_file.get('auto_complete')

    def project_data(self):
        """
        ST2/ST3-compatible wrapper for getting the project data for a window as a dictionary, made possible with
        titoBouzout's getProjectFile method in SideBarEnhancements (refactored to project_data)
        """
        window = sublime.active_window()
        if not window:
            return
        if hasattr(window, 'project_data'):
            return window.project_data()
        # get the project file, returning None if it doesn't exist, just like ST3's get_project_file()
        project_file_name = self.project_file_name()
        if not project_file_name:
            return
        # read the project json file
        try:
            with open(project_file_name) as fp:
                return json.load(fp, strict=False)
        except IOError:
            pass

    def _check_project_file_name(self, folders, session_filename):
        try:
            with open(session_filename) as fp:
                data = json.load(fp, strict=False)
        except IOError:
            return
        try:
            projects = data['workspaces']['recent_workspaces']
        except KeyError:
            return

        for project_file_name in projects:
            try:
                with open(project_file_name) as fp:
                    project_json = json.load(fp, strict=False)
            except IOError:
                pass
            else:
                project_path = os.path.dirname(project_file_name)
                try:
                    project_folders = set(os.path.realpath(os.path.join(project_path, f['path'])) for f in project_json['folders'])
                except KeyError:
                    pass
                else:
                    if project_folders == folders:
                        return project_file_name

    def project_file_name(self):
        """
        ST2/ST3-compatible wrapper for getting the project file for a window, made possible with
        titoBouzout's getProjectFile method in SideBarEnhancements (refactored to project_file_name)
        """
        window = sublime.active_window()
        if not window:
            return
        if hasattr(window, 'project_file_name'):
            return window.project_file_name()
        wid = window.id()
        now = time.time()
        try:
            project_file_name, before = self.project_file_names[wid]
            if now > before + 10:  # Invalidate every 10 seconds
                raise KeyError
        except KeyError:
            pass
        folders = window.folders()
        if not folders:
            return
        settings_path = os.path.normpath(os.path.join(sublime.packages_path(), '..', 'Settings'))

        folders = set(os.path.realpath(f) for f in folders)

        session_filename = os.path.join(settings_path, 'Session.sublime_session')
        project_file_name = self._check_project_file_name(folders, session_filename)

        # if not project_file_name:
        #     session_filename = os.path.join(settings_path, 'Auto Save Session.sublime_session')
        #     project_file_name = self._check_project_file_name(folders, session_filename)

        self.project_file_names[wid] = project_file_name, now
        return project_file_name

    def get(self, config_key, default=None, language=None):
        if language is not None:
            if language in self.language_settings:
                return self.language_settings[language].get(config_key, default)
            else:
                # special case for "codeintel_live"
                # if language has no specific setting but is enabled, take the
                # general setting
                if config_key is "codeintel_live":
                    if self._settings.get("codeintel_live"):
                        return language in self._settings["codeintel_enabled_languages"]

        return self._settings.get(config_key, default)

    def getSettings(self, lang=None):
        self.update()
        return self._settings if (lang is None or lang not in self.language_settings) else self.language_settings[lang]

    def load_relevant_settings(self):
        settings = {}

        # load ALL_SETTINGS from *.sublime-settings file
        for setting_name in self.ALL_SETTINGS:
            if self.user_settings_file.get(setting_name) is not None:
                settings[setting_name] = self.user_settings_file.get(setting_name)

        # override basic plugin settings with settings from .sublime-project file
        project_file_content = self.project_data()
        if project_file_content is not None and "codeintel_settings" in project_file_content:
            for setting_name in self.ALL_SETTINGS:
                if setting_name in project_file_content["codeintel_settings"]:
                    settings[setting_name] = project_file_content["codeintel_settings"][setting_name]

        return settings

    def settings_changed(self):
        self.setChangeCallbackToSettingsFile()
        self.needs_update = True

    def needsUpdate(self):
        sublime_project_filename = self.project_file_name()

        if sublime_project_filename is not None:
            # check if project-file changed
            projectfile_mtime = os.stat(sublime_project_filename)[stat.ST_MTIME]
            if self.projectfile_mtime != projectfile_mtime:
                self.needs_update = True
                self.projectfile_mtime = projectfile_mtime

        return self.needs_update

    def update(self):
        if self.sublime_auto_complete is None:
            self.loadSublimeSettings()

        if self.user_settings_file is None:
            self.user_settings_file = sublime.load_settings(self.SETTINGS_FILE_NAME + '.sublime-settings')
            # the file might not be loaded yet
            if self.user_settings_file is not None:
                self.setChangeCallbackToSettingsFile()

        if self.needsUpdate():
            self.needs_update = False
            self._settings = self.load_relevant_settings()
            self.generateSettingsId()
            self.updateLanguageSpecificSettings()

    def updateLanguageSpecificSettings(self):
        # store settings by language
        codeintel_language_settings = self._settings.get("codeintel_language_settings", [])

        for language in codeintel_language_settings:
            lang_settings = dict(list(self._settings.items()) + list(codeintel_language_settings.get(language).items()))
            # reinforce core settings / override not permitted!
            for core_setting in self.CORE_SETTINGS:
                lang_settings[core_setting] = self._settings.get(core_setting, None)

            self.language_settings[language] = lang_settings

    def generateSettingsId(self):
        self._settings_id = hash(time.time() + self.projectfile_mtime)

    def setChangeCallbackToSettingsFile(self):
        self.user_settings_file.clear_on_change(self.SETTINGS_FILE_NAME)
        self.user_settings_file.add_on_change(self.SETTINGS_FILE_NAME, self.settings_changed)

settings_manager = SettingsManager()


# make sure all settings could be loaded and sublime is ready
def codeintel_enabled(view=None, default=False):
    return settings_manager.sublime_auto_complete is not None


def format_completions_by_language(cplns, language, text_in_current_line, trigger):
    function = None if 'import ' in text_in_current_line else 'function'
    if language == "PHP":
        if not trigger or trigger.name != "php-complete-object-members":
            return [('%s〔%s〕' % (('$' if t == 'variable' else '') + n, t), (('$' if t == 'variable' else '') + n).replace("$", "\\$") + ('($0)' if t == function else '')) for t, n in cplns]
        else:
            return [('%s〔%s〕' % (n, t), (n).replace("$", "\\$") + ('($0)' if t == function else '')) for t, n in cplns]
    else:
        return [('%s〔%s〕' % (n, t), (n).replace("$", "\\$") + ('($0)' if t == function else '')) for t, n in cplns]


class PythonCodeIntel(sublime_plugin.EventListener):
    def on_activated(self, view):
        # possibly the project was changed
        settings_manager.update()
        # print(settings_manager.get("codeintel_database_dir"))

    # rescan a buffer on_pre_save, if it is dirty
    def on_pre_save(self, view):
        if view.is_dirty():
            path = view.file_name()
            content = view.substr(sublime.Region(0, view.size()))
            lang = guess_lang(view)
            codeintel_scan(view, path, content, lang)

    def on_close(self, view):
        vid = view.id()
        if vid in completions:
            del completions[vid]
        if vid in languages:
            del languages[vid]
        codeintel_cleanup(view.file_name())

    def on_modified(self, view):
        view_sel = view.sel()
        if not view_sel:
            return

        settings_manager.update()
        if not codeintel_enabled():
            return

        sublime_scope = getSublimeScope(view)
        path = view.file_name()
        lang = guess_lang(view, path, sublime_scope)
        if not lang:
            return

        exclude_scopes = settings_manager.get("codeintel_exclude_scopes_from_complete_triggers", language=lang, default=[])

        for exclude_scope in exclude_scopes:
            if exclude_scope in sublime_scope:
                return

        if not lang or lang.lower() not in [l.lower() for l in settings_manager.get('codeintel_enabled_languages', [])]:
            # restore the original sublime auto_complete settings from Preferences.sublime-settings file in User package
            # this is for files with mixed languages (HTML/PHP)
            view.settings().set('auto_complete', settings_manager.sublime_auto_complete)
            # if live completion is disabled, we're wrong here!
            return

        if lang.lower() not in [l.lower() for l in settings_manager.get('codeintel_enabled_languages', [])]:
            return

        # disable sublime's auto_complete for now / this is for files with
        # mixed languages (HTML/PHP)
        view.settings().set('auto_complete', False)

        sel = view_sel[0]
        pos = sel.end()
        next_char = view.substr(sublime.Region(pos - 1, pos))

        if next_char == '\n':
            return

        is_fill_char = next_char and next_char in cpln_fillup_chars.get(lang, '')
        is_stop_char = next_char and next_char in cpln_stop_chars.get(lang, '')

        # Stop characters hide autocomplete window
        if is_stop_char:
            hide_auto_complete(view)

        command_history = getattr(view, 'command_history', None)
        if command_history:
            redo_command = command_history(1)
            previous_command = view.command_history(0)
            before_previous_command = view.command_history(-1)
        else:
            redo_command = previous_command = before_previous_command = None

        # print('on_modified', "'%s'" % current_char, redo_command, previous_command, before_previous_command)
        if not command_history or redo_command[1] is None and (
            previous_command[0] == 'paste' or
            previous_command[0] == 'insert' and previous_command[1]['characters'][-1] not in ('\n', '\t') or
            previous_command[0] == 'insert_snippet' and previous_command[1]['contents'] == '($0)' or
            before_previous_command[0] in ('insert', 'paste') and (
                previous_command[0] == 'commit_completion' or
                previous_command[0] == 'insert_completion' or
                previous_command[0] == 'insert_best_completion'
            )
        ):
            if previous_command[0] == 'commit_completion':
                forms = ('calltips',)
            else:
                forms = ('calltips', 'cplns')

            # fast trigger word completions from buffer
            if not is_fill_char and not is_stop_char:
                codeintel_word_completions = settings_manager.get('codeintel_word_completions', language=lang)
                if codeintel_word_completions in ['buffer', 'all']:
                    triggerWordCompletions(view, lang, codeintel_word_completions)

            # will queue an autocomplete job
            autocomplete(view, 0, 50, forms, True, args=[path, pos, lang], kwargs={'caller': 'on_modified'})
        else:
            hide_auto_complete(view)

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
                set_status(view, "", lid=vid)

    def on_query_completions(self, view, prefix, locations):
        vid = view.id()

        lang = guess_lang(view)
        if not lang or lang.lower() not in [l.lower() for l in settings_manager.get('codeintel_enabled_languages', [])]:
            # lang is not ci enabled. Dont mess with the default completions!
            return []

        # add sublime completions to the mix / not recomended
        sublime_word_completions = False
        sublime_explicit_completions = False

        word_completions = 0
        explicit_completions = 0

        _completions = []
        if vid in completions:

            on_query_info = completions[vid]
            completion_type, add_word_completions, text_in_current_line, lang, trigger, sublime_explicit_completions = on_query_info['params']
            cplns = on_query_info['cplns']
            del completions[vid]

            word_completions = 0 if sublime_word_completions and len(prefix) != 0 else sublime.INHIBIT_WORD_COMPLETIONS
            explicit_completions = 0 if sublime_explicit_completions else sublime.INHIBIT_EXPLICIT_COMPLETIONS

            if completion_type == 'tooltips':
                return (cplns, sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)

            if completion_type == 'cplns':
                if cplns is not None:
                    _completions = format_completions_by_language(cplns, lang, text_in_current_line, trigger)

                if add_word_completions in ['buffer', 'all']:
                    wordsFromBufferMgr = WordCompletionsFromBuffer()
                    word_completions_from_buffer = wordsFromBufferMgr.getCompletions(view, prefix, locations, add_word_completions)
                    if cplns is not None:
                        # remove buffer completions that are already in
                        # codeintel completions
                        def extendForLanguages(n, lang):
                            for i in n:
                                yield i[1]
                                if lang == 'PHP':
                                    yield "$" + i[1]
                        cplns_list = [i for i in extendForLanguages(cplns, lang)]
                        word_completions_from_buffer = [x for x in word_completions_from_buffer if x[0] not in cplns_list]

                    _completions = list(_completions + word_completions_from_buffer)

        # is the sorting actually doing anything??
        return (sorted(_completions, key=lambda o: o[1], reverse=False), word_completions | explicit_completions)


class CodeIntelAutoComplete(sublime_plugin.TextCommand):
    def run(self, edit, block=False):
        view = self.view
        view_sel = view.sel()
        if not view_sel:
            return

        settings_manager.update()
        if not codeintel_enabled():
            return

        sublime_scope = getSublimeScope(view)
        path = view.file_name()
        lang = guess_lang(view, path, sublime_scope)
        if not lang:
            return

        sel = view_sel[0]
        pos = sel.end()
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

            def _trigger(trigger, citdl_expr, defns):
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


class SublimecodeintelDumpImportDirs(sublime_plugin.WindowCommand):
    def run(self):
        settings_manager.update()
        if not codeintel_enabled():
            return

        codeintel_database_dir = os.path.expanduser(settings_manager.get('codeintel_database_dir'))
        db_dir = os.path.join(codeintel_database_dir, 'db')

        stat_dir = os.path.join(codeintel_database_dir, 'import_dir_stats')
        if not os.path.exists(stat_dir):
            os.makedirs(stat_dir)

        def get_immediate_subdirectories(a_dir):
            for subdirname in os.listdir(a_dir):
                dirname = os.path.join(a_dir, subdirname)
                if os.path.isdir(dirname):
                    yield (dirname, subdirname)

        for lib_dir in [lib_dir for lib_dir in get_immediate_subdirectories(db_dir)]:
            if lib_dir[1] != 'stdlibs':
                lang = lib_dir[1]
                import_dirs = []
                hash_map = {}
                for lib_dir_entry in get_immediate_subdirectories(lib_dir[0]):
                    try:
                        pathfile_path = os.path.join(lib_dir_entry[0], 'path')
                        path_file = open(pathfile_path)
                        import_dir = path_file.read()
                        import_dirs.append(import_dir)
                        hash_map[import_dir] = lib_dir_entry[1]
                    except:
                        pass

                stat_file = open(os.path.join(stat_dir, lang), 'w')
                for item in sorted(import_dirs, key=str.lower):
                    stat_file.write("%s %s\n" % (hash_map[item], item))


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
        settings_manager.getSettings()
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
    def is_enabled(self, *args):
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

            print("WINDOW COMMAND ENABLED %s" % enabled)
        return bool(enabled)

    def run_(self, args={}):
        view = self.window.active_view()
        action = args.get('action', '')

        if view and action:
            view.run_command('codeintel', action)


class SublimecodeintelEnableCommand(SublimecodeintelCommand):
    def is_enabled(self, *args):
        return super(SublimecodeintelEnableCommand, self).is_enabled(False)


class SublimecodeintelDisableCommand(SublimecodeintelCommand):
    def is_enabled(self, *args):
        return super(SublimecodeintelDisableCommand, self).is_enabled(True)


class SublimecodeintelResetCommand(SublimecodeintelCommand):
    def is_enabled(self, *args):
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
    def is_enabled(self, *args):
        return super(SublimecodeintelEnableLiveCommand, self).is_enabled(False, False)


class SublimecodeintelDisableLiveCommand(SublimecodeintelLiveCommand):
    def is_enabled(self, *args):
        return super(SublimecodeintelDisableLiveCommand, self).is_enabled(True, False)


class SublimecodeintelEnableLiveLangCommand(SublimecodeintelLiveCommand):
    def is_enabled(self, *args):
        return super(SublimecodeintelEnableLiveLangCommand, self).is_enabled(False, True)


class SublimecodeintelDisableLiveLangCommand(SublimecodeintelLiveCommand):
    def is_enabled(self, *args):
        return super(SublimecodeintelDisableLiveLangCommand, self).is_enabled(True, True)
