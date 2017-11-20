# Copyright (c) 2015, 2017 Tim Savannah under LGPLv3. 
# See LICENSE (https://gnu.org/licenses/lgpl-3.0.txt) for more information.
#   HTML formatting (HTML->XHTML conversion as well)

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


from .constants import PREFORMATTED_TAGS, IMPLICIT_SELF_CLOSING_TAGS, PRESERVE_CONTENTS_TAGS, INVISIBLE_ROOT_TAG, INVISIBLE_ROOT_TAG_START, INVISIBLE_ROOT_TAG_END
from .exceptions import MultipleRootNodeException
from .Tags import AdvancedTag

from .utils import addStartTag, stripIEConditionals

import codecs


__all__ = ('AdvancedHTMLFormatter', )

class AdvancedHTMLFormatter(HTMLParser):
    '''
        A formatter for HTML. Note this does not understand CSS, so if you are enabling preformatted text based on css rules, it will not work.
        It does, however, understand "pre", "code" and "script" tags and will not try to format their contents.
    '''

    def __init__(self, indent='  ', encoding='utf-8'):
        '''
            Create a formatter.

            @param indent - Either a space/tab/newline that represents one level of indent, or an integer to use that number of spaces
            @param encoding - Use this encoding for the document.
        '''
        HTMLParser.__init__(self)

        # Do not automatically convert charrefs in python3
        self.convert_charrefs = False

        self.parsedData = []
        self.reset = self._reset
        self.decl = None
        self.currentIndentLevel = 0
        self.indent = indent
        self.encoding = encoding

        self.inPreformatted = 0

        self.root = None

        self._inTag = []
        self.doctype = None



    def feed(self, contents):
        '''
            feed - Load contents

            @param contents - HTML contents
        '''
        contents = stripIEConditionals(contents)
        try:
            HTMLParser.feed(self, contents)
        except MultipleRootNodeException:
            self.reset()

            HTMLParser.feed(self, "%s%s" %(addStartTag(contents, INVISIBLE_ROOT_TAG_START), INVISIBLE_ROOT_TAG_END))



    def getHTML(self):
        '''
            getHTML - Get the full HTML as contained within this tree, converted to  valid XHTML
                @returns - String
        '''
        root = self.getRoot()
        if root is None:
            raise ValueError('Cannot format, use feed to load contents.')

        if self.doctype:
            doctypeStr = '<!%s>\n' %(self.doctype)
        else:
            doctypeStr = ''

        # 6.6.0: If we have a real root tag, print the outerHTML. If we have a fake root tag (for multiple root condition),
        #   then print the innerHTML (skipping the outer root tag). Otherwise, we will miss
        #   untagged text (between the multiple root nodes).
        rootNode = self.getRoot()
        if rootNode.tagName == INVISIBLE_ROOT_TAG:
            return doctypeStr + rootNode.innerHTML
        else:
            return doctypeStr + rootNode.outerHTML
