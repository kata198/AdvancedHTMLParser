#!/usr/bin/env GoodTests.py

import sys
import subprocess

from AdvancedHTMLParser.Tags import AdvancedTag

class test_Attributes(object):
    '''
        Tests some attribute behaviour
    '''

    def test_setAttribute(self):
        tag = AdvancedTag('div')

        tag.setAttribute('id', 'abc')

        assert tag.getAttribute('id') == 'abc' , 'Expected id to be abc'

        assert tag.getAttribute('blah') == '' , 'Expected unset attribute to return empty string'

    def test_setAttributes(self):
        tag = AdvancedTag('div')
        tag.setAttributes( {
            'id' : 'abc',
            'name'  :  'cheese',
            'x-attr' : 'bazing'
        })

        assert tag.getAttribute('id') == 'abc'
        assert tag.getAttribute('name') == 'cheese'
        assert tag.getAttribute('x-attr') == 'bazing'

    def test_specialAttributes(self):
        tag = AdvancedTag('div')
        tag.setAttribute('style', 'position: absolute')
        assert tag.getAttribute('style', 'position: absolute')

        tag.setAttribute('className', 'one two')
        assert tag.className == 'one two'


if __name__ == '__main__':
    pipe  = subprocess.Popen('GoodTests.py "%s"' %(sys.argv[0],), shell=True).wait()
