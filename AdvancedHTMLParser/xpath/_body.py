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
from ..compat import STRING_TYPES
from ..utils import tostr

from .exceptions import XPathNotImplementedError, XPathRuntimeError, XPathParseError
from ._filters import _mk_xpath_op_filter_tag_is_nth_child_index
from .null import Null


# __all__ is currently set to what "parsing" imports
__all__ = ('parseBodyStringIntoBodyElements', 'BodyElement', 'BodyElementOperation', 'BodyElementValue', 'BodyElementValueGenerator', 'BodyLevel_Top')


class BodyElement(object):
    '''
        BodyElement - Base class of body elements.

          Every distinct "unit" within a body, be it a static value or a function call, or otherwise,
           are subclassed from this type.
    '''

    @classmethod
    def createFromMatch(cls, curBodyStr, matchObj):
        '''
            createFromMatch - Create this BodyElement from a given match object, and return the element and remainder for parsing

                @param curBodyStr <str> - The current body string (matchObj should have matched at the head of this)

                @param matchObj <re.match> - The match object

                @return tuple( createdElement<BodyElement>, remainingBodyStr<str> ) - A tuple of the created element and the remaining portion to parse
        '''
        groupDict = matchObj.groupdict()

        thisElement = cls( **groupDict )

        curBodyStr = curBodyStr[ matchObj.span()[1] : ]

        return ( thisElement, curBodyStr )


# XXX: This is a container for BodyElements, but itself can be treated as a BodyElement.
#         Should give same parent class, or keep separate?
class BodyLevel(BodyElement):
    '''
        BodyLevel - A single "level" of a body
    '''

    VALIDATE_ONLY_BOOLEAN_OR_STR = False

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


    def evaluateLevelForTag(self, currentTag):
        '''
            evaluateLevelForTag - Shorthand version of "evaluateLevelForTags" but for one tag



                @param currentTag <AdvancedTag> - A single tag


                @return <BodyElementValue> - Resulting value for running this level against given tag


                @see evaluateLevelForTags
        '''
        # TODO: Clean up this function
        return self.evaluateLevelForTags( [currentTag] )[0]


    def evaluateLevelForTags(self, currentTags):
        '''
            evaluate - Evaluate this level, and return the final value, for each tag.


                @param currentTags list/TagCollection < AdvancedTag > - The current set of tags to process


                @return list< BodyElementValue > - The BodyElementValue of the results, in a list 1:1 same order same size as #currentTags

        '''
        # thisLevelElements - local reference to our elements
        thisLevelElements = self.bodyElements

        # resultPerTag - This list contains the values to be returned for each tag, in same order as #currentTags
        resultPerTag = []

        if len(thisLevelElements) == 0:
            # This is an empty [], so just return the same
            return resultPerTag


        # TODO: Optimize this function, further


        ## These next two arrays provide the common and ordered interface to iterate through all various types which
        #    need evaluation.
        #  They are tuples,  ( Class, Lambda to Evaluate ). All lambdas within the same set follow same signature

        # ORDERED_BE_TYPES_TO_PROCESS_TAGS - The ordered types to process which generate values from the tag itself
        ORDERED_BE_TYPES_TO_PROCESS_TAGS = [
            (BodyLevel, lambda _bl, _curTag : _bl.evaluateLevelForTag(_curTag) ),
            (BodyElementValueGenerator, lambda _bevg, _curTag : _bevg.resolveValueFromTag(_curTag) ),
        ]

        # ORDERED_BE_TYPES_TO_PROCESS_VALUES - The ordered types to process which generate values from left side and right side
        ORDERED_BE_TYPES_TO_PROCESS_VALUES = [

            (BodyElementOperation, lambda _beo, _leftSide, _rightSide : _beo.performOperation(_leftSide, _rightSide) ),
            (BodyElementComparison, lambda _bec, _leftSide, _rightSide : _bec.doComparison(_leftSide, _rightSide) ),
            (BodyElementBooleanOps, lambda _bebo, _leftSide, _rightSide : _bebo.doBooleanOp(_leftSide, _rightSide) ),
        ]


        # Iterate over all tags
        for thisTag in currentTags:

            # curElements - The current set of elements for this tag, as we unroll, this will change.
            #                 Initial value will be reference to the original set of elements
            curElements = thisLevelElements

            # Run through the tag-processing (value generators, sublevels) ones first
            for typeToProcess, processFunction in ORDERED_BE_TYPES_TO_PROCESS_TAGS:


                curElements = [ (issubclass( curElement.__class__, typeToProcess ) and processFunction( curElement, thisTag )) or curElement for curElement in curElements ]

