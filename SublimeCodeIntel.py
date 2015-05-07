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
# The Original Code is SublimeCodeIntel code by German M. Bravo (Kronuz).
#
# Contributor(s):
#   ActiveState Software Inc
#
# Portions created by ActiveState Software Inc are Copyright (C) 2000-2007
# ActiveState Software Inc. All Rights Reserved.
#
"""
CodeIntel is a plugin intended to display "code intelligence" information.
The plugin is based in code from the Open Komodo Editor and has a MPL license.
Port by German M. Bravo (Kronuz). 2011-2015

"""
from __future__ import absolute_import, unicode_literals, print_function

VERSION = "3.0.0"

codeintel_syntax_map = {
    "Python Django": "Python",
}


import os
import sys

__file__ = os.path.normpath(os.path.abspath(__file__))
__path__ = os.path.dirname(__file__)

python_sitelib_path = os.path.normpath(__path__)
if python_sitelib_path not in sys.path:
    sys.path.insert(0, python_sitelib_path)

import re
import logging
import textwrap
import threading
import collections

import sublime
import sublime_plugin

from codeintel import CodeIntel, CodeIntelBuffer

logger_name = 'CodeIntel'
logger = logging.getLogger(logger_name)
logger.setLevel(logging.INFO)  # INFO

handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(logging.Formatter("%(name)s: %(levelname)s: %(message)s"))
logger.handlers = [handler]


