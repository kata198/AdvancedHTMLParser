#!/usr/bin/env python

from setuptools import setup

long_description = """
AdvancedHTMLParser
==================

AdvancedHTMLParser is an Advanced HTML Parser (with optional indexing), writer, and formatter, and html->xhtml formtter written in python, and compatible and tested in Python 2.7 and Python 3.4.

There are many potential applications, not limited to:
 * Webpage Scraping / Data Extraction
 * Testing and Validation
 * HTML Modification/Insertion
 * Debugging
 * HTML Document generation
 * Web Crawling
 * Formatting HTML documents or web pages

The AdvancedHTMLParser can read in a file (or string) of HTML, and will create a modifiable DOM tree from it. It can also be constructed manually from AdvancedHTMLParser.AdvancedTag objects.

The parser then exposes many "standard" functions as you'd find on the web for accessing the data:

    getElementsByTagName   - Returns a list of all elements matching a tag name

    getElementsByName      - Returns a list of all elements with a given name attribute

    getElementById         - Returns a single AdvancedTag (or None) if found an element matching the provided ID

    getElementsByClassName - Returns a list of all elements containing a class name

    getElementsByAttr       - Returns a list of all elements matching a paticular attribute/value pair.

    getElementsWithAttrValues - Returns a list of all elements with a specific attribute name containing one of a list of values

    getHTML                 - Returns string of HTML representing this DOM

    getFormattedHTML        - Returns a formatted string (using AdvancedHTMLFormatter; see below) of the HTML. Takes as argument an indent (defaults to two spaces)


The results of all of these getElement\* functions are TagCollection objects. These objects can be modified, and will be reflected in the parent DOM.

**TagCollection**

A TagCollection can be used like a list. It also exposes the various get\* functions which operate on the elements within the list (and their children).

**AdvancedTag**

the AdvancedTag represents a single tag and its inner text. It exposes many of the functions and properties you would expect to be present if using javascript.
each AdvancedTag also supports the same getElementsBy\* functions as the parser. It adds several additional that are not found in javascript, such as peers and arbitrary attribute searching.

some of these include:

    appendText              -  Append text to this element

    appendChild             -  Append a child to this element

    removeChild             -  Removes a child

    getChildren             - Returns the children as a list

    getStartTag             - Start Tag, with attributes

    getEndTag               - End Tag

    getPeersByName          - Gets "peers" (elements with same parent, at same level in tree) with a given name

    getPeersByAttr          - Gets peers by an arbitrary attribute/value combination

    getPeersWithAttrValues  - Gets peers by an arbitrary attribute/values combination. 

    getPeersByClassName   - Gets peers that contain a given class name

    getElement\*            - Same as above, but act on the children of this element.

    {get,set,has}Attribute  - get/set/test for an attribute

    {add,remove}Class       - Add/remove a class from the list of classes

    getUid                  - Get a unique ID for this tag (internal)

    __str__                 - str(tag) will show start tag with attributes, inner text, and end tag

    __getitem__             - Can be indexed like tag[2] to access second child.


And some properties:

    children/childNodes     - The children as a list

    innerHTML               - The innerHTML including the html of all children

    outerHTML               - innerHTML wrapped in this tag

    classNames/classList    - a list of the classes

    parentNode/parentElement - The parent tag

    tagName                - The tag name


IndexedAdvancedHTMLParser
-------------------------

IndexedAdvancedHTMLParser provides the ability to use indexing for faster search. If you are just parsing and not modifying, this is your best bet. If you are modifying the DOM tree, make sure you call IndexedAdvancedHTMLParser.reindex() before relying on them. Each of the get* functions above takes an additional "useIndex" function, which can also be set to False to skip index. See constructor for more information, and "Performance and Indexing" section below.

AdvancedHTMLFormatter and formatHTML
------------------------------------

The AdvancedHTMLFormatter formats HTML into a pretty layout. It can handle elements like pre, core, script, style, etc to keep their contents preserved, but does not understand CSS rules.

The methods are:

   parseStr               - Parse a string of contents
   parseFile              - Parse a filename or file object

   getHTML                - Get the formatted html


A script, formatHTML comes with this package and will perform formatting on an input file, and output to a file or stdout:

    Usage: formatHTML [/path/to/in.html] (optional: [/path/to/output.html])

      Formats HTML on input and writes to output file, or stdout if output file is omitted.



Notes
-----

* Each tag has a generated unique ID which is assigned at create time. The search functions use these to prevent duplicates in search results. There is a global function in the module, AdvancedHTMLParser.uniqueTags, which will filter a list of tags and remove any duplicates. TagCollections will only allow one instance of a tag (no duplicates)
* In general, for tag names and attribute names, you should use lowercase values. During parsing, the parser will lowercase attribute names (like NAME="Abc" becomes name="Abc"). During searching, however, for performance reasons, it is assumed you are passing in already-lowercased strings. If you can't trust the input to be lowercase, then it is your responsibility to call .lower() before calling .getElementsBy\*
* If you are using this to construct HTML and not search, I recommend either setting the index params to False in the constructor, or calling  AdvancedHTMLParser.disableIndexing()
* There are additional functions and usages not documented here, check the file for more information.

Performance and Indexing
------------------------

Performance is very good using this class. The performance can be further enhanced via several indexing tunables:

Firstly, in the constructor of IndexedAdvancedHTMLParser and in the reindex method is a boolean to be set which determines if each field is indexed (e.x. indexIDs will make getElementByID use an index).

If an index is used, parsing time slightly goes up, but searches become O(1) (from root node, slightly less efficent from other nodes) instead of O(n) [n=num elements].

By default, IDs, Names, Tag Names, Class Names are indexed.

You can add an index for any arbitrary field (used in getElementByAttr) via IndexedAdvancedHTMLParser.addIndexOnAttribute('src'), for example, to index the 'src' attribute. This index can be removed via removeIndexOnAttribute.

Example Usage
-------------

See `This Example <https://raw.githubusercontent.com/kata198/AdvancedHTMLParser/master/example.py>`_ for an example of parsing store data using this class.

Changes
-------
See: https://raw.githubusercontent.com/kata198/AdvancedHTMLParser/master/ChangeLog


Contact Me / Support
--------------------

I am available by email to provide support, answer questions, or otherwise  provide assistance in using this software. Use my email kata198 at gmail.com with "AdvancedArgumentParser" in the subject line.

"""

