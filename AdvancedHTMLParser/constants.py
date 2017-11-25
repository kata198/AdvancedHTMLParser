# Copyright (c) 2015, 2017 Tim Savannah under LGPLv3. 
#  See LICENSE (https://gnu.org/licenses/lgpl-3.0.txt) for more information.
#   Constants in AdvancedHTMLParser

# These tags are always self-closing, whether given that way or not.
IMPLICIT_SELF_CLOSING_TAGS = set(['meta', 'link', 'input', 'img', 'hr', 'br'])

# These tags have preformatted content and will not be modified at all
PREFORMATTED_TAGS = set(['pre', 'code'])

# These tags will not have content modified, except for first-and-last line indentation
PRESERVE_CONTENTS_TAGS = set(['script', 'pre', 'code', 'style'])

# Tag name for a "transparent" root node. Used if there are multiple nodes at root level as an internal placeholder.
#  I.E. an inomplete page, or an ajax request. @see Parser.AdvancedHTMLParser.getRootNodes
INVISIBLE_ROOT_TAG = 'xxxblank'

# Start tag used on invisible root tag
INVISIBLE_ROOT_TAG_START = '<%s>' %(INVISIBLE_ROOT_TAG,)
# End tag used on invisible root tag
INVISIBLE_ROOT_TAG_END = '</%s>' %(INVISIBLE_ROOT_TAG,)

# Tag names with attributes that are not common to all, but exist on certain elements
TAG_NAMES_TO_ADDITIONAL_ATTRIBUTES = { 
    'input' : {'checked', 'onsearch', 'onchange', 'oncontextmenu', 'oninput', 'oninvalid', 'onreset', 'onselect'},
    'option': {'selected', },
    'body'  : {'onafterprint', 'onbeforeprint', 'onbeforeunload', 'onerror', 'onhashchange', 'onload', 'onmessage', \
                'onoffline', 'ononline', 'onpagehide', 'onpageshow', 'onpopstate', 'onresize', 'onstorage', 'onunload'},
    'form'  : {'onblur', 'onchange', 'oncontextmenu', 'onfocus', 'oninput', 'oninvalid', 'onreset', 'onsearch', 'onselect', 'onsubmit'},
    'menu'  : {'onshow', },
    'a'     : {'href', 'target', },
    'details' : {'ontoggle', },
}

# These all inherit the special attributes from input
for otherInputName in ('button', 'select', 'option'):
    TAG_NAMES_TO_ADDITIONAL_ATTRIBUTES['button'] = TAG_NAMES_TO_ADDITIONAL_ATTRIBUTES['input']

# Inherits special attributes from input plus onsubmit
TAG_NAMES_TO_ADDITIONAL_ATTRIBUTES['submit'] = TAG_NAMES_TO_ADDITIONAL_ATTRIBUTES['input'].union('onsubmit')

# Javascript attributes common to all elements
COMMON_JAVASCRIPT_ATTRIBUTES = { 'onkeydown', 'onkeyup', 'onkeypress', 'onfocus', 'onblur', 'onselect', 'oncontextmenu', \
                                    'onclick', 'ondblclick', 'onmousedown', 'onmousemove', 'onmouseout', 'onmouseover', \
                                    'onmouseup', 'onmousewheel', 'onwheel', 'oncopy', 'onpaste', 'oncut', \
                                    'ondrag', 'ondragend', 'ondragenter', 'ondragleave', 'ondragover', 'ondragstop', 'ondrop', 'onscroll',
                                    'onchange', 
}

# All javascript attributes known by AdvancedHTMLParser
ALL_JAVASCRIPT_EVENT_ATTRIBUTES = COMMON_JAVASCRIPT_ATTRIBUTES.union( 
    set([value for values in TAG_NAMES_TO_ADDITIONAL_ATTRIBUTES.values() for value in values if value.startswith('on')]) 
)

# object-access that link directly to an attribute on the tag
TAG_ITEM_ATTRIBUTE_LINKS = { 'id', 'name', 'title', 'dir', 'align', 'tabIndex', 'value', 'className', 
    'hidden', }

# Add all javascript event attributes
TAG_ITEM_ATTRIBUTE_LINKS.update(COMMON_JAVASCRIPT_ATTRIBUTES)

# These attributes have a different object-access than their name
TAG_ITEM_CHANGE_NAME_FROM_ITEM = {
    'tabIndex' : 'tabindex',
    'className' : 'class',
}

# These attributes are binary (only accept true/false)
TAG_ITEM_BINARY_ATTRIBUTES = { 'hidden', 'checked', 'selected' }

# The opposite of TAG_ITEM_CHANGE_NAME_FROM_ITEM, for going from the attribute name to the object-access name
TAG_ITEM_CHANGE_NAME_FROM_ATTR = { val : key for key, val in TAG_ITEM_CHANGE_NAME_FROM_ITEM.items() }

# These attributes can have a special value
TAG_ITEM_ATTRIBUTES_SPECIAL_VALUES = {
    'tabIndex' : lambda em : _attr_value_int_or_negative_one_if_unset(em.getAttribute('tabindex', None))
}

def _attr_value_int_or_negative_one_if_unset(val):
    '''
        _attr_value_int_or_negative_one_if_unset - Converts a value
        
        @param val <int/str/None> - Value
        
        Takes a value, if not set or not an integer, returns -1
    '''
    if val in (None, ''):
        return -1
    try:
        return int(val)
    except:
        return -1

