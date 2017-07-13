# Copyright (c) 2015, 2017 Tim Savannah under LGPLv3. 
# See LICENSE (https://gnu.org/licenses/lgpl-3.0.txt) for more information.
#
# These are various helpers for "special" attributes

import copy

from collections import OrderedDict

from .utils import escapeQuotes

__all__ = ('SpecialAttributesDict', 'AttributeNode', 'AttributeNodeMap', 'StyleAttribute' )


class SpecialAttributesDict(dict):
    '''
        SpecialAttributesDict - A dictionary that supports the various special members, to allow javascript-like syntax
    '''

    # A dict that supports returning special members
    def __init__(self, tag):
        dict.__init__(self)
        self.tag = tag

    def __getitem__(self, key):
        if key == 'style':
            return self.tag.style
        elif key == 'class':
            return dict.get(self, 'class', '')

        try:
            return dict.__getitem__(self, key)
        except KeyError:
            return None #  TODO: support undefined?

    def get(self, key, default=None):
        if key in {'style', 'class'} or key in self.keys():
            return self[key]
        return default

    def _direct_set(self, key, value):
        dict.__setitem__(self, key, value)
        return value

    def __setitem__(self, key, value):
        if key == 'style':
            if not isinstance(value, StyleAttribute):
                self.tag.style = StyleAttribute(value, self.tag)
            else:
                self.tag.style = value
        elif key == 'class':

            # Ensure when we update the "class" attribute, that we update the list as well.
            self.tag.classNames = [x for x in value.split(' ') if x]
            dict.__setitem__(self, 'class',  value)
            return value

        dict.__setitem__(self, key,  value)

        return value


class AttributeNode(object):
    '''
        AttributeNode - A basic NamedNode implementing Attribute Node, mostly.
    '''

    def __init__(self, name, value, ownerElement, ownerDocument=None):
        self.name = name
        self._value = value
        self.ownerElement = ownerElement
        self.ownerDocument = ownerDocument


    @property
    def specified(self):
        return True

    @property
    def localName(self):
        return self.name

    nodeName = localName

    @property
    def prefix(self):
        return None

    @property
    def namespaceURI(self):
        # Not supported..
        return None

    def __getattribute__(self, name):
        if name == 'value':
            return self._value
        return object.__getattribute__(self, name)

    def __getitem__(self, name):
        if name == 'value':
            return self._value

        return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        if name in ('name', '_value', 'ownerElement', 'ownerDocument'):
            return object.__setattr__(self, name, value)

        if name == 'value':
            self._value = value
            if self.ownerElement:
                self.ownerElement.setAttribute(self.name, value)
        else:
            raise ValueError('Cannot change the value of "%s". Only "value" is mutable.' %(name, ))

    @property
    def nodeType(self):
        '''
            nodeType - Return this node type (ATTRIBUTE_NODE)
        '''
        return 2

    @property
    def nodeValue(self):
        '''
            nodeValue - value of this node.
        '''
        return self._value

    def cloneNode(self):
        '''
            cloneNode - Make a copy of this node, but not associated with the ownerElement

            @return AttributeNode
        '''
        return AttributeNode(self.name, self._value, None, self.ownerDocument)

    def __str__(self):
        return '%s="%s"' %(self.name, escapeQuotes(self._value))

    def __repr__(self):
        return "%s(%s, %s, %s, %s)" %(self.__class__.__name__, repr(self.name), repr(self._value), repr(self.ownerElement), repr(self.ownerDocument))

    def __hash__(self):
        return hash( "%d_%d_%d_%d" %(hash(self.name), hash(self._value), hash(self.ownerElement), hash(self.ownerDocument)) )

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return hash(self) == hash(other)

    def __ne__(self, other):
        return not self.__eq__(self, other)


