'''
    Copyright (c) 2015, 2017 Tim Savannah under LGPLv3. All Rights Reserved.

    See LICENSE (https://gnu.org/licenses/lgpl-3.0.txt) for more information.


    Constants in AdvancedHTMLParser
'''

from .conversions import ( convertToIntOrNegativeOneIfUnset, convertToPositiveInt,
    convertPossibleValues, convertToIntRange, convertToIntRangeCapped, EMPTY_IS_INVALID
)

from .exceptions import IndexSizeErrorException

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
    'a'     : { 'href', 'target', },
    'area'  : { 'alt', 'coords', 'download', 'href', 'rel', 'shape', 'target', },
    'audio' : { 'autoplay', 'controls', 'loop', 'muted', 'preload', 'src', },
    'base'  : { 'href', 'target' },
    'basefont' : { 'color', 'face', 'size'},
    'bdo'   : { 'dir', },
    'blockquote' : { 'cite', },
    'body'  : { 'bgcolor', 'background', 'vlink', 'alink', 'link', 'onafterprint', 'onbeforeprint', \
                'onbeforeunload', 'onerror', 'onhashchange', 'onload', 'onmessage', \
                'onoffline', 'ononline', 'onpagehide', 'onpageshow', 'onpopstate', 'onresize', 'onstorage', 'onunload' },
    'button' : { 'autofocus', 'disabled', 'form', 'formAction', 'formEnctype', 'formMethod', 'formNoValidate', 'formTarget', 'type', 'value', },
    'canvas' : { 'height', 'width'},
    'caption': { 'align', },
    'col'    : { 'span', 'valign', 'width', },  # TODO: col.span = 0 will set span="0" but col.span still returns 1 in firefox (we return 0)
    'colgroup' : { 'align', 'span', 'valign', 'width' },
    'data'   : { 'value', },
    'del'    : { 'cite', 'dateTime'},
    'details' : { 'ontoggle', },
    'dir'    : { 'compact', },
    'div'    : { 'align', },
    'embed'  : { 'height', 'width', 'src', 'type', },
    'fieldset' : { 'form', },
    'font'     : { 'color', 'face', 'size', },
    # TODO: form->action defaults to current url, but we don't have such info
    'form'     : { 'acceptCharset', 'action', 'autocomplete', 'encoding', 'enctype', 'method', 'noValidate', 'target',
        'onblur', 'onchange', 'oncontextmenu', 'onfocus', 'oninput', 'oninvalid', 'onreset', 'onsearch', 'onselect', 'onsubmit' },
    # TODO: frame->longDesc is a url, and relative urls have an absolute value in dot-access, but we don't know the url
    # TODO: frame->src is a url, and relative urls have an absolute value in dot-access, but we don't know the url
    'frame'    : { 'frameBorder', 'longDesc', 'marginHeight', 'marginWidth', 'noResize', 'scrolling', 'src', },
    'frameset' : { 'cols', 'rows', },
    'h1'       : { 'align', },
    'h2'       : { 'align', },
    'h3'       : { 'align', },
    'h4'       : { 'align', },
    'h5'       : { 'align', },
    'h6'       : { 'align', },
    # TODO: head->profile is listed by w3 as a pre-html5 attribute, but isn't implemented in firefox
    'head'     : { 'profile', },
    'hr'       : { 'align', 'noShade', 'size', 'width', },
    # TODO: w3 specifies html as having "xmlns" but firefox does not support such attribute.
    'html'     : { 'xmlns', },
    'iframe'   : { 'align', 'frameBorder', 'height', 'marginHeight', 'marginWidth', 'sandbox',
                   'scrolling', "src", "srcdoc", 'width', },
    'img'   : { 'align', 'alt', 'border', 'crossOrigin', 'height', 'hspace', 'isMap', 'longDesc', 'sizes',
                'src', 'srcset', 'useMap', 'vspace', 'width'},
    # TODO: input->formAction, formEnctype default to current url but we don't know it
    # TODO: input->list default is null
    # TODO: input->size seems to have some sort of default value in firefox (20?)
    # TODO: input->size is an integer through dot-access, also throws exception on invalid value
    # TODO: input->size has a minimum value of 1
    # TODO: input->src is a url can be realitve and we don't know the current url
    'input' : { 'accept', 'align', 'alt', 'autocomplete', 'autofocus', 'checked', 'dir', 'disabled', 'form', 'formAction', 'formEnctype',
                'formAction', 'formEnctype', 'formMethod', 'formNoValidate', 'formTarget', 'list', 'max', 'maxLength',
                'min', 'multiple', 'pattern', 'placeholder', 'readOnly',  'required', 'size', 'src',
                'step', 'type', 'value', 'width', },
    'ins'   : { 'cite', 'dateTime', },
    'label' : { 'for', 'form', },
    'legend': { 'align', },
    'li'    : { 'type', 'value', },
    # TODO: link->sizes is only for type="icon" and is DOMTokenList
    'link'  : { 'charset', 'crossOrigin', 'href', 'hreflang', 'media', 'rel', 'rev', 'sizes', 'target', 'type', },
    'menu'  : { 'label', 'type', 'onshow', },
    # TODO: menuitem has "default" but not implemented in firefox
    # TODO: menuitem->icon is url
    'menuitem' : { 'checked', 'disabled', 'icon', 'label', 'radiogroup', 'type', },
    # TODO:  meta->charset is defined by w3 but implemented in firefox
    'meta'   : { 'charset', 'content', 'httpEquiv', 'scheme', },
    # TODO:  meter->form is defined by w3 but implemented in firefox
    # TODO:  meter->high, low, max, min, optimum is float, infinite range
    # TODO:  all but optimum are default 0, optimum is default 1/2 of (max - min)
    'meter'  : { 'form', 'high', 'low', 'max', 'min', 'optimum', 'value' },
    # TODO: object->archive is url
    # TODO: object->classid is w3 not firefox
    'object' : { 'align', 'archive', 'border', 'classid', 'codeBase', 'codeType', 'data', 'declare', 'form',
                 'height', 'hspace', 'standby', 'type', 'useMap', 'vspace', 'width', },
    # TODO: ol->start is a number any range, and 0 for invalid
    'ol'     : { 'compact', 'reversed', 'start', 'type', },
    'optgroup' : { 'disabled', 'label', },
    'option' : { 'disabled', 'label', 'selected', 'value', },
    'output' : { 'for', 'form', },
    'p'      : { 'align', },
    'param'  : { 'type', 'value', 'valueType', },
    'pre'    : { 'width', },
    # TODO: output->progress puts in html attr whatever value for "max" in, but on dot-access invalid and minimum are 1
    'progress' : { 'max', 'value', },
    # TODO: q->cite is a url
    'q'        : { 'cite', },
    # TODO: script->async is boolean, but default is true
    # TODO: script has "xml:space" but not supported in firefox
    'script'   : { 'async', 'charset', 'defer', 'src', 'type',  },
    'select'   : { 'autofocus', 'disabled', 'form', 'multiple', 'required', 'size', },
    # TODO: sizes list
    'source'   : { 'src', 'srcdest', 'media', 'sizes', 'type', },
    # TODO: style has "scoped" in w3 but not firefox
    'style'    : { 'media', 'scoped', 'type', },
    'table'    : { 'align', 'bgcolor', 'border', 'cellPadding', 'cellSpacing', 'frame', 'rules', 'summary', 'width', },
    # TODO: tbody has "char" and "charoff" in w3 but not firefox
    'tbody'    : { 'align', 'char', 'charoff', 'vAlign', },
    # TODO: td has "char" and "charoff" in w3 but not firefox
    'td'       : { 'abbr', 'align', 'axis', 'bgcolor', 'char', 'charoff', 'colSpan', 'headers', 'height', 'noWrap',
                   'rowSpan', 'scope', 'vAlign', 'width',  },
    # TODO: "cols" is numeric
    'textarea' : { 'autofocus', 'cols', 'dirname', 'disabled', 'form', 'maxLength', 'placeholder',
                   'readOnly', 'required', 'rows', 'wrap', },
    'tfoot'    : { 'align', 'char', 'charoff', 'vAlign', },
    # TODO: th->sorted in w3 but not firefox
    'th'       : { 'abbr', 'align', 'axis', 'bgcolor', 'char', 'charoff', 'colSpan', 'headers', 'height', 'noWrap',
                   'rowSpan', 'scope', 'sorted', 'vAlign', 'width', },
    'thead'    : { 'align', 'char', 'charoff', 'vAlign', },
    'time'     : { 'dateTime', },
    'tr'       : { 'align', 'bgcolor', 'char', 'charoff', 'vAlign', },
    # TODO: track has 'default' but pretty sure it's used elsewhere (not firefox impl) which is NOT binary
    'track'    : { 'default', 'kind', 'label', 'src', 'srclang', },
    'ul'       : { 'compact', 'type', },
    # TODO: poster is url
    'video'    : { 'autoplay', 'controls', 'height', 'loop', 'muted', 'poster', 'preload', 'src', 'width', },


    # TODO: Some items in firefox have "defaultValue" and "defaultChecked" (inputs and inputlike)
}

