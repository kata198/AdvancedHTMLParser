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

NEXT_TAG_OPERATION_RE = re.compile(r'''^[ \t]*(?P<lead_in>[/]{1,2})[ \t]*(?P<full_tag>(((?P<prefix>parent|child|ancestor|descendant))[:][:]){0,1}(?P<tagname>[\*]|([a-zA-Z_][a-zA-Z0-9_\-]*))([:][:](?P<suffix>[a-zA-Z][a-zA-Z0-9_\-]*([\(][ \t]*[\)]){0,1})){0,1})''')

BRACKETED_SUBSET_RE = re.compile(r'''^[ \t]*[\[](?P<bracket_inner>((["]([\\]["]|[^"])*["])|([']([\\][']|[^'])*['])|[^\]])*)[\]][ \t]*''')

global DEBUG

DEBUG = False
#DEBUG = True

def _setDebug(newValue):
    '''
        _setDebug - Temp function to change the global DEBUG for development.

            Will be removed for production release.

              @param newValue <bool> - True to enable debugging prints, False to disable them.
    '''
    global DEBUG
    DEBUG = newValue

class XPathParseError(Exception):
    '''
        XPathParseError - Base exception raised when there is a parsing error for a provided XPath string.
    '''
    pass


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



class NullType(object):
    '''
        NullType - Represents a comparative class for use with Null (equal to other nulls, not equal to non-nulls)
    '''

    def __eq__(self, other):

        return bool( isinstance(other, NullType) )

    def __ne__(self, other):

        return not bool( isinstance(other, NullType) )

# Null - Singleton for the NullType
Null = NullType()


def _mk_xpath_op_filter_by_tagname_one_level_function(tagName):
    '''
        _mk_xpath_op_filter_by_tagname_one_level_function - Filters one level of descent, by tag name or wildcard.

            This function will create and return the function to be used with the associated XPathOperation.


                @param tagName <str> - The tag name upon which to filter, or "*" for wildcard


                @return list< AdvancedHTMLParser.Tags.AdvancedTag > - A list of tags which match the provided tagname after descent
    '''

    tagName = tagName.lower()

    if tagName == '*':

        # Get all direct children

        def _innerFunc(prevTag):

            # Make a copy of children, will be consolidated to unique in final TagCollection assembly
            return list( prevTag.children )

    else:

        # For a specific tag

        def _innerFunc(prevTag):

            _tagName = tagName

            return [ childEm for childEm in prevTag.children if childEm.tagName == _tagName ]

    return _innerFunc


def _mk_xpath_op_filter_by_tagname_one_level_function_or_self(tagName):
    '''
        _mk_xpath_op_filter_by_tagname_one_level_function_or_self - Filters one level of descent, by tag name or wildcard, or self.

            This function will create and return the function to be used with the associated XPathOperation.


                @param tagName <str> - The tag name upon which to filter, or "*" for wildcard


                @return list< AdvancedHTMLParser.Tags.AdvancedTag > - A list of tags which match the provided tagname after descent
    '''

    tagName = tagName.lower()

    if tagName == '*':

        # Get all direct children

        def _innerFunc(prevTag):

            # Make a copy of children, will be consolidated to unique in final TagCollection assembly
            return [prevTag] + list( prevTag.children )

    else:

        # For a specific tag

        def _innerFunc(prevTag):

            _tagName = tagName

            ret = [ childEm for childEm in prevTag.children if childEm.tagName == _tagName ]
            if prevTag.tagName == tagName:
                return [prevTag] + ret
            return ret

    return _innerFunc



def _mk_xpath_op_filter_by_tagname_multi_level_function(tagName):
    '''
        _mk_xpath_op_filter_by_tagname_multi_level_function - Filter for a given tag name on any number of levels down

            This function will create the function to be associated with the XPathOperation.


                @param tagName <str> - The tag name on which to filter, or "*" for wildcard


                @return list< Tags.AdvancedTag > - A list of tags which match this filter operation
    '''

    tagName = tagName.lower()

    if tagName == '*':
        # Get all child nodes recursively

        def _innerFunc(prevTag):
            # Make a copy of all child nodes, they will be made unique in the final TagCollection assembly
            return list( prevTag.getAllChildNodes() )

    else:
        # Specific tag name

        def _innerFunc(prevTag):

            _tagName = tagName.lower()

            # TODO: Better?
            thisTagCollection = TagCollection(prevTag)

            # These will all be merged into a unique TagCollection by calee
            return list( thisTagCollection.getElementsByTagName(_tagName) )

    return _innerFunc


def _mk_xpath_op_filter_by_tagname_multi_level_function_or_self(tagName):
    '''
        _mk_xpath_op_filter_by_tagname_multi_level_function_or_self - Filter for a given tag name on any number of levels down and self

            This function will create the function to be associated with the XPathOperation.


                @param tagName <str> - The tag name on which to filter, or "*" for wildcard


                @return list< Tags.AdvancedTag > - A list of tags which match this filter operation
    '''

    tagName = tagName.lower()

    if tagName == '*':
        # Get all child nodes recursively

        def _innerFunc(prevTag):
            # Make a copy of all child nodes, they will be made unique in the final TagCollection assembly
            return [prevTag] + list( prevTag.getAllChildNodes() )

    else:
        # Specific tag name

        def _innerFunc(prevTag):

            _tagName = tagName.lower()

            # TODO: Better?
            thisTagCollection = TagCollection(prevTag)

            # These will all be merged into a unique TagCollection by calee
            ret = list( thisTagCollection.getElementsByTagName(_tagName) )
            if prevTag.tagName == _tagName:
                return [prevTag] + ret
            return ret

    return _innerFunc


