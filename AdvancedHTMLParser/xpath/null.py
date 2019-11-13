'''
    Copyright (c) 2019 Timothy Savannah under terms of LGPLv3. All Rights Reserved.

    See LICENSE (https://gnu.org/licenses/lgpl-3.0.txt) for more information.

    See: https://github.com/kata198/AdvancedHTMLParser for full information


    xpath.null.py - The XPath engine null type and related

'''
# vim: set ts=4 sw=4 st=4 expandtab :


__all__ = ( 'NullType', 'Null', )

class NullType(object):
    '''
        NullType - Represents a comparative class for use with Null (equal to other nulls, not equal to non-nulls)

          "Null" is the singleton instance of this class, and should be used instead of separate instances, but either will work.
    '''

    def __eq__(self, other):

        return bool( isinstance(other, NullType) )

    def __ne__(self, other):

        return not bool( isinstance(other, NullType) )


# Null - Singleton for the NullType
Null = NullType()



# vim: set ts=4 sw=4 st=4 expandtab :