#                # nextElements - We will assemble into this list the next iteration of #curElements
#                nextElements = []
#
#                for curElement in curElements:
#
#                    curElementClass = curElement.__class__
#
#                    if not issubclass(curElementClass, typeToProcess):
#                        # Not processing this type, just put back on the list
#                        nextElements.append( curElement )
#
#                    else:
#                        # Processing type, get new value
#                        generatedValue = processFunction( curElement, thisTag )
#                        nextElements.append( generatedValue )
#
#                # Update #curElements
#                curElements = nextElements


            # Great, now we have to start keeping track of left/right and process the rest
            for typeToProcess, processFunction in ORDERED_BE_TYPES_TO_PROCESS_VALUES:

                # nextElements - We will assemble into this list the next iteration of #curElements
                nextElements = []

                # leftSide - this will be the left side value
                leftSide = None

                numElements = len(curElements)
                i = 0

                while i < numElements:

                    curElement = curElements[i]
                    curElementClass = curElement.__class__

                    if not issubclass(curElementClass, typeToProcess ):
                        # We aren't processing this type, just add it back

                        nextElements.append( curElement )

                        # Update previous value and increment counter
                        leftSide = curElement
                        i += 1

                        # Loop back
                        continue

                    else:
                        # Validate that we are not at the end (need to gather a right)
                        if (i + 1) >= numElements:
                            # TODO: Better error message?
                            raise XPathParseError('XPath expression ends in an operation, no right-side to operation.')

                        # Validate left is right type
                        if not issubclass(leftSide.__class__, BodyElementValue):
                            # TODO: Better error message?
                            raise XPathParseError('XPath expression contains two consecutive operations (left side)')

                        # Grab and validate right is right type
                        rightSide = curElements[i + 1]
                        if not issubclass(rightSide.__class__, BodyElementValue):
                            # TODO: Better error message?
                            raise XPathParseError('XPath expression contains two consecutive operations (right side)')

                        # Resolve a new value feeding left, right into the function
                        resolvedValue = processFunction( curElement, leftSide, rightSide)

                        # TODO: Remove this check?
                        if not issubclass(resolvedValue.__class__, BodyElementValue):
                            # Not a value? Error for now, may add back looping later if necessary for some ops
                            raise XPathRuntimeError('XPath expression for op  "%s"  did not return a BodyElementValue, as expected. Got: <%s> %s' % ( \
                                    repr(curElement),
                                    resolvedValue.__class__.__name__,
                                    repr(resolvedValue),
                                )
                            )

                        # Pop the last value (left side), drop the operation, load the resolved value in place.
                        nextElements = nextElements[ : -1 ] + [resolvedValue]

                        # Update new left to this generated value

                        leftSide = resolvedValue
                        # Move past right side
                        i += 2

                # Update #curElements
                curElements = nextElements

            # END: for typeToProcess, processFunction in ORDERED_BE_TYPES_TO_PROCESS_VALUES:


            # At this point, should be only one value left. Zero was already handled at start
            numElementsRemaining = len(curElements)
            if numElementsRemaining != 1:
                raise XPathRuntimeError('Got unexpected current number of elements at the end. Expected 1, got %d.  Repr: %s' % ( \
                        numElementsRemaining,
                        repr(curElements),
                    )
                )


            finalElement = curElements[0]
            finalElementClass = finalElement.__class__
            # TODO: Remove this check?
            try:
                finalElementValueType = finalElement.VALUE_TYPE
            except AttributeError:
                # Missing this class attribute implicitly also checks the type,
                #   as no other types provide such a name.

                # TODO: Do a better repr, maybe with string of the xpath?
                raise XPathRuntimeError('Final Value resolved from level """%s""" was not a BodyElementValue, as was expected.\nIt is a: %s \nrepr: %s' % ( \
                        repr(self),
                        finalElementClass.__name__,
                        repr(finalElement),
                    )
                )

            if self.VALIDATE_ONLY_BOOLEAN_OR_STR and finalElementValueType not in (BODY_VALUE_TYPE_BOOLEAN, BODY_VALUE_TYPE_NUMBER):
                raise XPathRuntimeError('Final value resolved from level """%s""" was not an integer or a boolean, cannot proceed.\nVALUE_TYPE is %s.\nClass: %s\nRepr: %s' % ( \
                        repr(self),
                        _bodyValueTypeToDebugStr(finalElementValueType),
                        finalElementClass.__name__,
                        repr(finalElement),
                    )
                )

            # Validated and processed this tag on this level, append to the result array
            resultPerTag.append(finalElement)

            # END for thisTag in currentTags

        return resultPerTag


