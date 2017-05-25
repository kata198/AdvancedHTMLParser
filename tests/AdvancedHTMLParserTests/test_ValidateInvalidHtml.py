#!/usr/bin/env GoodTests.py
'''
    Test that we can validate some types of invalid html
'''

import sys
import subprocess

from AdvancedHTMLParser.Validator import ValidatingAdvancedHTMLParser
from AdvancedHTMLParser.exceptions import InvalidCloseException, MissedCloseException


MULTIPLE_ROOT = """
   <div id='one'>
        <span id='one_s' >
            Hello
        </span>
    </div>
    <div id='two'>
        <span id='two_s' >
            Goodbye
        </span>
    </div>
"""
 

INVALID_CLOSE = """
    <html>
        <div id="one">
            <span>Hello</span>
        </span>
        </div>
    </html>
"""

MISS_CLOSE = """
    <html>
        <div id="one">
            <span>Hello
        </div>
    </html>
"""

CATCH_OPTIONAL_CLOSE = """
    <html>
        <div id="one">
            <img src="blah.gif">
        </div>
    </html>
"""

class TestValidateInvalidHtml(object):

    def test_HandleMultipleRoot(self):
        '''
            test_HandleMultipleRoot - Make sure Validator parser still works to parse
        '''
        parser = ValidatingAdvancedHTMLParser()
        try:
            parser.parseStr(MULTIPLE_ROOT)
        except Exception as e:
            raise AssertionError('Failed to properly parse invalid HTML with multiple root nodes')

        oneEm = parser.getElementById('one')
        assert oneEm , 'Failed to find first element'
        assert len(parser.getRootNodes()) == 2

    def test_HandleInvalidClose(self):
        '''
            test_HandleInvalidClose - Properly raise exception when an invalid close is attempted
        '''
        parser = ValidatingAdvancedHTMLParser()

        exceptionObj = None
        try:
            parser.parseStr(INVALID_CLOSE)
        except InvalidCloseException as e:
            exceptionObj = e
        except Exception as e:
            raise AssertionError('Failed to properly parse invalid HTML with invalid close')

        assert exceptionObj is not None, 'Failed to catch InvalidClose'

        assert exceptionObj.triedToClose == 'span'
        assert [x.tagName for x in exceptionObj.stillOpen]  == ['html', 'div']

    def test_HandleMissClose(self):
        '''
            test_HandleMissClose - Properly raise exception when a close is missed that matters
        '''
        parser = ValidatingAdvancedHTMLParser()
        exceptionObj = None
        try:
            parser.parseStr(MISS_CLOSE)
        except MissedCloseException as e:
            exceptionObj = e
        except Exception as e:
            raise AssertionError('Failed to properly parse invalid HTML with missed close')

        assert exceptionObj is not None, 'Failed to catch invalid HTML with missed close'

    def test_HandleMissOptionalClose(self):
        '''
            test_HandleMissOptionalClose - Don't throw exception on optional-close cases
        '''
        parser = ValidatingAdvancedHTMLParser()
        exceptionObj = None
        try:
            parser.parseStr(CATCH_OPTIONAL_CLOSE)
        except MissedCloseException as e:
            exceptionObj = e
        except Exception as e:
            raise AssertionError('Failed to properly parse invalid HTML with missed close')

        assert exceptionObj is None, 'Raised exception on HTML with optional close'



if __name__ == '__main__':
    sys.exit(subprocess.Popen('GoodTests.py -n1 "%s" %s' %(sys.argv[0], ' '.join(['"%s"' %(arg.replace('"', '\\"'), ) for arg in sys.argv[1:]]) ), shell=True).wait())
