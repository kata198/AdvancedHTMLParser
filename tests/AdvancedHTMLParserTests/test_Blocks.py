#!/usr/bin/env GoodTests.py
'''
    Test blocks
'''

import subprocess
import sys
import re

import AdvancedHTMLParser

AdvancedTag = AdvancedHTMLParser.Tags.AdvancedTag

class TestBlocks(object):

    def setup_class(self):
        self.basicHTML = '''<html><head><title>Hello</title></head>
<body>
    <div id="topDiv">
    </div>

    <div id="existingDiv">
        Start Text
        <span id="existingDiv_sub1">
        Sub1 <span>Blah</span> Sub2
        </span>
        Middle Text
        <span>Hoo</span>
        End Text
    </div>
</body>
</html>
'''

    def test_findText(self):
        document =  AdvancedHTMLParser.AdvancedHTMLParser()

        document.parseStr(self.basicHTML)

        existingDivEm = document.getElementById('existingDiv')

        assert existingDivEm , 'Failed to get id="existingDiv"'

        innerHTML = existingDivEm.innerHTML

        assert 'Start Text' in innerHTML , 'Expected to find "Start Text", before any child elements'
        assert 'Middle Text' in innerHTML , 'Expected to find "Middle Text", between child elements'
        assert 'End Text' in innerHTML , 'Expected to find "End Text", after child elements'


    def test_append(self):
        document =  AdvancedHTMLParser.AdvancedHTMLParser()

        document.parseStr(self.basicHTML)

        existingDivEm = document.getElementById('existingDiv')

        assert existingDivEm , 'Failed to get id="existingDiv"'

        textBlock = 'Blah Text'

        existingDivEm.append(textBlock)

        assert 'Blah Text' in existingDivEm.text

        spanEm = document.createElement('span')
        spanEm.setAttribute("id", "mySpan")

        retBlock = existingDivEm.append(spanEm)

        assert 'mySpan' in existingDivEm.outerHTML , 'Expected append(AdvancedTag) to add a tag to representation'


    def test_tagBlocks(self):
        '''
            test_tagBlocks - Test the "tagBlocks" property and related
        '''

        document = AdvancedHTMLParser.AdvancedHTMLParser()

        document.parseStr(self.basicHTML)

        existingDivEm = document.getElementById('existingDiv')

        # Test the property
        tagBlocks = existingDivEm.tagBlocks

        assert len(tagBlocks) == 2 , "Expected to get 2 tagBlocks within existingDiv. Got %d: " %( len(tagBlocks), repr(tagBlocks) )

        assert tagBlocks[0].tagName == 'span' and tagBlocks[0].id == "existingDiv_sub1" , "Expected to get the 'existingDiv_sub1' span as first tagBlock. tagBlocks returned: %s" %(str(tagBlocks), )

        assert tagBlocks[1].tagName == 'span' and tagBlocks[1].id == "" and "Hoo" in tagBlocks[1].text, "Expected to get the second span as second entry in tagBlocks. tagBlocks retrned: %s" %(str(tagBlocks), )

        # Make sure we are getting a COPY back
        someEm = document.createElement('div')
        someEm.id = "Great div"
        someEm.appendText("Hello Everybody")

        tagBlocks.append(someEm)

        assert len(tagBlocks) == 3 and someEm in tagBlocks , 'Failed to append to returned tagBlocks list'

        newTagBlocks = existingDivEm.tagBlocks

        assert len(newTagBlocks) == 2 , "Expected modifying the list returned by tagBlocks to not affect the element"


    def test_appendBlock(self):
        document =  AdvancedHTMLParser.AdvancedHTMLParser()

        document.parseStr(self.basicHTML)

        existingDivEm = document.getElementById('existingDiv')

        assert existingDivEm , 'Failed to get id="existingDiv"'

        textBlock = 'Blah Text'

        existingDivEm.appendBlock(textBlock)

        assert 'Blah Text' in existingDivEm.text

        spanEm = document.createElement('span')
        spanEm.setAttribute("id", "mySpan")

        retBlock = existingDivEm.appendBlock(spanEm)

        assert 'mySpan' in existingDivEm.outerHTML , 'Expected appendBlock(AdvancedTag) to add a tag to representation'


    @staticmethod
    def _checkContainsAllText(haystack, *needles):
        '''
            _checkContainsAllText - Checks #haystack for the strings found in #needles,

                    and returns a list containing any entries in #needles that were not in #haystack.

                @param haystack <str> - The string to search

                @param needles (several args) - The strings to search for, each one as an argument.

                @return list<str> - A list of any strings searched for that did not appear in #haystack

              Example:
              --------

                  _checkContainsAllText("The quick brown fox jumped over the lazy dog", "lazy", "cat", "brown", "ran")

                   ^ Return for this would be   ["cat", "ran"]
                       because those two search terms were not within the haystack text
        '''
        notFound = []

        for needle in needles:
            if needle not in haystack:
                notFound.append(needle)

        return notFound


    def test_textBlocks(self):
        '''
            test_textBlocks - Test the "textBlocks" property and related
        '''

        document = AdvancedHTMLParser.AdvancedHTMLParser()

        document.parseStr(self.basicHTML)

        existingDivEm = document.getElementById('existingDiv')

        # Test the property
        textBlocks = existingDivEm.textBlocks

        nonEmptyTextBlocks = [tblock for tblock in textBlocks if len(tblock.strip()) > 0 ]

        joinedTextBlocks = ''.join(textBlocks)

        assert len(nonEmptyTextBlocks) == 3 , "Expected to get 3 non-whitespace text nodes. Got %d : %s" %( len(nonEmptyTextBlocks), str(nonEmptyTextBlocks) )


        # Test the checkContainsAllText method..

        testLst = self._checkContainsAllText("The quick brown fox jumped over the lazy dog", "jumped", "over", "lollypop", "dog", "tom")

        assert len(testLst) == 2 and testLst[0] == "lollypop" and testLst[1] == "tom" , "self._checkContainsAllText did not work as expected. Expected ['lollypop', 'tom'] and got %s" %(repr(testLst), )

        missingTexts = self._checkContainsAllText(joinedTextBlocks, "Start Text", "Middle Text", "End Text")

        assert len( missingTexts ) == 0  , "Could not find expected strings in the text nodes: %s" %( repr(missingTexts), )


    def test_text(self):
        '''
            test_text - Test innerText and textContent properties
        '''

        document = AdvancedHTMLParser.AdvancedHTMLParser()
        document.parseStr('''<html><head></head>
<body>
    <div id="main">Hello world <span>this is cool </span><div>and the text just keeps going <span>and going</span> on and on forever.</div> Have a good night!</div>
</body>
</html>''')

        def stripExtraWhitespace(text):
            text = text.strip()

            text = re.sub('[ ][ ]+', ' ', text)

            return text

        mainEm = document.getElementById('main')

        assert mainEm and mainEm.tagName == 'div' and mainEm.id == 'main' , 'Unable to fetch div id="main" via getElementById. Got: ' + repr(mainEm)

        innerText = mainEm.innerText

        innerTextStripped = stripExtraWhitespace(innerText)

        assert innerTextStripped == 'Hello world Have a good night!' , 'Expected innerText (stripped) to be "Hello world Have a good night!" but got: ' + repr(innerTextStripped)

        textContent = mainEm.textContent

        textContentStripped = stripExtraWhitespace(textContent)


        expectedStr = 'Hello world this is cool and the text just keeps going and going on and on forever. Have a good night!'

        assert textContentStripped == expectedStr , 'Expected .textContent to collate ALL text, and have a stripped value of "%s" but got: %s' %(expectedStr, textContentStripped)

if __name__ == '__main__':
    sys.exit(subprocess.Popen('GoodTests.py -n1 "%s" %s' %(sys.argv[0], ' '.join(['"%s"' %(arg.replace('"', '\\"'), ) for arg in sys.argv[1:]]) ), shell=True).wait())