COMMON_INPUT_ATTRS = { 'value', 'checked', 'onsearch', 'onchange', 'oncontextmenu', 'oninput', 'oninvalid', 'onreset', 'onselect'}

# These all inherit the special attributes from input
for otherInputName in ('input', 'button', 'select', 'option'):
    if otherInputName not in TAG_NAMES_TO_ADDITIONAL_ATTRIBUTES:
        TAG_NAMES_TO_ADDITIONAL_ATTRIBUTES[otherInputName] = COMMON_INPUT_ATTRS.copy()
    else:
        TAG_NAMES_TO_ADDITIONAL_ATTRIBUTES[otherInputName].update(COMMON_INPUT_ATTRS.copy())

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
TAG_ITEM_ATTRIBUTE_LINKS = { 'id', 'name', 'title', 'dir', 'align', 'tabIndex', 'className',
    'hidden', 'spellcheck', 'lang', }

# Add all javascript event attributes
TAG_ITEM_ATTRIBUTE_LINKS.update(COMMON_JAVASCRIPT_ATTRIBUTES)

# These attributes have a different object-access than their name
TAG_ITEM_CHANGE_NAME_FROM_ITEM = {
    'tabIndex' : 'tabindex',
    'className' : 'class',
    'vAlign' : 'valign',
    'dateTime' : 'datetime',
    'acceptCharset' : 'accept-charset',
    'noValidate' : 'novalidate',
    'frameBorder' : 'frameborder',
    'longDesc' : 'longdesc',
    'marginHeight' : 'marginheight',
    'marginWidth'  : 'marginWidth',
    'noResize' : 'noresize',
    'noShade'  : 'noshade',
    'frameBorder' : 'frameborder',
    'crossOrigin' : 'crossorigin',
    'isMap' : 'ismap',
    'useMap' : 'usemap',
    'dir'    : 'dirname',
    'formAction' : 'formaction',
    'formEnctype' : 'formenctype',
    'formMethod'  : 'formmethod',
    'formNoValidate' : 'formnovalidate',
    'formTarget' : 'formtarget',
    'maxLength'  : 'maxlength',
    'readOnly'   : 'readonly',
    'httpEquiv'  : 'http-equiv',
    'codeBase'   : 'codebase',
    'codeType'   : 'codetype',
    'valueType'  : 'valuetype',
    'cellPadding' : 'cellpadding',
    'cellSpacing' : 'cellspacing',
    'colSpan'     : 'colspan',
    'noWrap'      : 'nowrap',
    'rowSpan'     : 'rowspan',
    'encoding'    : 'enctype',

}

