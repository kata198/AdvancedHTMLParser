'''
    Copyright (c)  2017 Tim Savannah under LGPLv3. All Rights Reserved.

    See LICENSE (https://gnu.org/licenses/lgpl-3.0.txt) for more information.

    Value-conversion methods
'''

__all__ = ('convertToIntOrNegativeOneIfUnset', 'convertToBooleanString', 'convertBooleanStringToBoolean',
            'convertPossibleValues', 'convertToIntRange', 'convertToIntRangeCapped', 'EMPTY_IS_INVALID',
)

class _EMPTY_IS_INVALID_TYPE(object):
    '''
        _EMPTY_IS_INVALID_TYPE - Special type for EMPTY_IS_INVALID singleton
    '''
    pass

# EMPTY_IS_INVALID - A singleton to specify that passing an empty value should be treated
#                       as the "invalidDefault" path
EMPTY_IS_INVALID = _EMPTY_IS_INVALID_TYPE()


def convertToIntOrNegativeOneIfUnset(val=None):
    '''
        convertToIntOrNegativeOneIfUnset - Converts value to an integer, or -1 if unset

        @param val <int/str/None> - Value

        Takes a value, if not set returns -1. If not an integer, returns 0
    '''
    if val in (None, ''):
        return -1
    try:
        return int(val)
    except:
        return 0

def convertToBooleanString(val=None):
    '''
        convertToBooleanString - Converts a value to either a string of "true" or "false"

            @param val <int/str/bool> - Value
    '''
    if hasattr(val, 'lower'):
        val = val.lower()

        # Technically, if you set one of these attributes (like "spellcheck") to a string of 'false',
        #   it gets set to true. But we will retain "false" here.
        if val in ('false', '0'):
            return 'false'
        else:
            return 'true'

    try:
        if bool(val):
            return "true"
    except:
        pass

    return "false"

def convertBooleanStringToBoolean(val=None):
    '''
        convertBooleanStringToBoolean - Convert from a boolean attribute (string "true" / "false" ) into a booelan
    '''
    if not val:
        return False

    if hasattr(val, 'lower'):
        val = val.lower()

    if val == "false":
        return False
    return True


def convertToPositiveInt(val=None, invalidDefault=0):
    '''
        convertToPositiveInt - Convert to a positive integer, and if invalid use a given value
    '''
    if val is None:
        return invalidDefault

    try:
        val = int(val)
    except:
        return invalidDefault

    if val < 0:
        return invalidDefault

    return val

def _handleInvalid(invalidDefault):
    '''
        _handleInvalid - Common code for raising / returning an invalid value

            @param invalidDefault <None/str/Exception> - The value to return if "val" is not empty string/None
                                                           and "val" is not in #possibleValues

                     If instantiated Exception (like ValueError('blah')):  Raise this exception

                     If an Exception type ( like ValueError ) - Instantiate and raise this exception type

                     Otherwise, use this raw value
    '''
    # If not
    #   If an instantiated Exception, raise that exception
    try:
        isInstantiatedException = bool( issubclass(invalidDefault.__class__, Exception) )
    except:
        isInstantiatedException = False

    if isInstantiatedException:
        raise invalidDefault
    else:
        try:
            isExceptionType = bool( issubclass( invalidDefault, Exception) )
        except TypeError:
            isExceptionType = False

        #   If an Exception type, instantiate and raise
        if isExceptionType:
            raise invalidDefault()
        else:
        #   Otherwise, just return invalidDefault itself
            return invalidDefault


def convertPossibleValues(val, possibleValues, invalidDefault, emptyValue=''):
    '''
        convertPossibleValues - Convert input value to one of several possible values,

                                    with a default for invalid entries

            @param val <None/str> - The input value

            @param possibleValues list<str> - A list of possible values

            @param invalidDefault <None/str/Exception> - The value to return if "val" is not empty string/None
                                                           and "val" is not in #possibleValues

                     If instantiated Exception (like ValueError('blah')):  Raise this exception

                     If an Exception type ( like ValueError ) - Instantiate and raise this exception type

                     Otherwise, use this raw value

            @param emptyValue Default '', used for an empty value (empty string or None)


    '''
    from .utils import tostr

    # If null, retain null
    if val is None:
        if emptyValue is EMPTY_IS_INVALID:
            return _handleInvalid(invalidDefault)
        return emptyValue

    # Convert to a string
    val = tostr(val).lower()

    # If empty string, same as null
    if val == '':
        if emptyValue is EMPTY_IS_INVALID:
            return _handleInvalid(invalidDefault)
        return emptyValue

    # Check if this is a valid value
    if val not in possibleValues:
        return _handleInvalid(invalidDefault)

    return val


def convertToIntRange(val, minValue, maxValue, invalidDefault, emptyValue=''):
    '''
        converToIntRange - Convert input value to an integer within a certain range

            @param val <None/str/int/float> - The input value

            @param minValue <None/int> - The minimum value (inclusive), or None if no minimum

            @param maxValue <None/int> - The maximum value (inclusive), or None if no maximum

            @param invalidDefault <None/str/Exception> - The value to return if "val" is not empty string/None
                                                           and "val" is not in #possibleValues

                     If instantiated Exception (like ValueError('blah')):  Raise this exception

                     If an Exception type ( like ValueError ) - Instantiate and raise this exception type

                     Otherwise, use this raw value

            @param emptyValue Default '', used for an empty value (empty string or None)


    '''
    from .utils import tostr

    # If null, retain null
    if val is None or val == '':
        if emptyValue is EMPTY_IS_INVALID:
            return _handleInvalid(invalidDefault)
        return emptyValue

    try:
        val = int(val)
    except ValueError:
        return _handleInvalid(invalidDefault)

    if minValue is not None and val < minValue:
        return _handleInvalid(invalidDefault)
    if maxValue is not None and val > maxValue:
        return _handleInvalid(invalidDefault)

    return val

def convertToIntRangeCapped(val, minValue, maxValue, invalidDefault, emptyValue=''):
    '''
        converToIntRangeCapped - Convert input value to an integer within a certain range, capping the value potentially at a minimum or maximum

            @param val <None/str/int/float> - The input value

            @param minValue <None/int> - The minimum value (inclusive), or None if no minimum

            @param maxValue <None/int> - The maximum value (inclusive), or None if no maximum

            @param invalidDefault <None/str/Exception> - The value to return if "val" is not empty string/None
                                                           and "val" is not in #possibleValues

                     If instantiated Exception (like ValueError('blah')):  Raise this exception

                     If an Exception type ( like ValueError ) - Instantiate and raise this exception type

                     Otherwise, use this raw value

            @param emptyValue Default '', used for an empty value (empty string or None)


    '''
    from .utils import tostr

    # If null, retain null
    if val is None or val == '':
        if emptyValue is EMPTY_IS_INVALID:
            return _handleInvalid(invalidDefault)
        return emptyValue

    try:
        val = int(val)
    except ValueError:
        return _handleInvalid(invalidDefault)

    if minValue is not None and val < minValue:
        val = minValue

    if maxValue is not None and val > maxValue:
        val = maxValue

    return val

