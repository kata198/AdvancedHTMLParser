#!/usr/bin/env python
# Copyright (c) 2015, 2016 Tim Savannah under LGPLv3. See LICENSE (https://gnu.org/licenses/lgpl-3.0.txt) for more information.
#
#   Parser implementation

# In general below, all "tag names" (body, div, etc) should be lowercase. The parser will lowercase internally. All attribute names (like `id` in id="123") provided to search functions should be lowercase. Values are not lowercase. This is because doing tons of searches, lowercasing every search can quickly build up. Lowercase it once in your code, not every time you call a function.

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

from collections import defaultdict

from .constants import IMPLICIT_SELF_CLOSING_TAGS, INVISIBLE_ROOT_TAG, INVISIBLE_ROOT_TAG_START, INVISIBLE_ROOT_TAG_END
from .exceptions import MultipleRootNodeException
from .Tags import AdvancedTag, TagCollection

import codecs

from .utils import stripIEConditionals, addStartTag

class AdvancedHTMLParser(HTMLParser):
    '''
        AdvancedHTMLParser - This class parses and allows searching of  documents
    '''

    def __init__(self, filename=None, encoding='utf-8'):
        '''
            __init__ - Creates an Advanced HTML parser object. For read-only parsing, consider IndexedAdvancedHTMLPaser for faster searching.

                @param filename <str>         - Optional filename to parse. Otherwise use parseFile or parseStr methods.
                @param encoding <str>         - Specifies the document encoding. Default utf-8
                                            
        '''
        HTMLParser.__init__(self)
        # Do not automatically convert charrefs in python3
        self.convert_charrefs = False

        self.encoding = encoding

        self.inTag = []
        self.root = None
        self.doctype = None

        self.reset = self._reset # Must assign after first call, otherwise members won't yet be present

        if filename is not None:
            self.parseFile(filename)

###########################################
#####        INTERNAL               #######
###########################################


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

        if isSelfClosing is False and tagName in IMPLICIT_SELF_CLOSING_TAGS:
            isSelfClosing = True

        newTag = AdvancedTag(tagName, attributeList, isSelfClosing)
        if self.root is None:
            self.root = newTag
        elif len(self.inTag) > 0:
            self.inTag[-1].appendChild(newTag)
        else:
            raise MultipleRootNodeException()

        if isSelfClosing is False:
            self.inTag.append(newTag)

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
            for i in range(len(self.inTag)):
                if self.inTag[i].tagName == tagName:
                    foundIt = True
                    break

            if not foundIt:
                return
            # Handle closing tags which should have been closed but weren't
            while self.inTag[-1].tagName != tagName:
                self.inTag.pop()

            self.inTag.pop()
        except:
            pass


    def handle_data(self, data):
        '''
            Internal for parsing
        '''
        if data:
            if len(self.inTag) > 0:
                self.inTag[-1].appendText(data)
            elif data.strip(): #and not self.getRoot():
                # Must be text prior to or after root node
                raise MultipleRootNodeException()

    def handle_entityref(self, entity):
        '''
            Internal for parsing
        '''
        if len(self.inTag) > 0:
            self.inTag[-1].appendText('&%s;' %(entity,))
        else:
            raise MultipleRootNodeException()

    def handle_charref(self, charRef):
        '''
            Internal for parsing
        '''
        if len(self.inTag) > 0:
            self.inTag[-1].appendText('&#%s;' %(charRef,))
        else:
            raise MultipleRootNodeException()

    def handle_comment(self, comment):
        '''
            Internal for parsing
        '''
        if len(self.inTag) > 0:
            self.inTag[-1].appendText('<!-- %s -->' %(comment,))
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
            getRoot - returns the root Tag 
                @return Tag
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

        for child in root.children:
            if child.tagName == tagName:
                elements.append(child)
            elements += self.getElementsByTagName(tagName, child)
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

        for child in root.children:
            if child.attributes.get('name') == name:
                elements.append(child)
            elements += self.getElementsByName(name, child)

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

        for child in root.children:
            if child.attributes.get('id') == _id:
                return child
            potential = self.getElementById(_id, child)
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

        for child in root.children:
            if className in child.classNames:
                elements.append(child)
            elements += self.getElementsByClassName(className, child)
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

        for child in root.children:
            if child.attributes.get(attrName) == attrValue:
                elements.append(child)
            elements += self.getElementsByAttr(attrName, attrValue, child)
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

        for child in root.children:
            if filterFunc(child) is True:
                elements.append(child)
            elements += self.getElementsCustomFilter(filterFunc, child)
        return TagCollection(elements)


    def getHTML(self):
        '''
            getHTML - Get the full HTML as contained within this tree
                @returns - String
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


    def getFormattedHTML(self, indent='  '):
        '''
            getFormattedHTML - Get formatted and xhtml of this document

            @param indent - space/tab/newline of each level of indent, or integer for how many spaces per level
        
            @return - Formatted html as string
        '''
        from .Formatter import AdvancedHTMLFormatter
        html = self.getHTML()
        formatter = AdvancedHTMLFormatter(indent, None) # Do not double-encode
        formatter.feed(html)
        return formatter.getHTML()
    

    def _reset(self):
        '''
            _reset - reset this object. Assigned to .reset after __init__ call.
        '''
        HTMLParser.reset(self)

        self.root = None
        self.doctype = None
        self.inTag = []

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
        for child in tag.children:
            self._indexTagRecursive(child)

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
                elements = [x for x in elements if self._hasTagInParentLine(x, root)]
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
                elements = [x for x in elements if self._hasTagInParentLine(x, root)]
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
                elements = [x for x in elements if self._hasTagInParentLine(x, root)]

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
                elements = [x for x in elements if self._hasTagInParentLine(x, root)]
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

        if useIndex is True and attrName in self._otherAttributeIndexes:
            elements = TagCollection()
            for value in values:
                elements += TagCollection(self._otherAttributeIndexes[attrName].get(value, []))

            return elements

        return AdvancedHTMLParser.getElementsWithAttrValues(self, attrName, values, root, useIndex)

    def _reset(self):
        '''
            _reset - reset this object. Assigned to .reset after __init__ call.
        '''
        AdvancedHTMLParser.reset(self)

        self._resetIndexInternal()

#vim: set ts=4 sw=4 expandtab
