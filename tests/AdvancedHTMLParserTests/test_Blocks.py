#!/usr/bin/env GoodTests.py
'''
    Test blocks
'''

import subprocess
import sys

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


    def test_addBlocks(self):
        document =  AdvancedHTMLParser.AdvancedHTMLParser()

        document.parseStr(self.basicHTML)

        existingDivEm = document.getElementById('existingDiv')

        assert existingDivEm , 'Failed to get id="existingDiv"'
        
        
        textBlock = 'Blah Text'
        

if __name__ == '__main__':
    sys.exit(subprocess.Popen('GoodTests.py -n1 "%s" %s' %(sys.argv[0], ' '.join(['"%s"' %(arg.replace('"', '\\"'), ) for arg in sys.argv[1:]]) ), shell=True).wait())
