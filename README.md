
AdvancedHTMLParser
==================

AdvancedHTMLParser is an Advanced HTML Parser and writer written in python, and compatible and tested in Python 2.7 and Python 3.4.

There are many potential applications, not limited to:
 * Webpage Scraping / Data Extraction
 * Testing and Validation
 * HTML Modification/Insertion
 * Debugging
 * HTML Document generation
 * Web Crawling

The AdvancedHTMLParser can read in a file (or string) of HTML, and will create a modifiable DOM tree from it. It can also be constructed manually from AdvancedHTMLParser.AdvancedTag objects.

The parser then exposes many "standard" functions as you'd find on the web for accessing the data:

    getElementsByTagName   - Returns a list of all elements matching a tag name
    getElementsByName      - Returns a list of all elements with a given name attribute
    getElementById         - Returns a single AdvancedTag (or None) if found an element matching the provided ID
    getElementsByClassName - Returns a list of all elements containing a class name
    getElementsByAttr       - Returns a list of all elements matching a paticular attribute/value pair.
    getElementsWithAttrValues - Returns a list of all elements with a specific attribute name containing one of a list of values
    getHTML                 - Returns string of HTML representing this DOM

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


Notes
-----

* Each tag has a generated unique ID which is assigned at create time. The search functions use these to prevent duplicates in search results. There is a global function in the module, AdvancedHTMLParser.uniqueTags, which will filter a list of tags and remove any duplicates. TagCollections will only allow one instance of a tag (no duplicates)
* In general, for tag names and attribute names, you should use lowercase values. During parsing, the parser will lowercase attribute names (like NAME="Abc" becomes name="Abc"). During searching, however, for performance reasons, it is assumed you are passing in already-lowercased strings. If you can't trust the input to be lowercase, then it is your responsibility to call .lower() before calling .getElementsBy\*
* There are additional functions and usages not documented here, check the file for more information.

Performance and Indexing
------------------------

Performance is very good using this class. The performance can be further enhanced via several indexing tunables:

Firstly, in the constructor of AdvancedHTMLParser and in the reindex method is a boolean to be set which determines if each field is indexed (e.x. indexIDs will make getElementByID use an index).

If an index is used, parsing time slightly goes up, but searches become O(1) instead of O(n) [n=num elements].

By default, IDs and Names are indexed. Class names, tag names, and others are not indexed.

You can add an index for any arbitrary field (used in getElementByAttr) via AdvancedHTMLParser.addIndexForAttribute('src'), for example, to index the 'src' attribute. This index can be removed via removeIndexForAttribute.

The indexing behaviour can further be controlled via a property available in constructor and a setter, onlyCheckIndexOnIndexedFields. This is True by default, and should always be True for a read-only tree. You can also keep it True reliably, so long as you call reindex() after modifications. Set this to False if you are doing lots of reads and write concurrently.

When True, only the index (for fields with enabled index) will be used. If not in the index, not returned.
When False, if at least one element is found in the index, it will be returned. If nothing is present in the index, it will fallback to a full tree search.

Example Usage
-------------

The following example shows scraping a webpage to extract data tht meet certain criteria:

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
    print ( "----------------------\n-")
    items = parser.getElementsByName('items')
    for item in items:
        priceEm = item.getElementsByName('price')[0]
    
        priceValue = round(float(priceEm.innerHTML.strip()), 2)
        if priceValue < 4.00:
            name = priceEm.getPeersByName('itemName')[0].innerHTML.strip()
    
            print ( "%s - $%.2f" %(name, priceValue) )

**Output**

Items less than $4.00:
-----------------------

Sponges - $1.96
Turtles - $3.55
Pudding Cups - $1.60


Contact Me / Support
--------------------

I am available by email to provide support, answer questions, or otherwise  provide assistance in using this software. Use my email kata198 at gmail.com with "AdvancedArgumentParser" in the subject line.

