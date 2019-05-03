#!/usr/bin/env GoodTests.py
'''
    Test various attribute related things
'''

import sys
import subprocess

from AdvancedHTMLParser.Tags import AdvancedTag, isValidAttributeName
from AdvancedHTMLParser.Parser import AdvancedHTMLParser
from AdvancedHTMLParser.SpecialAttributes import StyleAttribute


class TestAttributes(object):
    '''
        Tests some attribute behaviour
    '''

    def test_setAttribute(self):
        '''
            test_setAttribute - Tests the AdvancedTag.setAttribute function
        '''
        tag = AdvancedTag('div')

        tag.setAttribute('id', 'abc')

        assert tag.getAttribute('id') == 'abc' , 'Expected id to be abc'

        assert tag.getAttribute('blah') == None , 'Expected unset attribute to return None, actually returned %s' %(tag.getAttribute('blah'),)

        # Try to set some invalid attribute names, and assure we get a KeyError

        # Invalid symbol
        gotRightException = False
        try:
            tag.setAttribute('x;', 'hello')
        except KeyError:
            gotRightException = True

        assert gotRightException is True, 'Failed to raise KeyError on setAttribute of invalid name: "x;"'

        # Does not start with alpha
        gotRightException = False
        try:
            tag.setAttribute('9chan', 'yes')
        except KeyError:
            gotRightException = True

        assert gotRightException is True, 'Failed to raise KeyError on setAttribute of invalid name: "9chan"'


    def test_isValidAttributeName(self):
        '''
            test_isValidAttributeName - Tests the attribute name validator
        '''
        def testExpectValid(validNames):
            '''
                testExpectValid - Expect names to be valid
            '''

            for validName in validNames:

                assert isValidAttributeName(validName) is True , 'Expected attribute name validator to return that "%s" IS a valid attribute name, but it failed validation.' %(validName, )


        def testExpectInvalid(invalidNames):
            '''
                testExpectInvalid - Expect names to be invalid
            '''

            for invalidName in invalidNames:

                assert isValidAttributeName(invalidName) is False , 'Expected attribute name validator to return that "%s" is not a valid attribute name, but it passed validation.' %(invalidName, )


        # Test a few common valid names
        testExpectValid( ('id', 'name', 'class', 'aria-data') )

        # Test a few less common but still valid names
        testExpectValid( ('attr99', '_', '_test', 'x-', 'my_attr') )

        # Must start with alpha or underscore
        testExpectInvalid( ('9chan', '-world', '+3', ';') )

        # Must not contain invalid characters
        testExpectInvalid( ( 'r&b', 'k+a', 'hello/world', 'cheese(mega)', 'blah[4]') )



    def test_getElementsByAttr(self):
        '''
            test_getElementsByAttr - Tests the getElementsByAttr function
        '''
        html = """<html> <head> <title> Hello </title> </head>
<body>
    <div cheese="cheddar" id="cheddar1" >
        <span> Hello </span>
    </div>
    <div cheese="bologna" id="not_really_cheese">
        <span cheese="cheddar" id="cheddar2" > Goodbye </span>
    </div>
</body>
</html>"""
        parser = AdvancedHTMLParser()
        parser.parseStr(html)

        elements = parser.getElementsByAttr('cheese', 'cheddar')
        assert len(elements) == 2

        foundCheese1 = foundCheese2 = False
        for element in elements:
            myID = element.getAttribute('id')
            if myID == 'cheddar1':
                foundCheese1 = True
            elif myID == 'cheddar2':
                foundCheese2 = True

        assert foundCheese1
        assert foundCheese2


    def test_getAttributesList(self):
        parser = AdvancedHTMLParser()

        parser.parseStr('<div id="hello" style="display: none; width: 500px; padding-left: 15px;" class="One Two" data="Yes">Hello</div>')

        helloEm = parser.getElementById('hello')

        assert helloEm.getAttribute('id', '') == 'hello' , 'Got unxpected element'

        attributesList = helloEm.getAttributesList()

        foundId = False
        foundStyle = False
        foundClass = False
        foundData = False

        for attrName, attrValue in attributesList:
            if attrName == 'id':
                assert attrValue == 'hello' , 'Attribute "id" did not have expected value "hello", got "%s"' %(attrValue,)

                foundId = True
            elif attrName == 'style':

                style = StyleAttribute(attrValue)
                assert style.display == 'none', 'Got unexpected value for display in style copy. Expected "none", got "%s"' %(style.display,)
                assert style.width == '500px' , 'Got unexpected value for width in style copy. Expected "500px", got "%s"' %(style.width,)
                assert style.paddingLeft == '15px', 'Got unexpected value for padding-left. Expected "15px", got "%s"' %(style.paddingLeft, )

                foundStyle = True
            elif attrName == 'class':

                assert attrValue == 'One Two', 'Expected class name to equal "One Two", got: %s' %(attrValue, )

                foundClass = True
            elif attrName == 'data':

                assert attrValue == 'Yes', 'Expected attribute "data" to have the value "Yes", got: %s' %(attrValue, )

                foundData = True

            else:
                raise AssertionError('Got unexpected attribute in copy: (%s, %s)' %(attrName, attrValue))


        assert foundId is True , 'Did not find id element in attribute list'
        assert foundStyle is True , 'Did not find style element in attribute list'
        assert foundClass is True , 'Did not find class element in attribute list'
        assert foundData is True , 'Did not find data element in attribute list'

        # Test that we have a COPY, not the originals

        for item in attributesList:
            if item[0] == 'style':
                # Just incase in the future we want to include a StyleAttribute instead of the str
                if not isinstance(item[1], StyleAttribute):
                    style = StyleAttribute(item[1])
                else:
                    style = item[1]
                style.paddingTop = '10px'



        # These should not be modified in the original element
        assert 'padding-top' not in str(helloEm.style)
