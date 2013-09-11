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
#
# Contributors:
#   Eric Promislow (EricP@ActiveState.com)
#
# Common wrapper around SilverCity used by Ruby, Perl

import copy
import re
import sys

from SilverCity import ScintillaConstants

import logging
#---- global data
log = logging.getLogger("codeintel_shared_lexer")
# log.setLevel(logging.DEBUG)

MAX_REASONABLE_LIMIT = 10000

WHITESPACE = '\t\n\x0b\x0c\r '  # don't use string.whitespace (bug 81316)
ws_re = re.compile("^[" + WHITESPACE + "\\\\" + "]*$")
trailing_spaces_re = re.compile("\n([ \t]*)$")
trim_ws_re2 = re.compile(r'[\r\n\t]')
trim_ws_re3 = re.compile(r' {2,}')


def makeToken(style, text="", start_column=None, start_line=None, end_column=None, end_line=None):
    return {
        'style': style,
        'text': text,
        'start_column': start_column,
        'start_line': start_line,
        'end_column': end_column,
        'end_line': end_line,
    }

EOF_STYLE = -1
EOF_TOKEN = {'style': EOF_STYLE,
             'text': None,
             'start_column': None,
             'start_line': None,
             'end_column': None,
             'end_line': None,
             }


class Signature:
    def __init__(self):
        self._gathering = False
        self._text = ""

    def open(self):
        self._gathering = True
        self._text = ""

    def close(self):
        self._gathering = False

    def text(self):
        return self._text

    def append(self, text):
        self._text += text

    def replace(self, text):
        self._text = text

    def is_gathering(self):
        return self._gathering


class Lexer:
    def __init__(self):
        self.gen = self._get_next_token
        self.curr_indentation = 0
        self.curr_comments = []
        self.finished_comment = True
        self.use_leading_spaces = True
        self.signature = Signature()
        self.q = []
        self.curr_line = 1

    def prepare_token_list_for_use(self):
        self.q_position = 0
        self.q_lim = len(self.q)

    def build_dict(self, ws_sep_str):
        the_dict = {}
        for the_key in ws_sep_str.strip().split():
            the_dict[the_key] = 1
        return the_dict

    def is_string_token(self, tok):
        return tok['style'] in self.string_types

    def contains_nl(self, str2):
        return str2.find("\n") >= 0

    def _adapt_line(self, line_num):
        if line_num is None:
            return None
        return line_num + 1

    def complete_token_push(self, tok, adjust_line=True, dest_q=None):
        if dest_q is not None:
            dest_q.append(tok)
        else:
            self.q.append(tok)

    def _get_next_token(self):
        if self.q_position >= self.q_lim:
            return EOF_TOKEN
        tok = self.q[self.q_position]
        self.q_position += 1
        if 'adjust_lines' not in tok:
            for s in ('start_line', 'end_line'):
                if s not in tok:
                    tok[s] = None
                else:
                    tok[s] += 1
            tok['adjust_lines'] = True
        return tok

    def _get_eof_token(self):
        return EOF_TOKEN

    def matches_whitespace(self, text):
        return ws_re.match(text)

    def get_curr_indentation(self):
        return self.curr_indentation

    def curr_comment(self, destroy=1):
        hold = self.curr_comments
        self.curr_comments = []
        return hold

    def clear_comments(self):
        self.curr_comments = []

    def has_comment(self):
        return len(self.curr_comments) > 0

    def is_udl_markup_family(self, ttype):
        return ScintillaConstants.SCE_UDL_M_DEFAULT <= ttype <= ScintillaConstants.SCE_UDL_M_COMMENT

    def is_udl_css_family(self, ttype):
        return ScintillaConstants.SCE_UDL_CSS_DEFAULT <= ttype <= ScintillaConstants.SCE_UDL_CSS_OPERATOR

    def is_udl_csl_family(self, ttype):
        return ScintillaConstants.SCE_UDL_CSL_DEFAULT <= ttype <= ScintillaConstants.SCE_UDL_CSL_REGEX

    def is_udl_ssl_family(self, ttype):
        return ScintillaConstants.SCE_UDL_SSL_DEFAULT <= ttype <= ScintillaConstants.SCE_UDL_SSL_VARIABLE

    def is_udl_tpl_family(self, ttype):
        return ScintillaConstants.SCE_UDL_TPL_DEFAULT <= ttype <= ScintillaConstants.SCE_UDL_TPL_VARIABLE

    # Methods for manipulating signatures

    def start_sig(self):
        self.signature.open()

    def stop_sig(self):
        self.signature.close()

    def trim_ws(self, s1):
        s2 = trim_ws_re2.sub(' ', s1)
        s3 = trim_ws_re3.sub(' ', s2)
        s4 = s3.strip()
        if len(s4) == 0:
            if len(s1) > 0:
                return " "
        return s4

    def get_sig(self):
        return self.signature.text().strip()

    # Main external routines

    def put_back(self, tok):
        if tok['style'] == EOF_STYLE:
            return
        if self.signature.is_gathering():
            sig = self.signature.text()
            last_text = tok['text']
            if sig[-len(last_text):] == last_text:
                sig = sig[0:-len(last_text)]
                self.signature.replace(sig)

        # Skip over white-space nodes
        while True:
            self.q_position -= 1
            if self.q_position < 0:
                raise Exception(
                    "Trying to put back a token when position is at start")
            q_tok = self.q[self.q_position]
            if q_tok['style'] == tok['style'] or q_tok['text'] == tok['text']:
                break

        if tok.get('start_line') is not None:
            # Move back for the current line #
            self.curr_line = self.q[self.q_position]['start_line']

    def peek_next_token(self):
        if self.q_position < self.q_lim:
            return self.q[self.q_position]
        return EOF_TOKEN

    def curr_line_no(self):
        return self.curr_line

    def append_split_tokens(self, tok, multi_char_ops_dict,
                            adjust_line=False, dest_q=None, end_column_offset=1):
        # Treat dest_q like a queue here.
        tval = tok['text']
        split_tokens = []
        while len(tval) > 0:
            if tval in multi_char_ops_dict:
                split_tokens.append(tval)
                break
            else:
                # XXX Handle allowed prefixes, as in "<<" and "<<="
                found_something = False
                for possible_op in list(multi_char_ops_dict.keys()):
                    if tval.startswith(possible_op):
                        split_tokens.append(possible_op)
                        tval = tval[len(possible_op):]
                        found_something = True
                        break
                if not found_something:
                    split_tokens.append(tval[0])
                    tval = tval[1:]
        if len(split_tokens) > 1:
            col = tok['start_column']
            for stxt in split_tokens:
                new_tok = copy.copy(tok)
                new_tok['text'] = stxt
                new_tok['start_column'] = col
                new_tok['end_column'] = col + len(stxt) - end_column_offset
                col = new_tok['end_column']
                self.complete_token_push(
                    new_tok, adjust_line=adjust_line, dest_q=dest_q)
        else:
            self.complete_token_push(
                tok, adjust_line=adjust_line, dest_q=dest_q)

    def get_next_token(self, skip_ws=1):
        while True:
            tok = self.gen()
            gather = self.signature.is_gathering()

            ttype = tok['style']
            if tok.get('start_line') is not None:
                self.curr_line = tok['start_line']
            if ttype == EOF_STYLE:
                # Stop leaning on the queue, just return an eof_token
                self.gen = self._get_eof_token
                self.curr_indentation = 0
            elif ttype == self.classifier.style_comment:
                if self.finished_comment:
                    self.curr_comments = []
                    self.finished_comment = False
                self.curr_comments.append(tok['text'])
                self.use_leading_spaces = False
                if skip_ws:
                    continue
            elif ttype == self.classifier.style_default and self.matches_whitespace(tok['text']):
                if gather:
                    self.signature.append(self.trim_ws(tok['text']))
                has_nl = self.contains_nl(tok['text'])
                if has_nl or self.use_leading_spaces:
                    # Update this line's indentation only if we're at the start
                    if has_nl:
                        try:
                            self.curr_indentation = len(
                                trailing_spaces_re.findall(tok['text'])[-1])
                        except:
                            self.curr_indentation = 0
                    else:
                        self.curr_indentation = len(tok['text'])
                    # Do we still need to count white-space in subsequent
                    # tokens?
                    self.use_leading_spaces = (self.curr_indentation == 0)
                if skip_ws:
                    continue
            else:
                # At this point we're done with comments and leading white-
                # space
                if gather:
                    self.signature.append(tok['text'])
                self.finished_comment = True
                self.use_leading_spaces = False
            # If the loop doesn't continue, break here
            break
        return tok