def _mk_xpath_op_filter_tag_is_nth_child_index(tagName, nthIdxOrd1):
    '''
        _mk_xpath_op_filter_tag_is_nth_child_index - Filter for the Nth (origin-1) instance of a given tag name, as a child

            This function will create the function to be associated with the XPathOperation.


                @param tagName <str> - The tag name on which to filter, or "*" for wildcard

                @param nthIdxOrd1 <int> - An origin-1 number (1 = first, 2 = second) for which child to return, if present.


                @return list< Tags.AdvancedTag > - A list of tags which match this filter operation.
    '''

    # Check if this is the nth node, ord-1, of a given parent (for like /div[5])
    #  If so, return the previous tag (matched), otherwise discard.

    _tagName = tagName.lower()

    _nthIdxOrd1 = int(nthIdxOrd1)


    # TODO: Should this be combined with the tag search, per above, or kept as separate operation?
    def _innerFunc(prevTag):

        parentElement = prevTag.parentElement

        if parentElement is None:

            if nthIdxOrd1 == 1:
                # No parent, but we are requesting first node (this)
                return [prevTag]

            return []

        if tagName == '*':

            childrenOfRelevance = list(parentElement.children)

        else:

            childrenOfRelevance = [ childEm for childEm in parentElement.children if childEm.tagName == _tagName ]

        childIdx = childrenOfRelevance.index( prevTag )

        if childIdx + 1 == _nthIdxOrd1:

            return [ prevTag ]

        return []

    return _innerFunc


def _mk_xpath_op_filter_by_parent_tagname_one_level_function(tagName):
    '''
        _mk_xpath_op_filter_by_parent_tagname_one_level_function - Filter one level up of current level for a parent with a given tag name.

            This function will create and return a function to be associated with the XPathOperation


            @param tagName <str> - The tag name for which to filter, or "*" for wildcard.


            @return list<AdvancedTag> - A list of tags which match this operation.
    '''

    tagName = tagName.lower()

    if tagName == '*':

        # Get all direct children

        def _innerFunc(prevTag):

            # Reference any parent
            parentElement = prevTag.parentElement
            if parentElement:
                return [ parentElement ]
            return []

    else:

        # For a specific tag

        def _innerFunc(prevTag):

            parentElement = prevTag.parentElement
            if parentElement and parentElement.tagName == tagName:
                return [ parentElement ]
            return []

    return _innerFunc


def _mk_xpath_op_filter_by_ancestor_tagname_multi_level_function(tagName):
    '''
        _mk_xpath_op_filter_by_ancestor_tagname_multi_level_function - Search all ancestors upward of the current level for tag name matches

            This function will create and return the function to be associated with the XPathOperation


            @param tagName <str> - The tag name on which to filter, or "*" for wildcard


            @return list<AdvancedTag> - A list of all tags which matched this filter operation.
    '''

    tagName = tagName.lower()

    if tagName == '*':
        # Get all child nodes recursively

        def _innerFunc(prevTag):

            curNode = prevTag.parentElement
            ret = []

            while curNode:

                ret.append( curNode )
                curNode = curNode.parentElement

            return ret

    else:
        # Specific tag name

        def _innerFunc(prevTag):

            curNode = prevTag.parentElement
            ret = []

            while curNode:

                if curNode.tagName == tagName:
                    ret.append(curNode)

                curNode = curNode.parentElement

            return ret

    return _innerFunc


def _mk_xpath_op_filter_by_ancestor_or_self_tagname_multi_level_function(tagName):
    '''
        _mk_xpath_op_filter_by_ancestor_or_self_tagname_multi_level_function - Search all ancestors upward of the current level, and self, for tag name matches

            This function will create and return the function to be associated with the XPathOperation


            @param tagName <str> - The tag name on which to filter, or "*" for wildcard


            @return list<AdvancedTag> - A list of all tags which matched this filter operation.
    '''

    tagName = tagName.lower()

    if tagName == '*':
        # Get all child nodes recursively

        def _innerFunc(prevTag):

            curNode = prevTag.parentElement
            ret = []

            while curNode:

                ret.append( curNode )
                curNode = curNode.parentElement

            return [prevTag] + ret

    else:
        # Specific tag name

        def _innerFunc(prevTag):

            curNode = prevTag.parentElement
            ret = []

            while curNode:

                if curNode.tagName == tagName:
                    ret.append(curNode)

                curNode = curNode.parentElement

            if prevTag.tagName == tagName:
                return [prevTag] + ret
            return ret

    return _innerFunc


def _mk_helper_float_comparison_filter_wildcard(attributeValue, compareTagAttributeValueToTestValueLambda):
    '''
        _mk_helper_float_comparison_filter_wildcard - A helper function to make a function which will

            test a given attribute value, as a float, and compare it using a provided compare function/lambda.

            Wildcard version, all attributes.


            @param attributeValue <float/int/str> - The attribute value to test

            @param compareTagAttributeValueToTestValueLambda <function/lambda> - The comparison function to use, should return bool (True = match, False = no match)


            @return <function> - A special comparitive function to use to compare a provided tag against the given attribute value and comparison function
    '''

    try:
        _attributeValueFloat = float(attributeValue)
    except ValueError:

        # Not a parse error, just empty result
        _innerFunc = lambda prevTag : []
        return _innerFunc

    _compareTagAttributeValueToTestValueLambda = compareTagAttributeValueToTestValueLambda

    def _innerFunc(prevTag):

        for tagAttributeName, tagAttributeValue in prevTag.attributesDict.items():

            try:
                tagAttributeValueFloat = float(tagAttributeValue)
            except ValueError:
                continue

            if _compareTagAttributeValueToTestValueLambda( tagAttributeValueFloat, _attributeValueFloat ) is True:

                return [prevTag]

        return []

    return _innerFunc


def _mk_helper_float_comparison_filter_named(attributeName, attributeValue, compareTagAttributeValueToTestValueLambda):
    '''
        _mk_helper_float_comparison_filter_named - A helper function to make a function which will

            test a given attribute value, as a float, and compare it using a provided compare function/lambda.

            Named version -- tests a specific attribute, by name.


            @param attributeName <str> - The name of the attribute to test

            @param attributeValue <float/int/str> - The attribute value to test

            @param compareTagAttributeValueToTestValueLambda <function/lambda> - The comparison function to use, should return bool (True = match, False = no match)


            @return <function> - A special comparitive function to use to compare a provided tag against the given attribute name's value and comparison function
    '''

    try:
        _attributeValueFloat = float(attributeValue)
    except ValueError:

        # Not a parse error, just empty result
        _innerFunc = lambda prevTag : []
        return _innerFunc

    _compareTagAttributeValueToTestValueLambda = compareTagAttributeValueToTestValueLambda
    _attributeName = attributeName[:]

    def _innerFunc(prevTag):

        if prevTag.hasAttribute(_attributeName) is False:

            # No such attribute, not a match
            return []

        try:
            tagAttributeValueFloat = float( prevTag.getAttribute(_attributeName) )
        except ValueError:
            # Cannot convert attribute value to float, not a match
            return []

        if _compareTagAttributeValueToTestValueLambda( tagAttributeValueFloat, _attributeValueFloat ) is True:

            return [prevTag]

        return []

    return _innerFunc


