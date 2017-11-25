#!/usr/bin/env GoodTests.py
'''
    Test conversions
'''

import pickle
import subprocess
import sys

import AdvancedHTMLParser

from AdvancedHTMLParser.conversions import convertToIntOrNegativeOneIfUnset, convertToBooleanString, convertBooleanStringToBoolean

AdvancedTag = AdvancedHTMLParser.AdvancedTag

class TestConversions(object):
    '''
        Test conversions

    '''

    @classmethod
    def _test_convert(cls, method, inputValue, expectedValue):
        '''
            _test_convert - Perform a test using a conversion method, an input, and match against an expected value.

                @param method <method> - A conversion method

                @param inputValue <anything> - Value to pass to conversion method

                @param expectedValue <anything> - Expected value after conversion
        '''
        
        convertedValue = method(inputValue)

        assert convertedValue == expectedValue , 'Expected %s to return %s for value=%s. Got: %s' %( method.__name__, repr(expectedValue), repr(inputValue), repr(convertedValue))


    def test_convertToIntOrNegativeOneIfInset(self):
        '''
            test_convertToIntOrNegativeOneIfInset - Test the convertToIntOrNegativeOneIfUnset conversion method
        '''
        
        doTest = lambda inputValue, expectedValue : self._test_convert(convertToIntOrNegativeOneIfUnset, inputValue, expectedValue)

        doTest( None, -1)
        doTest( True, 1) # Odd, but this is how firefox behaves..
        doTest( False, 0)
        doTest( "Yes", 0)
        doTest( "Hamburrrrrger", 0)
        doTest( 16, 16)
        doTest( 1, 1)
        doTest(0, 0)
        doTest(-1, -1)
        doTest(-14, -14)


    def test_convertToBooleanString(self):
        '''
            test_convertToBooleanString - Test the convertToBooleanString method
        '''

        doTest = lambda inputValue, expectedValue : self._test_convert(convertToBooleanString, inputValue, expectedValue)

        doTest(None, "false")
        doTest(True, "true")
        doTest(False, "false")
        doTest("yes", "true")
        doTest("no", "true")
        doTest(0, "false")
        doTest(1, "true")
        doTest(10, "true")
        doTest(-10, "true")

    def test_convertBooleanStringToBoolean(self):
        '''
            test_convertBooleanStringToBoolean - Test the convertBooleanStringToBoolean method
        '''
        doTest = lambda inputValue, expectedValue : self._test_convert(convertBooleanStringToBoolean, inputValue, expectedValue)

        doTest(None, False)
        doTest("true", True)
        doTest("TRuE", True)
        doTest("false", False)
        doTest("fAlSe", False)
        doTest("FAlsE", False)

#from AdvancedHTMLParser.conversions import convertToIntOrNegativeOneIfUnset, convertToBooleanString, convertBooleanStringToBoolean

if __name__ == '__main__':
    sys.exit(subprocess.Popen('GoodTests.py -n1 "%s" %s' %(sys.argv[0], ' '.join(['"%s"' %(arg.replace('"', '\\"'), ) for arg in sys.argv[1:]]) ), shell=True).wait())
