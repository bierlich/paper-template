#!/usr/bin/ python3

"""
Use the inspirehep JSON-based API to generate bibliographies.

Author: Christian Bierlich <christian.bierlich@thep.lu.se>
"""

import sys
import urllib.request, json
import os.path
import re
import ssl
import argparse

# Check what we already have in a local bibliography.
def readLocal(fName):
    if not os.path.isfile(fName):
        return []
    keys = []
    with open(fName,'r') as f:
        for line in f.readlines():
            if '@' in line:
                key = re.search('{(.*),',line)
                keys.append(key.group(1))
    return keys

# Read a .aux file and get all citation keys not in local.
def setupQuery(fName, local):
    keys = []
    if '.aux' not in fName:
        print('Please input a .aux latex file!')
        return []
    with open(fName,'r') as f:
        for line in f:
            if '\citation' in line:
                fkeys = re.search('\\\citation{(.*)}',line)
                fkeys = fkeys.group(1)
                for key in fkeys.split(','):
                    key = key.replace("\n","")
                    if key not in local and key not in keys:
                        keys.append(key)
    return keys
            
def insQuery(key, silent):
    # API address for searches.
    API = 'https://inspirehep.net/api/literature?sort=mostrecent&size=25&page=1&q='
    context = ssl._create_unverified_context()
    if not silent:
        print("Fetching: "+key)
    sstring = urllib.request.urlopen(API+key, context=context).read().decode('utf-8')
    data = json.loads(sstring)
    return urllib.request.urlopen(data['links']['bibtex'], context=context).read().decode('utf-8')

parser = argparse.ArgumentParser(description='Automatically fetch bibtex file from inspire')
parser.add_argument('--bibfile', dest='BIBFILE', 
        default='bibliography.bib',help='name of the bibliography file (default: bibliography.bib)')
parser.add_argument('--auxbib', dest='AUXBIB', 
        default='aux-bib.bib',help='name of an auxillary bibliography file which will not be touched, and items with same key will not be fected (default: aux-bib.bib)')
parser.add_argument('--auxfile', dest='AUXFILE', 
        default='paper.aux',help='name of the .aux file produced by pdflated (main tex-file).aux (default: paper.aux)')
parser.add_argument('--print', dest='PRINT', action='store_true', default=False,
        help='fetch full bibliography and print to screen instead of file (default: False)')
parser.add_argument('--silent', dest='SILENT', action='store_true', default=False,
        help='be silent (no status messages, default: False)')
parser.add_argument('--noempty', dest='NOEMPTY', action='store_true', default=False,
        help='exit with code 1 if bibliography is empty (for gitlab CI compatibility, default: False)')

args = parser.parse_args()

bibfile = args.BIBFILE
mabib = args.AUXBIB
auxfile = args.AUXFILE
silent = args.SILENT

local = []
if not args.PRINT:
    local = readLocal(bibfile) + readLocal(mabib)

queries = setupQuery(auxfile, local)

if len(queries) and not silent:
    print("Fetching bibliographical info from inspire. This can take some time.")
bibitems = [insQuery(q, silent) for q in queries]

emptyRef = False
with open(bibfile,'a') as f:
    for b in bibitems:
        if b == '':
            emptyRef = True
        if args.PRINT:
            print(b)
        else:
            f.write(b)

if emptyRef and args.NOEMPTY:
    sys.exit(1)
