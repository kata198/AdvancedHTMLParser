'''
    Copyright (c) 2019 Timothy Savannah under terms of LGPLv3. All Rights Reserved.

    See LICENSE (https://gnu.org/licenses/lgpl-3.0.txt) for more information.

    See: https://github.com/kata198/AdvancedHTMLParser for full information


    ==INTERNAL==

    xpath._body.py - Internal module for dealing with items within the "body" of a filter expression on a tag
'''
# vim: set ts=4 sw=4 st=4 expandtab :

import copy
import re

from ..Tags import TagCollection

from .exceptions import XPathNotImplementedError, XPathRuntimeError, XPathParseError
from ._filters import _mk_xpath_op_filter_tag_is_nth_child_index
from .null import Null


# TODO: __all__ not complete
#__all__ = ('parseBodyStringIntoBodyElements', )


BODY_VALUE_TYPE_UNKNOWN = 0
BODY_VALUE_TYPE_NUMBER = 1
# Leave a gap for 2 should we split float/int
BODY_VALUE_TYPE_STRING = 3
BODY_VALUE_TYPE_BOOLEAN = 4
# List - Unimplemented
BODY_VALUE_TYPE_LIST = 5
BODY_VALUE_TYPE_NULL = 6

class BodyLevel(object):
    '''
        BodyLevel - A single "level" of a body
    '''

    def __init__(self):
        '''
            __init__ - Create this object
        '''
        self.bodyElements = []


    # TODO: Give these a better name, as they could contain BodyElement or BodyLevels
    def appendBodyElement(self, bodyElement):
        '''
            appendBodyElement - Add a body element to the current tail of this level


                @param bodyElement <BodyElement> - The body element to add
        '''
        self.bodyElements.append(bodyElement)


    def appendBodyElements(self, bodyElements):
        '''
            addBodyElements - Add a list of body elements to the current tail of this level


                @param bodyElements list<BodyElement> - A list of BodyElements to add
        '''
        self.bodyElements += bodyElements


    def evaluate(self, currentTags):
        '''
            evaluate - Evaluate this level, and return the tags which match the criteria


                @param currentTags list/TagCollection < AdvancedTag > - The current set of tags to process


                @return TagCollection < AdvancedTag > - The tags which "pass" this level
        '''
        pass


