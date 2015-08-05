#!/usr/bin/env GoodTests.py

import re
import subprocess
import sys

import AdvancedHTMLParser


class TestGeneral(object):
    '''
        A general test class. Basically example.py converted a bit.

        TODO: Add more specific testsfor everything
    '''

    def __init__(self):
        self.testHTML = '''
        <div id="testItem" style="display: block">Hello</div>
'''

    def setup_method(self, method):
        '''
            This test writes, so reparse for every method
        '''
        self.parser =  AdvancedHTMLParser.AdvancedHTMLParser()
        self.parser.parseStr(self.testHTML)

        self.item = self.parser.getElementById('testItem')

    def test_getStyleMember(self):
        '''
            test  member access  of parsed style attribute
        '''
        item  = self.item

        assert item.style.display == 'block'

    def test_getStyleMethod(self):
        '''
            Test method access of parsed style  attribute
        '''
        item = self.item 

        assert item.getStyle('display') == 'block'

    def test_getUnsetStyleMethod(self):
        '''
            Test that getting a style attribute that  hasn't been set returns empty string
        '''
        item = self.item

        assert item.getStyle('color') == ''

    def test_getUnsetStyleMember(self):
        '''
            Test that getting a style attribute that  hasn't been set returns empty string
        '''
        item = self.item

        assert item.style.color  == ''

    def test_setStyleMember(self):
        '''
            Test that  setting style attributes by their members  works as expected
        '''
        item = self.item

        item.style = 'position: relative; top: 6px;'

        assert item.style
        assert item.style.position == 'relative'
        assert item.style.top == '6px'
        assert item.style.display == '' # Should have cleared because we overrode


if __name__ == '__main__':
    import subprocess
    import sys
    pipe  = subprocess.Popen('GoodTests.py "%s"' %(sys.argv[0],), shell=True).wait()