class ComplexBodyPart(object):
    '''
        ComplexBodyPart - Base class for a single operation within a bracketed filter expression
    '''

    PART_TYPE_FUNCTION = 0
    PART_TYPE_FETCH_ATTRIBUTE = 1
    PART_TYPE_OPERATOR = 2
    PART_TYPE_STATIC_DATA = 3
    PART_TYPE_MATH_OPERATOR = 4
    PART_TYPE_TRANSFORMATION = 5
    PART_TYPE_MULTIPLE = 6

    def __init__(self, partType):
        '''
            __init__ - Create a ComplexBodyPart of a given type

                @param partType <int> - The corrosponding "part type" constant, ComplexBodyPart.PART_TYPE_*
        '''

        self.partType = partType

    def evaluate(self, thisTag):
        '''
            evaluate - Evaluate this body part against a tag.


                @param thisTag <AdvancedTag> - Tag of interest

                TODO: Note what this returns
        '''
        raise Exception('ComplexBodyPart.evaluate must be overridden!')

    def __repr__(self):
        '''
            __repr__ - String representation of this type
        '''
        return "%s< %s >" %( self.__class__.__name__, repr(self.__dict__))

# BODY_PARTS_TO_RES - A list of tuples, ( BodyPartRE, BodyPartChildClass)
BODY_PARTS_TO_RES = []

# BODY_PART_FUNCTION_NAMES_TO_CLASS - The names of a given function to its BodyPart class
BODY_PART_FUNCTION_NAMES_TO_CLASS = {}


class ComplexBodyPart_Function(ComplexBodyPart):
    '''
        ComplexBodyPart_Function - The ComplexBodyPart base class for a PART_TYPE_FUNCTION
    '''

    def __init__(self, functionName, functionInner=None):
        '''
            __init__ - Create a function ComplexBodyPart

                @param functionName <str> - Name of the function

                @param functionInner <str/None> Default None - The "inner" portion of the function, as a string, or None
        '''

        ComplexBodyPart.__init__(self, ComplexBodyPart.PART_TYPE_FUNCTION)

        self.functionName = functionName
        self.functionInner = functionInner

    def evaluate(self, thisTag):
        pass



class ComplexBodyPart_Function_Last(ComplexBodyPart_Function):
    '''
        ComplexBodyPart_Function_Last - Implementation for the function last()
    '''

    def __init__(self, functionInner=None):
        ComplexBodyPart_Function.__init__(self, 'last', functionInner)


    def evaluate(self, thisTag):
        '''
            evaluate - Evaluate the "last()" value for the given tag's parent

                @param thisTag <AdvancedTag> - Tag to test


                @return <str> - The 1-origin index of the last tag of parent with same tag name
        '''
        # TODO: Is this right?

        parentElement = thisTag.parentElement

        if parentElement is None:

            # No parent, last() must be 1
            return '1'

        thisTagName = thisTag.tagName

        childrenOfRelevance = [ childEm for childEm in parentElement.children if childEm.tagName == thisTagName ]

        return str( len( childrenOfRelevance ) )


BODY_PART_FUNCTION_LAST_RE = re.compile(r'^([ \t]*[lL][aA][sS][tT][ \t]*[\(][ \t]*[\)][ \t]*)')
BODY_PARTS_TO_RES.append( (BODY_PART_FUNCTION_LAST_RE, ComplexBodyPart_Function_Last) )

BODY_PART_FUNCTION_NAMES_TO_CLASS['last'] = ComplexBodyPart_Function_Last

# TODO: Do wildcards stay true to their own tag name, or change to all tag names?
#  For example, is //*[position() < 3] all nodes with a parent index < (ord 1) 3, or with same tag name?

# Seems to be per tag name, but test more?

class ComplexBodyPart_Function_Position(ComplexBodyPart_Function):

    def __init__(self, functionInner=None):

        ComplexBodyPart_Function.__init__(self, 'position', functionInner)


    def evaluate(self, thisTag):

        parentElement = thisTag.parentElement

        if parentElement is None:

            # No parent, position() must be 1
            return '1'

        thisTagName = thisTag.tagName

        childrenOfRelevance = [ childEm for childEm in parentElement.children if childEm.tagName == thisTagName ]

        return str( childrenOfRelevance.index( thisTag ) + 1 )


BODY_PART_FUNCTION_POSITION_RE = re.compile(r'^([ \t]*[pP][oO][sS][iI][tT][iI][oO][nN][ \t]*[\(][ \t]*[\)][ \t]*)')
BODY_PARTS_TO_RES.append( (BODY_PART_FUNCTION_POSITION_RE, ComplexBodyPart_Function_Position) )

BODY_PART_FUNCTION_NAMES_TO_CLASS['position'] = ComplexBodyPart_Function_Position


class ComplexBodyPart_Function_Text(ComplexBodyPart_Function):

    def __init__(self, functionInner=None):

        ComplexBodyPart_Function.__init__(self, 'text', functionInner)


    def evaluate(self, thisTag):

        # TODO: Something special to separate these strings from raw values?
        return '%s' %(thisTag.innerText, )


BODY_PART_FUNCTION_TEXT_RE = re.compile(r'^([ \t]*[tT][eE][xX][tT][ \t]*[\(][ \t]*[\)][ \t]*)')
BODY_PARTS_TO_RES.append( (BODY_PART_FUNCTION_TEXT_RE, ComplexBodyPart_Function_Text) )

