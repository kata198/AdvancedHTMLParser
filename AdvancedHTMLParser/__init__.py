#!/usr/bin/env python
# Copyright (c) 2015 Tim Savannah under LGPLv3. See LICENSE (https://gnu.org/licenses/lgpl-3.0.txt) for more information.
#
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

import uuid
# End Compat

from collections import defaultdict



__version__ = '4.0.0'

IMPLICIT_SELF_CLOSING_TAGS = ('meta', 'link')


def uniqueTags(tagList):
    '''
        uniqueTags - Returns the unique tags in tagList.
        
            @param tagList list<AdvancedTag> : A list of tag objects.
    '''
    ret = []
    alreadyAdded = set()
    for tag in tagList:
        myUid = tag.getUid()
        if myUid in alreadyAdded:
            continue
        ret.append(tag)
    return TagCollection(ret) # Convert to a TagCollection here for performance reasons.

class TagCollection(list):
    '''
        A collection of AdvancedTags. You may use this like a normal list, or you can use the various getElements* functions within to operate on the results.
    '''

    def __init__(self, values=None):
        list.__init__(self)
        self.uids = set()
        if values is not None:
            self.__add__(values)

    @staticmethod
    def _subset(ret, cmpFunc, tag):
        if cmpFunc(tag) is True and ret._hasTag(tag) is False:
            ret.append(tag)

        for subtag in tag.getChildren():
            TagCollection._subset(ret, cmpFunc, subtag)

        return ret

    def __add__(self, others):
        # Maybe this can be optimized by changing self.uids to a dictionary, and using appending the set difference
        for other in others:
            if self._hasTag(other) is False:
                self.append(other)

    def __sub__(self, others):
        for other in others:
            if self._hasTag(other) is True:
                self.remove(other)

    def _hasTag(self, tag):
        return tag.uid in self.uids

    def append(self, newVal):
        list.append(self, newVal)
        self.uids.add(newVal.uid)

    def remove(self, toRemove):
        list.remove(self, toRemove)
        self.uids.remove(toRemove.uid)

    def getElementsByTagName(self, tagName):
        ret = TagCollection()
        if len(self) == 0:
            return ret

        tagName = tagName.lower()
        _cmpFunc = lambda tag : bool(tag.tagName == tagName)
        
        for tag in self:
            TagCollection._subset(ret, _cmpFunc, tag)

        return ret

            
    def all(self):
        return list(self)

    def getElementsByName(self, name):
        ret = TagCollection()
        if len(self) == 0:
            return ret
        _cmpFunc = lambda tag : bool(tag.name == name)
        for tag in self:
            TagCollection._subset(ret, _cmpFunc, tag)

        return ret

    def getElementsByClassName(self, className):
        ret = TagCollection()
        if len(self) == 0:
            return ret
        _cmpFunc = lambda tag : tag.hasClass(className)
        for tag in self:
            TagCollection._subset(ret, _cmpFunc, tag)
        
        return ret

    def getElementById(self, _id):
        for tag in self:
            if tag.getId() == _id:
                return tag
            for subtag in tag.children:
                tmp = subtag.getElementById(_id)
                if tmp is not None:
                    return tmp
        return None

    def getElementsByAttr(self, attr, value):
        ret = TagCollection()
        if len(self) == 0:
            return ret

        attr = attr.lower()
        _cmpFunc = lambda tag : tag.getAttribute(attr) == value
        for tag in self:
            TagCollection._subset(ret, _cmpFunc, tag)
        
        return ret

    def getElementsWithAttrValues(self, attr, values):
        ret = TagCollection()
        if len(self) == 0:
            return ret

        attr = attr.lower()
        _cmpFunc = lambda tag : tag.getAttribute(attr) in values
        for tag in self:
            TagCollection._subset(ret, _cmpFunc, tag)
        
        return ret
        


