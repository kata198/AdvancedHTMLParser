# Copyright (c) 2015 Tim Savannah under LGPLv3. 
# See LICENSE (https://gnu.org/licenses/lgpl-3.0.txt) for more information.
#
# These are various helpers for "special" attributes

from collections import OrderedDict


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
        elif key in {'class', 'className'}:
            return self.tag.className

        try:
            return dict.__getitem__(self, key)
        except KeyError:
            return None #  TODO: support undefined?

    def get(self, key, default=None):
        if key in {'style', 'class', 'className'} or key in self.keys():
            return self[key]
        return default

    def _direct_set(self, key, value):
        dict.__setitem__(self, key, value)
        return value

    def __setitem__(self, key, value):
        if key == 'style':
            self.tag.style = StyleAttribute(value)
        elif key in {'class', 'className'}:
            self.tag.className = value
            self.tag.classNames = [x for x in value.split(' ') if x]
            dict.__setitem__(self, 'class',  value)
            return value

        dict.__setitem__(self, key,  value)

        return value


class StyleAttribute(object):
    '''
        StyleAttribute - Represents the "style" field on a tag.
    '''

    RESERVED_ATTRIBUTES = ('_styleValue', '_styleDict', '_asStr')

    def __init__(self, styleValue):
        self._styleValue = styleValue
        self._styleDict = StyleAttribute.styleToDict(styleValue)

    def __getattribute__(self, name):
        if name in StyleAttribute.RESERVED_ATTRIBUTES:
            return object.__getattribute__(self, name)

        name = name.lower()

        return self._styleDict.get(name) or ''

    def __setattr__(self, name, val):
        if name in StyleAttribute.RESERVED_ATTRIBUTES:
            return object.__setattr__(self, name, val)

        name = name.lower()

        if not val:
            if name in self._styleDict:
                del self._styleDict[name]
        else:
            self._styleDict[name] = val

        return val

    @staticmethod
    def styleToDict(styleStr):
        '''
            getStyleDict - Gets a dictionary of style attribute/value pairs.

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


    def __str__(self):
        return self._asStr()

    def __repr__(self):
        return repr(self._asStr())

#vim: set ts=4 sw=4 expandtab :