# These attributes are binary (only accept true/false)
TAG_ITEM_BINARY_ATTRIBUTES = { 'hidden', 'checked', 'selected',
    'autoplay', 'controls', 'loop', 'muted',
    'compact', 'novalidate', 'noresize', 'autofocus', 'disabled', 'formnovalidate', 'multiple', 'readOnly', 'required',
    'declare', 'reversed', 'async', 'defer', 'nowrap', 'default',
    }

# These attributes are binary for dot-access, but have the value "true" or "false" in the HTML representation
TAG_ITEM_BINARY_ATTRIBUTES_STRING_ATTR = { 'spellcheck', }

# The opposite of TAG_ITEM_CHANGE_NAME_FROM_ITEM, for going from the attribute name to the object-access name
TAG_ITEM_CHANGE_NAME_FROM_ATTR = { val : key for key, val in TAG_ITEM_CHANGE_NAME_FROM_ITEM.items() }


POSSIBLE_VALUES_CROSS_ORIGIN = ('use-credentials', 'anonymous')

POSSIBLE_VALUES_TRACK__KIND = ( 'captions', 'chapters', 'descriptions', 'metadata', 'subtitles' )


POSSIBLE_VALUES_ON_OFF = ('on', 'off')

POSSIBLE_VALUES_YES_NO = ('yes', 'no')

