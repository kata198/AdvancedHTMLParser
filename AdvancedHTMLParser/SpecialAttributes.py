'''
    Copyright (c) 2015, 2017, 2018, 2019 Tim Savannah under LGPLv3. All Rights Reserved.

    See LICENSE (https://gnu.org/licenses/lgpl-3.0.txt) for more information.


    These are various helpers for "special" attributes
'''

import copy
import weakref

from collections import OrderedDict

from .utils import escapeQuotes, tostr, isstr, stripWordsOnly
from .conversions import convertToBooleanString
from .constants import TAG_ITEM_BINARY_ATTRIBUTES_STRING_ATTR

__all__ = ('SpecialAttributesDict', 'AttributeNode', 'AttributeNodeMap', 'StyleAttribute', 'DOMTokenList' )


class SpecialAttributesDict(dict):
    '''
        SpecialAttributesDict - A dictionary that supports the various special members, to allow javascript-like syntax
    '''

    # A dict that supports returning special members
    def __init__(self, tag):
        dict.__init__(self)

        self._setTag(tag)


    @property
    def tag(self):
        '''
            tag - Property (dot-access) for the associated tag to this attributes dict

                  Handles getting the value from a weak association

                    @return <AdvancedTag/None> - The associated tag, or None if no association
        '''

        tagRef = self._tagRef
        if tagRef:
            return tagRef()
        else:
            return None

    def _setTag(self, tag):
        '''
            _setTag - INTERNAL METHOD. Associated a given AdvancedTag to this attributes dict.

                        If bool(#tag) is True, will set the weakref to that tag.

                        Otherwise, will clear the reference

                      @param tag <AdvancedTag/None> - Either the AdvancedTag to associate, or None to clear current association
        '''
        if tag:
            self._tagRef = weakref.ref(tag)
        else:
            self._tagRef = None


    def __getitem__(self, key):
        key = key.lower()

        if key == 'style':
            # TODO: If detatched from a tag, this will throw an error.
            #         Need to handle detatch and reattach for this attribute
            return self.tag.style
        elif key == 'class':
            return self.tag.className
        elif key in TAG_ITEM_BINARY_ATTRIBUTES_STRING_ATTR:
            try:
                val = dict.__getitem__(self, key)
            except:
                val = None

            return convertToBooleanString(val)

        try:
            return dict.__getitem__(self, key)
        except KeyError:
            return None #  TODO: support undefined?

    def __setitem__(self, key, value):

        key = key.lower()

        tag = self.tag

        if key == 'style':
            if not isinstance(value, StyleAttribute):
                tag.style = StyleAttribute(value, tag)
            else:
                tag.style = value
        elif key == 'class':
            # The setter for className will perform necessary stripping
            tag.className = value
            return
        elif key in TAG_ITEM_BINARY_ATTRIBUTES_STRING_ATTR:
            value = convertToBooleanString(value)

        dict.__setitem__(self, key,  value)

        return value

    def __delitem__(self, key):
        '''
            __delitem__ - Called when someone does del tag.attributes['key']

                @param key <str> - The attribute key to delete
        '''

        key = key.lower()

        if key == 'style':
            self.tag.style = ''
            return
        elif key == 'class':
            self.tag.className = ''
            return
        else:
            try:
                return dict.__delitem__(self, key)
            except KeyError:
                return None


    def __contains__(self, key):
        # Hack in 'class' here

        key = key.lower()

        if key == 'class':
            return bool( len(self.tag._classNames) > 0 )

        return dict.__contains__(self, key)

    def __iter__(self):
        # Hack in 'class' here
        self._handleClassAttr()

        return dict.__iter__(self)


    def pop(self, key):
        raise TypeError('pop not supported on SpecialAttributesDict')

    def setdefault(self, *args, **kwargs):
        raise TypeError('setdefault not supported on SpecialAttributesDict')

    def _handleClassAttr(self):
        '''
            _handleClassAttr - Hack to ensure "class" and "style" show up in attributes when classes are set,
                and doesn't when no classes are present on associated tag.

                TODO: I don't like this hack.
        '''
        if len(self.tag._classNames) > 0:
            dict.__setitem__(self, "class", self.tag.className)
        else:
            try:
                dict.__delitem__(self, "class")
            except:
                pass

        styleAttr = self.tag.style
        if styleAttr.isEmpty() is False:
            dict.__setitem__(self, "style", styleAttr)
        else:
            try:
                dict.__delitem__(self, "style")
            except:
                pass

    def items(self):
        # Intercept and apply the "class" attribute hack
        self._handleClassAttr()

        return dict.items(self)

    def keys(self):
        # Intercept and apply the "class" attribute hack
        self._handleClassAttr()

        return dict.keys(self)

    def get(self, key, default=None):
        '''
            get - Gets an attribute by key with the chance to provide a default value

                @param key <str> - The key to query

                @param default <Anything> Default None - The value to return if key is not found

             @return - The value of attribute at #key, or #default if not present.
        '''

        key = key.lower()

        if key == 'class':
            return self.tag.className

        if key in ('style', 'class') or key in self.keys():
            return self[key]
        return default

    def _direct_set(self, key, value):
        '''
            _direct_set - INTERNAL USE ONLY!!!!

                Directly sets a value on the underlying dict, without running through the setitem logic

        '''
        dict.__setitem__(self, key, value)
        return value

    def _direct_del(self, key):
        '''
            _direct_set - INTERNAL USE ONLY!!!!

                Directly deletes a value from the underlying dict, without running through logic

        '''
        try:
            dict.__delitem__(self, key)
        except:
            pass


    def __repr__(self):
        self._handleClassAttr()

        reprStr = dict.__repr__(self)

        return 'SpecialAttributesDict( %s )' %(reprStr, )

    # __str__ already calls __repr__
    #def __str__(self):
    #    self._handleClassAttr()
    #
    #    strStr = dict.__str__(self)
    #    return 'SpecialAttributesDict( %s )' %(strStr, )


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
        return '[ %s ]' %(' '.join([tostr(self.getNamedItem(name)) for name in self._attributesDict.keys()]))



