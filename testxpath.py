#!/usr/bin/python3
'''
    testxpath.py - Test the xpath engine

        Has an HTML_STR you can change to provide your own HTML.

        Takes an xpath expression as commandline argument, or, if omitted, will prompt for one.

        Runs the expression against HTML_STR, and prints the results (and optionally debug info).

          Then, drops you to a pdb shell to explore the results.
'''

from AdvancedHTMLParser import xpath as axpath
from AdvancedHTMLParser.xpath._debug import setXPathDebug, getXPathDebug

import AdvancedHTMLParser

import sys
import time

# UNCOMMENT THIS LINE TO ENABLE DEBUGGING, or pass --debug
setXPathDebug(True)

DEBUG = getXPathDebug()

global DO_PDB
DO_PDB = False
DO_PDB = True

HTML_STR = '''<html>
  <head>
    <title>Hello World!</title>
  </head>
  <body class="bodyclass smalltext" >
    <div id="mainOuterDiv" >

      <table>
        <thead>
          <tr class="head_first_row" >
            <th>Name</th>
            <th>Price</th>
            <th>Image</th>
          </tr>
        </thead>
        <tbody>
          <tr class="first_row" name="itemRow" >
            <td>Soap</td>
            <td class="price" cost="1.88" >$1.88</td>
            <td> <img src="soap.png" /> </td>
          </tr>

          <tr class="second_row" name="itemRow" >
            <td>Turkey Sandwich</td>
            <td class="price special-price" cost="2.35" >$2.35</td>
            <td> <img src="turkey_sandwich.png" /> </td>
          </tr>
          <tr class="third_row" name="itemRow" >
            <td>Banana</td>
            <td class="price" cost="0.98" >$0.98</td>
            <td> <img src="banana.png" /> </td>
          </tr>
        </tbody>
      </table>

      <div class="whitespace" >&nbsp;</div>

      <div class="cheese" >
        <span id="cheddar" >Cheddar</span>
        <br />
        <span id="mozerella" >Mozerella</span>
        <br />
      </div>
    </div>
  </body>
</html>
'''


if __name__ == '__main__':

    ##                                  ##
    ###  Commandline Argument Parsing  ###
    #                                    #
    cmdlineArgs = sys.argv[1:]

    for pdbOnArg in ('-p', '--pdb', '--do-pdb', '--pdb-on'):
        if pdbOnArg in cmdlineArgs:
            DO_PDB = True
            cmdlineArgs.remove(pdbOnArg)

    for noPdbOnArg in ('-np', '--no-pdb', '--pdb-off'):
        if noPdbOnArg in cmdlineArgs:
            DO_PDB = False
            cmdlineArgs.remove(noPdbOnArg)


    for debugArg in ('-d', '--debug'):
        if debugArg in cmdlineArgs:
            setXPathDebug(True)
            DEBUG = getXPathDebug()
            cmdlineArgs.remove(debugArg)

    for noDebugArg in ('-nd', '--no-debug'):
        if noDebugArg in cmdlineArgs:
            setXPathDebug(False)
            DEBUG = getXPathDebug()
            cmdlineArgs.remove(noDebugArg)


    try:
        xpathStr = cmdlineArgs[0]
    except:
        sys.stdout.write("\nEnter xpath str: ")
        sys.stdout.flush()

        xpathStr = sys.stdin.readline()[:-1]

        if xpathStr in ('quit', 'exit'):
            sys.stderr.write('\nQuitting...\n\n')
            sys.stderr.flush()
            sys.exit(0)

    document = AdvancedHTMLParser.AdvancedHTMLParser()
    document.parseStr(HTML_STR)

    startTime = time.time()

    if DEBUG is True:
        # XXX: In debug mode, run the parts explicitly
        x = axpath.XPathExpression(xpathStr)
        print ( "\nCreated XPath Operations: %s\n" %(repr(x.orderedOperations), ))
        res = x.evaluate( document.getElementsByTagName('html')[0] )

    else:
        # XXX: Outside debug mode, just go straight to public interface on parser
        res = document.getElementsByXPathExpression(xpathStr)

    endTime = time.time()

    print ( "\nTook %.8f seconds.\n\nGot return: %s\n" %(endTime - startTime, repr(res), ))
    if DO_PDB is True:
        print ( "\n--------------------\nENTERING PDB\n  Results are in 'res' variable.\n\n" )
        import pdb; pdb.set_trace()
    pass
    pass
    pass
