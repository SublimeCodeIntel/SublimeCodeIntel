#!/usr/bin/env python
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
# Portions created by ActiveState Software Inc are Copyright (C) 2010-2011
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

"""NodeJS support for CodeIntel"""

import logging

from codeintel2.lang_javascript import (JavaScriptLexer,
                                        JavaScriptLangIntel,
                                        JavaScriptBuffer,
                                        JavaScriptImportHandler,
                                        JavaScriptCILEDriver)


#---- globals

lang = "Node.js"
log = logging.getLogger("codeintel.nodejs")
#log.setLevel(logging.DEBUG)


#---- language support

class NodeJSLexer(JavaScriptLexer):
    lang = lang

class NodeJSLangIntel(JavaScriptLangIntel):
    lang = lang
    interpreterPrefName = "nodejsDefaultInterpreter"
    extraPathsPrefName = "nodejsExtraPaths"

class NodeJSBuffer(JavaScriptBuffer):
    lang = lang

class NodeJSImportHandler(JavaScriptImportHandler):
    lang = lang

class NodeJSCILEDriver(JavaScriptCILEDriver):
    lang = lang

#---- registration

def register(mgr):
    """Register language support with the Manager."""
    mgr.set_lang_info(lang,
                      silvercity_lexer=NodeJSLexer(mgr),
                      buf_class=NodeJSBuffer,
                      langintel_class=NodeJSLangIntel,
                      import_handler_class=NodeJSImportHandler,
                      cile_driver_class=NodeJSCILEDriver,
                      is_cpln_lang=True)