# TODO: Need to refactor this a bit maybe, to support levels as designed
class BodyLevel_Top(BodyLevel):
    '''
        BodyLevel_Top - The topmost level of a body. This is the final evaluation before passing onto the next tag filter
    '''

    def evaluate(self, currentTags):
        '''
            evaluate - Evaluate the topmost level, and return tags to match.

                For the topmost level, we run all components left-to-right, and evaluate the result.

                If an integer remains, we use that 1-origin Nth child of parent.
                If a boolean remains, we use True to retain, False to discard.
        '''
        thisLevelElements = self.bodyElements

        if len(thisLevelElements) == 0:
            # This is an empty [], just return same tags
            return currentTags

        retTags = []

        # TODO: Optimize this function

        for thisTag in currentTags:

            # stillProcessingTagValueGenerators - Loop while we are still processing down to only values/operations
            stillProcessingTagValueGenerators = True

            # curElements - The current set of elements for this tag, as we unroll, this will change.
            #                 Initial value will be a copy of the original set of elements
            curElements = copy.deepcopy(thisLevelElements)

            # Loop until we are done with value generators
            while stillProcessingTagValueGenerators is True:

                # Set to False, we will trigger to True if there is a reason to iterate again (a sub level, for example)
                stillProcessingTagValueGenerators = False

                # nextElements - We will assemble into this list the next iteration of #curElements
                nextElements = []

                for thisBodyElement in curElements:

                    thisBodyElementClass = thisBodyElement.__class__

                    # TODO: Optimize
                    if issubclass(thisBodyElementClass, BodyElementValue):
                        # A value, static or otherwise, throw it on the stack.
                        nextElements.append( thisBodyElement )
                        continue

                    elif issubclass(thisBodyElementClass, (BodyElementOperation, BodyElementComparison, BodyElementBooleanOps)):
                        # An operation, we will run these after value generators have processed.
                        #  NOTE: Can be optimized further, as we may not need to unroll all value generators before passing/failing a node
                        # Just throw it back onto list for now
                        nextElements.append( thisBodyElement )
                        continue

                    elif issubclass(thisBodyElementClass, BodyElementValueGenerator):
                        # A value generator, run this against the current tag
                        generatedValue = thisBodyElement.resolveValueFromTag(thisTag)

                        nextElements.append( generatedValue )

                        # NOTE: Currently, resolveValueFromTag always returns a BodyElementValue,
                        #         but in the future it may not.
                        #       So, conditionally loop if we got a non-value returned
                        if not issubclass(generatedValue.__class__, BodyElementValue):
                            stillProcessingTagValueGenerators = True

                        continue

                    else:

                        raise XPathRuntimeError('Found an unexpected type in list of level elements: %s . Repr: %s' %( thisBodyElementClass.__name__, repr(thisBodyElement)) )

                # Update #curElements
                curElements = nextElements

            # At this point, we should have only values and operations. Run through until no operations remain

            # TODO: This variable and associated loop are not needed?
            stillProcessingTagOperations = True

            while stillProcessingTagOperations is True:

                stillProcessingTagOperations = False

                nextElements = []

                prevValue = None

                # TODO: Check for impossible types in operations here?

                numElements = len(curElements)
                i = 0

                while i < numElements:

                    thisBodyElement = curElements[i]
                    thisBodyElementClass = thisBodyElement.__class__

                    if issubclass(thisBodyElementClass, (BodyElementValue, BodyElementComparison, BodyElementBooleanOps)):

                        # Throw values and comparisons back on the stack as-is
                        nextElements.append( thisBodyElement )
                        prevValue = thisBodyElement

                        i += 1
                        continue

                    else:
                        # XXX Must be an Operation. All other types exhausted by this point.

                        if (i + 1) >= numElements:
                            # TODO: Better error message?
                            raise XPathParseError('XPath expression ends in an operation, no right-side to operation.')

                        leftSide = prevValue
                        if not issubclass(leftSide.__class__, BodyElementValue):
                            # TODO: Better error message?
                            raise XPathParseError('XPath expression contains two consecutive operations (left side)')

                        rightSide = curElements[i + 1]
                        if not issubclass(rightSide.__class__, BodyElementValue):
                            # TODO: Better error message?
                            raise XPathParseError('XPath expression contains two consecutive operations (right side)')

                        resolvedValue = thisBodyElement.performOperation(leftSide, rightSide)

                        if not issubclass(resolvedValue.__class__, BodyElementValue):
                            # Not a value? Loop again.
                            print ( "WARNING: Got a non-value returned from performOperation" )
                            stillProcessingTagOperations = True

                        # Pop the last value (left side), drop the operation, load the resolved value in place.
                        nextElements = nextElements[ : -1 ] + [resolvedValue]

                        # Move past right side
                        i += 2
                        continue

                # Update the current set of elements
                curElements = nextElements

            stillProcessingTagComparisons = True

            while stillProcessingTagComparisons is True:

                stillProcessingTagComparisons = False

                nextElements = []

                prevValue = None

                # TODO: Check for impossible types in operations here?

                numElements = len(curElements)
                i = 0

                while i < numElements:

                    thisBodyElement = curElements[i]
                    thisBodyElementClass = thisBodyElement.__class__

                    if issubclass(thisBodyElementClass, (BodyElementValue, BodyElementBooleanOps)):

                        nextElements.append( thisBodyElement )
                        prevValue = thisBodyElement

                        i += 1
                        continue

                    else:
                        # XXX Must be a Comparison, all other types exhausted

                        if (i + 1) >= numElements:
                            # TODO: Better error message?
                            raise XPathParseError('XPath expression ends in an operation, no right-side to operation.')

                        leftSide = prevValue
                        if not issubclass(leftSide.__class__, BodyElementValue):
                            # TODO: Better error message?
                            raise XPathParseError('XPath expression contains two consecutive operations (left side)')

                        rightSide = curElements[i + 1]
                        if not issubclass(rightSide.__class__, BodyElementValue):
                            # TODO: Better error message?
                            raise XPathParseError('XPath expression contains two consecutive operations (right side)')

                        resolvedValue = thisBodyElement.doComparison(leftSide, rightSide)

                        if not issubclass(resolvedValue.__class__, BodyElementValue):
                            # Not a value? Loop again.
                            print ( "WARNING: Got a non-value returned from performOperation" )
                            stillProcessingTagComparisons = True

                        # Pop the last value (left side), drop the operation, load the resolved value in place.
                        nextElements = nextElements[ : -1 ] + [resolvedValue]

                        # Move past right side
                        i += 2
                        continue

                # Update the current set of elements
                curElements = nextElements


            # TODO: Should restructure this per the "levels" design such that we can short circuit
            stillProcessingTagBooleanOps = True

            while stillProcessingTagBooleanOps is True:

                stillProcessingTagBooleanOps = False

                nextElements = []

                prevValue = None

                numElements = len(curElements)
                i = 0

                while i < numElements:

                    thisBodyElement = curElements[i]
                    thisBodyElementClass = thisBodyElement.__class__

                    if issubclass(thisBodyElementClass, BodyElementValue):

                        nextElements.append( thisBodyElement )
                        prevValue = thisBodyElement

                        i += 1
                        continue

                    else:
                        # XXX Must be a BooleanOps all other types exhausted

                        if (i + 1) >= numElements:
                            # TODO: Better error message?
                            raise XPathParseError('XPath expression ends in an operation, no right-side to operation.')

                        leftSide = prevValue
                        if not issubclass(leftSide.__class__, BodyElementValue):
                            # TODO: Better error message?
                            raise XPathParseError('XPath expression contains two consecutive operations (left side)')

                        rightSide = curElements[i + 1]
                        if not issubclass(rightSide.__class__, BodyElementValue):
                            # TODO: Better error message?
                            raise XPathParseError('XPath expression contains two consecutive operations (right side)')

                        resolvedValue = thisBodyElement.doBooleanOp(leftSide, rightSide)

                        if not issubclass(resolvedValue.__class__, BodyElementValue):
                            # Not a value? Loop again.
                            print ( "WARNING: Got a non-value returned from performOperation" )
                            stillProcessingTagBooleanOps = True

                        # Pop the last value (left side), drop the operation, load the resolved value in place.
                        nextElements = nextElements[ : -1 ] + [resolvedValue]

                        # Move past right side
                        i += 2
                        continue

                # Update the current set of elements
                curElements = nextElements


            # At this point, should be only one value left. Zero was already handled at start
            numElementsRemaining = len(curElements)
            if numElementsRemaining != 1:
                raise XPathRuntimeError('Got unexpected current number of elements at the end. Expected 1, got %d.  Repr: %s' %( numElementsRemaining, repr(curElements) ) )


            finalValue = curElements[0]
            finalValueClass = finalValue.__class__

            if finalValue.VALUE_TYPE == BODY_VALUE_TYPE_NUMBER:

                # TODO: Make sure is an integer and not a float
                innerNum = int( finalValue.getValue() )

                # TODO: Better.
                testFunc = _mk_xpath_op_filter_tag_is_nth_child_index(thisTag.tagName, innerNum)

                retTags += testFunc( thisTag )

            elif finalValue.VALUE_TYPE == BODY_VALUE_TYPE_BOOLEAN:

                shouldRetainTag = finalValue.getValue()

                if shouldRetainTag is True:
                    retTags.append( thisTag)

            else:

                raise XPathRuntimeError('Final value was not an integer or a boolean, cannot proceed. Was: %s . Repr: %s' %(finalValueClass.__name__, repr(finalValue)) )

        return TagCollection(retTags)


    applyFunction = evaluate


