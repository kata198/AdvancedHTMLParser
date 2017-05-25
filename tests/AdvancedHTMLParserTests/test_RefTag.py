#!/usr/bin/env GoodTests.py
'''
    Test that we retain &lt; and &gt;
'''

import sys
import subprocess

from AdvancedHTMLParser.Parser import AdvancedHTMLParser


class TestRefTag(object):

    def test_refTag(self):
        html = """<html><body><p>This is &lt;html&gt;</p></body></html>"""

        parser = AdvancedHTMLParser()
        parser.parseStr(html)

        html = parser.getHTML().replace('\n', '').replace('html ', 'html')
        assert 'This is <html>' not in html, 'Expected to retain &lt; and &gt;, got %s' %(html,)
        assert 'This is &lt;html&gt;' in html, 'Expected to retain &lt; and &gt;, got %s' %(html,)

    def test_nbsp(self):
        html = """<html><body><p>Test&nbsp;One</p></body></html>"""
        parser = AdvancedHTMLParser()
        parser.parseStr(html)

        html = parser.getHTML().replace('\n', '').replace('html ', 'html')
        assert '&nbsp;' in html, '(Will fail in python2..) Expected to retain &nbsp; got %s' %(html,)

        html = """<html><body><p>Test One</p></body></html>"""
        parser = AdvancedHTMLParser()
        parser.parseStr(html)

        html = parser.getHTML().replace('\n', '').replace('html ', 'html')
        assert '&nbsp;' not in html, '(Will fail in python2..) Expected not to insert &nbsp; got %s' %(html,)

        html = """<html><body><p>Test&nbsp;&nbsp;One</p></body></html>"""
        parser = AdvancedHTMLParser()
        parser.parseStr(html)

        html = parser.getHTML().replace('\n', '').replace('html ', 'html')
        assert 'Test&nbsp;&nbsp;One' in html, '(Will fail in python2..) Expected to retain original data with two &nbsp; got %s' %(html,)


if __name__ == '__main__':
    sys.exit(subprocess.Popen('GoodTests.py -n1 "%s" %s' %(sys.argv[0], ' '.join(['"%s"' %(arg.replace('"', '\\"'), ) for arg in sys.argv[1:]]) ), shell=True).wait())
