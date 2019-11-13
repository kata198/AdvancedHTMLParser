'''
    Copyright (c) 2019 Timothy Savannah under terms of LGPLv3. All Rights Reserved.

    See LICENSE (https://gnu.org/licenses/lgpl-3.0.txt) for more information.

    See: https://github.com/kata198/AdvancedHTMLParser for full information

    xpath - Provide xpath support

        NOTE: THIS IS STILL IN ALPHA.

            Several parts of the XPath spec are not yet implemented,
             nor has the code yet been organized or optimized.

'''
# vim: set ts=4 st=4 sw=4 expandtab :

import copy
import re

from ..Tags import AdvancedTag, TagCollection

from .exceptions import XPathParseError
from ._filters import ( \
    _mk_xpath_op_filter_by_tagname_one_level_function, _mk_xpath_op_filter_by_tagname_one_level_function_or_self, \
    _mk_xpath_op_filter_by_tagname_multi_level_function, _mk_xpath_op_filter_by_tagname_multi_level_function_or_self, \
    _mk_xpath_op_filter_by_parent_tagname_one_level_function, \
    _mk_xpath_op_filter_by_ancestor_tagname_multi_level_function, _mk_xpath_op_filter_by_ancestor_or_self_tagname_multi_level_function, \
    _mk_xpath_op_filter_tag_is_nth_child_index, \
    _mk_helper_float_comparison_filter_named, _mk_helper_float_comparison_filter_wildcard, \
)
from .null import Null
from .expression import XPathOperation
from ._debug import getXPathDebug
from ._axes import TAG_OPERATION_AXES_POSSIBILITIES_REGEX_STR, TAG_OPERATION_AXES_TO_FIND_TAG_FUNC_GEN
from ._body import parseBodyStringIntoBodyElements, BodyElement, BodyElementOperation, BodyElementValue, BodyElementValueGenerator, BodyLevel_Top

NEXT_TAG_OPERATION_RE = re.compile(r'''^[ \t]*(?P<lead_in>[/]{1,2})[ \t]*(?P<full_tag>(((?P<axis>%s))[:][:]){0,1}(?P<tagname>[\*]|([a-zA-Z_][a-zA-Z0-9_]*))([:][:](?P<suffix>[a-zA-Z][a-zA-Z0-9_]*([\(][ \t]*[\)]){0,1})){0,1})''' %(TAG_OPERATION_AXES_POSSIBILITIES_REGEX_STR, ))

BRACKETED_SUBSET_RE = re.compile(r'''^[ \t]*[\[](?P<bracket_inner>((["]([\\]["]|[^"])*["])|([']([\\][']|[^'])*['])|[^\]])*)[\]][ \t]*''')

__all__ = ('parseXPathStrIntoOperations', )

def _buildOperationFromOperator(leftSide, operatorPart, rightSide):

    _leftSide = leftSide
    _operatorPart = operatorPart
    _rightSide = rightSide

    def _innerFunc(prevTag):

        comparisonPassed = bool( _operatorPart.evaluate( _leftSide, _rightSide ) )

        if comparisonPassed is True:

            return [prevTag]

        return []

    return _innerFunc



def parseBodyStringIntoBodyLevelTop(bodyString):
    curString = bodyString[:].strip()

    bodyElements = parseBodyStringIntoBodyElements(bodyString)
    ret = BodyLevel_Top()
    ret.appendBodyElements(bodyElements)

    return ret


