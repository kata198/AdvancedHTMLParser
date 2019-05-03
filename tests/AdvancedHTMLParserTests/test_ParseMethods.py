#!/usr/bin/env GoodTests.py
'''
    Test that Parse methods work as expected
'''

import sys
import subprocess
import tempfile

from AdvancedHTMLParser.Parser import AdvancedHTMLParser

TEST_HTML = b"""<html>
  <head>
  </head>
  <body>
    <span>1\xe2\x88\x9a4</span>
    <div id="farm">
      <span>Moo</span>
      <span>Cock-a-doodle-doo</span>
    </div>
  </body>
</html>
"""


class TestParseMethods(object):

    def setup_class(self):
        self.tempFile = tempfile.NamedTemporaryFile()
        self.tempFile.write(TEST_HTML)
        self.tempFile.flush()

    def teardown_class(self):
        self.tempFile.close()


    def test_ParseFile(self):
        parser = AdvancedHTMLParser()
        try:
            parser.parseFile(self.tempFile.name)
        except Exception as e:
            raise AssertionError('Failed to parse file, exception was: %s' %(str(e),))

        testEm = parser.getElementById('farm')
        assert testEm , 'Failed to extract data from file parsing'
        assert len(testEm.children) == 2 , 'Invalid data from file parsing'
        assert testEm.children[0].innerHTML.strip() == 'Moo' , 'Invalid data from file parsing'





    def test_ParseStr(self):
        parser = AdvancedHTMLParser()

        parser.parseStr(TEST_HTML)

        testEm = parser.getElementById('farm')
        assert testEm , 'Failed to extract data'
        assert len(testEm.children) == 2 , 'Invalid data from file parsing'
        assert testEm.children[0].innerHTML.strip() == 'Moo' , 'Invalid data from file parsing'


    def test_encodingWorkingStr(self):
        parser = AdvancedHTMLParser(encoding='ascii')

        gotException = False
        try:
            parser.parseStr(TEST_HTML)
        except UnicodeDecodeError as e:
            gotException = True

        assert gotException is True, 'Should have failed to parse unicode characters in ascii codec, probably not using passed encoding'

    def test_encodingWorkingFile(self):
        parser = AdvancedHTMLParser(encoding='ascii')

        gotException = False
        try:
            parser.parseFile(self.tempFile.name)
        except UnicodeDecodeError as e:
            gotException = True

        assert gotException is True, 'Should have failed to parse unicode characters in ascii codec, probably not using passed encoding'




if __name__ == '__main__':
    sys.exit(subprocess.Popen('GoodTests.py -n1 "%s" %s' %(sys.argv[0], ' '.join(['"%s"' %(arg.replace('"', '\\"'), ) for arg in sys.argv[1:]]) ), shell=True).wait())
