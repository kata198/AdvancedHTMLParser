
AdvancedHTMLParser
==================

AdvancedHTMLParser is an Advanced HTML Parser, with support for adding, removing, modifying, and formatting HTML. 

It aims to provide the same interface as you would find in a compliant browser through javascript ( i.e. all the getElement methods, appendChild, etc), as well as many more complex and sophisticated features not available through a browser. And most importantly, it's in python!


There are many potential applications, not limited to:

 * Webpage Scraping / Data Extraction

 * Testing and Validation

 * HTML Modification/Insertion

 * Outputting your website

 * Debugging

 * HTML Document generation

 * Web Crawling

 * Formatting HTML documents or web pages


It is especially good for servlets/webpages. It is quick to take an expertly crafted page in raw HTML / css, and have your servlet's ingest with AdvancedHTMLParser and create/insert data elements into the existing view using a simple and well-known interface ( javascript-like + HTML DOM ).

Another useful scenario is creating automated testing suites which can operate much more quickly and reliably (and at a deeper function-level), unlike in-browser testing suites.



Full API
--------

Can be found  http://htmlpreview.github.io/?https://github.com/kata198/AdvancedHTMLParser/blob/master/doc/AdvancedHTMLParser.html?vers=8.1.2 .


Examples
--------

Various examples can be found in the "tests" directory. A very old, simple example can also be found as "example.py" in the root directory.


Short Doc
---------


**AdvancedHTMLParser**

Think of this like "document" in a browser.


The AdvancedHTMLParser can read in a file (or string) of HTML, and will create a modifiable DOM tree from it. It can also be constructed manually from AdvancedHTMLParser.AdvancedTag objects.


To populate an AdvancedHTMLParser from existing HTML:

	parser = AdvancedHTMLParser.AdvancedHTMLParser()

	# Parse an HTML string into the document

	parser.parseStr(htmlStr)

	# Parse an HTML file into the document

	parser.parseFile(filename)



The parser then exposes many "standard" functions as you'd find on the web for accessing the data, and some others:

	getElementsByTagName   \- Returns a list of all elements matching a tag name

	getElementsByName      \- Returns a list of all elements with a given name attribute

	getElementById         \- Returns a single AdvancedTag (or None) if found an element matching the provided ID

	getElementsByClassName \- Returns a list of all elements containing a class name

	getElementsByAttr       \- Returns a list of all elements matching a paticular attribute/value pair.

	getElementsWithAttrValues \- Returns a list of all elements with a specific attribute name containing one of a list of values

	getElementsCustomFilter \- Provide a function/lambda that takes a tag argument, and returns True to "match" it. Returns all matched objects

	getRootNodes            \- Get a list of nodes at root level (0)

	getAllNodes             \- Get all the nodes contained within this document

	getHTML                 \- Returns string of HTML representing this DOM

	getFormattedHTML        \- Returns a formatted string (using AdvancedHTMLFormatter; see below) of the HTML. Takes as argument an indent (defaults to four spaces)

	getMiniHTML             \- Returns a "mini" HTML representation which disregards all whitespace and indentation beyond the functional single\-space


The results of all of these getElement\* functions are TagCollection objects. This is a special kind of list which contains additional functions. See the "TagCollection" section below for more info.

These objects can be modified, and will be reflected in the parent DOM.


The parser also contains some expected properties, like


	head                    \- The "head" tag associated with this document, or None

	body                    \- The "body" tag associated with this document, or None

	forms                   \- All "forms" on this document as a TagCollection


**General Attributes**

In general, attributes can be accessed with dot-syntax, i.e.

	tagEm.id = "Hello"

will set the "id" attribute. If it works in HTML javascript on a tag element, it should work on an AdvancedTag element with python.

setAttribute, getAttribute, and removeAttribute are more explicit and recommended ways of getting/setting/deleting attributes on elements.