BODY_PART_FUNCTION_NAMES_TO_CLASS['text'] = ComplexBodyPart_Function_Text


class ComplexBodyPart_Function_NormalizeSpace(ComplexBodyPart_Function):

    def __init__(self, functionInner=None):

        ComplexBodyPart_Function.__init__(self, 'normalize-space', functionInner)


    def evaluate(self, thisTag):

        # TODO: Something special to separate these strings from raw values?
        return '%s' %(thisTag.innerText.strip(), )


BODY_PART_FUNCTION_NORMALIZESPACE_RE = re.compile(r'^([ \t]*[nN][oO][rR][mM][aA][lL][iI][zZ][eE][\-][sS][pP][aA][cC][eE][ \t]*[\(][ \t]*[\)][ \t]*)')
BODY_PARTS_TO_RES.append( (BODY_PART_FUNCTION_NORMALIZESPACE_RE, ComplexBodyPart_Function_NormalizeSpace) )

BODY_PART_FUNCTION_NAMES_TO_CLASS['normalize-space'] = ComplexBodyPart_Function_NormalizeSpace


class ComplexBodyPart_Operator(ComplexBodyPart):

    def __init__(self, operator):

        ComplexBodyPart.__init__(self, ComplexBodyPart.PART_TYPE_OPERATOR)
        self.operator = operator

    def evaluate(self, left, right):
        raise Exception('ComplexBodyPart_Operator.evaluate should not be called directly, use a subclass!')


# TODO: Work on these "evaluate"s

class ComplexBodyPart_Operator_Equal(ComplexBodyPart_Operator):

    def __init__(self):

        ComplexBodyPart_Operator.__init__(self, '=')

    def evaluate(self, left, right):

        try:
            return float(left) == float(right)
        except:
            return left == right


BODY_PART_OPERATOR_EQUAL_RE = re.compile(r'^([ \t]*[=][ \t]*)')
BODY_PARTS_TO_RES.append( (BODY_PART_OPERATOR_EQUAL_RE, ComplexBodyPart_Operator_Equal) )


class ComplexBodyPart_Operator_NotEqual(ComplexBodyPart_Operator):

    def __init__(self):

        ComplexBodyPart_Operator.__init__(self, '!=')

    def evaluate(self, left, right):

        try:
            return float(left) != float(right)
        except:
            return left != right


BODY_PART_OPERATOR_NOTEQUAL_RE = re.compile(r'^([ \t]*[!][=][ \t]*)')
BODY_PARTS_TO_RES.append( (BODY_PART_OPERATOR_NOTEQUAL_RE, ComplexBodyPart_Operator_NotEqual) )


class ComplexBodyPart_Operator_LessThanEqual(ComplexBodyPart_Operator):

    def __init__(self):

        ComplexBodyPart_Operator.__init__(self, '<=')

    def evaluate(self, left, right):

        try:
            return float(left) <= float(right)
        except:
            return False


BODY_PART_OPERATOR_LESSTHANEQUAL_RE = re.compile(r'^([ \t]*[<][=][ \t]*)')
BODY_PARTS_TO_RES.append( (BODY_PART_OPERATOR_LESSTHANEQUAL_RE, ComplexBodyPart_Operator_LessThanEqual) )



class ComplexBodyPart_Operator_LessThan(ComplexBodyPart_Operator):

    def __init__(self):

        ComplexBodyPart_Operator.__init__(self, '<')

    def evaluate(self, left, right):

        try:
            return float(left) < float(right)
        except:
            return False


BODY_PART_OPERATOR_LESSTHAN_RE = re.compile(r'^([ \t]*[<][ \t]*)')
BODY_PARTS_TO_RES.append( (BODY_PART_OPERATOR_LESSTHAN_RE, ComplexBodyPart_Operator_LessThan) )


class ComplexBodyPart_Operator_GreaterThanEqual(ComplexBodyPart_Operator):

    def __init__(self):

        ComplexBodyPart_Operator.__init__(self, '>=')

    def evaluate(self, left, right):

        try:
            return float(left) >= float(right)
        except:
            return False


BODY_PART_OPERATOR_GREATERTHANEQUAL_RE = re.compile(r'^([ \t]*[>][=][ \t]*)')
BODY_PARTS_TO_RES.append( (BODY_PART_OPERATOR_GREATERTHANEQUAL_RE, ComplexBodyPart_Operator_GreaterThanEqual) )


class ComplexBodyPart_Operator_GreaterThan(ComplexBodyPart_Operator):

    def __init__(self):

        ComplexBodyPart_Operator.__init__(self, '>')

    def evaluate(self, left, right):

        try:
            return float(left) > float(right)
        except:
            return False


BODY_PART_OPERATOR_GREATERTHAN_RE = re.compile(r'^([ \t]*[>][ \t]*)')
BODY_PARTS_TO_RES.append( (BODY_PART_OPERATOR_GREATERTHAN_RE, ComplexBodyPart_Operator_GreaterThan) )


class ComplexBodyPart_FetchAttribute(ComplexBodyPart):

    def __init__(self, attributeName):

        ComplexBodyPart.__init__(self, ComplexBodyPart.PART_TYPE_FETCH_ATTRIBUTE)
        self.attributeName = attributeName

    def evaluate(self, thisTag):

        # TODO: Improve this, wildcards, etc.
        if self.attributeName == '*':
            raise Exception('Wildcard attributes not yet supported')

        if not thisTag.hasAttribute( self.attributeName ):
            # TODO: Investigate this singleton type
            return Null

        # TODO: Escape?
        # TODO: Something special to separate this result from random string?
        return '%s' %( thisTag.getAttribute( self.attributeName) )

BODY_PART_FETCH_ATTRIBUTE_RE = re.compile(r'^[ \t]*[@](?P<attributeName>([*]|[a-zA-Z_][a-zA-Z0-9_\-]*))[ \t]*')
BODY_PARTS_TO_RES.append( (BODY_PART_FETCH_ATTRIBUTE_RE, ComplexBodyPart_FetchAttribute) )

# TODO: Static names like "null" ?

