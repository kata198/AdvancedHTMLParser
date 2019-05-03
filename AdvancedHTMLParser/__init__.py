'''
    Copyright (c) 2015, 2016, 2017, 2018, 2019 Tim Savannah All Rights Rserved under LGPLv3. All Rights Reserved.


    See LICENSE (https://gnu.org/licenses/lgpl-3.0.txt) for more information.

    See: https://github.com/kata198/AdvancedHTMLParser for full information
'''


#
# In general below, all "tag names" (body, div, etc) should be lowercase. The parser will lowercase internally. All attribute names (like `id` in id="123") provided to search functions should be lowercase. Values are not lowercase. This is because doing tons of searches, lowercasing every search can quickly build up. Lowercase it once in your code, not every time you call a function.

from .Parser import AdvancedHTMLParser, IndexedAdvancedHTMLParser
from .Tags import AdvancedTag, TagCollection, toggleAttributesDOM, isTextNode, isTagNode
from .Formatter import AdvancedHTMLFormatter, AdvancedHTMLMiniFormatter, AdvancedHTMLSlimTagFormatter, AdvancedHTMLSlimTagMiniFormatter
from .Validator import ValidatingAdvancedHTMLParser
from .exceptions import InvalidCloseException, MissedCloseException, HTMLValidationException, MultipleRootNodeException
from .SpecialAttributes import StyleAttribute

__version__ = '8.1.5'
__version_tuple__ = ('8', '1', '5')
__int_version_tuple__ = (8, 1, 5)

__all__ = ( 'AdvancedHTMLParser', 'IndexedAdvancedHTMLParser', 'AdvancedHTMLFormatter', 'AdvancedTag', 'TagCollection',
    'ValidatingAdvancedHTMLParser', 'MissedCloseException', 'InvalidCloseException', 'HTMLValidationException', 'MultipleRootNodeException',
    'StyleAttribute', 'toggleAttributesDOM', 'isTextNode', 'isTagNode',
    'AdvancedHTMLMiniFormatter', 'AdvancedHTMLSlimTagFormatter', 'AdvancedHTMLSlimTagMiniFormatter' )

#vim: set ts=4 sw=4 expandtab
