#!/usr/bin/env GoodTests.py
'''
    Test pickling
'''

import pickle
import subprocess
import sys

import AdvancedHTMLParser

AdvancedTag = AdvancedHTMLParser.AdvancedTag

class TestPickle(object):
    '''
        A general test class. Basically example.py converted a bit.

    '''

    def test_pickleTagGeneral(self):
        '''
            pickleTagGeneral - Test simple pickling a lone AdvancedTag
        '''

        # Test just a general tag first
        tag = AdvancedHTMLParser.AdvancedTag('div')
        tag.id = 'myDiv'
        tag.className = 'one two'

        pickleStr = pickle.dumps(tag)

        assert pickleStr , "Failed to get a pickle dump from AdvancedTag"

        loadedTag = pickle.loads(pickleStr)

        assert issubclass(loadedTag.__class__, AdvancedHTMLParser.AdvancedTag) , 'Failed to get an AdvancedTag object loading from pickled string'

        assert loadedTag.id == 'myDiv' , 'Pickle failed to retain id of tag'
        assert loadedTag.className == 'one two' , 'Pickle failed to retain className'
        assert loadedTag.tagName == 'div' , 'Pickle failed to retain tagName'
        assert loadedTag.uid == tag.uid , "Failed to retain uid after restore from pickle"

        assert loadedTag.isTagEqual(tag) , 'isTagEqual returned False'



    def test_pickleTagComplex(self):
        '''
            test_pickleTagComplex - Test more complex variations on a tag
        '''
        mainDivTag = AdvancedTag('div')
        mainDivTag.id = 'mainDiv'
        mainDivTag.setAttribute('x-cheese', 'cheddar')

        subspan1 = AdvancedTag('span')
        subspan1.setAttribute('id', 'subspan1')
        subspan1.name = 'subspans'
        subspan1.style = 'display: block; float: left; clear: both;'

        subspan1.appendText("My Text")

        mainDivTag.appendChild(subspan1)

        subspan2 = AdvancedTag('span')
        subspan2.setAttribute('id', 'subspan2')
        subspan2.name = 'subspans'
        subspan2.className = "heavy-text quoteblock"

        imgTag = AdvancedTag('img')
        imgTag.src = '/images/cheese.png'
        imgTag.style.width = '80px'
        imgTag.style.height = '60px'

        subspan2.appendChild(imgTag)

        mainDivTag.appendChild(subspan2)


        pickleStr = pickle.dumps(mainDivTag)

        assert pickleStr , "Was unable to get a pickle string from complex AdvancedTag"

        loadedMainDivTag = pickle.loads(pickleStr)

        assert issubclass(loadedMainDivTag.__class__, AdvancedTag) , "Loaded pickle string but did not get AdvancedTag back. Got: " + type(loadedMainDivTag).__name__

        assert loadedMainDivTag.id == "mainDiv" , "Loaded pickle did not retain id on mainDiv"
        assert loadedMainDivTag.getAttribute("x-cheese") == "cheddar" , "Loaded pickle did not retain 'x-cheese' attribute."

        assert len(loadedMainDivTag.children) == 2 , "Loaded pickle did not retain 2 children. children property is: " + repr(loadedMainDivTag.children)

        loadedChild1 = loadedMainDivTag.children[0]
        assert loadedChild1.tagName == 'span' , "Expected first child on loaded pickle to have tagName='span'. Got: " + repr(loadedChild1.tagName)
        assert loadedChild1.id == 'subspan1' , "Expected first child on loaded pickle to have id='subspan1'. Got: " + repr(loadedChild1.id)
        assert loadedChild1.name == 'subspans' , 'Expected first child on loaded pickle to have name="subspans". Got: ' + repr(loadedChild1.name)

        for styleName, styleValue in [ ('display', 'block'), ('float', 'left'), ('clear', 'both') ]:
            loadedChild1StyleVal = getattr(loadedChild1.style, styleName)
            assert loadedChild1StyleVal == styleValue , 'Wrong value for style property "%s" on first child. Expected "%s" but got "%s"' %(styleName, styleValue, loadedChild1StyleVal)

        loadedChild1StartTag = loadedChild1.getStartTag()
        assert "display: block" in loadedChild1StartTag , 'style.display missing in HTML representation after pickle load. Got: ' + repr(loadedChild1StartTag)

        assert "<span" in loadedChild1StartTag, "Missing correct tag name in HTML representation after pickle load. Got: " + repr(loadedChild1StartTag)

        assert "My Text" in loadedChild1.text , "Expected 'My Text' to appear in .text attribute. Got: " + repr(loadedChild1.text)

        assert "My Text" in str(loadedChild1) , "Expected 'My Text' to appear in HTML reprsentation. Got: " + repr(str(loadedChild1))

        loadedChild2 = loadedMainDivTag.children[1]

        assert loadedChild2.tagName == 'span' , 'Expected tagName to be "span", but got: ' + repr(loadedChild2.tagName)
        assert loadedChild2.id == 'subspan2' , 'Expected id="subspan2" but got: ' + repr(loadedChild2.id)
        assert loadedChild2.getAttribute('name') == 'subspans' , "Expected name='subspans' but got: " + repr(loadedChild2.getAttribute('name'))

        assert 'heavy-text' in loadedChild2.classList , "Expected 'heavy-text' to be in classList, but got: " + repr(loadedChild2.classList)
        assert loadedChild2.className == 'heavy-text quoteblock' , 'Expected className to be "heavy-text quoteblock" but got: ' + repr(loadedChild2.className)

        assert len(loadedChild2.children) == 1 , 'Expected 1 child node for subspan2. Children are: ' + repr(loadedChild2.children)


        loadedImgTag = loadedChild2.children[0]

        assert loadedImgTag.tagName == 'img' , 'Expected tagName="img" but got: ' + repr(loadedImgTag.tagName)
        assert loadedImgTag.src == '/images/cheese.png' , 'Got unexpected "src" attribute. Got: ' + repr(loadedImgTag.src)

        loadedImgTagStyle = loadedImgTag.style
        assert loadedImgTagStyle.width == '80px' , 'Expected width: 80px but got: ' + repr(loadedImgTagStyle.width)
        assert loadedImgTagStyle.height == '60px' , 'Expected height: 60px but got: ' + repr(loadedImgTagStyle.height)

        assert 'height: 60px' in str(loadedImgTagStyle) and 'width: 80px' in str(loadedImgTagStyle) , 'Expected style to contain both "width: 80px" and "height: 60px" but it was: ' + repr(str(loadedImgTagStyle))

        assert len(loadedImgTag.children) == 0 , 'Expected image tag to have no children'
        assert loadedImgTag.uid == imgTag.uid , 'Did not retain uid on img. Expected "%s" but got "%s"' %(str(imgTag.uid), str(loadedImgTag.uid))

        assert mainDivTag.isTagEqual(loadedMainDivTag) , 'mainDivTag.isTagEqual(loadedMainDivTag) returned False'
        assert subspan1.isTagEqual(loadedChild1) , 'subspan1.isTagEqual(loadedChild1) returned False'
        assert subspan2.isTagEqual(loadedChild2) , 'subspan2.isTagEqual(loadedChild2) returned False'
        assert imgTag.isTagEqual(loadedImgTag) , 'img.isTagEqual(loadedImgTag) returned False'


    def test_pickleParser(self):
        '''
            test_pickleParser - Test pickling the parser
        '''
        document = AdvancedHTMLParser.AdvancedHTMLParser()

        document.parseStr('''
<html>
    <head>
        <title>Hello World Page</title>
    </head>
    <body bgcolor="black" style="background-color: black; color: white">
        <div id="main">
            <h2>This is a test page</h2>
            <br />
            <br />
            <div id="subDiv">
                <span id="text1">This</span> is a sub div
                <div class="some-div" >
                    Embedded again
                </div>
                <div class="some-div cheese" style="font-weight: bold">
                    Some bold embedded test
                </div>
            </div>
        </div>
    </body>
</html>
''')
        pickleStr = pickle.dumps(document)

        assert pickleStr , "Failed to get a pickle str for an AdvancedHTMLParser.AdvancedHTMLParser assembled with parseStr."

        loadedDocument = pickle.loads(pickleStr)

        assert issubclass(loadedDocument.__class__, AdvancedHTMLParser.AdvancedHTMLParser)

        allOrigNodes = document.getAllNodes()
        allLoadedNodes = loadedDocument.getAllNodes()

        assert len(allOrigNodes) == len(allLoadedNodes) , 'Got different number of nodes after load. Orig %d != Loaded %d' %( len(allOrigNodes), len(allLoadedNodes))

        bodyEm = document.body
        loadedBodyEm = loadedDocument.body

        assert bodyEm.isTagEqual(loadedBodyEm) , 'bodyEm.isTagEqual(loadedBodyEm) returned False'

        assert bodyEm.ownerDocument == document , 'ownerDocument not correct on original body node'
        assert loadedBodyEm.ownerDocument == loadedDocument , 'ownerDocument on unpickled body not set to unpickled document'

        assert id(loadedBodyEm.ownerDocument) == id(loadedDocument) , 'ownerDocument does not share same identity as unpickled document'
        assert id(loadedBodyEm.ownerDocument) != id(document) , "Expected the unpickled ownerDocument to not share identity with the original document"



    def test_pickleThenModify(self):
        '''
            test_pickleThenModify - Ensure that unpickled tags can be modified,

                those modifications take hold, and do not affect the originals
        '''
        mainDivTag = AdvancedTag('div')
        mainDivTag.id = 'mainDiv'
        mainDivTag.className = 'firstClass second-class'
        mainDivTag.setAttribute('x-cheese', 'cheddar')

        subspan1 = AdvancedTag('span')
        subspan1.setAttribute('id', 'subspan1')
        subspan1.name = 'subspans'
        subspan1.style = 'display: block; float: left; clear: both;'

        subspan1.appendText("My Text")

        mainDivTag.appendChild(subspan1)

        pickleStr = pickle.dumps(mainDivTag)

        assert pickleStr , "Was unable to get a pickle string from complex AdvancedTag"

        loadedMainDivTag = pickle.loads(pickleStr)

        assert issubclass(loadedMainDivTag.__class__, AdvancedTag) , "Loaded pickle string but did not get AdvancedTag back. Got: " + type(loadedMainDivTag).__name__

        assert loadedMainDivTag.id == "mainDiv" , "Loaded pickle did not retain id on mainDiv"

        loadedMainDivTag.id = 'copyOfMainDiv'

        assert loadedMainDivTag.getAttribute('id') == 'copyOfMainDiv' , 'Unable to change id attribute'
        assert 'copyOfMainDiv' in loadedMainDivTag.getStartTag() , 'change to id attribute not reflected in generated HTML. Got: ' + repr(loadedMainDivTag.getStartTag())

        loadedMainDivTag.addClass('cheese')

        assert 'cheese' in loadedMainDivTag.classList , 'Expected .addClass to be able to add a class to the unpickled tag. Got: ' + repr(loadedMainDivTag.classList)

        assert 'cheese' not in mainDivTag.classList , 'Expected .addClass to not affect the original tag.'

        assert loadedMainDivTag.className == 'firstClass second-class cheese' , 'Expected .addClass to append to .className on unpickeld tag'
        assert mainDivTag.className == 'firstClass second-class' , 'Expected .addClass to not affect original tag .className'

        loadedSubspan1 = loadedMainDivTag.children[0]

        assert loadedSubspan1.id == 'subspan1' , 'Got unexpected first child. Expected subspan1, got: ' + repr(str(loadedSubspan1))

        loadedSubspan1.style.display = 'inline'

        assert 'display: inline' in str(loadedSubspan1.style) , 'Expected to be able to change style, display -> inline, on unpickled tag. Got: ' + repr(str(loadedSubspan1.style))

        assert 'display: block' in str(subspan1.style) and 'display: inline' not in str(subspan1.style) , 'Expected to be able to change style, display -> inline, on unpickled tag without affecting original. Got: ' + repr(str(subspan1.style))



if __name__ == '__main__':
    sys.exit(subprocess.Popen('GoodTests.py -n1 "%s" %s' %(sys.argv[0], ' '.join(['"%s"' %(arg.replace('"', '\\"'), ) for arg in sys.argv[1:]]) ), shell=True).wait())