class UDLLexerClassifier:
    """ This classifier is similar to the parser-level classifier, but
    it works on the SilverCity "raw" tokens as opposed to the
    tokens that get created by the lexer layer.  There should be some
    folding though."""

    def is_comment(self, ttype):
        return ttype in (ScintillaConstants.SCE_UDL_SSL_COMMENT,
                         ScintillaConstants.SCE_UDL_SSL_COMMENTBLOCK)

    @property
    def style_comment(self):
        return ScintillaConstants.SCE_UDL_SSL_COMMENT

    @property
    def style_default(self):
        return ScintillaConstants.SCE_UDL_SSL_DEFAULT

    @property
    def style_operator(self):
        return ScintillaConstants.SCE_UDL_SSL_OPERATOR


def read_and_detab(fs, closefd=False, tabwidth=8):
    sample_code = ""
    try:
        # Decompress tabs so our indentation calculations work
        lines = []
        for line in fs:
            lines.append(line.expandtabs(tabwidth))
        sample_code = "".join(lines)
    finally:
        if closefd:
            fs.close()
    return sample_code


def main(argv, provide_sample_code, specificLexer):
    if len(argv) == 1:
        sample_code = provide_sample_code()
        fs = None
    elif argv[1] == "-":
        fs = sys.stdin
    else:
        fs = open(argv[1], "r")
    if fs is not None:
        sample_code = read_and_detab(fs)
        # fs comes back closed

    lexer_wrapper = specificLexer(sample_code)
    last_line = -1
    while 1:
        tok = lexer_wrapper.get_next_token(1)
        if tok['style'] == EOF_STYLE:
            break
        if last_line != tok['start_line']:
            print("[%d:%d] " % (tok['start_line'], lexer_wrapper.curr_indentation), end=' ')
            last_line = tok['start_line']
        if lexer_wrapper.has_comment():
            comments = lexer_wrapper.curr_comment(1)
            print(comments)
        print(tok)