class AttributeNodeMap(object):
    '''
        AttributeNodeMap - A map of AttributeNode associated with an element.

            Not very useful, I've never actually seen the "Node" interface used in practice,
            but here just incase...

            You probably want to just use the normal getAttribute and setAttribute on nodes... that way makes sense.
             This way really doesn't make a whole lot of sense.
    '''


    def __init__(self, attributesDict, ownerElement, ownerDocument=None):

        self._attributesDict = attributesDict
        self._ownerElement = ownerElement
        self._ownerDocument = ownerDocument

        self.__setitem__ = self.X__setitem__
        self.__setattr__ = self.X__setitem__

    def getNamedItem(self, name):
        name = name.lower()

        if name in self._attributesDict:
            return AttributeNode(name, self._attributesDict[name], self._ownerElement, self._ownerDocument)

        return None

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except:
            pass

        return self.getNamedItem(name)

    def __getitem__(self, name):
        if isinstance(name, int):
            return self.getNamedItem(self._attributesDict.keys()[name])
        
        return self.getNamedItem(name)

    def __iter__(self):
        keys = list(self._attributesDict.keys())

        for key in keys:
            if key in self._attributesDict:
                yield key

    item = getNamedItem

    def setNamedItem(self, *args, **kwargs):
        raise NotImplementedError("I can't figure out the constructor to Attr(), which seems to be the type this takes as a parameter. No documentation to be found either. Don't use this method, or figure it out and submit a patch!'")

    def X__setitem__(self, name, value):
        raise NotImplementedError('setitem and setattr are not implemented on an AttributeNodeMap. Maybe you mean setAttribute on the node itself? Actually setting a value in a real JS DOM does nothing. You can also access an element on this map and set the .value attribute to change the value on the parent node.')


    def __str__(self):
        return '[ %s ]' %(' '.join([str(self.getNamedItem(name)) for name in self._attributesDict.keys()]))