class ComplexBodyPart_StaticData(ComplexBodyPart):

    def __init__(self):

        ComplexBodyPart.__init__(self, ComplexBodyPart.PART_TYPE_STATIC_DATA)


class ComplexBodyPart_StaticData_Number(ComplexBodyPart_StaticData):

    def __init__(self, staticNumber, hasDecimal=False):

        ComplexBodyPart_StaticData.__init__(self)
        self.staticNumber = staticNumber.replace(' ', '').replace('\t', '')
        hasDecimal = bool(hasDecimal)

        if hasDecimal is True:
            self.staticNumber = float(self.staticNumber)
        else:
            self.staticNumber = int(self.staticNumber)

    def evaluate(self, thisTag):

        if isinstance(self.staticNumber, float):
            return "%f" %(self.staticNumber, )

        return "%d" %(self.staticNumber, )


# TODO: This accepts things like "12." as just "12", when it should reject
#BODY_PART_STATICDATA_NUMBER_RE = re.compile(r'^[ \t]*(?P<staticNumber>[-]{0,1}[ \t]*([\d]*[\.][\d]+|[\d]+))[ \t]*')
BODY_PART_STATICDATA_NUMBER_RE = re.compile(r'^[ \t]*(?P<staticNumber>[-]{0,1}[ \t]*([\d]*(?P<hasDecimal>[\.])[\d]+|[\d]+))[ \t]*')
BODY_PARTS_TO_RES.append( (BODY_PART_STATICDATA_NUMBER_RE, ComplexBodyPart_StaticData_Number) )


class ComplexBodyPart_StaticData_String(ComplexBodyPart_StaticData):

    def __init__(self, staticString):

        ComplexBodyPart_StaticData.__init__(self)
        self.staticString = staticString

    def evaluate(self, thisTag):

        return "%s" %(self.staticString, )


# TODO: Unquoted static strings?
BODY_PART_STATICDATA_DOUBLEQUOTE_STRING_RE = re.compile(r'^[ \t]*["](?P<staticString>([\\]["]|[^"]*))["][ \t]*')
BODY_PARTS_TO_RES.append( (BODY_PART_STATICDATA_DOUBLEQUOTE_STRING_RE, ComplexBodyPart_StaticData_String) )

BODY_PART_STATICDATA_SINGLEQUOTE_STRING_RE = re.compile(r'''^[ \t]*['](?P<staticString>([\\][']|[^']*))['][ \t]*''')
BODY_PARTS_TO_RES.append( (BODY_PART_STATICDATA_SINGLEQUOTE_STRING_RE, ComplexBodyPart_StaticData_String) )



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




class ComplexBodyPart_Transformation(ComplexBodyPart):


    def __init__(self, transformationName):

        ComplexBodyPart.__init__(self, ComplexBodyPart.PART_TYPE_TRANSFORMATION)

        self.transformationName = transformationName



class ComplexBodyPart_Transformation_Concat(ComplexBodyPart_Transformation):

    def __init__(self):

        ComplexBodyPart_Transformation('concat')


class ComplexBodyPart_Multiple(ComplexBodyPart):

    def __init__(self):

        ComplexBodyPart.__init__(self, ComplexBodyPart.PART_TYPE_MULTIPLE)

        self.innerToOuterComplexBodies = []


    def addComplexBody(self, complexBody):

        self.innerToOuterComplexBodies.append(complexBody)


COMPLEX_BODY_FUNCTION_EXTRACT_RE = re.compile(r'''^[ \t]*(?P<name>[a-zA-Z_][a-zA-Z0-9_\-]*)[ \t]*[\(](?P<function_inner>([^\)'"]+|["]([\\]["]|[^"])*["]|[']([\\][']|[^'])*)*)''')

# TODO: These expressions will not work in conjunction with very complex statements, or compound statements ("and" / "or" within same body)
#  Replace parsing with tokenization?



class ComplexBody(object):
    '''
        ComplexBody - A base class to hold several complex body parts, the sum of which represents a full body for a filter operation
    '''

    def __init__(self):

        self.bodyParts = []


    def evaluateBodyToString(self, thisTag):

        raise Exception('UNUSED')

        parts = []
        for bodyPart in self.bodyParts:

            parts.append( bodyPart.evaluate(thisTag) )

        return ' '.join(parts)



    def evaluateBodyToOperations(self, thisTag):

        origParts = copy.deepcopy(self.bodyParts)
        thisLevelParts = origParts[:]
        keepGoing = True

        while keepGoing is True:
            curParts = []
            keepGoing = False

            for thisPart in thisLevelParts:

                if not issubclass(thisPart.__class__, ComplexBodyPart):
                    curParts.append(thisPart)
                    continue

                if thisPart.partType == ComplexBodyPart.PART_TYPE_OPERATOR:

                    curParts.append(thisPart)
                    continue

                else:

                    thisItem = thisPart.evaluate( thisTag )
                    curParts.append(thisItem)

                    if issubclass(thisItem.__class__, ComplexBodyPart):
                        # If we did not recurse into another function that needs unrolling, we can complete.
                        #  Otherwise, we have to go another round.
                        # TODO: Maybe can just loop on unrolls here?
                        keepGoing = True

            thisLevelParts = curParts
            if DEBUG is True:
                print ( "After iteration, remaining parts are: %s\n" %( repr(curParts), ))

        # Now need to combine into operations
        leftSide = None
        operatorPart = None
        rightSide = None

        i = 0
        numPartsTotal = len(thisLevelParts)

        retOperations = []

        while i < numPartsTotal:

            thisPart = thisLevelParts[i]
            i += 1

            if getattr(thisPart, 'partType', None) == ComplexBodyPart.PART_TYPE_OPERATOR:

                if leftSide is None:

                    raise XPathParseError('Converting complex body to operations -- hit an operator %s but no left-side yet defined!' %( repr(thisPart), ))

                operatorPart = thisPart
                # TODO: Implicit rules, no operator? Any conditions where both left and right would not have to be present for an operator?
                continue

            if leftSide is None:

                # Set the left side to this data
                leftSide = thisPart
                continue

            if rightSide is None:

                rightSide = thisPart

                if operatorPart is None:

                    raise XPathParseError('Converting complex body to operations -- Found a left side "%s"  and a right side  "%s"  but no operator between!' %( leftSide, rightSide ) )

                # Okay, we should have everything to build an operation
                operationFunc = _buildOperationFromOperator(leftSide, operatorPart, rightSide)

                # Build and add operation to our ordered operations
                thisXPathOperation = XPathOperation(operationFunc, 'TODO:XPATH TEXT' )
                retOperations.append(thisXPathOperation)

                # Clear construction variables
                leftSide = None
                operatorPart = None
                rightSide = None


        if leftSide is not None:

            # TODO: Should be no results if just float that != int, rather than exception
            try:
                if int(float(leftSide)) == float(leftSide):
                    leftSide = str( int( float(leftSide) ) )
            except:
                pass

            if leftSide.isdigit():
                # We have a fixed digit
                innerNum = int(leftSide)

                if innerNum == 0:
                    # Do not allow 0.
                    # XXX: Normal xpath will just return empty list, but raise an actual error here instead.
                    raise XPathParseError('Got request for 0th node in xpath portion, "%s" -- indexes must be 1-ordinal.' %(' TODO:XPATH TEXT2', ))

                innerFunc = _mk_xpath_op_filter_tag_is_nth_child_index( thisTag.tagName, innerNum )

                # XXX: Should the second part just be the body? Maybe highlighted somewhere else?
                innerXPathOperation = XPathOperation( innerFunc, '' ) # TODO: Xpath text 2.1

                retOperations.append( innerXPathOperation )

                leftSide = None

            else:

                raise XPathParseError('Converting complex body to operations -- extra parts with no operator!  leftSide=%s , operatorPart=%s, rightSide=%s' %( repr(leftSide), repr(operatorPart), repr(rightSide) ) )

        return retOperations


    def addPart(self, nextPart):

        self.bodyParts.append(nextPart)


    def addParts(self, nextParts):

        self.bodyParts += nextParts


    def __repr__(self):

        return "ComplexBody< bodyParts = %s >" %( repr(self.bodyParts), )




