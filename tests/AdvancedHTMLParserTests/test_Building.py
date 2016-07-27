#!/usr/bin/env GoodTests.py
'''
    Test that we can build HTML using the parser
'''

import subprocess
import sys

from AdvancedHTMLParser.Parser import AdvancedHTMLParser
from AdvancedHTMLParser.Tags import AdvancedTag

class TestBuilding(object):

    def test_setRoot(self):
        parser =  AdvancedHTMLParser()
        assert not parser.root, 'Root should start blank'

        root = AdvancedTag('html')
        parser.setRoot(root)

        assert parser.root  , 'Expected root to be set'
        assert parser.root.tagName  == 'html'  , 'Expected root node to be tagName=html'

        parser.reset()

        assert not parser.root,  'Expected parser root to be blank after reset is called'

        parser.parseStr(root.outerHTML)
        root = parser.getRoot()

        assert parser.root  , 'Expected root to be set'
        assert parser.root.tagName  == 'html'  , 'Expected root node to be tagName=html'

    def test_multipleRoot(self):
        parser = AdvancedHTMLParser()

        root1 =  AdvancedTag('div')
        root1.setAttribute('id', 'div1')

        root2 = AdvancedTag('div')
        root2.setAttribute('id', 'div2')

        parser.parseStr(root1.outerHTML + root2.outerHTML)

        assert len(parser.getRootNodes()) == 2, 'Expected two root nodes on tree'

        foundRoot1 = parser.getElementById('div1')
        assert foundRoot1, 'Expected to find id=div1 in multi-root tree'

        foundRoot2 = parser.getElementById('div2')
        assert foundRoot2, 'Expected to find id=div1 in multi-root tree'

        combinedHTML = (foundRoot1.outerHTML + foundRoot2.outerHTML).replace('\n', '').strip()
        parsedHTML = parser.getHTML().replace('\n', '').strip()

        assert combinedHTML == parsedHTML, 'Expected single element outerHTMLs to match parser HTML. """\n%s\n""" != """\n%s\n"""' %(combinedHTML, parsedHTML)

    def test_appending(self):
        parser = AdvancedHTMLParser()

        parser.parseStr("""<div id='outer'> <div id='items'> <div name="item" id="item1" >item1</div> <div name="item" id="item2" >item2</div> </div> </div>""")

        itemsEm = parser.getElementById('items')
        assert itemsEm , 'Expected  to get <div id="outer" '

        assert len(itemsEm.children) == 2 , 'Expected two children'

        newItem =  AdvancedTag('div')
        newItem.setAttributes( {
            'name' : 'item',
            'id' : 'item3' }
        )

        itemsEm.appendNode(newItem)

        assert parser.getElementById('item3') , 'Expected to get item3 after append'
        assert len(parser.getElementsByName('item')) == 3, 'Expected after append that 3 nodes are  set'
        assert itemsEm.children[2].getAttribute('id') == 'item3' , 'Expected to be third attribute'

        newItem =  AdvancedTag('div')
        newItem.setAttributes( {
            'name' : 'item',
            'id' : 'item2point5' }
        )

        itemsEm.insertAfter(newItem, itemsEm.children[1])
        childIds = [x.id for x in itemsEm.getElementsByName('item')]

        assert childIds == ['item1', 'item2', 'item2point5', 'item3'] , 'Expected items to be ordered. Got: %s' %(str(childIds,))

if __name__ == '__main__':
    pipe  = subprocess.Popen('GoodTests.py "%s"' %(sys.argv[0],), shell=True).wait()
