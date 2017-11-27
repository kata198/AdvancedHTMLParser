'''
 Copyright (c)  2017 Tim Savannah under LGPLv3. 
  See LICENSE (https://gnu.org/licenses/lgpl-3.0.txt) for more information.

   Value-conversion methods
'''

__all__ = ('convertToIntOrNegativeOneIfUnset', 'convertToBooleanString', 'convertBooleanStringToBoolean', 
            'convertPossibleValues'
)

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
        return emptyValue

    # Convert to a string
    val = tostr(val).lower()

    # If empty string, same as null
    if val == '':
        return emptyValue

    # Check if this is a valid value
    if val not in possibleValues:
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
    return val