class BodyElement(object):
    '''
        BodyElement - Base class of body elements
    '''
    pass


class BodyElementValue(BodyElement):
    '''
        BodyElementValue - Base class of BodyElements which represent a resolved value
    '''

    # VALUE_TYPE - The type of this value. Should be set by subclass
    VALUE_TYPE = BODY_VALUE_TYPE_UNKNOWN

    def __init__(self, value):
        '''
            __init__ - Create this element as a wrapper around an already-calculated value
        '''
        self.value = None
        self.setValue(value)


    def getValue(self):
        '''
            getvalue - Get the value associated with this object
        '''
        return self.value


    def setValue(self, newValue):
        '''
            setValue - Sets the value associated with this object

              This will be called on all value sets, including __init__ (and from regex)


                @param newValue <???> - The new value for this object
        '''
        self.value = newValue


# TODO: Stronger type checking on these?

class BodyElementValue_Boolean(BodyElementValue):
    '''
        BodyElementValue_Boolean - A True/False BodyElementValue, like returned by a comparison operation
    '''

    VALUE_TYPE = BODY_VALUE_TYPE_BOOLEAN

    def setValue(self, newValue):
        '''
            setValue - Set a boolean value


                @param newValue <bool> - Boolean value


                @see BodyElementValue.setValue
        '''
        if not isinstance(newValue, bool):
            raise XPathRuntimeError('BodyElementValue_Boolean tried to setValue as a non-boolean type. Was: %s . Repr: %s' %( newValue.__class__.__name__, repr(newValue) ))

        self.value = newValue


class BodyElementValue_String(BodyElementValue):
    '''
        BodyElementValue_String - A string BodyElementValue
    '''

    VALUE_TYPE = BODY_VALUE_TYPE_STRING

    def setValue(self, newValue):
        '''
            setValue - Set a string value


                @param newValue <str> - String value


                @see BodyElementValue.setValue
        '''
        # TODO: Check type of newValue against str (or str/unicode for py2) ?
        self.value = str(newValue)


class BodyElementValue_Null(BodyElementValue):
    '''
        BodyElementValue_Null - A null BodyElementValue
    '''

    VALUE_TYPE = BODY_VALUE_TYPE_NULL

    def __init__(self, value=Null):
        '''
            __init__ - Create this object. Override default to allow passing no value (there is only one)
        '''
        BodyElementValue.__init__(self, value)


    def setValue(self, newValue=Null):
        '''
            setValue - Set a null value


                @param newValue <str> - String value


                @see BodyElementValue.setValue
        '''
        # TODO: Do we want this? None == Null?
        if newValue is None:
            newValue = Null

        if newValue != Null:
            raise XPathRuntimeError('BodyElementValue_Null tried to set a value but was not Null. Was: %s . Repr: %s' %( newValue.__class__.__name__, repr(newValue)))

        self.value = newValue


class BodyElementValue_Number(BodyElementValue):
    '''
        BodyElementValue_Number - A numeric BodyElementValue
    '''

    VALUE_TYPE = BODY_VALUE_TYPE_NUMBER

    def setValue(self, newValue):
        '''
            setValue - Sets the inner value to a float, or raises exception on failure to convert.


                @param newValue <str/float> - A number (positive or negative, integer or float)


                @raises XPathRuntimeError - Type passed is not convertable to float


                @see BodyElementValue_StaticValue.setValue
        '''
        try:
            self.value = float(newValue)
        except Exception as fe:
            raise XPathRuntimeError('Runtime Type Error: BodyElementValue_StaticValue_Number was passed a value, <%s> %s  -- but could not convert to float. %s  %s' %( \
                    type(newValue).__name__,
                    repr(newValue),
                    fe.__class__.__name__,
                    str(fe),
                )
            )



#############################
##    Value Generators     ##
#############################


# VALUE_GENERATOR_RES - A list of tuples, which will be iterated upon parsing a body to create the ValueGenerator types
#                        Tuples are in format: ( re.compile'd expression, BodyElementValueGenerator child class implementing related )
#
#                           Where all of the named groups within the compiled regular expression are passed to __init__ of the related class.
VALUE_GENERATOR_RES = []


class BodyElementValueGenerator(BodyElement):
    '''
        BodyElementValueGenerator - Base class of BodyElements which resolve to a BodyValue after execution with context of a tag
    '''


    def resolveValueFromTag(self, thisTag):
        '''
            resolveValueFromTag - Process "thisTag" to obtain a BodyElementValue relative to this tag and the extending class's implementation


                @param thisTag <Tags.AdvancedTag> - The tag of relevance


                @return <BodyElementValue> - The resulting value
        '''
        raise NotImplementedError('BodyElementValueGenerator.resolveValueFromTag is not implemented in type %s! Must use a class extending BodyElementValueGenerator' % ( \
                self.__class__.__name__,
            )
        )