class StyleAttribute(object):
    '''
        StyleAttribute - Represents the "style" field on a tag.
    '''

    RESERVED_ATTRIBUTES = ('_styleValue', '_styleDict', '_asStr', '_ensureHtmlAttribute', 'tag', '_tagRef', 'setTag', 'isEmpty', 'setProperty')

    def __init__(self, styleValue, tag=None):
        '''
            __init__ - Create a StyleAttribute object.

            @param styleValue <str> - A style string ( like "display: none; padding-top: 5px" )
        '''
        if isinstance(styleValue, StyleAttribute):
            styleValue = tostr(styleValue)

        self._styleValue = styleValue
        self._styleDict = StyleAttribute.styleToDict(styleValue)

        self.setTag(tag)

        # Set the attribute in the tag html if necessary, or clear it.
        self._ensureHtmlAttribute()

    @property
    def tag(self):
        '''
            tag - Property (dot-access variable) which will return the associated tag, if any.

              This method should be used for access to handle the weakref.

              @see setTag - Method to set or remove the tag association

                @return <AdvancedTag/None> - If a tag is associated with this style, it will be returned.
                                                Otherwise, None will be returned
        '''
        tagRef = object.__getattribute__(self, '_tagRef')
        if tagRef:
            return tagRef()

        return None

    def setTag(self, tag):
        '''
            setTag - Set the tag association for this style.

              This will handle the underlying weakref to the tag.

              Call setTag(None) to clear the association, otherwise setTag(tag) to associate this style to that tag.


                @param tag <AdvancedTag/None> - The new association. If None, the association is cleared, otherwise the passed tag
                    becomes associated with this style.

        '''

        if tag:
            self._tagRef = weakref.ref(tag)
        else:
            self._tagRef = None


    def __getattribute__(self, name):
        '''
            __getattribute__ - used on dot (.) access on a Style element.

            @param name <str> - The style attribute name

              NOTE: This should the camelCase name (like paddingTop)

            @return <str> - The attribute value or empty string if not set
        '''
        if name in StyleAttribute.RESERVED_ATTRIBUTES or name.startswith('__'):
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

        styleDict = self._styleDict

        if attrName != name:
            name = attrName

        if not val:
            if name in styleDict:
                del styleDict[name]
        else:
            styleDict[name] = val

        # Okay, since we don't want empty style="" on every tag, we have to attach and remove as properties change
        self._ensureHtmlAttribute()

        return val

    def _ensureHtmlAttribute(self):
        '''
            _ensureHtmlAttribute - INTERNAL METHOD.
                                    Ensure the "style" attribute is present in the html attributes when
                                        is has a value, and absent when it does not.

              This requires special linkage.
        '''
        tag = self.tag

        if tag:
            styleDict = self._styleDict
            tagAttributes = tag._attributes

            # If this is called before we have _attributes setup
            if not issubclass(tagAttributes.__class__, SpecialAttributesDict):
                return

            # If we have any styles set, ensure we have the style="whatever" in the HTML representation,
            #   otherwise ensure we don't have style=""
            if not styleDict:
                tagAttributes._direct_del('style')
            else: #if 'style' not in tagAttributes.keys():
                tagAttributes._direct_set('style', self)


    def isEmpty(self):
        '''
            isEmpty - Check if this is an "empty" style (no attributes set)

                @return <bool> - True if no attributes are set, otherwise False
        '''

        return bool( len(self._styleDict) == 0)


    def setProperty(self, name, value):
        '''
            setProperty - Set a style property to a value.

                NOTE: To remove a style, use a value of empty string, or None

                 @param name <str> - The style name.

                    NOTE: The dash names are expected here, whereas dot-access expects the camel case names.

                      Example:  name="font-weight"  versus the dot-access  style.fontWeight

                 @param value <str> - The style value, or empty string to remove property
        '''
        styleDict = self._styleDict

        if value in ('', None):
            try:
                del styleDict[name]
            except KeyError:
                pass
        else:
            styleDict[name] = str(value)


