from xml.etree.ElementTree import *

# Import the C accelerators
try:
    # Element, SubElement, ParseError, TreeBuilder, XMLParser
    from _ielementtree import *
except ImportError:
    _patched_for_komodo_ = False
else:
    from xml.etree.ElementTree import _ListDataStream

    _patched_for_komodo_ = True

    # Overwrite 'ElementTree.parse' and 'iterparse' to use the C XMLParser

    class ElementTree(ElementTree):

        def parse(self, source, parser=None):
            close_source = False
            if not hasattr(source, 'read'):
                source = open(source, 'rb')
                close_source = True
            try:
                if parser is not None:
                    while True:
                        data = source.read(65536)
                        if not data:
                            break
                        parser.feed(data)
                    self._root = parser.close()
                else:
                    parser = XMLParser()
                    self._root = parser._parse(source)
                return self._root
            finally:
                if close_source:
                    source.close()

    class iterparse:
        """Parses an XML section into an element tree incrementally.

        Reports what’s going on to the user. 'source' is a filename or file
        object containing XML data. 'events' is a list of events to report back.
        The supported events are the strings "start", "end", "start-ns" and
        "end-ns" (the "ns" events are used to get detailed namespace
        information). If 'events' is omitted, only "end" events are reported.
        'parser' is an optional parser instance. If not given, the standard
        XMLParser parser is used. Returns an iterator providing
        (event, elem) pairs.
        """

        root = None
        def __init__(self, file, events=None, parser=None):
            self._close_file = False
            if not hasattr(file, 'read'):
                file = open(file, 'rb')
                self._close_file = True
            self._file = file
            self._events = []
            self._index = 0
            self._error = None
            self.root = self._root = None
            if parser is None:
                parser = XMLParser(target=TreeBuilder())
            self._parser = parser
            self._parser._setevents(self._events, events)

        def __next__(self):
            while True:
                try:
                    item = self._events[self._index]
                    self._index += 1
                    return item
                except IndexError:
                    pass
                if self._error:
                    e = self._error
                    self._error = None
                    raise e
                if self._parser is None:
                    self.root = self._root
                    if self._close_file:
                        self._file.close()
                    raise StopIteration
                # load event buffer
                del self._events[:]
                self._index = 0
                data = self._file.read(16384)
                if data:
                    try:
                        self._parser.feed(data)
                    except SyntaxError as exc:
                        self._error = exc
                else:
                    self._root = self._parser.close()
                    self._parser = None

        def __iter__(self):
            return self

    def XML(text, parser=None):
        if not parser:
            parser = XMLParser(target=TreeBuilder())
        parser.feed(text)
        return parser.close()

    fromstring = XML

    def fromstringlist(sequence, parser=None):
        if not parser:
            parser = XMLParser(target=TreeBuilder())
        for text in sequence:
            parser.feed(text)
        return parser.close()

    def XMLID(text, parser=None):
        if not parser:
            parser = XMLParser(target=TreeBuilder())
        parser.feed(text)
        tree = parser.close()
        ids = {}
        for elem in tree.iter():
            id = elem.get("id")
            if id:
                ids[id] = elem
        return tree, ids

    def tostring(element, encoding=None, method=None):
        stream = io.StringIO() if encoding == 'unicode' else io.BytesIO()
        ElementTree(element).write(stream, encoding, method=method)
        return stream.getvalue()

    def tostringlist(element, encoding=None, method=None):
        lst = []
        stream = _ListDataStream(lst)
        ElementTree(element).write(stream, encoding, method=method)
        return lst

    def dump(elem):
        if not isinstance(elem, ElementTree):
            elem = ElementTree(elem)
        elem.write(sys.stdout, encoding="unicode")
        tail = elem.getroot().tail
        if not tail or tail[-1] != "\n":
            sys.stdout.write("\n")

    def parse(source, parser=None):
        tree = ElementTree()
        tree.parse(source, parser)
        return tree

    XMLTreeBuilder = XMLParser