class BodyElementValueGenerator_FetchAttribute(BodyElementValueGenerator):

    def __init__(self, attributeName):
        '''
            __init__ - Create this Value Generator to fetch the value of an attribute

              on a tag.

                @param attributeName <str> - The name of the attribute to fetch
        '''
        BodyElementValueGenerator.__init__(self)

        self.attributeName = attributeName


    def resolveValueFromTag(self, thisTag):
        '''
            resolveValueFromTag - Fetch the value of a given attribute from a tag, and return the value.


                @param thisTag <Tags.AdvancedTag> - An instance of a tag on which to work


                @return <BodyElementValue> - The value of the attribute, or Null, wrapped in a BodyElementValue container
        '''
        attributeName = self.attributeName

        if attributeName == '*' or '*' in attributeName:
            raise XPathNotImplementedError('Wildcard attributes are not yet supported!')

        # TODO: Can just use getAttribute with a default?


        if not thisTag.hasAttribute( attributeName ):
            # No attribute present, return Null
            return BodyElementValue_Null()


        val = '%s' %( thisTag.getAttribute(attributeName), )
        return BodyElementValue_String(val)



BEVG_FETCH_ATTRIBUTE_RE = re.compile(r'^[ \t]*[@](?P<attributeName>([*]|[a-zA-Z_][a-zA-Z0-9_\-]*))[ \t]*')
VALUE_GENERATOR_RES.append( (BEVG_FETCH_ATTRIBUTE_RE, BodyElementValueGenerator_FetchAttribute) )


class BodyElementValueGenerator_NormalizeSpace(BodyElementValueGenerator):
    '''
        BodyElementValueGenerator_NormalizeSpace - Implement the 'normalize-space()' function
    '''

    def __init__(self, functionInner=None):

        BodyElementValueGenerator.__init__(self)


    def resolveValueFromTag(self, thisTag):

        return BodyElementValue_String( thisTag.innerText.strip() )


BEVG_NORMALIZE_SPACE_RE = re.compile(r'^([ \t]*[nN][oO][rR][mM][aA][lL][iI][zZ][eE][\-][sS][pP][aA][cC][eE][ \t]*[\(][ \t]*[\)][ \t]*)')
VALUE_GENERATOR_RES.append( (BEVG_NORMALIZE_SPACE_RE, BodyElementValueGenerator_NormalizeSpace) )


class BodyElementValueGenerator_Text(BodyElementValueGenerator):
    '''
        BodyElementValueGenerator_Text - Implement the 'text()' function
    '''

    def __init__(self, functionInner=None):

        BodyElementValueGenerator.__init__(self)


    def resolveValueFromTag(self, thisTag):

        return BodyElementValue_String( thisTag.innerText )


BEVG_TEXT_RE = re.compile(r'^([ \t]*[tT][eE][xX][tT][ \t]*[\(][ \t]*[\)][ \t]*)')
VALUE_GENERATOR_RES.append( (BEVG_TEXT_RE, BodyElementValueGenerator_Text) )


class BodyElementValueGenerator_ConcatFunction(BodyElementValueGenerator):
    '''
        BodyElementValueGenerator_ConcatFunction - Implement the 'concat(...)' function
    '''

    ARG_SPLIT_RE = re.compile(r'''^[ \t]*(?P<arg_value>(["]([\\]["]|[^"])*["])|([']([\\][']|[^'])*[']))[ \t]*(?P<nextarg_comma>[,]{0,1})[ \t]*''')

    def __init__(self, fnArgsStr):
        '''
            __init__ - Create this object

                @param fnArgsStr <str> - Arguments to this function, strings to concatenate
        '''
        BodyElementValueGenerator.__init__(self)

        # TODO: Args other than static strings?

        # TODO: Parse to a static value during xpath parsing rather than every execution?
        #        For now, always split (for when we support things besides static string), but
        #         we could optimize in the future.

        fnArgsStr = fnArgsStr.strip()
        if not fnArgsStr:
            # TODO: Better error message, containing the context?
            raise XPathParseError('concat function present, but missing required arguments!')

        # fnArgs - The arguments to concat
        self.fnArgs = fnArgs = []

        # remainingStr - Arguments yet to be parsed
        remainingStr = fnArgsStr

        argSplitRE = self.ARG_SPLIT_RE

        # self.isConstantValue - True if we are concatenating static strings, and always will be same value.
        #                        False if we are concatenating something dynamic, like an attribute value, which needs
        #                          to be calculated for every tag.
        self.isConstantValue = True
        self.constantValue = None

        while remainingStr:

            nextArgMatchObj = argSplitRE.match(remainingStr)
            if not nextArgMatchObj:
                raise XPathParseError('Failed to parse arguments to concat function.\nAll arguments: """%s"""\nError at: """%s"""' %(fnArgsStr, remainingStr))

            groupDict = nextArgMatchObj.groupdict()

            # TODO: Replace escaped quote with actual quote? e.x. 'don\'t do that' we should drop the escape

            # Strip first and last character, as these will always be the quote (" or ')
            thisValue = groupDict['arg_value'][1:-1]

            # nextStr - What remains after this arg
            nextStr = remainingStr[ nextArgMatchObj.span()[1] : ]

            hasCommaAfterValue = bool(groupDict['nextarg_comma'])

            if hasCommaAfterValue is True and not nextStr:
                # We have a trailing comma, but no next arg
                raise XPathParseError('Trailing comma without an arg following in concat function: """%s"""' %(fnArgsStr, ))

            elif hasCommaAfterValue is False and nextStr:
                # We have a next argument string, but no comma
                # TODO: Need to support things like nested function calls, etc, as args
                raise XPathParseError('Junk / unsupported value in concat function.\nAll arguments: """%s"""\nError at: """%s"""' %(fnArgsStr, nextStr))

                # Set this to False when we have a generator or similar present
                self.isConstantValue = False

            # Completed validation, add this as an argument and move on
            fnArgs.append(thisValue)

            remainingStr = nextStr

        if len(fnArgs) < 2:
            raise XPathParseError('concat function takes at least two arguments, but found only %d. Error is at: %s' %( len(fnArgs), fnArgsStr ) )

        if self.isConstantValue is True:
            # We are concatenating static values only, so calculate now instead of for every tag processed
            val = ''.join(self.fnArgs)
            self.constantValue = BodyElementValue_String(val)


    def resolveValueFromTag(self, thisTag):
        '''
            resolveValueFromTag - Return the concatenated string


                @param thisTag <AdvancedTag> - The tag of interest


                @return <BodyElementValue_String> - The concatenated string as a body element value
        '''
        if self.isConstantValue is True:
            return self.constantValue

        valParts = []

        # TODO: Right now we only handle static strings, but we could parse to body element value generators, etc, and calculate here.
        for fnArg in self.fnArgs:
            fnArgClass = fnArg.__class__

            if issubclass(fnArgClass, BodyElementValueGenerator):
                valPart = fnArg.resolveValueFromTag(thisTag)

            elif issubclass(fnArgClass, BodyElementValue):
                # TODO: Is this right?
                # TODO: Handle float vs integer?
                valPart = str( fnArg.getValue() )

            elif issubclass(fnArgClass, str):
                # TODO: python2 compat w/ unicode
                valPart = fnArg

            else:
                raise XPathRuntimeError('Unhandled type for concat: %s . Repr: %s' %( fnArgClass.__name__, repr(fnArg) ) )

            valParts.append(valPart)

        val = ''.join(valParts)
        return BodyElementValue_String(val)


