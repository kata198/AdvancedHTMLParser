#!/usr/bin/env GoodTests.py
'''
    Test TokenList
'''

import sys
import subprocess

from AdvancedHTMLParser.SpecialAttributes import TokenList


class TestTokenList(object):
    '''
        Test SpecialAttributes.TokenList
    '''

    def test_general(self):
        
        tl = TokenList( [ 'hello', 'world'] )

        assert len(tl) == 2 , 'Expected len to work.'

        assert tl[0] == 'hello' , 'Expected indexing to work'
        assert tl[1] == 'world' , 'Expected indexing to work'

        assert str(tl) == 'hello world' , 'Expected str(TokenList) to do a string join, but got: ' + repr(str(tl))


if __name__ == '__main__':
    sys.exit(subprocess.Popen('GoodTests.py -n1 "%s" %s' %(sys.argv[0], ' '.join(['"%s"' %(arg.replace('"', '\\"'), ) for arg in sys.argv[1:]]) ), shell=True).wait())