def _getNextFunctionParts(curString, theseParts=None):

    if theseParts is None:
        theseParts = []

    #COMPLEX_BODY_FUNCTION_EXTRACT_RE = re.compile(r'''^[ \t]*(?P<name>[a-zA-Z_][a-zA-Z0-9_\-]*)[ \t]*[\(](?P<function_inner>([^\)'"]+|["]([\\]["]|[^"])*["]|[']([\\][']|[^'])*)*)''')

    complexFunctionParts = COMPLEX_BODY_FUNCTION_EXTRACT_RE.match(curString)

    if not complexFunctionParts:
        return None

    theseFunctionPartGroupDicts = []

    thisGroupDict = complexFunctionParts.groupdict()

    thisFunctionName = thisGroupDict['name'].lower()
    if thisFunctionName not in BODY_PART_FUNCTION_NAMES_TO_CLASS:
        raise Exception('Unknown function name: %s' %(thisFunctionName, ))

    thisFunctionInner = thisGroupDict['function_inner']

    theseFunctionPartGroupDicts.append(thisGroupDict)
    keepGoing = True

    while keepGoing is True:

        nextComplexFunctionParts = COMPLEX_BODY_FUNCTION_EXTRACT_RE.match( thisFunctionInner )

        if not nextComplexFunctionParts:
            keepGoing = False
            break

        nextGroupDict = nextComplexFunctionParts.groupdict()

        nextFunctionName = nextGroupDict['name'].lower()
        if nextFunctionName not in BODY_PART_FUNCTION_NAMES_TO_CLASS:
            raise Exception('2Unknown function name: %s' %(nextFunctionName, ))

        thisFunctionInner = nextGroupDict['function_inner']

        theseFunctionPartGroupDicts.append(nextGroupDict)


    complexBodyPartMultiple = ComplexBodyPart_Multiple()

    theseFunctionPartGroupDictsReversed = reversed( theseFunctionPartGroupDicts )

    for innerMostFunctionPartGroupDict in theseFunctionPartGroupDictsReversed:

        theseComplexParts = parseBodyStringIntoComplexBodyParts('%s(%s)' %( innerMostFunctionPartGroupDict['name'], innerMostFunctionPartGroupDict['function_inner'] ))

        thisComplexBody = ComplexBody()
        thisComplexBody.addParts( theseComplexParts )

        complexBodyPartMultiple.addComplexBody(thisComplexBody)


def parseBodyStringIntoComplexBodyParts(bodyString):

    curString = bodyString[:].strip()
    ret = []

    while curString:

        gotMatch = False

        for ( bodyPartRE, bodyPartClass ) in BODY_PARTS_TO_RES:

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



def parseBodyStringIntoComplexBody(bodyString):

    curString = bodyString[:].strip()
    ret = ComplexBody()

    while curString:
        gotMatch = False

        for ( bodyPartRE, bodyPartClass ) in BODY_PARTS_TO_RES:

            matchObj = bodyPartRE.match(curString)
            if matchObj is None:
                continue

            gotMatch = True
            break

        if gotMatch is False:

            raise XPathParseError('2Failed to parse body string into usable part, at: "%s"' %(curString, ))

        groupDict = matchObj.groupdict()

        thisPart = bodyPartClass( **groupDict )
        ret.addPart(thisPart)

        curString = curString[ matchObj.span()[1] : ].lstrip()

    return ret






# TODO: Make sure we correctly handle variably cased attribute names, xpath is case insensitive on names
# TODO: Handle special functions within attribute value

# TODO: Support math ( +, -, *, div )
# TODO: Support "or" , "and" , "mod"
# TODO: Support compound / multiple conditions

# TODO: Support node inner text searching (e.x. //li[a='hello'] for an <li> tag with a child <a ... >hello</a>