POSSIBLE_VALUES_FORM_METHOD = ('get', 'post')

def _special_value_rows(em):
    '''
        _special_value_rows - Handle "rows" special attribute, which differs if tagName is a textarea or frameset
    '''
    if em.tagName == 'textarea':
        return convertToIntRange(em.getAttribute('rows', 2), minValue=1, maxValue=None, invalidDefault=2)
    else:
        # frameset
        return em.getAttribute('rows', '')

def _special_value_cols(em):
    '''
        _special_value_cols - Handle "cols" special attribute, which differs if tagName is a textarea or frameset
    '''
    if em.tagName == 'textarea':
        return convertToIntRange(em.getAttribute('cols', 20), minValue=1, maxValue=None, invalidDefault=20)
    else:
        # frameset
        return em.getAttribute('cols', '')

def _special_value_autocomplete(em):
    '''
        handle "autocomplete" property, which has different behaviour for form vs input"
    '''
    if em.tagName == 'form':
        return convertPossibleValues(em.getAttribute('autocomplete', 'on'), POSSIBLE_VALUES_ON_OFF, invalidDefault='on', emptyValue=EMPTY_IS_INVALID)
    # else: input
    return convertPossibleValues(em.getAttribute('autocomplete', ''), POSSIBLE_VALUES_ON_OFF, invalidDefault="", emptyValue='')

def _special_value_size(em):
    '''
        handle "size" property, which has different behaviour for input vs everything else
    '''
    if em.tagName == 'input':
        # TODO: "size" on an input is implemented very weirdly. Negative values are treated as invalid,
        #          A value of "0" raises an exception (and does not set HTML attribute)
        #          No upper limit.
        return convertToPositiveInt(em.getAttribute('size', 20), invalidDefault=20)
    return em.getAttribute('size', '')


class NOT_PROVIDED_TYPE(object):
    '''
        NOT_PROVIDED_TYPE - A type for a singleton which is meant to mean "Argumnent not provided"

            (since None, empty string, etc are legitimate possible values
    '''
    pass

# NOT_PROVIDED - Singleton of NOT_PROVIDED_TYPE, used to indicate that an argument is not provided
NOT_PROVIDED = NOT_PROVIDED_TYPE()

def _special_value_maxLength(em, newValue=NOT_PROVIDED):
    '''
        _special_value_maxLength - Handle the special "maxLength" property

            @param em <AdvancedTag> - The tag element

            @param newValue - Default NOT_PROVIDED, if provided will use that value instead of the

                current .getAttribute value on the tag. This is because this method can be used for both validation

                and getting/setting
    '''

    if newValue is NOT_PROVIDED:
        if not em.hasAttribute('maxlength'):
            return -1

        curValue = em.getAttribute('maxlength', '-1')

        # If we are accessing, the invalid default should be negative
        invalidDefault = -1
    else:
        curValue = newValue

        # If we are setting, we should raise an exception upon invalid value
        invalidDefault = IndexSizeErrorException

    return convertToIntRange(curValue, minValue=0, maxValue=None, emptyValue='0', invalidDefault=invalidDefault)



