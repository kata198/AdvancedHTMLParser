#!/usr/bin/env GoodTests.py
'''
    Test various comparison methods
'''

import copy
import sys
import subprocess

from AdvancedHTMLParser.Tags import AdvancedTag
from AdvancedHTMLParser.Parser import AdvancedHTMLParser

class TestCompare(object):
    '''
        Tests some attribute behaviour
    '''

    def test_tagOperators(self):

        parser = AdvancedHTMLParser()
        parser.parseStr('''<html> <body>
        <div id="hello"  class="classX classY" cheese="cheddar" > <span>Child</span><span>Other Child</span> </div>
        <div id="hello2" class="classX classY" cheese="cheddar" > <span>Child</span><span>Other Child</span> </div>
        <div id="goodbye" one="1"> Yay </div>

        <div id="sameAttrChildren">
          <div class="classX classY" cheese="gouda">Blah</div>
          <div class="classX classY" cheese="gouda">Blah</div>
        </div>
</body></html>''')


        helloTag = parser.getElementById('hello')
        assert helloTag, 'Expected to fetch tag with id="hello" but failed.'

        hello2Tag = parser.getElementById('hello2')
        assert hello2Tag, 'Expected to fetch tag with id="hello2" but failed.'

        goodbyeTag = parser.getElementById('goodbye')
        assert goodbyeTag, 'Expected to fetch tag with id="goodbye" but failed.'

        tagsEq = ( helloTag == hello2Tag )

        assert tagsEq is False , "Expected different tags with same attributes names to not be =="

        tagsNe = ( helloTag != hello2Tag )

        assert tagsNe is True, "Expected different tags with same attributes names to be !="

        sameTagEq = ( helloTag == helloTag )

        assert sameTagEq is True, "Expected same tag to == itself"

        diffTagsEq = (helloTag == goodbyeTag)

        assert diffTagsEq is False, "Expected different tags with different attributes to not be =="

        diffTagsNe = (helloTag != goodbyeTag)

        assert diffTagsNe is True, "Expected different tags with different attributes to be !="

        helloTagCopy = copy.copy(helloTag)

        copyEq = (helloTag == helloTagCopy)

        assert copyEq is False, "Expected copy of tag to not == original"

        copyNe = (helloTag != helloTagCopy)

        assert copyNe is True, "Expected copy of tag to != original"

        helloTagCopyRecon = AdvancedTag(helloTag.tagName, helloTag.getAttributesList(), helloTag.isSelfClosing)

        copyEq = (helloTag == helloTagCopyRecon)

        assert copyEq is False , "Expected reconstruction of tag to not == original"

        copyNe = (helloTag != helloTagCopyRecon)

        assert copyNe is True, "Expected reconstruction of tag to != original"

        helloTagFetch2 = parser.getElementById('hello')

        fetchEq = (helloTag == helloTagFetch2)

        assert fetchEq is True, "Expected fetching the same tag is =="

        fetchNe = (helloTag != helloTagFetch2)

        assert fetchNe is False, "Expected fetching the same tag to not be !="

        sameAttrChildrenEm = parser.getElementById('sameAttrChildren')

        child1 = sameAttrChildrenEm.children[0]
        child2 = sameAttrChildrenEm.children[1]

        childrenEq = (child1 == child2)

        assert childrenEq is False, "Expected elements with exact same attributes and values but different individual tags to not be =="

        childrenNe = (child1 != child2)

        assert childrenNe is True, "Expected elements with exact same attributes and values but different individual tags to be !="

    def test_isTagEqual(self):

        parser = AdvancedHTMLParser()
        parser.parseStr('''<html> <body>
        <div id="hello"  class="classX classY" cheese="cheddar" > <span>Child</span><span>Other Child</span> </div>
        <div id="hello2" class="classX classY" cheese="cheddar" > <span>Child</span><span>Other Child</span> </div>
        <div id="goodbye" one="1"> Yay </div>

        <div id="sameAttrChildren">
          <div class="classX classY" cheese="gouda">Blah</div>
          <div class="classX classY" cheese="gouda">Blah</div>
          <div class="classY classX" cheese="gouda">Blah</div>
        </div>
        <div id="sameAttrChildrenSpans">
          <span class="classX classY" cheese="gouda">Blah</span>
          <span class="classX classY" cheese="gouda">Blah</span>
          <span class="classY classX" cheese="gouda">Blah</span>
        </div>
</body></html>''')


        helloTag = parser.getElementById('hello')
        assert helloTag, 'Expected to fetch tag with id="hello" but failed.'

        hello2Tag = parser.getElementById('hello2')
        assert hello2Tag, 'Expected to fetch tag with id="hello2" but failed.'

        goodbyeTag = parser.getElementById('goodbye')
        assert goodbyeTag, 'Expected to fetch tag with id="goodbye" but failed.'


        helloTagsEq = (helloTag.isTagEqual(hello2Tag))

        assert helloTagsEq is False, "Expected tags with same attribute names but different values (id) to not be equal."

        sameAttrChildrenEm = parser.getElementById('sameAttrChildren')

        child1 = sameAttrChildrenEm.children[0]
        child2 = sameAttrChildrenEm.children[1]
        child3 = sameAttrChildrenEm.children[2]

        assert child1.isTagEqual(child2) is True, "Expected tags with exact same tag name and attributes return isTagEqual as True"

        assert child1.isTagEqual(child3) is False, "Expected tags with exact same tag name and attributes (but class name in different order) return isTagEqual as False"

        # TODO: Style should compare the same regardless of order

        sameAttrChildrenSpansEm = parser.getElementById('sameAttrChildrenSpans')

        childSpan1 = sameAttrChildrenSpansEm[0]
        childSpan2 = sameAttrChildrenSpansEm[1]
        childSpan3 = sameAttrChildrenSpansEm[2]

        assert childSpan1.isTagEqual(childSpan2) is True, "Expected tags with exact same tag name and attributes return isTagEqual as True"

        assert child1.isTagEqual(childSpan1) is False, "Expected tags with exact same attributes but different tag name to return isTagEqual as False"

        child1Copy = copy.copy(child1)

        assert child1.isTagEqual(child1Copy) is True, "Expected copy of tag to return isTagEqual as True"

        # Do a deep copy so we can change attributes and not affect the former
        child1Copy = copy.copy(child1)

        child1Copy.setAttribute("cheese", "none")

        assert child1.isTagEqual(child1Copy) is False, "Expected same tag name same attribute names but different value to return isTagEqual as False"

    def test_cloneNode(self):
        parser = AdvancedHTMLParser()
        parser.parseStr('''
        <div id="hello"  class="classX classY" cheese="cheddar" > <span>Child</span><span>Other Child</span> </div>
        ''')

        helloEm = parser.getElementById('hello')

        helloClone = helloEm.cloneNode()

        for attributeName in ('id', 'class', 'cheese'):
            helloEmValue = helloEm.getAttribute(attributeName, None)
            helloCloneValue = helloClone.getAttribute(attributeName, None)
            assert helloEmValue == helloCloneValue, 'Expected cloneNode to return an exact copy, got different %s. %s != %s' %(attributeName, repr(helloEmValue), repr(helloCloneValue))

        assert helloEm.childElementCount == 2 , 'Expected original helloEm to retain two direct children'
        assert helloClone.childElementCount == 0 , 'Expected clone to NOT copy children'



if __name__ == '__main__':
    sys.exit(subprocess.Popen('GoodTests.py -n1 "%s" %s' %(sys.argv[0], ' '.join(['"%s"' %(arg.replace('"', '\\"'), ) for arg in sys.argv[1:]]) ), shell=True).wait())
