#!/usr/bin/env GoodTests.py
'''
    Test inserting data and tags
'''

import copy
import subprocess
import sys
import traceback

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
        assert itemsEm , 'Failed to get <div id="items" '

        newItem =  AdvancedTag('div')
        newItem.setAttributes( {
            'name' : 'item',
            'id' : 'item1point5'
            }
        )

        blocksBefore = copy.copy(itemsEm.blocks)
        childrenBefore = copy.copy(itemsEm.children)

        gotException = False
        try:
            itemsEm.insertBefore(newItem, parser.getElementById('outer'))
        except ValueError:
            gotException = True
        except Exception as otherExc:
            exc_info = sys.exc_info()
            traceback.print_exception(*exc_info)

            raise AssertionError('Expected insertBefore to raise ValueError if I try to insert before an item that does not exist.')

        assert gotException , 'Expected to get ValueError trying to insert before an element not contained within the node'

        assert blocksBefore == itemsEm.blocks , 'Expected blocks to NOT be changed on insertBefore error case'
        assert childrenBefore == itemsEm.children , 'Expected children to NOT be changed on insertBefore error case'


        ret = itemsEm.insertBefore(newItem, itemsEm.getElementById('item2'))
        assert ret == newItem , 'Expected insertBefore to return the added element'

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


    def test_insertBeforeWithText(self):
        '''
            test_insertBeforeWithText - Tests that insertBefore works with a text node, as well as an AdvancedTag
        '''
        parser = self.getItemsParser()

        itemsEm = parser.getElementById('items')
        item2Em = parser.getElementById('item2')

        assert itemsEm , 'Failed to get id="items"'

        childBlockText = 'BlArGie Buff$$'

        blocksBefore = copy.copy(itemsEm.blocks)
        childrenBefore = copy.copy(itemsEm.children)

        ret = itemsEm.insertBefore(childBlockText, item2Em)

        assert ret == childBlockText , 'Expected return to be the text added'

        assert itemsEm.children == childrenBefore , 'Expected child nodes to not be modified when text is inserted'
        assert itemsEm.blocks   != blocksBefore , 'Expected blocks to change'

        assert ret in itemsEm.blocks , 'Expected added text to be in the blocks'

        idxNewBlock = itemsEm.blocks.index(childBlockText)
        idxItems2 =   itemsEm.blocks.index(item2Em)

        assert idxNewBlock < idxItems2 , 'Expected insertBefore to add BEFORE.\n%s should have been added after id=items2.\nGot: %s'  %(repr(childBlockText), repr(itemsEm.innerHTML))

        blocksBefore = copy.copy(itemsEm.blocks)
        childrenBefore = copy.copy(itemsEm.children)

        childBlockText2 = 'Wh00ptie Whap'

        ret = itemsEm.insertBefore(childBlockText2, None)

        assert ret == childBlockText2 , 'Expected return to be the text added'

        assert itemsEm.children == childrenBefore , 'Expected child nodes to not be modified when text is inserted'
        assert itemsEm.blocks   != blocksBefore , 'Expected blocks to change'

        assert itemsEm.blocks[-1] == childBlockText2 , 'Expected last block to be added text when "afterChild" is None'



    def test_insertAfter(self):
        parser = self.getItemsParser()

        itemsEm = parser.getElementById('items')
        assert itemsEm , 'Failed to get <div id="items" '

        blocksBefore = copy.copy(itemsEm.blocks)
        childrenBefore = copy.copy(itemsEm.children)


        newItem =  AdvancedTag('div')
        newItem.setAttributes( {
            'name' : 'item',
            'id' : 'item1point5' }
        )

        gotException = False
        try:
            itemsEm.insertBefore(newItem, parser.getElementById('outer'))
        except ValueError:
            gotException = True
        except Exception as otherExc:
            exc_info = sys.exc_info()
            traceback.print_exception(*exc_info)

            raise AssertionError('Expected insertBefore to raise ValueError if I try to insert before an item that does not exist.')

        assert gotException , 'Expected to get ValueError trying to insert before an element not contained within the node'

        assert blocksBefore == itemsEm.blocks , 'Expected blocks to NOT be changed on insertBefore error case'
        assert childrenBefore == itemsEm.children , 'Expected children to NOT be changed on insertBefore error case'



        ret = itemsEm.insertAfter(newItem,  itemsEm.getElementById('item1'))
        assert ret == newItem , 'Expected insertAfter to return element added'

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


    def test_insertAfterWithText(self):
        '''
            test_insertAfterWithText - Tests that insertAfter works with a text node, as well as an AdvancedTag
        '''
        parser = self.getItemsParser()

        itemsEm = parser.getElementById('items')

        item2Em = parser.getElementById('item2')

        assert itemsEm , 'Failed to get id="items"'

        childBlockText = 'BlArGie Buff$$'

        blocksBefore = copy.copy(itemsEm.blocks)
        childrenBefore = copy.copy(itemsEm.children)

        ret = itemsEm.insertAfter(childBlockText, item2Em)

        assert ret == childBlockText , 'Expected return to be the text added'

        assert itemsEm.children == childrenBefore , 'Expected child nodes to not be modified when text is inserted'
        assert itemsEm.blocks   != blocksBefore , 'Expected blocks to change'

        assert ret in itemsEm.blocks , 'Expected added text to be in the blocks'

        idxNewBlock = itemsEm.blocks.index(childBlockText)
        idxItems2 =   itemsEm.blocks.index(item2Em)

        assert idxNewBlock > idxItems2 , 'Expected insertAfter to add AFTER.\n%s should have been added after id=items2.\nGot: %s'  %(repr(childBlockText), repr(itemsEm.innerHTML))

        blocksBefore = copy.copy(itemsEm.blocks)
        childrenBefore = copy.copy(itemsEm.children)

        childBlockText2 = 'Wh00ptie Whap'

        ret = itemsEm.insertAfter(childBlockText2, None)

        assert ret == childBlockText2 , 'Expected return to be the text added'

        assert itemsEm.children == childrenBefore , 'Expected child nodes to not be modified when text is inserted'
        assert itemsEm.blocks   != blocksBefore , 'Expected blocks to change'

        assert itemsEm.blocks[-1] == childBlockText2 , 'Expected last block to be added text when "afterChild" is None'


    def test_previousSibling(self):
        parser = AdvancedHTMLParser()
        parser.parseStr('<div>Head Text<div id="one">An item</div><div id="two">Another item</div>More Text<div id="three">Last  item</div></div>')

        root = parser.getRoot()

        assert root.getElementById('one').previousSibling == 'Head Text' , 'Expected to get "Head Text" as first sibling'
        assert root.getElementById('one').previousSiblingElement == None , 'Expected to get no element prior to first sibling'

        assert root.getElementById('two').previousSibling.id == 'one' , 'Expected to get element  "one" prior to two'
        assert root.getElementById('two').previousSiblingElement.id == 'one' , 'Expected to get element  "one" prior to two'


    def test_nextSibling(self):
        parser = AdvancedHTMLParser()
        parser.parseStr('<div>Head Text<div id="one">An item</div><div id="two">Another item</div>More Text<div id="three">Last  item</div></div>')

        root = parser.getRoot()

        assert root.getElementById('one').nextSibling.id == 'two' , 'Expected to get element with id "two"'
        assert root.getElementById('one').nextElementSibling.id == 'two' , 'Expected to get element with id "two"'
        assert root.getElementById('one').nextSiblingElement.id == 'two' , 'Expected to get element with id "two"'

        assert root.getElementById('two').nextSibling == 'More Text' , 'Expected to get text "Another Item" after item id=two'
        assert root.getElementById('two').nextElementSibling.id == 'three' , 'Expected to get element with id "three"'
        assert root.getElementById('two').nextSiblingElement.id == 'three' , 'Expected to get element with id "three"'

        assert root.getElementById('three').nextSibling == None , 'Expected to get no element after id="three"'
        assert root.getElementById('three').nextElementSibling == None , 'Expected to get no element after id="three"'
        assert root.getElementById('three').nextSiblingElement == None , 'Expected to get no element after id="three"'


    def test_firstLastChild(self):
        '''
            test_firstChild - test

                AdvancedTag.firstChild and AdvancedTag.firstElementChild
                AdvancedTag.lastChild and AdvancedTag.lastElementChild
        '''
        document = AdvancedHTMLParser()
        document.parseStr('<div id="main">Hello<div id="two">Blah</div><div id="emptyDiv"></div><div id="three">Three</div>End Text</div>')


        mainEm = document.getElementById('main')

        assert mainEm , "Failed to get element by id='main'"

        assert mainEm.id == 'main' , 'Got wrong element for id="main"'

        firstChild = mainEm.firstChild

        assert firstChild == 'Hello' , 'Expected .firstChild to return the first block child, str("Hello") but got: %s(%s)' %( firstChild.__class__.__name__, repr(firstChild))

        firstChildEm = mainEm.firstElementChild

        assert issubclass(firstChildEm.__class__, AdvancedTag) , 'Expected firstElementChild to return an AdvancedTag object. Got: ' + firstChildEm.__class__.__name__

        assert firstChildEm.tagName == 'div' and firstChildEm.id == 'two' , 'Expected to get div id="two" as firstElementChild. Got: %s(%s)' %( firstChildEm.__class__.__name__, repr(firstChildEm))

        lastChild = mainEm.lastChild

        assert lastChild == "End Text" , 'Expected .lastChild to return the last block child, str("End Text") but got: %s(%s)' %( lastChild.__class__.__name__, repr(lastChild))

        lastChildEm = mainEm.lastElementChild

        assert issubclass(lastChildEm.__class__, AdvancedTag) , 'Expected lastElementChild to return an AdvancedTag object. Got: ' + lastChildEm.__class__.__name__

        assert lastChildEm.tagName == 'div' and lastChildEm.id == 'three' , 'Expected to get div id="three" as lastElementChild. Got: %s(%s)' %( lastChildEm.__class__.__name__, repr(lastChildEm))


        emptyDivEm = document.getElementById('emptyDiv')

        assert emptyDivEm , 'Failed to get element by id="emptyDiv"'
        assert emptyDivEm.id == 'emptyDiv' , 'Got wrong element for id="emptyDiv"'

        firstChildEmpty = emptyDivEm.firstChild

        assert firstChildEmpty is None , 'Expected empty div .firstChild to be None (null). Got: ' + repr(firstChildEmpty)

        firstChildElementEmpty = emptyDivEm.firstElementChild

        assert firstChildElementEmpty is None , 'Expected empty div .firstElementChild to be None (null). Got: ' + repr(firstChildElementEmpty)

        lastChildEmpty = emptyDivEm.lastChild

        assert lastChildEmpty is None , 'Expected empty div .lastChild to be None (null). Got: ' + repr(lastChildEmpty)

        lastChildElementEmpty = emptyDivEm.lastElementChild

        assert lastChildElementEmpty is None , 'Expected empty div .lastElementChild to be None (null). Got: ' + repr(lastChildElementEmpty)


if __name__ == '__main__':
    sys.exit(subprocess.Popen('GoodTests.py -n1 "%s" %s' %(sys.argv[0], ' '.join(['"%s"' %(arg.replace('"', '\\"'), ) for arg in sys.argv[1:]]) ), shell=True).wait())
