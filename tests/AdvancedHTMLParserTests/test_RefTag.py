#!/usr/bin/env GoodTests.py
'''
    Test that we retain &lt; and &gt;
'''

import sys
import tempfile
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


if __name__ == '__main__':
    pipe  = subprocess.Popen('GoodTests.py "%s"' %(sys.argv[0],), shell=True).wait()
