'''
    Copyright (c) 2019 Timothy Savannah under terms of LGPLv3. All Rights Reserved.

    See LICENSE (https://gnu.org/licenses/lgpl-3.0.txt) for more information.

    See: https://github.com/kata198/AdvancedHTMLParser for full information


    xpath.operation.py - Module defines operation type and related
'''
# vim: set ts=4 sw=4 st=4 expandtab :

from ._debug import getXPathDebug
from .exceptions import XPathParseError

from ..Tags import TagCollection, AdvancedTag

__all__ = ('XPathOperation', )

class XPathOperation(object):
    '''
        XPathOperation - Represents an XPath operation.

            A filter function on a list of elements, which when applied will return the next set of elements.
            An XPath expression will be compiled to a list of linear operations to achieve the final result.
    '''

    def __init__(self, filterFunction=None, thisOperationXPathStr=None):
        '''
            __init__ - Create an XPathOperation

                @param filterFunction <None/function/lambda> - The filter function to apply, or None to set later.

                @param thisOperationXPathStr <None/str> - The relevant portion of the xpath string associated with this operation, or None
        '''

        self.filterFunction = filterFunction
        self.thisOperationXPathStr = thisOperationXPathStr


    def applyFunction(self, prevResultTagCollection):
        '''
            applyFunction - Applies the associated function to this operation to the previous operation's output,

                to perform the next set of filtering steps and pass forward.


                @param prevResultTagCollection <AdvancedHTMLParser.Tags.TagCollection> - TagCollection of previous operation

                    If beginning, this should be a TagCollection of the starting tag/tags


                @return <AdvancedHTMLParser.Tags.TagCollection> - TagCollection of the results of this operation, to be passed forward

                    to the next operation (or returned as final result)
        '''

        resultNodes = []

        for prevTag in prevResultTagCollection:

             resultNodes += self.filterFunction( prevTag )

        return TagCollection( resultNodes )

    def __repr__(self):
        '''
            __repr__ - Informative represenative string display of this object.

                For now, will show the xpath str associated with this operation.
        '''

        return 'XPathOperation( thisOperationXPathStr="""%s""" )' %( self.thisOperationXPathStr or 'UNSET', )


# vim: set ts=4 sw=4 st=4 expandtab :