The same names are used in python as in the javascript/DOM, such as 'className' corrosponding to a space-separated string of the 'class' attribute, 'classList' corrosponding to a list of classes, etc.


**Style Attribute**

Style attributes can be manipulated just like in javascript, so element.style.position = 'relative' for setting, or element.style.position for access.

You can also assign the tag.style as a string, like:

	myTag.style = "display: block; float: right; font\-weight: bold"

in addition to individual properties:

	myTag.style.display = 'block'

	myTag.style.float = 'right'

	myTag.style.fontWeight = 'bold'

You can remove style properties by setting its value to an empty string.

For example, to clear "display" property:

	myTag.style.display = ''

A standard method *setProperty* can also obe used to set or remove individual properties

For example:

	myTag.style.setProperty("display", "block") # Set display: block

	myTag.style.setProperty("display", '') # Clear display: property


The naming conventions are the same as in javascript, like "element.style.paddingTop" for "padding-top" attribute.


**TagCollection**

A TagCollection can be used like a list. Every element has a unique uuid associated with it, and a TagCollection will ensure that the same element does not appear twice within its list (so it acts like an ordered set)

It also exposes the various getElement\* functions which operate on the elements within the list (and their children).

For example:

	
	# Filter off the parser all tags with "item" in class

	tagCollection = document.getElementsByClassName('item')

	# Return all nodes which are nested within any class="item" object

	#  and also contains the class name "onsale"

	itemsWithOnSaleClass = tagCollection.getElementsByClassName('onsale')


To operate just on items in the list, you can use the TagCollection method, *filterCollection*, which takes a lambda/function and returns True to retain that tag in the return.

For example:

	# Filter off the parser all tags with "item" in class

	tagCollection = document.getElementsByClassName('item')

	# Provide a lambda to filter this collection, returning in tagCollection2

	#   those items which have a "value" attribute > 20 and contains at least

	#   1 child element with "specialPrice" class

	tagCollection2 = tagCollection.filterCollection( lambda node : int(node.getAttribute('value') or 0) > 20 and len(node.getElementsByClassName('specialPrice')) > 1 )


TagCollections also support advanced filtering (find/filter methods), see "Advanced Filtering" section below.


**AdvancedTag**

The AdvancedTag represents a single tag and its inner text. It exposes many of the functions and properties you would expect to be present if using javascript.

each AdvancedTag also supports the same getElementsBy\* functions as the parser.

It adds several additional that are not found in javascript, such as peers and arbitrary attribute searching.

