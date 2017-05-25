#!/usr/bin/env GoodTests.py
'''
    Test that we find untagged text.
'''

import sys
import subprocess

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

    def test_textPriorToRoot(self):
        html = """Hello<html><span id="one">Cheese</span><div>Goodbye</div></html>"""

        parser = AdvancedHTMLParser()
        parser.parseStr(html)

        strippedHTML = parser.getHTML().replace('\n', '')

#        print ( strippedHTML )
        assert strippedHTML.startswith('Hello') , 'Expected text before root tag to be retained, got "%s"' %(strippedHTML,)

    def test_textAfterRoot(self):
        html = """<html><span id="one">Cheese</span><div>Goodbye</div></html>Hello"""

        parser = AdvancedHTMLParser()
        parser.parseStr(html)

        strippedHTML = parser.getHTML().replace('\n', '')

#        print ( strippedHTML )

        assert strippedHTML.endswith('Hello') , 'Expected text after root tag to be retained, got "%s"' %(strippedHTML,)


    def test_textBeforeAndAfterRoot(self):
        html = """Hello<html><span id="one">Cheese</span><div>Goodbye</div></html>World"""

        parser = AdvancedHTMLParser()
        parser.parseStr(html)

        strippedHTML = parser.getHTML().replace('\n', '')

#        print ( strippedHTML )

        assert strippedHTML.startswith('Hello') , 'Expected text before root tag to be retained, got "%s"' %(strippedHTML,)
        assert strippedHTML.endswith('World') , 'Expected text after root tag to be retained, got "%s"' %(strippedHTML,)

    def test_commentRetained(self):
        html = """<html>
        <!-- CommentX -->
        <body><span>Hello</span></body></html>"""

        parser = AdvancedHTMLParser()
        parser.parseStr(html)

        retHTML = parser.getHTML()

        assert 'CommentX' in retHTML, 'Expected to find comment, "CommentX" in returned HTML: "%s"' %(retHTML,)

    def test_commentRetainedPriorRoot(self):
        html = """<!-- CommentX --><html>
        <body><span>Hello</span></body></html>"""

        parser = AdvancedHTMLParser()
        parser.parseStr(html)

        retHTML = parser.getHTML()

        assert 'CommentX' in retHTML, 'Expected to find comment, "CommentX" in returned HTML: "%s"' %(retHTML,)

    def test_commentRetainedAfterRoot(self):
        html = """<html>
        <body><span>Hello</span></body></html><!-- CommentX -->"""

        parser = AdvancedHTMLParser()
        parser.parseStr(html)

        retHTML = parser.getHTML()

        assert 'CommentX' in retHTML, 'Expected to find comment, "CommentX" in returned HTML: "%s"' %(retHTML,)

    def test_commentRetainedBeforeAndAfterRoot(self):
        html = """<!-- CommentX --><html>
        <body><span>Hello</span></body></html><!-- CommentY -->"""

        parser = AdvancedHTMLParser()
        parser.parseStr(html)

        retHTML = parser.getHTML()

        assert 'CommentX' in retHTML, 'Expected to find comment, "CommentX" in returned HTML: "%s"' %(retHTML,)
        assert 'CommentY' in retHTML, 'Expected to find comment, "CommentY" in returned HTML: "%s"' %(retHTML,)



if __name__ == '__main__':
    sys.exit(subprocess.Popen('GoodTests.py -n1 "%s" %s' %(sys.argv[0], ' '.join(['"%s"' %(arg.replace('"', '\\"'), ) for arg in sys.argv[1:]]) ), shell=True).wait())
