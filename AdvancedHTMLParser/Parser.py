'''
    Copyright (c) 2015, 2016, 2017, 2018 Tim Savannah under LGPLv3. All Rights Reserved.

    See LICENSE (https://gnu.org/licenses/lgpl-3.0.txt) for more information.


    Parser Implementation
'''

# In general below, all "tag names" (body, div, etc) should be lowercase. The parser will lowercase internally. All attribute names (like `id` in id="123") provided to search functions should be lowercase. Values are not lowercase. This is because doing tons of searches, lowercasing every search can quickly build up. Lowercase it once in your code, not every time you call a function.

import re
import sys
import uuid

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

from collections import defaultdict

from .constants import IMPLICIT_SELF_CLOSING_TAGS, INVISIBLE_ROOT_TAG, INVISIBLE_ROOT_TAG_START, INVISIBLE_ROOT_TAG_END
from .exceptions import MultipleRootNodeException
from .Tags import AdvancedTag, TagCollection, canFilterTags, FilterableTagCollection

import codecs

from .utils import stripIEConditionals, addStartTag

__all__ = ('AdvancedHTMLParser', 'IndexedAdvancedHTMLParser')

def isInvisibleRootTag(tag):
    '''
        isInvisibleRootTag - Check if #tag is a the special root tag when there are multiple root elements.

        @param tag <AdvancedTag> - A tag

        @return <bool> - True if tag is the "fake" root tag used when multiple elements are at root level, otherwise False.
    '''
    return bool(tag.tagName == INVISIBLE_ROOT_TAG)

class AdvancedHTMLParser(HTMLParser):
    '''
        AdvancedHTMLParser - This class parses and allows searching of  documents
    '''

    def __init__(self, filename=None, encoding='utf-8'):
        '''
            __init__ - Creates an Advanced HTML parser object. For read-only parsing, consider IndexedAdvancedHTMLParser for faster searching.

                @param filename <str>         - Optional filename to parse. Otherwise use parseFile or parseStr methods.
                @param encoding <str>         - Specifies the document encoding. Default utf-8

        '''
        HTMLParser.__init__(self)
        # Do not automatically convert charrefs in python3
        self.convert_charrefs = False

        # Encoding to use for this document
        self.encoding = encoding

        self._inTag = []
        self.root = None
        self.doctype = None

        self.reset = self._reset # Must assign after first call, otherwise members won't yet be present

        if filename is not None:
            self.parseFile(filename)

###########################################
#####        INTERNAL               #######
###########################################

    def __getstate__(self):
        '''
            __getstate__ - Get state for pickling

                @return <dict>
        '''
        state = self.__dict__

        # Python2 compat
        del state['reset']

        return state

    def __setstate__(self, state):
        '''
            __setstate - Restore state for loading pickle

                @param state <dict> - The state
        '''
        for key, value in state.items():
            setattr(self, key, value)

        # Python2 compat
        self.reset = self._reset


    def _hasTagInParentLine(self, tag, root):
        if tag == root or tag.parentNode == root:
            return True
        if tag.parentNode is None:
            return False
        return self._hasTagInParentLine(tag.parentNode, root)

    def _handleRootArg(self, root):
        # Check if tag is string of root and apply to real root.
        # If real root is unparsed: raise an error.
        # Otherwise: return passed arg.
        # Return is tuple (root, isRoot)
        if root == 'root' or root == self.root:
            return (self.root, True)
        return (root, False)

    ######## Parsing #########

    def handle_starttag(self, tagName, attributeList, isSelfClosing=False):
        '''
            Internal for parsing
        '''
        tagName = tagName.lower()
        inTag = self._inTag

        if isSelfClosing is False and tagName in IMPLICIT_SELF_CLOSING_TAGS:
            isSelfClosing = True

        newTag = AdvancedTag(tagName, attributeList, isSelfClosing, ownerDocument=self)
        if self.root is None:
            self.root = newTag
        elif len(inTag) > 0:
            inTag[-1].appendChild(newTag)
        else:
            raise MultipleRootNodeException()

        if isSelfClosing is False:
            inTag.append(newTag)

        return newTag

    def handle_startendtag(self, tagName, attributeList):
        '''
            Internal for parsing
        '''
        return self.handle_starttag(tagName, attributeList, True)

    def handle_endtag(self, tagName):
        '''
            Internal for parsing
        '''
        try:
            foundIt = False
            inTag = self._inTag
            for i in range(len(inTag)):
                if inTag[i].tagName == tagName:
                    foundIt = True
                    break

            if not foundIt:
                return
            # Handle closing tags which should have been closed but weren't
            while inTag[-1].tagName != tagName:
                inTag.pop()

            inTag.pop()
        except:
            pass


    def handle_data(self, data):
        '''
            Internal for parsing
        '''
        if data:
            inTag = self._inTag
            if len(inTag) > 0:
                inTag[-1].appendText(data)
            elif data.strip(): #and not self.getRoot():
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