some of these include:

	appendText              \- Append text to this element

	appendChild             \- Append a child to this element

	appendBlock             \- Append a block (text or AdvancedTag) to this element

	append                  \- alias of appendBlock

	removeChild             \- Removes a child

	removeText              \- Removes first occurance of some text from any text nodes

	removeTextAll           \- Removes ALL occurances of some text from any text nodes

	insertBefore            \- Inserts a child before an existing child

	insertAfter             \- Inserts a child after an existing child

	getChildren             \- Returns the children as a list

	getStartTag             \- Start Tag, with attributes

	getEndTag               \- End Tag

	getPeersByName          \- Gets "peers" (elements with same parent, at same level in tree) with a given name

	getPeersByAttr          \- Gets peers by an arbitrary attribute/value combination

	getPeersWithAttrValues  \- Gets peers by an arbitrary attribute/values combination. 

	getPeersByClassName   \- Gets peers that contain a given class name

	getElement\\\*            \- Same as above, but act on the children of this element.

	getParentElementCustomFilter \- Takes a lambda/function and applies on all parents of this element upward until the document root. Returns the first node that when passed to this function returns True, or None if no matches on any parent nodes

	getHTML / toHTML / asHTML \- Get the HTML representation using this node as a root (so start tag and attributes, innerHTML (text and child nodes), and end tag)

	firstChild             \- Get the first child of this node, be it text or an element (AdvancedTag)

	firstElementChild      \- Get the first child of this node that is an element

	lastChild             \- Get the last child of this node, be it text or an element (AdvancedTag)

	lastElementChild      \- Get the last child of this node that is an element

	nextSibling            \- Get next sibling, be it text  or  an element

	nextElementSibling     \- Get next sibling, that is an element

	previousSibling            \- Get previous sibling, be it text  or  an element

	previousElementSibling     \- Get previous sibling, that is an element

	{get,set,has,remove}Attribute  \- get/set/test/remove an attribute

	{add,remove}Class       \- Add/remove a class from the list of classes

	setStyle                \- Set a specific style property [like: setStyle("font\-weight", "bold") ]

	isTagEqual              \- Compare if two tags have the same attributes. Using the == operator will compare if they are the same exact tag (by uuid)

	getUid                  \- Get a unique ID for this tag (internal)

	getAllChildNodes        \- Gets all nodes beneath this node in the document (its children, its children's children, etc)

	getAllNodes             \- Same as getAllChildNodes, but also includes this node

	contains                \- Check if a provided node appears anywhere beneath this node (as child, child\-of\-child, etc)

	remove                  \- Remove this node from its parent element, and disassociates this and all sub\-nodes from the associated document

	\_\_str\_\_                 \- str(tag) will show start tag with attributes, inner text, and end tag

	\_\_repr\_\_                \- Shows a reconstructable representation of this tag

	\_\_getitem\_\_             \- Can be indexed like tag[2] to access second child.


And some properties:

	children/childNodes     \- The children (tags) as a list NOTE: This returns only AdvancedTag objects, not text.

	childBlocks             \- All direct child blocks. This includes both AdvnacedTag objects and text nodes (str)

	innerHTML               \- The innerHTML including the html of all children

	innerText               \- The text nodes, in order, as they appear as direct children to this node as a string

	textContent             \- All the text nodes, in order, as they appear within this node or any children (or their children, etc.)

	outerHTML               \- innerHTML wrapped in this tag

	classNames/classList    \- a list of the classes

	parentNode/parentElement \- The parent tag

	tagName                \- The tag name

	ownerDocument          \- The document associated with this node, if any


And many others. See the pydocs for a full list, and associated docstrings.


**Appending raw HTML**

You can append raw HTML to a tag by calling:

	tagEm.appendInnerHTML('<div id="Some sample HTML"> <span> Yes </span> </div>')

which acts like, in javascript:

	tagEm.innerHTML += '<div id="Some sample HTML"> <span> Yes </span> </div>';


**Creating Tags from HTML**

Tags can be created from HTML strings outside of AdvancedHTMLParser.parseStr (which parses an entire document) by:

* Parser.AdvancedHTMLParser.createElement - Like document.createElement, creates a tag with a given tag name. Not associated with any document.

* Parser.AdvancedHTMLParser.createElementFromHTML - Creates a single tag from HTML.

* Parser.AdvancedHTMLParser.createElementsFromHTML - Creates and returns a list of one or more tags from HTML.

* Parser.AdvancedHTMLParser.createBlocksFromHTML - Creates and returns a list of blocks. These can be AdvancedTag objects (A tag), or a str object (if raw text outside of tags). This is recommended for parsing arbitrary HTML outside of parsing the entire document. The createElement{,s}FromHTML functions will discard any text outside of the tags passed in.



Advanced Filtering
------------------

AdvancedHTMLParser contains two kinds of "Advanced Filtering":

**find**

The most basic unified-search, AdvancedHTMLParser has a "find" method on it. This will search all nodes with a single, simple query.

This is not as robust as the "filter" method (which can also be used on any tag or TagCollection), but does not require any dependency packages.

	find \- Perform a search of elements using attributes as keys and potential values as values

	   (i.e.  parser.find(name='blah', tagname='span')  will return all elements in this document

		 with the name "blah" of the tag type "span" )

	Arguments are key = value, or key can equal a tuple/list of values to match ANY of those values.

	Append a key with \_\_contains to test if some strs (or several possible strs) are within an element

	Append a key with \_\_icontains to perform the same \_\_contains op, but ignoring case

	Special keys:

	   tagname    \- The tag name of the element

	   text       \- The text within an element

	NOTE: Empty string means both "not set" and "no value" in this implementation.


Example:

	cheddarElements = parser.find(name='items', text\_\_icontains='cheddar')


**filter**

If you have QueryableList installed (a default dependency since 7.0.0 to AdvancedHTMLParser, but can be skipped with '\-\-no\-deps' passed to setup.py)

then you can take advantage of the advanced "filter" methods, on either the parser (entire document), any tag (that tag and nodes beneath), or tag collection (any of those tags, or any tags beneath them).

A full explanation of the various filter modes that QueryableList supports can be found at https://github.com/kata198/QueryableList

Special keys are: "tagname" for the tag name, and "text" for the inner text of a node.

An attribute that is unset has a value of None, which is different than a set attribute with an empty value ''.


For example:

	cheddarElements = parser.filter(name='items', text\_\_icontains='cheddar')


The AdvancedHTMLParser has:

	filter / filterAnd      \- Perform a filter query on all nodes in this document, returning a TagCollection of elements matching ALL criteria

	filterOr                \- Perform a filter query on all nodes in this document, returning a TagCollection of elements matching ANY criteria


Every AdvancedTag has:

	filter / filterAnd      \- Perform a filter query on this nodes and all sub\-nodes, returning a TagCollection of elements matching ALL criteria

	filterOr                \- Perform a filter query on this nodes and all sub\-nodes, returning a TagCollection of elements matching ANY criteria


Every TagCollection has:


	filter / filterAnd      \- Perform a filter query on JUST the nodes contained within this list (no children), returning a TagCollection of elements matching ALL criteria

	filterOr                \- Perform a filter query on JUST the nodes contained within this list (no children), returning a TagCollection of elements matching ANY criteria

	filterAll / filterAllAnd \- Perform a filter query on the nodes contained within this list, and all of their sub\-nodes, returning a TagCollection of elements matching ALL criteria

	filterAllOr              \- Perform a filter query on the nodes contained within this list, and all of their sub\-nodes, returning a TagCollection of elements matching ANY criteria



Validation
----------
Validation can be performed by using ValidatingAdvancedHTMLParser. It will raise an exception if an assumption would have to be made to continue parsing (i.e. something important).

InvalidCloseException - Tried to close a tag that shouldn't have been closed

MissedCloseException  - Missed a non-optional close of a tag that would lead to causing an assumption during parsing.

InvalidAttributeNameException - An attribute name was found that contained an invalid character, or broke a naming rule.


IndexedAdvancedHTMLParser
=========================

IndexedAdvancedHTMLParser provides the ability to use indexing for faster search. If you are just parsing and not modifying, this is your best bet. If you are modifying the DOM tree, make sure you call IndexedAdvancedHTMLParser.reindex() before relying on them. 

Each of the get\* functions above takes an additional "useIndex" function, which can also be set to False to skip index. See constructor for more information, and "Performance and Indexing" section below.

AdvancedHTMLFormatter and formatHTML
------------------------------------

**AdvancedHTMLFormatter**

The AdvancedHTMLFormatter formats HTML into a pretty layout. It can handle elements like pre, core, script, style, etc to keep their contents preserved, but does not understand CSS rules.

The methods are:

	parseStr               \- Parse a string of contents

	parseFile              \- Parse a filename or file object

	getHTML                \- Get the formatted html

	getRootNodes           \- Get a list of the "root" nodes (most outer nodes, should be <html> on a valid document)

	getRoot                \- Gets the "root" node (on a valid document this should be <html>). For arbitrary HTML, you should use getRootNodes, as there may be several nodes at the same outermost level


You can access this same formatting off an AdvancedHTMLParser.AdvancedHTMLParser (or IndexedAdvancedHTMLParser) by calling .getFormattedHTML()


**AdvancedHTMLMiniFormatter**

The AdvancedHTMLMiniFormatter will strip all non-functional whitespace (meaning any whitespace which wouldn't normally add a space to the document or is required for xhtml) and provide no indentation.

Use this when pretty-printing doesn't matter and you'd like to save space.


You can access this same formatting off an AdvancedHTMLParser.AdvancedHTMLParser (or IndexedAdvancedHTMLParser) by calling .getMiniHTML()


**AdvancedHTMLSlimTagFormatter and AdvancedHTMLSlimTagMiniFormatter**

In order to support some less-leniant parsers, AdvancedHTMLParser will by default include a space prior to the close-tag '>' character in HTML output.

For example:

	<span id="abc" >Blah</span>

	<br />

	<hr class="bigline" />


It is recommended to keep these extra spaces, but if for some reason you feel you need to get rid of them, you can use either *AdvancedHTMLSlimTagFormatter* or *AdvancedHTMLSlimTagMiniFormatter*.


*AdvancedHTMLSlimTagFormatter* will do pretty-printing (like getFormattedHTML / AdvancedHTMLFormatter.getHTML output)

*AdvancedHTMLSlimTagMiniFormatter* will do mini-printing (like getMiniHTML / AdvancedHTMLMiniFormatter.getHTML output)


Feeding in your HTML via formatter.parseStr(htmlStr) [where htmlStr can be parser.getHTML()] will cause it to be output without the start-tag padding.

For example:

	<span id="abc">Blah</span>

By default, self-closing tags will retain their padding so that an xhtml-compliant parser doesn't treat "/" as either an attribute or part of the attribute-value of the preceding attribute.

For example:

	<hr class="bigline"/>

Could be interpreted as a horizontal rule with a class name of "bigline/". Most modern browsers work around this and will not have issue, but some parsers will.

You may pass an optional keyword-argument to the formatter constructor, slimSelfClosing=True, in order to force removal of this padding from self-closing tags.

For example:

	myHtml = '<hr class="bigline" />'

	formatter = AdvancedHTMLSlimTagMiniFormatter(slimSelfClosing=True)

	formatter.parseStr(myHtml)

	miniHtml = formatter.getHTML()

	# miniHtml will now contain '<hr class="bigline"/>'

.

**formatHTML script**


A script, formatHTML comes with this package and will perform formatting on an input file, and output to a file or stdout:

	Usage: formatHTML (Optional Arguments) (optional: /path/to/in.html) (optional: [/path/to/output.html])

	  Formats HTML on input and writes to output.

	 Optional Arguments:

	 \-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-

		\-e [encoding]        \- Specify an encoding to use. Default is utf\-8

		\-m  or \-\-mini        \- Output "mini" HTML (only retain functional whitespace,

								strip the rest and no indentation)

		\-p  or \-\-pretty      \- Output "pretty" HTML [This is the defualt mode]


		\-\-indent='    '      \- Use the provided string [default 4\-spaces] to represent each

								level of nesting. Use \-\-indent="	" for 1 tab insead, for example.

							   Affects pretty printing mode only


	 If output filename is not specified or is empty string, output will be to stdout.

	 If input filename is not specified or is empty string, input will be from stdin

	 If \-e is provided, will use that as the encoding. Defaults to utf\-8


Notes
-----

* Each tag has a generated unique ID which is assigned at create time. The search functions use these to prevent duplicates in search results. There is a global function in the module, AdvancedHTMLParser.uniqueTags, which will filter a list of tags and remove any duplicates. TagCollections will only allow one instance of a tag (no duplicates)

* In general, for tag names and attribute names, you should use lowercase values. During parsing, the parser will lowercase attribute names (like NAME="Abc" becomes name="Abc"). During searching, however, for performance reasons, it is assumed you are passing in already-lowercased strings. If you can't trust the input to be lowercase, then it is your responsibility to call .lower() before calling .getElementsBy\*

* If you are using IndexedAdvancedHTMLParser (instead of AdvancedHTMLParser) to construct HTML and not search, I recommend either setting the index params to False in the constructor, or calling  IndexedAdvancedHTMLParser.disableIndexing(). When you are finished and want to go back to searching, you can call IndexedAdvancedHTMLParser.reindex and set to True what you want to reindex.

* There are additional functions and usages not documented here, check the file for more information.

Performance and Indexing
------------------------

Performance is very good using either AdvancedHTMLParser, and even better (for scraping) using IndexedAdvancedHTMLParser class. The performance can be further enhanced on IndexedAdvancedHTMLParser via several indexing tunables:

First, in the constructor of IndexedAdvancedHTMLParser and in the reindex method is a boolean to be set which determines if each field is indexed (e.x. indexIDs will make getElementByID use an index).

If an index is used, parsing time slightly goes up, but searches become O(1) (from root node, slightly less efficent from other nodes) instead of O(n) [n=num elements].

By default, IDs, Names, Tag Names, Class Names are indexed.

You can add an index for any arbitrary field (used in getElementByAttr) via IndexedAdvancedHTMLParser.addIndexOnAttribute('src'), for example, to index the 'src' attribute. This index can be removed via removeIndexOnAttribute.


Dependencies
------------

AdvancedHTMLParser can be installed without dependencies (pass '\-\-no\-deps' to setup.py), and everything will function EXCEPT filter\* methods.

By default, https://github.com/kata198/QueryableList will be installed, which will enable support for those additional filter methods.


Unicode
-------

AdvancedHTMLParser generally has very good support for unicode, and defaults to "utf\-8" (can be altered by the "encoding" argument to the AdvancedHTMLParser.AdvancedHTMLParser when parsing.)

If you are still getting UnicodeDecodeError or UnicodeEncodeError, there are a few things you can try:

* If the error happens when printing/writing to stdout ( default behaviour for apache / mod\_python is to open stdout with the ANSI/ASCII encoding ), ensure your streams are, in fact, set to utf\-8.

	\* Set the environment variable PYTHONIOENCODING to "utf\\\-8" before python is launched. In Apache, you can add the line "SetEnv PYTHONIOENCODING utf\\\-8" to your httpd.conf in order to achieve this.

* Ensure that the data you are passing to AdvancedHTMLParser has the correct encoding (matching the "encoding" parameter).

* Switch to python3 if at all possible \-\- python2 does have 'unicode' support and AdvancedHTMLParser uses it to the best of its ability, but python2 does still have some inherit flaws which may come up using standard library / output functions. You should ensure that these are set to use utf\-8 (as described above).


AdvancedHTMLParser is tested against unicode ( even has a unit test ) which works in both python2 and python3 in the general case.

If you are having an issue (even on python2) and you've checked the above "common configuration/usage" errors and think there is still an issue, please open a bug report on https://github.com/kata198/AdvancedHTMLParser with a test case, python version, and traceback.


The library itself is considered unicode-safe, and almost always it's an issue outside of this library, or has a simple workaround.


Example Usage
-------------

See https://raw.githubusercontent.com/kata198/AdvancedHTMLParser/master/example.py for an example of parsing store data using this class.

Changes
-------
See: https://raw.githubusercontent.com/kata198/AdvancedHTMLParser/master/ChangeLog


Contact Me / Support
--------------------

I am available by email to provide support, answer questions, or otherwise  provide assistance in using this software. Use my email kata198 at gmail.com with "AdvancedHTMLParser" in the subject line.


If you are having an issue / found a bug / want to merge in some changes, please open a pull request.


Unit Tests
----------

See "tests" directory available in github. Use "runTests.py" within that directory. Tests use my `GoodTests <https://github.com/kata198/GoodTests>`_ framework. It will download it to the current directory if not found in path, so you don't need to worry that it's a dependency.