# TODO: Improve the fnArgsStr group to handle quoted parens
BEVG_CONCAT_FUNCTION_RE = re.compile(r'''^([ \t]*[cC][oO][nN][cC][aA][tT][ \t]*[\(][ \t]*(?P<fnArgsStr>[^\)]+)[ \t]*[\)][ \t]*)''')
VALUE_GENERATOR_RES.append( (BEVG_CONCAT_FUNCTION_RE, BodyElementValueGenerator_ConcatFunction) )


class BodyElementValueGenerator_Last(BodyElementValueGenerator):
    '''
        BodyElementValueGenerator_Text - Implement the 'text()' function
    '''

    def __init__(self, functionInner=None):

        BodyElementValueGenerator.__init__(self)


    def resolveValueFromTag(self, thisTag):

        parentElement = thisTag.parentElement

        if parentElement is None:

            # No parent, last() must be 1
            return '1'

        thisTagName = thisTag.tagName

        childrenOfRelevance = [ childEm for childEm in parentElement.children if childEm.tagName == thisTagName ]

        return BodyElementValue_Number( len( childrenOfRelevance ) )


BEVG_LAST_RE = re.compile(r'''^([ \t]*[lL][aA][sS][tT][ \t]*[\(][ \t]*[\)][ \t]*)''')
VALUE_GENERATOR_RES.append( (BEVG_LAST_RE, BodyElementValueGenerator_Last) )


class BodyElementValueGenerator_Position(BodyElementValueGenerator):
    '''
        BodyElementValueGenerator_Position - Implement the 'position()' function
    '''

    def __init__(self, functionInner=None):

        BodyElementValueGenerator.__init__(self)


    def resolveValueFromTag(self, thisTag):

        parentElement = thisTag.parentElement

        if parentElement is None:

            # No parent, position() must be 1
            return '1'

        thisTagName = thisTag.tagName

        childrenOfRelevance = [ childEm for childEm in parentElement.children if childEm.tagName == thisTagName ]

        return BodyElementValue_Number( childrenOfRelevance.index( thisTag ) + 1 )


BEVG_POSITION_RE = re.compile(r'^([ \t]*[pP][oO][sS][iI][tT][iI][oO][nN][ \t]*[\(][ \t]*[\)][ \t]*)')
VALUE_GENERATOR_RES.append( (BEVG_POSITION_RE, BodyElementValueGenerator_Position) )



#############################
##        Operations       ##
#############################


# OPERATION_RES - A list of tuples, which will be iterated upon parsing a body to create the Operation types
#                        Tuples are in format: ( re.compile'd expression, BodyElementOperation child class implementing related )
#
#                           Where all of the named groups within the compiled regular expression are passed to __init__ of the related class.
OPERATION_RES = []


class BodyElementOperation(BodyElement):
    '''
        BodyElementOperation - Base class of BodyElements which perform some operation against the other body elements
    '''


    def performOperation(self, leftSide, rightSide):
        raise NotImplementedError('BodyElementOperation.performOperation is not implemented in type %s! Must use a class extending BodyElementOperation' % ( \
                self.__class__.__name__,
            )
        )
        pass


#############################
##       Comparisons       ##
#############################


# COMPARISON_RES - A list of tuples, which will be iterated upon parsing a body to create the Comparison types
#                        Tuples are in format: ( re.compile'd expression, BodyElementComparison child class implementing related )
#
#                           Where all of the named groups within the compiled regular expression are passed to __init__ of the related class.
COMPARISON_RES = []