class AdvancedTag(object):
    '''
        AdvancedTag - Represents a Tag. Used with AdvancedHTMLParser to create a DOM-model

        Keep tag names lowercase.

        Use the getters and setters instead of attributes directly, or you may lose accounting.
    '''
    def __init__(self, tagName, attrList=None, isSelfClosing=False):
        '''
            __init__ - Construct

                @param tagName - String of tag name. This will be lowercased!
                @param attrList - A list of tuples (key, value)
                @param isSelfClosing - True if self-closing tag ( <tagName attrs /> ) will be set to False if text or children are added.
        '''
                
        self.tagName = tagName.lower()

        self.attributes = {}
        if attrList is not None:
            for key, value in attrList:
                self.attributes[key.lower()] = value

        self.text = ''
        self.blocks = ['']

        self.isSelfClosing = isSelfClosing

        if 'class' in self.attributes:
            self.className = self.attributes['class']
            self.classNames = [x for x in self.attributes['class'].split(' ') if x]
        else:
            self.className = ''
            self.classNames = []

        self.children = []

        self.parentNode = None
        self.uid = uuid.uuid4()

    def appendText(self, text):
        '''
            appendText - append some inner text
        '''
        self.text += text
        self.isSelfClosing = False # inner text means it can't self close anymo
        self.blocks.append(text)

    def removeText(self, text):
        '''
            removeText - Removes some inner text
        '''
        newBlocks = []
        for block in self.blocks:
            if isinstance(block, AdvancedTag):
                newBlocks.append(block)
                continue
            if text in block:
                block = block.replace(text, '')
            if block:
                newBlocks.append(block)

        del block # pyflakes warning
        self.blocks = newBlocks

        self.text = ''.join([block for block in self.blocks if not isinstance(block, AdvancedTag)])

    def appendChild(self, child):
        '''
            appendChild - Append a child to this element.
        '''
    
        child.parentNode = self
        self.isSelfClosing = False
        self.children.append(child)
        self.blocks.append(child)
        return child

    appendNode = appendChild

    def removeChild(self, child):
        '''
            removeChild - Remove a child, if present.

                @param child - The child to remove
                @return - The child [with parentNode cleared] if removed, otherwise None.
        '''
        try:
            self.children.remove(child)
            self.blocks.remove(child)
            child.parentNode = None
            return child
        except ValueError:
            return None

    removeNode = removeChild
            
    def getChildren(self):
        '''
            getChildren - returns child nodes
        '''
        return TagCollection(self.children)

    def getPeers(self):
        if not self.parentNode:
            return None
        return [peer for peer in self.parentNode.children if peer is not self]

    @property
    def peers(self):
        return self.getPeers()

    @property
    def childNodes(self):
        '''
            childNodes - returns child nodes
        '''
        return TagCollection(self.children)

    @property
    def parentElement(self):
        return self.parentNode

    @property
    def classList(self):
        '''
            classList - get the list of class names
        '''
        return self.classNames

    @property
    def name(self):
        return self.attributes.get('name', '')

    @property
    def id(self):
        return self.attributes.get('id', '')

    def getUid(self):
        return self.uid

    def getTagName(self):
        '''
            getTagName - Gets the tag name of this Tag.

            @return - str
        '''
        return self.tagName

    def getStartTag(self):
        '''
            getStartTag - Returns the start tag
        '''
        attributeString = []
        for name, val in self.attributes.items():
            if val:
                val = val.replace('"', '\\"')
                attributeString.append('%s="%s"' %(name, val) )

        if attributeString:
            attributeString = ' ' + ' '.join(attributeString)
        else:
            attributeString = ''

        if self.isSelfClosing is False:
            return "<%s%s >" %(self.tagName, attributeString)
        else:
            return "<%s%s />" %(self.tagName, attributeString)
    
    def getEndTag(self):
        '''
            getEndTag - returns the end tag
        '''
        if self.isSelfClosing is True:
            return ''

        return "</%s>" %(self.tagName)

    @property
    def innerHTML(self):
        '''
            innerHTML - Returns a string of the inner contents of this tag, including children.
        '''
        if self.isSelfClosing is True:
            return ''
        ret = []
        for block in self.blocks:
            if isinstance(block, AdvancedTag):
                ret.append(block.outerHTML)
            else:
                ret.append(block)
        
        return ''.join(ret)

    @property
    def outerHTML(self):
        '''
            outerHTML - Returns start tag, innerHTML, and end tag
        '''
        return self.getStartTag() + self.innerHTML + self.getEndTag()

    @property
    def value(self):
        return self.getAttribute('value', '')

    def getAttribute(self, attrName):
        '''
            getAttribute - Gets an attribute on this tag. Do not use this for classname, use .className . Attribute names are all lowercase.
                @return - The attribute value, or None if none exists.
           '''
        return self.attributes.get(attrName, None)

    def setAttribute(self, attrName, attrValue):
        '''
            setAttribute - Sets an attribute. Do not use this for classname, use addClass/removeClass. Attribute names are all lowercase.
        
            @param attrName <str> - The name of the attribute
            @param attrValue <str> - The value of the attribute
        '''
        self.attributes[attrName] = attrValue

    def hasAttribute(self, attrName):
        '''
            hasAttribute - Checks for the existance of an attribute. Attribute names are all lowercase.
   
                @param attrName <str> - The attribute name
                
                @return <bool> - True or False if attribute exists by that name
        '''
        return bool(attrName in self.attributes)

    def hasClass(self, className):
        return bool(className in self.classNames)
     
    def addClass(self, className):
        '''
            addClass - append a class name if not present
        '''
        if className in self.classNames:
            return
        self.classNames.append(className)
        self.className = ' '.join(self.classNames)

        return None

    def removeClass(self, className):
        '''
            removeClass - remove a class name if present. Returns the class name if  removed, otherwise None.
        '''
        if className in self.classNames:
            self.classNames.remove(className)
            self.className = ' '.join(self.classNames)
            return className

        return None
   

    def __str__(self):
        '''
            __str__ - Returns start tag, inner text, and end tag
        '''
        return self.getStartTag() + self.text + self.getEndTag()

    def __getitem__(self, key):
        return self.children[key]

    def getElementById(self, _id):
        for child in self.children:
            if child.getAttribute('id') == _id:
                return child
            found = child.getElementById(_id)
            if found is not None:
                return found
        return None

    def getElementsByAttr(self, attrName, attrValue):
        elements = TagCollection()
        for child in self.children:
            if child.getAttribute(attrName) == attrValue:
                elements.append(child)
            elements += child.getElementsByAttr(attrName, attrValue)
        return elements

    def getElementsByName(self, name):
        return self.getElementsByAttr('name', name)

    def getElementsByClassName(self, className):
        elements = TagCollection()
        for child in self.children:
            if child.hasClass(className) is True:
                elements.append(child)
            elements += child.getElementsByClassName(className)
        return elements

    def getElementsWithAttrValues(self, attr, values):
        elements = TagCollection()

        for child in self.children:
            if child.getAttribute(attr) in values:
                elements.append(child)
            elements += child.getElementsWithAttrValues(attr, values)
        return elements

    def getPeersByAttr(self, attrName, attrValue):
        '''
            getPeersByAttr - Gets peers (elements on same level) which match an attribute/value combination.

            @param attrName - Name of attribute
            @param attrValue - Value that must match

            @return - None if no parent element (error condition), otherwise a list of peers that matched.
        '''
        peers = self.peers
        if peers is None:
            return None
        return [peer for peer in peers if peer.getAttribute(attrName) == attrValue]

    def getPeersWithAttrValues(self, attrName, attrValues):
        '''
            getPeersByAttr - Gets peers (elements on same level) whose attribute given by #attrName 
                are in the list of possible vaues #attrValues

            @param attrName - Name of attribute
            @param attrValues - List of possible values which will match

            @return - None if no parent element (error condition), otherwise a list of peers that matched.
        '''
        peers = self.peers
        if peers is None:
            return None
        return [peer for peer in peers if peer.getAttribute(attrName) in attrValues]

    def getPeersByName(self, name):
        peers = self.peers
        if peers is None:
            return None
        return [peer for peer in peers if peer.name == name]

    def getPeersByClassName(self, className):
        peers = self.peers
        if peers is None:
            return None
        return [peer for peer in peers if peer.hasClass(className)]
                


