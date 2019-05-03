#!/usr/bin/env GoodTests.py
'''
    Test conversions
'''

import pickle
import subprocess
import sys

import AdvancedHTMLParser

from AdvancedHTMLParser.conversions import (convertToIntOrNegativeOneIfUnset, convertToBooleanString,
    convertBooleanStringToBoolean, convertPossibleValues, convertToIntRange, convertToIntRangeCapped
)

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

        try:
            assert convertedValue == expectedValue , 'Expected %s to return %s for value=%s. Got: %s' %( method.__name__, repr(expectedValue), repr(inputValue), repr(convertedValue))
        except AssertionError as ae:
            raise ae
        except Exception as e:
            raise AssertionError('Got unexpected Exception %s ( %s ) from %s instead of expected result %s for value=%s' %( str(e.__class__.__name__), str(e), method.__name__, repr(expectedValue), repr(inputValue)))


    @classmethod
    def _test_convert_raises(cls, method, inputValue, exceptionType):
        '''
            _test_convert_raises - Perform a test using a conversion method, an input, and assert that

                                        an exception of a given type is raised.

                @param method <method> - A conversion method

                @param inputValue <anything> - Value to pass to conversion method

                @param exceptionType <Exception> - Assert that this exception is raised

                @return <Exception> - The exception raised
        '''

        gotExpectedException = False
        theException = None

        try:
            convertedValue = method(inputValue)
        except exceptionType as e:
            gotExpectedException = True
            theException = e
        except Exception as e2:
            raise AssertionError('Call to %s expected to get an Exception of type %s, but instead got a %s exception.' %(method.__name__, exceptionType.__name__, e2.__class__.__name__))

        assert gotExpectedException is True , 'Call to %s expected to get an Exception of type %s, but instead got a return value: %s' %(method.__name__, exceptionType.__name__, repr(convertedValue))

        return theException

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


    def test_convertToIntRange(self):
        '''
            test_convertToIntRange - Test the convertToIntRange method
        '''
        def doTestResult(inputValue, minValue, maxValue, invalidDefault, expectedValue):
            '''
                doTestResult - Perform a test of convertToIntRange where the expected return is a result (not an exception)

                @see doTestRaises for the exception case

            '''

            # Create a method do call convertToIntRange with the args that fits into the self._test_convert framework
            _testMethod = lambda _inputValue : convertToIntRange(_inputValue, minValue, maxValue, invalidDefault)

            # Give it a meaningful name for the assertion message
            _testMethod.__name__ = 'convertToIntRange( _inputValue, minValue=%s, maxValue=%s, invalidDefault=%s )' %( repr(minValue), repr(maxValue), repr(invalidDefault))

            return self._test_convert( _testMethod, inputValue, expectedValue)


        def doTestRaises(inputValue, minValue, maxValue, invalidDefault):
            '''
                doTestRaises - Perform a test of convertToIntRange where the expected result is an exception to be raised.

                @see doTestResult for the returned value case
            '''
            # Create a method do call convertToIntRange with the args that fits into the self._test_convert framework
            _testMethod = lambda _inputValue : convertToIntRange(_inputValue, minValue, maxValue, invalidDefault)

            try:
                if issubclass(invalidDefault, Exception):
                    expectedExceptionType = invalidDefault
                else:
                    raise Exception('goto except')
            except:
                if issubclass(invalidDefault.__class__, Exception):
                    expectedExceptionType = invalidDefault.__class__
                else:
                    raise Exception('Provided invalidDefault param %s does not seem to be an Exception type..' %( repr(invalidDefault), ))

            # Give it a meaningful name for the assertion message
            _testMethod.__name__ = 'convertToIntRange( _inputValue, minValue=%s, maxValue=%s, invalidDefault=%s )' %( repr(minValue), repr(maxValue), repr(invalidDefault))

            return self._test_convert_raises( _testMethod, inputValue, expectedExceptionType)


        # Test that doTestResult method works
        doTestResult("5", 0, 10, "INVALID", 5)


        # Test that doTestRaises method works
        doTestRaises("1", 2, 5, ValueError)


        doTestResult("5", 5, 10, "INVALID", 5)
        doTestResult("5", 0, 5, "INVALID", 5)
        doTestResult("5", None, 10, "INVALID", 5)
        doTestResult("5", 0, None, "INVALID", 5)


        doTestResult("5", 1, 4, "INVALID", "INVALID")
        doTestResult("5", 6, None, "INVALID", "INVALID")
        doTestResult("5", None, 4, "INVALID", "INVALID")

        doTestRaises("5", 1, 4, ValueError)
        doTestRaises("5", 6, None, ValueError)
        doTestRaises("5", None, 4, ValueError)

        doTestRaises("abc", 2, 5, ValueError)

    def test_convertToIntRangeCapped(self):
        '''
            test_convertToIntRangeCapped - Test the convertToIntRangeCapped method
        '''
        def doTestResult(inputValue, minValue, maxValue, invalidDefault, expectedValue):
            '''
                doTestResult - Perform a test of convertToIntRangeCapped where the expected return is a result (not an exception)

                @see doTestRaises for the exception case

            '''

            # Create a method do call convertToIntRangeCapped with the args that fits into the self._test_convert framework
            _testMethod = lambda _inputValue : convertToIntRangeCapped(_inputValue, minValue, maxValue, invalidDefault)

            # Give it a meaningful name for the assertion message
            _testMethod.__name__ = 'convertToIntRangeCapped( _inputValue, minValue=%s, maxValue=%s, invalidDefault=%s )' %( repr(minValue), repr(maxValue), repr(invalidDefault))

            return self._test_convert( _testMethod, inputValue, expectedValue)


        def doTestRaises(inputValue, minValue, maxValue, invalidDefault):
            '''
                doTestRaises - Perform a test of convertToIntRangeCapped where the expected result is an exception to be raised.

                @see doTestResult for the returned value case
            '''
            # Create a method do call convertToIntRangeCapped with the args that fits into the self._test_convert framework
            _testMethod = lambda _inputValue : convertToIntRangeCapped(_inputValue, minValue, maxValue, invalidDefault)

            try:
                if issubclass(invalidDefault, Exception):
                    expectedExceptionType = invalidDefault
                else:
                    raise Exception('goto except')
            except:
                if issubclass(invalidDefault.__class__, Exception):
                    expectedExceptionType = invalidDefault.__class__
                else:
                    raise Exception('Provided invalidDefault param %s does not seem to be an Exception type..' %( repr(invalidDefault), ))

            # Give it a meaningful name for the assertion message
            _testMethod.__name__ = 'convertToIntRangeCapped( _inputValue, minValue=%s, maxValue=%s, invalidDefault=%s )' %( repr(minValue), repr(maxValue), repr(invalidDefault))

            return self._test_convert_raises( _testMethod, inputValue, expectedExceptionType)


        # Test that doTestResult method works
        doTestResult("5", 0, 10, "INVALID", 5)


        # Test that doTestRaises method works
        doTestRaises("abc", 2, 5, ValueError)


        doTestResult("5", 5, 10, "INVALID", 5)
        doTestResult("5", 0, 5, "INVALID", 5)
        doTestResult("5", None, 10, "INVALID", 5)
        doTestResult("5", 0, None, "INVALID", 5)


        doTestResult("5", 1, 4, "INVALID", 4)
        doTestResult("5", 6, None, "INVALID", 6)
        doTestResult("5", None, 4, "INVALID", 4)



    def test_convertPossibleValues(self):
        '''
            test_convertPossibleValues - Test the convertPossibleValues method
        '''

        def doTestResult(inputValue, possibleValues, invalidDefault, expectedValue):
            '''
                doTestResult - Perform a test of convertPossibleValues where the expected return is a result (not an exception)

                @see doTestRaises for the exception case

            '''

            # Create a method do call convertPossibleValues with the args that fits into the self._test_convert framework
            _testMethod = lambda _inputValue : convertPossibleValues(_inputValue, possibleValues, invalidDefault)

            # Give it a meaningful name for the assertion message
            _testMethod.__name__ = 'convertPossibleValues( _inputValue, possibleValues=%s, invalidDefault=%s )' %( repr(possibleValues), repr(invalidDefault))

            return self._test_convert( _testMethod, inputValue, expectedValue)


        def doTestRaises(inputValue, possibleValues, invalidDefault):
            '''
                doTestRaises - Perform a test of convertPossibleValues where the expected result is an exception to be raised.

                @see doTestResult for the returned value case
            '''
            # Create a method do call convertPossibleValues with the args that fits into the self._test_convert framework
            _testMethod = lambda _inputValue : convertPossibleValues(_inputValue, possibleValues, invalidDefault)

            try:
                if issubclass(invalidDefault, Exception):
                    expectedExceptionType = invalidDefault
                else:
                    raise Exception('goto except')
            except:
                if issubclass(invalidDefault.__class__, Exception):
                    expectedExceptionType = invalidDefault.__class__
                else:
                    raise Exception('Provided invalidDefault param %s does not seem to be an Exception type..' %( repr(invalidDefault), ))

            # Give it a meaningful name for the assertion message
            _testMethod.__name__ = 'convertPossibleValues( _inputValue, possibleValues=%s, invalidDefault=%s )' %( repr(possibleValues), repr(invalidDefault))

            return self._test_convert_raises( _testMethod, inputValue, expectedExceptionType)



        # Test that doTestResult is working
        doTestResult( 'hello', ['hello', 'goodbye'], 'INVALID', 'hello' )

        # Test that doTestRaises is working
        doTestRaises( 'hello', ['blah', ], ValueError )

        # Ensure we lowercase the input value
        doTestResult('Hello', ['hello', 'goodbye'], 'INVALID', 'hello')

        # Assert we get the "INVALID" option when no match
        doTestResult('hello', ['cheese', 'blah'], 'INVALID', 'INVALID')

        # Ensure we get empty string back for empty string input
        doTestResult('', ['cheese', 'blah'], 'INVALID', '')

        # Ensure we get empty string back for None input
        doTestResult(None, ['cheese', 'blah'], 'INVALID', '')

        # Check that we handle an instantiated exception as well
        theException = doTestRaises( 'hello', ['cheese', 'doodles'], ValueError('Bad man you are'))

        assert str(theException) == 'Bad man you are' , 'Expected that the instantiated Exception we passed gets raised as-is. Got: ' + repr(theException)


if __name__ == '__main__':
    sys.exit(subprocess.Popen('GoodTests.py -n1 "%s" %s' %(sys.argv[0], ' '.join(['"%s"' %(arg.replace('"', '\\"'), ) for arg in sys.argv[1:]]) ), shell=True).wait())
