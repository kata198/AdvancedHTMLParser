# Copyright (c) 2015 Tim Savannah under LGPLv3. 
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

INVISIBLE_ROOT_TAG_START = '<%s>' %(INVISIBLE_ROOT_TAG,)
INVISIBLE_ROOT_TAG_END = '</%s>' %(INVISIBLE_ROOT_TAG,)