# Uncomment this line to display the HTML in lists
#    __repr__ = __str__

class AdvancedHTMLParser(HTMLParser):

    def __init__(self, filename=None, indexIDs=True, indexNames=True, indexClassNames=False, indexTagNames=False, onlyCheckIndexOnIndexedFields=True, encoding='utf-8'):
        '''
            __init__ - Creates an Advanced HTML parser object, with specific indexing settings.
              For the various index* fields, if True an index will be created for the respective attribute. If an index is found, the index is used during search
              which results in O(1) efficency, at the cost of increased parsing time. If an index is not present, every node in the tree will be scanned for each search
              on the respective type. See note below on onlyCheckIndexOnIndexedFields for more information. If you are modifying the contents of the tags or the DOM model,
              note the reindex function.

                @param filename <str>         - Optional filename to parse. Otherwise use parseFile or parseStr methods.
                @param indexIDs <bool>        - True to create an index for getElementByID method.  <default True>
                @param indexNames <bool>      - True to create an index for getElementsByName method  <default True>
                @param indexClassNames <bool> - True to create an index for getElementsByClassName method. <default False>
                @param indexTagNames <bool>   - True to create an index for tag names. <default False>

                @param onlyCheckIndexOnIndexedFields <bool> - This option controls how strictly the indexes are used. Setting to True will greatly increase the efficency of
                                                        search time, but the data will be subject to restrictions. If you are not modifing the tree or tags, you should leave this true.
                                                       If true, for each of (id, name, classname, tagname), if that field is indexed ONLY the index is used. 
                                                       If false, the index (if enabled) is used first, and IF NO RESULTS ARE FOUND, the entire tree is searched. If any nodes are found in the index,
                                                        only they are returned.  This is useful if you are concurrently modifying and scanning the tree. 
                                                        Note the `reindex` method on this class which will rebuild the index.
                                                        If this is False, the tag name index may be present but will not be used.

                @param encoding <str> - Specifies the document encoding. Default utf-8
                                            
        '''
              
                
        HTMLParser.__init__(self)

        self.encoding = encoding



        self.inTag = []
        self.root = None
        self.doctype = None

        self.indexFunctions = []
        self.otherAttributeIndexFunctions = {}
        self._otherAttributeIndexes = {}
        self.indexIDs = indexIDs
        self.indexNames = indexNames
        self.indexClassNames = indexClassNames
        self.indexTagNames = indexTagNames
        self.onlyCheckIndexOnIndexedFields = onlyCheckIndexOnIndexedFields

        self._resetIndexInternal()

        self.reset = self._reset # Must assign after first call, otherwise members won't yet be present

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

    def _hasTagInParentLine(self, tag, root):
        if tag == root or tag.parentNode == root:
            return True
        if tag.parentNode is None:
            return False
        return self._hasTagInParentLine(tag.parentNode, root)

    ######## Parsing #########

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
        self._indexTag(newTag)

        if isSelfClosing is False:
            self.inTag.append(newTag)

    def handle_startendtag(self, tagName, attributeList):
        return self.handle_starttag(tagName, attributeList, True)

    def handle_endtag(self, tagName):
        try:
            # Handle closing tags which should have been closed but weren't
            while self.inTag[-1].tagName != tagName:
                self.inTag.pop()

            self.inTag.pop()
        except:
            pass

    def handle_data(self, data):
        if data and len(self.inTag) > 0:
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