class CodeIntelHandler(object):
    HISTORY_SIZE = 64
    jump_history_by_window = {}  # map of window id -> collections.deque([], HISTORY_SIZE)

    status_msg = {}
    status_lineno = {}
    status_lock = threading.Lock()

    def __init__(self, *args, **kwargs):
        self.log = logging.getLogger(logger_name + '.' + self.__class__.__name__)
        super(CodeIntelHandler, self).__init__(*args, **kwargs)
        ci.add_observer(self)

    @property
    def window(self):
        if hasattr(self, '_window'):
            return self._window
        window = sublime.active_window()
        if window:
            return window

    @window.setter
    def window(self, value):
        self._window = value

    @property
    def view(self):
        if hasattr(self, '_view'):
            return self._view
        window = self.window
        if window:
            view = window.active_view()
            if view:
                return view

    @view.setter
    def view(self, value):
        self._view = value

    def set_status(self, ltype, msg=None, timeout=None, delay=0, lid='SublimeCodeIntel', logger_obj=None):
        view = self.view
        if not view:
            return

        if timeout is None:
            timeout = {'error': 3000, 'warning': 5000, 'info': 10000,
                       'event': 10000}.get(ltype, 3000)

        if msg is None:
            msg, ltype = ltype, 'info'
        if isinstance(msg, tuple):
            try:
                msg = msg[0] % msg[1:]
            except:
                msg = repr(msg)
        msg = msg.strip()

        CodeIntelHandler.status_lock.acquire()
        try:
            CodeIntelHandler.status_msg.setdefault(lid, [None, None, 0])
            if msg == CodeIntelHandler.status_msg[lid][1]:
                return
            CodeIntelHandler.status_msg[lid][2] += 1
            order = CodeIntelHandler.status_msg[lid][2]
        finally:
            CodeIntelHandler.status_lock.release()

        def _set_status():
            is_warning = 'warning' in lid
            if not is_warning:
                view_sel = view.sel()
                lineno = view.rowcol(view_sel[0].end())[0] if view_sel else 0
            CodeIntelHandler.status_lock.acquire()
            try:
                current_type, current_msg, current_order = CodeIntelHandler.status_msg.get(lid, [None, None, 0])
                if msg != current_msg and order == current_order:
                    _logger_obj = getattr(logger, ltype, None) if logger_obj is None else logger_obj
                    if _logger_obj:
                        _logger_obj(msg)
                    if ltype != 'debug':
                        view.set_status(lid, "%s %s: %s" % (lid, ltype.capitalize(), msg.rstrip('.')))
                        CodeIntelHandler.status_msg[lid] = [ltype, msg, order]
                    if not is_warning:
                        CodeIntelHandler.status_lineno[lid] = lineno
            finally:
                CodeIntelHandler.status_lock.release()

        def _erase_status():
            CodeIntelHandler.status_lock.acquire()
            try:
                if msg == CodeIntelHandler.status_msg.get(lid, [None, None, 0])[1]:
                    view.erase_status(lid)
                    CodeIntelHandler.status_msg[lid][1] = None
                    if lid in CodeIntelHandler.status_lineno:
                        del CodeIntelHandler.status_lineno[lid]
            finally:
                CodeIntelHandler.status_lock.release()

        if msg:
            sublime.set_timeout(_set_status, delay or 0)
            sublime.set_timeout(_erase_status, timeout)
        else:
            sublime.set_timeout(_erase_status, delay or 0)

    def pos2bytes(self, content, pos):
        return len(content[:pos].encode('utf-8'))

    def guess_language(self, view, path):
        lang = os.path.splitext(os.path.basename(view.settings().get('syntax')))[0]
        lang = codeintel_syntax_map.get(lang, lang)
        return lang

    def buf_from_view(self, view):
        if not view:
            return None

        view_sel = view.sel()
        if not view_sel:
            return None

        file_name = view.file_name()
        path = file_name if file_name else "<Unsaved>"

        lang = self.guess_language(view, path)
        if not lang or lang not in ci.languages:
            return None

        logger.debug("buf_from_view: %r, %r, %r", view, path, lang)

        vid = view.id()
        try:
            buf = ci.buffers[vid]
        except KeyError:
            logger.debug("creating new %s document %s", lang, path)
            buf = CodeIntelBuffer(ci, vid=vid)
            ci.buffers[vid] = buf

        sel = view_sel[0]
        original_pos = sel.end()
        lpos = view.line(sel).begin()

        text_in_current_line = view.substr(sublime.Region(lpos, original_pos + 1))
        text = view.substr(sublime.Region(0, view.size()))

        # Get encoded content and current position
        pos = self.pos2bytes(text, original_pos)

        buf.lang = lang
        buf.path = path
        buf.text = text
        buf.pos = pos
        buf.text_in_current_line = text_in_current_line
        buf.original_pos = original_pos

        window = sublime.active_window()
        extra_paths = os.pathsep.join(window.folders())

        javascriptExtraPaths = extra_paths
        nodejsExtraPaths = extra_paths
        perlExtraPaths = extra_paths
        phpExtraPaths = extra_paths
        python3ExtraPaths = extra_paths
        pythonExtraPaths = extra_paths
        rubyExtraPaths = extra_paths

        buf.prefs = {
            'codeintel_max_recursive_dir_depth': 10,
            'codeintel_scan_files_in_project': True,
            'codeintel_selected_catalogs': [],
            'defaultHTML5Decl': '-//W3C//DTD HTML 5//EN',
            'defaultHTMLDecl': '-//W3C//DTD HTML 5//EN',
            'javascriptExtraPaths': javascriptExtraPaths,
            'nodejsDefaultInterpreter': '',
            'nodejsExtraPaths': nodejsExtraPaths,
            'perl': '',
            'perlExtraPaths': perlExtraPaths,
            'php': '',
            'phpConfigFile': '',
            'phpExtraPaths': phpExtraPaths,
            'python': '',
            'python3': '',
            'python3ExtraPaths': python3ExtraPaths,
            'pythonExtraPaths': pythonExtraPaths,
            'ruby': '',
            'rubyExtraPaths': rubyExtraPaths,
        }

        return buf

    def format_completions_by_language(self, cplns, language, text_in_current_line, type):
        function = None if 'import ' in text_in_current_line else 'function'
        get_name = lambda c: c[1]
        get_type = lambda c: c[0].title()
        if language == 'PHP' and type != 'php-complete-object-members':
            get_name = lambda c: ('$' + c[1]) if c[0] == 'variable' else c[1]
        return [('%s\t〔%s〕' % (get_name(c), get_type(c)), get_name(c).replace("$", "\\$") + ('($0)' if c[0] == function else '')) for c in cplns]

    # Handlers follow

    def on_document_scanned(self, buf):
        """Handler callback for scan_document"""

    def on_get_calltip_range(self, buf, start, end):
        pass

    def on_trg_from_pos(self, buf, context, trg):
        if context == 'trg_from_pos':
            buf.async_eval_at_trg(self, trg)
        elif context == 'defn_trg_from_pos':
            buf.async_eval_at_trg(self, trg)

    def set_status_message(self, buf, message, highlight=None):
        def _set_status_message():
            self.set_status(message)
        sublime.set_timeout(_set_status_message, 0)

    def set_call_tip_info(self, buf, calltip, explicit, trg):
        def _set_call_tip_info():
            view = self.view
            if not view:
                return
            vid = view.id()
            if vid != buf.vid:
                return

            # TODO: This snippets are created and work for Python language def functions.
            # i.e. in the form: name(arg1, arg2, arg3)
            # Other languages might need different treatment.

            # Figure out how many arguments are there already:
            text_in_current_line = buf.text_in_current_line[:-1]  # Remove next char after cursor
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

            # Insert parameters as snippet:
            snippet = None
            tip_info = calltip.split('\n')
            tip0 = tip_info[0]
            m = re.search(r'^(.*\()([^\[\(\)]*)(.*)$', tip0)
            if m:
                params = [p.strip() for p in m.group(2).split(',')]
                if params:
                    n = 1
                    tip0 = []
                    snippet = []
                    for i, p in enumerate(params):
                        if p:
                            var, sep, default = p.partition('=')
                            var = var.strip()
                            tvar = var
                            if sep:
                                tvar = "%s<i>=%s</i>" % (tvar, default)
                            # if i == arguments:
                            #     tvar = "<b>%s</b>" % tvar
                            tip0.append(tvar)
                            if i >= arguments:
                                if ' ' in var:
                                    var = var.split(' ')[1]
                                if var[0] == '$':
                                    var = var[1:]
                                snippet.append('${%s:%s}' % (n, var))
                                n += 1
                    tip0 = "<h1>%s%s%s</h1>" % (m.group(1), ', '.join(tip0), m.group(3))
                    snippet = ', '.join(snippet)
                    if arguments and snippet:
                        snippet = initial_separator + snippet
            css = (
                "html {background-color: #232628; color: #999999;}" +
                "body {font-size: 10px; }" +
                "b {color: #6699cc; }" +
                "a {color: #99cc99; }" +
                "h1 {color: #cccccc; font-weight: normal; font-size: 11px; }"
            )

            # Wrap lines that are too long:
            wrapper = textwrap.TextWrapper(width=100, break_on_hyphens=False, break_long_words=False)
            measured_tips = [tip0]
            for t in tip_info[1:]:
                measured_tips.extend(wrapper.wrap(t))

            if hasattr(view, 'show_popup'):
                def insert_snippet(href):
                    view.run_command('insert_snippet', {'contents': snippet})
                    view.hide_popup()

                view.show_popup('<style>%s</style>%s<br><br><a href="insert">insert</a>' % (css, "<br>".join(measured_tips)), location=-1, max_width=700, on_navigate=insert_snippet)

            else:
                # Insert tooltip snippet
                padding = '   '
                snippets = [((padding if i > 0 else '') + l + (padding if i > 0 else ''), snippet or '${0}') for i, l in enumerate(measured_tips)]

                buf.cplns = snippets or None
                if buf.cplns:
                    view.run_command('auto_complete', {
                        'disable_auto_insert': True,
                        'api_completions_only': True,
                        'next_completion_if_showing': False,
                        'auto_complete_commit_on_tab': True,
                    })
        sublime.set_timeout(_set_call_tip_info, 0)

    def set_auto_complete_info(self, buf, cplns, trg):
        def _set_auto_complete_info():
            view = self.view
            if not view:
                return
            vid = view.id()
            if vid != buf.vid:
                return

            _cplns = self.format_completions_by_language(cplns, buf.lang, buf.text_in_current_line, trg.get('type'))

            buf.cplns = _cplns or None
            if buf.cplns:
                view.run_command('auto_complete', {
                    'disable_auto_insert': True,
                    'api_completions_only': True,
                    'next_completion_if_showing': False,
                    'auto_complete_commit_on_tab': True,
                })
        sublime.set_timeout(_set_auto_complete_info, 0)

    def set_definitions_info(self, buf, defns, trg):
        def _set_definitions_info():
            view = self.view

            view_sel = view.sel()
            if not view_sel:
                return

            file_name = view.file_name()
            path = file_name if file_name else "<Unsaved>"

            defn = defns[0]
            row, col = defn['line'], 1
            path = defn['path']
            if not path:
                msg = "Cannot jump to definition!"
                logger.debug(msg)
                return

            jump_location = "%s:%s:%s" % (path, row, col)
            msg = "Jumping to: %s" % jump_location
            logger.debug(msg)

            window = sublime.active_window()
            wid = window.id()
            if wid not in CodeIntelHandler.jump_history_by_window:
                CodeIntelHandler.jump_history_by_window[wid] = collections.deque([], CodeIntelHandler.HISTORY_SIZE)
            jump_history = CodeIntelHandler.jump_history_by_window[wid]

            # Save current position so we can return to it
            row, col = view.rowcol(view_sel[0].begin())
            current_location = "%s:%d:%d" % (file_name, row + 1, col + 1)
            jump_history.append(current_location)

            window.open_file(jump_location, sublime.ENCODED_POSITION)
            window.open_file(jump_location, sublime.ENCODED_POSITION)
        sublime.set_timeout(_set_definitions_info, 0)


