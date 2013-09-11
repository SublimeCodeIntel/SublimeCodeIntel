#!/usr/bin/env python
# Copyright (c) 2006-2012 ActiveState Software Inc.
# See LICENSE.txt for license details.

"""Twig support for codeintel"""

import logging

from codeintel2.common import *
from codeintel2.langintel import LangIntel
from codeintel2.udl import UDLLexer, UDLBuffer, UDLCILEDriver, XMLParsingBufferMixin

if _xpcom_:
    from xpcom.server import UnwrapObject

#---- globals

lang = "Twig"
log = logging.getLogger("codeintel.twig")


twig_keywords = [
    "and",
    "as",
    "b-and",
    "b-or",
    "b-xor",
    "by",
    "in",
    "not",
    "or",
]
twig_keywords2 = [
    "attribute",
    "block",
    "constant",
    "cycle",
    "date",
    "dump",
    "parent",
    "random",
    "range",

    "constant",
    "defined",
    "divisibleby",
    "empty",
    "even",
    "iterable",
    "null",
    "odd",
    "sameas",
]
twig_keywords += twig_keywords2

twig_tags = [
    "autoescape",
    "block",
    "do",
    "embed",
    "extends",
    "filter",
    "flush",
    "for",
    "from",
    "if",
    "import",
    "include",
    "macro",
    "raw",
    "sandbox",
    "set",
    "spaceless",
    "use",

    # end tags
    "endautoescape",
    "endblock",
    "endcomment",
    "endembed",
    "endfilter",
    "endfor",
    "endif",
    "endmacro",
    "endraw",
    "endsandbox",
    "endspaceless",
    "endwith",
]

twig_default_filter_names = [
    # These are default filter names in twig
    "capitalize",
    "convert_encoding",
    "date",
    "default",
    "escape",
    "format",
    "join",
    "json_encode",
    "keys",
    "length",
    "lower",
    "merge",
    "nl2br",
    "number_format",
    "raw",
    "replace",
    "reverse",
    "slice",
    "sort",
    "striptags",
    "title",
    "trim",
    "upper",
    "url_encode",
]


#---- language support

class TwigLexer(UDLLexer):
    lang = lang


class TwigBuffer(UDLBuffer, XMLParsingBufferMixin):
    lang = lang
    tpl_lang = lang
    m_lang = "HTML"
    css_lang = "CSS"
    csl_lang = "JavaScript"
    ssl_lang = "Twig"

    # Characters that should close an autocomplete UI:
    # - wanted for XML completion: ">'\" "
    # - wanted for CSS completion: " ('\";},.>"
    # - wanted for JS completion:  "~`!@#%^&*()-=+{}[]|\\;:'\",.<>?/ "
    # - dropping ':' because I think that may be a problem for XML tag
    #   completion with namespaces (not sure of that though)
    # - dropping '[' because need for "<!<|>" -> "<![CDATA[" cpln
    # - dropping '-' because causes problem with CSS (bug 78312)
    # - dropping '!' because causes problem with CSS "!important" (bug 78312)
    cpln_stop_chars = "'\" (;},~`@#%^&*()=+{}]|\\;,.<>?/"


class TwigLangIntel(LangIntel):
    lang = lang

    # Used by ProgLangTriggerIntelMixin.preceding_trg_from_pos()
    trg_chars = tuple('| ')
    calltip_trg_chars = tuple()

    def trg_from_pos(self, buf, pos, implicit=True, DEBUG=False):
        """
            CODE       CONTEXT      RESULT
            '{<|>'     anywhere     tag names, i.e. {% if %}
            'foo|<|>'  filters      filter names, i.e. {{ foo|capfirst }}
        """
        # DEBUG = True # not using 'logging' system, because want to be fast
        if DEBUG:
            print("\n----- Twig trg_from_pos(pos=%r, implicit=%r) -----"\
                  % (pos, implicit))

        if pos < 2:
            return None
        accessor = buf.accessor
        last_pos = pos - 1
        last_char = accessor.char_at_pos(last_pos)
        if DEBUG:
            print("  last_pos: %s" % last_pos)
            print("  last_char: %r" % last_char)
            print('accessor.text_range(last_pos-2, last_pos): %r' % (accessor.text_range(last_pos-2, last_pos), ))

        if last_char == " " and \
           accessor.text_range(last_pos-2, last_pos) == "{%":
            if DEBUG:
                print("  triggered: 'complete-tags'")
            return Trigger(lang, TRG_FORM_CPLN,
                           "complete-tags", pos, implicit)

        if last_char == "|":
            if DEBUG:
                print("  triggered: 'complete-filters'")
            return Trigger(lang, TRG_FORM_CPLN,
                           "complete-filters", pos, implicit)

    _twigtag_cplns = [("element", t) for t in sorted(twig_tags)]
    _twigfilter_cplns = [("function", t) for t in sorted(
        twig_default_filter_names)]

    def async_eval_at_trg(self, buf, trg, ctlr):
        if _xpcom_:
            trg = UnwrapObject(trg)
            ctlr = UnwrapObject(ctlr)

        ctlr.start(buf, trg)

        # Twig tag completions
        if trg.id == (lang, TRG_FORM_CPLN, "complete-tags"):
            ctlr.set_cplns(self._twigtag_cplns)
            ctlr.done("success")
            return
        if trg.id == (lang, TRG_FORM_CPLN, "complete-filters"):
            ctlr.set_cplns(self._twigfilter_cplns)
            ctlr.done("success")
            return

        ctlr.done("success")


class TwigCILEDriver(UDLCILEDriver):
    lang = lang
    csl_lang = "JavaScript"
    tpl_lang = "Twig"


#---- registration
def register(mgr):
    """Register language support with the Manager."""
    mgr.set_lang_info(lang,
                      silvercity_lexer=TwigLexer(),
                      buf_class=TwigBuffer,
                      langintel_class=TwigLangIntel,
                      import_handler_class=None,
                      cile_driver_class=TwigCILEDriver,
                      is_cpln_lang=True)
