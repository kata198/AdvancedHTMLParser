#!/usr/bin/env GoodTests.py
'''
    Test DOMTokenList
'''

import sys
import subprocess

from AdvancedHTMLParser.SpecialAttributes import DOMTokenList


class TestDOMTokenList(object):
    '''
        Test SpecialAttributes.DOMTokenList
    '''

    def test_general(self):
        '''
            test_general - Test basic listy operations of a DOMTokenList
        '''

        tl = DOMTokenList( [ 'hello', 'world'] )

        assert len(tl) == 2 , 'Expected len to work.'

        assert tl[0] == 'hello' , 'Expected indexing to work'
        assert tl[1] == 'world' , 'Expected indexing to work'

        assert str(tl) == 'hello world' , 'Expected str(DOMTokenList) to do a string join, but got: ' + repr(str(tl))


    def test_createFromString(self):
        '''
            test_createFromString - Test that we can create a DOMTokenList from a string
        '''

        myStr = 'hello world'

        tl = DOMTokenList(myStr)

        assert len(tl) == 2 , 'Expected len to work.'

        assert tl[0] == 'hello' , 'Expected indexing to work'
        assert tl[1] == 'world' , 'Expected indexing to work'

        assert str(tl) == 'hello world' , 'Expected str(DOMTokenList) to do a string join, but got: ' + repr(str(tl))


    def test_createFromCrazyString(self):
        '''
            test_createFromCrazyString - Test that we properly strip before splitting a TokenString from string
        '''

        myStr = '    hello         world '

        tl = DOMTokenList(myStr)

        assert len(tl) == 2 , 'Expected len to work.'

        assert tl[0] == 'hello' , 'Expected indexing to work'
        assert tl[1] == 'world' , 'Expected indexing to work'

        assert str(tl) == 'hello world' , 'Expected str(DOMTokenList) to do a string join, but got: ' + repr(str(tl))

    def test_emptyFromEmptyStr(self):
        '''
            test_emptyFromEmptyStr - Test that we create an empty list with an empty str (or only whitespace)
        '''

        myStr = ''

        tl = DOMTokenList(myStr)

        assert len(tl) == 0 , 'Expected to have no elements in DOMTokenList constructed with empty string, but got: ' + repr(tl)

        myStr = '        '

        tl = DOMTokenList(myStr)

        assert len(tl) == 0 , 'Expected to have no elements in DOMTokenList constructed with whitespace-only string, but got: ' + repr(tl)


if __name__ == '__main__':
    sys.exit(subprocess.Popen('GoodTests.py -n1 "%s" %s' %(sys.argv[0], ' '.join(['"%s"' %(arg.replace('"', '\\"'), ) for arg in sys.argv[1:]]) ), shell=True).wait())
