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

    def test_escapeQuotes(self):
        tag = AdvancedHTMLParser.AdvancedTag('div')

        tag.setAttribute('onclick', 'alert("hi");')

        assert 'onclick="alert(&quot;hi&quot;);"' in tag.outerHTML , 'Expected to escape quotes in attribute. Got: %s' %(tag.outerHTML, )

    def test_getBody(self):
        parser = AdvancedHTMLParser.AdvancedHTMLParser()
        parser.parseStr(self.testHTML)

        bodyEm = parser.body

        assert bodyEm , 'Expected ".body" property to fetch an element'
        assert bodyEm.tagName == 'body' , 'Got wrong body element'

        parser = AdvancedHTMLParser.AdvancedHTMLParser()
        parser.parseStr('<div id="hello"> <span> One </span> </div>')

        bodyEm = parser.body

        assert not bodyEm , 'Expected to find no "body" when no <body> tag is present.'

        parser = AdvancedHTMLParser.AdvancedHTMLParser()
        parser.parseStr('<div id="hello"> <span> One </span> </div> <div id="other">Cheese</div>')

        bodyEm = parser.body

        assert not bodyEm , 'Expected to find no "body" when no <body> tag is present.'


    def test_getHead(self):
        parser = AdvancedHTMLParser.AdvancedHTMLParser()
        parser.parseStr(self.testHTML)

        headEm = parser.head

        assert headEm , 'Expected ".head" property to fetch an element'
        assert headEm.tagName == 'head' , 'Got wrong head element'

        parser = AdvancedHTMLParser.AdvancedHTMLParser()
        parser.parseStr('<div id="hello"> <span> One </span> </div>')

        headEm = parser.head

        assert not headEm , 'Expected to find no "head" when no <head> tag is present.'

        parser = AdvancedHTMLParser.AdvancedHTMLParser()
        parser.parseStr('<div id="hello"> <span> One </span> </div> <div id="other">Cheese</div>')

        headEm = parser.head

        assert not headEm , 'Expected to find no "head" when no <head> tag is present.'

    def test_getForms(self):
        document = AdvancedHTMLParser.AdvancedHTMLParser()
        document.parseStr('''<html>
        <head> <title>Hello</title></head>
        <body>
            <div id="mainDiv">
                <form id="form1" method="PUT" action="putItem.py">
                    <input id="input1" />
                </form>
                <div>
                    <form id="form2" method="GET" action="getItem.py">
                        <input id="input2" />
                    </form>
                </div>
            </div>
        </body>
</html>
''')
        formEms = document.forms

        assert len(formEms) == 2 , 'Expected to find 2 form elements'

        assert formEms[0].id == 'form1' , 'Expected to find form1 first'
        assert formEms[1].id == 'form2' , 'Expected to find form2 second'

        assert issubclass(formEms.__class__, AdvancedHTMLParser.TagCollection) , 'Expected result of document.forms to be a TagCollection'

        try:
            assert formEms.filter(id='form1').all() == [formEms[0]] , 'Expected filtering to work on TagCollection returned from document.forms'
        except ImportError:
            sys.stderr.write('WARNING: .filter is disabled via ImportError. QueryableList not installed?\n\n')



if __name__ == '__main__':
    sys.exit(subprocess.Popen('GoodTests.py -n1 "%s" %s' %(sys.argv[0], ' '.join(['"%s"' %(arg.replace('"', '\\"'), ) for arg in sys.argv[1:]]) ), shell=True).wait())
