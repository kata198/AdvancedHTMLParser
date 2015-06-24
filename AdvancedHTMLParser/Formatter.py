
import sys

# Python 2/3 compatibility:
try:
    from HTMLParser import HTMLParser
    pyver = 2
except ImportError:
    from html.parser import HTMLParser
    pyver = 3

try:
    file
except NameError:
    from io import TextIOWrapper as file


from .constants import PREFORMATTED_TAGS, IMPLICIT_SELF_CLOSING_TAGS, PRESERVE_CONTENTS_TAGS
from .exceptions import MultipleRootNodeException
from .Tags import AdvancedTag


class AdvancedHTMLFormatter(HTMLParser):
    '''
        A formatter for HTML. Note this does not understand CSS, so if you are enabling preformatted text based on css rules, it will not work.
        It does, however, understand "pre", "code" and "script" tags and will not try to format their contents.
    '''

    def __init__(self, indent='  ', encoding='utf-8'):
        HTMLParser.__init__(self)

        self.parsedData = []
        self.reset = self._reset
        self.decl = None
        self.currentIndentLevel = 0
        self.indent = indent
        self.encoding = encoding

        self.inPreformatted = 0

        self.root = None

        self.inTag = []
        self.doctype = None



    def feed(self, contents):
        if self.encoding and self.encoding != sys.getdefaultencoding():
            if pyver == 2:
                contents = contents.decode(self.encoding)
            else:
                contents = contents.encode().decode(self.encoding)
        try:
            HTMLParser.feed(self, contents)
        except MultipleRootNodeException:
            self.reset()
            HTMLParser.feed(self, '<xxxblank>' + contents + '</xxxblank>')



    def getHTML(self):
        '''
            getHTML - Get the full HTML as contained within this tree
                @returns - String
        '''
        root = self.getRoot()
        if root is None:
            raise ValueError('Cannot format, use feed to load contents.')

        if self.doctype:
            doctypeStr = '<!%s>\n' %(self.doctype)
        else:
            doctypeStr = ''

        if root.tagName == 'xxxblank': # If we had to add a temp tag, don't include it here.
            return doctypeStr + ''.join([x.outerHTML for x in root.children]) 
        return doctypeStr + root.outerHTML


    def getRoot(self):
        '''
            getRoot - returns the root Tag 
                @return Tag
        '''
        return self.root

    def setRoot(self, root):
        '''
            Sets the root node, and reprocesses the indexes
        '''
        self.root = root

    #####################################
    ##           Internal             ###
    #####################################

    def _reset(self):
        HTMLParser.reset(self)
        self.currentIndentLevel = 0
        self.parsedData = []
        self.inTag = []
        self.root = None
        self.doctype = None
        self.inPreformatted = 0

    def _getIndent(self):
        return '\n' + (self.indent * self.currentIndentLevel)

    def handle_starttag(self, tagName, attributeList, isSelfClosing=False):
        tagName = tagName.lower()

        if isSelfClosing is False and tagName in IMPLICIT_SELF_CLOSING_TAGS:
            isSelfClosing = True

        newTag = AdvancedTag(tagName, attributeList, isSelfClosing)
        if self.root is None:
            self.root = newTag
        elif len(self.inTag) > 0:
            self.inTag[-1].appendChild(newTag)
        else:
            raise MultipleRootNodeException()

        if self.inPreformatted is 0:
            newTag.indent = self._getIndent()

        if tagName in PREFORMATTED_TAGS:
            self.inPreformatted += 1

        if isSelfClosing is False:
            self.inTag.append(newTag)
            if tagName != 'xxxblank':
                self.currentIndentLevel += 1


    def handle_startendtag(self, tagName, attributeList):
        return self.handle_starttag(tagName, attributeList, True)

    def handle_endtag(self, tagName):
        try:
            # Handle closing tags which should have been closed but weren't
            while self.inTag[-1].tagName != tagName:
                oldTag = self.inTag.pop()
                if oldTag.tagName in PREFORMATTED_TAGS:
                    self.inPreformatted -= 1

                self.currentIndentLevel -= 1

            self.inTag.pop()
            if tagName != 'xxxblank':
                self.currentIndentLevel -= 1
            if tagName in PREFORMATTED_TAGS:
                self.inPreformatted -= 1
        except:
            pass

    def handle_data(self, data):
        if data and len(self.inTag) > 0:
            if self.inTag[-1].tagName not in PRESERVE_CONTENTS_TAGS:
                data = data.replace('\t', ' ').strip('\r\n')
                if data.startswith(' '):
                    data = ' ' + data.lstrip()
                if data.endswith(' '):
                    data = data.rstrip() + ' '
            self.inTag[-1].appendText(data)

    def handle_entityref(self, entity):
        if len(self.inTag) > 0:
            self.inTag[-1].appendText('&%s;' %(entity,))

    def handle_charref(self, charRef):
        if len(self.inTag) > 0:
            self.inTag[-1].appendText('&#%s;' %(charRef,))

    def handle_comment(self, comment):
        if len(self.inTag) > 0:
            self.inTag[-1].appendText('<!-- %s -->' %(comment,))

    def handle_decl(self, decl):
        self.doctype = decl

    def unknown_decl(self, decl):
        if not self.doctype:
            self.doctype = decl

    def parseFile(self, filename):
        '''
            parseFile - Parses a file and creates the DOM tree and indexes
    
                @param filename <str/file> - A string to a filename or a file object. If file object, it will not be closed, you must close.
        '''
        self.reset()

        if isinstance(filename, file):
            contents = filename.read()
        else:
            with open(filename, 'r') as f:
                contents = f.read()
        self.feed(contents)

    def parseStr(self, html):
        '''
            parseStr - Parses a string and creates the DOM tree and indexes.

                @param html <str> - valid HTML
        '''
        self.reset()
        self.feed(html)
 
#vim: set ts=4 sw=4 expandtab
