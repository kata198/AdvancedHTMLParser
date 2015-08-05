#!/usr/bin/env GoodTests.py

import re
import subprocess
import sys

import AdvancedHTMLParser


class TestGeneral(object):
    '''
        A general test class. Basically example.py converted a bit.

        TODO: Add more specific testsfor everything
    '''

    def __init__(self):
        self.testHTML = '''
<html>
 <head>
  <title>HEllo</title>
 </head>
 <body>
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
    </div>
  </body>
</html>
'''

    def setup_TestGeneral(self):
        self.parser =  AdvancedHTMLParser.AdvancedHTMLParser()
        self.parser.parseStr(self.testHTML)

    def test_getItems(self):
        parser = self.parser

        items = parser.getElementsByName('items')
        assert len(items) == 5
        for  item in items:
            assert item.tagName == 'div'

    def test_correctTitle(self):
        parser = self.parser

        titleEms =  parser.getElementsByTagName('title')
        assert titleEms
        assert len(titleEms) == 1
        
        titleEm  =  titleEms[0]
        assert titleEm.innerHTML.strip() ==  'HEllo'

        assert titleEm.outerHTML.strip().replace(' ', '') == '<title>HEllo</title>'

    def _getItemsUnder(self, items, maxPrice):
        itemsUnder = []
        for item in items:
            priceEms =  item.getElementsByName('price')
            assert priceEms
            assert len(priceEms) == 1
            priceEm = priceEms[0]

            priceInner =  priceEm.innerHTML.strip()
            assert priceInner
            try:
                priceValue =  round(float(priceEm.innerHTML.strip()), 2)
            except:
                raise AssertionError('Failed to parse price  value, not a float? (%f)' %(priceValue,))
            if priceValue <  maxPrice:
                itemsUnder.append(item)

        return itemsUnder

    def _getItemName(self, item):
        peers = item.getElementsByName('itemName')
        assert peers
        assert len(peers) == 1

        return peers[0].innerHTML.strip()
        


    def test_advancedSearching(self):
        parser = self.parser
        items = parser.getElementsByName('items')
        assert items

        itemsUnderFour =  self._getItemsUnder(items, 4.00)
        assert len(itemsUnderFour) == 3

        names = [self._getItemName(item) for item in itemsUnderFour]
        for name in names:
            assert name
        
        names = set(names)

        assert 'Sponges' in names
        assert 'Turtles' in names
        assert 'Pudding Cups' in names
        assert 'Gold Brick' not in names

    def test_appendAndSearch(self):
        parser = AdvancedHTMLParser.AdvancedHTMLParser()
        parser.parseStr(self.testHTML)


        items = parser.getElementsByName('items')
        assert items

        cheapoItems =  self._getItemsUnder(items, .25)
        assert len(cheapoItems) == 0

        parser2 = AdvancedHTMLParser.AdvancedHTMLParser()
        parser2.parseStr('<div name="items"> <span name="itemName">Mint</span><span name="price">.19</span></div>')

        items[0].parentNode.appendChild(parser2.getRoot())

        items = parser.getElementsByName('items')
        assert items

        cheapoItems =  self._getItemsUnder(items, .25)
        assert len(cheapoItems) == 1

        assert self._getItemName(cheapoItems[0]) == 'Mint'

    def test_singleItemSearch(self):
        parser = AdvancedHTMLParser.AdvancedHTMLParser()
        parser.parseStr('<div id="theItem">Hello World</div>')

        theItemEm = parser.getElementById('theItem')
        assert theItemEm
        assert theItemEm.id == 'theItem'


if __name__ == '__main__':
    import subprocess
    import sys
    pipe  = subprocess.Popen('GoodTests.py "%s"' %(sys.argv[0],), shell=True).wait()