class BodyElementComparison(BodyElement):
    '''
        BodyElementComparison - Base class of Comparison operations (such as equals, not equals, greater than, etc.)
    '''

    # NUMERIC_ONLY - Must be representable as a float, or is error
    NUMERIC_ONLY = False

    # COMPARISON_OPERATOR_STR - This should be set to the operator associated with the comparison (e.x. "!=" or "<")
    COMPARISON_OPERATOR_STR = 'UNKNOWN'


    def doComparison(self, leftSide, rightSide):
        '''
            doComparison - Do the comparison associated with the subclass of BodyElementComparison

              and return the result.


                @param leftSide <BodyElementValue/str/float/BodyElementValue> - Left side of comparison operator

                @param rightSideValue <BodyElementValue/str/float/other?> - Right side of comparison operator


                @return <bool> - The result of the comparison operation
        '''

        (leftSideValue, rightSideValue) = BodyElementComparison._resolveTypesForComparison(leftSide, rightSide)

        return self._doComparison(leftSideValue, rightSideValue)


    def _doComparison(self, leftSideValue, rightSideValue):
        '''
            _doComparison - TYPE INTERNAL. Do the comparison associated with the subclass of BodyElementComparison

              and return the result.

              This should be implemented by each comparison type, rather than doComparison directly (which prepares arguments)


                @param leftSideValue <str/float/other?> - Left side of comparison operator's value

                @param rightSideValue <str/float/other?> - Right side of comparison operator's value


                @return <bool> - The result of the comparison operation
        '''
        raise NotImplementedError('BodyElementComparison._doComparison must be implemented by extending subclass, but %s does not implement!' % ( \
                self.__class__.__name__,
            )
        )


    @classmethod
    def _resolveTypesForComparison(cls, leftSide, rightSide):
        '''
            _resolveTypesForComparison - Resolve the given leftSide and rightSide dynamic types for comparison


                @param leftSide <BodyElementValue/...> - A value, either wrapped in a BodyElementValue or direct.

                    Represents the left side of the operator

                @param rightSide <BodyElementValue/...> - A value, either wrapped in a BodyElementValue or direct.

                    Represents the right side of the operator


                @return tuple(left, right) of either <float, float> if castable, or the original raw pythonic types instead (pulled out of BodyElementValue if provided in one)


                @notes - If cls.NUMERIC_ONLY is True, will throw an exception if cannot cast both sides to float. See raises section, below.

                @raises XPathRuntimeError - If NUMERIC_ONLY is True, and cannot cast both sides to a float.

        '''
        if issubclass(leftSide.__class__, BodyElementValue):
            leftSideValue = leftSide.getValue()
        else:
            leftSideValue = leftSide

        if issubclass(rightSide.__class__, BodyElementValue):
            rightSideValue = rightSide.getValue()
        else:
            rightSideValue = rightSide

        try:
            return ( float(leftSideValue), float(rightSideValue) )
        except:
            if cls.NUMERIC_ONLY is False:
                return ( leftSideValue, rightSideValue )
            else:
                # TODO: Say explicitly which side won't convert?
                raise XPathRuntimeError('XPath Runtime Error: Numeric-only comparison attempted with non-numeric values! Comparison "%s" only supports both sides being numeric, and cannot convert. Left side is <%s> ( %s ) and Right side is <%s> ( %s )' % ( \
                        cls.COMPARISON_OPERATOR_STR,
                        type(leftSideValue).__name__, repr(leftSideValue),
                        type(rightSideValue).__name__, repr(rightSideValue),
                    )
                )




class BodyElementComparison_Equal(BodyElementComparison):

    COMPARISON_OPERATOR_STR = "="

    def _doComparison(self, leftSideValue, rightSideValue):
        return BodyElementValue_Boolean( leftSideValue == rightSideValue )


BEC_EQUAL_RE = re.compile(r'^([ \t]*[=][ \t]*)')
COMPARISON_RES.append( (BEC_EQUAL_RE, BodyElementComparison_Equal) )


class BodyElementComparison_NotEqual(BodyElementComparison):

    COMPARISON_OPERATOR_STR = "!="

    def _doComparison(self, leftSideValue, rightSideValue):
        return BodyElementValue_Boolean( leftSideValue != rightSideValue )


BEC_NOT_EQUAL_RE = re.compile(r'^([ \t]*[!][=][ \t]*)')
COMPARISON_RES.append( (BEC_NOT_EQUAL_RE, BodyElementComparison_NotEqual) )

# TODO: Other types of comparison (greater than, less than or equal, etc.)

class BodyElementComparison_LessThan(BodyElementComparison):

    NUMERIC_ONLY = True

    COMPARISON_OPERATOR_STR = '<'

    def _doComparison(self, leftSideValue, rightSideValue):
        return BodyElementValue_Boolean( leftSideValue < rightSideValue )


BEC_LESS_THAN_RE = re.compile(r'^([ \t]*[<][ \t]*)')
COMPARISON_RES.append( (BEC_LESS_THAN_RE, BodyElementComparison_LessThan) )


class BodyElementComparison_LessThanOrEqual(BodyElementComparison):

    NUMERIC_ONLY = True

    COMPARISON_OPERATOR_STR = '<='

    def _doComparison(self, leftSideValue, rightSideValue):
        return BodyElementValue_Boolean( leftSideValue <= rightSideValue )