def _mk_xpath_op_filter_attribute(attributeName, attributeValue, operator):

    # TODO: Check that value is quoted if it is a non-number

    _attributeName = attributeName.lower()
    _attributeValue = copy.copy(attributeValue)
    _operator = copy.copy(operator)

    if _attributeValue is None:

        # No attribute value means no operator

        if _attributeName == '*':

            # Wildcard attribute name, no value specified, must contain at least one attribute

            def _innerFunc(prevTag):

                if len(prevTag.attributesDict.keys()) >= 1:

                    return [prevTag]

                return []

            return _innerFunc

        else:

            # Specific attribute name, no value specified, must contain a given attribute

            def _innerFunc(prevTag):

                # XXX: Do we need second part of check?
                if _attributeName in prevTag.attributesDict and prevTag.getAttribute(_attributeName) is not None:

                    return [prevTag]

                return []

            return _innerFunc

    else:

        # We have both a defined name and value

        if _attributeName == '*':

            # Wildcard name, at least one attribute must match criteria

            if operator == '=':

                # At least one attribute equals value

                def _innerFunc(prevTag):

                    tagAttributeValues = list(prevTag.attributesDict.values())

                    if _attributeValue in tagAttributeValues:

                        # Matched on an attribute containing desired value
                        return [prevTag]

                    return []

                return _innerFunc

            elif _operator == '!=':

                # At least one attribute does NOT equal value

                def _innerFunc(prevTag):

                    tagAttributeValues = list(prevTag.attributesDict.values())

                    # Must have at least one value to compare, or no match
                    if len(tagAttributeValues) > 0 and _attributeValue not in tagAttributeValues:

                        # Matched on an attribute containing desired value
                        return [prevTag]

                    return []

                return _innerFunc

            elif _operator == '<':

                # At least one attribute has value less than some number

                return _mk_helper_float_comparison_filter_wildcard( _attributeValue, lambda tagAttrValueFloat, testAttrValueFloat : bool(tagAttrValueFloat < testAttrValueFloat))

            elif _operator == '>':

                # At least one attribute has value greater than some number

                return _mk_helper_float_comparison_filter_wildcard( _attributeValue, lambda tagAttrValueFloat, testAttrValueFloat : bool(tagAttrValueFloat > testAttrValueFloat))

            elif _operator == '<=':

                # At least one attribute has value less than or equal to some number
                return _mk_helper_float_comparison_filter_wildcard( _attributeValue, lambda tagAttrValueFloat, testAttrValueFloat : bool(tagAttrValueFloat <= testAttrValueFloat))

            elif _operator == '>=':

                # At least one attribute has value less than or equal to some number
                return _mk_helper_float_comparison_filter_wildcard( _attributeValue, lambda tagAttrValueFloat, testAttrValueFloat : bool(tagAttrValueFloat >= testAttrValueFloat))

            else:

                # TODO: Reference some code? maybe catch and append?
                raise XPathParseError('Unknown operator requested in comparison: "%s"' %(_operator, ))


        else:

            # TODO: How to test for null?

            # Non-wildcard name and value both defined

            if _operator == '=':

                # Attribute with given name must match

                def _innerFunc(prevTag):

                    if prevTag.getAttribute(_attributeName) == _attributeValue:

                        return [prevTag]

                    return []

                return _innerFunc

            elif _operator == '!=':

                # Attribute must exist, but value must not match

                def _innerFunc(prevTag):

                    if prevTag.hasAttribute(_attributeName) is False:

                        # No such attribute, skip
                        return []

                    if prevTag.getAttribute(_attributeName) == _attributeValue:

                        return []

                    return [prevTag]

                return _innerFunc

            elif _operator == '<':

                # Attribute must exist, value must be less than reference

                return _mk_helper_float_comparison_filter_named(_attributeName, _attributeValue, lambda tagAttrValueFloat, testAttrValueFloat : bool(tagAttrValueFloat < testAttrValueFloat))

            elif _operator == '>':

                # Attribute must exist, has value greater than some number

                return _mk_helper_float_comparison_filter_named(_attributeName, _attributeValue, lambda tagAttrValueFloat, testAttrValueFloat : bool(tagAttrValueFloat > testAttrValueFloat))

            elif _operator == '<=':

                # Attribute must exist, has value less than or equal to some number
                return _mk_helper_float_comparison_filter_named(_attributeName, _attributeValue, lambda tagAttrValueFloat, testAttrValueFloat : bool(tagAttrValueFloat <= testAttrValueFloat))

            elif _operator == '>=':

                # Attribute must exist, has value less than or equal to some number
                return _mk_helper_float_comparison_filter_named(_attributeName, _attributeValue, lambda tagAttrValueFloat, testAttrValueFloat : bool(tagAttrValueFloat >= testAttrValueFloat))

            else:

                # TODO: Reference some code? maybe catch and append?
                raise XPathParseError('Unknown operator requested in comparison: "%s"' %(_operator, ))


# Assemble all known tag operation prefixes (e.x. the 'parent' in 'parent::tr')
TAG_OPERATION_PREFIX_INFOS = {}

# TODO: Do suffixes as well

TAG_OPERATION_PREFIX_INFOS['parent'] = {
    'findTagFunc' : _mk_xpath_op_filter_by_parent_tagname_one_level_function,
}
TAG_OPERATION_PREFIX_INFOS['ancestor'] = {
    'findTagFunc' : _mk_xpath_op_filter_by_ancestor_tagname_multi_level_function,
}
TAG_OPERATION_PREFIX_INFOS['ancestor-or-self'] = {
    'findTagFunc' : _mk_xpath_op_filter_by_ancestor_or_self_tagname_multi_level_function,
}
TAG_OPERATION_PREFIX_INFOS['descendant'] = {
    'findTagFunc' : _mk_xpath_op_filter_by_tagname_multi_level_function,
}
TAG_OPERATION_PREFIX_INFOS['descendant-or-self'] = {
    'findTagFunc' : _mk_xpath_op_filter_by_tagname_multi_level_function_or_self,
}
TAG_OPERATION_PREFIX_INFOS['child'] = {
    'findTagFunc' : _mk_xpath_op_filter_by_tagname_one_level_function,
}
TAG_OPERATION_PREFIX_INFOS['self'] = {
    # Just return the prevTag, we must use a function creator here per pattern though, so double lambda!
    'findTagFunc' : lambda tagName : lambda prevTag : prevTag,
}

