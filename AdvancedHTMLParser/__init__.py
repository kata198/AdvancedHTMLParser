#!/usr/bin/env python
# Copyright (c) 2015 Tim Savannah under LGPLv3. See LICENSE (https://gnu.org/licenses/lgpl-3.0.txt) for more information.
#
# In general below, all "tag names" (body, div, etc) should be lowercase. The parser will lowercase internally. All attribute names (like `id` in id="123") provided to search functions should be lowercase. Values are not lowercase. This is because doing tons of searches, lowercasing every search can quickly build up. Lowercase it once in your code, not every time you call a function.

from .Parser import AdvancedHTMLParser, IndexedAdvancedHTMLParser
from .Formatter import AdvancedHTMLFormatter

__version__ = '6.0.0'
__version_tuple__ = ('6', '0', '0')

__all__ = ['AdvancedHTMLParser', 'IndexedAdvancedHTMLParser', 'AdvancedHTMLFormatter']

#vim: set ts=4 sw=4 expandtab
