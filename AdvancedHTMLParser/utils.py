'''
    Copyright (c) 2015, 2017, 2019 Tim Savannah  under terms of LGPLv3. All Rights Reserved.

    See LICENSE (https://gnu.org/licenses/lgpl-3.0.txt) for more information.


    Some misc utils and regular expressions
'''

import sys
import re

__all__ = ('IE_CONDITIONAL_PATTERN', 'END_HTML', 'START_HTML', 'DOCTYPE_MATCH',
    'stripIEConditionals', 'addStartTag', 'escapeQuotes', 'unescapeQuotes', 'tostr', 'isstr',
    'stripWordsOnly',
)

IE_CONDITIONAL_PATTERN = re.compile('[<][!][-][-][ \t\r\n]*[\[][ \t\r\n]*if.*-->', re.MULTILINE)

END_HTML = re.compile('.*</[ \t\r\n]*[hH][tT][mM][lL][ \t\r\n]*>.*', re.DOTALL)
START_HTML = re.compile('.*<[ \t\r\n]*[hH][tT][mM][lL][ \t\r\n]*>.*', re.DOTALL)

DOCTYPE_MATCH = re.compile('[\n]*[ \t]*(?P<tag><[!][ \t]*[dD][oO][cC][tT][yY][pP][eE].*[>])')

WORDS_ONLY_RE = re.compile('[ ][ ]+')

def stripWordsOnly(contents):
    return WORDS_ONLY_RE.sub(' ', contents.strip())

def stripIEConditionals(contents, addHtmlIfMissing=True):
    '''
        stripIEConditionals - Strips Internet Explorer conditional statements.

        @param contents <str> - Contents String
        @param addHtmlIfMissing <bool> - Since these normally encompass the "html" element, optionally add it back if missing.
    '''
    allMatches = IE_CONDITIONAL_PATTERN.findall(contents)
    if not allMatches:
        return contents

    for match in allMatches:
        contents = contents.replace(match, '')

    if END_HTML.match(contents) and not START_HTML.match(contents):
        contents = addStartTag(contents, '<html>')

    return contents


def addStartTag(contents, startTag):
    '''
        addStartTag - Safetly add a start tag to the document, taking into account the DOCTYPE

        @param contents <str> - Contents
        @param startTag <str> - Fully formed tag, i.e. <html>
    '''

    matchObj = DOCTYPE_MATCH.match(contents)
    if matchObj:
        idx = matchObj.end()
    else:
        idx = 0
    return "%s\n%s\n%s" %(contents[:idx], startTag, contents[idx:])


def escapeQuotes(value):
    '''
        escapeQuotes - Escape quotes within a value (replaces " with &quot;)

        @param value <str>

        @return <str> - Escaped value
    '''
    return value.replace('"', '&quot;')


def unescapeQuotes(value):
    '''
        unescapeQuotes - Unescapes quotes within a value (replaces &quot; with ")

        @param value <str>

        @return <str> - Escaped value
    '''
    return value.replace('&quot;', '"')

if sys.version_info.major < 3:
    def tostr(value):
        if not isinstance(value, (str, unicode)):
            value = unicode(value)
        return value

    def isstr(value):
        return isinstance(value, (str, unicode))
else:
    def tostr(value):
        return str(value)

    def isstr(value):
        return isinstance(value, str)