# TODO: Need to refactor this a bit maybe, to support levels as designed
class BodyLevel_Top(BodyLevel):
    '''
        BodyLevel_Top - The topmost level of a body. This is the final evaluation before passing onto the next tag filter
    '''

    VALIDATE_ONLY_BOOLEAN_OR_STR = True

    def filterTagsByBody(self, currentTags):
        '''
            evaluate - Evaluate the topmost level (and all sub levels), and return tags that match.

                For the topmost level, we run all components left-to-right, and evaluate the result.

                If an integer remains, we use that 1-origin Nth child of parent.
                If a boolean remains, we use True to retain, False to discard.


                    @param currentTags TagCollection/list<AdvancedTag> - Current set of tags to validate


                    @return TagCollection - The tags which passed validation
        '''

        retTags = []

        if not currentTags:
            return retTags

        # Process this level and all subs, get the final value per tag for processing
        #   validation to retain or discard
        finalResultPerTag = self.evaluateLevelForTags(currentTags)

        numTags = len(currentTags)

        for i in range(numTags):

            currentTag = currentTags[i]
            finalValue = finalResultPerTag[i]
            #finalValueClass = finalValue.__class__

            # TODO: We should be able to optimize this loop as all results will have either
            #         a number, or a boolean
            if finalValue.VALUE_TYPE == BODY_VALUE_TYPE_BOOLEAN:

                shouldRetainTag = finalValue.getValue()

                if shouldRetainTag is True:
                    retTags.append( currentTag )

            #elif finalValue.VALUE_TYPE == BODY_VALUE_TYPE_NUMBER:
            else:
                # This should have already been validated

                theValue = finalValue.getValue()
                innerNum = int( theValue )

                if float(innerNum) != theValue:
                    # Float value, not integer, return nothing.
                    continue

                # TODO: Better.
                testFunc = _mk_xpath_op_filter_tag_is_nth_child_index(currentTag.tagName, innerNum)

                retTags += testFunc( currentTag )

            #else:
            #    raise XPathRuntimeError('Error, unexpected value type %s  on value:  %s' %( _bodyValueTypeToDebugStr(finalValue.VALUE_TYPE), repr(finalValue) ) )


        return TagCollection(retTags)

    # applyFunction - follow this interface, for now.
    applyFunction = filterTagsByBody



#############################
##          Values         ##
#############################

## Values are calculated (returned from a BodyElementValueGenerator or otherwise),
#    or static (provided explicitly in body string).
#   These are given separate bases, and are all subclasses of BodyElement.

# Values are associated with a type (cls.VALUE_TYPE), defined as one of the types below.

# Values are wrapped within the associated BodyElementValue subclasses rather than as native python types

#####                    #####
### BodyElementValue types ###
#####                    #####

# NOTE: Use enum type? Requires additional package under python2

# An enumeration of the possible types a BodyElementValue subclass may hold
BODY_VALUE_TYPE_UNKNOWN = 0
BODY_VALUE_TYPE_NUMBER = 1
# Leave a gap for 2 should we split float/int
BODY_VALUE_TYPE_STRING = 3
BODY_VALUE_TYPE_BOOLEAN = 4
# List - Unimplemented
BODY_VALUE_TYPE_LIST = 5
BODY_VALUE_TYPE_NULL = 6

# BODY_VALUE_TYPE_TO_STR - The value type integer to a string representation.
BODY_VALUE_TYPE_TO_STR = {
    BODY_VALUE_TYPE_UNKNOWN : "unknown",
    BODY_VALUE_TYPE_NUMBER  : "number",
    BODY_VALUE_TYPE_STRING  : "string",
    BODY_VALUE_TYPE_BOOLEAN : "boolean",
    BODY_VALUE_TYPE_LIST    : "list",
    BODY_VALUE_TYPE_NULL    : "null",
}

def _bodyValueTypeToDebugStr(bodyValue):
    return "<%d>%s" %(bodyValue, BODY_VALUE_TYPE_TO_STR[bodyValue])