TAG_OPERATION_PREFIX_POSSIBILITIES_STR = ''

_TAG_OPERATION_PREFIX_POSSIBILITIES_TMP_LST = []
for key, info in TAG_OPERATION_PREFIX_INFOS.items():

    # Support both case of alpha, or dash if in the name
    regexStr = ''.join( [ ch != '-' and ('[' + ch + ch.upper() + ']') or ('[\\-]') for ch in key ] )
    _TAG_OPERATION_PREFIX_POSSIBILITIES_TMP_LST.append(regexStr)

TAG_OPERATION_PREFIX_POSSIBILITIES_STR = '|'.join(_TAG_OPERATION_PREFIX_POSSIBILITIES_TMP_LST)
del _TAG_OPERATION_PREFIX_POSSIBILITIES_TMP_LST

NEXT_TAG_OPERATION_RE = re.compile(r'''^[ \t]*(?P<lead_in>[/]{1,2})[ \t]*(?P<full_tag>(((?P<prefix>%s))[:][:]){0,1}(?P<tagname>[\*]|([a-zA-Z_][a-zA-Z0-9_]*))([:][:](?P<suffix>[a-zA-Z][a-zA-Z0-9_]*([\(][ \t]*[\)]){0,1})){0,1})''' %(TAG_OPERATION_PREFIX_POSSIBILITIES_STR, ))

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
        self.orderedOperations = self._parseXPathStrIntoOperations()


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

            if issubclass(orderedOperation.__class__, ComplexBody):

                # We have a complex body, unroll it into operations

                nextCollection = TagCollection()

                for thisTag in curCollection:

                    thisBodyOperations = orderedOperation.evaluateBodyToOperations(thisTag)

                    thisTagAsCollection = TagCollection( [ thisTag ] )

                    for thisBodyOperation in thisBodyOperations:

                        thisResultCollection = thisBodyOperation.applyFunction( thisTagAsCollection )

                        nextCollection += thisResultCollection

                if len( nextCollection ) == 0:

                    # TODO: Why create fresh?
                    return TagCollection()

                curCollection = nextCollection

            else:

                thisResultCollection = orderedOperation.applyFunction( curCollection )

                if len(thisResultCollection) == 0:

                    # TODO: Why create fresh?
                    return TagCollection()

                curCollection = thisResultCollection

        return curCollection


    def _parseXPathStrIntoOperations(self):
        '''
            _parseXPathStrIntoOperations - INTERNAL - Processes the XPath string of this object into operations,

                and sets them on this object.
        '''

        # Bring into local namespace
        nextTagOperationRE = NEXT_TAG_OPERATION_RE
        bracketSubsetRE = BRACKETED_SUBSET_RE

        remainingStr = self.xpathStr[:].strip()

        if DEBUG is True:
            print ( "Parsing xpath str: %s\n----------------------\n\n" %( repr(remainingStr), ))

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

            thisTagPrefix = thisGroupDict['prefix'] or None
            if thisTagPrefix:
                thisTagPrefix = thisTagPrefix.strip().lower()
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
                thisXPathPortion += remainingStr[ : endMatchIdx ]
                remainingStr = remainingStr[ endMatchIdx : ].strip()

            # TODO: Evaluate this next block, is it still correct?
            if thisLeadIn == '//':
                # TODO: unofficial fallback operations on the double '/' ?

                if isFirst is False:
                    thisOperationFindTagFunc = _mk_xpath_op_filter_by_tagname_multi_level_function(thisTagName)
                else:
                    thisOperationFindTagFunc = _mk_xpath_op_filter_by_tagname_multi_level_function_or_self(thisTagName)

            else:
                # Default with no prefix or suffix (TODO: Any impossible prefix + suffix combinations that break this pattern?)
                if isFirst is False:
                    thisOperationFindTagFunc = _mk_xpath_op_filter_by_tagname_one_level_function(thisTagName)
                else:
                    thisOperationFindTagFunc = _mk_xpath_op_filter_by_tagname_one_level_function_or_self(thisTagName)

            if (thisTagSuffix or '').replace(' ', '') == 'node()':

                if thisTagName == 'child':
                    thisTagName = '*'

            if thisTagPrefix:

                tagPrefixInfo = TAG_OPERATION_PREFIX_INFOS[thisTagPrefix]
                newFindFunc = tagPrefixInfo['findTagFunc']
                if newFindFunc is not None:
                    thisOperationFindTagFunc = newFindFunc(thisTagName)

                if False:

                    # Should never happen
                    # TODO: Can we bring back this error handling? The special parsing stuff removes it

                    raise XPathParseError('Unhandled special tag prefix "%s" in "%s" at "%s"' %(thisTagPrefix, thisTagName, thisXPathPortion) )

            #XXX: NEEDED? # Check if we matched a trailing slash, if so reduce one from our index
            #if thisNoInnerText == '/':
            #    endMatchIdx -= 1

            #thisXPathPortion = remainingStr[ : endMatchIdx ]

            # XXX: Create an XPathOperation from this function

            # TODO: How much of this portion is needed?
            thisXPathOperation = XPathOperation( thisOperationFindTagFunc, thisXPathPortion )

            orderedOperations.append( thisXPathOperation )

            # XXX: Test inner body
            while thisInnerStr:

                # TODO: On an empty inner bracket, this will fail when it should be a no-op

                didMatch = False

                complexBody = parseBodyStringIntoComplexBody(thisInnerStr)
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
                    remainingStr = remainingStr[ endMatchIdx : ].strip()


            if DEBUG is True:
                print ( ' Parsed line: %s\n   lead =\t%-8s\n   tagn =\t%-20s\n   inner =\t%-50s\n\n' %( \
                        repr(thisXPathPortion), repr(thisLeadIn), repr(thisTagName), repr(thisInnerStr), \
                    ) \
                )

            # isFirst - Completed first round, set flag to False henceforth
            isFirst = False

            if not remainingStr:
                keepGoing = False


        return orderedOperations


# vim: set ts=4 st=4 sw=4 expandtab :