BEC_LESS_THAN_OR_EQUAL_RE = re.compile(r'^([ \t]*[<][=][ \t]*)')
COMPARISON_RES.append( (BEC_LESS_THAN_OR_EQUAL_RE, BodyElementComparison_LessThanOrEqual) )


class BodyElementComparison_GreaterThan(BodyElementComparison):

    NUMERIC_ONLY = True

    COMPARISON_OPERATOR_STR = '>'

    def _doComparison(self, leftSideValue, rightSideValue):
        return BodyElementValue_Boolean( leftSideValue > rightSideValue )


BEC_GREATER_THAN_RE = re.compile(r'^([ \t]*[>][ \t]*)')
COMPARISON_RES.append( (BEC_GREATER_THAN_RE, BodyElementComparison_GreaterThan) )


class BodyElementComparison_GreaterThanOrEqual(BodyElementComparison):

    NUMERIC_ONLY = True

    COMPARISON_OPERATOR_STR = '>='

    def _doComparison(self, leftSideValue, rightSideValue):
        return BodyElementValue_Boolean( leftSideValue <= rightSideValue )


BEC_GREATER_THAN_OR_EQUAL_RE = re.compile(r'^([ \t]*[>][=][ \t]*)')
COMPARISON_RES.append( (BEC_GREATER_THAN_OR_EQUAL_RE, BodyElementComparison_GreaterThanOrEqual) )


#############################
##       Boolean Ops       ##
#############################


# BOOLEAN_OPS_RES - A list of tuples, which will be iterated upon parsing a body to create the BooleanOps types
#                        Tuples are in format: ( re.compile'd expression, BodyElementBooleanOps child class implementing related )
#
#                           Where all of the named groups within the compiled regular expression are passed to __init__ of the related class.
BOOLEAN_OPS_RES = []


class BodyElementBooleanOps(BodyElement):
    '''
        BodyElementBooleanOps - Base comparison class for boolean comparison operations (e.x. "and" , "or" )
    '''

    # BOOLEAN_OP_STR - The boolean operation being implemented, should be set by the subclass.
    BOOLEAN_OP_STR = 'unknown'


    def doBooleanOp(self, leftSide, rightSide):
        '''
            doBooleanOp - Do the comparison associated with the subclass of BodyElementBooleanOps

              and return the result.


                @param leftSide <BodyElementValue/str/float/BodyElementValue> - Left side of comparison operator

                @param rightSideValue <BodyElementValue/str/float/other?> - Right side of comparison operator


                @return <bool> - The result of the comparison operation
        '''
        (leftSideValue, rightSideValue) = BodyElementBooleanOps._resolveTypesForBooleanOp(leftSide, rightSide)

        return self._doBooleanOp(leftSideValue, rightSideValue)


    def _doBooleanOp(self, leftSideValue, rightSideValue):
        '''
            _doBooleanOp - TYPE INTERNAL. Do the comparison associated with the subclass of BodyElementBooleanOp

              and return the result.

              This should be implemented by each comparison type, rather than doBooleanOp directly (which prepares arguments)


                @param leftSideValue <str/float/other?> - Left side of comparison operator's value

                @param rightSideValue <str/float/other?> - Right side of comparison operator's value


                @return <bool> - The result of the comparison operation
        '''
        raise NotImplementedError('BodyElementBooleanOps._doBooleanOp must be implemented by extending subclass, but %s does not implement!' % ( \
                self.__class__.__name__,
            )
        )


    @classmethod
    def _resolveTypesForBooleanOp(cls, leftSide, rightSide):
        '''
            _resolveTypesForBooleanOp - Resolve the given leftSide and rightSide dynamic types for comparison

                Boolean type overrides the comparison base in order to only accept booleans (instead of numeric / strings)


                @param leftSide <BodyElementValue/...> - A value, either wrapped in a BodyElementValue or direct.

                    Represents the left side of the operator.

                    Must be or resolve to a boolean

                @param rightSide <BodyElementValue/...> - A value, either wrapped in a BodyElementValue or direct.

                    Represents the right side of the operator

                    Must be or resolve to a boolean


                @return tuple(left<bool>, right<bool>)


                @raises XPathRuntimeError - If either side is not a boolean, or a boolean-wrapped BodyElementValue

        '''
        # Since we are dealining specifically with booleans only here,
        if issubclass(leftSide.__class__, BodyElementValue):
            leftSideValue = leftSide.getValue()
        else:
            leftSideValue = leftSide

        if issubclass(rightSide.__class__, BodyElementValue):
            rightSideValue = rightSide.getValue()
        else:
            rightSideValue = rightSide


        # TODO: Provide better context here of where this operation was in the xpath string?
        if not isinstance(leftSideValue, bool):
            # Should this be a parse error? Their expression caused it....
            raise XPathRuntimeError('XPath Runtime Error: Boolean comparison attempted ( "%s" operator ) but left side was not a boolean! Was: %s . Repr: %s' % ( \
                    cls.BOOLEAN_OP_STR,
                    type(leftSideValue).__name__,
                    repr(leftSideValue),
                )
            )
        if not isinstance(rightSideValue, bool):
            raise XPathRuntimeError('XPath Runtime Error: Boolean comparison attempted ( "%s" operator ) but right side was not a boolean! Was: %s . Repr: %s' % ( \
                    cls.BOOLEAN_OP_STR,
                    type(rightSideValue).__name__,
                    repr(rightSideValue),
                )
            )

        return ( leftSideValue, rightSideValue )


class BodyElementBooleanOps_And(BodyElementBooleanOps):

    BOOLEAN_OP_STR = 'and'

    def _doBooleanOp(self, leftSideValue, rightSideValue):
        return BodyElementValue_Boolean( leftSideValue and rightSideValue )

