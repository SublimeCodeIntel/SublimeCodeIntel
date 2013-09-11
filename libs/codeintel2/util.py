#!python
# encoding: utf-8
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
# The Original Code is Komodo code.
#
# The Initial Developer of the Original Code is ActiveState Software Inc.
# Portions created by ActiveState Software Inc are Copyright (C) 2000-2007
# ActiveState Software Inc. All Rights Reserved.
#
# Contributor(s):
#   ActiveState Software Inc
#
# Alternatively, the contents of this file may be used under the terms of
# either the GNU General Public License Version 2 or later (the "GPL"), or
# the GNU Lesser General Public License Version 2.1 or later (the "LGPL"),
# in which case the provisions of the GPL or the LGPL are applicable instead
# of those above. If you wish to allow use of your version of this file only
# under the terms of either the GPL or the LGPL, and not to allow others to
# use your version of this file under the terms of the MPL, indicate your
# decision by deleting the provisions above and replace them with the notice
# and other provisions required by the GPL or the LGPL. If you do not delete
# the provisions above, a recipient may use your version of this file under
# the terms of any one of the MPL, the GPL or the LGPL.
#
# ***** END LICENSE BLOCK *****

"""Code Intelligence: utility functions"""

import bisect
import os
from os.path import basename
import sys
import re
import stat
import textwrap
import logging
import types
from pprint import pprint, pformat
import time
import codecs

# Global dict for holding specific hotshot profilers
hotshotProfilers = {}

#---- general stuff


def isident(char):
    char = ord(char)
    return ord('a') <= char <= ord('z') or ord('A') <= char <= ord('Z') or char == ord('_')


def isdigit(char):
    char = ord(char)
    return ord('0') <= char <= ord('9')

# A "safe" language name for the given language where safe generally
# means safe for a file path.
_safe_lang_from_lang_cache = {
    "C++": "cpp",
}


def safe_lang_from_lang(lang):
    global _safe_lang_from_lang_cache
    try:
        return _safe_lang_from_lang_cache[lang]
    except KeyError:
        safe_lang = lang.lower().replace(' ', '_')
        _safe_lang_from_lang_cache[lang] = safe_lang
        return safe_lang


# @deprecated: Manager.buf_from_path now uses textinfo to guess lang.
def guess_lang_from_path(path):
    lang_from_ext = {
        ".py": "Python",
        ".pl": "Perl",
        ".pm": "Perl",
        ".tcl": "Tcl",
        ".php": "PHP",
        ".inc": "PHP",
        ".rb": "Ruby",
        ".rhtml": "RHTML",
        ".html.erb": "RHTML",
        ".js": "JavaScript",
        ".java": "Java",
        ".css": "CSS",
        ".xul": "XUL",
        ".xbl": "XBL",
        ".html": "HTML",
        ".xml": "XML",
        ".tpl": "Smarty",
        ".django.html": "Django",
        ".mason.html": "Mason",
        ".ttkt.html": "TemplateToolkit",
        ".cxx": "C++",
    }
    idx = 0
    base = basename(path)
    while base.find('.', idx) != -1:
        idx = base.find('.', idx)
        if idx == -1:
            break
        ext = base[idx:]
        if ext in lang_from_ext:
            return lang_from_ext[ext]
        idx += 1
    from codeintel2.common import CodeIntelError
    raise CodeIntelError("couldn't guess lang for `%s'" % path)


def gen_dirs_under_dirs(dirs, max_depth, interesting_file_patterns=None,
                        skip_scc_control_dirs=True):
    """Generate all dirs under the given dirs (including the given dirs
    themselves).

        "max_depth" is an integer maximum number of sub-directories that
            this method with recurse.
        "file_patterns", if given, is a sequence of glob patterns for
            "interesting" files. Directories with no interesting files are
            not included (though sub-directories of these may be).
        "skip_scc_control_dirs" is a boolean (default True) indicating if
            svn and cvs control dirs should be skipped.
    """
    from os.path import normpath, abspath, expanduser
    from fnmatch import fnmatch

    dirs_to_skip = (skip_scc_control_dirs
                    and ["CVS", ".svn", ".hg", ".git", ".bzr"] or [])
    # We must keep track of the directories we have walked, as the list of dirs
    # can overlap - bug 90289.
    walked_these_dirs = {}
    for dir in dirs:
        norm_dir = normpath(abspath(expanduser(dir)))
        LEN_DIR = len(norm_dir)
        for dirpath, dirnames, filenames in walk2(norm_dir):
            if dirpath in walked_these_dirs:
                dirnames[:] = []  # Already walked - no need to do it again.
                continue
            if dirpath[LEN_DIR:].count(os.sep) >= max_depth:
                dirnames[:] = []  # hit max_depth
            else:
                walked_these_dirs[dirpath] = True
                for dir_to_skip in dirs_to_skip:
                    if dir_to_skip in dirnames:
                        dirnames.remove(dir_to_skip)
            if interesting_file_patterns:
                for pat, filename in (
                    (p, f) for p in interesting_file_patterns
                        for f in filenames):
                    if fnmatch(filename, pat):
                        break
                else:
                    # No interesting files in this dir.
                    continue

            yield dirpath


