'''
    Copyright (c) 2019 Timothy Savannah under terms of LGPLv3. All Rights Reserved.

    See LICENSE (https://gnu.org/licenses/lgpl-3.0.txt) for more information.

    See: https://github.com/kata198/AdvancedHTMLParser for full information


    ==INTERNAL==

    xpath._cache.py - Internal module for caching recent XPath expression parsings
'''
# vim: set ts=4 sw=4 st=4 expandtab :

import threading

from hashlib import sha1

from ..compat import ensureStringEncoded

__all__ = ('XPathExpressionCache', 'XPathExpressionCacheType', )

# MAX_CACHED_EXPRESSIONS - The maximum number of cached expressions before we perform a clean-up of the cache
MAX_CACHED_EXPRESSIONS = 10

# CLEAR_AT_ONE_TIME - The number of cached expressions that we clear from the cache upon exceeding #MAX_CACHED_EXPRESSIONS
CLEAR_AT_ONE_TIME = 3

class XPathExpressionCacheType(object):
    '''
        XPathExpressionCacheType - The type of the XPath Expression Cache.

            This is meant to be used as a singleton, the instance being "XPathExpressionCache"
    '''

    def __init__(self):
        '''
            __init__ - Create this object
        '''

        self.cachedCompiledExpressions = {}
        self.recentCachedExpressionStrs = []

        self.cacheLock = threading.Lock()


    @staticmethod
    def getKeyForExpressionStr(expressionStr):
        '''
            getKeyForExpressionStr - Get a unique hash "key" for a given expression str,

                as will be used to cache the compiled expression.


                    @param expressionStr <str/unicode/bytes> - The XPath expression str


                    @return <str> - The key
        '''
        expressionStr = ensureStringEncoded(expressionStr)

        return sha1(expressionStr).hexdigest()


    def getCachedExpression(self, expressionStr):
        '''
            getCachedExpression - Try to get a cached XPathExpression object for a given key


                @param expressionStr <str> - The XPath expression str


                @return <XPathExpression/None> - The XPathExpression object, if one was cached, otherwise None
        '''
        key = self.getKeyForExpressionStr(expressionStr)

        self.cacheLock.acquire()
        xpathExpressionObj = self.cachedCompiledExpressions.get(key, None)

        if xpathExpressionObj is None:
            self.cacheLock.release()
            return None

        # We got a match, mark it as hot
        while True:
            # Ensure we remove all references, if multiple got in somehow
            try:
                self.recentCachedExpressionStrs.remove(key)
            except ValueError:
                break

        # Add single refernce to end (hot side) of list
        self.recentCachedExpressionStrs.append(key)

        self.cacheLock.release()

        # And return the expression obj
        return xpathExpressionObj


    def applyCachedExpressionIfAvailable(self, expressionStr, xpathExpressionObj):
        '''
            applyCachedExpressionIfAvailable - Check if a cached compiled expression object is available, based on the xpath expression string,

                and if it is, update the expression object's members with the cached version.


                    @param expressionStr <str> - The XPath expression str

                    @param xpathExpressionObj <xpath.expression.XPathExpression> - The expression object


                    @return <bool> - True if did apply from cache, False if no match (expression needs to be compiled)
        '''
        cachedExpression = self.getCachedExpression(expressionStr)
        if cachedExpression is None:
            return False

        xpathExpressionObj._copyOperationsFromXPathExpressionObj(cachedExpression)
        return True


    def setCachedExpression(self, expressionStr, xpathExpressionObj):
        '''
            setCachedExpression - Sets the expression object to be cached under a given string


                @param expressionStr <str> - The XPath expression str

                @param xpathExpressionObj <XPathExpression> - The XPathExpression object
        '''
        key = self.getKeyForExpressionStr(expressionStr)
        self.cacheLock.acquire()
        try:
            while True:
                # Ensure we remove all references, if multiple got in somehow
                try:
                    self.recentCachedExpressionStrs.remove(key)
                except ValueError:
                    break

            self.cachedCompiledExpressions[key] = xpathExpressionObj
            self.recentCachedExpressionStrs.append(key)

            numCachedExpressionStrs = len(self.recentCachedExpressionStrs)
            if numCachedExpressionStrs > MAX_CACHED_EXPRESSIONS:

                numRemainingAfterClear = MAX_CACHED_EXPRESSIONS - CLEAR_AT_ONE_TIME

                # Gather and remove overflow
                keysToRemove = self.recentCachedExpressionStrs[ : len(self.recentCachedExpressionStrs) - numRemainingAfterClear ]
                for keyToRemove in keysToRemove:
                    try:
                        del self.cachedCompiledExpressions[keyToRemove]
                    except:
                        pass

                # Retain references to remaining
                self.recentCachedExpressionStrs = self.recentCachedExpressionStrs[ -1 * numRemainingAfterClear : ]

        except Exception as exc:
            self.cacheLock.release()
            raise exc

        self.cacheLock.release()

# XPathExpressionCache - The singleton instance of the XPath Expression Cache. Use this instead of creating a new XPathExpressionCacheType()
XPathExpressionCache = XPathExpressionCacheType()


# vim: set ts=4 sw=4 st=4 expandtab :
