import HTMLGenerator
import Keywords
import Lexer
from DispatchHandler import DispatchHandler
from _SilverCity import find_lexer_module_by_id, PropertySet, WordList
from ScintillaConstants import SCLEX_CSS
import LanguageInfo

class CSSLexer(Lexer.Lexer):
    def __init__(self, properties = PropertySet()):
        self._properties = properties
        self._lexer = find_lexer_module_by_id(SCLEX_CSS)
        self._keyword_lists = [
            WordList(Keywords.css_keywords),
            WordList(Keywords.css_pseudo_classes),
            WordList(Keywords.css_keywords_2),
                               ]
            
class CSSHandler(DispatchHandler):
    def __init__(self):
        DispatchHandler.__init__(self, 'SCE_CSS')

class CSSHTMLGenerator(HTMLGenerator.SimpleHTMLGenerator, CSSHandler):
    name = 'css'
    description = 'Cascading Style Sheets'
    
    def __init__(self):
        CSSHandler.__init__(self)
        HTMLGenerator.SimpleHTMLGenerator.__init__(self, 'SCE_CSS')
            
    def generate_html(self, file, buffer, lexer = CSSLexer()):
        self._file = file
        lexer.tokenize_by_style(buffer, self.event_handler)

css_language_info = LanguageInfo.LanguageInfo(
                'css',
                 ['css'],
                 ['.*?css.*?'],
                 [CSSHTMLGenerator]
            ) 

LanguageInfo.register_language(css_language_info)
