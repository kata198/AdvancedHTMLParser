'''
    Copyright (c) 2019 Timothy Savannah under terms of LGPLv3. All Rights Reserved.

    See LICENSE (https://gnu.org/licenses/lgpl-3.0.txt) for more information.

    See: https://github.com/kata198/AdvancedHTMLParser for full information


    ==INTERNAL==

    xpath._debug.py - Internal module for toggling XPath debugging
'''
# vim: set ts=4 sw=4 st=4 expandtab :


__all__ = ('setXPathDebug', 'getXPathDebug')


global _XPATH_DEBUG

_XPATH_DEBUG = False
#_XPATH_DEBUG = True


def setXPathDebug(newValue):
    '''
        setXPathDebug - Function to change the global DEBUG for development.

            Will be removed / set to false for production release.

              @param newValue <bool> - True to enable debugging prints, False to disable them.
    '''
    global _XPATH_DEBUG
    _XPATH_DEBUG = newValue


def getXPathDebug():
    '''
        getXPathDebug - Get whether we should print debug messages.

            Each function call with DEBUG output should fetch a fresh copy of this.
    '''
    global _XPATH_DEBUG
    return _XPATH_DEBUG



# vim: set ts=4 sw=4 st=4 expandtab :
