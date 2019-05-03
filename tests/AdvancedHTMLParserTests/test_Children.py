#!/usr/bin/env GoodTests.py
'''
    test_Children - Test some child-related tag stuff
'''

import subprocess
import sys

import AdvancedHTMLParser

from AdvancedHTMLParser import isTextNode, isTagNode


class TestChildren(object):
    '''
        A general test class. Basically example.py converted a bit.

    '''

    def setup_class(self):
        self.testHTML = '''
<html>
 <head>
  <title>HEllo</title>
 </head>
 <body>
   Welcome to my website!
   <div id="container1" class="abc">
     <div name="items">
      <span name="price">1.96</span>
      <span name="itemName">Sponges</span>
     </div>
     <div name="items">
       <span name="price">3.55</span>
       <span name="itemName">Turtles</span>
     </div>
     <div name="items">
       <span name="price" class="something" >6.55</span>
       <img src="/images/cheddar.png" style="width: 64px; height: 64px;" />
       <span name="itemName">Cheese</span>
     </div>
   </div>
   <div id="images">
     <img src="/abc.gif" name="image" />
     <img src="/abc2.gif" name="image" />
  </div>
  <div id="saleSection" style="background-color: blue">
    <div name="items">
      <span name="itemName">Pudding Cups</span>
      <span name="price">1.60</span>
    </div>
    <hr />
    <div name="items" class="limited-supplies" >
      <span name="itemName">Gold Brick</span>
      <span name="price">214.55</span>
      <b style="margin-left: 10px">LIMITED QUANTITIES: <span id="item_5123523_remain">130</span></b>
      Some other text
    </div>
  </body>
</html>
'''

    def _getDocument(self):
        parser =  AdvancedHTMLParser.AdvancedHTMLParser()
        parser.parseStr(self.testHTML)

        return parser

    def test_getBlocks(self):
        document = self._getDocument()

        blocks = document.body.getChildBlocks()

        # Hack for first block being empty block? TODO: Look into this
        while blocks[0] == '':
            blocks = blocks[1:]

        assert isTextNode(blocks[0]) , 'Expected first block to be a text node'
        assert 'Welcome to my website!' in blocks[0] , 'Expected first block inside body to be a text node. Got: %s' %(repr(blocks[0]), )

        assert isTagNode(blocks[1]) , 'Expected second block to be a tag'

        divEm = blocks[1]

        assert divEm.tagName == 'div' , 'Expected second block to be a div tag'
        assert divEm.id == 'container1' , 'Got wrong div tag.'

        assert len([block for block in blocks if isTagNode(block) or block.strip()]) == 4 , 'Expected to get 4 non-empty blocks'


    def test_getChildren(self):
        document = self._getDocument()

        children = document.body.getChildren()

        divEm = children[0]

        assert divEm.tagName == 'div' , 'Expected second block to be a div tag'
        assert divEm.id == 'container1' , 'Got wrong div tag.'

        assert len(children) == 3 , 'Expected 3 children'

        for i in range(len(children)):
            child = children[i]
            assert isTagNode(child) , 'Expected all nodes returned to be AdvancedTag\'s. On object %d got:  %s' %(i, child.__class__.__name__)





if __name__ == '__main__':
    sys.exit(subprocess.Popen('GoodTests.py -n1 "%s" %s' %(sys.argv[0], ' '.join(['"%s"' %(arg.replace('"', '\\"'), ) for arg in sys.argv[1:]]) ), shell=True).wait())
