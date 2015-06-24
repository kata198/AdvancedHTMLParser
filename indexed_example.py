import AdvancedHTMLParser

parser = AdvancedHTMLParser.IndexedAdvancedHTMLParser()

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
parser.reindex()
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