###########################################
#####        Public                 #######
###########################################

    def getRoot(self):
        '''
            getRoot - returns the root Tag.

              NOTE: if there are multiple roots, this will be a special tag.
               You may want to consider using getRootNodes instead if this
               is a possible situation for you.

            @return AdvancedTag
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

    def getAllNodes(self):
        '''
            getAllNodes - Get every element

            @return TagCollection<AdvancedTag>
        '''

        ret = TagCollection()

        for rootNode in self.getRootNodes():
            ret.append(rootNode)

            ret += rootNode.getAllChildNodes()

        return ret

    def setRoot(self, root):
        '''
            Sets the root node, and reprocesses the indexes
        '''
        self.root = root

    def getElementsByTagName(self, tagName, root='root'):
        '''
            getElementsByTagName - Searches and returns all elements with a specific tag name.

                @param tagName <lowercase str> - A lowercase string of the tag name.
                @param root <AdvancedTag/'root'> - Search starting at a specific node, if provided. if string 'root', the root of the parsed tree will be used.
        '''
        (root, isFromRoot) = self._handleRootArg(root)

        elements = []

        if isFromRoot is True and root.tagName == tagName:
            elements.append(root)

        getElementsByTagName = self.getElementsByTagName
        for child in root.children:

            if child.tagName == tagName:
                elements.append(child)

            elements += getElementsByTagName(tagName, child)

        return TagCollection(elements)

    def getElementsByName(self, name, root='root'):
        '''
            getElementsByName - Searches and returns all elements with a specific name.

                @param name <str> - A string of the name attribute
                @param root <AdvancedTag/'root'> - Search starting at a specific node, if provided. if string 'root' [default], the root of the parsed tree will be used.
        '''
        (root, isFromRoot) = self._handleRootArg(root)

        elements = []

        if isFromRoot is True and root.name == name:
            elements.append(root)

        getElementsByName = self.getElementsByName
        for child in root.children:

            if child.getAttribute('name') == name:
                elements.append(child)

            elements += getElementsByName(name, child)

        return TagCollection(elements)

    def getElementById(self, _id, root='root'):
        '''
            getElementById - Searches and returns the first (should only be one) element with the given ID.

                @param id <str> - A string of the id attribute.
                @param root <AdvancedTag/'root'> - Search starting at a specific node, if provided. if string 'root' [default], the root of the parsed tree will be used.
        '''
        (root, isFromRoot) = self._handleRootArg(root)

        if isFromRoot is True and root.id == _id:
            return root

        getElementById = self.getElementById
        for child in root.children:

            if child.getAttribute('id') == _id:
                return child

            potential = getElementById(_id, child)
            if potential is not None:
                return potential

        return None

    def getElementsByClassName(self, className, root='root'):
        '''
            getElementsByClassName - Searches and returns all elements containing a given class name.

                @param className <str> - A one-word class name
                @param root <AdvancedTag/'root'> - Search starting at a specific node, if provided. if string 'root' [default], the root of the parsed tree will be used.
        '''
        (root, isFromRoot) = self._handleRootArg(root)

        elements = []

        if isFromRoot is True and className in root.classNames:
            elements.append(root)

        getElementsByClassName = self.getElementsByClassName
        for child in root.children:

            if className in child.classNames:
                elements.append(child)

            elements += getElementsByClassName(className, child)

        return TagCollection(elements)

    def getElementsByAttr(self, attrName, attrValue, root='root'):
        '''
            getElementsByAttr - Searches the full tree for elements with a given attribute name and value combination. This is always a full scan.

                @param attrName <lowercase str> - A lowercase attribute name
                @param attrValue <str> - Expected value of attribute
                @param root <AdvancedTag/'root'> - Search starting at a specific node, if provided. if string 'root', the root of the parsed tree will be used.
        '''
        (root, isFromRoot) = self._handleRootArg(root)

        elements = []

        if isFromRoot is True and root.getAttribute(attrName) == attrValue:
            elements.append(root)

        getElementsByAttr = self.getElementsByAttr
        for child in root.children:

            if child.getAttribute(attrName) == attrValue:
                elements.append(child)

            elements += getElementsByAttr(attrName, attrValue, child)

        return TagCollection(elements)

    def getElementsWithAttrValues(self, attrName, attrValues, root='root'):
        '''
            getElementsWithAttrValues - Returns elements with an attribute, named by #attrName contains one of the values in the list, #values

            @param attrName <lowercase str> - A lowercase attribute name
            @param attrValues set<str> - A set of all valid values.


            @return - TagCollection of all matching elements

        '''
        (root, isFromRoot) = self._handleRootArg(root)

        if type(attrValues) != set:
            attrValues = set(attrValues)

        return root.getElementsWithAttrValues(attrName, attrValues)


    def getElementsCustomFilter(self, filterFunc, root='root'):
        '''
            getElementsCustomFilter - Scan elements using a provided function

            @param filterFunc <function>(node) - A function that takes an AdvancedTag as an argument, and returns True if some arbitrary criteria is met

            @return - TagCollection of all matching elements
        '''
        (root, isFromRoot) = self._handleRootArg(root)

        elements = []

        if isFromRoot is True and filterFunc(root) is True:
            elements.append(root)

        getElementsCustomFilter = self.getElementsCustomFilter
        for child in root.children:

            if filterFunc(child) is True:
                elements.append(child)

            elements += getElementsCustomFilter(filterFunc, child)

        return TagCollection(elements)


    def getFirstElementCustomFilter(self, filterFunc, root='root'):
        '''
            getFirstElementCustomFilter - Scan elements using a provided function, stop and return the first match.

                @see getElementsCustomFilter to match multiple elements

            @param filterFunc <function>(node) - A function that takes an AdvancedTag as an argument, and returns True if some arbitrary criteria is met

            @return - An AdvancedTag of the node that matched, or None if no match.
        '''
        (root, isFromRoot) = self._handleRootArg(root)

        elements = []

        if isFromRoot is True and filterFunc(root) is True:
            return root

        getFirstElementCustomFilter = self.getFirstElementCustomFilter

        for child in root.children:

            if filterFunc(child) is True:
                return child

            subRet = getFirstElementCustomFilter(filterFunc, child)

            if subRet:
                return subRet

        return None

    @property
    def body(self):
        '''
            body - Get the body element

            @return <AdvancedTag> - The body tag, or None if no body tag present
        '''
        return self.getFirstElementCustomFilter(lambda em : em.tagName == 'body')

    @property
    def head(self):
        '''
            head - Get the head element

            @return <AdvancedTag> - The head tag, or None if no head tag present
        '''
        return self.getFirstElementCustomFilter(lambda em : em.tagName == 'head')

    @property
    def forms(self):
        '''
            forms - Return all forms associated with this document

            @return <TagCollection> - All "form" elements
        '''

        return self.getElementsByTagName('form')

    def contains(self, em):
        '''
            Checks if #em is found anywhere within this element tree

            @param em <AdvancedTag> - Tag of interest

            @return <bool> - If element #em is within this tree
        '''
        for rootNode in self.getRootNodes():
            if rootNode.contains(em):
                return True

        return False

    __contains__ = contains

    def containsUid(self, uid):
        '''
            Check if #uid is found anywhere within this element tree

            @param uid <uuid.UUID> - Uid

            @return <bool> - If #uid is found within this tree
        '''
        for rootNode in self.getRootNodes():
            if rootNode.containsUid(uid):
                return True

        return False

    def __contains__(self, other):
        if isinstance(other, uuid.UUID):
            return self.containsUid(other)
        elif issubclass(other.__class__, AdvancedTag):
            return self.contains(other)
        else:
            raise TypeError('Invalid operand, should be either a uuid.UUID object or an AdvancedTag')


    def filter(self, **kwargs):
        '''
            filter aka filterAnd - Filter ALL the elements in this DOM.

            Results must match ALL the filter criteria. for ANY, use the *Or methods

            Requires the QueryableList module to be installed (i.e. AdvancedHTMLParser was installed
              without '--no-deps' flag.)

            For alternative without QueryableList,
              consider #AdvancedHTMLParser.AdvancedHTMLParser.find method or the getElement* methods

            Special Keys:

               tagname - The tag name
               text    - The inner text

            @return TagCollection<AdvancedTag>
        '''
        if canFilterTags is False:
            raise NotImplementedError('filter methods requires QueryableList installed, it is not. Either install QueryableList, or try the less-robust "find" method, or the getElement* methods.')

        allNodes = self.getAllNodes()

        filterableNodes = FilterableTagCollection(allNodes)

        return filterableNodes.filterAnd(**kwargs)

    filterAnd = filter

    def filterOr(self, **kwargs):
        '''
            filterOr - Perform a filter operation on this node and all children (and their children, onto the end)

            Results must match ANY the filter criteria. for ALL, use the *AND methods

            For special filter keys, @see #AdvancedHTMLParser.AdvancedHTMLParser.filter

            Requires the QueryableList module to be installed (i.e. AdvancedHTMLParser was installed
              without '--no-deps' flag.)

            For alternative, consider AdvancedHTMLParser.AdvancedHTMLParser.find method or the getElement* methods

            @return TagCollection<AdvancedTag>
        '''
        if canFilterTags is False:
            raise NotImplementedError('filter methods requires QueryableList installed, it is not. Either install QueryableList, or try the less-robust "find" method, or the getElement* methods.')

        allNodes = self.getAllNodes() + [self]

        filterableNodes = FilterableTagCollection(allNodes)

        return filterableNodes.filterOr(**kwargs)

    def find(self, **kwargs):
        '''
            find - Perform a search of elements using attributes as keys and potential values as values

               (i.e.  parser.find(name='blah', tagname='span')  will return all elements in this document
                 with the name "blah" of the tag type "span" )

            Arguments are key = value, or key can equal a tuple/list of values to match ANY of those values.

            Append a key with __contains to test if some strs (or several possible strs) are within an element
            Append a key with __icontains to perform the same __contains op, but ignoring case

            Special keys:

               tagname    - The tag name of the element
               text       - The text within an element

            NOTE: Empty string means both "not set" and "no value" in this implementation.

            NOTE: If you installed the QueryableList module (i.e. ran setup.py without --no-deps) it is
              better to use the "filter"/"filterAnd" or "filterOr" methods, which are also available
              on all tags and tag collections (tag collections also have filterAllAnd and filterAllOr)


            @return TagCollection<AdvancedTag> - A list of tags that matched the filter criteria
        '''

        if not kwargs:
            return TagCollection()


        # Because of how closures work in python, need a function to generate these lambdas
        #  because the closure basically references "current key in iteration" and not
        #  "actual instance" of variable. Seems to me to be a bug... but whatever
        def _makeTagnameLambda(tagName):
            return lambda em : em.tagName == tagName

        def _makeAttributeLambda(_key, _value):
            return lambda em : em.getAttribute(_key, '') == _value

        def _makeTagnameInLambda(tagNames):
            return lambda em : em.tagName in tagNames

        def _makeAttributeInLambda(_key, _values):
            return lambda em : em.getAttribute(_key, '') in _values

        def _makeTextLambda(_value):
            return lambda em : em.text == _value

        def _makeTextInLambda(_values):
            return lambda em : em.text in _values

        def _makeAttributeContainsLambda(_key, _value, icontains=False):
            if icontains is False:
                return lambda em : _value in em.getAttribute(_key, '')
            else:
                _value = _value.lower()
                return lambda em : _value in em.getAttribute(_key, '').lower()

        def _makeTextContainsLambda(_value, icontains=False):
            if icontains is False:
                return lambda em : _value in em.text
            else:
                _value = _value.lower()
                return lambda em : _value in em.text.lower()

        def _makeAttributeContainsInLambda(_key, _values, icontains=False):
            if icontains:
                _values = tuple([x.lower() for x in _values])

            def _testFunc(em):
                attrValue = em.getAttribute(_key, '')
                if icontains:
                    attrValue = attrValue.lower()

                for value in _values:
                    if value in attrValue:
                        return True

                return False

            return _testFunc

        def _makeTextContainsInLambda(_values, icontains=False):
            if icontains:
                _values = tuple([x.lower() for x in _values])

            def _testFunc(em):
                text = em.text
                if icontains:
                    text = text.lower()

                for value in _values:
                    if value in text:
                        return True

                return False

            return _testFunc

        # This will hold all the functions we will chain for matching
        matchFunctions = []

        # Iterate over all the filter portions, and build a filter.
        for key, value in kwargs.items():
            key = key.lower()

            endsIContains = key.endswith('__icontains')
            endsContains = key.endswith('__contains')

            isValueList = isinstance(value, (list, tuple))

            thisFunc = None

            if endsIContains or endsContains:
                key = re.sub('__[i]{0,1}contains$', '', key)
                if key == 'tagname':
                    raise ValueError('tagname is not supported for contains')

                if isValueList:
                    if key == 'text':
                        thisFunc = _makeTextContainsInLambda(value, icontains=endsIContains)
                    else:
                        thisFunc = _makeAttributeContainsLambda(key, value, icontains=endsIContains)
                else:
                    if key == 'text':
                        thisFunc = _makeTextContainsLambda(value, icontains=endsIContains)
                    else:
                        thisFunc = _makeAttributeContainsLambda(key, value, icontains=endsIContains)

            else:
                # Not contains, straight up

                if isValueList:
                    if key == 'tagname':
                        thisFunc = _makeTagnameInLambda(value)
                    elif key == 'text':
                        thisFunc = _makeTextInLambda(value)
                    else:
                        thisFunc = _makeAttributeInLambda(key, value)
                else:
                    if key == 'tagname':
                        thisFunc = _makeTagnameLambda(value)
                    elif key == 'text':
                        thisFunc = _makeTextLambda(value)
                    else:
                        thisFunc = _makeAttributeLambda(key, value)


            matchFunctions.append( thisFunc )

        # The actual matching function - This will run through the assembled
        #  #matchFunctions list, testing the element against each match
        #  and returning all elements in a TagCollection that match this list.
        def doMatchFunc(em):
            for matchFunction in matchFunctions:
                if matchFunction(em) is False:
                    return False

            return True

        return self.getElementsCustomFilter(doMatchFunc)


    def getHTML(self):
        '''
            getHTML - Get the full HTML as contained within this tree.

                If parsed from a document, this will contain the original whitespacing.

                @returns - <str> of html

                    @see getFormattedHTML

                    @see getMiniHTML
        '''
        root = self.getRoot()
        if root is None:
            raise ValueError('Did not parse anything. Use parseFile or parseStr')

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


    # toHTML - Alias of getHTML
    toHTML = getHTML

    # asHTML - Alias of getHTML
    asHTML = getHTML


    def getFormattedHTML(self, indent='  '):
        '''
            getFormattedHTML - Get formatted and xhtml of this document, replacing the original whitespace
                with a pretty-printed version

            @param indent - space/tab/newline of each level of indent, or integer for how many spaces per level

            @return - <str> Formatted html

            @see getHTML - Get HTML with original whitespace

            @see getMiniHTML - Get HTML with only functional whitespace remaining
        '''
        from .Formatter import AdvancedHTMLFormatter
        html = self.getHTML()
        formatter = AdvancedHTMLFormatter(indent, None) # Do not double-encode
        formatter.feed(html)
        return formatter.getHTML()

    def getMiniHTML(self):
        '''
            getMiniHTML - Gets the HTML representation of this document without any pretty formatting
                and disregarding original whitespace beyond the functional.

                @return <str> - HTML with only functional whitespace present
        '''
        from .Formatter import AdvancedHTMLMiniFormatter
        html = self.getHTML()
        formatter = AdvancedHTMLMiniFormatter(None) # Do not double-encode
        formatter.feed(html)
        return formatter.getHTML()

    def _reset(self):
        '''
            _reset - reset this object. Assigned to .reset after __init__ call.
        '''
        HTMLParser.reset(self)

        self.root = None
        self.doctype = None
        self._inTag = []

    def feed(self, contents):
        '''
            feed - Feed contents. Use  parseStr or parseFile instead.

            @param contents - Contents
        '''
        contents = stripIEConditionals(contents)
        try:
            HTMLParser.feed(self, contents)
        except MultipleRootNodeException:
            self.reset()
            HTMLParser.feed(self, "%s%s" %(addStartTag(contents, INVISIBLE_ROOT_TAG_START), INVISIBLE_ROOT_TAG_END))

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


    def createElement(self, tagName):
        '''
            createElement - Create an unattached tag with the given tag name

            @param tagName <str> - Name of tag

            @return <AdvancedTag> - A tag with the given tag name
        '''
        return AdvancedTag(tagName=tagName.lower())


    @classmethod
    def createElementFromHTML(cls, html, encoding='utf-8'):
        '''
            createElementFromHTML - Creates an element from a string of HTML.

                If this could create multiple root-level elements (children are okay),
                  you must use #createElementsFromHTML which returns a list of elements created.

            @param html <str> - Some html data

            @param encoding <str> - Encoding to use for document

            @raises MultipleRootNodeException - If given html would produce multiple root-level elements (use #createElementsFromHTML instead)

            @return AdvancedTag - A single AdvancedTag

            NOTE: If there is text outside the tag, they will be lost in this.
              Use createBlocksFromHTML instead if you need to retain both text and tags.

              Also, if you are just appending to an existing tag, use AdvancedTag.appendInnerHTML
        '''

        parser = cls(encoding=encoding)

        html = stripIEConditionals(html)
        try:
            HTMLParser.feed(parser, html)
        except MultipleRootNodeException:
            raise MultipleRootNodeException('Multiple nodes passed to createElementFromHTML method. Use #createElementsFromHTML instead to get a list of AdvancedTag elements.')

        rootNode = parser.getRoot()
        rootNode.remove()

        return rootNode


    @classmethod
    def createElementsFromHTML(cls, html, encoding='utf-8'):
        '''
            createElementsFromHTML - Creates elements from provided html, and returns a list of the root-level elements
                children of these root-level nodes are accessable via the usual means.

            @param html <str> - Some html data

            @param encoding <str> - Encoding to use for document

            @return list<AdvancedTag> - The root (top-level) tags from parsed html.

            NOTE: If there is text outside the tags, they will be lost in this.
              Use createBlocksFromHTML instead if you need to retain both text and tags.

              Also, if you are just appending to an existing tag, use AdvancedTag.appendInnerHTML
        '''
        # TODO: If text is present outside a tag, it will be lost.

        parser = cls(encoding=encoding)

        parser.parseStr(html)

        rootNode = parser.getRoot()

        rootNode.remove() # Detatch from temp document

        if isInvisibleRootTag(rootNode):
            return rootNode.children

        return [rootNode]

    @classmethod
    def createBlocksFromHTML(cls, html, encoding='utf-8'):
        '''
            createBlocksFromHTML - Returns the root level node (unless multiple nodes), and
                a list of "blocks" added (text and nodes).

            @return list< str/AdvancedTag > - List of blocks created. May be strings (text nodes) or AdvancedTag (tags)

            NOTE:
                Results may be checked by:

                    issubclass(block.__class__, AdvancedTag)

                If True, block is a tag, otherwise, it is a text node
        '''

        parser = cls(encoding=encoding)

        parser.parseStr(html)

        rootNode = parser.getRoot()

        rootNode.remove()

        return rootNode.blocks


class IndexedAdvancedHTMLParser(AdvancedHTMLParser):
    '''
        An AdvancedHTMLParser that indexes for much much faster searching. If you are doing searching/validation, this is your bet.
          If you are writing/modifying, you may use this, but be sure to call reindex() after changes.
    '''

    def __init__(self, filename=None, encoding='utf-8', indexIDs=True, indexNames=True, indexClassNames=True, indexTagNames=True):
        '''
            __init__ - Creates an Advanced HTML parser object, with specific indexing settings.

                For the various index* arguments, if True the index will be collected and use (if useIndex=True [default] on get* function)

                @param filename <str>         - Optional filename to parse. Otherwise use parseFile or parseStr methods.
                @param encoding <str> - Specifies the document encoding. Default utf-8
                @param indexIDs <bool>        - True to create an index for getElementByID method.  <default True>
                @param indexNames <bool>      - True to create an index for getElementsByName method  <default True>
                @param indexClassNames <bool> - True to create an index for getElementsByClassName method. <default True>
                @param indexTagNames <bool>   - True to create an index for tag names. <default True>

                For indexing other attributes, see the more generic addIndexOnAttribute

        '''
        self.indexFunctions = []
        self.otherAttributeIndexFunctions = {}
        self._otherAttributeIndexes = {}
        self.indexIDs = indexIDs
        self.indexNames = indexNames
        self.indexClassNames = indexClassNames
        self.indexTagNames = indexTagNames

        self._resetIndexInternal()

        AdvancedHTMLParser.__init__(self, filename, encoding)

        if filename is not None:
            self.parseFile(filename)

###########################################
#####        INTERNAL               #######
###########################################

    def _resetIndexInternal(self):
        self.indexFunctions = []
        if self.indexIDs is True:
            self.indexFunctions.append(self._indexID)
        if self.indexNames is True:
            self.indexFunctions.append(self._indexName)
        if self.indexClassNames is True:
            self.indexFunctions.append(self._indexClassName)
        if self.indexTagNames is True:
            self.indexFunctions.append(self._indexTagName)

        self._idMap = {}
        self._nameMap = defaultdict(list)
        self._classNameMap = defaultdict(list)
        self._tagNameMap = defaultdict(list)
        for key in self._otherAttributeIndexes:
            self._otherAttributeIndexes[key] = {}
#        self._otherAttributeIndexes = {}

    ######## Specific Indexing Functions #######

    def _indexID(self, tag):
        _id = tag.getAttribute('id')
        if _id:
            self._idMap[_id] = tag

    def _indexName(self, tag):
        name = tag.getAttribute('name')
        if name:
            self._nameMap[name].append(tag)

    def _indexClassName(self, tag):
        classNames = tag.classNames
        for className in classNames:
            self._classNameMap[className].append(tag)

    def _indexTagName(self, tag):
        self._tagNameMap[tag.tagName].append(tag)


    ######### Index parent functions #########

    def _indexTag(self, tag):
        for indexFunction in self.indexFunctions:
            indexFunction(tag)

        for attributeIndexFunction in self.otherAttributeIndexFunctions.values():
            attributeIndexFunction(self, tag)

    def _indexTagRecursive(self, tag):
        self._indexTag(tag)

        _indexTagRecursive = self._indexTagRecursive
        for child in tag.children:
            _indexTagRecursive(child)

    ######## Parsing #########

    def handle_starttag(self, tagName, attributeList, isSelfClosing=False):
        '''
            internal for parsing
        '''
        newTag = AdvancedHTMLParser.handle_starttag(self, tagName, attributeList, isSelfClosing)
        self._indexTag(newTag)

        return newTag

    def setRoot(self, root):
        '''
            Sets the root node, and reprocesses the indexes

            @param root - AdvancedTag for root
        '''
        AdvancedHTMLParser.setRoot(self, root)
        self.reindex()

##########################################################
#                 Public
##########################################################

    # This should be called if you modify a parsed tree at an element level, then search it.
    def reindex(self, newIndexIDs=None, newIndexNames=None, newIndexClassNames=None, newIndexTagNames=None):
        '''
            reindex - reindex the tree. Optionally, change what fields are indexed.

                @param newIndexIDs <bool/None>        - None to leave same, otherwise new value to index IDs
                @parma newIndexNames <bool/None>      - None to leave same, otherwise new value to index names
                @param newIndexClassNames <bool/None> - None to leave same, otherwise new value to index class names
                @param newIndexTagNames <bool/None>   - None to leave same, otherwise new value to index tag names
        '''
        if newIndexIDs is not None:
            self.indexIDs = newIndexIDs
        if newIndexNames is not None:
            self.indexNames = newIndexNames
        if newIndexClassNames is not None:
            self.newIndexClassNames = newIndexClassNames
        if newIndexTagNames is not None:
            self.newIndexTagNames = newIndexTagNames

        self._resetIndexInternal()
        self._indexTagRecursive(self.root)

    def disableIndexing(self):
        '''
            disableIndexing - Disables indexing. Consider using plain AdvancedHTMLParser class.
              Maybe useful in some scenarios where you want to parse, add a ton of elements, then index
              and do a bunch of searching.
        '''
        self.indexIDs = self.indexNames = self.indexClassNames = self.indexTagNames = False
        self._resetIndexInternal()

    def addIndexOnAttribute(self, attributeName):
        '''
            addIndexOnAttribute - Add an index for an arbitrary attribute. This will be used by the getElementsByAttr function.
                You should do this prior to parsing, or call reindex. Otherwise it will be blank. "name" and "id" will have no effect.

                @param attributeName <lowercase str> - An attribute name. Will be lowercased.
        '''
        attributeName = attributeName.lower()
        self._otherAttributeIndexes[attributeName] = {}

        def _otherIndexFunction(self, tag):
            thisAttribute = tag.getAttribute(attributeName)
            if thisAttribute is not None:
                if thisAttribute not in self._otherAttributeIndexes[attributeName]:
                    self._otherAttributeIndexes[attributeName][thisAttribute] = []
                self._otherAttributeIndexes[attributeName][thisAttribute].append(tag)


        self.otherAttributeIndexFunctions[attributeName] = _otherIndexFunction

    def removeIndexOnAttribute(self, attributeName):
        '''
            removeIndexOnAttribute - Remove an attribute from indexing (for getElementsByAttr function) and remove indexed data.

        @param attributeName <lowercase str> - An attribute name. Will be lowercased. "name" and "id" will have no effect.
        '''
        attributeName = attributeName.lower()
        if attributeName in self.otherAttributeIndexFunctions:
                del self.otherAttributeIndexFunctions[attributeName]
        if attributeName in self._otherAttributeIndexes:
                del self._otherAttributeIndexes[attributeName]


    def getElementsByTagName(self, tagName, root='root', useIndex=True):
        '''
            getElementsByTagName - Searches and returns all elements with a specific tag name.

                @param tagName <lowercase str> - A lowercase string of the tag name.
                @param root <AdvancedTag/'root'> - Search starting at a specific node, if provided. if string 'root', the root of the parsed tree will be used.
                @param useIndex - If True [default] and tag names are set to be indexed [default, see constructor], only the index will be used. If False, all tags
                  will be searched.
        '''
        (root, isFromRoot) = self._handleRootArg(root)

        if useIndex is True and self.indexTagNames is True:
            elements = self._tagNameMap.get(tagName, []) # Use .get here as to not create a lot of extra indexes on the defaultdict for misses
            if isFromRoot is False:
                _hasTagInParentLine = self._hasTagInParentLine
                elements = [x for x in elements if _hasTagInParentLine(x, root)]

            return TagCollection(elements)

        return AdvancedHTMLParser.getElementsByTagName(self, tagName, root)


    def getElementsByName(self, name, root='root', useIndex=True):
        '''
            getElementsByName - Searches and returns all elements with a specific name.

                @param name <str> - A string of the name attribute
                @param root <AdvancedTag/'root'> - Search starting at a specific node, if provided. if string 'root', the root of the parsed tree will be used.
                @param useIndex <bool> If useIndex is True and names are indexed [see constructor] only the index will be used. Otherwise a full search is performed.
        '''
        (root, isFromRoot) = self._handleRootArg(root)

        elements = []
        if useIndex is True and self.indexNames is True:

            elements = self._nameMap.get(name, [])

            if isFromRoot is False:
                _hasTagInParentLine = self._hasTagInParentLine
                elements = [x for x in elements if _hasTagInParentLine(x, root)]

            return TagCollection(elements)

        return AdvancedHTMLParser.getElementsByName(self, name, root)


    def getElementById(self, _id, root='root', useIndex=True):
        '''
            getElementById - Searches and returns the first (should only be one) element with the given ID.

                @param id <str> - A string of the id attribute.
                @param root <AdvancedTag/'root'> - Search starting at a specific node, if provided. if string 'root', the root of the parsed tree will be used.
                @param useIndex <bool> If useIndex is True and ids are indexed [see constructor] only the index will be used. Otherwise a full search is performed.
        '''
        (root, isFromRoot) = self._handleRootArg(root)

        if self.useIndex is True and self.indexIDs is True:

            element = self._idMap.get(_id, None)

            if isFromRoot is False and element is not None:

                if self._hasTagInParentLine(element, root) is False:
                    element = None

            return element


        return AdvancedHTMLParser.getElementById(self, _id, root)


    def getElementsByClassName(self, className, root='root', useIndex=True):
        '''
            getElementsByClassName - Searches and returns all elements containing a given class name.

                @param className <str> - A one-word class name
                @param root <AdvancedTag/'root'> - Search starting at a specific node, if provided. if string 'root', the root of the parsed tree will be used.
                @param useIndex <bool> If useIndex is True and class names are indexed [see constructor] only the index will be used. Otherwise a full search is performed.
        '''
        (root, isFromRoot) = self._handleRootArg(root)

        if useIndex is True and self.indexClassNames is True:

            elements = self._classNameMap.get(className, [])

            if isFromRoot is False:
                _hasTagInParentLine = self._hasTagInParentLine
                elements = [x for x in elements if _hasTagInParentLine(x, root)]

            return TagCollection(elements)

        return AdvancedHTMLParser.getElementsByClassName(self, className, root)


    def getElementsByAttr(self, attrName, attrValue, root='root', useIndex=True):
        '''
            getElementsByAttr - Searches the full tree for elements with a given attribute name and value combination. If you want multiple potential values, see getElementsWithAttrValues
               If you want an index on a random attribute, use the addIndexOnAttribute function.

                @param attrName <lowercase str> - A lowercase attribute name
                @param attrValue <str> - Expected value of attribute
                @param root <AdvancedTag/'root'> - Search starting at a specific node, if provided. if string 'root', the root of the parsed tree will be used.
                @param useIndex <bool> If useIndex is True and this specific attribute is indexed [see addIndexOnAttribute] only the index will be used. Otherwise a full search is performed.
        '''
        (root, isFromRoot) = self._handleRootArg(root)

        if useIndex is True and attrName in self._otherAttributeIndexes:

            elements = self._otherAttributeIndexes[attrName].get(attrValue, [])

            if isFromRoot is False:
                _hasTagInParentLine = self._hasTagInParentLine
                elements = [x for x in elements if _hasTagInParentLine(x, root)]

            return TagCollection(elements)

        return AdvancedHTMLParser.getElementsByAttr(self, attrName, attrValue, root)


    def getElementsWithAttrValues(self, attrName, values, root='root', useIndex=True):
        '''
            getElementsWithAttrValues - Returns elements with an attribute matching one of several values. For a single name/value combination, see getElementsByAttr

                @param attrName <lowercase str> - A lowercase attribute name
                @param attrValues set<str> - List of expected values of attribute
                @param root <AdvancedTag/'root'> - Search starting at a specific node, if provided. if string 'root', the root of the parsed tree will be used.
                @param useIndex <bool> If useIndex is True and this specific attribute is indexed [see addIndexOnAttribute] only the index will be used. Otherwise a full search is performed.
        '''
        (root, isFromRoot) = self._handleRootArg(root)

        _otherAttributeIndexes = self._otherAttributeIndexes
        if useIndex is True and attrName in _otherAttributeIndexes:

            elements = TagCollection()

            for value in values:
                elements += TagCollection(_otherAttributeIndexes[attrName].get(value, []))

            return elements

        return AdvancedHTMLParser.getElementsWithAttrValues(self, attrName, values, root, useIndex)

    def _reset(self):
        '''
            _reset - reset this object. Assigned to .reset after __init__ call.
        '''
        AdvancedHTMLParser.reset(self)

        self._resetIndexInternal()

#vim: set ts=4 sw=4 expandtab
