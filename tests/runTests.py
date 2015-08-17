#!/usr/bin/env python

# vim: set ts=4 sw=4 expandtab :
import os
import glob
import subprocess
import sys

GOODTESTS_URL = 'https://raw.githubusercontent.com/kata198/GoodTests/master/GoodTests.py'

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
        sys.stdout.write('GoodTests notfound. Would you like to install  it? (y/n): ')
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

    didDownload = False
    
    goodTestsInfo = findGoodTests()
    if goodTestsInfo['success'] is False:
        download_goodTests()
        goodTestsInfo =  findGoodTests()
        if goodTestsInfo['success'] is False:
            sys.stderr.write('Could not download or find GoodTests.py. Try  to download it yourself using "pip install GoodTests",  or wget %s\n' %( GOODTESTS_URL,))
            sys.exit(1)

    sys.stdout.write('Starting test..\n')
    sys.stdout.flush()
    sys.stderr.flush()
    pipe = subprocess.Popen(goodTestsInfo['path'] + ['AdvancedHTMLParserTests'], shell=False)
    pipe.wait()
