'''
    Copyright (c) 2015, 2017, 2019 Tim Savannah under LGPLv3. All Rights Reserved.

    See LICENSE (https://gnu.org/licenses/lgpl-3.0.txt) for more information.

    Exceptions used by AdvancedHTMLParser
'''

__all__ = ('MultipleRootNodeException', 'HTMLValidationException', 'InvalidCloseException', 'MissedCloseException', 'IndexSizeErrorException')

class MultipleRootNodeException(Exception):
    '''
        Exception raised and used internally when you try to use multiple root nodes
          Example:
            <one>
              <b>Hi</b>
              <i>Hello</i>
            </one>
            <two>
              <b>Cheese</b>
              <i>Ssdf</i>
            </two>

        This is legal, a fake root node with tag name of constants.INVISIBLE_TAG_NAME will be set at head, and all methods will handle it correctly.
        If you need to get the root nodes, and there's the possibility of more than one, consider getRootObjects instead of getRoot.
    '''
    pass


class HTMLValidationException(Exception):
    '''
        HTMLValidationException - common baseclass for invalid-HTML validation errors
    '''
    pass


class InvalidCloseException(HTMLValidationException):
    '''
        InvalidCloseException - Raised when a tag is closed that shouldn't be closed in validating parser
    '''

    def __init__(self, triedToClose, stillOpen):
        self.triedToClose = triedToClose
        self.stillOpen = stillOpen
        if not stillOpen:
            message = 'Attempted to close "%s", but there are no open tags.' %(triedToClose, )
        else:
            message = 'Attempted to close "%s", but it does not match any of the open tags: %s' %(triedToClose, str([x.tagName for x in stillOpen]),)

        Exception.__init__(self, message)


class MissedCloseException(HTMLValidationException):
    '''
        MissedCloseException - Raised when a close was missed in validating parser
    '''

    def __init__(self, triedToClose, stillOpen):
        self.triedToClose = triedToClose
        self.stillOpen = stillOpen

        message = 'Attempted to close "%s" prior to closing: %s' %(triedToClose , str([x.tagName for x in stillOpen]))

        Exception.__init__(self, message)


class InvalidAttributeNameException(HTMLValidationException):
    '''
        InvalidAttributeNameException - Raised when an invalid attribute name is found when parsing via validating parser
    '''

    def __init__(self, tagName, badAttributeName, badAttributeValue):
        '''
            __init__ - Create this object

                @param tagName <str> - Tag name

                @param badAttributeName <str> - Bad attribute name

                @param badAttributeValue <str> - Bad attribute value
        '''

        message = 'Parsed a tag %s  which contains an invalid attribute, %s = %s . ( Maybe characters outside quotes in tag? )' % ( \
            tagName, repr(badAttributeName), repr(badAttributeValue) \
        )

        Exception.__init__(self, message)


class IndexSizeErrorException(ValueError):

    def __init__(self, *args, **kwargs):
        if len(args) == 0 and len(kwargs) == 0:
            ValueError.__init__(self, "Index or size is negative or greater than the allowed amount")
        else:
            ValueError.__init__(self, *args, **kwargs)

#vim: set ts=4 sw=4 expandtab
