
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


Full API
--------

Can be found  http://htmlpreview.github.io/?https://github.com/kata198/AdvancedHTMLParser/blob/master/doc/AdvancedHTMLParser.html .

Various examples  can be found in the "tests" directory, check github.

Short Doc
---------


The AdvancedHTMLParser can read in a file (or string) of HTML, and will create a modifiable DOM tree from it. It can also be constructed manually from AdvancedHTMLParser.AdvancedTag objects.

The parser then exposes many "standard" functions as you'd find on the web for accessing the data:

    getElementsByTagName   - Returns a list of all elements matching a tag name

    getElementsByName      - Returns a list of all elements with a given name attribute

    getElementById         - Returns a single AdvancedTag (or None) if found an element matching the provided ID

    getElementsByClassName - Returns a list of all elements containing a class name

    getElementsByAttr       - Returns a list of all elements matching a paticular attribute/value pair.

    getElementsWithAttrValues - Returns a list of all elements with a specific attribute name containing one of a list of values

    getElementsCustomFilter - Provide a function/lambda that takes a tag argument, and returns True to "match" it. Returns all matched objects

    getHTML                 - Returns string of HTML representing this DOM

    getRootNodes            - Get a list of nodes at root level (0)

    getFormattedHTML        - Returns a formatted string (using AdvancedHTMLFormatter; see below) of the HTML. Takes as argument an indent (defaults to two spaces)


The results of all of these getElement\* functions are TagCollection objects. These objects can be modified, and will be reflected in the parent DOM.


**Style Attribute**

Style attributes can be manipulated just like in javascript, so element.style.position = 'relative' for setting, or element.style.position for access. There are also helper methods, getStyle(name) and setStyle(name, value) which will set the  correct values.


**TagCollection**

A TagCollection can be used like a list. It also exposes the various get\* functions which operate on the elements within the list (and their children). To operate just on items in the list, you can use filterCollection which takes a lambda/function and returns True to retain that tag in the return.

**AdvancedTag**

the AdvancedTag represents a single tag and its inner text. It exposes many of the functions and properties you would expect to be present if using javascript.
each AdvancedTag also supports the same getElementsBy\* functions as the parser. It adds several additional that are not found in javascript, such as peers and arbitrary attribute searching.

some of these include:

    appendText              -  Append text to this element

    appendChild             -  Append a child to this element

    removeChild             -  Removes a child

    insertBefore            - Inserts a child before an existing child

    insertAfter             - Inserts a child after an existing child

    getChildren             - Returns the children as a list

    getStartTag             - Start Tag, with attributes

    getEndTag               - End Tag

    getPeersByName          - Gets "peers" (elements with same parent, at same level in tree) with a given name

    getPeersByAttr          - Gets peers by an arbitrary attribute/value combination

    getPeersWithAttrValues  - Gets peers by an arbitrary attribute/values combination. 

    getPeersByClassName   - Gets peers that contain a given class name

    getElement\*            - Same as above, but act on the children of this element.

    nextSibling            - Get next sibling, be it text  or  an element

    nextSiblingElement     - Get next sibling, that is an element

    previousSibling            - Get previous sibling, be it text  or  an element

    previousSiblingElement     - Get previous sibling, that is an element

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


Validation
----------
Validation can be performed by using ValidatingAdvancedHTMLParser. It will raise an exception if an assumption would have to be made to continue parsing (i.e. something important).

InvalidCloseException - Tried to close a tag that shouldn't have been closed

MissedCloseException  - Missed a non-optional close of a tag that would lead to causing an assumption during parsing.

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

    Usage: formatHTML (Optional: [/path/to/in.html]) (optional: [/path/to/output.html])

      Formats HTML on input and writes to output file, or stdout if output file is omitted.


    If output filename is not specified or is empty string, output will be to stdout.

    If input filename is not specified or is empty string, input will be from stdin



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

See https://raw.githubusercontent.com/kata198/AdvancedHTMLParser/master/example.py for an example of parsing store data using this class.

Changes
-------
See: https://raw.githubusercontent.com/kata198/AdvancedHTMLParser/master/ChangeLog


Contact Me / Support
--------------------

I am available by email to provide support, answer questions, or otherwise  provide assistance in using this software. Use my email kata198 at gmail.com with "AdvancedArgumentParser" in the subject line.

Unit Tests
----------

See "tests" directory available in github. Use "runTests.py" within that directory. Tests use my `GoodTests <https://github.com/kata198/GoodTests>`_ framework. It will download it to the current directory if not found in path, so you don't need to worry that it's a dependency.