###########################################
#####        Public                 #######
###########################################

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
        self.reindex()

    def setOnlyCheckIndexOnIndexedFields(self, onlyCheckIndexOnIndexedFields):
        '''
            setOnlyCheckIndexOnIndexedFields - Set the onlyCheckIndexOnIndexedFields flag. 
        '''
        self.onlyCheckIndexOnIndexedFields = onlyCheckIndexOnIndexedFields

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

    def addIndexForAttribute(self, attributeName):
        '''
            addIndexForAttribute - Add an index for an arbitrary attribute. This will be used by the getElementsByAttr function.
                You should do this prior to parsing, or call reindex. Otherwise it will be blank.
    
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

    def removeIndexForAttribute(self, attributeName):
        '''
            removeIndexForAttribute - Remove an attribute from indexing (for getElementsByAttr function) and remove indexed data.

        @param attributeName <lowercase str> - An attribute name. Will be lowercased.
        '''
        attributeName = attributeName.lower()
        if attributeName in self.otherAttributeIndexFunctions:
                del self.otherAttributeIndexFunctions[attributeName]
        if attributeName in self._otherAttributeIndexes:
                del self._otherAttributeIndexes[attributeName]
    

    def getElementsByTagName(self, tagName, root='root', onlyCheckIndex=None):
        '''
            getElementsByTagName - Searches and returns all elements with a specific tag name.
                Only if `onlyCheckIndexOnIndexedFields` and indexTagNames are both true, the index is used exclusivly. Otherwise a full search.
               
                @param tagName <lowercase str> - A lowercase string of the tag name. 
                @param root <AdvancedTag/'root'> - Search starting at a specific node, if provided. if string 'root', the root of the parsed tree will be used.
        '''
        isFromRoot = bool( root == 'root' or root == self.root)
        if onlyCheckIndex is None:
            onlyCheckIndex = self.onlyCheckIndexOnIndexedFields

        if isFromRoot is True:
            root = self.root
            if root is None:
                raise ValueError('Did not parse anything. Use parseFile or parseStr')

        if onlyCheckIndex is True and self.indexTagNames is True:
            elements = self._tagNameMap.get(tagName, []) # Use .get here as to not create a lot of extra indexes on the defaultdict for misses
            if isFromRoot is False:
                elements = [x for x in elements if self._hasTagInParentLine(x, root)]
            return TagCollection(elements)

        elements = []
        for child in root.children:
            if child.tagName == tagName:
                elements.append(child)
            elements += self.getElementsByTagName(tagName, child)
        return TagCollection(elements)

    def getElementsByName(self, name, root='root'):
        '''
            getElementsByName - Searches and returns all elements with a specific name.
               If indexed and `onlyCheckIndexOnIndexedFields` is False, if the index contains more than one element it is returned, otherwise a full search. see __init__ for more detauls
               
                @param name <str> - A string of the name attribute
                @param root <AdvancedTag/'root'> - Search starting at a specific node, if provided. if string 'root', the root of the parsed tree will be used.
        '''
        isFromRoot = bool( root == 'root' or root == self.root)
        if isFromRoot is True:
            root = self.root
            if root is None:
                raise ValueError('Did not parse anything. Use parseFile or parseStr')

        elements = []
        if self.indexNames is True:
            elements = self._nameMap.get(name, [])
            if isFromRoot is False:
                elements = [x for x in elements if self._hasTagInParentLine(x, root)]
            if self.onlyCheckIndexOnIndexedFields is True or len(elements) > 0:
                return TagCollection(elements)

        for child in root.children:
            if child.attributes.get('name') == name:
                elements.append(child)
            elements += self.getElementsByName(name, child)
        return TagCollection(elements)

    def getElementById(self, _id, root='root'):
        '''
            getElementById - Searches and returns the first (should only be one) element with the given ID.
               If indexed and `onlyCheckIndexOnIndexedFields` is False, and a full scan will happen if the index is a miss. If True, only index is used.
               
                @param id <str> - A string of the id attribute.
                @param root <AdvancedTag/'root'> - Search starting at a specific node, if provided. if string 'root', the root of the parsed tree will be used.
        '''
        isFromRoot = bool( root == 'root' or root == self.root)
        if isFromRoot is True:
            root = self.root
            if root is None:
                raise ValueError('Did not parse anything. Use parseFile or parseStr')


        if self.indexIDs is True:
            element = self._idMap.get(_id, None)
            if isFromRoot is False and element is not None:
                if self._hasTagInParentLine(element, root) is False:
                    element = None
                    
            if self.onlyCheckIndexOnIndexedFields is True or element is not None:
                return element

        for child in root.children:
            if child.attributes.get('id') == _id:
                return child
            potential = self.getElementById(_id, child)
            if potential is not None:
                return potential
        return None

    def getElementsByClassName(self, className, root='root'):
        '''
            getElemenstByClassName - Searches and returns all elements containing a given class name.
               If indexed and `onlyCheckIndexOnIndexedFields` is False, and more than one element is found in the index, only that is returned. If None found then full search.
               
                @param className <str> - A one-word class name
                @param root <AdvancedTag/'root'> - Search starting at a specific node, if provided. if string 'root', the root of the parsed tree will be used.
        '''
        isFromRoot = bool( root == 'root' or root == self.root)
        if isFromRoot is True:
            root = self.root
            if root is None:
                raise ValueError('Did not parse anything. Use parseFile or parseStr')

        if self.indexClassNames is True:
            elements = self._classNameMap.get(className, [])
            if isFromRoot is False:
                elements = [x for x in elements if self._hasTagInParentLine(x, root)]
            if self.onlyCheckIndexOnIndexedFields is True or len(elements) > 0:
                return TagCollection(elements)

        elements = []
        for child in root.children:
            if className in child.classNames:
                elements.append(child)
            elements += self.getElementsByClassName(className, child)
        return TagCollection(elements)

    def getElementsByAttr(self, attrName, attrValue, root='root'):
        '''
            getElemenstByAttr - Searches the full tree for elements with a given attribute name and value combination. This is always a full scan.
               If you want an index on a random attribute, use the addIndexForAttribute function.
               
                @param attrName <lowercase str> - A lowercase attribute name
                @param attrValue <str> - Expected value of attribute
                @param root <AdvancedTag/'root'> - Search starting at a specific node, if provided. if string 'root', the root of the parsed tree will be used.
        '''
        isFromRoot = bool( root == 'root' or root == self.root)
        if isFromRoot is True:
            root = self.root
            if root is None:
                raise ValueError('Did not parse anything. Use parseFile or parseStr')

        # TODO: Rewrite so this condition isn't called every go. Just use child method instead
        if attrName in self._otherAttributeIndexes:
            elements = self._otherAttributeIndexes[attrName].get(attrValue, [])
            if isFromRoot is False:
                elements = [x for x in elements if self._hasTagInParentLine(x, root)]
            if self.onlyCheckIndexOnIndexedFields is True or len(elements) > 0:
                return TagCollection(elements)
        

        elements = []
        for child in root.children:
            if child.attributes.get(attrName) == attrValue:
                elements.append(child)
            elements += self.getElementsByAttr(attrName, attrValue, child)
        return TagCollection(elements)

    def getElementsWithAttrValues(self, attrName, values, root='root'):
        '''
            getElementsWithAttrValues - Returns elements with an attribute, named by #attrName contains one of the values in the list, #values

        '''
        isFromRoot = bool( root == 'root' or root == self.root)
        if isFromRoot is True:
            root = self.root
            if root is None:
                raise ValueError('Did not parse anything. Use parseFile or parseStr')

        if attrName in self._otherAttributeIndexes:
            elements = TagCollection()
            for value in values:
                elements += TagCollection(self._otherAttributeIndexes[attrName].get(value, []))
            if self.onlyCheckIndexOnIndexedFields is True or len(elements) > 0:
                return elements
        
        return root.getElementsWithAttrValues(attrName, values)

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

        if root.tagName == 'XXXblank': # If we had to add a temp tag, don't include it here.
            return doctypeStr + ''.join([x.outerHTML() for x in root.children]) 
        return doctypeStr + root.outerHTML

    def _reset(self):
        '''
            _reset - reset this object. Assigned to .reset after __init__ call.
        '''
        HTMLParser.reset(self)
        self._resetIndexInternal()
        self.root = None
        self.doctype = None
        self.inTag = []

    def feed(self, contents):
        if self.encoding != sys.getdefaultencoding():
            if pyver == 2:
                contents = contents.decode(self.encoding)
            else:
                contents = contents.encode().decode('utf-8')
        try:
            HTMLParser.feed(self, contents)
        except MultipleRootNodeException:
            self.reset()
            HTMLParser.feed(self, '<XXXblank>' + contents + '</XXXblank>')

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

class MultipleRootNodeException(Exception):
    pass

#vim: set ts=4 sw=4 expandtab
