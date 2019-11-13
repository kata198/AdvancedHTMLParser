'''
    Copyright (c) 2019 Timothy Savannah under terms of LGPLv3. All Rights Reserved.

    See LICENSE (https://gnu.org/licenses/lgpl-3.0.txt) for more information.

    See: https://github.com/kata198/AdvancedHTMLParser for full information


    xpath.expression.py - Module defines some types and features related to expressions
'''
# vim: set ts=4 sw=4 st=4 expandtab :

from ..Tags import TagCollection, AdvancedTag

from ._debug import getXPathDebug
from .exceptions import XPathParseError
from .operation import XPathOperation
from .parsing import parseXPathStrIntoOperations


__all__ = ('XPathExpression', )


class XPathExpression(object):
    '''
        XPathExpression - The main class for dealing with XPath expressions
    '''


    def __init__(self, xpathStr):
        '''
            __init__ - Create this object from a string expression

                @param xpathStr <str> - An xpath expression
        '''

        self.xpathStr = xpathStr
        self.orderedOperations = parseXPathStrIntoOperations(self.xpathStr)


    def evaluate(self, pathRoot):
        '''
            evaluate - Run this XPath expression against a tree, and return the results.

                @param pathRoot <
        curResults = [ pathRoot ]
                        Tags.AdvancedTag [From a single root tag] -or-
                        Parser.AdvancedHTMLParser [From the root of a document] -or-
                        (list/tuple)<Tags.AdvancedTag> [From a list or tuple of tags] -or-
                        Tags.TagCollecction [From a TagCollection of tags]
                    > -
                          Run this XPath expression against this/these given node/nodes/document


                @return <TagCollection> - A TagCollection of matched tags
        '''

        # Late binding import
        from ..Parser import AdvancedHTMLParser

        pathRootClass = pathRoot.__class__

        # TODO: Support starting from a text node (not a tag node) ?
        # TODO: Check for "None" ?
        if issubclass(pathRootClass, AdvancedTag):

            # A single tag
            curResults = [ pathRoot ]

        elif issubclass(pathRootClass, AdvancedHTMLParser):

            # A "document" (AdvancedHTMLParser instance)
            curResults = pathRoot.getRootNodes()

            # TODO: Test if above is okay,
            #     e.x. will /html[1] return the <html> as expected, or fail to find because start at <html? ?

        # TagCollection is a subclass of list, so check it explicitly, first.
        elif issubclass(pathRootClass, TagCollection):

            # A TagCollection -- convert to a basic list
            #  NOTE: Just cast to list instead?
            curResults = pathRoot.all()

        elif issubclass(pathRootClass, (list, tuple)):

            # If a list/tuple, make into a copy list
            curResults = list(pathRoot)

            # TODO: Check if the elements in #pathRoot are actually Tags.AdvancedTag objects?

        else:

            raise ValueError('Unknown type < %s > ( %s ) passed to XPathExpression.evaluate! Should be Tags.AdvancedTag or Parser.AdvancedHTMLParser or Tags.TagCollectiojn or list/tuple<Tags,AdvancedTag>.' %( pathRootClass.__name__, str(type(pathRoot)) ) )


        # Make a fresh TagCollection, even if we were passed one at start
        curCollection = TagCollection(curResults)

        for orderedOperation in self.orderedOperations:

            thisResultCollection = orderedOperation.applyFunction( curCollection )

            if len(thisResultCollection) == 0:

                # TODO: Why create fresh?
                return TagCollection()

            curCollection = thisResultCollection

        return curCollection


# vim: set ts=4 sw=4 st=4 expandtab :
