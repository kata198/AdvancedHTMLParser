#!/usr/bin/env python
'''
    Copyright (c) 2015, 2016, 2017, 2018, 2019 Timothy Savannah under terms of LGPLv3. All Rights Reserved.


    You should have received a copy of this with this distribution as "LICENSE"
      If you did not, the current license can be found at: https://github.com/kata198/AdvancedHTMLParser/blob/master/LICENSE


  NOTE: - If you pass --no-deps, you can get a standalone install of AdvancedHTMLParser
   (aka no deps), but the .filter method will be unavailable
'''



import os
import sys
from setuptools import setup


if __name__ == '__main__':


    dirName = os.path.dirname(__file__)
    if dirName and os.getcwd() != dirName:
        os.chdir(dirName)

    if '--no-deps' in sys.argv:
        requires = []
        sys.argv.remove('--no-deps')
    else:
        requires = ['QueryableList']


    summary = 'A Powerful HTML Parser/Scraper/Validator/Formatter that constructs a modifiable, searchable DOM tree, and includes many standard JS DOM functions (getElementsBy*, appendChild, etc) and additional methods'

    try:
        with open('README.rst', 'rt') as f:
            long_description = f.read()
    except Exception as e:
        sys.stderr.write('Exception when reading long description: %s\n' %(str(e),))
        long_description = summary

    setup(name='AdvancedHTMLParser',
            version='8.1.5',
            packages=['AdvancedHTMLParser'],
            scripts=['formatHTML'],
            author='Tim Savannah',
            author_email='kata198@gmail.com',
            maintainer='Tim Savannah',
            requires=requires,
            install_requires=requires,
            url='https://github.com/kata198/AdvancedHTMLParser',
            maintainer_email='kata198@gmail.com',
            description=summary,
            long_description=long_description,
            license='LGPLv3',
            keywords=['html', 'parser', 'tree', 'DOM', 'getElementsByName', 'getElementById', 'getElementsByClassName', 'simple', 'python', 'xml', 'HTMLParser', 'getElementsByTagName', 'getElementsByAttr', 'javascript', 'parse', 'scrape', 'test', 'SimpleHTMLParser', 'modify', 'JS', 'write'],
            classifiers=['Development Status :: 5 - Production/Stable',
                         'Programming Language :: Python',
                         'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
                         'Programming Language :: Python :: 2',
                          'Programming Language :: Python :: 2',
                          'Programming Language :: Python :: 2.7',
                          'Programming Language :: Python :: 3',
                          'Programming Language :: Python :: 3.3',
                          'Programming Language :: Python :: 3.4',
                          'Programming Language :: Python :: 3.5',
                          'Programming Language :: Python :: 3.6',
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
# Coop - $1.44
# Pudding Cups - $1.60

"""

#vim: set ts=4 sw=4 expandtab