class StyleAttribute(object):
    '''
        StyleAttribute - Represents the "style" field on a tag.
    '''

    RESERVED_ATTRIBUTES = ('_styleValue', '_styleDict', '_asStr', 'tag')

    def __init__(self, styleValue, tag=None):
        '''
            __init__ - Create a StyleAttribute object.

            @param styleValue <str> - A style string ( like "display: none; padding-top: 5px" )
        '''
        if isinstance(styleValue, StyleAttribute):
            styleValue = str(styleValue)

        self._styleValue = styleValue
        self._styleDict = StyleAttribute.styleToDict(styleValue)
        self.tag = tag

    def __getattribute__(self, name):
        '''
            __getattribute__ - used on dot (.) access on a Style element.

            @param name <str> - The style attribute name

              NOTE: This should the camelCase name (like paddingTop)

            @return <str> - The attribute value or empty string if not set
        '''
        if name in StyleAttribute.RESERVED_ATTRIBUTES:
            return object.__getattribute__(self, name)

        dashName = StyleAttribute.camelCaseToDashName(name)

        if '-' in dashName:
            name = dashName

        return self._styleDict.get(name) or ''


    def __setattr__(self, name, val):
        '''
            __setattr__ - Used to set an attribute using dot (.) access on a Style element

            @param name <str> - The attribute name

              NOTE: This must be the camelCase name (like paddingTop).

            @param val <str> - The value of the attribute

        '''
        if name in StyleAttribute.RESERVED_ATTRIBUTES:
            return object.__setattr__(self, name, val)

        
        attrName = StyleAttribute.camelCaseToDashName(name)

        if attrName != name:
            name = attrName

        if not val:
            if name in self._styleDict:
                del self._styleDict[name]
        else:
            self._styleDict[name] = val

        if self.tag and self._styleDict:
            self.tag.setAttribute('style', self)

        return val

    @staticmethod
    def dashNameToCamelCase(dashName):
        '''
            dashNameToCamelCase - Converts a "dash name" (like padding-top) to its camel-case name ( like "paddingTop" )

            @param dashName <str> - A name containing dashes

                NOTE: This method is currently unused, but may be used in the future. kept for completeness.

            @return <str> - The camel-case form
        '''
        nameParts = dashName.split('-')
        for i in range(1, len(nameParts), 1):
            nameParts[i][0] = nameParts[i][0].upper()

        return ''.join(nameParts)

    @staticmethod
    def camelCaseToDashName(camelCase):
        '''
            camelCaseToDashName - Convert a camel case name to a dash-name (like paddingTop to padding-top)

            @param camelCase <str> - A camel-case string

            @return <str> - A dash-name
        '''

        camelCaseList = list(camelCase)

        ret = []

        for ch in camelCaseList:
            if ch.isupper():
                ret.append('-')
                ret.append(ch.lower())
            else:
                ret.append(ch)

        return ''.join(ret)

    @staticmethod
    def styleToDict(styleStr):
        '''
            getStyleDict - Gets a dictionary of style attribute/value pairs.

              NOTE: dash-names (like padding-top) are used here

            @return - OrderedDict of "style" attribute.
        '''
        styleStr = styleStr.strip()
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

    def getStyleDict(self):
        '''
            getStyleDict - Returns a dictionary of style attribute name:value. 

            @return dict <str:str> style attribute names to values. Impl is OrderedDict and will match positioning in string value
        '''
        return self._styleDict

    def getStyle(self, styleName):
        '''
            getStyle - Gets the value of a style paramater, part of the "style" attribute

            @param styleName - The name of the style

              NOTE: dash-names (like padding-top) are expected here

            @return - String of the value of the style. '' is no value.
        '''
        return self.getStyleDict().get(styleName.lower()) or ''
        

    def setStyle(self, styleName, styleValue):
        '''
            setStyle - Sets a style param. Example: "display", "block"

                If you need to set many styles on an element, use setStyles instead. 
                It takes a dictionary of attribute, value pairs and applies it all in one go (faster)

                To remove a style, set its value to empty string.
                When all styles are removed, the "style" attribute will be nullified.

            @param styleName - The name of the style element

            @param styleValue - The value of which to assign the style element

              NOTE: dash-names (like padding-top) are expected here

            @return - String of current value of "style" after change is made.
        '''
        return self.setStyles( {styleName : styleValue} )

    def setStyles(self, styleUpdatesDict):
        '''
            setStyles - Sets one or more style params. 
                This all happens in one shot, so it is much much faster than calling setStyle for every value.

                To remove a style, set its value to empty string.
                When all styles are removed, the "style" attribute will be nullified.

            @param styleUpdatesDict - Dictionary of attribute : value styles.

              NOTE: dash-names (like padding-top) are expected here.

            @return - String of current value of "style" after change is made.
        '''
        styleDict = self.getStyleDict()

        for newName, newValue in styleUpdatesDict.items():
            if newValue:
                # If replacing, just set/override it
                styleDict[newName] = newValue
            elif newName in styleDict:
                # Delete if present and empty value passed
                del styleDict[newName]

        if styleDict:
            # If anything left, build a str
            styleStr = '; '.join([name + ': ' + value for name, value in styleDict.items()])
            self.setAttribute('style', styleStr)
            return styleStr
        else:
            # Last item removed, so remove attribute.
            self.removeAttribute('style')
            return ''

    def _asStr(self):
        styleDict = self._styleDict
        if styleDict:
            return '; '.join([name + ': ' + value for name, value in styleDict.items()])
        return ''


    def __eq__(self, other):
        selfDict = self._styleDict
        otherDict = other._styleDict

        selfDictKeys = list(selfDict.keys())
        otherDictKeys = list(otherDict.keys())

        if set(selfDictKeys) != set(otherDictKeys):
            return False

        for key in selfDictKeys:
            if selfDict.get(key) != otherDict.get(key):
                return False

        return True

    def __ne__(self, other):
        return not ( self == other )

    def __str__(self):
        return self._asStr()

    def __repr__(self):
        return "%s(%s)" %(type(self).__name__, repr(self._asStr()))

    def __copy__(self):
        return self.__class__(self._asStr())

    def __deepcopy__(self, memo):
        return self.__class__(self._asStr())


#vim: set ts=4 sw=4 expandtab :
