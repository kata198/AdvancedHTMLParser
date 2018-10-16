#!/usr/bin/env GoodTests.py
'''
    Test various formatting methods
'''

import sys
import subprocess
import tempfile

from AdvancedHTMLParser.Parser import AdvancedHTMLParser

TEST_HTML = '''<html><head><title>Hello World</title></head>
 <body>
 <div>Hello world <span>And welcome to the show.</span>
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

        

if __name__ == '__main__':
    sys.exit(subprocess.Popen('GoodTests.py -n1 "%s" %s' %(sys.argv[0], ' '.join(['"%s"' %(arg.replace('"', '\\"'), ) for arg in sys.argv[1:]]) ), shell=True).wait())
