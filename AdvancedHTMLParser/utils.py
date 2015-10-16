# Copyright (c) 2015 Tim Savannah  under terms of LGPLv3

import re

IE_CONDITIONAL_PATTERN = re.compile('[<][!][-][-][ \t\r\n]*[\[][ \t\r\n]*if.*-->', re.MULTILINE)

END_HTML = re.compile('.*</[ \t\r\n]*[hH][tT][mM][lL][ \t\r\n]*>.*', re.DOTALL)
START_HTML = re.compile('.*<[ \t\r\n]*[hH][tT][mM][lL][ \t\r\n]*>.*', re.DOTALL)

DOCTYPE_MATCH = re.compile('[\n]*[ \t]*(?P<tag><[!][ \t]*[dD][oO][cC][tT][yY][pP][eE].*[>])')

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