#---- standard module/class/function doc parsing
LINE_LIMIT = 5      # limit full number of lines this number
LINE_WIDTH = 60     # wrap doc summaries to this width

# Examples matches to this pattern:
#    foo(args)
#    foo(args) -> retval
#    foo(args) -- description
#    retval = foo(args)
#    retval = foo(args) -- description
_gPySigLinePat = re.compile(
    r"^((?P<retval>[^=]+?)\s*=|class)?\s*(?P<head>[\w\.]+\s?\(.*?\))\s*(?P<sep>[:<>=-]*)\s*(?P<tail>.*)$")
_gSentenceSepPat = re.compile(r"(?<=\.)\s+", re.M)  # split on sentence bndry


def parseDocSummary(doclines, limit=LINE_LIMIT, width=LINE_WIDTH):
    """Parse out a short summary from the given doclines.

        "doclines" is a list of lines (without trailing newlines) to parse.
        "limit" is the number of lines to which to limit the summary.

    The "short summary" is the first sentence limited by (1) the "limit"
    number of lines and (2) one paragraph. If the first *two* sentences fit
    on the first line, then use both. Returns a list of summary lines.
    """
    # Skip blank lines.
    start = 0
    while start < len(doclines):
        if doclines[start].strip():
            break
        start += 1

    desclines = []
    for i in range(start, len(doclines)):
        if len(desclines) >= limit:
            break
        stripped = doclines[i].strip()
        if not stripped:
            break
        sentences = _gSentenceSepPat.split(stripped)
        if sentences and not sentences[-1].endswith('.'):
            del sentences[-1]  # last bit might not be a complete sentence
        if not sentences:
            desclines.append(stripped + ' ')
            continue
        elif i == start and len(sentences) > 1:
            desclines.append(' '.join([s.strip() for s in sentences[:2]]))
        else:
            desclines.append(sentences[0].strip())
        break
    if desclines:
        if desclines[-1][-1] == ' ':
            # If terminated at non-sentence boundary then have extraneous
            # trailing space.
            desclines[-1] = desclines[-1][:-1]
        desclines = textwrap.wrap(''.join(desclines), width)
    return desclines


