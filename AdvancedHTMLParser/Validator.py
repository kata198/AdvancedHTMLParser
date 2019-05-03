'''
    Copyright (c) 2015, 2019 Tim Savannah under LGPLv3. All Rights Reserved.


    See LICENSE (https://gnu.org/licenses/lgpl-3.0.txt) for more information.


    Validator - A validating version of the HTML parser (vs the normal 'best effort' parser)
'''

from .Parser import AdvancedHTMLParser
from .Tags import isValidAttributeName

from .exceptions import InvalidCloseException, MissedCloseException, InvalidAttributeNameException

__all__ = ('InvalidCloseException', 'MissedCloseException', 'InvalidAttributeNameException',
    'ValidatingAdvancedHTMLParser',
)

class ValidatingAdvancedHTMLParser(AdvancedHTMLParser):
    '''
        ValidatingAdvancedHTMLParser - A parser which will raise Exceptions for a couple HTML errors that would otherwise cause
            an assumption to be made during parsing.

        exceptions.InvalidCloseException - The parsed string/file tried to close something it shouldn't have.
        exceptions.MissedCloseException  - The parsed string/file missed closing an item.
    '''

    def handle_starttag(self, tagName, attributeList, isSelfClosing=False):
        '''
            handle_starttag - internal for parsing,

                ValidatingAdvancedHTMLParser will run through the attributes list and make sure
                  none have an invalid name, or will raise an error.


                @raises - InvalidAttributeNameException if an attribute name is passed with invalid character(s)
        '''

        # Iterate over the passed attributes, and validate them.
        for (attrName, attrValue) in attributeList:

            if isValidAttributeName(attrName) is False:

                raise InvalidAttributeNameException(tagName, attrName, attrValue)

        # Done validating, feed to parent.
        return AdvancedHTMLParser.handle_starttag(self, tagName, attributeList, isSelfClosing)


    def handle_endtag(self, tagName):
        '''
            Internal for parsing
        '''
        inTag = self._inTag
        if len(inTag) == 0:
            # Attempted to close, but no open tags
            raise InvalidCloseException(tagName, [])

        foundIt = False
        i = len(inTag) - 1
        while i >= 0:
            if inTag[i].tagName == tagName:
                foundIt = True
                break
            i -= 1

        if not foundIt:
            # Attempted to close, but did not match anything
            raise InvalidCloseException(tagName, inTag)

        if inTag[-1].tagName != tagName:
            raise MissedCloseException(tagName, [x for x in inTag[-1 * (i+1): ] ] )

        inTag.pop()

