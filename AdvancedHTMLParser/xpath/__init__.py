'''
    Copyright (c) 2019 Timothy Savannah under terms of LGPLv3. All Rights Reserved.

    See LICENSE (https://gnu.org/licenses/lgpl-3.0.txt) for more information.

    See: https://github.com/kata198/AdvancedHTMLParser for full information

    xpath - Provide xpath support

        NOTE: THIS IS STILL IN ALPHA.

            Several parts of the XPath spec are not yet implemented,
             nor has the code yet been organized or optimized.

'''
# vim: set ts=4 st=4 sw=4 expandtab :

from .expression import XPathExpression

__all__ = ('XPathExpression', )