def parsePyFuncDoc(doc, fallbackCallSig=None, scope="?", funcname="?"):
    """Parse the given Python function/method doc-string into call-signature
    and description bits.

        "doc" is the function doc string.
        "fallbackCallSig" (optional) is a list of call signature lines to
            fallback to if one cannot be determined from the doc string.
        "scope" (optional) is the module/class parent scope name. This
            is just used for better error/log reporting.
        "funcname" (optional) is the function name. This is just used for
            better error/log reporting.

    Examples of doc strings with call-signature info:
        close(): explicitly release resources held.
        x.__repr__() <==> repr(x)
        read([s]) -- Read s characters, or the rest of the string
        recv(buffersize[, flags]) -> data
        replace (str, old, new[, maxsplit]) -> string
        class StringIO([buffer])

    Returns a 2-tuple: (<call-signature-lines>, <description-lines>)
    """
    if doc is None or not doc.strip():
        return ([], [])

    limit = LINE_LIMIT
    if not isinstance(doc, str):
        # try to convert from utf8 to unicode; if we fail, too bad.
        try:
            doc = codecs.utf_8_decode(doc)[0]
        except UnicodeDecodeError:
            pass
    doclines = doc.splitlines(0)
    index = 0
    siglines = []
    desclines = []

    # Skip leading blank lines.
    while index < len(doclines):
        if doclines[index].strip():
            break
        index += 1

    # Parse out the call signature block, if it looks like there is one.
    if index >= len(doclines):
        match = None
    else:
        first = doclines[index].strip()
        match = _gPySigLinePat.match(first)
    if match:
        # The 'doc' looks like it starts with a call signature block.
        for i, line in enumerate(doclines[index:]):
            if len(siglines) >= limit:
                index = i
                break
            stripped = line.strip()
            if not stripped:
                index = i
                break
            match = _gPySigLinePat.match(stripped)
            if not match:
                index = i
                break
            # Now parse off what may be description content on the same line.
            #   ":", "-" or "--" separator: tail is description
            #   "-->" or "->" separator: tail if part of call sig
            #   "<==>" separator: tail if part of call sig
            #   other separtor: leave as part of call sig for now
            descSeps = ("-", "--", ":")
            groupd = match.groupdict()
            retval, head, sep, tail = (
                groupd.get("retval"), groupd.get("head"),
                groupd.get("sep"), groupd.get("tail"))
            if retval:
                siglines.append(head + " -> " + retval)
                if tail and sep in descSeps:
                    desclines.append(tail)
            elif tail and sep in descSeps:
                siglines.append(head)
                desclines.append(tail)
            else:
                siglines.append(stripped)
        else:
            index = len(doclines)
    if not siglines and fallbackCallSig:
        siglines = fallbackCallSig

    # Parse out the description block.
    if desclines:
        # Use what we have already. Just need to wrap it.
        desclines = textwrap.wrap(' '.join(desclines), LINE_WIDTH)
    else:
        doclines = doclines[index:]
        # strip leading empty lines
        while len(doclines) > 0 and not doclines[0].rstrip():
            del doclines[0]
        try:
            skip_first_line = (doclines[0][0] not in (" \t"))
        except IndexError:
            skip_first_line = False  # no lines, or first line is empty
        desclines = dedent("\n".join(
            doclines), skip_first_line=skip_first_line)
        desclines = desclines.splitlines(0)

    ## debug logging
    # f = open("parsePyFuncDoc.log", "a")
    # if 0:
    #    f.write("\n---- %s:\n" % funcname)
    #    f.write(pformat(siglines)+"\n")
    #    f.write(pformat(desclines)+"\n")
    # else:
    #    f.write("\n")
    #    if siglines:
    #        f.write("\n".join(siglines)+"\n")
    #    else:
    #        f.write("<no signature for '%s.%s'>\n" % (scope, funcname))
    #    for descline in desclines:
    #        f.write("\t%s\n" % descline)
    # f.close()

    return (siglines, desclines)


#---- debugging utilities

def unmark_text(markedup_text):
    """Parse text with potential markup as follows and return
    (<text>, <data-dict>).

        "<|>" indicates the current position (pos), defaults to the end
            of the text.
        "<+>" indicates the trigger position (trg_pos), if present.
        "<$>" indicates the start position (start_pos) for some kind of
            of processing, if present.
        "<N>" is a numbered marker. N can be any of 0-99. These positions
            are returned as the associate number key in <data-dict>.

    Note that the positions are in UTF-8 byte counts, not character counts.
    This matches the behaviour of Scintilla positions.

    E.g.:
        >>> unmark_text('foo.<|>')
        ('foo.', {'pos': 4})
        >>> unmark_text('foo.<|><+>')
        ('foo.', {'trg_pos': 4, 'pos': 4})
        >>> unmark_text('foo.<+>ba<|>')
        ('foo.ba', {'trg_pos': 4, 'pos': 6})
        >>> unmark_text('fo<|>o.<+>ba')
        ('foo.ba', {'trg_pos': 4, 'pos': 2})
        >>> unmark_text('os.path.join<$>(<|>')
        ('os.path.join(', {'pos': 13, 'start_pos': 12})
        >>> unmark_text('abc<3>defghi<2>jk<4>lm<1>nopqrstuvwxyz')
        ('abcdefghijklmnopqrstuvwxyz', {1: 13, 2: 9, 3: 3, 4: 11, 'pos': 26})
        >>> unmark_text('Ůɳíčóďé<|>')
        ('Ůɳíčóďé', {'pos': 14})

    See the matching markup_text() below.
    """
    splitter = re.compile(r"(<(?:[\|\+\$\[\]<]|\d+)>)")
    text = "" if isinstance(markup_text, str) else ""
    data = {}
    posNameFromSymbol = {
        "<|>": "pos",
        "<+>": "trg_pos",
        "<$>": "start_pos",
        "<[>": "start_selection",
        "<]>": "end_selection",
    }

    def byte_length(text):
        if isinstance(text, str):
            return len(text.encode("utf-8"))
        return len(text)

    bracketed_digits_re = re.compile(r'<\d+>$')
    for token in splitter.split(markedup_text):
        if token in posNameFromSymbol:
            data[posNameFromSymbol[token]] = byte_length(text)
        elif token == "<<>":  # escape sequence
            text += "<"
        elif bracketed_digits_re.match(token):
            data[int(token[1:-1])] = byte_length(text)
        else:
            text += token
    if "pos" not in data:
        data["pos"] = byte_length(text)
    # sys.stderr.write(">> text:%r, data:%s\n" % (text, data))
    return text, data


