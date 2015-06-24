
import uuid

from .constants import PREFORMATTED_TAGS, IMPLICIT_SELF_CLOSING_TAGS

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

        if isSelfClosing is False and tagName in IMPLICIT_SELF_CLOSING_TAGS:
            isSelfClosing = True

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

        self.indent = ''

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
            return "%s<%s%s >" %(self.indent, self.tagName, attributeString)
        else:
            return "%s<%s%s />" %(self.indent, self.tagName, attributeString)
    
    def getEndTag(self):
        '''
            getEndTag - returns the end tag
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

#vim: set ts=4 sw=4 expandtab
