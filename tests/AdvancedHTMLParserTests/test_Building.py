#!/usr/bin/env GoodTests.py
'''
    Test that we can build HTML using the parser
'''

import subprocess
import sys

from AdvancedHTMLParser.Parser import AdvancedHTMLParser
from AdvancedHTMLParser.Tags import AdvancedTag
from AdvancedHTMLParser import MultipleRootNodeException

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

        assert itemsEm.childElementCount == 2 , 'Expected childElementCount to equal 2'

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

    def test_ownerDocument(self):
        parser = AdvancedHTMLParser()

        parser.parseStr("""<div id='outer'> <div id='items'> <div name="item" id="item1" >item1 <span id="subItem1">Sub item</span></div> <div name="item" id="item2" >item2</div> </div> </div>""")

        outerEm = parser.getElementById('outer')

        assert outerEm.ownerDocument == parser , 'Expected the ownerDocument to be set to parser'

        for element in outerEm.getAllNodes():
            assert element.ownerDocument == parser, 'Expected ownerDocument to be set on every element. Was not set on: %s' %(element.getStartTag(),)


        clonedEm = outerEm.cloneNode()

        assert clonedEm.parentNode is None , 'Expected cloned child to have no parent'
        assert clonedEm.ownerDocument is None , 'Expected cloned child to have no owner document'

        assert len(clonedEm.children) == 0 , 'Expected cloned element to have no children'

        itemsEm = outerEm.removeChild(outerEm.children[0])

        assert itemsEm , 'Expected removeChild to return removed element'

        assert itemsEm.id == 'items' , 'Got wrong element, expected to remove "items", got: %s' %(itemsEm.getStartTag(),)

        assert itemsEm.ownerDocument is None , 'Expected owner document to be set to None after element was removed.'

        for subElement in itemsEm.getAllChildNodes():
            assert subElement.ownerDocument is None, 'Expected owner document to be cleared on all children after removal from document'



    def test_removeAndContains(self):
        parser = AdvancedHTMLParser()

        parser.parseStr("""<div id='outer'> <div id='items'> <div name="item" id="item1" >item1 <span id="subItem1">Sub item</span></div> <div name="item" id="item2" >item2</div> </div> </div>""")


        itemsEm = parser.getElementById('items')
        item1Em = parser.getElementById('item1')
        subItem1 = parser.getElementById('subItem1')

        assert itemsEm.hasChild(item1Em) is True, 'Expected itemsEm to have item1Em as a child.'

        assert parser.getElementById('subItem1') is not None, 'Expected to find id=subItem1'

        assert itemsEm.contains(item1Em) , 'Expected itemsEm to contain items1Em'
        assert itemsEm.contains(subItem1) , 'Expected itemsEm to contain subItem1'

        assert subItem1.uid in itemsEm.getAllNodeUids()

        assert parser.contains(item1Em) , 'Expected parser to contain item1Em via contains'
        assert item1Em in parser, 'Expected parser to contain item1Em via in operator'

        assert item1Em.ownerDocument == parser , 'Expected ownerDocument to be set prior to remove'

        # Remove item1 from the tree
        item1Em.remove()

        assert itemsEm.hasChild(item1Em) is False, 'Expected after remove for item1Em to no longer be a child of itemsEm'

        assert parser.getElementById('item1') is None, 'Expected to not be able to find id=item1 after remove'

        assert parser.getElementById('subItem1') is None, 'Expected to not be able to find sub item of id=item1, id=subItem1 after remove.'

        assert item1Em.parentNode is None , 'Expected parentNode on item1Em to be None after remove.'

        assert not itemsEm.contains(item1Em) , 'Expected itemsEm to not contain items1Em'
        assert not itemsEm.containsUid(item1Em.uid) , 'Expected itemsEm to not contain items1Em'
        assert not itemsEm.contains(subItem1) , 'Expected itemsEm to not contain subItem1'

        assert subItem1.uid not in itemsEm.getAllNodeUids()

        assert not parser.contains(item1Em) , 'Expected parser to not contain item1Em via contains'
        assert item1Em not in parser, 'Expected parser to not contain item1Em via in operator'

        assert item1Em.ownerDocument is None , 'Expected owner document to be unset upon removal'


    def test_createElement(self):
        parser = AdvancedHTMLParser()

        divEm = parser.createElement('div')

        assert isinstance(divEm, AdvancedTag) , 'Expected createElement to create an AdvancedTag element.'
        assert divEm.tagName == 'div' , 'Expected createElement to set tag name properly'

    def test_createElementFromHtml(self):

        divEm = AdvancedHTMLParser.createElementFromHTML('<div class="hello world" id="xdiv"> <span id="subSpan1"> Sub element </span> <span id="subSpan2"> Sub element2 </span> </div>')

        assert isinstance(divEm, AdvancedTag) , 'Expected createElementFromHtml to return an AdvancedTag element'
        assert divEm.tagName == 'div', 'Expected tagName to be set from parsed html'

        assert len(divEm.children) == 2 , 'Expected two children on div'

        assert divEm.getAttribute('id') == 'xdiv' , 'Expected id attribute to be set'
        assert divEm.className == 'hello world' , 'Expected className attribute to be set'

        assert divEm.children[0].id == 'subSpan1' , 'Expected child to be parsed and have id set'

        assert divEm.children[0].innerHTML.strip() == 'Sub element' , 'Expected text to be parsed'

        assert divEm.documentElement is None , 'Expected documentElement to not be set on standalone element'
        assert divEm.children[1].documentElement is None , 'Expected documentElement to not be set on standalone element, in sub.'

        gotException = False

        try:
            divEm = AdvancedHTMLParser.createElementFromHTML('<div id="oneDiv"> <span> Sub</span> </div><div id="twoDiv"></div>')
        except MultipleRootNodeException:
            gotException = True

        assert gotException is True , 'Expected to get MultipleRootNodeException when trying to pass several top-level elements to createElementFromHTML'

        divEm.appendInnerHTML('Hello World <div id="addedSubDiv">Yay</div>')

        print ( "Inner is:\n\n%s\n" %(divEm.innerHTML,))

        assert divEm.getElementById('addedSubDiv') , 'Expected to add a child element'
        assert 'Hello World' in divEm.innerHTML , 'Expected text to be added to innerHTML'

    def test_createElementsFromHtml(self):

        divEms = AdvancedHTMLParser.createElementsFromHTML('<div class="hello world" id="xdiv"> <span id="subSpan1"> Sub element </span> <span id="subSpan2"> Sub element2 </span> </div>')

        assert issubclass(divEms.__class__, (list, tuple)) , 'Expected to get a list returned from createElementsFromHTML'
        assert len(divEms) == 1 , 'Expected one element when one root element passed'

        divEm = divEms[0]

        assert isinstance(divEm, AdvancedTag) , 'Expected createElementFromHtml to return an AdvancedTag element'
        assert divEm.tagName == 'div', 'Expected tagName to be set from parsed html'

        assert len(divEm.children) == 2 , 'Expected two children on div'

        assert divEm.getAttribute('id') == 'xdiv' , 'Expected id attribute to be set'
        assert divEm.className == 'hello world' , 'Expected className attribute to be set'

        assert divEm.children[0].id == 'subSpan1' , 'Expected child to be parsed and have id set'

        assert divEm.children[0].innerHTML.strip() == 'Sub element' , 'Expected text to be parsed'

        assert divEm.documentElement is None , 'Expected documentElement to not be set on standalone element'
        assert divEm.children[1].documentElement is None , 'Expected documentElement to not be set on standalone element, in sub.'

        gotException = False

        try:
            divEms = AdvancedHTMLParser.createElementsFromHTML('<div id="oneDiv"> <span> Sub</span> </div><div id="twoDiv"></div>')
        except MultipleRootNodeException:
            gotException = True

        assert gotException is False , 'Expected NOT to get MultipleRootNodeException when trying to pass several top-level elements to createElementsFromHTML'

        assert len(divEms) == 2 , 'Expected to get two elements'

        assert divEms[0].id == 'oneDiv' , 'Got wrong ID on first element'

        assert divEms[1].id == 'twoDiv' , 'Got wrong ID on second element'

if __name__ == '__main__':
    sys.exit(subprocess.Popen('GoodTests.py -n1 "%s" %s' %(sys.argv[0], ' '.join(['"%s"' %(arg.replace('"', '\\"'), ) for arg in sys.argv[1:]]) ), shell=True).wait())
