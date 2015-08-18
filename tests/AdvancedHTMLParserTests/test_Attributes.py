#!/usr/bin/env GoodTests.py

import sys
import subprocess

from AdvancedHTMLParser.Tags import AdvancedTag

class TestAttributes(object):
    '''
        Tests some attribute behaviour
    '''

    def test_setAttribute(self):
        tag = AdvancedTag('div')

        tag.setAttribute('id', 'abc')

        assert tag.getAttribute('id') == 'abc' , 'Expected id to be abc'

        assert tag.getAttribute('blah') == None , 'Expected unset attribute to return None, actually returned %s' %(tag.getAttribute('blah'),)

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
        styleValue = str(tag.getAttribute('style'))
        styleValue = styleValue.strip()
        assert styleValue == 'position: absolute' , 'Expected position: absolute, got %s' %(str(tag.getAttribute('style')),)

        tag.setAttribute('className', 'one two')
        assert str(tag.className).strip() == 'one two' , 'Expected classname to be "one two", got %s' %(repr(str(tag.className).strip()),)

    def test_specialAttributesInHTML(self):
        tag = AdvancedTag('div')
        tag.attributes['style'] = 'position: absolute; color: purple'

        outerHTML = tag.outerHTML

        assert 'position: absolute' in outerHTML , 'Missing style attribute in outerHTML'
        assert 'purple' in outerHTML , 'Missing style attribute in outerHTML'

    def test_classNames(self):
        tag = AdvancedTag('div')
        tag.addClass('abc')

        assert tag.hasClass('abc'), 'Failed to add class'
        assert 'abc' in tag.outerHTML , 'Failed to add class in outerHTML'

        tag.addClass('def')

        assert tag.hasClass('abc'), 'Failed to retain class'
        assert 'abc' in tag.outerHTML , ' Failed to retain in outerHTML'

        assert tag.hasClass('def'), 'Failed to add second class'
        assert 'def' in tag.outerHTML , ' Failed to add to outerHTML'

        tag.removeClass('abc')
        assert not tag.hasClass('abc'), 'Failed to remove class'
        assert 'abc' not in tag.outerHTML , 'Failed to remove class from outerHTML'

        assert tag.hasClass('def'), 'Failed to retain class'
        assert 'def' in tag.outerHTML , ' Failed to retain in outerHTML'


if __name__ == '__main__':
    pipe  = subprocess.Popen('GoodTests.py "%s"' %(sys.argv[0],), shell=True).wait()
