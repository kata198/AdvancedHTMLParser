#!/usr/bin/env GoodTests.py
'''
    Test that we find untagged text.
'''

import sys
import tempfile

from AdvancedHTMLParser.Parser import AdvancedHTMLParser


class TestUntaggedText(object):

    def test_untaggedText(self):
        html = """    <span class="WebRupee">Rs.</span>\n29\n<br/><font style="font-size:smaller;font-weight:normal">\n3 days\n</font></td>, <td class="pricecell"><span class="WebRupee">Rs.</span>\n59\n<br/><font style="font-size:smaller;font-weight:normal">\n7 days\n</font></td>, <td class="pricecell"><span class="WebRupee">Rs.</span>\n99\n<br/><font style="font-size:smaller;font-weight:normal">\n12 days\n</font></td>"""

        parser = AdvancedHTMLParser()
        parser.parseStr(html)

        html = parser.getHTML()

        assert '\n29\n' in html , 'Expected to find item outside tags: \\n29\\n in ' + str(html)


    def test_multipleRootsSameReturn(self):
        html = """<span>Hello</span><span>World</span>"""
        parser = AdvancedHTMLParser()
        parser.parseStr(html)

        strippedHTML = parser.getHTML().replace('\n', '').replace(' ','')

        assert strippedHTML == html , "Expected multiple root nodes to retain, '%s' == '%s'" %(html, strippedHTML)

    def test_multipleRootsWithExternalTextSameReturn(self):
        html = """<span>Hello</span>Outside<span>World</span>End"""
        parser = AdvancedHTMLParser()
        parser.parseStr(html)

        strippedHTML = parser.getHTML().replace('\n', '').replace(' ','')
        assert strippedHTML == html, "Expected multiple root nodes with text between the nodes to retain, '%s' == '%s'" %(html, strippedHTML)


if __name__ == '__main__':
    pipe  = subprocess.Popen('GoodTests.py "%s"' %(sys.argv[0],), shell=True).wait()
