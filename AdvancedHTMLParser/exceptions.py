# Copyright (c) 2015, 2017 Tim Savannah under LGPLv3. 
# See LICENSE (https://gnu.org/licenses/lgpl-3.0.txt) for more information.
#  Exceptions used

__all__ = ('MultipleRootNodeException', 'HTMLValidationException', 'InvalidCloseException', 'MissedCloseException')

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
        InvalidCloseException - Raised when a tag is closed that shouldn't be closed.
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
        MissedCloseException - Raised when a close was missed
    '''
    
    def __init__(self, triedToClose, stillOpen):
        self.triedToClose = triedToClose
        self.stillOpen = stillOpen

        message = 'Attempted to close "%s" prior to closing: %s' %(triedToClose , str([x.tagName for x in stillOpen]))

        Exception.__init__(self, message)


#vim: set ts=4 sw=4 expandtab
