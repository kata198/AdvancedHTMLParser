#!/usr/bin/env GoodTests.py
'''
    Test that Custom Filters work as expected
'''

import sys
import subprocess
from AdvancedHTMLParser import AdvancedHTMLParser

class TestCustomFilter(object):


    def setup_method(self, method):
        someHTML = '''
<html>
    <head>
        <title>Blah</title>
    </head>
    <body style="background-color: purple" >
        <div class="one two" name="one" id="item1">
            <span class="two" name="one" id="item2">
                Hello
            </span>
            <span class="three" id="item4">
                item4
            </span>
        </div>
        <div class="one durp" name="three" id="item3">
           Yes
        </div>
        <span>
            <span class="three">Hi</span>
        </span>
    </body>
</html>'''
        parser = AdvancedHTMLParser()
        parser.parseStr(someHTML)
        self.parser = parser



    def test_CustomFilter(self):

        parser = self.parser

        def searchFunc(node):
            if node.hasClass("two") and node.getAttribute('name') == "one":
                return True
            return False

        results = parser.getElementsCustomFilter(searchFunc)

        assert len(results) == 2, 'Expected two results from filter'
        assert results[0].id == 'item1' and results[1].id == 'item2', 'Expected to find item1 and item2'

        del searchFunc

        def searchFunc(node):
            return bool(node.tagName == 'div')

        results = parser.getElementsCustomFilter(searchFunc)

        assert len(results) == 2, 'Expected two results from filter'
        assert results[0].id == 'item1' and results[1].id == 'item3'

    def test_tagCollectionCustomFilter(self):

        parser = self.parser

        def searchFunc(node):
            return bool(node.hasClass('one'))

        results = parser.getElementsByTagName('div')
        assert len(results) == 2 , 'Expected to find two divs'

        # Asserting that a custom filter applied to a TagCollection only works on the elements and their children contained therein

        filtered = results.getElementsCustomFilter(searchFunc)

        assert len(filtered) == 2 , 'Expected custom filter return two divs'

        del searchFunc

        def searchFunc(node):
            return bool(node.hasClass('three'))

        filtered = results.getElementsCustomFilter(searchFunc)

        assert len(filtered) == 1 , 'Expected to only find one subset of any div with class "three"'

        assert filtered[0].id == 'item4' , 'Expected to find item4'

        del searchFunc

        # Asserting that filterCollection does not transverse into children

        def searchFunc(node):
            return bool(node.hasClass('two'))

        filtered = results.filterCollection(searchFunc)

        assert len(filtered) == 1 , 'Expected only one div result'
        assert filtered[0].tagName == 'div', 'Expected result to be a div'
        assert filtered[0].id == 'item1' , 'Expected to find item1'


    def test_tagCustomFilter(self):

        parser = self.parser

        def searchFunc(node):
            return bool(node.hasClass('three'))

        body = parser.getElementsByTagName('body')[0]

        results = body.getElementsCustomFilter(searchFunc)

        assert len(results) == 2
        assert results[0].id == 'item4'
        assert results[1].innerHTML.strip() == 'Hi'

        item1 = parser.getElementById('item1')

        results = item1.getElementsCustomFilter(searchFunc)

        assert len(results) == 1
        assert results[0].id == 'item4'

    def test_oneElementCustomFilter(self):

        parser = self.parser

        def searchFunc(node):
            return bool(node.hasClass('three'))


        firstThreeNode = parser.getFirstElementCustomFilter(searchFunc)

        assert firstThreeNode , 'Expected to get a node with class="three" on AdvancedHTMLParser.getFirstElementCustomFilter'
        assert firstThreeNode.id == 'item4' , 'Expected to get id="item4"'

        bodyNode = parser.getElementsByTagName('body')[0]
        assert bodyNode , 'Failed to find body node'

        firstThreeNode = bodyNode.getFirstElementCustomFilter(searchFunc)

        assert firstThreeNode , 'Expected to get a node with class="three" on AdvancedTag.getFirstElementCustomFilter'
        assert firstThreeNode.id == 'item4' , 'Expected to get id="item4"'



if __name__ == '__main__':
    sys.exit(subprocess.Popen('GoodTests.py -n1 "%s" %s' %(sys.argv[0], ' '.join(['"%s"' %(arg.replace('"', '\\"'), ) for arg in sys.argv[1:]]) ), shell=True).wait())
