#!/usr/bin/env GoodTests.py
'''
    Test various formatting methods
'''

import sys
import subprocess
import tempfile

from AdvancedHTMLParser.Parser import AdvancedHTMLParser

from AdvancedHTMLParser.Formatter import AdvancedHTMLSlimTagFormatter, AdvancedHTMLSlimTagMiniFormatter

TEST_HTML = '''<html><head><title>Hello World</title></head>
 <body>
 <div>Hello world <span>And welcome to the show.</span>
 </div>
 </body></html>'''


TEST_HTML_2 = '''<html><head></head>
    <body>  <div>Hello world<br> Welcome to <span id="abc" >The Show</span>
    <hr class="whatever">
    </div>
 </body></html>'''

class TestFormatting(object):

    # TODO: Add a test which checks that we retain whitespace

    def test_retainOriginalWhitespace(self):
        '''
            test_retainOriginalWhitespace - Test that we retain the original whitespacing
        '''
        parser = AdvancedHTMLParser()

        parser.parseStr(TEST_HTML)

        rawHtml = parser.getHTML()

        # This will not equal the original HTML exactly because we fixup some tag issues, like ' >'
        assert rawHtml == '<html ><head ><title >Hello World</title></head>\n <body >\n <div >Hello world <span >And welcome to the show.</span>\n </div>\n </body></html>' , 'Did not retain original whitespace like expected'


    def test_getFormattedHTML(self):
        '''
            test_getFormattedHTML - Tests the getFormattedHTML call for pretty-printing HTML
        '''
        parser = AdvancedHTMLParser()

        parser.parseStr(TEST_HTML)

        formattedHTML = parser.getFormattedHTML()

        assert formattedHTML == '\n<html >\n  <head >\n    <title >Hello World\n    </title>\n  </head> \n  <body > \n    <div >Hello world \n      <span >And welcome to the show.\n      </span> \n    </div> \n  </body>\n</html>' , 'Did not get expected formatting using default 4 spaces.'

        formattedHTMLTabIndent = parser.getFormattedHTML('\t')

        assert formattedHTMLTabIndent == '\n<html >\n\t<head >\n\t\t<title >Hello World\n\t\t</title>\n\t</head> \n\t<body > \n\t\t<div >Hello world \n\t\t\t<span >And welcome to the show.\n\t\t\t</span> \n\t\t</div> \n\t</body>\n</html>' , 'Did not get expected formatting using tabs.'


    def test_getMiniHTML(self):
        '''
            test_getMiniHTML - Gets a "mini" representation that only contains the functional whitespace characters in HTML repr
        '''
        parser = AdvancedHTMLParser()

        parser.parseStr(TEST_HTML)

        miniHTML = parser.getMiniHTML()

        assert miniHTML == '<html ><head ><title >Hello World</title></head> <body > <div >Hello world <span >And welcome to the show.</span> </div> </body></html>'

    def test_slimTagFormatter(self):
        '''
            test_slimTagFormatter - Test the AdvancedHTMLSlimTagFormatter
        '''

        parser = AdvancedHTMLSlimTagFormatter()
        parser.parseStr(TEST_HTML_2)

        prettyHTML = parser.getHTML()

        assert prettyHTML == '\n<html>\n    <head>\n    </head> \n    <body> \n        <div>Hello world\n            <br /> Welcome to \n            <span id="abc">The Show\n            </span> \n            <hr class="whatever" /> \n        </div> \n    </body>\n</html>' , 'Got unexpected HTML output for slim-tag pretty printer with slimSelfClosing=False'

        parser = AdvancedHTMLSlimTagFormatter(slimSelfClosing=True)
        parser.parseStr(TEST_HTML_2)

        prettyHTML = parser.getHTML()
        assert prettyHTML == '\n<html>\n    <head>\n    </head> \n    <body> \n        <div>Hello world\n            <br/> Welcome to \n            <span id="abc">The Show\n            </span> \n            <hr class="whatever"/> \n        </div> \n    </body>\n</html>' , 'Got unexpected HTML output for slim-tag pretty printer with slimSelfClosing=True'


    def test_slimTagMiniFormatter(self):
        '''
            test_slimTagMiniFormatter - Test the AdvancedHTMLSlimTagMiniFormatter
        '''

        parser = AdvancedHTMLSlimTagMiniFormatter()
        parser.parseStr(TEST_HTML_2)

        prettyHTML = parser.getHTML()

        print ( repr(prettyHTML) )

        assert prettyHTML == '<html><head></head> <body> <div>Hello world<br /> Welcome to <span id="abc">The Show</span> <hr class="whatever" /> </div> </body></html>' , 'Got unexpected HTML output for slim-tag mini printer with slimSelfClosing=False'


        parser = AdvancedHTMLSlimTagMiniFormatter(slimSelfClosing=True)
        parser.parseStr(TEST_HTML_2)

        prettyHTML = parser.getHTML()
        assert prettyHTML == '<html><head></head> <body> <div>Hello world<br/> Welcome to <span id="abc">The Show</span> <hr class="whatever"/> </div> </body></html>' , 'Got unexpected HTML output for slim-tag mini printer with slimSelfClosing=True'


if __name__ == '__main__':
    sys.exit(subprocess.Popen('GoodTests.py -n1 "%s" %s' %(sys.argv[0], ' '.join(['"%s"' %(arg.replace('"', '\\"'), ) for arg in sys.argv[1:]]) ), shell=True).wait())