#        parser.parseStr('<div id="hello" style="display: none; width: 500px; padding-left: 15px;" class="One Two" data="Yes">Hello</div>')

    def test_attributesCase(self):
        '''
            test_attributesCase - Test that getAttribute and setAttribute force lowercase for keys
        '''

        em = AdvancedTag('input')

        em.setAttribute('MaXlEnGtH', '5')

        html = str(em)

        assert 'maxlength="5"' in html , 'Expected setAttribute to lowercase the key before setting. Got: ' + html

        assert em.getAttribute('MAXlength', None) == '5' , 'Expected getAttribute to lowercase the key before setting.'

        assert em.hasAttribute('maXlenGTH') is True , 'Expected hasAttribute to lowercase the key'

        assert 'MaxLength' in em.attributes , 'Expected "in" operator to lowercase the key'

    def test_getAttributesDict(self):
        parser = AdvancedHTMLParser()

        parser.parseStr('<div id="hello" style="display: none; width: 500px; padding-left: 15px;" class="One Two" data="Yes">Hello</div>')

        helloEm = parser.getElementById('hello')

        assert helloEm.getAttribute('id', '') == 'hello' , 'Got unxpected element'

        attributesDict = helloEm.getAttributesDict()

        assert 'id' in attributesDict , 'Did not find "id" in the attributes dict copy'
        assert 'style' in attributesDict , 'Did not find "style" in the attributes dict copy'
        assert 'class' in attributesDict , 'Did not find "class" in the attributes dict copy'
        assert 'data' in attributesDict , 'Did not find "data" in the attributes dict copy'

        assert len(attributesDict.keys()) == 4 , 'Got unexpected keys in attributesDict. Only expected "id" "style" "class" and "data", got: "%s"' %(repr(attributesDict),)

        assert attributesDict['id'] == 'hello' , 'Attribute "id" did not have expected value "hello", got "%s"' %(attributesDict['id'],)

        style = StyleAttribute(attributesDict['style'])
        assert style.display == 'none', 'Got unexpected value for display in style copy. Expected "none", got "%s"' %(style.display,)
        assert style.width == '500px' , 'Got unexpected value for width in style copy. Expected "500px", got "%s"' %(style.width,)
        assert style.paddingLeft == '15px', 'Got unexpected value for padding-left. Expected "15px", got "%s"' %(style.paddingLeft, )

        assert attributesDict['class'] == 'One Two', 'Got unexpected value for "class" in dict copy. Expected "One Two", Got: "%s"' %(attributesDict['class'], )

        assert attributesDict['data'] == 'Yes' , 'Got unexpected value for "data" in dict copy, Expected "Yes", Got: "%s"' %(attributesDict['data'], )

        # Assert we aren't modifying the original element
        style.paddingTop = '13em'

        assert helloEm.style.paddingTop != '13em' , 'Expected getAttributesDict to return copies, but modified original element on "style"'

        attributesDict['class'] += ' Three'

        assert 'Three' not in helloEm.getAttribute('class') , 'Expected getAttributesDict to return copies, but modified original element on "class"'

        attributesDict['id'] = 'zzz'

        assert helloEm.getAttribute('id') != 'zzz' , 'Expected getAttributesDict to return copies, but modified original element on "id"'



    def test_setAttributes(self):
        tag = AdvancedTag('div')
        tag.setAttributes( {
            'id' : 'abc',
            'name'  :  'cheese',
            'x-attr' : 'bazing'
        })

        assert tag.getAttribute('id') == 'abc'
        assert tag.getAttribute('name') == 'cheese'
        assert tag.getAttribute('x-attr') == 'bazing'

    def test_specialAttributes(self):
        tag = AdvancedTag('div')
        tag.setAttribute('style', 'position: absolute')
        styleValue = str(tag.getAttribute('style'))
        styleValue = styleValue.strip()
        assert styleValue == 'position: absolute' , 'Expected position: absolute, got %s' %(str(tag.getAttribute('style')),)

        tag.className = 'one two'
        assert str(tag.className).strip() == 'one two' , 'Expected classname to be "one two", got %s' %(repr(str(tag.className).strip()),)

    def test_specialAttributesInHTML(self):
        tag = AdvancedTag('div')
        tag._attributes['style'] = 'position: absolute; color: purple'

        outerHTML = tag.outerHTML

        assert 'position: absolute' in outerHTML , 'Missing style attribute in outerHTML'
        assert 'purple' in outerHTML , 'Missing style attribute in outerHTML'

    def test_classNames(self):
        tag = AdvancedTag('div')
        tag.addClass('abc')

        assert tag.hasClass('abc'), 'Failed to add class'
        assert 'abc' in tag.outerHTML , 'Failed to add class in outerHTML'

        assert 'abc' in tag.classNames

        tag.addClass('def')

        assert tag.hasClass('abc'), 'Failed to retain class'
        assert 'abc' in tag.outerHTML , ' Failed to retain in outerHTML'

        assert tag.hasClass('def'), 'Failed to add second class'
        assert 'def' in tag.outerHTML , ' Failed to add to outerHTML'

        tag.removeClass('abc')
        assert not tag.hasClass('abc'), 'Failed to remove class'
        assert 'abc' not in tag.outerHTML , 'Failed to remove class from outerHTML'

        assert tag.hasClass('def'), 'Failed to retain class'
        assert 'def' in tag.outerHTML , ' Failed to retain in outerHTML'


    def test_noValueAttributes(self):
        parser = AdvancedHTMLParser()
        parser.parseStr('<input id="thebox" type="checkbox" checked />')

        tag = parser.getElementById('thebox')
        assert tag.hasAttribute('checked')
        assert 'checked' in tag.outerHTML

    def test_valueMethod(self):
        parser = AdvancedHTMLParser()
        parser.parseStr('<input id="item" type="text" value="hello" />')

        tag = parser.getElementById('item')
        assert tag.value == 'hello'

    def test_attributeDefault(self):
        parser = AdvancedHTMLParser()
        parser.parseStr('<input id="item" type="text" value="hello" />')

        tag = parser.getElementById('item')
        assert tag.getAttribute('type', 'bloogity') == 'text'
        assert tag.getAttribute('woogity', 'snoogity') == 'snoogity'


    def test_setAttributesOnItem(self):
        tag = AdvancedTag('div')

        tag.id = 'hello'


        assert tag.id == 'hello' , 'Expected to be able to set special attribute "id" and have it show up as both attribute and on item'
        assert tag.getAttribute('id', '') == 'hello' , 'Expected to be able to set special attribute "id" and have it show up as both attribute and on item'

        tag.name = 'cheese'

        assert tag.name == 'cheese' , 'Expected to be able to set special attribute "name" and have it show up as both attribute and on item'
        assert tag.getAttribute('name', '') == 'cheese' , 'Expected to be able to set special attribute "name" and have it show up as both attribute and on item'

        assert tag.tabIndex == -1 , 'Expected default tab index (unset) to be -1'

        tag.tabIndex = 5

        assert 'tabindex="5"' in tag.outerHTML , 'Expected setting the tabIndex to set tabindex attribute on html'

    def test_domAttributes(self):

        parser = AdvancedHTMLParser()

        parser.parseStr(''''<html>
        <body>
            <div id="someDiv" class="one two" align="left">
                <span>Some Child</span>
            </div>

        </body>
    </html>
        ''')

        someDivEm = parser.getElementById('someDiv')

        assert someDivEm , 'Failed to get element by id="someDiv"'

        attributes = someDivEm.attributesDOM

        assert attributes['id'].value == 'someDiv' , 'Expected attributes["id"].value to be equal to "someDiv"'

        assert attributes['class'].value == 'one two', "Expected attributes['class'].value to be equal to 'one two'"
        assert attributes['align'].value == 'left' , "Expected attributes['align'].value to be equal to 'left'"

        assert attributes['notset'] is None, 'Expected attributes["notset"] to be None'

        assert attributes['id'].ownerElement == someDivEm , 'Expected ownerElement to be "someDivEm"'

        assert attributes['id'].ownerDocument == parser , 'Expected ownerDocument to be parser'

        assert str(attributes['id']) == 'id="someDiv"' , 'Expected str of attribute to be \'id="someDiv"\' but got: %s' %(str(attributes['id']), )

        attributes['align'].value = 'right'

        assert attributes['align'].value == 'right' , 'Expected to be able to change attribute value by assigning .value. Failed on "align".'

        assert someDivEm.getAttribute('align') == 'right' , 'Expected that changing a property in the attributes map would change the value in parent element'

        attrNames = []
        for attrName in attributes:
            attrNames.append(attrName)

        assert 'id' in attrNames , 'Expected "id" to be returned from iter on attributes'
        assert 'class' in attrNames , 'Expected "class" to be returned from iter on attributes'
        assert 'align' in attrNames , 'Expected "align" to be returned from iter on attributes'

        clonedAttributes = {attrName : attributes[attrName].cloneNode() for attrName in attrNames}

        for attrName in ('id', 'class', 'align'):
            attrValue = clonedAttributes[attrName].value
            origValue = attributes[attrName].value

            assert attrValue == origValue , 'Expected cloned attribute %s to match original, but did not. (clone) %s != %s (orig)' %(attrName, attrValue, origValue)

        assert clonedAttributes['id'].ownerElement is None, 'Expected clone to clear ownerElement'
        assert clonedAttributes['id'].ownerDocument == parser , 'Expected clone to retain same ownerDocument'

        clonedAttributes['align'].value = 'middle'

        assert clonedAttributes['align'].value == 'middle' , 'Expected to be able to change value on cloned attribute'
        assert attributes['align'].value == 'right' , 'Expected change on clone to not affect original'

        assert someDivEm.getAttribute('align') == 'right' , 'Expected change on clone to not affect element'

        assert attributes.getNamedItem('id') == attributes['id'], 'Expected getNamedItem("id") to be the same as attributes["id"]'

    def test_unknownStillAttribute(self):
        '''
            test_unknownStillAttribute - Test that setting an unknwon attribute still sets it in HTML
        '''
        tag = AdvancedTag('div')

        tag.setAttribute('squiggle', 'wiggle')

        htmlStr = str(tag)

        assert 'squiggle="wiggle"' in htmlStr

        squiggleAttrValue = tag.getAttribute('squiggle')

        assert squiggleAttrValue == 'wiggle', "Expected 'squiggle' attribute from tag.getAttribute to return 'wiggle'. Got: " + repr(squiggleAttrValue)


    def test_removeAttribute(self):
        '''
            test_removeAttribute - Test removing attributes
        '''

        tag = AdvancedTag('div')

        tag.setAttribute('align', 'left')
        tag.setAttribute('title', 'Hover text')

        htmlStr = str(tag)

        assert 'align="left"' in htmlStr , 'Expected setAttribute("align", "left") to result in align="left" in HTML representation. Got: ' + htmlStr

        alignAttrValue = tag.getAttribute('align')

        assert alignAttrValue == 'left' , 'Expected getAttribute("align") to return "left" after having set align to "left". Got: ' + repr(alignAttrValue)

        tag.removeAttribute('align')

        htmlStr = str(tag)

        assert 'align="left"' not in htmlStr , 'Expected removeAttribute("align") to remove align="left" from HTML representation. Got: ' + htmlStr

        alignAttrValue = tag.getAttribute('align')

        assert alignAttrValue != 'left' , 'Expected removeAttribute("align") to remove align: left from attributes map. Got: ' + repr(alignAttrValue)


        tag.removeAttribute('title')

        htmlStr = str(tag)

        assert 'align="left"' not in htmlStr , 'Expected after all attributes removed via removeAttribute that align="left" would not be present. Got: ' + htmlStr
        assert 'title=' not in htmlStr , 'Expected after all attributes removed via removeAttribute that align="left" would not be present. Got: ' + htmlStr

        attributes = tag.attributes

        assert 'align' not in attributes , 'Expected to NOT find "align" within the attributes. Got: ' + repr(attributes)
        assert 'title' not in attributes , 'Expected to NOT find "align" within the attributes. Got: ' + repr(attributes)


    def test_delAttributes(self):
        '''
            test_delAttributes - Test deleting attributes
        '''
        tag = AdvancedTag('div')

        tag.setAttribute('id', 'abc')

        tag.style = 'display: block; float: left'

        tagHTML = tag.toHTML()

        assert 'id="abc"' in tagHTML , 'Expected id="abc" to be present in tag html. Got: ' + tagHTML
        assert 'style=' in tagHTML , 'Expected style attribute to be present in tag html. Got: ' + tagHTML

        assert tag.style.display == 'block' , 'Expected style.display to be "block". Style is: ' + str(tag.style)
        assert tag.style.float == 'left' , 'Expected style.float to be "left". Style is: ' + str(tag.style)

        del tag.attributes['id']

        tagHTML = tag.toHTML()

        assert not tag.id , "Expected id to be empty after deleting attribute. It is: " + repr(tag.id)
        assert 'id="abc"' not in tagHTML , 'Expected id attribute to NOT be present in tagHTML after delete. Got: ' + tagHTML

        del tag.attributes['style']

        tagHTML = tag.toHTML()

        assert 'style=' not in tagHTML , 'Expected style attribute to NOT be present in tagHTML after delete. Got: ' + tagHTML
        assert str(tag.style) == '' , 'Expected str(tag.style) to be empty string after delete of style attribute. It was: ' + repr(str(tag.style))
        assert tag.style.display == '' , 'Expected display style property to be cleared after delete of style attribute. Style is: ' + str(tag.style)
        assert tag.style.float == '' , 'Expected float style property to be cleared after delete of style attribute. Style is: ' + str(tag.style)


        tag.style = 'font-weight: bold; float: right'

        tagHTML = tag.toHTML()

        assert 'style=' in tagHTML , 'Expected after deleting style, then setting it again style shows up as HTML attr. Got: ' + tagHTML

        assert 'font-weight: bold' in tagHTML , 'Expected after deleting style, then setting it again the properties show up in the HTML "style" attribute. Got: ' + tagHTML

        assert id(tag.getAttribute('style', '')) == id(tag.style) , 'Expected after deleting style, then setting it again the attribute remains linked.'

        assert tag.style.fontWeight == 'bold' , 'Expected after deleting style, then setting it again everything works as expected. Set style to "font-weight: bold; float: left" but on tag.style it is: ' + str(tag.style)

        tag.addClass('bold-item')
        tag.addClass('blue-font')

        assert 'bold-item' in tag.classList , 'Did addClass("bold-item") but did not find it in classList. classList is: ' + repr(tag.classList)
        assert 'blue-font' in tag.classList , 'Did addClass("blue-font") but did not find it in classList. classList is: ' + repr(tag.classList)

        classes = tag.getAttribute('class')

        assert 'bold-item' in classes and 'blue-font' in classes , 'Expected class attribute to contain both classes. Got: ' + str(classes)

        # This should call del tag._attributes['class']
        tag.removeAttribute('class')

        assert 'bold-item' not in tag.classList , 'After removing class, expected to not find classes in tag.classList. classList is: ' + repr(tag.classList)

        assert len(tag.classList) == 0 , 'Expected to have no classes in classList after delete. Got %d' %(len(tag.classList), )

        assert tag.getAttribute('class') == '' , 'Expected after removing class it would be an empty string'

        assert tag.getAttribute('clazz') is None , 'Expected default getAttribute on non-set attribute to be None'

    def test_specialAttributes(self):
        tag = AdvancedTag('div')

        assert tag.spellcheck is False , 'Expected default value of "spellcheck" field via dot-access to be False'
        assert 'spellcheck' not in str(tag) , 'Expected "spellcheck" to not show up in HTML representation before set. Got: ' + str(tag)

        tag.spellcheck = True

        assert tag.spellcheck is True , 'Expected after setting spellcheck to True, dot-access returns True.'

        tagHTML = str(tag)

        assert 'spellcheck="true"' in tagHTML , "Expected spellcheck to have value of string 'true' in HTML representation. Got: " + tagHTML

        tag.spellcheck = False
        tagHTML = str(tag)

        assert tag.spellcheck is False , 'Expected spellcheck to have dot-access value of False after being set to False. Got: ' + repr(tag.spellcheck)
        assert 'spellcheck="false"' in tagHTML , "Expected spellcheck to have value of string 'false' in HTML representation after being set to False. Got: " + tagHTML
        assert tag.getAttribute('spellcheck') == 'false' , 'Expected getAttribute("spellcheck") to return string "false" in HTML representation. Got: ' + repr(tag.getAttribute('spellcheck'))


        tag.spellcheck = "yes"

        assert tag.spellcheck is True , 'Expected after setting spellcheck to "yes", dot-access reutrns True. Got: ' + repr(tag.spellcheck)
        tagHTML = str(tag)

        assert 'spellcheck="true"' in tagHTML , "Expected spellcheck to have value of string 'true' in HTML representation after being set to 'yes'. Got: " + tagHTML

        assert tag.getAttribute('spellcheck') == "true" , "Expected getAttribute('spellcheck') to return string of True"


    def test_nameChangeFields(self):
        '''
            Test that fields with a different dot-access variable are handled properly
        '''

        td = AdvancedTag('td')

        assert td.colspan is None , 'Expected "colspan" to be "colSpan"'

        assert td.colSpan is not None , 'Expected "colSpan" to map to "colspan"'


        td.colSpan = 5

        assert not td.colspan , 'dot access should be colSpan, but colspan worked.'

        assert str(td.colSpan) == "5" , "dot access on .colSpan should have worked"

        assert str(td.getAttribute('colspan')) == "5" , "Expected getAttribute to use the all lowercase name"

        tdHTML = str(td)

        assert "colSpan" not in tdHTML , "Expected html attribute to be the lowercased name. Got: " + tdHTML

        assert 'colspan="5"' in tdHTML , 'Expected colspan="5" to be present. Got: ' + tdHTML

        td.setAttribute('colspan', '8')

        tdHTML = str(td)

        assert str(td.colSpan) == '8' , 'Expected setAttribute("colspan",...) to update .colSpan attribute. Was 5, set to 8, and got: ' + repr(td.colSpan)

        assert 'colspan="8"' in tdHTML , 'Expected setAttribute("colspan") to update HTML. Got: ' + tdHTML

        assert td.colSpan == 8 , 'Expected colSpan to be an integer value. Got: ' + str(type(td.colSpan))


        td = AdvancedTag('td', attrList=[ ('colspan', '5') ])

        assert td.colSpan == 5 , 'Expected setting "colspan" in attrList sets colSpan'

        # Now try a binary field

        form = AdvancedTag('form')

        assert form.novalidate is None , 'Expected novalidate on form to have dot-access name of noValidate'
        assert form.noValidate is not None , 'Expected novalidate on form to have dot-access name of noValidate'

        assert form.noValidate is False , 'Expected default for form.noValidate to be False'

        form.noValidate = "yes"

        assert form.noValidate is True , 'Expected noValidate to be converted to a bool. Got: ' + repr(form.noValidate)

        formHTML = str(form)

        assert 'novalidate' in formHTML , 'Expected form.noValidate to set "novalidate" property in HTML. Got: ' + formHTML

        form.noValidate = True
        formHTML = str(form)

        assert 'novalidate' in formHTML , 'Expected form.noValidate to set "novalidate" property in HTML. Got: ' + formHTML

        form.noValidate = False
        formHTML = str(form)

        assert 'novalidate' not in formHTML , 'Expected setting form.noValidate to False to remove it from HTML. Got: ' + formHTML

    def test_crossOrigin(self):
        '''
            test crossOrigin attribute
        '''

        img = AdvancedTag('img')

        assert img.crossOrigin is None , 'Default for crossOrigin (never set) should be None (null). Got: ' + repr(img.crossOrigin)

        img.crossOrigin = 'blah'

        assert img.crossOrigin == 'anonymous', 'Default dot-access value for invalid crossOrigin should be "anonymous". Got: ' + repr(img.crossOrigin)

        imgHTML = str(img)

        assert 'crossorigin' in imgHTML , 'Expected "crossOrigin" to be converted to "crossorigin" in HTML. Got: ' + imgHTML

        assert 'crossorigin="blah"' in imgHTML , 'Expected whatever was set via img.crossOrigin = "blah" to show up in html text, even though the dot-access variable is different. Got: ' + imgHTML

        img.crossOrigin = 'use-credentials'
        imgHTML = str(img)

        assert img.crossOrigin == 'use-credentials' , 'Expected "use-credentials" value to be retained for crossOrigin. Got: ' + repr(img.crossOrigin)

        assert 'crossorigin="use-credentials"' in imgHTML , 'Expected crossorigin="use-credentials" to be retained in HTML. Got: ' + imgHTML

        img.crossOrigin = 'anonymous'
        imgHTML = str(img)

        assert img.crossOrigin == 'anonymous' , 'Expected "anonymous" value to be retained for crossOrigin. Got: ' + repr(img.crossOrigin)

        assert 'crossorigin="anonymous"' in imgHTML , 'Expected crossorigin="anonymous" to be retained in HTML. Got: ' + imgHTML

    def test_inputAutocomplete(self):
        '''
            test input autocomplete attribute
        '''

        inputEm = AdvancedTag('input')

        assert inputEm.autocomplete == '' , 'Expected default for unset "autocomplete" to be "". Got: ' + repr(inputEm.autocomplete)

        inputEm.autocomplete = 'on'
        inputHTML = str(inputEm)

        assert inputEm.autocomplete == 'on' , 'Expected autocomplete="on" to retain on. Got: ' + repr(inputEm.autocomplete)

        assert inputEm.getAttribute('autocomplete') == 'on' , 'Expected getAttribute to return the value on a binary attribute when provided'

        assert 'autocomplete="on"' in inputHTML , 'Expected html property to be set. Got: ' + repr(inputHTML)

        inputEm.autocomplete = 'blah'

        assert inputEm.autocomplete == '' , 'Expected autocomplete="blah" to use invalid fallback of "". Got: ' + repr(inputEm.autocomplete)

        inputEm.autocomplete = 'off'
        inputHTML = str(inputEm)

        assert inputEm.autocomplete == 'off' , 'Expected to be able to switch autocomplete to off. Got: ' + repr(inputEm.autocomplete)

        assert 'autocomplete="off"' in inputHTML , 'Expected html property to be set. Got: ' + repr(inputHTML)

        inputEm.autocomplete = ''
        inputHTML = str(inputEm)

        assert inputEm.autocomplete == '' , 'Expected to be able to set autocomplete to empty string. Got: ' + repr(inputEm.autocomplete)

        assert 'autocomplete=""' in inputHTML , 'Expected html property to be set to empty string. Got: ' + repr(inputHTML)


    def test_formAutocomplete(self):
        '''
            test form autocomplete attribute
        '''

        formEm = AdvancedTag('form')

        assert formEm.autocomplete == 'on' , 'Expected default for unset "autocomplete" to be "on". Got: ' + repr(formEm.autocomplete)

        formEm.autocomplete = 'on'
        formHTML = str(formEm)

        assert formEm.autocomplete == 'on' , 'Expected autocomplete="on" to retain on. Got: ' + repr(formEm.autocomplete)

        assert 'autocomplete="on"' in formHTML , 'Expected html property to be set. Got: ' + repr(formHTML)

        formEm.autocomplete = 'blah'

        assert formEm.autocomplete == 'on' , 'Expected autocomplete="blah" to use invalid fallback of "on". Got: ' + repr(formEm.autocomplete)

        formEm.autocomplete = 'off'
        formHTML = str(formEm)

        assert formEm.autocomplete == 'off' , 'Expected to be able to switch autocomplete to off. Got: ' + repr(formEm.autocomplete)

        assert 'autocomplete="off"' in formHTML , 'Expected html property to be set. Got: ' + repr(formHTML)

        formEm.autocomplete = ''
        formHTML = str(formEm)

        assert formEm.autocomplete == 'on' , 'Expected setting autocomplete to empty string to revert to invalid, "on". Got: ' + repr(formEm.autocomplete)

        assert 'autocomplete=""' in formHTML , 'Expected html property to be set to empty string. Got: ' + repr(formHTML)


    def test_formMethod(self):
        '''
            test the form's "method" attribute
        '''

        formEm = AdvancedTag('form')

        assert formEm.method == 'get' , 'Expected default for form.method to be "get". Got: ' + repr(formEm.method)

        formEm.method = 'get'

        assert formEm.method == 'get' , 'Expected to be able to set form.method to "get". Got: ' + repr(formEm.method)

        formHTML = str(formEm)

        assert 'method="get"' in formHTML , 'Expected html attribute method to be set in html representation. Got: ' + repr(formHTML)

        formEm.method = 'post'
        formHTML = str(formEm)

        assert formEm.method == 'post' , 'Expected to be able to set form.method to "post". Got: ' + repr(formEm.method)


        assert 'method="post"' in formHTML , 'Expected html attribute method to be set in html representation. Got: ' + repr(formHTML)

        formEm.method = 'POST'
        formHTML = str(formEm)

        assert formEm.method == 'post' , 'Expected to be able to set form.method to "POST" and it be converted to lowercase for dot-access. Got: ' + repr(formEm.method)


        assert 'method="POST"' in formHTML , 'Expected html attribute method to be set in html representation as given (i.e. not lowercased). Got: ' + repr(formHTML)

        # NOTE: This is strange, but it is the behaviour as the w3 spec only allows "post" or "get" to be values,
        #         even though other methods exist.
        formEm.method = 'put'
        formHTML = str(formEm)

        assert formEm.method == 'get' , 'Expected dot-access to only support "get" and "post", and default to "get" for invalid values. Got: ' + repr(formEm.method)

        assert 'method="put"' in formHTML , 'Expected html representation to have the value as provided, even though dot-access returns a different value. Got: ' + repr(formHTML)


    def test_formAttribute(self):
        '''
            test the "form" attribute, that links to parent form
        '''

        document = AdvancedHTMLParser()
        document.parseStr('''<html><head></head><body><div id="main"> <form id="myForm"> <div> <input type="text" id="inputWithinForm" /> </div> </form> </div> <input type="text" id="inputOutsideForm" /> </body></html>''')


        myFormEm = document.getElementById('myForm')

        assert myFormEm , 'Failed to get element by id="myForm"'

        inputWithinFormEm = document.getElementById('inputWithinForm')

        assert inputWithinFormEm , 'Failed to get element with id="inputWithinForm"'

        foundFormEm = inputWithinFormEm.form

        assert foundFormEm , 'Expected inputWithinFormEm.form to return parent form. Got nada.'

        assert foundFormEm is myFormEm , 'Expected to get parent form via .form, got: ' + str(foundFormEm.getStartTag())

        inputOutsideFormEm = document.getElementById('inputOutsideForm')

        assert inputOutsideFormEm , 'Failed to get element with id="inputOutsideForm"'

        foundFormEm = inputOutsideFormEm.form

        assert foundFormEm is None , 'Expected .form to return None on an input outside of form. Got: ' + str(foundFormEm.getStartTag())

    def test_rowAndColSpan(self):
        '''
            test_rowAndColSpan - test rowSpan and colSpan
        '''

        tdEm = AdvancedTag('td')

        assert tdEm.colspan is None , 'Expected colspan dot-access to be None'
        assert tdEm.colSpan is not None , 'Expected colSpan dot-access to not be None'

        assert tdEm.colSpan == 1 , 'Expected default colSpan to be 1 but got: ' + repr(tdEm.colSpan)

        tdEm.colSpan = 10
        tdEmHTML = str(tdEm)

        assert tdEm.colSpan == 10 , 'Expected to be able to set colSpan to 10, but value returned was: ' + repr(tdEm.colSpan)
        assert 'colspan="10"' in tdEmHTML , 'Expected colspan="10" to be in HTML string after setting, but got: ' + tdEmHTML

        tdEm.colSpan = -5
        assert tdEm.colSpan == 1 , 'Expected colSpan to be clamped to a minimum of 1, but got: ' + repr(tdEm.colSpan)

        tdEm.colSpan = 1000000
        assert tdEm.colSpan == 1000 , 'Expected colSpan to be clamped to a maximum of 1000, but got: ' + repr(tdEm.colSpan)

        tdEm = AdvancedTag('td')

        assert tdEm.rowspan is None , 'Expected rowspan dot-access to be None'
        assert tdEm.rowSpan is not None , 'Expected rowSpan dot-access to not be None'

        assert tdEm.rowSpan == 1 , 'Expected default rowSpan to be 1 but got: ' + repr(tdEm.rowSpan)


        tdEm.rowSpan = 10
        tdEmHTML = str(tdEm)

        assert tdEm.rowSpan == 10 , 'Expected to be able to set rowSpan to 10, but value returned was: ' + repr(tdEm.rowSpan)
        assert 'rowspan="10"' in tdEmHTML , 'Expected rowspan="10" to be in HTML string after setting, but got: ' + tdEmHTML

        tdEm.rowSpan = -5
        assert tdEm.rowSpan == 0 , 'Expected rowSpan to be clamped to a minimum of 0, but got: ' + repr(tdEm.rowSpan)

        tdEm.rowSpan = 1000000
        assert tdEm.rowSpan == 65534 , 'Expected rowSpan to be clamped to a maximum of 65534, but got: ' + repr(tdEm.rowSpan)

    def test_spanAttributeOnCol(self):
        '''
            test_spanAttributeOnCol - Tests the "span" attribute on a "col"
        '''

        colEm = AdvancedTag('col')

        assert colEm.span == 1 , 'Expected default for col.span to be 1. Got: ' + repr(colEm.span)

        colEm.span = 5

        assert colEm.span == 5 , 'Expected to be able to set col.span to 5, but returned: ' + repr(colEm.span)

        colEmHTML = str(colEm)

        assert 'span="5"' in colEmHTML , 'Expected span="5" to show up after setting col.span to 5. Got: ' + repr(colEmHTML)

        colEm.span = -5

        assert colEm.span == 1 , 'Expected col.span to be clamped to a minimum of 1. Got: ' + repr(colEm.span)

        colEm.span = 1
        assert colEm.span == 1 , 'Expected col.span to be clamped to a minimum of 1. Got: ' + repr(colEm.span)

        colEm.span = 1500

        assert colEm.span == 1000 , 'Expected col.span to be clamped to a maximum of 1000. Got: ' + repr(colEm.span)


    def test_colsAttribute(self):
        '''
            test_colsAttribute - Tests the "cols" attribute

                NOTE: This differs in behaviour between a textarea and a frameset
        '''

        textareaEm = AdvancedTag('textarea')

        assert textareaEm.cols == 20 , 'Expected default "cols" for textarea to be 20, but got: ' + repr(textareaEm.cols)

        textareaEm.cols = 100

        assert textareaEm.cols == 100 , 'Expected to be able to set "cols" to 100 and that value stick, but got: ' + repr(textareaEm.cols)

        textareaEmHTML = str(textareaEm)

        assert 'cols="100"' in textareaEmHTML , 'Expected to find "cols" attribute set to "100" in HTML, but got: ' + repr(textareaEmHTML)

        textareaEm.cols = 0

        assert textareaEm.cols == 20 , 'Expected an invalid value in "cols" attribute on textarea to return 20, but got: ' + repr(textareaEm.cols)


        framesetEm = AdvancedTag('frameset')

        assert framesetEm.cols == '' , 'Expected "cols" attribute on frameset to default to empty string, but got: ' + repr(framesetEm.cols)

        framesetEm.cols = "5"

        assert framesetEm.cols == "5" , 'Expected to be able to set "cols" attribute to "5" and it apply, but got: ' + repr(framesetEm.cols)

        framesetEmHTML = str(framesetEm)

        assert 'cols="5"' in framesetEmHTML , 'Expected "cols" attribute to be set to "5" in HTML representation, but got: ' + repr(framesetEmHTML)

        framesetEm.cols = "bologna"

        assert framesetEm.cols == "bologna" , 'Expected to be able to set "cols" to any string, set to "bologna" but got back: ' + repr(framesetEm.cols)


    def test_rowsAttribute(self):
        '''
            test_rowsAttribute - Tests the "rows" attribute

                NOTE: This differs in behaviour between a textarea and a frameset
        '''

        textareaEm = AdvancedTag('textarea')

        assert textareaEm.rows == 2 , 'Expected default "rows" for textarea to be 2, but got: ' + repr(textareaEm.rows)

        textareaEm.rows = 100

        assert textareaEm.rows == 100 , 'Expected to be able to set "rows" to 100 and that value stick, but got: ' + repr(textareaEm.rows)

        textareaEmHTML = str(textareaEm)

        assert 'rows="100"' in textareaEmHTML , 'Expected to find "rows" attribute set to "100" in HTML, but got: ' + repr(textareaEmHTML)

        textareaEm.rows = 0

        assert textareaEm.rows == 2 , 'Expected an invalid value in "rows" attribute on textarea to return "2", but got: ' + repr(textareaEm.rows)


        framesetEm = AdvancedTag('frameset')

        assert framesetEm.rows == '' , 'Expected "rows" attribute on frameset to default to empty string, but got: ' + repr(framesetEm.rows)

        framesetEm.rows = "5"

        assert framesetEm.rows == "5" , 'Expected to be able to set "rows" attribute to "5" and it apply, but got: ' + repr(framesetEm.rows)

        framesetEmHTML = str(framesetEm)

        assert 'rows="5"' in framesetEmHTML , 'Expected "rows" attribute to be set to "5" in HTML representation, but got: ' + repr(framesetEmHTML)

        framesetEm.rows = "bologna"

        assert framesetEm.rows == "bologna" , 'Expected to be able to set "rows" to any string, set to "bologna" but got back: ' + repr(framesetEm.rows)


    def test_iframeSandbox(self):
        '''
            Test iframe's "sandbox" attribute
        '''
        from AdvancedHTMLParser.SpecialAttributes import DOMTokenList

        iframeEm = AdvancedTag('iframe')

        assert isinstance(iframeEm.sandbox, DOMTokenList) , 'Expected iframe.sandbox to be a "DOMTokenList", but got: ' + str(iframeEm.sandbox.__class__.__name__)

        iframeEm.sandbox = ''

        sandbox = iframeEm.sandbox

        assert isinstance(sandbox, DOMTokenList) , 'Expected after setting iframe.sandbox = "" to retain a DOMTokenList on access, but got: ' +  str(iframeEm.sandbox.__class__.__name__)

        assert len(sandbox) == 0 , 'Expected to have no elements after setting to empty string, but got: ' + repr(sandbox)

        iframeEm.sandbox = 'one two three'

        sandbox = iframeEm.sandbox
        assert isinstance(sandbox, DOMTokenList) , 'Expected after setting iframe.sandbox = "one two three" to retain a DOMTokenList on access, but got: ' +  str(iframeEm.sandbox.__class__.__name__)

        assert len(sandbox) == 3 , 'Expected to have 3 elements in sandbox. Got: ' + repr(sandbox)

        assert sandbox[0] == 'one', 'Expected first element to be "one". Got: ' + repr(sandbox[0])
        assert sandbox[1] == 'two', 'Expected second element to be "two". Got: ' + repr(sandbox[1])
        assert sandbox[2] == 'three', 'Expected third element to be "third". Got: ' + repr(sandbox[2])

        assert str(sandbox) == 'one two three', 'Expected str of sandbox attr to be "one two three". Got: ' + repr(str(sandbox))

        iframeEmHTML = str(iframeEm)

        assert 'sandbox="one two three"' in iframeEmHTML , 'Expected sandbox="one two three" to be in HTML, but got: ' + iframeEmHTML

        sandbox.append('Hello')

        assert len(iframeEm.sandbox) == 3 , 'Expected appending to the DOMTokenList returned to have no effect.'


    def test_trackKind(self):
        '''
            test the "kind" attribute on a track
        '''

        # A copy of the possible values. Use a copy so that we are testing not using the code we are testing for validation of the validation of the code we are testing to validate the code that the validation of the INFINTIEEEE LOOOOP AHHHHHHHHHHHHHH
        TRACK_POSSIBLE_KINDS = ( 'captions', 'chapters', 'descriptions', 'metadata', 'subtitles' )

        trackEm = AdvancedTag('track')

        assert trackEm.kind == 'subtitles' , 'Expected default value of trackEm.kind to be "subtitles"'

        trackEm.kind = 'blah'

        trackEmHTML = str(trackEm)

        assert trackEm.kind == 'metadata' , 'Expected when an "invalid" value is provided for track->kind, that "metadata" is returned, but got: ' + repr(trackEm.kind)

        assert 'kind="blah"' in trackEmHTML , 'Expected when an "invalid" value is provided for track->kind, that the value is put into the HTML attribute as-is, but got: ' + str(trackEmHTML)

        for possibleKind in TRACK_POSSIBLE_KINDS:

            trackEm.kind = possibleKind

            assert trackEm.kind == possibleKind , 'Expected to be able to set track->kind to "%s", but after doing so got %s as the return.' %( possibleKind, repr(trackEm.kind))

        trackEm.kind = ''

        assert trackEm.kind == 'metadata' , 'Expected setting kind to an empty string returns "metadata" (the invalid result), but got: ' + repr(trackEm.kind)


    def test_hiddenAttr(self):
        '''
            Test that the "hidden" attribute works correctly.
        '''
        myHTML = '''<html> <input hidden value="hello" id="abc" />'''

        parser = AdvancedHTMLParser()

        parser.parseStr(myHTML)

        idEm = parser.getElementById('abc')

        assert idEm.hidden == True

        assert 'hidden' in str(idEm)

        # Make sure we treat this as a real binary attribute
        x = str(idEm)
        assert 'hidden=' not in str(idEm)

        assert idEm.getAttribute('hidden') is True


    def test_maxLength(self):
        '''
            test_maxLength - Test the "maxLength" attribute
        '''

        inputEm = AdvancedTag('input')

        assert inputEm.maxlength is None , 'Expected .maxlength to not be valid (should be .maxLength)'

        assert inputEm.maxLength == -1 , 'Expected default .maxLength to be -1'

        inputEm.maxLength = 5

        assert inputEm.maxLength == 5 , 'Expected to be able to set maxLength to 5 and get 5 back, but got: ' + repr(inputEm.maxLength)

        inputEmHTML = str(inputEm)

        assert 'maxlength="5"' in inputEmHTML , 'Expected .maxLength to set the "maxlength" attribute. Got: ' + inputEmHTML

        maxLengthAttr = inputEm.getAttribute('maxlength', None)
        assert maxLengthAttr == "5" , 'Expected .getAttribute("maxlength") to return "5", but got: ' + repr(maxLengthAttr)

        inputEm.maxLength = 0

        assert inputEm.maxLength == 0 , 'Expected to be able to set maxLength to 0'

        gotException = False
        try:
            inputEm.maxLength = -4
        except Exception as e:
            gotException = e

        assert gotException is not False , 'Expected to get an exception when setting maxLength < 0. Did not.'

        try:
            inputEm.setAttribute('maxlength', '-5')
        except Exception as e:
            raise AssertionError('Expected to be able to use .setAttribute to set "maxlength" to an invalid value, but got exception: %s: %s' %( e.__class__.__name__, str(e)) )

        inputEmHTML = str(inputEm)

        assert 'maxlength="-5"' in inputEmHTML , 'Expected .setAttribute to really set an invalid value on the HTML. Should be maxlength="-5", but got: ' + inputEmHTML

        maxLengthValue = None
        try:
            maxLengthValue = inputEm.maxLength
        except Exception as e:
            raise AssertionError('Expected to be able to query .maxLength after .setAttribute to an invalid value, but got an exception: %s: %s' %( e.__class__.__name__, str(e)) )

        assert maxLengthValue == -1 , 'Expected invalid attribute value to return "-1" on .maxLength access, but got: ' + repr(maxLengthValue)


    def test_getElementsByClassName(self):
        '''
            test_getElementsByClassName - Test the getElementsByClassName method
        '''

        html = '''<html><head><title>Page</title></head>
<body class="background">
  <div id="outer" class="outer">
   <div class="inner special">Hello</div>
   <div class="inner cheese">
     <div class="blah" id="blahdiv1">One</div>
       <span>
         <div class="blah" id="blahdiv2" >
         </div>
       </span>
     </div>
   </div>
  </div>
  <div id="outer2" >
    <div class="yes-dash cheese" >Hello</div>
  </div>
  <div id="outer3" >
    <div class="class-dash CDONE" >One</div>
    <div class="CDBEFORE class-dash CDAFTER class-dash2" >Two</div>
    <div class="class-dash">Three
      <div class="class-dash pickle">Nested Four</div>
    </div>
</body>
</html>
        '''
        document = AdvancedHTMLParser()
        document.parseStr(html)

        tags = document.getElementsByClassName('background')
        assert len(tags) == 1 and tags[0].tagName == 'body' , 'Expected to get body tag for getElementsByClassName("background")'

        tags = document.getElementsByClassName("inner")
        assert len(tags) == 2 and tags[0].tagName == 'div' and tags[1].tagName == 'div' , 'Expected to find 2 div tags with class="inner"'

        assert "inner" in tags[0].classNames and "inner" in tags[1].classNames , 'Expected to find "inner" in the classNames list'

        assert issubclass(tags[0].classNames.__class__, (list, tuple)) , 'Expected .classNames to be a list of class names'


        assert tags[0].className.startswith("inner") and tags[1].className.startswith("inner") , 'Expected to find "inner" at start of className string'

        specialDiv = None
        cheeseDiv = None
        for tag in tags:
            if "cheese" in tag.classNames:
                cheeseDiv = tag
            elif "special" in tag.classNames:
                specialDiv = tag

        assert specialDiv , 'Failed to find div with "special" in className'
        assert cheeseDiv , 'Failed to find div with "cheese" in className'

        assert 'Hello' in specialDiv.innerHTML , 'Expected "Hello" to be inside special div'

        assert specialDiv.getElementsByClassName('bogus') == [] , 'Expected to get no results for specialDiv.getElementsByClassName("bogus")'

        blahDivsDocument = document.getElementsByClassName("blah")
        blahDivsCheese = cheeseDiv.getElementsByClassName("blah")

        assert len(blahDivsDocument) == 2 , 'Expected to get 2 class="blah" divs from document, but got ' + str(len(blahDivsDocument))

        assert len(blahDivsCheese) == 2 , 'Expected to get 2 class="blah" divs from cheeseDiv, but got ' + str(len(blahDivsCheese))

        blahDiv1 = None
        blahDiv2 = None

        for blahDiv in blahDivsDocument:
            if blahDiv.id == 'blahdiv1':
                blahDiv1 = blahDiv
            elif blahDiv.id == 'blahdiv2':
                blahDiv2 = blahDiv

        assert blahDiv1 , 'Failed to find id="blahdiv1" on one of the class="blah" divs'
        assert blahDiv2 , 'Failed to find id="blahdiv2" on one of the class="blah" divs'

        assert blahDiv1 in blahDivsCheese , 'Expected id="blahdiv1" div to also be in results from root=cheese div'
        assert blahDiv2 in blahDivsCheese , 'Expected id="blahdiv2" div to also be in results from root=cheese div'


        # Test dash in class name - ( Reported as Issue #6, but cannot reproduce. )
        dashDivs = document.getElementsByClassName('yes-dash')
        assert dashDivs , 'Failed to find any results for getElementsByClassName with dash.'
        assert len(dashDivs) == 1 , 'Expected to find one result for class="yes-dash", but got %d. %s' %(len(dashDivs), repr(dashDivs))

        dashDiv = dashDivs[0]
        assert dashDiv.innerText.strip() == 'Hello' , 'Expected innerText="Hello", but got: %s' %(repr(dashDiv.innerText.strip()), )
        assert dashDiv.tagName == 'div' , 'Expected to find a div, but got %s' %(dashDiv.tagName, )


        classDashEms = document.getElementsByClassName('class-dash')
        assert classDashEms , 'Failed to find elements with class name = "class-dash"'
        assert len(classDashEms) == 4 , 'Expected to find 4 elements with class name = "class-dash" but got %d. %s' %( len(classDashEms), repr(classDashEms))

        classDash2Ems = document.getElementsByClassName('class-dash2')
        assert classDash2Ems , 'Failed to find elements with class name = "class-dash2"'
        assert len(classDash2Ems) == 1 , 'Expected to find 1 element with class name = "class-dash2" but got %d. %s' %( len(classDash2Ems), repr(classDash2Ems))


if __name__ == '__main__':
    sys.exit(subprocess.Popen('GoodTests.py -n1 "%s" %s' %(sys.argv[0], ' '.join(['"%s"' %(arg.replace('"', '\\"'), ) for arg in sys.argv[1:]]) ), shell=True).wait())