class BodyElementValue(BodyElement):
    '''
        BodyElementValue - Base class of BodyElements which represent a static or resolved value.

          These wrap the native python representation of the values.

          A class-level varible, VALUE_TYPE, defines the type associated with the value.
    '''

    # VALUE_TYPE - The type of this value. Should be set by subclass
    VALUE_TYPE = BODY_VALUE_TYPE_UNKNOWN

    def __init__(self, value):
        '''
            __init__ - Create this element as a wrapper around an already-calculated value


                @param value <...> - The python-native value to be held by this element.

                    This will be passed into self.setValue for processing/validation
        '''
        self.value = None
        self.setValue(value)


    def getValue(self):
        '''
            getvalue - Get the value associated with this object


                @return <...> - The python-native value wrapped by this object
        '''
        return self.value


    def setValue(self, newValue):
        '''
            setValue - Sets the value associated with this object

              This will be called on all value sets, including __init__ (and from regex)


                @param newValue <???> - The new value for this object
        '''
        self.value = newValue


    def __repr__(self):
        '''
            __repr__ - Get a string representation of this value, with code information
        '''
        className = self.__class__.__name__
        valueType = self.VALUE_TYPE
        valueTypeStr = BODY_VALUE_TYPE_TO_STR[ valueType ]
        valueRepr = repr( self.getValue() )
        return "%s<VALUE_TYPE=%d[%s]>(value=%s)" %( className, valueType, valueTypeStr, valueRepr )


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
        self.value = tostr(newValue)


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
        BodyElementValue_StaticValue_String - A StaticValue which represents a string
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
                valPart = tostr( fnArg.getValue() )

            elif issubclass(fnArgClass, STRING_TYPES):
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


class BodyElementOperation_Concat(BodyElementOperation):
    '''
        BodyElementOperation_Concat - Operation to handle the concat operator, "||"
    '''

    def performOperation(self, leftSide, rightSide):
        '''
            performOperation - Concatenate two strings


                @param leftSide <str/BodyElementValue_String> - The left side string (will be the prefix)

                @param rightSide <str/BodyElementValue_String> - The right side string (will be the suffix)


                @return <BodyElementValue_String> - The concatenated string of leftSide + rightSide

        '''
        if issubclass(leftSide.__class__, BodyElementValue):
            leftSideValue = leftSide.getValue()

        else:
            leftSideValue = leftSide

        if issubclass(rightSide.__class__, BodyElementValue):
            rightSideValue = rightSide.getValue()

        else:
            rightSideValue = rightSide

        if not issubclass(leftSideValue.__class__, STRING_TYPES):
            raise XPathRuntimeError('Concat operator tried to concatenate, but left side is not a string type! It is a %s . repr: %s' % ( \
                    type(leftSideValue).__name__,
                    repr(leftSideValue),
                )
            )
        if not issubclass(rightSideValue.__class__, STRING_TYPES):
            raise XPathRuntimeError('Concat operator tried to concatenate, but right side is not a string type! It is a %s . repr: %s' % ( \
                type(rightSideValue).__name__,
                repr(rightSideValue),
            )
        )
        #print ( "Left: %s\nRight: %s\n" %(repr(leftSideValue), repr(rightSideValue)) )

        val = leftSideValue + rightSideValue

        return BodyElementValue_String(val)


BEO_CONCAT_RE = re.compile(r'''^([ \t]*[\|][\|][ \t]*)''')
OPERATION_RES.append( (BEO_CONCAT_RE, BodyElementOperation_Concat) )


