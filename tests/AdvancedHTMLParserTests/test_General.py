#!/usr/bin/env GoodTests.py
'''
    Test some general parsing
'''

import subprocess
import sys

import AdvancedHTMLParser


class TestGeneral(object):
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
            assert item.tagName == 'div', 'Bad Tag name, should  have been DIV'

    def test_correctTitle(self):
        parser = self.parser

        titleEms =  parser.getElementsByTagName('title')
        assert titleEms, 'Failed to find elements with tag name, "Title"'
        assert len(titleEms) == 1, 'More than one element with name title found (%d), expected  1.'  %(len(titleEms),)
        
        titleEm  =  titleEms[0]
        assert titleEm.innerHTML.strip() ==  'HEllo', 'Bad innerHTML attribute, expected "HEllo"'

        assert titleEm.outerHTML.strip().replace(' ', '') == '<title>HEllo</title>' , 'Bad outerHTML, extpected "<title>HEllo</title>"'

    def _getItemsUnder(self, items, maxPrice):
        itemsUnder = []
        for item in items:
            priceEms =  item.getElementsByName('price')
            assert priceEms, 'Failed to find price elements'
            assert len(priceEms) == 1, 'Expected 1 price element, got %d' %(len(priceEms),)
            priceEm = priceEms[0]

            priceInner =  priceEm.innerHTML.strip()
            assert priceInner,  'Got blank innerHTML in price element'
            try:
                priceValue =  round(float(priceEm.innerHTML.strip()), 2)
            except:
                raise AssertionError('Failed to parse price  value, not a float? (%f)' %(priceValue,))
            if priceValue <  maxPrice:
                itemsUnder.append(item)

        return itemsUnder

    def _getItemName(self, item):
        itemNames = item.getElementsByName('itemName')
        assert itemNames, 'Failed to get item name subelement of: %s' %(item.outerHTML,)
        assert len(itemNames) == 1, 'Expected 1 item name  elements, got %d'  %(len(itemNames),)

        return itemNames[0].innerHTML.strip()
        


    def test_advancedSearching(self):
        parser = self.parser
        items = parser.getElementsByName('items')
        assert items, 'Failed to get items'

        itemsUnderFour =  self._getItemsUnder(items, 4.00)
        assert len(itemsUnderFour) == 3, 'Asserted to find 3 items under 4.00, but found %d' %(len(itemsUnderFour),)

        names = [self._getItemName(item) for item in itemsUnderFour]
        for name in names:
            assert name , 'Expected name not to be blank'
        
        names = set(names)

        assert 'Sponges' in names , 'Expected to find Sponges'
        assert 'Turtles' in names , 'Expected to find  Turtles'
        assert 'Pudding Cups' in names ,  'Expected to find Pudding Cups'
        assert 'Gold Brick' not in names , 'Expected NOT TO find Gold Brick'

    def test_appendAndSearch(self):
        parser = AdvancedHTMLParser.AdvancedHTMLParser()
        parser.parseStr(self.testHTML)


        items = parser.getElementsByName('items')
        assert items , 'Should have found name=items in %s' %(parser.getHTML(),)

        cheapoItems =  self._getItemsUnder(items, .25)
        assert len(cheapoItems) == 0 ,  'Expected  to find  0 items under .25'

        parser2 = AdvancedHTMLParser.AdvancedHTMLParser()
        parser2.parseStr('<div name="items"> <span name="itemName">Mint</span><span name="price">.19</span></div>')

        items[0].parentNode.appendChild(parser2.getRoot())

        items = parser.getElementsByName('items')
        assert items , 'Should have found name=items in %s' %(parser.getHTML(),)

        cheapoItems =  self._getItemsUnder(items, .25)
        assert len(cheapoItems) == 1 ,  'Expected to find 1 item under  .25'

        assert self._getItemName(cheapoItems[0]) == 'Mint'

    def test_singleItemSearch(self):
        parser = AdvancedHTMLParser.AdvancedHTMLParser()
        parser.parseStr('<div id="theItem">Hello World</div>')

        theItemEm = parser.getElementById('theItem')
        assert theItemEm , 'Expected  to find div id="theItem"'
        assert theItemEm.id == 'theItem' , 'Expected it  to be "theItem"'


    def test_withAttrValues(self):
        parser = AdvancedHTMLParser.AdvancedHTMLParser()
        parser.parseStr(self.testHTML)


        results = parser.getElementsWithAttrValues('src', set(['/abc.gif', '/abc2.gif']))

        assert len(results) == 2 , 'Expected two results'

        assert results[0].tagName == 'img' and results[1].tagName == 'img' , 'Expected to get two images'   


if __name__ == '__main__':
    subprocess.Popen('GoodTests.py "%s"' %(sys.argv[0],), shell=True).wait()
