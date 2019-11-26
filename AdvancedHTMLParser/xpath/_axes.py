'''
    Copyright (c) 2019 Timothy Savannah under terms of LGPLv3. All Rights Reserved.

    See LICENSE (https://gnu.org/licenses/lgpl-3.0.txt) for more information.

    See: https://github.com/kata198/AdvancedHTMLParser for full information


    ==INTERNAL==

    xpath._axes.py - Internal module for handling axes
'''
# vim: set ts=4 sw=4 st=4 expandtab :

from ._filters import ( \
    _mk_xpath_op_filter_by_tagname_one_level_function, _mk_xpath_op_filter_by_tagname_one_level_function_or_self, \
    _mk_xpath_op_filter_by_tagname_multi_level_function, _mk_xpath_op_filter_by_tagname_multi_level_function_or_self, \
    _mk_xpath_op_filter_by_parent_tagname_one_level_function, \
    _mk_xpath_op_filter_by_ancestor_tagname_multi_level_function, _mk_xpath_op_filter_by_ancestor_or_self_tagname_multi_level_function, \
    _mk_xpath_op_filter_tag_is_nth_child_index, \
    _mk_helper_float_comparison_filter_named, _mk_helper_float_comparison_filter_wildcard, \
)
from .null import Null

__all__ = ('TAG_OPERATION_AXES_TO_FIND_TAG_FUNC_GEN', 'TAG_OPERATION_AXES_POSSIBILITIES_REGEX_STR')

# Tag axes (prefix, e.x. parent::tr the "parent" is it) to function which will take tagName (or wildcard)
#  and generate a function to search current/previous set of tags and return the new tags to process within the body
TAG_OPERATION_AXES_TO_FIND_TAG_FUNC_GEN = {}


TAG_OPERATION_AXES_TO_FIND_TAG_FUNC_GEN['parent'] = _mk_xpath_op_filter_by_parent_tagname_one_level_function

TAG_OPERATION_AXES_TO_FIND_TAG_FUNC_GEN['ancestor'] = _mk_xpath_op_filter_by_ancestor_tagname_multi_level_function
TAG_OPERATION_AXES_TO_FIND_TAG_FUNC_GEN['ancestor-or-self'] = _mk_xpath_op_filter_by_ancestor_or_self_tagname_multi_level_function

TAG_OPERATION_AXES_TO_FIND_TAG_FUNC_GEN['descendant'] = _mk_xpath_op_filter_by_tagname_multi_level_function
TAG_OPERATION_AXES_TO_FIND_TAG_FUNC_GEN['descendant-or-self'] = _mk_xpath_op_filter_by_tagname_multi_level_function_or_self

TAG_OPERATION_AXES_TO_FIND_TAG_FUNC_GEN['child'] = _mk_xpath_op_filter_by_tagname_one_level_function

# 'self' - Just return the prevTag, we must use a function creator here per pattern though, so double lambda!
TAG_OPERATION_AXES_TO_FIND_TAG_FUNC_GEN['self'] = lambda tagName : lambda prevTag : prevTag


def _mkRegexStrAllAxesPossibilities():
    '''
        _mkRegexStrAllAxesPossibilities - Make a regular expression string to match entire entities in our supported list

          of axes, case insensitively.


            @return <str> - A string for use within a regular expression
    '''
    possibilitiesStr = ''

    tmpList = []
    for key, info in TAG_OPERATION_AXES_TO_FIND_TAG_FUNC_GEN.items():

        # Support both case of alpha, or dash if in the name
        regexStr = ''.join( [ ch != '-' and ('[' + ch + ch.upper() + ']') or ('[\\-]') for ch in key ] )
        tmpList.append(regexStr)

    possibilitiesStr = '|'.join(tmpList)

    # NOTE: Probably do not need this explicit delete anymore, since not in the global scope.
    del tmpList

    return possibilitiesStr


# TAG_OPERATION_AXES_POSSIBILITIES_REGEX_STR - String for inclusion in regex for case-insensitive axes matching
TAG_OPERATION_AXES_POSSIBILITIES_REGEX_STR = _mkRegexStrAllAxesPossibilities()


# vim: set ts=4 sw=4 st=4 expandtab :
