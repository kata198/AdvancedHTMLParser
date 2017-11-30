#!/usr/bin/env python
# Copyright (c) 2015, 2016, 2017 Tim Savannah All Rights Rserved under LGPLv3. See LICENSE (https://gnu.org/licenses/lgpl-3.0.txt) for more information.
#
# In general below, all "tag names" (body, div, etc) should be lowercase. The parser will lowercase internally. All attribute names (like `id` in id="123") provided to search functions should be lowercase. Values are not lowercase. This is because doing tons of searches, lowercasing every search can quickly build up. Lowercase it once in your code, not every time you call a function.

from .Parser import AdvancedHTMLParser, IndexedAdvancedHTMLParser
from .Tags import AdvancedTag, TagCollection, toggleAttributesDOM, isTextNode, isTagNode
from .Formatter import AdvancedHTMLFormatter
from .Validator import ValidatingAdvancedHTMLParser
from .exceptions import InvalidCloseException, MissedCloseException, HTMLValidationException, MultipleRootNodeException
from .SpecialAttributes import StyleAttribute

__version__ = '8.0.1'
__version_tuple__ = ('8', '0', '1')
__int_version_tuple__ = (8, 0, 1)

__all__ = ( 'AdvancedHTMLParser', 'IndexedAdvancedHTMLParser', 'AdvancedHTMLFormatter', 'AdvancedTag', 'TagCollection',
    'ValidatingAdvancedHTMLParser', 'MissedCloseException', 'InvalidCloseException', 'HTMLValidationException', 'MultipleRootNodeException',
    'StyleAttribute', 'toggleAttributesDOM', 'isTextNode', 'isTagNode' )

#vim: set ts=4 sw=4 expandtab