class SublimeCodeIntel(CodeIntelHandler, sublime_plugin.EventListener):
    def observer(self, topic, data):
        def _observer():
            if topic == 'progress':
                message = data.get('message')
                progress = data.get('progress')
                if message:
                    message = "%s - %s%% / %s%%" % (message, progress, 100)
                else:
                    message = "%s%% / %s%%" % (progress, 100)
                self.set_status('info', message, lid='SublimeCodeIntel Notification')
            elif topic == 'status_message':
                message = data.get('message')
                if message:
                    self.set_status('info', message, lid='SublimeCodeIntel Notification')
            elif topic == 'error_message':
                message = data.get('message')
                if message:
                    self.set_status('error', message, lid='SublimeCodeIntel Notification')
            elif 'codeintel_buffer_scanned':
                pass
        sublime.set_timeout(_observer, 0)

    def on_pre_save(self, view):
        if view.is_dirty():
            buf = self.buf_from_view(view)
            if buf:
                buf.scan_document(self, True)

    def on_close(self, view):
        vid = view.id()
        ci.buffers.pop(vid, None)

    def on_modified(self, view):
        view_sel = view.sel()
        if not view_sel:
            return

        sel = view_sel[0]
        pos = sel.end()
        current_char = view.substr(sublime.Region(pos - 1, pos))

        if not current_char or current_char in ('\n', '\t'):
            return

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
            buf = self.buf_from_view(view)
            if buf:
                is_stop_char = current_char in buf.cpln_stop_chars

                # Stop characters hide autocomplete window
                if is_stop_char:
                    view.run_command('hide_auto_complete')

                buf.scan_document(self, True)
                buf.trg_from_pos(self, True)

    def on_selection_modified(self, view):
        pass

    def on_query_completions(self, view, prefix, locations):
        buf = self.buf_from_view(view)
        if not buf:
            return
        cplns, buf.cplns = getattr(buf, 'cplns', None), None
        return cplns


class GotoPythonDefinition(CodeIntelHandler, sublime_plugin.TextCommand):
    def run(self, edit, block=False):
        view = self.view

        buf = self.buf_from_view(view)
        if buf:
            buf.scan_document(self, True)
            buf.defn_trg_from_pos(self)


class BackToPythonDefinition(sublime_plugin.TextCommand):
    def run(self, edit, block=False):

        window = sublime.active_window()
        wid = window.id()
        if wid in CodeIntelHandler.jump_history_by_window:
            jump_history = CodeIntelHandler.jump_history_by_window[wid]

            if len(jump_history) > 0:
                previous_location = jump_history.pop()
                window = sublime.active_window()
                window.open_file(previous_location, sublime.ENCODED_POSITION)


ci = CodeIntel()
ci.activate()