def _DOMTokenList_type(*args):
    '''
        _DOMTokenList_type - A method which imports and returns SpecialAttributes.DOMTokenList

            for late-binding reasons

            If arguments are passed, will construct a DOMTokenList object, otherwise will return the type itself
    '''
    from .SpecialAttributes import DOMTokenList

    if args:
        return DOMTokenList(*args)

    return DOMTokenList


# IndexSizeError - Singleton for the IndexSizeErrorException type
IndexSizeError = IndexSizeErrorException()

# TODO: Send firefox some bug reports based on below info

# These attributes can have a special value
TAG_ITEM_ATTRIBUTES_SPECIAL_VALUES = {
    'tabIndex' : lambda em : convertToIntOrNegativeOneIfUnset(em.getAttribute('tabindex', None)),
    # TODO: span is minimum 1, but firefox (I think it's a bug) allows you to set to 0, it sets the html text to span="0" but value remains 1. Also, it is clamped at "1000" via dot-access, but the html string will go up to what appears to be a 32-bit variable overflowing
    'span'     : lambda em : convertToIntRangeCapped(em.getAttribute('span', 1), minValue=1, maxValue=1000, invalidDefault=1),
    # TODO: colSpan on invalid in firefox sets HTML attribute text to "0" but returns "1" on JS. We aren't doing the HTML attr portion
    'colSpan'     : lambda em : convertToIntRangeCapped(em.getAttribute('colspan', 1), minValue=1, maxValue=1000, invalidDefault=1),
    # TODO: rowSpan on invalid in firefox sets HTML attribute text to "0" but returns "0" on JS. We aren't doing the HTML attr portion
    'rowSpan'     : lambda em : convertToIntRangeCapped(em.getAttribute('rowspan', 1), minValue=0, maxValue=65534, invalidDefault=0),
    'hspace'     : lambda em : convertToPositiveInt(em.getAttribute('hspace', 0), invalidDefault=0),
    'vspace'     : lambda em : convertToPositiveInt(em.getAttribute('vspace', 0), invalidDefault=0),
    'maxLength'     : _special_value_maxLength,
    # size throws exception on invalid value, and a minimum of 1
    'size'     : _special_value_size,
    # crossOrigin is "use-credentials" or "anonymous" (all invalid values go to anonymous) default null
    'crossOrigin' : lambda em : convertPossibleValues(em.getAttribute('crossorigin', None), POSSIBLE_VALUES_CROSS_ORIGIN, invalidDefault="anonymous", emptyValue=None),
    # autocomplete has different behaviour for "input" vs "form"
    'autocomplete' : _special_value_autocomplete,
    'method' : lambda em : convertPossibleValues(em.getAttribute('method', 'get'), POSSIBLE_VALUES_FORM_METHOD, invalidDefault="get", emptyValue=''),
    'form'   : lambda em : em.getParentElementCustomFilter( lambda em : em.tagName == 'form' ),
    'cols'   : _special_value_cols,
    'rows'   : _special_value_rows,
    'sandbox' : lambda em : _DOMTokenList_type( em.getAttribute('sandbox', '') ),

    # track->kind has a default of "subtitles", an invalid of "metadata", and possible of the list below.
    'kind' : lambda em : convertPossibleValues(em.getAttribute('kind', "subtitles"), POSSIBLE_VALUES_TRACK__KIND, invalidDefault="metadata", emptyValue=EMPTY_IS_INVALID)

}


# TAG_ITEM_ATTRIBUTES_SPECIAL_VALIDATION - These perform a validation step when setting the value via AdvancedTag.${NAME} = something
#    Key should be the . access name, value is a function/lambda which takes the element as first argument, and the new value as the second argument.
TAG_ITEM_ATTRIBUTES_SPECIAL_VALIDATION = {
    'maxLength' : _special_value_maxLength,
}