#            if newValue:
#                # If replacing, just set/override it
#                styleDict[newName] = newValue
#            elif newName in styleDict:
#                # Delete if present and empty value passed
#                del styleDict[newName]
#
#        if styleDict:
#            # If anything left, build a str
#            styleStr = '; '.join([name + ': ' + value for name, value in styleDict.items()])
#            self.setAttribute('style', styleStr)
#            return styleStr
#        else:
#            # Last item removed, so remove attribute.
#            self.removeAttribute('style')
#            return ''

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

    # NOTE: THE MAJORITY OF THESE BELOW ARE DISABLED (not in reserved attributes)

#    def getStyleDict(self):
#        '''
#            getStyleDict - Returns a dictionary of style attribute name:value.
#
#            @return dict <str:str> style attribute names to values. Impl is OrderedDict and will match positioning in string value
#        '''
#        return self._styleDict
#
#    def getStyle(self, styleName):
#        '''
#            getStyle - Gets the value of a style paramater, part of the "style" attribute
#
#            @param styleName - The name of the style
#
#              NOTE: dash-names (like padding-top) are expected here
#
#            @return - String of the value of the style. '' is no value.
#        '''
#        return self.getStyleDict().get(styleName.lower()) or ''
#
#
#    def setStyle(self, styleName, styleValue):
#        '''
#            setStyle - Sets a style param. Example: "display", "block"
#
#                If you need to set many styles on an element, use setStyles instead.
#                It takes a dictionary of attribute, value pairs and applies it all in one go (faster)
#
#                To remove a style, set its value to empty string.
#                When all styles are removed, the "style" attribute will be nullified.
#
#            @param styleName - The name of the style element
#
#            @param styleValue - The value of which to assign the style element
#
#              NOTE: dash-names (like padding-top) are expected here
#
#            @return - String of current value of "style" after change is made.
#        '''
#        return self.setStyles( {styleName : styleValue} )
#
#    def setStyles(self, styleUpdatesDict):
#        '''
#            setStyles - Sets one or more style params.
#                This all happens in one shot, so it is much much faster than calling setStyle for every value.
#
#                To remove a style, set its value to empty string.
#                When all styles are removed, the "style" attribute will be nullified.
#
#            @param styleUpdatesDict - Dictionary of attribute : value styles.
#
#              NOTE: dash-names (like padding-top) are expected here.
#
#            @return - String of current value of "style" after change is made.
#        '''
#        styleDict = self.getStyleDict()
#
#        for newName, newValue in styleUpdatesDict.items():
#            if newValue:
#                # If replacing, just set/override it
#                styleDict[newName] = newValue
#            elif newName in styleDict:
#                # Delete if present and empty value passed
#                del styleDict[newName]
#
#        if styleDict:
#            # If anything left, build a str
#            styleStr = '; '.join([name + ': ' + value for name, value in styleDict.items()])
#            self.setAttribute('style', styleStr)
#            return styleStr
#        else:
#            # Last item removed, so remove attribute.
#            self.removeAttribute('style')
#            return ''

    def _asStr(self):
        '''
            _asStr - Get the string representation of this style

              @return <str> - A string representation of this style (semicolon separated, key: value format)
        '''

        styleDict = self._styleDict
        if styleDict:
            return '; '.join([name + ': ' + value for name, value in styleDict.items()])
        return ''


    def __eq__(self, other):
        '''
            __eq__ - Test if two "style" tag properties are equal.

                NOTE: This differs from javascript. In javascript, no two styles equal eachother, it's
                        an identity comparison not a value comparison.

                      I don't understand how that is useful, but in a future version we may choose to adopt
                        that "feature" and export comparison into a different "isSaneAs(otherStyle)" function

                @param other<StyleAttribute> - The other style attribute map.
        '''

        selfDict = self._styleDict

        # Check if "other" is a string and convert it to a StyleAttribute if so, for comparison
        #   (this also allows any-order, i.e.
        #     StyleAttribute("float: left; font-weight: bold") == StyleAttribute("font-weight: bold; float: left")
        try:
            otherDict = other._styleDict
        except:
            otherStyle = StyleAttribute(other)
            otherDict = otherStyle._styleDict

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


class DOMTokenList(list):
    '''
        DOMTokenList - Imitates a DOMTokenList, that is a list in normal form, but joins via " " on stringifying

                and can be constructed from a string by stripping to single words and splitting by " ", ignoring empty string case
    '''

    def __init__(self, *args, **kwargs):
        '''
            __init__ - Create a DOMTaskList.

                Can take no arguments to create empty list

                Can take a list argument to use those elements in this list

                Can take a string argument, and will strip whitespace and retain each distinct word as an element
        '''
        if len(args) == 1 and isstr(args[0]):
            strippedValue = stripWordsOnly(args[0])
            if not strippedValue:
                # Empty string, don't try to split (we would get one empty string element)
                return list.__init__(self)
            # Create list with split string
            return list.__init__(self, strippedValue.split(' '))

        return list.__init__(self, *args, **kwargs)


    def __str__(self):
        '''
            __str__ - String this element. Equivilant to a javascript DOMTokenList.toString(),

                and will join by ' '
        '''
        return ' '.join(self)

    def __repr__(self):
        return 'DOMTokenList(%s)' %( list.__repr__(self), )

#vim: set ts=4 sw=4 expandtab :