class BodyElementOperation_Math(BodyElementOperation):
    '''
        BodyElementOperation_Math - Base class for math operators
    '''

    # MATH_OPERATOR_STR - Override with the math operator (e.x. "+")
    MATH_OPERATOR_STR = 'unknown'


    def _prepareValuesForOperation(self, leftSide, rightSide):
        '''
            _prepareValuesForOperation - Prepare values for a numeric operation


                @param leftSide <str/BodyElementValue/int/float> - The left side of the operation

                @param rightSide <str/BodyElementValue/int/float> - The right side of the operation


                @return tuple( leftSideValue<float>, rightSideValue<float> )
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

            raise XPathRuntimeError('Math operation "%s" attempted, but could not convert body sides to numbers!\nLeft side: <%s>  %s\nRight side: <%s>  %s' % ( \
                    self.MATH_OPERATOR_STR,
                    type(leftSideValue).__name__,
                    repr(leftSideValue),
                    type(rightSideValue).__name__,
                    repr(rightSideValue),
                )
            )


    def performOperation(self, leftSide, rightSide):
        '''
            performOperation - Perform a math operation (see type for details)


                @param leftSide <...> - The left side (must be convertable to float)

                @param rightSide <...> - The right side (must be convertable to float)


                @return <BodyElementValue_Number> - The calculated value

        '''

        (leftSideValue, rightSideValue) = self._prepareValuesForOperation(leftSide, rightSide)

        return self.doCalculation(leftSideValue, rightSideValue)



    def doCalculation(self, leftSideValue, rightSideValue):
        '''
            doCalculation - Perform the math operation implemented by this subclas.

              Subclass must override this method.


                @param leftSideValue <float> - Left side value

                @param rightSideValue <float> - Right side value


                @return <BodyElementValue_Number> - The result of the operation
        '''
        raise NotImplementedError('BodyElementOperation_Math class "%s" must implement doCalculation function!' %( self.__class__.__name__, ))


class BodyElementOperation_Math_Plus(BodyElementOperation_Math):
    '''
        BodyElementOperation_Math_Plus - BodyElementOperation that implements the Math operation "plus" / "addition" / "+"
    '''

    MATH_OPERATOR_STR = '+'

    def doCalculation(self, leftSideValue, rightSideValue):
        '''
            doCalculation - Add two values, return the result.


                @param leftSideValue <float> - Left side value

                @param rightSideValue <float> - Right side value


                @return <BodyElementValue_Number> - The result of the operation
        '''
        result = leftSideValue + rightSideValue

        return BodyElementValue_Number(result)


BEO_MATH_PLUS_RE = re.compile(r'''^([ \t]*[+][ \t]*)''')
OPERATION_RES.append( (BEO_MATH_PLUS_RE, BodyElementOperation_Math_Plus) )


class BodyElementOperation_Math_Minus(BodyElementOperation_Math):
    '''
        BodyElementOperation_Math_Minus - BodyElementOperation that implements the Math operation "minus" / "subtraction" / "-"
    '''

    MATH_OPERATOR_STR = '-'

    def doCalculation(self, leftSideValue, rightSideValue):
        '''
            doCalculation - Subtract two values, return the result.


                @param leftSideValue <float> - Left side value

                @param rightSideValue <float> - Right side value


                @return <BodyElementValue_Number> - The result of the operation
        '''
        result = leftSideValue - rightSideValue

        return BodyElementValue_Number(result)


BEO_MATH_MINUS_RE = re.compile(r'''^([ \t]*[-][ \t]*)''')
OPERATION_RES.append( (BEO_MATH_MINUS_RE, BodyElementOperation_Math_Minus) )


class BodyElementOperation_Math_Multiply(BodyElementOperation_Math):
    '''
        BodyElementOperation_Math_Multiply - BodyElementOperation that implements the Math operation "multiply" / "multiplication" / "*"
    '''

    MATH_OPERATOR_STR = '*'

    def doCalculation(self, leftSideValue, rightSideValue):
        '''
            doCalculation - Multiply two values, return the result.


                @param leftSideValue <float> - Left side value

                @param rightSideValue <float> - Right side value


                @return <BodyElementValue_Number> - The result of the operation
        '''
        result = leftSideValue * rightSideValue

        return BodyElementValue_Number(result)


BEO_MATH_MULTIPLY_RE = re.compile(r'''^([ \t]*[\*][ \t]*)''')
OPERATION_RES.append( (BEO_MATH_MULTIPLY_RE, BodyElementOperation_Math_Multiply) )


class BodyElementOperation_Math_Divide(BodyElementOperation_Math):
    '''
        BodyElementOperation_Math_Divide - BodyElementOperation that implements the Math operation "divide" / "division" / "div"
    '''

    MATH_OPERATOR_STR = 'div'

    def doCalculation(self, leftSideValue, rightSideValue):
        '''
            doCalculation - Divide two values, return the result.


                @param leftSideValue <float> - Left side value

                @param rightSideValue <float> - Right side value


                @return <BodyElementValue_Number> - The result of the operation
        '''
        result = leftSideValue / rightSideValue

        return BodyElementValue_Number(result)


BEO_MATH_DIVIDE_RE = re.compile(r'''^([ \t]*[dD][iI][vV][ \t]*)''')
OPERATION_RES.append( (BEO_MATH_DIVIDE_RE, BodyElementOperation_Math_Divide) )


class BodyElementOperation_Math_Modulus(BodyElementOperation_Math):
    '''
        BodyElementOperation_Math_Modulus - BodyElementOperation that implements the Math operation "modulus" / "%" / "mod"
    '''

    MATH_OPERATOR_STR = 'mod'

    def doCalculation(self, leftSideValue, rightSideValue):
        '''
            doCalculation - Divide two values, return the remainder.


                @param leftSideValue <float> - Left side value

                @param rightSideValue <float> - Right side value


                @return <BodyElementValue_Number> - The result of the operation
        '''
        result = leftSideValue % rightSideValue

        return BodyElementValue_Number(result)


BEO_MATH_MODULUS_RE = re.compile(r'''^([ \t]*[mM][oO][dD][ \t]*)''')
OPERATION_RES.append( (BEO_MATH_MODULUS_RE, BodyElementOperation_Math_Modulus) )


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

    # NUMERIC_ONLY - If True, the value must be represenatble as a float (Number), or error.
    #                If False, other values (e.x. string) are supported.
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


                @param leftSideValue <str/float/other?> - Left side of comparison operator's value (unrolled from its BodyElementValue wrapper)

                @param rightSideValue <str/float/other?> - Right side of comparison operator's value (unrolled from its BodyElementValue wrapper)


                @return <BodyElementValue_Boolean> - The result of the comparison operation
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

        # Try to represent both sides as floats (Number), if possible
        try:
            return ( float(leftSideValue), float(rightSideValue) )
        except:
            # If we failed to convert both sides to number (e.x. strings), then check if this is a NUMERIC_ONLY type,
            #    in which case we will throw an error.
            #  Otherwise, return the raw python types

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
    '''
        BodyElementComparison_Equal - A BodyElementComparison which represents the "equals" operation, "="
    '''

    COMPARISON_OPERATOR_STR = "="

    def _doComparison(self, leftSideValue, rightSideValue):
        return BodyElementValue_Boolean( leftSideValue == rightSideValue )


BEC_EQUAL_RE = re.compile(r'^([ \t]*[=][ \t]*)')
COMPARISON_RES.append( (BEC_EQUAL_RE, BodyElementComparison_Equal) )


class BodyElementComparison_NotEqual(BodyElementComparison):
    '''
        BodyElementComparison_NotEqual - A BodyElementComparison which represents the "not equals" operation, "!="
    '''

    COMPARISON_OPERATOR_STR = "!="

    def _doComparison(self, leftSideValue, rightSideValue):
        return BodyElementValue_Boolean( leftSideValue != rightSideValue )


BEC_NOT_EQUAL_RE = re.compile(r'^([ \t]*[!][=][ \t]*)')
COMPARISON_RES.append( (BEC_NOT_EQUAL_RE, BodyElementComparison_NotEqual) )

# TODO: Other types of comparison (greater than, less than or equal, etc.)

class BodyElementComparison_LessThan(BodyElementComparison):
    '''
        BodyElementComparison_LessThan - A BodyElementComparison which represents the "less than" operation, "<"

            This is a "NUMERIC_ONLY" comparison operation.
    '''

    NUMERIC_ONLY = True

    COMPARISON_OPERATOR_STR = '<'

    def _doComparison(self, leftSideValue, rightSideValue):
        return BodyElementValue_Boolean( leftSideValue < rightSideValue )


BEC_LESS_THAN_RE = re.compile(r'^([ \t]*[<][ \t]*)')
COMPARISON_RES.append( (BEC_LESS_THAN_RE, BodyElementComparison_LessThan) )


class BodyElementComparison_LessThanOrEqual(BodyElementComparison):
    '''
        BodyElementComparison_LessThanOrEqual - A BodyElementComparison which represents the "less than or equal" operation, "<="

            This is a "NUMERIC_ONLY" comparison operation.
    '''

    NUMERIC_ONLY = True

    COMPARISON_OPERATOR_STR = '<='

    def _doComparison(self, leftSideValue, rightSideValue):
        return BodyElementValue_Boolean( leftSideValue <= rightSideValue )


BEC_LESS_THAN_OR_EQUAL_RE = re.compile(r'^([ \t]*[<][=][ \t]*)')
COMPARISON_RES.append( (BEC_LESS_THAN_OR_EQUAL_RE, BodyElementComparison_LessThanOrEqual) )


class BodyElementComparison_GreaterThan(BodyElementComparison):
    '''
        BodyElementComparison_GreaterThan - A BodyElementComparison which represents the "greater than" operation, ">"

            This is a "NUMERIC_ONLY" comparison operation.
    '''

    NUMERIC_ONLY = True

    COMPARISON_OPERATOR_STR = '>'

    def _doComparison(self, leftSideValue, rightSideValue):
        return BodyElementValue_Boolean( leftSideValue > rightSideValue )


BEC_GREATER_THAN_RE = re.compile(r'^([ \t]*[>][ \t]*)')
COMPARISON_RES.append( (BEC_GREATER_THAN_RE, BodyElementComparison_GreaterThan) )


class BodyElementComparison_GreaterThanOrEqual(BodyElementComparison):
    '''
        BodyElementComparison_GreaterThanOrEqual - A BodyElementComparison which represents the "greater than or equal" operation, ">="

            This is a "NUMERIC_ONLY" comparison operation.
    '''

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
    '''
        BodyElementBooleanOps_And - A BodyElementBooleanOps which represents the "and" operation -

            will check that both the left and right side are True
    '''

    BOOLEAN_OP_STR = 'and'

    def _doBooleanOp(self, leftSideValue, rightSideValue):
        return BodyElementValue_Boolean( leftSideValue and rightSideValue )

# NOTE: these requires a whitespace after, unlike other operators.
BEBO_AND_RE = re.compile(r'^([ \t]*[aA][nN][dD][ \t]+)')
BOOLEAN_OPS_RES.append( (BEBO_AND_RE, BodyElementBooleanOps_And) )


class BodyElementBooleanOps_Or(BodyElementBooleanOps):
    '''
        BodyElementBooleanOps_Or - A BodyElementBooleanOps which represents the "or" operation -

            will check that either the left and right side are True
    '''

    BOOLEAN_OP_STR = 'or'

    def _doBooleanOp(self, leftSideValue, rightSideValue):
        return BodyElementValue_Boolean( leftSideValue or rightSideValue )


BEBO_OR_RE = re.compile(r'^([ \t]*[oO][rR][ \t]+)')
BOOLEAN_OPS_RES.append( (BEBO_OR_RE, BodyElementBooleanOps_Or) )

# ALL_BODY_ELEMENT_RES - All regular expressions used in parsing out a body into individual operations
ALL_BODY_ELEMENT_RES = VALUE_GENERATOR_RES + STATIC_VALUES_RES + COMPARISON_RES + OPERATION_RES + BOOLEAN_OPS_RES

# NOTE: Static values should come before operations, so negative values match as a static value and not a substract operation



class BodyLevel_Group(BodyLevel):
    '''
        BodyLevel_Group - A group of elements
    '''

    def __init__(self, groupMembers=None):
        '''
            __init__ - Create this element


                @param groupMembers list<BodyElement> - Members of this group
        '''
        BodyLevel.__init__(self)

        if not groupMembers:
            groupMembers = []

        self.appendBodyElements(groupMembers)

# BODY_ELEMENT_GROUP_OPEN_RE - The opening of a parenthesis group
BODY_ELEMENT_GROUP_OPEN_RE = re.compile(r'^([ \t]*[\(](?P<restOfBody>.+)[ \t]*)$')
# BODY_ELEMENT_GROUP_CLOSE_RE - The closing of a parenthesis group
BODY_ELEMENT_GROUP_CLOSE_RE = re.compile(r'^(?P<endOfGroup>[ \t]*[\)][ \t]*)')


def _parseBodyLevelGroup(restOfBody):
    '''
        _parseBodyLevelGroup - Parse a group, within parenthesis


            @param restOfBody <str> - The remainder of the body string to parse


            @return tuple< <BodyLevel_Group>, remainderStr<str> > - The group parsed, and the unused portion of the str on which to continue parsing at parent level
    '''
    allBodyElementREs = ALL_BODY_ELEMENT_RES
    bodyElementGroupOpenRE = BODY_ELEMENT_GROUP_OPEN_RE
    bodyElementGroupCloseRE = BODY_ELEMENT_GROUP_CLOSE_RE

    curString = restOfBody[:].strip()
    ret = []

    while curString:

        gotMatch = False

        groupCloseMatch = bodyElementGroupCloseRE.match(curString)
        if groupCloseMatch:
            # We are at the end of this group, return the rest of the string back upward

            gotMatch = True

            newCurString = curString[ groupCloseMatch.span()[1] : ]
            curString = newCurString

            break

        groupOpenMatch = bodyElementGroupOpenRE.match(curString)
        if groupOpenMatch:

            gotMatch = True

            (subLevel, newCurString) = _parseBodyLevelGroup( groupOpenMatch.groupdict()['restOfBody'] )

            ret.append(subLevel)
            curString = newCurString

            continue

        else:
            for ( bodyElementRE, bodyElementClass ) in allBodyElementREs:

                matchObj = bodyElementRE.match(curString)
                if matchObj is None:
                    continue

                gotMatch = True
                break

        if gotMatch is False:

            raise XPathParseError('Failed to parse body string into usable part, at: "%s"' %(curString, ))

        (thisElement, newCurString) = bodyElementClass.createFromMatch(curString, matchObj)
        ret.append(thisElement)

        curString = newCurString



    # Optimization: Before returning, run through and perform any operations against static values possible
    #newRet = _optimizeStaticValueCalculations(ret)
    ret = _optimizeStaticValueCalculations(ret)

    #print ( "\nPrevious BodyElements(%2d): %s\n\n  New    BodyElements(%2d): %s\n" %( len(ret), repr(ret), len(newRet), repr(newRet)) )

    #return newRet

    return ( BodyLevel_Group(ret), curString )


def parseBodyStringIntoBodyElements(bodyString):
    '''
        parseBodyStringIntoBodyElements - Parses the body string of a tag filter expression (between square brackets)

            into individual body elements.


                @param bodyString <str> - A body string of an XPath expression


                @return list<BodyElement> - A list of matched BodyElement items, in order of appearance.


                @raises XPathParseError - Failure to parse
    '''

    allBodyElementREs = ALL_BODY_ELEMENT_RES
    bodyElementGroupOpenRE = BODY_ELEMENT_GROUP_OPEN_RE

    curString = bodyString[:].strip()
    ret = []

    while curString:

        gotMatch = False

        groupOpenMatch = bodyElementGroupOpenRE.match(curString)
        if groupOpenMatch:

            gotMatch = True

            (subLevel, newCurString) = _parseBodyLevelGroup( groupOpenMatch.groupdict()['restOfBody'] )

            ret.append(subLevel)
            curString = newCurString

            continue

        else:
            for ( bodyElementRE, bodyElementClass ) in allBodyElementREs:

                matchObj = bodyElementRE.match(curString)
                if matchObj is None:
                    continue

                gotMatch = True
                break

        if gotMatch is False:

            raise XPathParseError('Failed to parse body string into usable part, at: "%s"' %(curString, ))


        (thisElement, newCurString) = bodyElementClass.createFromMatch(curString, matchObj)
        ret.append(thisElement)

        curString = newCurString


    # Optimization: Before returning, run through and perform any operations against static values possible
    #newRet = _optimizeStaticValueCalculations(ret)
    ret = _optimizeStaticValueCalculations(ret)

    #print ( "\nPrevious BodyElements(%2d): %s\n\n  New    BodyElements(%2d): %s\n" %( len(ret), repr(ret), len(newRet), repr(newRet)) )

    #return newRet
    return ret



def _optimizeStaticValueCalculations(bodyElements):
    '''
        _optimizeStaticValueCalculations - Optimize element portions that can be pre-calculated


            @param bodyElements - list<BodyElement> - List of BodyElements following parsing of XPath string


            @return list<BodyElement> - Optimized list of BodyElements, where pre-calculated operations are ran once at parse-time

                instead of per tag at run-time.
    '''
    numOrigElements = len(bodyElements)

    if numOrigElements <= 2:
        # Nothing to do
        return bodyElements


    # We are already going to hit __class__ on every object, so do it ahead of time
    #  in a quicker list comprehension, which we will reference later
    bodyElementClasses = [bodyElement.__class__ for bodyElement in bodyElements]

    # No benefit in checking if we have any BodyElementOperation (or future optimizations) first,
    #  as we will already iterate over everything. The only thing saved when none would be recreating the list,
    #  at the expense of O(n) vs O(2n) for the check in the event we can optimize.

    ret = []

    prevElement = bodyElements[0]
    prevElementClass = bodyElementClasses[0]

    ret.append(prevElement)

    i = 1
    while i < numOrigElements:

        curElement = bodyElements[i]
        curElementClass = bodyElementClasses[i]

        if issubclass(curElementClass, (BodyElementOperation, BodyElementComparison)):
            # If we have an operation to optimize, check if left and right are already values.
            #  If so, we can run it.

            if (i+1) < numOrigElements and issubclass(prevElementClass, BodyElementValue):
                # We are not on the last element, and the previous was a value.
                #  If next is value, run the operation.

                nextElement = bodyElements[i + 1]
                nextElementClass = bodyElementClasses[i + 1]

                if issubclass(nextElementClass, BodyElementValue):

                    # Score! We can optimize!
                    if issubclass(curElementClass, BodyElementOperation):
                        calculatedValue = curElement.performOperation(prevElement, nextElement)
                    #elif issubclass(curElementClass, BodyElementComparison):
                    else:
                        # Only Comparison left
                        calculatedValue = curElement.doComparison(prevElement, nextElement)

                    # Strip off the previous value, and replace this operation and next value with calculated
                    ret = ret[ : -1 ] + [calculatedValue]

                    # Set previous value to this value
                    prevElement = calculatedValue
                    prevElementClass = prevElement.__class__

                    # And increment past the next element
                    i += 2

                    continue

        # No optimization available, add the element as-is
        ret.append(curElement)

        # Update previous element to this element for next round
        prevElement = curElement
        prevElementClass = curElementClass

        # Increment to next element
        i += 1

    return ret


# vim: set ts=4 sw=4 st=4 expandtab :
