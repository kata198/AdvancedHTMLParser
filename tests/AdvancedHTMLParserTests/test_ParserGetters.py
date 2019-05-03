#!/usr/bin/env GoodTests.py
'''
    Test that the get* methods work as expected
'''

import subprocess
import sys

import AdvancedHTMLParser


class TestParserGetters(object):
    '''
        Testt the various "get"  methods when cakled von the Parser  object
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
    sys.exit(subprocess.Popen('GoodTests.py -n1 "%s" %s' %(sys.argv[0], ' '.join(['"%s"' %(arg.replace('"', '\\"'), ) for arg in sys.argv[1:]]) ), shell=True).wait())
