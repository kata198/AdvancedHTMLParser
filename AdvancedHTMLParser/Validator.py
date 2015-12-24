#!/usr/bin/env python
# Copyright (c) 2015 Tim Savannah All Rights Rserved under LGPLv3. See LICENSE (https://gnu.org/licenses/lgpl-3.0.txt) for more information.

from .Parser import AdvancedHTMLParser

from .exceptions import InvalidCloseException, MissedCloseException

__all__ = ('InvalidCloseException', 'MissedCloseException', 'ValidatingAdvancedHTMLParser')

class ValidatingAdvancedHTMLParser(AdvancedHTMLParser):
    '''
        ValidatingAdvancedHTMLParser - A parser which will raise Exceptions for a couple HTML errors that would otherwise cause
            an assumption to be made during parsing.

        exceptions.InvalidCloseException - The parsed string/file tried to close something it shouldn't have.
        exceptions.MissedCloseException  - The parsed string/file missed closing an item.
    '''


    def handle_endtag(self, tagName):
        '''
            Internal for parsing
        '''
        if len(self.inTag) == 0:
            # Attempted to close, but no open tags
            raise InvalidCloseException(tagName, [])

        foundIt = False
        i = len(self.inTag) - 1
        while i >= 0:
            if self.inTag[i].tagName == tagName:
                foundIt = True
                break
            i -= 1

        if not foundIt:
            # Attempted to close, but did not match anything
            raise InvalidCloseException(tagName, self.inTag)

        if self.inTag[-1].tagName != tagName:
            raise MissedCloseException(tagName, [x for x in self.inTag[-1 * (i+1): ] ] )

        self.inTag.pop()