#        return doctypeStr + ''.join([elem.outerHTML for elem in self.getRootNodes()])

    def getRoot(self):
        '''
            getRoot - returns the root Tag 
                @return - AdvancedTag at root. If you provided multiple root nodes, this will be a "holder" with tagName value as constants.INVISIBLE_ROOT_TAG
        '''
        return self.root

    def getRootNodes(self):
        '''
            getRootNodes - Gets all objects at the "root" (first level; no parent). Use this if you may have multiple roots (not children of <html>)
                Use this method to get objects, for example, in an AJAX request where <html> may not be your root.

                Note: If there are multiple root nodes (i.e. no <html> at the top), getRoot will return a special tag. This function automatically
                  handles that, and returns all root nodes.

                @return list<AdvancedTag> - A list of AdvancedTags which are at the root level of the tree.
        '''
        root = self.root
        if not root:
            return []
        if root.tagName == INVISIBLE_ROOT_TAG:
            return list(root.children)
        return [root]

    def setRoot(self, root):
        '''
            setRoot - Sets the root node, and reprocesses the indexes

            @param root - AdvancedTag to be new root
        '''
        self.root = root

    #####################################
    ##           Internal             ###
    #####################################

    def _reset(self):
        HTMLParser.reset(self)
        self.currentIndentLevel = 0
        self.parsedData = []
        self._inTag = []
        self.root = None
        self.doctype = None
        self.inPreformatted = 0

    def _getIndent(self):
        return '\n' + (self.indent * self.currentIndentLevel)

    def handle_starttag(self, tagName, attributeList, isSelfClosing=False):
        '''
            handle_starttag - Internal for parsing
        '''
        tagName = tagName.lower()
        inTag = self._inTag

        if isSelfClosing is False and tagName in IMPLICIT_SELF_CLOSING_TAGS:
            isSelfClosing = True

        newTag = AdvancedTag(tagName, attributeList, isSelfClosing)
        if self.root is None:
            self.root = newTag
        elif len(inTag) > 0:
            inTag[-1].appendChild(newTag)
        else:
            raise MultipleRootNodeException()

        if self.inPreformatted is 0:
            newTag._indent = self._getIndent()

        if tagName in PREFORMATTED_TAGS:
            self.inPreformatted += 1

        if isSelfClosing is False:
            inTag.append(newTag)
            if tagName != INVISIBLE_ROOT_TAG:
                self.currentIndentLevel += 1


    def handle_startendtag(self, tagName, attributeList):
        '''
            handle_startendtag - Internal for parsing
        '''
        return self.handle_starttag(tagName, attributeList, True)

    def handle_endtag(self, tagName):
        '''
            handle_endtag - Internal for parsing
        '''
        inTag = self._inTag
        try:
            # Handle closing tags which should have been closed but weren't
            foundIt = False
            for i in range(len(inTag)):
                if inTag[i].tagName == tagName:
                    foundIt = True
                    break

            if not foundIt:
                sys.stderr.write('WARNING: found close tag with no matching start.\n')
                return
                
            while inTag[-1].tagName != tagName:
                oldTag = inTag.pop()
                if oldTag.tagName in PREFORMATTED_TAGS:
                    self.inPreformatted -= 1

                self.currentIndentLevel -= 1

            inTag.pop()
            if tagName != INVISIBLE_ROOT_TAG:
                self.currentIndentLevel -= 1
            if tagName in PREFORMATTED_TAGS:
                self.inPreformatted -= 1
        except:
            pass

    def handle_data(self, data):
        '''
            handle_data - Internal for parsing
        '''
        if data:
            inTag = self._inTag
            if len(inTag) > 0:
                if inTag[-1].tagName not in PRESERVE_CONTENTS_TAGS:
                    data = data.replace('\t', ' ').strip('\r\n')
                    if data.startswith(' '):
                        data = ' ' + data.lstrip()
                    if data.endswith(' '):
                        data = data.rstrip() + ' '
                inTag[-1].appendText(data)
            elif data.strip():
                # Must be text prior to or after root node
                raise MultipleRootNodeException()

    def handle_entityref(self, entity):
        '''
            Internal for parsing
        '''
        inTag = self._inTag
        if len(inTag) > 0:
            inTag[-1].appendText('&%s;' %(entity,))
        else:
            raise MultipleRootNodeException()

    def handle_charref(self, charRef):
        '''
            Internal for parsing
        '''
        inTag = self._inTag
        if len(inTag) > 0:
            inTag[-1].appendText('&#%s;' %(charRef,))
        else:
            raise MultipleRootNodeException()

    def handle_comment(self, comment):
        '''
            Internal for parsing
        '''
        inTag = self._inTag
        if len(inTag) > 0:
            inTag[-1].appendText('<!-- %s -->' %(comment,))
        else:
            raise MultipleRootNodeException()

    def handle_decl(self, decl):
        '''
            Internal for parsing
        '''
        self.doctype = decl

    def unknown_decl(self, decl):
        '''
            Internal for parsing
        '''
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
            with codecs.open(filename, 'r', encoding=self.encoding) as f:
                contents = f.read()
        self.feed(contents)

    def parseStr(self, html):
        '''
            parseStr - Parses a string and creates the DOM tree and indexes.

                @param html <str> - valid HTML
        '''
        self.reset()
        if isinstance(html, bytes):
            self.feed(html.decode(self.encoding))
        else:
            self.feed(html)

#vim: set ts=4 sw=4 expandtab
