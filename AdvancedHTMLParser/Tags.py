# Copyright (c) 2015 Tim Savannah under LGPLv3. 
# See LICENSE (https://gnu.org/licenses/lgpl-3.0.txt) for more information.
#  AdvancedTag and TagCollection which represent tags and their data.

from collections import OrderedDict

import uuid

from .constants import PREFORMATTED_TAGS, IMPLICIT_SELF_CLOSING_TAGS
from .SpecialAttributes import SpecialAttributesDict, StyleAttribute

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
        Generally, this is the return of all get* functions.

        All the get* functions called on a TagCollection search all contained elements and their childrens. If you need to check ONLY the elements in the tag collection, and not their children,
        either provide your own list comprehension to do so, or use the "filterCollection" method, which takes an arbitrary function/lambda expression and filters just the immediate tags.
    '''

    def __init__(self, values=None):
        '''
            Create this object.

            @param values - Initial values, or None for empty
        '''
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

    def append(self, tag):
        '''
            append - Append an item to this tag collection

            @param tag - an AdvancedTag
        '''
        list.append(self, tag)
        self.uids.add(tag.uid)

    def remove(self, toRemove):
        '''
            remove - Remove an item from this tag collection

            @param toRemove - an AdvancedTag
        '''
        list.remove(self, toRemove)
        self.uids.remove(toRemove.uid)

    def all(self):
        '''
            all - A plain list of these elements

            @return - List of these elements
        '''
        return list(self)

    def filterCollection(self, filterFunc):
        '''
            filterCollection - Filters only the immediate objects contained within this Collection against a function, not including any children

            @param filterFunc <function> - A function or lambda expression that returns True to have that element match

            @return TagCollection of tags that met the given criteria
        '''
        ret = TagCollection()
        if len(self) == 0:
            return ret

        for tag in self:
            if filterFunc(tag) is True:
                ret.append(tag)

        return ret

    def getElementsByTagName(self, tagName):
        '''
            getElementsByTagName - Gets elements within this collection having a specific tag name

            @param tagName - String of tag name

            @return - TagCollection of unique elements within this collection with given tag name
        '''
        ret = TagCollection()
        if len(self) == 0:
            return ret

        tagName = tagName.lower()
        _cmpFunc = lambda tag : bool(tag.tagName == tagName)
        
        for tag in self:
            TagCollection._subset(ret, _cmpFunc, tag)

        return ret

            
    def getElementsByName(self, name):
        '''
            getElementsByName - Get elements within this collection having a specific name

            @param name - String of "name" attribute

            @return - TagCollection of unique elements within this collection with given "name"
        '''
        ret = TagCollection()
        if len(self) == 0:
            return ret
        _cmpFunc = lambda tag : bool(tag.name == name)
        for tag in self:
            TagCollection._subset(ret, _cmpFunc, tag)

        return ret

    def getElementsByClassName(self, className):
        '''
            getElementsByClassName - Get elements within this collection containing a specific class name

            @param className - A single class name

            @return - TagCollection of unique elements within this collection tagged with a specific class name
        '''
        ret = TagCollection()
        if len(self) == 0:
            return ret
        _cmpFunc = lambda tag : tag.hasClass(className)
        for tag in self:
            TagCollection._subset(ret, _cmpFunc, tag)
        
        return ret

    def getElementById(self, _id):
        '''
            getElementById - Gets an element within this collection by id

            @param _id - string of "id" attribute

            @return - a single tag matching the id, or None if none found
        '''
        for tag in self:
            if tag.id == _id:
                return tag
            for subtag in tag.children:
                tmp = subtag.getElementById(_id)
                if tmp is not None:
                    return tmp
        return None

    def getElementsByAttr(self, attr, value):
        '''
            getElementsByAttr - Get elements within this collection posessing a given attribute/value pair

            @param attr - Attribute name (lowercase)
            @param value - Matching value

            @return - TagCollection of all elements matching name/value
        '''
        ret = TagCollection()
        if len(self) == 0:
            return ret

        attr = attr.lower()
        _cmpFunc = lambda tag : tag.getAttribute(attr) == value
        for tag in self:
            TagCollection._subset(ret, _cmpFunc, tag)
        
        return ret

    def getElementsWithAttrValues(self, attr, values):
        '''
            getElementsWithAttrValues - Get elements within this collection possessing an attribute name matching one of several values

            @param attr <lowercase str> - Attribute name (lowerase)
            @param values set<str> - Set of possible matching values

            @return - TagCollection of all elements matching criteria
        '''
        ret = TagCollection()
        if len(self) == 0:
            return ret

        if type(values) != set:
            values = set(values)

        attr = attr.lower()
        _cmpFunc = lambda tag : tag.getAttribute(attr) in values
        for tag in self:
            TagCollection._subset(ret, _cmpFunc, tag)
        
        return ret

    def getElementsCustomFilter(self, filterFunc):
        '''
            getElementsCustomFilter - Get elements within this collection that match a user-provided function.

            @param filterFunc <function> - A function that returns True if the element matches criteria

            @return - TagCollection of all elements that matched criteria
        '''
        ret = TagCollection()
        if len(self) == 0:
            return ret

        _cmpFunc = lambda tag : filterFunc(tag) is True
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

        if isSelfClosing is False and tagName in IMPLICIT_SELF_CLOSING_TAGS:
            isSelfClosing = True

        self.attributes = SpecialAttributesDict(self)
        self.text = ''
        self.blocks = ['']
        self.classNames = []
        self.className = ''
        self.style = StyleAttribute('')

        self.isSelfClosing = isSelfClosing

        if attrList is not None:
            for key, value in attrList:
                key = key.lower()
                self.attributes[key] = value

        self.children = []

        self.parentNode = None
        self.uid = uuid.uuid4()

        self.indent = ''

    def __setattr__(self, name, value):
        if name == 'style' and not isinstance(value, StyleAttribute):
            value = StyleAttribute(value)
        try:
            return object.__setattr__(self, name,  value)
        except AttributeError:
            raise AttributeError('Cannot set property %s. Use setAttribute?' %(name,))

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

            @param child <AdvancedTag> - Append a child element to this element
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

    def insertBefore(self, child, beforeChild):
        '''
            insertBefore - Inserts a child before @beforeChild

            child - Child to insert
            beforeChild - Child  to insert before. if None, will  be appended

        '''
        if beforeChild is None:
            return self.appendChild(child)

        try:
            childrenIdx = self.children.index(beforeChild)
            blocksIdx =  self.blocks.index(beforeChild)
            self.children = self.children[:childrenIdx] + [child] + self.children[childrenIdx:]
            self.blocks = self.blocks[:blocksIdx] + [child] + self.blocks[blocksIdx:]
        except ValueError:
            raise ValueError('Provided "beforeChild" is not a child of element, cannot insert.')

    def insertAfter(self, child, afterChild):
        '''
            insertAfter - Inserts a child after @afterChild

            child - Child to insert
            afterChild - Child  to insert after. if None, will  be appended

        '''
        if afterChild is None:
            return self.appendChild(child)

        try:
            childrenIdx = self.children.index(afterChild)
            blocksIdx =  self.blocks.index(afterChild)
            self.children = self.children[:childrenIdx+1] + [child] + self.children[childrenIdx+1:]
            self.blocks = self.blocks[:blocksIdx+1] + [child] + self.blocks[blocksIdx+1:]
        except ValueError:
            raise ValueError('Provided "afterChild" is not a child of element, cannot insert.')

    @property
    def nextSibling(self):
        '''
            nextSibling - Returns the next sibling.  This could be text or an element. use nextSiblingElement to ensure element
        '''
        if not self.parentNode:
            return None
        myBlockIdx = self.parentNode.blocks.index(self)
        if myBlockIdx == len(self.parentNode.blocks):
            return None
        return self.parentNode.blocks[myBlockIdx+1]

    @property
    def nextSiblingElement(self):
        '''
            nextSiblingElement - Returns the next sibling  that is an element. 
        '''
        if not self.parentNode:
            return None
        myElementIdx = self.parentNode.children.index(self)
        if myElementIdx == len(self.parentNode.children):
            return None
        return self.parentNode.children[myElementIdx+1]
        
    @property
    def previousSibling(self):
        '''
            previousSibling - Returns the previous sibling.  This could be text or an element. use previousSiblingElement to ensure element
        '''
        if not self.parentNode:
            return None
        myBlockIdx = self.parentNode.blocks.index(self)
        if myBlockIdx == 0:
            return None
        return self.parentNode.blocks[myBlockIdx-1]

    @property
    def previousSiblingElement(self):
        '''
            previousSiblingElement - Returns the previous  sibling  that is an element. 
        '''
        if not self.parentNode:
            return None
        myElementIdx = self.parentNode.children.index(self)
        if myElementIdx == 0:
            return None
        return self.parentNode.children[myElementIdx-1]
        

    def getChildren(self):
        '''
            getChildren - returns child nodes as a searchable TagCollection.

                @return - TagCollection of the immediate children to this tag.
        '''
        return TagCollection(self.children)

    def getChildren(self):
        '''
            getChildren - returns child nodes as a searchable TagCollection.

                @return - TagCollection of the immediate children to this tag.
        '''
        return TagCollection(self.children)

    def getPeers(self):
        '''
            getPeers - Get elements who share a parent with this element

            @return - TagCollection of elements
        '''
        if not self.parentNode:
            return None
        return TagCollection([peer for peer in self.parentNode.children if peer is not self])

    @property
    def peers(self):
        '''
            peers - Get elements with same parent as this item

            @return - TagCollection of elements
        '''
        return self.getPeers()

    @property
    def childNodes(self):
        '''
            childNodes - returns immediate child nodes as a TagCollection

            @return - TagCollection of child nodes
        '''
        return TagCollection(self.children)

    @property
    def parentElement(self):
        '''
            parentElement - get the parent element
        '''
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

            @return - String of start tag with attributes
        '''
        attributeString = []
        for name, val in self.attributes.items():
            if val:
                val = val.replace('"', '\\"')
                attributeString.append('%s="%s"' %(name, val) )
            else:
                attributeString.append(name)

        if attributeString:
            attributeString = ' ' + ' '.join(attributeString)
        else:
            attributeString = ''

        if self.isSelfClosing is False:
            return "%s<%s%s >" %(self.indent, self.tagName, attributeString)
        else:
            return "%s<%s%s />" %(self.indent, self.tagName, attributeString)
    
    def getEndTag(self):
        '''
            getEndTag - returns the end tag

            @return - String of end tag
        '''
        if self.isSelfClosing is True:
            return ''

        # Do not add any indentation to the end of preformatted tags.
        if self.indent and self.tagName in PREFORMATTED_TAGS:
            return "</%s>" %(self.tagName)

        return "%s</%s>" %(self.indent, self.tagName)

    @property
    def innerHTML(self):
        '''
            innerHTML - Returns a string of the inner contents of this tag, including children.

            @return - String of inner contents 
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

            @return - String of start tag, innerHTML, and end tag
        '''
        return self.getStartTag() + self.innerHTML + self.getEndTag()

    @property
    def value(self):
        '''
            value - The "value" attribute of this element
        '''
        return self.getAttribute('value', '')

    def getAttribute(self, attrName):
        '''
            getAttribute - Gets an attribute on this tag. Be wary using this for classname, maybe use addClass/removeClass. Attribute names are all lowercase.
                @return - The attribute value, or None if none exists.
           '''
        return self.attributes.get(attrName, None)

    def setAttribute(self, attrName, attrValue):
        '''
            setAttribute - Sets an attribute. Be wary using this for classname, maybe use addClass/removeClass. Attribute names are all lowercase.
        
            @param attrName <str> - The name of the attribute
            @param attrValue <str> - The value of the attribute
        '''
        self.attributes[attrName] = attrValue

    def setAttributes(self, attributesDict):
        '''
            setAttributes - Sets  several attributes at once, using a dictionary of attrName : attrValue

            @param  attributesDict - <str:str> - New attribute names -> values
        '''
        self.attributes.update(attributesDict)

    def hasAttribute(self, attrName):
        '''
            hasAttribute - Checks for the existance of an attribute. Attribute names are all lowercase.
   
                @param attrName <str> - The attribute name
                
                @return <bool> - True or False if attribute exists by that name
        '''
        attrName = attrName.lower()
        return bool(attrName in self.attributes)

    def removeAttribute(self, attrName):
        '''
            removeAttribute - Removes an attribute, by name.
            
            @param attrName <str> - The attribute name

        '''
        attrName = attrName.lower()
        try:
            del self.attributes[attrName]
        except KeyError:
            pass

    def hasClass(self, className):
        '''
            hasClass - Test if this tag has a paticular class name

            @param className - A class to search
        '''
        return bool(className in self.classNames)
     
    def addClass(self, className):
        '''
            addClass - append a class name if not present
        '''
        if className in self.classNames:
            return
        self.classNames.append(className)
        self.className = ' '.join(self.classNames)
        self.attributes._direct_set('class', self.className)

        return None

    def removeClass(self, className):
        '''
            removeClass - remove a class name if present. Returns the class name if  removed, otherwise None.
        '''
        if className in self.classNames:
            self.classNames.remove(className)
            self.className = ' '.join(self.classNames)
            self.attributes._direct_set('class', self.className)
            return className

        return None

    def getStyleDict(self):
        '''
            getStyleDict - Gets a dictionary of style attribute/value pairs.

            @return - OrderedDict of "style" attribute.
        '''
        styleStr = (self.getAttribute('style') or '').strip()
        styles = styleStr.split(';') # Won't work for strings containing semicolon..
        styleDict = OrderedDict()
        for item in styles:
            try:
                splitIdx = item.index(':')
                name = item[:splitIdx].strip().lower()
                value = item[splitIdx+1:].strip()
                styleDict[name] = value
            except:
                continue

        return styleDict


    def getStyle(self, styleName):
        '''
            getStyle - Gets the value of a style paramater, part of the "style" attribute

            @param styleName - The name of the style

            @return - String of the value of the style. '' is no value.
        '''
        return getattr(self.style, styleName.lower())
        

    def setStyle(self, styleName, styleValue):
        '''
            setStyle - Sets a style param. Example: "display", "block"

                If you need to set many styles on an element, use setStyles instead. 
                It takes a dictionary of attribute, value pairs and applies it all in one go (faster)

                To remove a style, set its value to empty string.
                When all styles are removed, the "style" attribute will be nullified.

            @param styleName - The name of the style element
            @param styleValue - The value of which to assign the style element

            @return - String of current value of "style" after change is made.
        '''
        setattr(self.style, styleName, styleValue)

    def setStyles(self, styleUpdatesDict):
        '''
            setStyles - Sets one or more style params. 
                This all happens in one shot, so it is much much faster than calling setStyle for every value.

                To remove a style, set its value to empty string.
                When all styles are removed, the "style" attribute will be nullified.

            @param styleUpdatesDict - Dictionary of attribute : value styles.

            @return - String of current value of "style" after change is made.
        '''
        for newName, newValue in styleUpdatesDict.items():
            setattr(self.style, newName, newValue)

        return self.style


    def __str__(self):
        '''
            __str__ - Returns start tag, inner text, and end tag
        '''
        return self.getStartTag() + self.text + self.getEndTag()

    def __getitem__(self, key):
        return self.children[key]

    def getElementById(self, _id):
        '''
            getElementById - Search children of this tag for a tag containing an id

            @param _id - String of id

            @return - AdvancedTag or None
        '''
        for child in self.children:
            if child.getAttribute('id') == _id:
                return child
            found = child.getElementById(_id)
            if found is not None:
                return found
        return None

    def getElementsByAttr(self, attrName, attrValue):
        '''
            getElementsByAttr - Search children of this tag for tags with an attribute name/value pair

            @param attrName - Attribute name (lowercase)
            @param attrValue - Attribute value

            @return - TagCollection of matching elements
        '''
        elements = []
        for child in self.children:
            if child.getAttribute(attrName) == attrValue:
                elements.append(child)
            elements += child.getElementsByAttr(attrName, attrValue)
        return TagCollection(elements)

    def getElementsByName(self, name):
        '''
            getElementsByName - Search children of this tag for tags with a given name

            @param name - name to search

            @return - TagCollection of matching elements
        '''
        return self.getElementsByAttr('name', name)

    def getElementsByClassName(self, className):
        '''
            getElementsByClassName - Search children of this tag for tags containing a given class name

            @param className - Class name

            @return - TagCollection of matching elements
        '''
        elements = []
        for child in self.children:
            if child.hasClass(className) is True:
                elements.append(child)
            elements += child.getElementsByClassName(className)
        return TagCollection(elements)

    def getElementsWithAttrValues(self, attrName, attrValues):
        '''
            getElementsWithAttrValues - Search children of this tag for tags with an attribute name and one of several values

            @param attrName <lowercase str> - Attribute name (lowercase)
            @param attrValues set<str> - set of acceptable attribute values

            @return - TagCollection of matching elements
        '''
        elements = []

        for child in self.children:
            if child.getAttribute(attrName) in attrValues:
                elements.append(child)
            elements += child.getElementsWithAttrValues(attrName, attrValues)
        return TagCollection(elements)


    def getElementsCustomFilter(self, filterFunc):
        '''
            getElementsCustomFilter - Searches children of this tag for those matching a provided user function

            @param filterFunc <function> - A function or lambda expression that should return "True" if the passed node matches criteria.

            @return - TagCollection of matching results
        '''
        elements = []

        for child in self.children:
            if filterFunc(child) is True:
                elements.append(child)
            elements += child.getElementsCustomFilter(filterFunc)

        return TagCollection(elements)

    def getPeersByAttr(self, attrName, attrValue):
        '''
            getPeersByAttr - Gets peers (elements on same level) which match an attribute/value combination.

            @param attrName - Name of attribute
            @param attrValue - Value that must match

            @return - None if no parent element (error condition), otherwise a TagCollection of peers that matched.
        '''
        peers = self.peers
        if peers is None:
            return None
        return TagCollection([peer for peer in peers if peer.getAttribute(attrName) == attrValue])

    def getPeersWithAttrValues(self, attrName, attrValues):
        '''
            getPeersWithAttrValues - Gets peers (elements on same level) whose attribute given by #attrName 
                are in the list of possible vaues #attrValues

            @param attrName - Name of attribute
            @param attrValues - List of possible values which will match

            @return - None if no parent element (error condition), otherwise a TagCollection of peers that matched.
        '''
        peers = self.peers
        if peers is None:
            return None
        return TagCollection([peer for peer in peers if peer.getAttribute(attrName) in attrValues])

    def getPeersByName(self, name):
        '''
            getPeersByName - Gets peers (elements on same level) with a given name

            @param name - Name to match

            @return - None if no parent element (error condition), otherwise a TagCollection of peers that matched.
        '''
        peers = self.peers
        if peers is None:
            return None
        return TagCollection([peer for peer in peers if peer.name == name])

    def getPeersByClassName(self, className):
        '''
            getPeersByClassName - Gets peers (elements on same level) with a given class name

            @param className - classname must contain this name

            @return - None if no parent element (error condition), otherwise a TagCollection of peers that matched.
        '''
        peers = self.peers
        if peers is None:
            return None
        return TagCollection([peer for peer in peers if peer.hasClass(className)])
                


# Uncomment this line to display the HTML in lists
#    __repr__ = __str__

#vim: set ts=4 sw=4 expandtab
