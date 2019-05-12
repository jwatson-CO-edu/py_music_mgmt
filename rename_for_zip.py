#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ~~ Future First ~~
from __future__ import division # Future imports must be called before everything else, including triple-quote docs!

__progname__ = "rename_for_zip.py"
__version__  = "2019.05" 
__desc__     = "Cannot zip files with weird names"
"""
James Watson , Template Version: 2019-05-12
Built on Wing 101 IDE for Python 2.7

Dependencies: numpy
"""


"""  
~~~ Developmnent Plan ~~~
[ ] ITEM1
[ ] ITEM2
"""

# === Init Environment =====================================================================================================================
# ~~~ Prepare Paths ~~~
import sys, os.path
SOURCEDIR = os.path.dirname( os.path.abspath( __file__ ) ) # URL, dir containing source file: http://stackoverflow.com/a/7783326
PARENTDIR = os.path.dirname( SOURCEDIR )
# ~~ Path Utilities ~~
def prepend_dir_to_path( pathName ): sys.path.insert( 0 , pathName ) # Might need this to fetch a lib in a parent directory

# ~~~ Imports ~~~
# ~~ Standard ~~
from math import pi , sqrt
import shutil
# ~~ Special ~~
import numpy as np
# ~~ Local ~~
from file_org_ops import safe_dir_name , makedirs_exist_ok

# ~~ Constants , Shortcuts , Aliases ~~
EPSILON = 1e-7
infty   = 1e309 # URL: http://stackoverflow.com/questions/1628026/python-infinity-any-caveats#comment31860436_1628026
endl    = os.linesep
sqt2    = sqrt(2)

# ~~ Script Signature ~~
def __prog_signature__(): return __progname__ + " , Version " + __version__ # Return a string representing program name and verions

# ___ End Init _____________________________________________________________________________________________________________________________


# === Main Program =========================================================================================================================


# === Program Vars ===

_OUTDIR = "output"
_INPDIR = "Dervish"

# ___ End Vars ___


# === Main Func ===

if __name__ == "__main__":
    print __prog_signature__()
    termArgs = sys.argv[1:] # Terminal arguments , if they exist
    
    # 0. Create the output dir , if it does not exist
    makedirs_exist_ok( _OUTDIR )
    
    # 1. For each file
    for root , dirs , files in os.walk( _INPDIR , topdown = False ):
        print "In dir" , root
        for name in files:
            # 2. Get the filename
            inpPath = os.path.join( root , name )
            print inpPath
            # 3. Get the fixed filename
            outName = safe_dir_name( name , defaultChar = '_' )
            outPath = os.path.join( _OUTDIR , outName )
            opStr   = str( inpPath ) + " --> " + str( outPath )
            try:
                shutil.move( inpPath , outPath )
                print "PASS:" , opStr
            except:
                print "FAIL:" , opStr
    
# ___ End Main ___

# ___ End Program __________________________________________________________________________________________________________________________


# === Spare Parts ==========================================================================================================================



# ___ End Spare ____________________________________________________________________________________________________________________________
