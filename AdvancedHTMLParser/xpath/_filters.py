'''
    Copyright (c) 2019 Timothy Savannah under terms of LGPLv3. All Rights Reserved.

    See LICENSE (https://gnu.org/licenses/lgpl-3.0.txt) for more information.

    See: https://github.com/kata198/AdvancedHTMLParser for full information


    ==INTERNAL==

    xpath._filters.py - Internal module for holding xpath filtering items
'''
# vim: set ts=4 sw=4 st=4 expandtab :

from ..Tags import TagCollection

__all__ = ( \
    '_mk_xpath_op_filter_by_tagname_one_level_function', '_mk_xpath_op_filter_by_tagname_one_level_function_or_self', \
    '_mk_xpath_op_filter_by_tagname_multi_level_function', '_mk_xpath_op_filter_by_tagname_multi_level_function_or_self', \
    '_mk_xpath_op_filter_by_parent_tagname_one_level_function', \
    '_mk_xpath_op_filter_by_ancestor_tagname_multi_level_function', '_mk_xpath_op_filter_by_ancestor_or_self_tagname_multi_level_function', \
    '_mk_xpath_op_filter_tag_is_nth_child_index', \
    '_mk_helper_float_comparison_filter_named', '_mk_helper_float_comparison_filter_wildcard', \
)

def _mk_xpath_op_filter_by_tagname_one_level_function(tagName):
    '''
        _mk_xpath_op_filter_by_tagname_one_level_function - Filters one level of descent, by tag name or wildcard.

            This function will create and return the function to be used with the associated XPathOperation.


            ==INTERNAL==


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




# vim: set ts=4 sw=4 st=4 expandtab :
