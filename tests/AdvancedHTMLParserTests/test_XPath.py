#!/usr/bin/env GoodTests.py
'''
    Test some xpath!
'''

import subprocess
import sys

import AdvancedHTMLParser

from AdvancedHTMLParser.xpath._body import parseBodyStringIntoBodyElements, BodyElementValue, BodyElementValue_Boolean

class TestXPath(object):
    '''
        xpath is way better than ypath
    '''

    def setup_class(self):
        self.testHTML = '''<!DOCTYPE html>
<html>
  <head>
    <title>HEllo</title>
  </head>
  <body>
    <div id="container1" class="abc" >
      <div name="items" id="item1" >
        <span name="price" >1.96</span>
        <span name="itemName" >Sponges</span>
      </div>
      <div name="items" id="item2" >
        <span name="price" >3.55</span>
        <span name="itemName" >Turtles</span>
      </div>
      <div name="items" id="item3" >
        <span name="price" class="something" >6.55</span>
        <img src="/images/cheddar.png" style="width: 64px; height: 64px;" />
        <span name="itemName">Cheese</span>
      </div>
    </div>
    <div id="images">
      <img src="/abc.gif" name="image" />
      <img src="/abc2.gif" name="image" />
    </div>
    <div id="saleSection" style="background-color: blue" >
      <div name="items" id="item4" >
        <span name="itemName" >Pudding Cups</span>
        <span name="price" >1.60</span>
      </div>
      <hr />
      <div name="items" class="limited-supplies" id="item5" >
        <span name="itemName">Gold Brick</span>
        <span name="price">214.55</span>
        <b style="margin-left: 10px">LIMITED QUANTITIES: <span id="item_5123523_remain">130</span></b>
      </div>
    </div>
  </body>
</html>
'''

    def setup_TestXPath(self):
        '''
            setup_TestXPath - Perform a one-time setup of this class (parse the test HTML into a parser.AdvancedHTMLParser document)

                Sets self.parser <Parser.AdvancedHTMLParser> = the parsed document
        '''
        self.parser =  AdvancedHTMLParser.AdvancedHTMLParser()
        self.parser.parseStr(self.testHTML)


    def test_xpathGetDivsAnyLevel(self):
        '''
            test_getDivsAnyLevel - Tests using xpath to get all divs as any descendent of root <html>
        '''
        # Grab directly from document
        allDivs = self.parser.getElementsByXPathExpression('''//div''')

        # Check that return is expected type -- TagCollection
        assert isinstance(allDivs, AdvancedHTMLParser.TagCollection) is True, \
                'Expected Parser.AdvancedHTMLParser.getElementsByXPathExpression to return a TagCollection object, but got: < %s . ( %s )' % \
                    ( \
                        allDivs.__class__.__name__, \
                        str( type( allDivs ) ), \
                    )

        # Check that we got the right number of elements
        assert len(allDivs) == 8 , 'Expected to find 8 divs in xpath expression, but found %d. Divs were:  %s' % ( len(allDivs), repr(allDivs) )


        # Assemble all divs with id="itemN", and sort by id so we can validate
        foundDivItemsWithItemIds = sorted( [ divEm for divEm in allDivs if (divEm.id or '').startswith('item') ], key = lambda em : em.id )
        assert len(foundDivItemsWithItemIds) == 5 , 'Expected to find 5 divs from xpath expression "//div" where "id" attribute starts with "item". Got %d, with ids= %s' % \
            ( \
                len(foundDivItemsWithItemIds),
                repr( [ (em.id or '') for em in foundDivItemsWithItemIds ] ),
            )

        # Iterate over expected item #s and assert we have found the matching div
        curNum = 1
        curIdx = 0

        while curNum <= 5:

            curDiv = foundDivItemsWithItemIds[curIdx]

            expectedId = ( "item" + str(curNum) )
            foundId = ( curDiv.id or '' )
            assert foundId == expectedId , 'Expected matched id="itemN" divs sorted by id (0-origin) index %d to have an id of %s, but found: %s.' % \
                (
                    curIdx,
                    expectedId,
                    foundId,
                )

            curNum += 1
            curIdx += 1


    def test_xpathGetWithNameSelector(self):
        '''
            test_xpathGetWithNameSelector - Test running an XPath expression against the test HTML, selecting where a div has a specific "name" attribute
        '''

        allItemsDivs = self.parser.getElementsByXPathExpression('''//div[@name="items"]''')

        # Check that return is expected type -- TagCollection
        assert isinstance(allItemsDivs, AdvancedHTMLParser.TagCollection) is True, \
                'Expected Parser.AdvancedHTMLParser.getElementsByXPathExpression to return a TagCollection object, but got: < %s . ( %s )' % \
                    ( \
                        allItemsDivs.__class__.__name__, \
                        str( type( allItemsDivs ) ), \
                    )

        # Check that we got the right number of elements
        assert len(allItemsDivs) == 5 , 'Expected to find 5 divs in xpath expression  (( //div[@name="items"] )), but found %d. Divs were:  %s' % ( len(allItemsDivs), repr(allItemsDivs) )


        # Now, try with single quotes instead of double quotes
        allItemsDivs2 = self.parser.getElementsByXPathExpression('''//div[@name='items']''')


        assert allItemsDivs == allItemsDivs2 , "Expected to get same set of results whether using single quotes or double quotes in the \"name\" attribute selector.\nallItemsDivs (double quotes)  =  %s\nallItemsDivs2 (single quote)  =  %s\n" %( repr(allItemsDivs), repr(allItemsDivs2) )

        # Assemble all divs with id="itemN", and sort by id so we can validate
        foundDivItemsWithItemIds = sorted( [ divEm for divEm in allItemsDivs if (divEm.id or '').startswith('item') ], key = lambda em : em.id )
        assert len(foundDivItemsWithItemIds) == 5 , 'Expected to find 5 divs from xpath expression "//div" where "id" attribute starts with "item". Got %d, with ids= %s' % \
            ( \
                len(foundDivItemsWithItemIds),
                repr( [ (em.id or '') for em in foundDivItemsWithItemIds ] ),
            )

        # Iterate over expected item #s and assert we have found the matching div
        curNum = 1
        curIdx = 0

        while curNum <= 5:

            curDiv = foundDivItemsWithItemIds[curIdx]

            expectedId = ( "item" + str(curNum) )
            foundId = ( curDiv.id or '' )
            assert foundId == expectedId , 'Expected matched id="itemN" divs sorted by id (0-origin) index %d to have an id of %s, but found: %s.' % \
                (
                    curIdx,
                    expectedId,
                    foundId,
                )

            curNum += 1
            curIdx += 1


    def test_xpathGetRootHtml(self):
        '''
            test_xpathGetRootHtml - Test that  selecting something on the root <html> nodw works as expected,

              rather than starting at the next tag down (<body> and <head>)
        '''
        bodyNodes = self.parser.getElementsByXPathExpression('''/body[1]''')
        assert bodyNodes and len(bodyNodes) == 1 , 'Expected to get one <body> node at 1-origin index=1 using "/body[1]". Got: %s' %(repr(bodyNodes), )

        bodyNodes2 = self.parser.getElementsByXPathExpression('''//body[1]''')
        assert bodyNodes2 and len(bodyNodes2) == 1 , 'Expected to get one <body> node at 1-origin index=1 using "//body[1]". Got: %s' %(repr(bodyNodes2), )

        assert bodyNodes == bodyNodes2 , 'Expected "/body[1]" and "//body[1]" to return the same thing when one <body> is present within the document, being executed from <html>'

        bodyNodes3 = self.parser.getElementsByXPathExpression('''/body''')
        assert bodyNodes3 and len(bodyNodes3) == 1 , 'Expected to get one <body> node at 1-origin index=1 using "/body". Got: %s' %(repr(bodyNodes3), )

        assert bodyNodes2 == bodyNodes3 , 'Expected "/body[1]" and "/body" to return the same thing when one <body> is present within the document, being executed from <html>'

        bodyNodes4 = self.parser.getElementsByXPathExpression('''//body''')
        assert bodyNodes4 and len(bodyNodes4) == 1 , 'Expected to get one <body> node at 1-origin index=1 using "//body". Got: %s' %(repr(bodyNodes4), )

        assert bodyNodes3 == bodyNodes4 , 'Expected "//body" and "/body" to return the same thing when one <body> is present within the document, being executed from <html>'


        htmlNodes = self.parser.getElementsByXPathExpression('''//html[1]''')
        assert htmlNodes and len(htmlNodes) == 1 , 'Expected to get one <html> element from root of parsed document with  single root <html> node, using xpath "//html[1]". Got: %s' %( repr(htmlNodes), )


    def test_xpathParentInExpression(self):
        '''
            test_xpathParentInExpression - Test some xpath expressions which include parent::
        '''

        itemsThatAreTurtles = self.parser.getElementsByXPathExpression('''//*[ @name = "itemName" ][normalize-space() = "Turtles"]/parent::div''')

        assert len(itemsThatAreTurtles) == 1 , 'Expected to find one turtle item, but got: %s' %(repr(itemsThatAreTurtles), )

        itemThatIsTurtles = itemsThatAreTurtles[0]
        assert itemThatIsTurtles.tagName == 'div' , 'Expected parent::div to be a div, but it was a %s' %( itemThatIsTurtles.tagName, )
        assert itemThatIsTurtles.id == 'item2' , 'Expected id="item2" to be the id of the matched element'

        # Now break it into multiple expressions, and we will use the TagCollection for second root set
        itemsNames = self.parser.getElementsByXPathExpression('''//*[ @name = "itemName" ]''')

        itemsThatAreTurtles = itemsNames.getElementsByXPathExpression('''/*[normalize-space() = "Turtles"]/parent::div''')

        assert len(itemsThatAreTurtles) == 1 , 'Expected to find one turtle item, but got: %s' %(repr(itemsThatAreTurtles), )

        itemThatIsTurtles = itemsThatAreTurtles[0]
        assert itemThatIsTurtles.tagName == 'div' , 'Expected parent::div to be a div, but it was a %s' %( itemThatIsTurtles.tagName, )
        assert itemThatIsTurtles.id == 'item2' , 'Expected id="item2" to be the id of the matched element'


    def test_xpathBooleanAnd(self):
        '''
            test_xpathBooleanAnd - Test the "and" boolean operator
        '''
        itemsThatAreTurtles = self.parser.getElementsByXPathExpression('''//*[ @name = "itemName" and normalize-space() = "Turtles"]/parent::div''')

        assert len(itemsThatAreTurtles) == 1 , 'Expected to find one turtle item, but got: %s' %(repr(itemsThatAreTurtles), )

        itemThatIsTurtles = itemsThatAreTurtles[0]
        assert itemThatIsTurtles.tagName == 'div' , 'Expected parent::div to be a div, but it was a %s' %( itemThatIsTurtles.tagName, )
        assert itemThatIsTurtles.id == 'item2' , 'Expected id="item2" to be the id of the matched element'


        itemsThatAreNotTurtles = self.parser.getElementsByXPathExpression('''//*[ @name = "itemName" and normalize-space() != "Turtles" ]/parent::div''')

        assert len(itemsThatAreNotTurtles) == 4 , 'Expected to find four non-turtle items, but got %d: %s' %( len(itemsThatAreNotTurtles), repr(itemsThatAreNotTurtles))

        assert itemThatIsTurtles not in itemsThatAreNotTurtles , 'Expected not to find the item already identified as turtles in the not turtles list, but did!'

        turtleDoubleCheck = [ itemEm for itemEm in itemsThatAreNotTurtles if itemEm.id == "item2" ]
        assert len(turtleDoubleCheck) == 0 , 'Expected to not find id="item2" (the turtle) in non-turtles expression, but did!'


    def test_xpathBooleanOr(self):
        '''
            test_xpathBooleanOr - Test the "or" boolean operator
        '''
        items2or3 = self.parser.getElementsByXPathExpression('''//*[ @id = "item2" or @id="item3"      ]''')

        assert len(items2or3) == 2 , 'Expected to find two items for expression ( @id="item2" or @id="item3" ), but found %d. %s' %(len(items2or3), repr(items2or3))

        item2Em = self.parser.getElementById('item2')
        assert item2Em , 'Expected to find item by id="item2" but did not.'
        item3Em = self.parser.getElementById('item3')
        assert item3Em , 'Expected to find item by id="item3" but did not.'

        assert item2Em in items2or3 , 'Expected to find element returned by getElementById("item2") in result for xpath expression of the same, but did not.'
        assert item3Em in items2or3 , 'Expected to find element returned by getElementById("item3") in result for xpath expression of the same, but did not.'


    def test_xpathConcatFunction(self):
        '''
            test_xpathConcatFunction - Test string concatenation via fn::concat
        '''

        item2Ems = self.parser.getElementsByXPathExpression('''//*[ @id = concat("ite", "m2") ]''')
        assert len(item2Ems) == 1 , 'Expected to find one element with "id" attribute as concatenated via function "ite" + "m2" , or "item2", but got: %s' %(repr(item2Ems), )

        item2Em = item2Ems[0]
        assert item2Em.id == "item2"


        item3Ems = self.parser.getElementsByXPathExpression('''//*[ @id = concat("it", "em", "3") ]''')
        assert len(item3Ems) == 1 , 'Expected to find one element with "id" attribute as concatenated via function "it" + "em" + "3" , or "item3", but got: %s' %(repr(item3Ems), )

        item3Em = item3Ems[0]
        assert item3Em.id == "item3"

        noSuchItemEms = self.parser.getElementsByXPathExpression('''//*[ @id = concat("no", "Such", "Item") ]''')
        assert len(noSuchItemEms) == 0 , 'Expected to find no elements with "id" attribute as concatenated via function "no" + "Such" + "Item" , or "noSuchItem", but got: %s' %(noSuchItemEms, )


        allItems = self.parser.getElementsByXPathExpression('''//*[@name = concat("i", "t", "em", "s")]''')
        assert len(allItems) == 5 , 'Expected to find 5 elements with "name" attribute as concatenated via function "i" + "t" + "em" + "s" , or "items", but got %d elements. %s' %( len(allItems), repr(allItems) )
        for item in allItems:
            assert item.name == "items" , 'Expected all items returned by concatenated "items" string to have "name" attribute be "items", but element had name %s. Tag was: %s' %( item.name, item.getStartTag() )


    def test_xpathConcatOperator(self):
        '''
            test_xpathConcatOperator - Test string concatenation via operator "||"
        '''
        item2Ems = self.parser.getElementsByXPathExpression('''//*[ @id = "ite" || "m2" ]''')
        assert len(item2Ems) == 1 , 'Expected to find one element with "id" attribute as concatenated via operator "ite" + "m2" , or "item2", but got: %s' %(repr(item2Ems), )

        item2Em = item2Ems[0]
        assert item2Em.id == "item2"

        item3Ems = self.parser.getElementsByXPathExpression('''//*[ @id = "it" || "em" || "3" ]''')
        assert len(item3Ems) == 1 , 'Expected to find one element with "id" attribute as concatenated via operator "it" + "em" + "3" , or "item3", but got: %s' %(repr(item3Ems), )

        item3Em = item3Ems[0]
        assert item3Em.id == "item3"

        noSuchItemEms = self.parser.getElementsByXPathExpression('''//*[ @id = "no" || "Such" || "Item" ]''')
        assert len(noSuchItemEms) == 0 , 'Expected to find no elements with "id" attribute as concatenated via operator "no" + "Such" + "Item" , or "noSuchItem", but got: %s' %(noSuchItemEms, )


        allItems = self.parser.getElementsByXPathExpression('''//*[@name = "i" || "t" || "em" || "s"]''')
        assert len(allItems) == 5 , 'Expected to find 5 elements with "name" attribute as concatenated via operator "i" + "t" + "em" + "s" , or "items", but got %d elements. %s' %( len(allItems), repr(allItems) )
        for item in allItems:
            assert item.name == "items" , 'Expected all items returned by concatenated "items" string to have "name" attribute be "items", but element had name %s. Tag was: %s' %( item.name, item.getStartTag() )


    def test_xpathLast(self):
        '''
            test_xpathLast - Test the "last()" function
        '''

        # This should match 3 spans which are item names, and two prices.
        results = self.parser.getElementsByXPathExpression('''//div[@name = "items"]/span[last()]''')

        assert len(results) == 5 , 'Expected 5 results, got %d. %s' %(len(results), repr(results))

        assert len( [x for x in results if x.name == 'itemName' ] ) == 3 , 'Expected 3 name="itemName" . Got: %s' %(repr(results), )
        assert len( [x for x in results if x.name == 'price' ] ) == 2 , 'Expected 2 name="price" . Got: %s' %(repr(results), )

        # Now, try to find the spans another way, and compare that we get the same results

        itemsEms = self.parser.getElementsByTagName('div').getElementsByName('items')

        lastSpans = [ [ child for child in itemsEm.children if child.tagName == 'span' ][-1] for itemsEm in itemsEms ]

        assert len(lastSpans) == 5 , 'Expected to get 5 span results from non-xpath method. Got: %s' %( repr(lastSpans), )

        for lastSpan in lastSpans:

            assert lastSpan in results , 'Got a mismatch of results from xpath vs non-xpath. Node  (  %s  ) was found via non-xpath, but not in the xpath set!' %(repr(lastSpan), )


    def test_parseOptimizations1(self):
        '''
            test_parseOptimizations1 - Test that we properly optimize xpath strings with values that can be calculated at parse time
        '''

        bodyElements = parseBodyStringIntoBodyElements('''"hello" || " " || "world" = "hello world"''')

        assert len(bodyElements) == 1 , 'Expected parsed string to be optimized to a single value. Got: %s' %(repr(bodyElements), )

        bodyElement = bodyElements[0]

        assert issubclass(bodyElement.__class__, BodyElementValue) , 'Expected parsed string to be optimized to a single BodyElementValue. Got: %s' %(bodyElement.__class__.__name__, )

        value = bodyElement.getValue()
        assert value is True , 'Expected the calculated BodyElementValue to be <bool> True. Got: <%s> %s' %( type(value).__name__, repr(value))


if __name__ == '__main__':
    sys.exit(subprocess.Popen('GoodTests.py -n1 "%s" %s' %(sys.argv[0], ' '.join(['"%s"' %(arg.replace('"', '\\"'), ) for arg in sys.argv[1:]]) ), shell=True).wait())

# vim: set ts=4 st=4 sw=4 expandtab :