if __name__ == '__main__':

    setup(name='AdvancedHTMLParser',
            version='6.0.0',
            packages=['AdvancedHTMLParser'],
            scripts=['formatHTML'],
            author='Tim Savannah',
            author_email='kata198@gmail.com',
            maintainer='Tim Savannah',
            url='https://github.com/kata198/AdvancedHTMLParser',
            maintainer_email='kata198@gmail.com',
            description='A Powerful HTML Parser/Scraper/Validator that constructs a modifiable, searchable DOM tree, and includes many standard JS DOM functions (getElementsBy*, appendChild, etc) and additional methods',
            long_description=long_description,
            license='LGPLv3',
            keywords=['html', 'parser', 'tree', 'DOM', 'getElementsByName', 'getElementById', 'getElementsByClassName', 'simple', 'python', 'xml', 'HTMLParser', 'getElementsByTagName', 'getElementsByAttr', 'javascript', 'parse', 'scrape', 'test', 'SimpleHTMLParser', 'modify', 'JS', 'write'],
            classifiers=['Development Status :: 5 - Production/Stable',
                         'Programming Language :: Python',
                         'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
                         'Programming Language :: Python :: 2',
                          'Programming Language :: Python :: 2',
                          'Programming Language :: Python :: 2.6',
                          'Programming Language :: Python :: 2.7',
                          'Programming Language :: Python :: 3',
                          'Programming Language :: Python :: 3.3',
                          'Programming Language :: Python :: 3.4',
                          'Topic :: Internet :: WWW/HTTP',
                          'Topic :: Text Processing :: Markup :: HTML',
                          'Topic :: Software Development :: Libraries :: Python Modules',
            ]
    )



exampleProgram = """
import AdvancedHTMLParser

parser = AdvancedHTMLParser.AdvancedHTMLParser()

parser.parseStr('''
<html>
 <head>
  <title>HEllo</title>
 </head>
 <body>
   <div id="container1" class="abc">
     <div name="items">
      <span name="price">1.96</span>
     <span name="itemName">Sponges</span>
   </div>
   <div name="items">
     <span name="price">3.55</span>
     <span name="itemName">Turtles</span>
   </div>
   <div name="items">
     <span name="price" class="something" >6.55</span>
     <img src="/images/cheddar.png" style="width: 64px; height: 64px;" />
     <span name="itemName">Cheese</span>
   </div>
 </div>
 <div id="images">
   <img src="/abc.gif" name="image" />
   <img src="/abc2.gif" name="image" />
  </div>
  <div id="saleSection" style="background-color: blue">
    <div name="items">
      <span name="itemName">Pudding Cups</span>
      <span name="price">1.60</span>
    </div>
    <hr />
    <div name="items" class="limited-supplies" >
      <span name="itemName">Gold Brick</span>
      <span name="price">214.55</span>
      <b style="margin-left: 10px">LIMITED QUANTITIES: <span id="item_5123523_remain">130</span></b>
    </div>
  </body>
</html>
 ''')

print ( "Items less than $4.00: ")
print ( "-----------------------\n")
items = parser.getElementsByName('items')

parser2 = AdvancedHTMLParser.AdvancedHTMLParser()
parser2.parseStr('<div name="items"> <span name="itemName">Coop</span><span name="price">1.44</span></div>')

items[0].parentNode.appendChild(parser2.getRoot())
items = parser.getElementsByName('items')

for item in items:
    priceEm = item.getElementsByName('price')[0]

    priceValue = round(float(priceEm.innerHTML.strip()), 2)
    if priceValue < 4.00:
        name = priceEm.getPeersByName('itemName')[0].innerHTML.strip()

        print ( "%s - $%.2f" %(name, priceValue) )


# OUTPUT:
# Items less than $4.00: 
# -----------------------
# 
# Sponges - $1.96
# Turtles - $3.55
# Pudding Cups - $1.60

"""

#vim: set ts=4 sw=4 expandtab
