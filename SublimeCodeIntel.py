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
Port by German M. Bravo (Kronuz). 2011-2017

"""
from __future__ import absolute_import, unicode_literals, print_function

NAME = "SublimeCodeIntel"
VERSION = "3.0.0-beta.37"

import os
import re
import logging
import textwrap
import threading
from collections import deque

import sublime
import sublime_plugin

from .libs.codeintel import CodeIntel, CodeIntelBuffer, logger as codeintel_logger, logger_level as codeintel_logger_level
from .settings import Settings, SettingTogglerCommandMixin

logger_name = 'CodeIntel'
logger_level = logging.WARNING  # WARNING

logger = logging.getLogger(logger_name)
logger.setLevel(logger_level)
if logger.root.handlers:
    logger.root.handlers[0].setFormatter(logging.Formatter("%(name)s: %(levelname)s: %(message)s"))


EXTRA_PATHS_MAP = {
    'ECMAScript': 'ecmascriptExtraPaths',
    'JavaScript': 'javascriptExtraPaths',
    'Node.js': 'nodejsExtraPaths',
    'Perl': 'perlExtraPaths',
    'PHP': 'phpExtraPaths',
    'Python3': 'python3ExtraPaths',
    'Python': 'pythonExtraPaths',
    'Ruby': 'rubyExtraPaths',
    'C++': 'cppExtraPaths',
}

EXCLUDE_PATHS_MAP = {
    'ECMAScript': 'ecmascriptExcludePaths',
    'JavaScript': 'javascriptExcludePaths',
    'Node.js': 'nodejsExcludePaths',
    'Perl': 'perlExcludePaths',
    'PHP': 'phpExcludePaths',
    'Python3': 'python3ExcludePaths',
    'Python': 'pythonExcludePaths',
    'Ruby': 'rubyExcludePaths',
    'C++': 'cppExcludePaths',
}


class CodeintelHandler(object):
    HISTORY_SIZE = 64
    MAX_FILESIZE = 1 * 1024 * 1024   # 1MB
    jump_history_by_window = {}  # map of window id -> deque([], HISTORY_SIZE)

    status_msg = {}
    status_lineno = {}
    status_lock = threading.Lock()

    def __init__(self, *args, **kwargs):
        self.log = logging.getLogger(logger_name + '.' + self.__class__.__name__)
        super(CodeintelHandler, self).__init__(*args, **kwargs)
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
            timeout = {'critical': 3000, 'error': 3000, 'warning': 5000, 'info': 10000, 'debug': 10000,
                       'event': 10000}.get(ltype, 3000)

        if msg is None:
            msg, ltype = ltype, 'info'
        if isinstance(msg, tuple):
            try:
                msg = msg[0] % msg[1:]
            except:
                msg = repr(msg)
        msg = msg.strip()

        CodeintelHandler.status_lock.acquire()
        try:
            CodeintelHandler.status_msg.setdefault(lid, [None, None, 0])
            if msg == CodeintelHandler.status_msg[lid][1]:
                return
            CodeintelHandler.status_msg[lid][2] += 1
            order = CodeintelHandler.status_msg[lid][2]
        finally:
            CodeintelHandler.status_lock.release()

        def _set_status():
            is_warning = 'warning' in lid
            if not is_warning:
                view_sel = view.sel()
                lineno = view.rowcol(view_sel[0].end())[0] if view_sel else 0
            CodeintelHandler.status_lock.acquire()
            try:
                current_type, current_msg, current_order = CodeintelHandler.status_msg.get(lid, [None, None, 0])
                if msg != current_msg and order == current_order:
                    _logger_obj = getattr(logger, ltype, None) if logger_obj is None else logger_obj
                    if _logger_obj:
                        _logger_obj(msg)
                    if ltype != 'debug':
                        view.set_status(lid, "%s %s: %s" % (lid, ltype.capitalize(), msg.rstrip('.')))
                        CodeintelHandler.status_msg[lid] = [ltype, msg, order]
                    if not is_warning:
                        CodeintelHandler.status_lineno[lid] = lineno
            finally:
                CodeintelHandler.status_lock.release()

        def _erase_status():
            CodeintelHandler.status_lock.acquire()
            try:
                if msg == CodeintelHandler.status_msg.get(lid, [None, None, 0])[1]:
                    view.erase_status(lid)
                    CodeintelHandler.status_msg[lid][1] = None
                    if lid in CodeintelHandler.status_lineno:
                        del CodeintelHandler.status_lineno[lid]
            finally:
                CodeintelHandler.status_lock.release()

        if msg:
            sublime.set_timeout(_set_status, delay or 0)
            sublime.set_timeout(_erase_status, timeout)
        else:
            sublime.set_timeout(_erase_status, delay or 0)

    def pos2bytes(self, content, pos):
        return len(content[:pos].encode('utf-8'))

    def guess_language(self, view, path):
        language = os.path.splitext(os.path.basename(view.settings().get('syntax')))[0]
        lang = settings.get('syntax_map', {}).get(language, language)
        logger.info("Language guessed: %s (for %s)", lang, language)
        if lang in settings.get('disabled_languages', []):
            return
        if settings.get('@disable', False, lang=lang):
            return
        return lang

    def buf_from_view(self, view):
        if not view:
            return

        view_sel = view.sel()
        if not view_sel:
            return

        file_name = view.file_name()
        path = file_name if file_name else "<Unsaved>"

        lang = self.guess_language(view, path)
        if not lang or lang not in ci.languages:
            logger.debug("buf_from_view: %r, %r? no: language unavailable in: [%s]", path, lang, ", ".join(ci.languages))
            return

        if not settings.get('live', False, lang=lang):
            logger.debug("buf_from_view: %r, %r? no: live disabled", path, lang)
            return

        view_size = view.size()
        if view.size() > self.MAX_FILESIZE:
            logger.warn("File %r has size greater than 1MB (%d)", path, view_size)
            return

        logger.debug("buf_from_view: %r, %r? yes", path, lang)

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
        text = view.substr(sublime.Region(0, view_size))

        # Get encoded content and current position
        pos = self.pos2bytes(text, original_pos)

        buf.lang = lang
        buf.path = path
        buf.text = text
        buf.pos = pos
        buf.text_in_current_line = text_in_current_line
        buf.original_pos = original_pos

        prefs = settings.get_prefs(lang)

        if settings.get('scan_files_in_project', lang=lang):
            window = sublime.active_window()
            extra_paths_name = EXTRA_PATHS_MAP.get(lang)
            extra_paths = prefs.get(extra_paths_name, '').split(os.pathsep)
            exclude_paths_name = EXCLUDE_PATHS_MAP.get(lang)
            exclude_paths = prefs.get(exclude_paths_name, '').split(os.pathsep)
            for f in window.folders():
                f = os.path.normcase(os.path.normpath(f)).rstrip(os.sep)
                if f not in exclude_paths and f not in extra_paths:
                    extra_paths.append(f)
            if extra_paths:
                prefs[extra_paths_name] = os.pathsep.join(extra_paths)

        buf.prefs = prefs

        return buf

    def format_completions_by_language(self, cplns, lang, text_in_current_line, type):
        function = None if 'import ' in text_in_current_line else 'function'

        def get_desc(c):
            return c[2] if len(c) > 2 else c[1]

        def get_name(c):
            name = c[1]
            name = name.replace("$", "\\$")
            if c[0] == function:
                name += "($0)"
            return name

        def get_type(c):
            return c[0].title()

        if lang == 'PHP' and type != 'object-members':
            def get_name(c):
                name = c[1]
                if c[0] == 'variable':
                    name = "$" + name
                name = name.replace("$", "\\$")
                if c[0] == function:
                    name += "($0)"
                return name

        if lang == 'ECMAScript':
            def get_name(c):
                name = c[1]
                name = name.replace("$", "\\$")
                if c[0] == 'attribute':
                    name += "=$0 "
                elif c[0] == function:
                    name += "($0)"
                return name

        def sorter(c):
            return {
                'import': '_',
                'attribute': '__',
                'variable': '__',
                'function': '___',
            }.get(c[0].lower(), c[0]), c[1]

        return [('%s\t〔%s〕' % (get_desc(c), get_type(c)), get_name(c)) for c in sorted(cplns, key=sorter)]

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
            if wid not in CodeintelHandler.jump_history_by_window:
                CodeintelHandler.jump_history_by_window[wid] = deque([], CodeintelHandler.HISTORY_SIZE)
            jump_history = CodeintelHandler.jump_history_by_window[wid]

            # Save current position so we can return to it
            row, col = view.rowcol(view_sel[0].begin())
            current_location = "%s:%d:%d" % (file_name, row + 1, col + 1)
            jump_history.append(current_location)

            window.open_file(jump_location, sublime.ENCODED_POSITION)
            window.open_file(jump_location, sublime.ENCODED_POSITION)
        sublime.set_timeout(_set_definitions_info, 0)

    def done(self):
        pass


class SublimeCodeIntel(CodeintelHandler, sublime_plugin.EventListener):
    def observer(self, topic, data):
        def _get_and_log_message(response):
            message = response.get('message')
            if message:
                stack = response.get('stack')
                if stack:
                    logger.error(message.rstrip() + "\n" + stack)
            return message

        def _observer():
            if topic == 'status_message':
                ltype = 'info'
            elif topic == 'error_message':
                ltype = 'error'
            elif 'codeintel_buffer_scanned':
                return
            else:
                return
            logger_obj = None
            if data.get('type') == 'logging':
                # logger_name = data.get('name')
                level = data.get('level')
                if level >= logging.CRITICAL:
                    logger_obj = logger.critical
                    ltype = 'critical'
                elif level >= logging.ERROR:
                    logger_obj = logger.error
                    ltype = 'error'
                elif level >= logging.WARNING:
                    logger_obj = logger.warn
                    ltype = 'warning'
                elif level >= logging.INFO:
                    logger_obj = logger.info
                    ltype = 'info'
                elif level >= logging.DEBUG:
                    logger_obj = logger.debug
                    ltype = 'debug'
            progress = data.get('progress') or data.get('completed')
            if progress is not None:
                total = data.get('total', 100)
                if not total:
                    progress = None
                elif total == 100:
                    progress = ("%0.1f" % progress).rstrip('.0') + "%"
                else:
                    progress = "%s/%s" % (progress, total)
            message = _get_and_log_message(data)
            if progress and message:
                message = "%s - %s" % (progress, message)
            elif progress:
                message = progress
            elif not message:
                return
            self.set_status(ltype, message, lid='SublimeCodeIntel Notification', logger_obj=logger_obj)
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

        if settings.get('@disable', False) or not settings.get('live', False):
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

        # print('on_modified', "%r\n\tcommand_history: %r\n\tredo_command: %r\n\tprevious_command: %r\n\tbefore_previous_command: %r" % (current_char, bool(command_history), redo_command, previous_command, before_previous_command))
        if not command_history or redo_command[1] is None and (
            previous_command[0] == 'insert' and previous_command[1]['characters'][-1] not in ('\n', '\t') or
            previous_command[0] in ('insert_completion', 'paste', 'codeintel_complete_commit') or
            previous_command[0] == 'insert_snippet' and previous_command[1]['contents'] in (
                '(${0:$SELECTION})', '[${0:$SELECTION}]', '{${0:$SELECTION}}', '`${0:$SELECTION}`', '"${0:$SELECTION}"', "'${0:$SELECTION}'",
                '($0)', '[$0]', '{$0}', '`$0`', '"$0"', "'$0'",
            ) or
            before_previous_command[0] in ('insert', 'paste') and (
                previous_command[0] == 'commit_completion' or
                previous_command[0] == 'insert_completion' or
                previous_command[0] == 'insert_best_completion'
            )
        ):
            buf = self.buf_from_view(view)
            # print('on_modified.triggering', bool(buf))
            if buf:
                buf.trg_from_pos(self, True)

    def on_selection_modified(self, view):
        pass

    def on_query_completions(self, view, prefix, locations):
        buf = self.buf_from_view(view)
        if buf:
            cplns, buf.cplns = getattr(buf, 'cplns', None), None
            return cplns

    def on_query_context(self, view, key, operator, operand, match_all):
        if key.startswith("codeintel.setting."):
            setting_name = key[len("codeintel.setting."):]
            value = settings.get(setting_name)
            if operator == sublime.OP_NOT_EQUAL:
                return value != operand
            elif operator == sublime.OP_EQUAL:
                return value == operand


class CodeintelAutoCompleteCommand(CodeintelHandler, sublime_plugin.TextCommand):
    def run(self, edit, block=False):
        view = self.view

        buf = self.buf_from_view(view)

        if buf:
            buf.trg_from_pos(self, True)


class CodeintelGoToDefinitionCommand(CodeintelHandler, sublime_plugin.TextCommand):
    def run(self, edit, block=False):
        view = self.view

        buf = self.buf_from_view(view)

        if buf:
            buf.defn_trg_from_pos(self)


class CodeintelBackFromDefinitionCommand(sublime_plugin.TextCommand):
    def run(self, edit, block=False):
        window = sublime.active_window()
        wid = window.id()
        if wid in CodeintelHandler.jump_history_by_window:
            jump_history = CodeintelHandler.jump_history_by_window[wid]

            if len(jump_history) > 0:
                previous_location = jump_history.pop()
                window = sublime.active_window()
                window.open_file(previous_location, sublime.ENCODED_POSITION)


class CodeintelCompleteCommitCommand(CodeintelHandler, sublime_plugin.TextCommand):
    def run(self, edit, character):
        view = self.view

        buf = self.buf_from_view(view)
        if buf:
            cpln_fillup_chars = buf.cpln_fillup_chars
            cpln_stop_chars = buf.cpln_stop_chars
        else:
            cpln_fillup_chars = ""
            cpln_stop_chars = "~`!@#$%^&*()-=+{}[]|\\;:'\",.<>?/ "

        # Fillup characters commit autocomplete
        if settings.get(buf.lang, 'complete_commit_fillup') and character in cpln_fillup_chars:
            view.window().run_command('commit_completion')
            if character not in ("(", "="):
                view.run_command('insert', {'characters': character})

        # Stop characters hide autocomplete window
        elif character in cpln_stop_chars:
            view.run_command('hide_auto_complete')
            view.run_command('insert', {'characters': character})

        else:
            view.run_command('insert', {'characters': character})


################################################################################
# Initialize settings and main objects only once

class CodeintelSettings(Settings):
    nested_settings = ('syntax_map', 'language_settings')

    def get(self, setting, default=None, lang=None):
        """Return a plugin setting, defaulting to default if not found."""
        language_settings = self.settings.get('language_settings', {}).get(lang)
        if language_settings and setting in language_settings:
            return language_settings[setting]
        return super(CodeintelSettings, self).get(setting, default)

    def on_update(self):
        """
        The previous settings are compared with the new settings; depending
        on what changed, engine will either be reconfigured or restarted.

        """
        need_deactivate = False

        for setting in ('@disable', 'command', 'oop_mode', 'log_levels'):
            if (
                setting in self.changeset or
                self.previous_settings and self.previous_settings.get(setting) != self.settings.get(setting)
            ):
                self.changeset.discard(setting)
                need_deactivate = True

        if (
            'debug' in self.changeset or
            self.previous_settings.get('debug', False) != self.settings.get('debug', False)
        ):
            self.changeset.discard('debug')

            if self.settings.get('debug'):
                logger.setLevel(logging.DEBUG)
                codeintel_logger.setLevel(logging.DEBUG)
            else:
                logger.setLevel(logger_level)
                codeintel_logger.setLevel(codeintel_logger_level)

        if need_deactivate:
            ci.deactivate()

        if not self.settings.get('@disable'):
            env = dict(os.environ)
            env.update(self.settings.get('env', {}))

            prefs = self.get_prefs()

            if ci.enabled:
                ci.mgr.set_global_environment(
                    env=env,
                    prefs=prefs,
                )
            else:
                command = self.settings.get('command')
                oop_mode = self.settings.get('oop_mode')
                log_levels = self.settings.get('log_levels')
                ci.activate(
                    reset_db_as_necessary=False,
                    codeintel_command=command,
                    oop_mode=oop_mode,
                    log_levels=log_levels,
                    env=env,
                    prefs=prefs,
                )

    def get_prefs(self, lang=None):
        prefs = {
            'codeintel_max_recursive_dir_depth': self.settings.get('max_recursive_dir_depth'),
            'codeintel_scan_files_in_project': self.settings.get('scan_files_in_project'),
            'codeintel_selected_catalogs': self.settings.get('selected_catalogs'),
        }

        disabled_languages = self.settings.get('disabled_languages', [])

        scan_extra_paths = self.settings.get('scan_extra_paths', [])
        if scan_extra_paths:
            scan_extra_paths = set(os.path.normcase(os.path.normpath(e)).rstrip(os.sep) for e in scan_extra_paths)

        scan_exclude_paths = self.settings.get('scan_exclude_paths', [])
        if scan_exclude_paths:
            scan_exclude_paths = set(os.path.normcase(os.path.normpath(e)).rstrip(os.sep) for e in scan_exclude_paths)

        language_settings = self.settings.get('language_settings', {})
        for l, s in language_settings.items():
            if lang is not None and l != lang:
                continue

            if l in disabled_languages or s.get('@disable'):
                continue

            for k, v in s.items():
                if k not in self.settings:
                    prefs[k] = v

            extra_paths_name = EXTRA_PATHS_MAP.get(l)
            language_scan_extra_paths = set(s.get('scan_extra_paths', [])) | set(s.get(extra_paths_name, []))
            if language_scan_extra_paths:
                language_scan_extra_paths = [os.path.normcase(os.path.normpath(e)).rstrip(os.sep) for e in scan_extra_paths | language_scan_extra_paths]
            if extra_paths_name:
                prefs[extra_paths_name] = os.pathsep.join(language_scan_extra_paths)

            exclude_paths_name = EXCLUDE_PATHS_MAP.get(l)
            language_scan_exclude_paths = set(s.get('scan_exclude_paths', [])) | set(s.get(exclude_paths_name, []))
            if language_scan_exclude_paths:
                language_scan_exclude_paths = [os.path.normcase(os.path.normpath(e)).rstrip(os.sep) for e in scan_exclude_paths | language_scan_exclude_paths]
            if exclude_paths_name:
                prefs[exclude_paths_name] = os.pathsep.join(language_scan_exclude_paths)

        return prefs


if 'settings' not in globals():
    settings = CodeintelSettings(NAME)

    class CodeintelToggleSettingCommand(SettingTogglerCommandMixin, sublime_plugin.WindowCommand):
        settings = settings

    ci = CodeIntel(lambda fn: sublime.set_timeout(fn, 0))


################################################################################

def plugin_loaded():
    settings.load()


# ST3 features a plugin_loaded hook which is called when ST's API is ready.
#
# We must therefore call our init callback manually on ST2. It must be the last
# thing in this plugin (thanks, beloved contributors!).
if int(sublime.version()) < 3000:
    plugin_loaded()
