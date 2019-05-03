#!/usr/bin/env GoodTests.py
'''
    Test that we properly handle InvalidHTML
'''

import sys
import subprocess

from AdvancedHTMLParser.Parser import AdvancedHTMLParser


MULTIPLE_ROOT = """
   <div id='one'>
        <span id='one_s' >
            Hello
        </span>
    </div>
    <div id='two'>
        <span id='two_s' >
            Goodbye
        </span>
    </div>
"""


INVALID_CLOSE = """
    <html>
        <div id="one">
            <span>Hello</span>
        </span>
        </div>
    </html>
"""

MISS_CLOSE = """
    <html>
        <div id="one">
            <span>Hello
        </div>
    </html>
"""


class TestInvalidHtml(object):

    def test_HandleMultipleRoot(self):
        parser = AdvancedHTMLParser()
        try:
            parser.parseStr(MULTIPLE_ROOT)
        except Exception as e:
            raise AssertionError('Failed to properly parse invalid HTML with multiple root nodes')

        oneEm = parser.getElementById('one')
        assert oneEm , 'Failed to find first element'
        assert len(parser.getRootNodes()) == 2

    def test_HandleInvalidClose(self):
        parser = AdvancedHTMLParser()
        try:
            parser.parseStr(INVALID_CLOSE)
        except Exception as e:
            raise AssertionError('Failed to properly parse invalid HTML with invalid close')

        oneEm = parser.getElementById('one')
        assert oneEm , 'Failed to find id="one"'
        assert oneEm.children[0].innerHTML.strip() == 'Hello' , 'Could not find child tag'

    def test_HandleMissClose(self):
        parser = AdvancedHTMLParser()
        try:
            parser.parseStr(MISS_CLOSE)
        except Exception as e:
            raise AssertionError('Failed to properly parse invalid HTML with missed close')

        oneEm = parser.getElementById('one')
        assert oneEm , 'Failed to find id="one"'
        assert oneEm.children[0].innerHTML.strip() == 'Hello' , 'Could not find child tag'



if __name__ == '__main__':
    sys.exit(subprocess.Popen('GoodTests.py -n1 "%s" %s' %(sys.argv[0], ' '.join(['"%s"' %(arg.replace('"', '\\"'), ) for arg in sys.argv[1:]]) ), shell=True).wait())