def markup_text(text, pos=None, trg_pos=None, start_pos=None):
    """Markup text with position markers.

    See the matching unmark_text() above.
    """
    positions_and_markers = []
    if pos is not None:
        positions_and_markers.append((pos, '<|>'))
    if trg_pos is not None:
        positions_and_markers.append((trg_pos, '<+>'))
    if start_pos is not None:
        positions_and_markers.append((start_pos, '<$>'))
    positions_and_markers.sort()

    text = str(text).encode("utf-8")
    m_text = ""
    m_pos = 0
    for position, marker in positions_and_markers:
        m_text += text[m_pos:position] + marker
        m_pos = position
    m_text += text[m_pos:]
    return m_text.decode("utf-8")


def lines_from_pos(unmarked_text, positions):
    """Get 1-based line numbers from positions
        @param unmarked_text {str} The text to examine
        @param positions {dict or list of int} Byte positions to look up
        @returns {dict or list of int} Matching line numbers (1-based)
    Given some text and either a list of positions, or a dict containing
    positions as values, return a matching data structure with positions
    replaced with the line number of the lines the positions are on.  Positions
    after the last line are assumed to be on a hypothetical line.

    E.g.:
        Assuming the following text with \n line endings, where each line is
        exactly 20 characters long:
        >>> text = '''
        ... line            one
        ... line            two
        ... line          three
        ... '''.lstrip()
        >>> lines_from_pos(text, [5, 15, 25, 55, 999])
        [1, 1, 2, 3, 4]
        >>> lines_from_pos(text, {"hello": 10, "moo": 20, "not": "an int"})
        {'moo': 1, 'hello': 1}
    """
    lines = str(unmarked_text).splitlines(True)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line.encode("utf-8")))
    try:
        # assume a dict
        keys = iter(positions.keys())
        values = {}
    except AttributeError:
        # assume a list/tuple
        keys = list(range(len(positions)))
        values = []

    for key in keys:
        try:
            position = positions[key] - 0
        except TypeError:
            continue  # not a number
        line_no = bisect.bisect_left(offsets, position)
        try:
            values[key] = line_no
        except IndexError:
            if key == len(values):
                values.append(line_no)
            else:
                raise

    return values

# Recipe: banner (1.0.1) in C:\trentm\tm\recipes\cookbook


