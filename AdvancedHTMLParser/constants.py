# Copyright (c) 2015, 2017 Tim Savannah under LGPLv3. 
#  See LICENSE (https://gnu.org/licenses/lgpl-3.0.txt) for more information.
#   Constants in AdvancedHTMLParser

from .conversions import convertToIntOrNegativeOneIfUnset, convertToPositiveInt, convertPossibleValues

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

# TODO: Need to remove "value" from all tags


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
    # button->form another form
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
    # TODO: form->autocomplete returns "yes" or "no" via dot-access, but sets the html attribute to whatever
    # TODO: form->encoding is an alias for "enctype"
    # TODO: form->method sets whatever value in html attribute, but on access forces to "get" or "post"
    'form'     : { 'acceptCharset', 'action', 'autocomplete', 'enctype', 'method', 'noValidate', 'target',
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
    # TODO: sandbox is a special DOMTokenList (like classList), but we don't yet support that.
    'iframe'   : { 'align', 'frameBorder', 'height', 'marginHeight', 'marginWidth', 'sandbox',
                   'scrolling', "src", "srcdoc", 'width', },
    'img'   : { 'align', 'alt', 'border', 'crossOrigin', 'height', 'hspace', 'isMap', 'longDesc', 'sizes',
                'src', 'srcset', 'useMap', 'vspace', 'width'},
    # TODO: input->autocomplete returns "yes" or "no" via dot-access, invalud empty str, but sets the html attribute to whatever
    # TODO: input->form dot-access returns the parent form element, but has no html attribute equivilant
    # TODO: input->formAction, formEnctype default to current url but we don't know it
    # TODO: input->list default is null
    # TODO: input->maxLength throws exception when negative value instead of default
    # TODO: input->size seems to have some sort of default value in firefox (20?)
    # TODO: input->size is an integer through dot-access, also throws exception on invalid value
    # TODO: input->size has a minimum value of 1
    # TODO: input->src is a url can be realitve and we don't know the current url
    'input' : { 'accept', 'align', 'alt', 'autocomplete', 'autofocus', 'checked', 'dir', 'disabled', 'formAction', 'formEnctype',
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
    # TODO: output->form another form
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
    # TODO: another form
    'select'   : { 'autofocus', 'disabled', 'form', 'multiple', 'required', 'size', },
    # TODO: sizes list
    'source'   : { 'src', 'srcdest', 'media', 'sizes', 'type', },
    # TODO: style has "scoped" in w3 but not firefox
    'style'    : { 'media', 'scoped', 'type', },
    'table'    : { 'align', 'bgcolor', 'border', 'cellPadding', 'cellSpacing', 'frame', 'rules', 'summary', 'width', },
    # TODO: tbody has "char" and "charoff" in w3 but not firefox
    'tbody'    : { 'align', 'char', 'charoff', 'vAlign', },
    # TODO: td has "char" and "charoff" in w3 but not firefox
    # TODO: td has "colspan" minimum 1 but puts whatever in html attribute
    # TODO: td has "rowspan" minimum 1 but puts whatever in html attribute
    'td'       : { 'abbr', 'align', 'axis', 'bgcolor', 'char', 'charoff', 'colSpan', 'headers', 'height', 'noWrap',
                   'rowSpan', 'scope', 'vAlign', 'width',  },
    # TODO: "cols" is numeric
    # TODO: form
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
    # TODO: "kind" has default 'subtitles'
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
TAG_ITEM_ATTRIBUTE_LINKS = { 'id', 'name', 'title', 'dir', 'align', 'tabIndex', 'value', 'className', 
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

# These attributes can have a special value
TAG_ITEM_ATTRIBUTES_SPECIAL_VALUES = {
    'tabIndex' : lambda em : convertToIntOrNegativeOneIfUnset(em.getAttribute('tabindex', None)),
      # span - Default (not present) value is "1", invalids are 0
    'span'     : lambda em : convertToPositiveInt(em.getAttribute('span', 1), invalidDefault=0),
    'colSpan'     : lambda em : convertToPositiveInt(em.getAttribute('colspan', 1), invalidDefault=1),
    'rowSpan'     : lambda em : convertToPositiveInt(em.getAttribute('rowspan', 1), invalidDefault=1),
    'hspace'     : lambda em : convertToPositiveInt(em.getAttribute('hspace', 0), invalidDefault=0),
    'vspace'     : lambda em : convertToPositiveInt(em.getAttribute('vspace', 0), invalidDefault=0),
    # maxLength needs to throw exception on invalid
    'maxLength'     : lambda em : convertToPositiveInt(em.getAttribute('maxlength', -1), invalidDefault=-1),
    # size throws exception on invalid value, and a minimum of 1
    'size'     : lambda em : convertToPositiveInt(em.getAttribute('size', 20), invalidDefault=20),
    # crossOrigin is "use-credentials" or "anonymous" (all invalid values go to anonymous) default null
    'crossOrigin' : lambda em : convertPossibleValues(em.getAttribute('crossorigin', None), POSSIBLE_VALUES_CROSS_ORIGIN, invalidDefault="anonymous", emptyValue=None)
}

