'''
    Copyright (c) 2019 Tim Savannah  under terms of LGPLv3. All Rights Reserved.

    See LICENSE (https://gnu.org/licenses/lgpl-3.0.txt) for more information.


    compat - Some python2/python3 compatibility things
'''
# vim: set ts=4 sw=4 st=4 expandtab :

import sys

__all__ = ('STRING_TYPES', 'RAW_STRING_TYPE', 'ALL_STRING_TYPES', 'ensureStringEncoded')

if sys.version_info.major < 3:

    # STRING_TYPES - Types that represent strings ("printable")
    STRING_TYPES = (str, unicode)

    # RAW_STRING_TYPE - The type of a raw "encoded" string
    RAW_STRING_TYPE = str

    # ALL_STRING_TYPES - All string-like types, encoded or otherwise
    ALL_STRING_TYPES = (str, unicode)

    # DECODED_STR_TYPE - String type that has been decoded
    DECODED_STR_TYPE = unicode

else:

    # STRING_TYPES - Types that represent strings ("printable")
    STRING_TYPES = (str, )

    # RAW_STRING_TYPE - The type of a raw "encoded" string
    RAW_STRING_TYPE = bytes

    # ALL_STRING_TYPES - All string-like types, encoded or otherwise
    ALL_STRING_TYPES = (str, bytes)

    # DECODED_STR_TYPE - String type that has been decoded
    DECODED_STR_TYPE = str


def ensureStringEncoded(theString, encoding='utf-8'):
    '''
        ensureStringEncoded - Ensure we have the encoded type for a given string


            @param theString <str/unicode/bytes> - A string-like object

            @param encoding <str> Default 'utf-8' - The encoding to use

                NOTE: If this string is already encoded, we do NOT ensure it is encoded in this type,
                  this type is only used when we have a decoded string, in order to encode it.


            @return (python3)<bytes> / (python2)<str> - A string encoded in utf-8
    '''

    if issubclass( theString.__class__, DECODED_STR_TYPE ):
        return theString.encode('utf-8')

    return theString

# vim: set ts=4 sw=4 st=4 expandtab :
