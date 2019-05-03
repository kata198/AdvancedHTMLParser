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

class TestTagClass(object):
    '''
        TestTagClass - GoodTests dealing with the 'class' attribute and related methods and interactions thereof.
    '''

    def test_setClassNameString(self):
        '''
            test_setClassNameString - Test setting the "className" attribute on an AdvancedTag and it being reflected.
        '''

        tag = AdvancedTag('div')

        assert "class=" not in tag.getHTML() , "Expected to not find 'class=' when none is set. Got: " + tag.getHTML()

        assert 'class' not in tag.attributes , 'Expected "class" to not be "in" attributes'

        # Try initial set

        tag.className = "cheese is good"

        assert 'class' in tag.attributes , 'Expected "class" to be "in" attributes'


        assert tag.className == "cheese is good" , "Expected className to equal 'cheese is good' after assign on className attribute. Got: " + repr(tag.className)

        assert 'class="cheese is good"' in str(tag) , "Expected to find class=\"cheese is good\" after set on className attribute. Got: " + str(tag)

        assert tag.classList == ['cheese', 'is', 'good'] , "Expected classList to be set after setting on className attribute. Got: " + repr(tag.classList)

        assert 'class' in tag.attributes.keys() ,  'Expected "class" to be in .keys()'

        # Try changing

        tag.className = "hello world"

        assert tag.className == "hello world" , "Expected to be able to change className attribute. Got: " + repr(tag.className)

        assert 'class="hello world"' in str(tag) , "Expected to be able to change className and have it show up in html attribute. Got: " + str(tag)

        assert tag.classList == ['hello', 'world'] , "Expected to be able to change className attribute, but update not reflected in classList. Got: " + repr(tag.classList)

        # Try removing

        tag.className = ''

        assert tag.className == '' , "Expected to be able to clear className attribute. Got: " + repr(tag.className)

        assert "class=" not in str(tag) , "Expected class attribute to not be on HTML representation after clearing className. Got: " + str(tag)

        assert tag.classList == [] , "Expected to be able to clear className attribute, but did not update classList to empty list. Got: " + repr(tag.classList)


    def test_setClassNameSetAttribute(self):
        '''
            test_setClassNameSetAttribute - Test setting/changing/removing the class attribute using setAttribute and friends.
        '''
        tag = AdvancedTag('div')

        assert "class=" not in tag.getHTML() , "Expected to not find 'class=' when none is set. Got: " + tag.getHTML()

        # Try initial set

        tag.setAttribute("class", "cheese is good")

        assert tag.className == "cheese is good" , "Expected className to equal 'cheese is good' after setAttribute('class', ...). Got: " + repr(tag.className)

        assert 'class="cheese is good"' in str(tag) , "Expected to find class=\"cheese is good\" after setAttribute('class', ...). Got: " + str(tag)

        assert tag.classList == ['cheese', 'is', 'good'] , "Expected classList to be set after setAttribute('class', ...). Got: " + repr(tag.classList)

        # Try changing

        tag.setAttribute("class", "hello world")

        assert tag.className == "hello world" , "Expected to be able to change class using setAttribute('class', ...). Got: " + repr(tag.className)

        assert 'class="hello world"' in str(tag) , "Expected to be able to change class using setAttribute('class', ...)  and have it show up in html attribute. Got: " + str(tag)

        assert tag.classList == ['hello', 'world'] , "Expected to be able to change class using setAttribute('class', ...), but update not reflected in classList. Got: " + repr(tag.classList)

        # Try removing, both through removeAttribute and setAttribute('class', '')

        tag1 = tag.cloneNode()

        tag2 = tag.cloneNode()

        tag1.removeAttribute('class')

        assert tag1.className == '' , "Expected to be able to clear class attribute using removeAttribute. Got: " + repr(tag1.className)

        assert "class=" not in str(tag1) , "Expected class attribute to not be on HTML representation after removeAttribute. Got: " + str(tag1)

        assert tag1.classList == [] , "Expected to be able to clear class attribut with removeAttributee, but did not update classList to empty list. Got: " + repr(tag1.classList)

        # Ensure cloneNode unlinked class attribute
        assert tag2.className == 'hello world', 'Expected clearing tag1 (cloned node of tag) to not affect tag2 (another cloned node of tag). className was effected.'
        assert tag2.classList == ['hello', 'world'], 'Expected clearing tag1 (cloned node of tag) to not affect tag2 (another cloned node of tag). classList was effected.'
        assert 'class="hello world"' in str(tag2), 'Expected clearing tag1 (cloned node of tag) to not affect tag2 (another cloned node of tag). class on string of html was effected.'

        tag2.setAttribute('class', '')

        assert tag2.className == '' , "Expected to be able to clear class attribute using setAttribute('class', ''). Got: " + repr(tag2.className)

        assert "class=" not in str(tag2) , "Expected class attribute to not be on HTML representation after setAttribute('class', ''). Got: " + str(tag2)

        assert tag2.classList == [] , "Expected to be able to clear class attribut with setAttribute('class', '')e, but did not update classList to empty list. Got: " + repr(tag2.classList)


    def test_classListCopy(self):
        '''
            test_classListCopy - Test that changing the list returned from .classList
                    does NOT affect the class attributes on a node (same as JS).
        '''

        tag = AdvancedTag('div')

        tag.className = "hello world"

        classList = tag.classList

        classList.append('xxx')

        assert 'xxx' not in tag.className , 'Expected .classList return to be independent of source tag, but changing affected className attribute'

        assert 'class="hello world"' in str(tag) , 'Expected .classList return to be independent of source tag, but changing affected class in HTML representation'

        assert tag.classList == ['hello', 'world'] , 'Expected .classList return to be independent of source tag, but changing affected return of .classList'


    def test_tagClassMethods(self):
        '''
            test_tagClassMethods - test class methods like addClass, removeClass, hasClass
        '''

        tag = AdvancedTag('div')

        ret = tag.removeClass('blah')
        assert ret is None , "Expected to get None from tag.removeClass trying to remove non-existant class. Got: " + repr(ret)

        # Set initial classes
        tag.className = "hello world"

        # Add a class
        tag.addClass("welcome")

        assert 'class="hello world welcome"' in str(tag) , "Expected addClass to add class, but did not change HTML representation. Got: " + str(tag)

        assert tag.className == "hello world welcome" , "Expected addClass to add class, but did not change className property. Got: " + repr(tag.className)

        assert tag.classList == ['hello', 'world', 'welcome'] , "Expected addClass to add class, but did not return expected ordered classList. Got: " + repr(tag.classList)

        assert tag.hasClass("hello") , "Expected hasClass('hello') to return True."
        assert tag.hasClass("world") , "Expected hasClass('world') to return True."
        assert tag.hasClass("welcome") , "Expected hasClass('welcome') to return True."
        assert not tag.hasClass("blah") , "Expected hasClass('blah') to return False."


        # Remove middle class

        tag.removeClass("world")

        assert 'class="hello welcome"' in str(tag) , "Expected removeClass to remove class, but did not change HTML representation. Got: " + str(tag)

        assert tag.className == "hello welcome" , "Expected removeClass to remove class, but did not change className property. Got: " + repr(tag.className)

        assert tag.classList == ["hello", "welcome" ], "Expected removeClass to remove class, but did get expected classList. Got: " + repr(tag.classList)


        # Try to add a duplicate class

        tag.addClass("hello")
        assert 'class="hello welcome"' in str(tag) , "Expected addClass to not add duplicate class, but changed HTML representation. Got: " + str(tag)

        assert tag.className == "hello welcome" , "Expected addClass to not add duplicate class, but changed className property. Got: " + repr(tag.className)

        assert tag.classList == ['hello', 'welcome' ] , "Expected addClass to not add duplicate class, but did not return expected ordered classList. Got: " + repr(tag.classList)



    def test_parsing(self):
        '''
            test_parsing - Test that the parser properly handles several cases of class attribute,
                             and that they are mutable in expected ways thereafter.
        '''

        someHtml = '''<html><body>
        <div class="one two three" id="firstDiv">Some text</div>
        <div id="secondDiv">This one is empty</div>
        <div class="three ZZ AA" id="thirdDiv">Last one</div>
        <div class="" id="emptyClassDiv">Empty</div>
</body></html>'''

        document = AdvancedHTMLParser()
        document.parseStr(someHtml)

        firstDiv = document.getElementById('firstDiv')
        secondDiv = document.getElementById('secondDiv')
        thirdDiv = document.getElementById('thirdDiv')
        emptyClassDiv = document.getElementById('emptyClassDiv')


        assert firstDiv , 'Failed to get element by id="firstDiv"'
        assert secondDiv , 'Failed to get element by id="secondDiv"'
        assert thirdDiv , 'Failed to get element by id="thirdDiv"'
        assert emptyClassDiv , 'Failed to get element by id="emptyClassDiv"'

        firstDivHTML = firstDiv.getHTML()
        secondDivHTML = secondDiv.getHTML()
        thirdDivHTML = thirdDiv.getHTML()
        emptyClassDivHTML = emptyClassDiv.getHTML()

        assert 'class="one two three"' in firstDivHTML , 'Expected string of class to show up in parsed html. Got: ' + firstDivHTML
        assert 'class=' not in secondDivHTML , 'Expected class attribute to not be present when no class set. Got: ' + secondDivHTML
        assert 'class="three ZZ AA"' in thirdDivHTML , 'Expected string of class to show up in parsed html. Got: ' + thirdDivHTML
        assert 'class=' not in emptyClassDivHTML , 'Expected class attribute to not be present when class set to empty in parsed html, i.e. class="". Got: ' + emptyClassDivHTML


        assert firstDiv.className == "one two three" , "Expected parsed className to match 'one two three' Got: " + repr(firstDiv.className)
        assert secondDiv.className == "" , "Expected parsed lack of className to match empty string, \"\" Got: " + repr(secondDiv.className)
        assert thirdDiv.className == "three ZZ AA" , "Expected parsed className to match 'three ZZ AA' Got: " + repr(thirdDiv.className)

        assert emptyClassDiv.className == "" , "Expected parse empty className to remain empty string. Got: " + repr(emptyClassDiv.className)

        assert firstDiv.classList == ["one", "two", "three"] , 'wrong classList'
        assert secondDiv.classList == [] , "wrong classList"
        assert thirdDiv.classList == ["three", "ZZ", "AA"] , "wrong classList"
        assert emptyClassDiv.classList == [] , "Wrong classList"

        # Check that we can modify and it shows up
        firstDiv.setAttribute('class', 'cheese is good')

        firstDivHTML = firstDiv.getHTML()

        assert 'class="cheese is good"' in firstDivHTML , "Expected to be able to change parsed element through code, and it apply changes. Updates not reflected in tag attribute. Got: " + firstDivHTML

        assert firstDiv.className == "cheese is good" , "Expected to be able to change parsed element through code, and it apply changes. Updates not reflected on AdvancedTag className attribute. Got: " + firstDiv.className

        assert firstDiv.classList == ["cheese", "is", "good"] , "Expected to be able to change parsed element through code, and it apply changes. Updates not reflected on AdvancedTag className attribute. Got: " + repr(firstDiv.classList)


        # TODO: Also test empty class attribute that it can be modified

    def test_stripClassName(self):
        '''
            test_stripClassName - Ensure class names are properly stripped
        '''
        x = AdvancedTag('div')

        x.addClass("  hello")

        assert x.className == "hello" , "Expected className to be stripped after addClass. Got: " + repr(x.className)

        assert x.classList == ["hello"] , "Expected 'class' to be stripped in 'classList' after addClass. Got: " + repr(x.classList)


        x = AdvancedTag('div')

        x.className = "  hello   goodbye"

        assert x.className == "hello goodbye" , "Expected className to be stripped after setting .className. Got: " + repr(x.className)

        assert x.classList == ["hello", "goodbye"] , "Expected className to be stripped and empty strings removed on classList. Got: " + repr(x.classList)


        x.addClass("hello  ")

        assert x.className == "hello goodbye" , "Expected addClass to strip class name before trying to add so as to not duplicate. Got: " + repr(x.className)

        assert x.classList == ["hello", "goodbye"] , "Expected addClass to strip class name before trying to add so as to not duplicate. Got: " + repr(x.classList)


        x.addClass("")

        assert x.className == "hello goodbye" , "Expected addClass on empty string to not affect className. Got: " + repr(x.className)

        assert x.classList == ["hello", "goodbye"], "Expected addClass on empty string to not affect classList. Got: " + repr(x.classList)

        x.addClass("  ")

        assert x.className == "hello goodbye" , "Expected addClass on whitespace string to not affect className. Got: " + repr(x.className)

        assert x.classList == ["hello", "goodbye"], "Expected addClass on whitespace string to not affect classList. Got: " + repr(x.classList)

        x.removeClass("")

        assert x.className == "hello goodbye" , "Expected removeClass on empty string to not affect className. Got: " + repr(x.className)

        assert x.classList == ["hello", "goodbye"], "Expected removeClass on empty string to not affect classList. Got: " + repr(x.classList)

        x.removeClass(" ")

        assert x.className == "hello goodbye" , "Expected removeClass on whitespace string to not affect className. Got: " + repr(x.className)

        assert x.classList == ["hello", "goodbye"], "Expected removeClass on whitespace string to not affect classList. Got: " + repr(x.classList)

        x = AdvancedTag('div')

        x.className = "hello   goodbye  "

        assert x.className == "hello goodbye" , "Expected setting class with extra whitespace to have extra whitespace stripped. className attribute not as expected. Got: " + repr(x.className)

        assert x.classList == ["hello", "goodbye"], "Expected setting class with extra whitespace to have extra whitespace stripped. classList not as expected. Got: " + repr(x.className)

        x.addClass('cheddar butter')

        assert x.className == 'hello goodbye cheddar butter' , 'Expected tag.addClass("cheddar butter") to add both "cheddar" and "butter" classes, but .className attribute only shows: ' + repr(x.className)

        assert x.classList == ['hello', 'goodbye', 'cheddar', 'butter'] , 'Expected tag.addClass("cheddar butter") to add both "cheddar" and "butter" classes, but .classList attribute only shows: ' + repr(x.classList)


        x.removeClass("   hello    cheddar ")

        assert x.className == "goodbye butter" , "Expected tag.removeClass('   hello    cheddar ') to split and strip and remove both 'hello' and 'cheddar' classes. className only shows: " + repr(x.className)

        assert x.classList == ["goodbye", "butter"] , "Expected tag.removeClass('   hello    cheddar ') to split and strip and remove both 'hello' and 'cheddar' classes. classList only shows: " + repr(x.classList)


    def test_strClassList(self):
        '''
            test_strClassList - Assert that a classList can be str'd (equiv to tag.classList.toString()) to get a " " join
        '''

        x = AdvancedTag('div')

        x.className = 'hello world welcome to the pizza haven'

        classList = x.classList

        assert len(classList) == 7 , 'Expected classList to contain 7 elements'

        strClassName = str(classList)

        assert strClassName == 'hello world welcome to the pizza haven' , 'Expected to be able to str() the .classList to get className'

        assert strClassName == x.className , 'Expected str of classList to be the same as .className'


if __name__ == '__main__':
    sys.exit(subprocess.Popen('GoodTests.py -n1 "%s" %s' %(sys.argv[0], ' '.join(['"%s"' %(arg.replace('"', '\\"'), ) for arg in sys.argv[1:]]) ), shell=True).wait())
