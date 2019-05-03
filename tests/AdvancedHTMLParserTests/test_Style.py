#!/usr/bin/env GoodTests.py
'''
    Test style attributes
'''

import subprocess
import sys

import AdvancedHTMLParser

from AdvancedHTMLParser.SpecialAttributes import StyleAttribute


class TestStyle(object):
    '''
        Test special style attribute
    '''

    def __init__(self):
        self.testHTML = '''
        <div id="testItem" style="display: block; padding-left: 5px">Hello</div>
'''

    def setup_method(self, method):
        '''
            This test writes, so reparse for every method
        '''
        self.parser =  AdvancedHTMLParser.AdvancedHTMLParser()
        self.parser.parseStr(self.testHTML)

        self.item = self.parser.getElementById('testItem')

    def test_getStyleMember(self):
        '''
            test  member access  of parsed style attribute
        '''
        item  = self.item

        assert item.style.display == 'block'

    def test_getStyleMethod(self):
        '''
            Test method access of parsed style  attribute
        '''
        item = self.item

        assert item.getStyle('display') == 'block'

    def test_getUnsetStyleMethod(self):
        '''
            Test that getting a style attribute that  hasn't been set returns empty string
        '''
        item = self.item

        assert item.getStyle('color') == ''

    def test_getUnsetStyleMember(self):
        '''
            Test that getting a style attribute that  hasn't been set returns empty string
        '''
        item = self.item

        assert item.style.color  == ''

    def test_setStyleMember(self):
        '''
            Test that  setting style attributes by their members  works as expected
        '''
        item = self.item

        item.style = 'position: relative; top: 6px;'

        assert item.style
        assert item.style.position == 'relative'
        assert item.style.top == '6px'
        assert item.style.display == '' # Should have cleared because we overrode


    def test_dashNames(self):

        item = self.item

        assert item.style.paddingLeft == '5px' , 'Expected to convert name "padding-left" to "paddingLeft" on attribute access.'

        item.style.paddingTop = '10px'

        assert item.style.paddingTop == '10px', 'Expected that after setting "paddingTop" you can retrieve it back using "paddingTop"'

        styleStr = str(item.style)

        assert 'padding-left: 5px' in styleStr , 'Expected to see dash-name "padding-left" in style string. Got: %s' %(styleStr, )

        assert 'padding-top: 10px' in styleStr, 'Expected to see dash-name "padding-top" in style string. Got: %s' %(styleStr, )

    def test_createStyleFromStyle(self):

        item = self.item

        newStyle = StyleAttribute(item.style)

        assert newStyle.display == 'block' , 'Expected new StyleAttribute from StyleAttribute to have same values. Got different value for display, expected "block", got "%s"' %(newStyle.display, )

        assert newStyle.paddingLeft == '5px', 'Expected new StyleAttribute from StyleAttribute to have same values. Got different value for padding-left, expected "5px", got "%s"' %(newStyle.paddingLeft, )

        newStyle.paddingLeft = '11px'

        assert newStyle.paddingLeft == '11px' , 'Expected to be able to change attributes on the new StyleAttribute object.'

        assert item.style.paddingLeft != '11px', 'Expected changes to the copy do not affect the original.'

    def test_setStyleMethod(self):
        tag = AdvancedHTMLParser.AdvancedTag('div')

        tag.setStyle('font-weight', 'bold')

        assert tag.getStyle('font-weight') == 'bold' , 'Expected setStyle to set style attribute (on tag.getStyle)'

        assert tag.style.fontWeight == 'bold' , 'Expected setStyle to set style attribute (on tag.style)'

        html = tag.outerHTML

        assert 'font-weight: bold' in html , 'Expected style attribute to be set on tag in html'

    def test_setStyleAttr(self):
        tag = AdvancedHTMLParser.AdvancedTag('div')

        tag.style.fontWeight = 'bold'

        assert tag.getStyle('font-weight') == 'bold' , 'Expected setStyle to set style attribute (on tag.getStyle)'

        assert tag.style.fontWeight == 'bold' , 'Expected setStyle to set style attribute (on tag.style)'

        html = tag.outerHTML

        assert 'font-weight: bold' in html , 'Expected style attribute to be set on tag in html. Got: ' + html

    def test_styleBools(self):
        '''
            test_styleBools - Assert that an empty style is not False (doesn't make sense, but that's how JS does it..
        '''
        tag1 = AdvancedHTMLParser.AdvancedTag('div')
        tag2 = AdvancedHTMLParser.AdvancedTag('div')

        assert bool(tag1.style) is True , 'Expected empty style to be True'

        tag1.style.fontWeight = 'bold'

        assert bool(tag1.style) is True , 'Expected style with a property set to be True'

        tag1.style = ''

        assert bool(tag1.style) is True , 'Expected style being set to empty string is still True'

        tag1.style = ''
        tag2.style = ''

        # TODO: This is how javascript handles it, but I disagree.
        try:
            assert tag1.style != tag2.style , 'Expected identical styles to be False'
        except AssertionError:
            sys.stderr.write('\nDiffering from javascript standard, identical style attributes on different tags equal eachother (empty string test)\n')

        tag1.style = 'float: left'
        tag2.style = 'float: left'

        # TODO: This is how javascript handles it, but I disagree.
        try:
            assert tag1.style != tag2.style , 'Expected identical styles to be False'
        except AssertionError:
            sys.stderr.write('\nDiffering from javascript standard, identical style attributes on different tags equal eachother (with property set test)\n')

    def test_styleAttributeHTML(self):

        tag1 = AdvancedHTMLParser.AdvancedTag('div')

        tag1.style = 'display: block'

        tag1Html = str(tag1)

        assert 'style=' in tag1Html , 'Expected "style=" to show up in html after being set by attribute. Got: ' + tag1Html

        assert 'display: block' in str(tag1) , 'Expected "display: block" to show up in html after being set by attribute. Got: ' + tag1Html

        tag1.style.fontWeight = 'bold'

        tag1Html = str(tag1)

        assert 'font-weight' in tag1Html , 'Expected "font-weight" to be in tag1Html after tag1.style.fontWeight = "bold". Got: ' + tag1Html

        tag2 = AdvancedHTMLParser.AdvancedTag('div')

        tag2.style.display = 'block'

        tag2Html = str(tag2)

        assert 'style=' in tag2Html , 'Expected just setting a property on style makes it show up as html attribute. Got: ' + tag2Html

        assert 'display: block' in tag2Html , 'Expected "display: block" to be in tag2Html after tag2.style.display = "block". Got: ' + tag2Html



        # Remove attributes and ensure style goes away

        tag1.style.fontWeight = ''
        tag1.style.display = ''

        tag1Html = str(tag1)

        assert 'style=' not in tag1Html , 'Expected after removing all style values that the style attribute will disappear from HTML. Got: ' + tag1Html


    def test_setProperty(self):
        '''
            test_setProperty - Test the "setProperty" method
        '''
        styleAttr = StyleAttribute('')

        styleAttr.setProperty('float', 'left')

        assert styleAttr.float == 'left' , 'Expected setProperty("float", "left") to work. It did not.'

        styleAttr.setProperty('float', '')

        assert styleAttr.float == '', 'Expected setProperty with value of empty string to remove the name.'

        try:
            styleAttr.setProperty('float', '')
        except:
            raise AssertionError('Expected to be able to clear a style property even if it was not present')

        styleAttr.setProperty('font-weight', 'bold')

        assert styleAttr.fontWeight == 'bold' , 'Expected to be able to use dash-name like "font-weight"'


    def test_styleCopy(self):
        '''
            test_styleCopy - Test if assigning a style from one tag to another creates a copy of the style attribute
                               so changing on the assigned doesn't affect both.
        '''

        tag1 = AdvancedHTMLParser.AdvancedTag('div')
        tag2 = AdvancedHTMLParser.AdvancedTag('div')

        tag1.style = "font-weight: bold; float: left;"

        assert tag1.style.fontWeight == 'bold' , 'Assigned style property "font-weight" to "bold", and style.fontWeight did not return "bold" '
        assert tag1.style.float == 'left', 'Assigned style property "float" to "left", and style.float did not return "left" '

        assert tag2.style.isEmpty(), "Expected before copy that tag2 has no style."

        # Make the assignment
        tag2.style = tag1.style

        assert not tag2.style.isEmpty(), "Expected after copy that tag2 has a style"

        assert tag1.style.fontWeight == 'bold' , 'After copy from tag1->tag2, on tag1 style.fontWeight did not return "bold" '
        assert tag1.style.float == 'left', 'After copy from tag1->tag2, on tag1 style.fontWeight did not return "bold" '

        assert tag2.style.fontWeight == 'bold' , 'After copy from tag1->tag2, on tag2 style.fontWeight did not return "bold" '
        assert tag2.style.float == 'left', 'After copy from tag1->tag2, on tag2 style.fontWeight did not return "bold" '

        assert tag2.style == "font-weight: bold; float: left"

        # Change on second tag
        tag2.style.float = 'right'

        assert tag2.style.float == 'right' , 'Tried to change tag2.style.float to "right", but did not work. Value: ' + str(tag2.style.float)

        assert tag1.style.float == 'left' , 'After changing tag2.style.float to "right", expected tag1.style.float to not change. It did.'

        tag1 = AdvancedHTMLParser.AdvancedTag('div')
        tag2 = AdvancedHTMLParser.AdvancedTag('div')

        tag1.style = 'display: block'

        tag2.style = 'float: left'

        idStyle1 = id(tag1.style)

        tag1.style = tag1.style

        assert idStyle1 == id(tag1.style) , 'Expected a self-set of style not to change variable id'

        del idStyle1

        tag1.style = tag2.style

        assert id(tag1.style) != id(tag2.style) , 'Expected style assignment from one tag to another to be a copy'

        assert tag1.style == tag2.style , 'Expected same style after assignment'

        tag1Html = str(tag1)
        tag2Html = str(tag2)

        assert 'float: left' in tag1Html , 'Expected new style to show up in tag1 (float: left). Got: ' + tag1Html
        assert 'display: block' not in tag1Html , 'Expected after assignment old style to NOT be in html. Got: ' + tag1Html

        assert tag1.style.float == 'left', 'Expected style to be copied'
        assert tag1.style.display != 'block' , 'Expected old style to be gone'

        tag2.style.display = 'inline'

        assert tag2.style.display == 'inline', 'Expected to set display to inline on tag2. Got: ' + str(tag2.style)

        tag1Html = str(tag1)
        tag2Html = str(tag2)

        assert 'display: inline' in tag2Html , 'Expected "display: inline" to be in tag2 after setting'
        assert 'display: inline' not in tag1Html , 'Expected "display: inline" to not be on tag1 after setting on tag2.'

        assert tag1.style.display != 'inline', 'Expected tag1.style.display to not be "inline" after only set on tag2.'

        tag1 = AdvancedHTMLParser.AdvancedTag('div')
        tag2 = AdvancedHTMLParser.AdvancedTag('div')

        tag1.style = 'display: block'

        oldStyle = tag1.style

        assert id(oldStyle) == id(tag1.style) , 'Expected assignment to retain identity. id(oldStyle)<%d> != id(tag1.style)<%s>' %( id(oldStyle), id(tag1.style))

        tag1.style = 'display: block'

        assert id(oldStyle) != id(tag1.style) , 'Expected assignment to equivilant string to udpate identity. id(oldStyle)<%d> == id(tag1.style)<%s>' %( id(oldStyle), id(tag1.style))

        oldStyle.float = 'left'

        assert 'float: left' in str(oldStyle) , 'Expected setting "float: left" would show up in style. Got: ' + str(oldStyle)

        assert tag1.style.float != 'left' , 'Expected updating oldStyle to not affect new style. On new style got: ' + str(tag1.style)

        assert 'float: left' not in str(tag1.style) , 'Expected update to oldStyle to not change html representation of tag with different style. str(tag1.style) = ' + str(tag1.style)
        assert 'float: left' not in str(tag1) , 'Expected update to oldStyle to not change html representation of tag with different style. str(tag1) = ' + str(tag1)


    def test_htmlAttrPresent(self):
        '''
            test_htmlAttrPresent - Test that html attribute is present when set, and not when not.
        '''
        tag = AdvancedHTMLParser.AdvancedTag('div')

        assert "style=" not in str(tag) , 'Expected style to not be in tag html. Got: ' + str(tag)

        assert 'style' not in tag.attributes , "Expected style to not be in tag attributes."

        tagCopy = tag.cloneNode()

        tag.style = 'display: block; float: left'

        tagHTML = str(tag)

        assert 'style="' in tagHTML and 'display: block' in tagHTML and 'float: left' in tagHTML , "Expected style to be set properly on tag, but was not. Got: " + tagHTML

        tag.style = ''
        tagHTML = str(tag)

        assert "style" not in tagHTML , "Expected after clearing style via tag.style='' that the attribute was gone. Got: " + tagHTML

        assert str(tag.getAttribute("style")) == "" , "Expected after clearing style via tag.style='' that attribute was gone."

        tag = tagCopy

        tagCopy = tag.cloneNode()

        assert str(tag.style) == '' , 'Expected cloned node to not have linked style to its parent'

        tag.setAttribute("style", "display: block; float: right")

        tagHTML = str(tag)

        assert 'style="' in tagHTML and 'display: block' in tagHTML and 'float: right' in tagHTML , "Expected style to be set properly on tag with setAttribute('style', ...) , but was not. Got: " + tagHTML

        tag.setAttribute('style', 'display: block')
        tagHTML = str(tag)
        assert 'style="' in tagHTML and 'display: block' in tagHTML and 'float: right' not in tagHTML , "Expected style to be set properly on tag after modification by setAttribute('style', ...) , but was not. Got: " + tagHTML

        tagCopy = tag.cloneNode()

        tag.setAttribute('style', '')

        tagHTML = str(tag)

        assert "style" not in tagHTML , "Expected setAttribute('style', '') to clear style from html, but did not. Got: " + tagHTML

        tag = tagCopy
        tagCopy = tag.cloneNode()
        tagHTML = str(tag)

        assert "style" in tagHTML , "Expected cloneNode to retain style, did not."

        tag.removeAttribute('style')
        tagHTML = str(tag)

        assert "style" not in tagHTML , "Expected removeAttribute('style') to clear style from html, but did not. Got: " + tagHTML


        tag = tagCopy


        tag.attributes['style'] = ''
        tagHTML = str(tag)

        assert "style" not in tagHTML , "Expected tag.attributes['style'] = '' to clear stlye from html, but did not. Got: " + tagHTML

        assert str(tag.style) == '' , 'Expected tag.attributes["style"] = '' to clear style attribute, but tag.style returned: ' + str(tag.style)


if __name__ == '__main__':
    sys.exit(subprocess.Popen('GoodTests.py -n1 "%s" %s' %(sys.argv[0], ' '.join(['"%s"' %(arg.replace('"', '\\"'), ) for arg in sys.argv[1:]]) ), shell=True).wait())
