#!/usr/bin/env GoodTests.py
'''
    Test inserting data and tags
'''

import subprocess
import sys

from AdvancedHTMLParser.Parser import AdvancedHTMLParser
from AdvancedHTMLParser.Tags import AdvancedTag

class TestInsertions(object):

    def getItemsParser(self):
        parser = AdvancedHTMLParser()

        parser.parseStr("""<div id='outer'> <div id='items'> <div name="item" id="item1" >item1</div> <div name="item" id="item2" >item2</div> </div> </div>""")

        return parser

    def test_insertBefore(self):
        parser = self.getItemsParser()

        itemsEm = parser.getElementById('items')
        assert itemsEm , 'Expected  to get <div id="outer" '

        newItem =  AdvancedTag('div')
        newItem.setAttributes( {
            'name' : 'item',
            'id' : 'item1point5' 
            }
        )

        itemsEm.insertBefore(newItem, itemsEm.getElementById('item2'))
        childIds = [x.id for x in itemsEm.getElementsByName('item')]

        assert childIds == ['item1', 'item1point5', 'item2'] , 'Expected items to be ordered. Got: %s' %(str(childIds,))
        newItem =  AdvancedTag('div')
        

        newItem.setAttributes( {
            'name' : 'item',
            'id' : 'item3' 
            }
        )

        # test None as before item inserts at end
        itemsEm.insertBefore(newItem, None)
        childIds = [x.id for x in itemsEm.getElementsByName('item')]

        assert childIds == ['item1', 'item1point5', 'item2', 'item3'] , 'Expected items to be ordered. Got: %s' %(str(childIds,))
        newItem =  AdvancedTag('div')
        

    def test_insertAfter(self):
        parser = self.getItemsParser()

        itemsEm = parser.getElementById('items')
        assert itemsEm , 'Expected  to get <div id="outer" '

        newItem =  AdvancedTag('div')
        newItem.setAttributes( {
            'name' : 'item',
            'id' : 'item1point5' }
        )

        itemsEm.insertAfter(newItem,  itemsEm.getElementById('item1'))
        childIds = [x.id for x in itemsEm.getElementsByName('item')]

        assert childIds == ['item1', 'item1point5', 'item2'] , 'Expected items to be ordered. Got: %s' %(str(childIds,))

        newItem =  AdvancedTag('div')
        newItem.setAttributes( {
            'name' : 'item',
            'id' : 'item3' 
            }
        )

        # test None as before item inserts at end
        itemsEm.insertAfter(newItem, None)
        childIds = [x.id for x in itemsEm.getElementsByName('item')]

        assert childIds == ['item1', 'item1point5', 'item2','item3'] , 'Expected items to be ordered. Got: %s' %(str(childIds,))
        newItem =  AdvancedTag('div')
        
    def testPreviousSibling(self):
        parser = AdvancedHTMLParser()
        parser.parseStr('<div>Head Text<div id="one">An item</div><div id="two">Another item</div>More Text<div id="three">Last  item</div></div>')
        
        root = parser.getRoot()

        assert root.getElementById('one').previousSibling == 'Head Text' , 'Expected to get "Head Text" as first sibling'
        assert root.getElementById('one').previousSiblingElement == None , 'Expected to get no element prior to first sibling'

        assert root.getElementById('two').previousSibling.id == 'one' , 'Expected to get element  "one" prior to two'
        assert root.getElementById('two').previousSiblingElement.id == 'one' , 'Expected to get element  "one" prior to two'

    def testNextSibling(self):
        parser = AdvancedHTMLParser()
        parser.parseStr('<div>Head Text<div id="one">An item</div><div id="two">Another item</div>More Text<div id="three">Last  item</div></div>')
        
        root = parser.getRoot()

        assert root.getElementById('one').nextSibling.id == 'two' , 'Expected to get element with id "two"'
        assert root.getElementById('one').nextSiblingElement.id == 'two' , 'Expected to get element with id "two"'

        assert root.getElementById('two').nextSibling == 'Another Item' , 'Expected to get text "Another Item" after item id=two'
        assert root.getElementById('two').nextSiblingElement.id == 'three' , 'Expected to get element with id "three"'

        assert root.getElementById('three').nextSibling == None , 'Expected to get no element after id="three"'
        assert root.getElementById('three').nextSiblingElement == None , 'Expected to get no element after id="three"'



if __name__ == '__main__':
    pipe  = subprocess.Popen('GoodTests.py "%s"' %(sys.argv[0],), shell=True).wait()