def banner(text, ch='=', length=78):
    """Return a banner line centering the given text.

        "text" is the text to show in the banner. None can be given to have
            no text.
        "ch" (optional, default '=') is the banner line character (can
            also be a short string to repeat).
        "length" (optional, default 78) is the length of banner to make.

    Examples:
        >>> banner("Peggy Sue")
        '================================= Peggy Sue =================================='
        >>> banner("Peggy Sue", ch='-', length=50)
        '------------------- Peggy Sue --------------------'
        >>> banner("Pretty pretty pretty pretty Peggy Sue", length=40)
        'Pretty pretty pretty pretty Peggy Sue'
    """
    if text is None:
        return ch * length
    elif len(text) + 2 + len(ch) * 2 > length:
        # Not enough space for even one line char (plus space) around text.
        return text
    else:
        remain = length - (len(text) + 2)
        prefix_len = remain // 2
        suffix_len = remain - prefix_len
        if len(ch) == 1:
            prefix = ch * prefix_len
            suffix = ch * suffix_len
        else:
            prefix = ch * (prefix_len // len(ch)) + ch[:prefix_len % len(ch)]
            suffix = ch * (suffix_len // len(ch)) + ch[:suffix_len % len(ch)]
        return prefix + ' ' + text + ' ' + suffix


# Recipe: dedent (0.1.2) in C:\trentm\tm\recipes\cookbook
def _dedentlines(lines, tabsize=8, skip_first_line=False):
    """_dedentlines(lines, tabsize=8, skip_first_line=False) -> dedented lines

        "lines" is a list of lines to dedent.
        "tabsize" is the tab width to use for indent width calculations.
        "skip_first_line" is a boolean indicating if the first line should
            be skipped for calculating the indent width and for dedenting.
            This is sometimes useful for docstrings and similar.

    Same as dedent() except operates on a sequence of lines. Note: the
    lines list is modified **in-place**.
    """
    DEBUG = False
    if DEBUG:
        print("dedent: dedent(..., tabsize=%d, skip_first_line=%r)"\
              % (tabsize, skip_first_line))
    indents = []
    margin = None
    for i, line in enumerate(lines):
        if i == 0 and skip_first_line:
            continue
        indent = 0
        for ch in line:
            if ch == ' ':
                indent += 1
            elif ch == '\t':
                indent += tabsize - (indent % tabsize)
            elif ch in '\r\n':
                continue  # skip all-whitespace lines
            else:
                break
        else:
            continue  # skip all-whitespace lines
        if DEBUG:
            print("dedent: indent=%d: %r" % (indent, line))
        if margin is None:
            margin = indent
        else:
            margin = min(margin, indent)
    if DEBUG:
        print("dedent: margin=%r" % margin)

    if margin is not None and margin > 0:
        for i, line in enumerate(lines):
            if i == 0 and skip_first_line:
                continue
            removed = 0
            for j, ch in enumerate(line):
                if ch == ' ':
                    removed += 1
                elif ch == '\t':
                    removed += tabsize - (removed % tabsize)
                elif ch in '\r\n':
                    if DEBUG:
                        print("dedent: %r: EOL -> strip up to EOL" % line)
                    lines[i] = lines[i][j:]
                    break
                else:
                    raise ValueError("unexpected non-whitespace char %r in "
                                     "line %r while removing %d-space margin"
                                     % (ch, line, margin))
                if DEBUG:
                    print("dedent: %r: %r -> removed %d/%d"\
                          % (line, ch, removed, margin))
                if removed == margin:
                    lines[i] = lines[i][j+1:]
                    break
                elif removed > margin:
                    lines[i] = ' '*(removed-margin) + lines[i][j+1:]
                    break
            else:
                if removed:
                    lines[i] = lines[i][removed:]
    return lines


def dedent(text, tabsize=8, skip_first_line=False):
    """dedent(text, tabsize=8, skip_first_line=False) -> dedented text

        "text" is the text to dedent.
        "tabsize" is the tab width to use for indent width calculations.
        "skip_first_line" is a boolean indicating if the first line should
            be skipped for calculating the indent width and for dedenting.
            This is sometimes useful for docstrings and similar.

    textwrap.dedent(s), but don't expand tabs to spaces
    """
    lines = text.splitlines(1)
    _dedentlines(lines, tabsize=tabsize, skip_first_line=skip_first_line)
    return ''.join(lines)


# Recipe: indent (0.2.1) in C:\trentm\tm\recipes\cookbook
def indent(s, width=4, skip_first_line=False):
    """indent(s, [width=4]) -> 's' indented by 'width' spaces

    The optional "skip_first_line" argument is a boolean (default False)
    indicating if the first line should NOT be indented.
    """
    lines = s.splitlines(1)
    indentstr = ' '*width
    if skip_first_line:
        return indentstr.join(lines)
    else:
        return indentstr + indentstr.join(lines)


def walk2(top, topdown=True, onerror=None, followlinks=False,
          ondecodeerror=None):
    """A version of `os.walk` that adds support for handling errors for
    files that cannot be decoded with the default encoding. (See bug 82268.)

    By default `UnicodeDecodeError`s from the os.listdir() call are
    ignored.  If optional arg 'ondecodeerror' is specified, it should be a
    function; it will be called with one argument, the `UnicodeDecodeError`
    instance. It can report the error to continue with the walk, or
    raise the exception to abort the walk.
    """
    from os.path import join, isdir, islink

    # We may not have read permission for top, in which case we can't
    # get a list of the files the directory contains.  os.path.walk
    # always suppressed the exception then, rather than blow up for a
    # minor reason when (say) a thousand readable directories are still
    # left to visit.  That logic is copied here.
    try:
        # Note that listdir and error are globals in this module due
        # to earlier import-*.
        names = os.listdir(top)
    except os.error as err:
        if onerror is not None:
            onerror(err)
        return

    dirs, nondirs = [], []
    for name in names:
        try:
            if isdir(join(top, name)):
                dirs.append(name)
            else:
                nondirs.append(name)
        except UnicodeDecodeError as err:
            if ondecodeerror is not None:
                ondecodeerror(err)

    if topdown:
        yield top, dirs, nondirs
    for name in dirs:
        path = join(top, name)
        if followlinks or not islink(path):
            for x in walk2(path, topdown, onerror, followlinks):
                yield x
    if not topdown:
        yield top, dirs, nondirs


# Decorators useful for timing and profiling specific functions.
#
# timeit usage:
#   Decorate the desired function and you'll get a print for how long
#   each call to the function took.
#
# hotspotit usage:
#   1. decorate the desired function
#   2. run your code
#   3. run:
#       python .../codeintel/support/show_stats.py .../<funcname>.prof
#
def timeit(func):
    clock = (sys.platform == "win32" and time.clock or time.time)

    def wrapper(*args, **kw):
        start_time = clock()
        try:
            return func(*args, **kw)
        finally:
            total_time = clock() - start_time
            print("%s took %.3fs" % (func.__name__, total_time))
    return wrapper


def hotshotit(func):
    def wrapper(*args, **kw):
        import hotshot
        global hotshotProfilers
        prof_name = func.__name__+".prof"
        profiler = hotshotProfilers.get(prof_name)
        if profiler is None:
            profiler = hotshot.Profile(prof_name)
            hotshotProfilers[prof_name] = profiler
        return profiler.runcall(func, *args, **kw)
    return wrapper

_koCProfiler = None


def getProfiler():
    global _koCProfiler
    if _koCProfiler is None:
        class _KoCProfileManager(object):
            def __init__(self):
                import atexit
                import cProfile
                from codeintel2.common import _xpcom_
                self.prof = cProfile.Profile()
                if _xpcom_:
                    from xpcom import components
                    _KoCProfileManager._com_interfaces_ = [
                        components.interfaces.nsIObserver]
                    obsSvc = components.classes["@mozilla.org/observer-service;1"].\
                        getService(
                            components.interfaces.nsIObserverService)
                    obsSvc.addObserver(self, 'xpcom-shutdown', False)
                else:
                    atexit.register(self.atexit_handler)

            def atexit_handler(self):
                self.prof.print_stats(sort="time")

            def observe(self, subject, topic, data):
                if topic == "xpcom-shutdown":
                    self.atexit_handler()
        _koCProfiler = _KoCProfileManager()
    return _koCProfiler.prof


def profile_method(func):
    def wrapper(*args, **kw):
        return getProfiler().runcall(func, *args, **kw)
    return wrapper

# Utility functions to perform sorting the same way as scintilla does it
# for the code-completion list.


def OrdPunctLast(value):
    result = []
    value = value.upper()
    for ch in value:
        i = ord(ch)
        if i >= 0x21 and i <= 0x2F:  # ch >= '!' && ch <= '/'
            result.append(chr(i - ord("!") + ord('[')))    # ch - '!' + '['
        elif i >= 0x3A and i <= 0x40:  # ch >= ':' && ch <= '@'
            result.append(chr(i - ord(":") + ord('[')))    # ch - ':' + '['
        else:
            result.append(ch)
    return "".join(result)


def CompareNPunctLast(value1, value2):
    # value 1 is smaller, return negative
    # value 1 is equal, return 0
    # value 1 is larger, return positive
    return cmp(OrdPunctLast(value1), OrdPunctLast(value2))


# Utility function to make a lookup dictionary
def make_short_name_dict(names, length=3):
    outdict = {}
    for name in names:
        if len(name) >= length:
            shortname = name[:length]
            l = outdict.get(shortname)
            if not l:
                outdict[shortname] = [name]
            else:
                l.append(name)
        # pprint(outdict)
    for values in list(outdict.values()):
        values.sort(CompareNPunctLast)
    return outdict


def makePerformantLogger(logger):
    """Replaces the info() and debug() methods with dummy methods.

    Assumes that the logging level does not change during runtime.
    """
    if not logger.isEnabledFor(logging.INFO):
        def _log_ignore(self, *args, **kwargs):
            pass
        logger.info = _log_ignore
        if not logger.isEnabledFor(logging.DEBUG):
            logger.debug = _log_ignore


#---- mainline self-test

if __name__ == "__main__":
    import doctest
    doctest.testmod()
