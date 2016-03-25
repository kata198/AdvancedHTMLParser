#!/usr/bin/env python
#
#  Copyright (c) 2015 Tim Savannah under following terms:
#   You may modify and redistribe this script with your project
#
# It will download the latest GoodTests.py and use it to execute the tests.
#
#  This should be placed in a directory, "tests", at the root of your project. It assumes that ../$MY_PACKAGE_MODULE is the path to your test module, and will create a symlink to it in order to run tests.
#  The tests should be found in $MY_TEST_DIRECTORY in given "tests" folder.

import os

import glob
import subprocess
import sys

GOODTESTS_URL = 'https://raw.githubusercontent.com/kata198/GoodTests/master/GoodTests.py'

# This should be your module name, assumed to be in "../$MY_PACKAGE_MODULE". A symlink will be created in order to test that without messing with the global copy.
#  If you set this to False, then a symlink will not be created and it will attempt to use the module as found in PYTHONPATH, or abort if it cannot be found.
MY_PACKAGE_MODULE = 'AdvancedHTMLParser'
# MY_PACKAGE_MODULE = False

# This is the test directory that should contain all your tests. This should be a directory in your "tests" folder
# TODO: modify this to  support a relative apth anywhere
MY_TEST_DIRECTORY = 'AdvancedHTMLParserTests'

def findGoodTests():
    pathSplit  = os.environ['PATH'].split(':')
    if '.' not in os.environ['PATH'].split(':'):
        pathSplit = ['.'] + pathSplit
        os.environ['PATH'] = ':'.join(pathSplit)
    with open('/dev/null', 'w') as devnull:
        pipe =  subprocess.Popen("which GoodTests.py", shell=True, stdout=subprocess.PIPE, stderr=devnull, env=os.environ)
        result = pipe.stdout.read().split()
    ret = pipe.wait()
    success = bool(ret == 0)
    return {
        'path'  :  result,
        "success" : success 
    }

def download_goodTests():
    validAnswer = False
    while validAnswer == False:
        sys.stdout.write('GoodTests notfound. Would you like to install it to local folder? (y/n): ')
        sys.stdout.flush()
        answer = sys.stdin.readline().strip().lower()
        if answer not in ('y', 'n', 'yes', 'no'):
            continue
        validAnswer =  True
        answer =  answer[0]

    if answer == 'n':
        sys.stderr.write('Cannot run tests without  installing GoodTests. http://pypi.python.org/pypi/GoodTests or https://github.com/kata198/Goodtests\n')
        sys.exit(1)
    try:
        import urllib2 as urllib
    except ImportError:
        try:
            import urllib.request as urllib
        except:
            sys.stderr.write('Failed to import urllib. Trying pip.\n')
            import  subprocess
            pipe  = subprocess.Popen('pip install GoodTests',  shell=True)
            res = pipe.wait()
            if res != 0:
                sys.stderr.write('Failed to  install GoodTests with pip or  direct download. aborting.\n')
                sys.exit(1)
    try:
        response = urllib.urlopen(GOODTESTS_URL)
        contents = response.read()
        if str !=  bytes:
            contents = contents.decode('ascii')
    except Exception as e:
        sys.stderr.write('Failed  to download  GoodTests.py from "%s"\n%s\n' %(GOODTESTS_URL, str(e)))
        sys.exit(1)
    try:
        with open('GoodTests.py', 'w') as f:
            f.write(contents)
    except Exception as e:
        sys.stderr.write('Failed to write to GoodTests.py\n%s\n' %(str(e,)))
        sys.exit(1)
    try:
        os.chmod('GoodTests.py', 0o775)
    except:
        sys.stderr.write('WARNING: Failed to chmod +x GoodTests.py, may not be able to be executed.\n')

    try:
        import GoodTests
    except ImportError:
        sys.stderr.write('Seemed to download GoodTests okay, but still cannot  import. Aborting.\n')
        sys.exit(1)
    

if __name__ == '__main__':

    thisDir = os.path.dirname(__file__)
    if not thisDir:
        thisDir = os.getcwd()
    elif not thisDir.startswith('/'):
        thisDir = os.getcwd() + '/' + thisDir

    os.chdir(thisDir)

    didDownload = False
    
    goodTestsInfo = findGoodTests()
    if goodTestsInfo['success'] is False:
        download_goodTests()
        goodTestsInfo =  findGoodTests()
        if goodTestsInfo['success'] is False:
            sys.stderr.write('Could not download or find GoodTests.py. Try  to download it yourself using "pip install GoodTests",  or wget %s\n' %( GOODTESTS_URL,))
            sys.exit(1)

    if MY_PACKAGE_MODULE and not os.path.exists(MY_PACKAGE_MODULE):
        if not os.path.exists('../' + MY_PACKAGE_MODULE):
            sys.stderr.write('Expected to find ../%s given MY_PACKAGE_MODULE, but not present. Have you unpacked all the source?\n' %(MY_PACKAGE_MODULE,))
            sys.exit(1)

        try:
            os.symlink('../'  + MY_PACKAGE_MODULE, MY_PACKAGE_MODULE)
        except Exception as e:
            sys.stderr.write('Unable to create a symlink to ../%s: %s\n' %(MY_PACKAGE_MODULE, str(e)))
            sys.exit(1)

    try:
        __import__(MY_PACKAGE_MODULE)
    except ImportError:
        sys.stderr.write('Could not import %s. Either install it or otherwise add to PYTHONPATH\n' %(MY_PACKAGE_MODULE,))
        sys.exit(1)

    sys.stdout.write('Starting test..\n')
    sys.stdout.flush()
    sys.stderr.flush()
    pipe = subprocess.Popen(goodTestsInfo['path'] + [MY_TEST_DIRECTORY], shell=False)
    pipe.wait()
