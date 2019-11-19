'''
    Copyright (c) 2019 Tim Savannah  under terms of LGPLv3. All Rights Reserved.

    See LICENSE (https://gnu.org/licenses/lgpl-3.0.txt) for more information.


    compat - Some python2/python3 compatibility things
'''
# vim: set ts=4 sw=4 st=4 expandtab :

import sys

__all__ = ('STRING_TYPES', 'RAW_STRING_TYPE', 'ALL_STRING_TYPES')

if sys.version_info.major < 3:
    
    # STRING_TYPES - Types that represent strings ("printable")
    STRING_TYPES = (str, unicode)

    # RAW_STRING_TYPE - The type of a raw "encoded" string
    RAW_STRING_TYPE = str

    # ALL_STRING_TYPES - All string-like types, encoded or otherwise
    ALL_STRING_TYPES = (str, unicode)

else:
    
    # STRING_TYPES - Types that represent strings ("printable")
    STRING_TYPES = (str, )

    # RAW_STRING_TYPE - The type of a raw "encoded" string
    RAW_STRING_TYPE = bytes

    # ALL_STRING_TYPES - All string-like types, encoded or otherwise
    ALL_STRING_TYPES = (str, bytes)

# vim: set ts=4 sw=4 st=4 expandtab :