def parseXPathStrIntoOperations(xpathStr):
    '''
        _parseXPathStrIntoOperations - INTERNAL - Processes the XPath string of this object into operations,

            and sets them on this object.
    '''

    DEBUG = getXPathDebug()

    # Bring into local namespace
    nextTagOperationRE = NEXT_TAG_OPERATION_RE
    bracketSubsetRE = BRACKETED_SUBSET_RE
    axesToFuncTagFuncGen = TAG_OPERATION_AXES_TO_FIND_TAG_FUNC_GEN

    remainingStr = xpathStr[:].strip()

    if DEBUG is True:
        firstDebugLine = "Parsing xpath str: %s" %( repr(remainingStr), )
        print ( "%s\n%s\n\n" %( firstDebugLine, '-' * len(firstDebugLine) ) )

    orderedOperations = []

    if not remainingStr:
        return orderedOperations

    keepGoing = True
    isFirst = True

    while keepGoing is True:

        tagOperationMatchObj = nextTagOperationRE.match(remainingStr)
        #    tagname - Always defined, the tag of operation for upcoming tag
        #    lead_in - Always defined, the lead in (either '/' or '//')

        # Check if we failed to parse
        if tagOperationMatchObj is None:

            # TODO: Better error message?
            raise XPathParseError('Could not parse xpath string, somewhere after: "%s"' %(remainingStr, ))

        thisGroupDict = tagOperationMatchObj.groupdict()

        thisTagName = thisGroupDict['tagname'].lower()
        thisLeadIn = thisGroupDict['lead_in']

        thisTagAxis = thisGroupDict['axis'] or None
        if thisTagAxis:
            thisTagAxis = thisTagAxis.strip().lower()
        thisTagSuffix = thisGroupDict['suffix'] or None
        if thisTagSuffix:
            thisTagSuffix = thisTagSuffix.strip().lower()

        endMatchIdx = tagOperationMatchObj.span()[1]
        # TODO: Be more efficient here
        remainingStr = remainingStr[ endMatchIdx : ].strip()
        thisXPathPortion = remainingStr[ : endMatchIdx ]

        # Now try to match this inner bracket
        thisBracketSubsetMatchObj = bracketSubsetRE.match(remainingStr)

        if thisBracketSubsetMatchObj is None:
            # No brackets at all
            thisInnerStr = None
        else:
            # Some brackets found, extract and strip inner
            thisInnerStr = thisBracketSubsetMatchObj.groupdict()['bracket_inner'].strip()

            # Move forward #remainingStr and add the inner portion to thiXPathPortion
            endMatchIdx = thisBracketSubsetMatchObj.span()[1]
            thisXPathPortion = remainingStr[ : endMatchIdx ]
            remainingStr = remainingStr[ endMatchIdx : ].strip()

        # TODO: Evaluate this next block, is it still correct?
        if thisLeadIn == '//':
            # TODO: unofficial fallback operations on the double '/' ?

            if isFirst is False:
                thisOperationFindTagFunc = _mk_xpath_op_filter_by_tagname_multi_level_function(thisTagName)
            else:
                thisOperationFindTagFunc = _mk_xpath_op_filter_by_tagname_multi_level_function_or_self(thisTagName)

        else:
            # Default with no axis or suffix (TODO: Any impossible axis + suffix combinations that break this pattern?)
            if isFirst is False:
                thisOperationFindTagFunc = _mk_xpath_op_filter_by_tagname_one_level_function(thisTagName)
            else:
                thisOperationFindTagFunc = _mk_xpath_op_filter_by_tagname_one_level_function_or_self(thisTagName)

        if (thisTagSuffix or '').replace(' ', '') == 'node()':

            if thisTagName == 'child':
                thisTagName = '*'

        if thisTagAxis:

            newFindFunc = axesToFuncTagFuncGen[thisTagAxis]

            if newFindFunc is not None:
                thisOperationFindTagFunc = newFindFunc(thisTagName)

            if False:

                # Should never happen
                # TODO: Can we bring back this error handling? The special parsing stuff removes it

                raise XPathParseError('Unhandled special tag axis "%s" in "%s" at "%s"' %(thisTagAxis, thisTagName, thisXPathPortion) )

        #XXX: NEEDED? # Check if we matched a trailing slash, if so reduce one from our index
        #if thisNoInnerText == '/':
        #    endMatchIdx -= 1

        #thisXPathPortion = remainingStr[ : endMatchIdx ]

        # XXX: Create an XPathOperation from this function

        # TODO: How much of this portion is needed?
        thisXPathOperation = XPathOperation( thisOperationFindTagFunc, thisXPathPortion )

        orderedOperations.append( thisXPathOperation )
        if DEBUG is True:
            print ( ' Parsed body: %s\n   lead =\t%-8s\n   tagn =\t%-20s\n   inner =\t%-50s\n\n' %( \
                    repr(thisXPathPortion), repr(thisLeadIn), repr(thisTagName), repr(thisInnerStr), \
                ) \
            )

        # XXX: Test inner body
        while thisInnerStr:

            # TODO: On an empty inner bracket, this will fail when it should be a no-op

            didMatch = False

            complexBody = parseBodyStringIntoBodyLevelTop(thisInnerStr)
            orderedOperations.append( complexBody )

            # TODO: Set this?
            didMatch = True
            if not didMatch:
                raise XPathParseError('Could not parse body: "%s" in expression: "%s"' %(thisInnerStr, thisXPathPortion))

            # Now try to match another inner bracket
            thisBracketSubsetMatchObj = bracketSubsetRE.match(remainingStr)

            if thisBracketSubsetMatchObj is None:
                # No brackets at all
                thisInnerStr = None
            else:
                # Some brackets found, extract and strip inner
                thisInnerStr = thisBracketSubsetMatchObj.groupdict()['bracket_inner'].strip()

                # Move forward #remainingStr and add the inner portion to thiXPathPortion
                endMatchIdx = thisBracketSubsetMatchObj.span()[1]
                thisXPathPortion += remainingStr[ : endMatchIdx ]
                if DEBUG is True:
                    additionalBody = remainingStr[ : endMatchIdx ]
                    print ( ' Parsed additional body: %s\n   lead =\t%-8s\n   tagn =\t%-20s\n   inner =\t%-50s\n\n' %( \
                            repr(additionalBody), repr(thisLeadIn), repr(thisTagName), repr(thisInnerStr), \
                        ) \
                    )
                remainingStr = remainingStr[ endMatchIdx : ].strip()



        # isFirst - Completed first round, set flag to False henceforth
        isFirst = False

        if not remainingStr:
            keepGoing = False


    return orderedOperations



# vim: set ts=4 st=4 sw=4 expandtab :
