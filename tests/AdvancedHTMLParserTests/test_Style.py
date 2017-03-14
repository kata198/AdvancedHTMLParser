#!/usr/bin/env GoodTests.py
'''
    Test style attributes
'''

import subprocess
import sys

import AdvancedHTMLParser

from AdvancedHTMLParser.SpecialAttributes import StyleAttribute


class TestStyle(object):
    '''
        Test special style attribute
    '''

    def __init__(self):
        self.testHTML = '''
        <div id="testItem" style="display: block; padding-left: 5px">Hello</div>
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


    def test_dashNames(self):

        item = self.item

        assert item.style.paddingLeft == '5px' , 'Expected to convert name "padding-left" to "paddingLeft" on attribute access.'

        item.style.paddingTop = '10px'

        assert item.style.paddingTop == '10px', 'Expected that after setting "paddingTop" you can retrieve it back using "paddingTop"'

        styleStr = str(item.style)

        assert 'padding-left: 5px' in styleStr , 'Expected to see dash-name "padding-left" in style string. Got: %s' %(styleStr, )

        assert 'padding-top: 10px' in styleStr, 'Expected to see dash-name "padding-top" in style string. Got: %s' %(styleStr, )

    def test_createStyleFromStyle(self):

        item = self.item

        newStyle = StyleAttribute(item.style)

        assert newStyle.display == 'block' , 'Expected new StyleAttribute from StyleAttribute to have same values. Got different value for display, expected "block", got "%s"' %(newStyle.display, )

        assert newStyle.paddingLeft == '5px', 'Expected new StyleAttribute from StyleAttribute to have same values. Got different value for padding-left, expected "5px", got "%s"' %(newStyle.paddingLeft, )

        newStyle.paddingLeft = '11px'

        assert newStyle.paddingLeft == '11px' , 'Expected to be able to change attributes on the new StyleAttribute object.'

        assert item.style.paddingLeft != '11px', 'Expected changes to the copy do not affect the original.'




if __name__ == '__main__':
    subprocess.Popen('GoodTests.py "%s"' %(sys.argv[0],), shell=True).wait()