# NOTE: these requires a whitespace after, unlike other operators.
BEBO_AND_RE = re.compile(r'^([ \t]*[aA][nN][dD][ \t]+)')
BOOLEAN_OPS_RES.append( (BEBO_AND_RE, BodyElementBooleanOps_And) )


class BodyElementBooleanOps_Or(BodyElementBooleanOps):

    BOOLEAN_OP_STR = 'or'

    def _doBooleanOp(self, leftSideValue, rightSideValue):
        return BodyElementValue_Boolean( leftSideValue or rightSideValue )


BEBO_OR_RE = re.compile(r'^([ \t]*[oO][rR][ \t]+)')
BOOLEAN_OPS_RES.append( (BEBO_OR_RE, BodyElementBooleanOps_Or) )


#############################
##      Static Values      ##
#############################


# STATIC_VALUES_RES - A list of tuples, which will be iterated upon parsing a body to create the BodyElementValue_StaticValue types
#                        Tuples are in format: ( re.compile'd expression, BodyElementValue_StaticValue child class implementing related )
#
#                           Where all of the named groups within the compiled regular expression are passed to __init__ of the related class.
STATIC_VALUES_RES = []


class BodyElementValue_StaticValue(BodyElementValue):
    '''
        BodyElementValue_StaticValue - Base class of static values ( appear in the body string directly, e.x. "hello" or 12 )
    '''
    pass


class BodyElementValue_StaticValue_String(BodyElementValue_StaticValue):
    '''
        BodyElementValue_StaticValue_String - StaticValue represents a string
    '''

    VALUE_TYPE = BODY_VALUE_TYPE_STRING


## String will have two expressions to generate -- one for single quotes, one for double quotes. Both extract the inner string
#    Can combine into one, but this is more clear.

# Double quoted string
#BEV_SV_STRING_DOUBLE_QUOTE_RE = re.compile(r'''^([ \t]*[\"](?P<value>[^"]*)[\"][ \t]*)''')
BEV_SV_STRING_DOUBLE_QUOTE_RE = re.compile(r'''^([ \t]*[\"](?P<value>([\\]["]|[^"])*)[\"][ \t]*)''')
STATIC_VALUES_RES.append( (BEV_SV_STRING_DOUBLE_QUOTE_RE, BodyElementValue_StaticValue_String) )

# Single quoted string
#BEV_SV_STRING_SINGLE_QUOTE_RE = re.compile(r"""^([ \t]*[\'](?P<value>[^']*)[\'][ \t]*)""")
BEV_SV_STRING_SINGLE_QUOTE_RE = re.compile(r"""^([ \t]*[\'](?P<value>([\\][']|[^'])*)[\'][ \t]*)""")
STATIC_VALUES_RES.append( (BEV_SV_STRING_SINGLE_QUOTE_RE, BodyElementValue_StaticValue_String) )


class BodyElementValue_StaticValue_Number(BodyElementValue_StaticValue):
    '''
        BodyElementValue_StaticValue_Number - StaticValue to represent a number
    '''

    VALUE_TYPE = BODY_VALUE_TYPE_NUMBER


    def setValue(self, newValue):
        '''
            setValue - Sets the inner value to a float, or raises exception on failure to convert.


                @param newValue <str/float> - A number (positive or negative, integer or float)


                @raises XPathRuntimeError - Type passed is not convertable to float


                @see BodyElementValue_StaticValue.setValue
        '''
        try:
            self.value = float(newValue)
        except Exception as fe:
            raise XPathRuntimeError('Runtime Type Error: BodyElementValue_StaticValue_Number was passed a value, <%s> %s  -- but could not convert to float. %s  %s' %( \
                    type(newValue).__name__,
                    repr(newValue),
                    fe.__class__.__name__,
                    str(fe),
                )
            )


# NOTE: Look into spaces after negative sign
BEV_SV_NUMBER_RE = re.compile(r'''^([ \t]*(?P<value>([-]){0,1}([\d]*[\.][\d]+)|([\d]+))[ \t]*)''')
STATIC_VALUES_RES.append( (BEV_SV_NUMBER_RE, BodyElementValue_StaticValue_Number) )

ALL_BODY_ELEMENT_RES = VALUE_GENERATOR_RES + COMPARISON_RES + OPERATION_RES + BOOLEAN_OPS_RES + STATIC_VALUES_RES


def parseBodyStringIntoBodyElements(bodyString):
    '''
        parseBodyStringIntoBodyElements - Parses the body string of a tag filter expression (between square brackets)

            into individual body elements.


                @param bodyString <str> - A body string of an XPath expression


                @return list<BodyElement> - A list of matched BodyElement items, in order of appearance.


                @raises XPathParseError - Failure to parse
    '''

    allBodyElementREs = ALL_BODY_ELEMENT_RES

    curString = bodyString[:].strip()
    ret = []

    while curString:

        gotMatch = False

        for ( bodyPartRE, bodyPartClass ) in allBodyElementREs:

            matchObj = bodyPartRE.match(curString)
            if matchObj is None:
                continue

            gotMatch = True
            break

        if gotMatch is False:

            raise XPathParseError('Failed to parse body string into usable part, at: "%s"' %(curString, ))

        groupDict = matchObj.groupdict()

        thisPart = bodyPartClass( **groupDict )
        ret.append(thisPart)

        curString = curString[ matchObj.span()[1] : ].lstrip()

    return ret


# vim: set ts=4 sw=4 st=4 expandtab :
