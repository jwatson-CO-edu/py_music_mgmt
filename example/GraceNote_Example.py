#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ~~ Future First ~~
from __future__ import division # Future imports must be called before everything else, including triple-quote docs!

__progname__ = "GraceNote_Example.py"
__version__  = "2018.11"
__desc__     = "Search the GraceNote database by artist and track"
"""
James Watson , Template Version: 2018-05-14
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
# ~~ Special ~~
import numpy as np
# ~~ Local ~~
prepend_dir_to_path( os.path.join( PARENTDIR , "marchhare" ) )
from pygn.pygn import register , search
from marchhare import parse_lines

# ~~ Constants , Shortcuts , Aliases ~~
EPSILON = 1e-7
infty   = 1e309 # URL: http://stackoverflow.com/questions/1628026/python-infinity-any-caveats#comment31860436_1628026
endl    = os.linesep

# ~~ Script Signature ~~
def __prog_signature__(): return __progname__ + " , Version " + __version__ # Return a string representing program name and verions

# ___ End Init _____________________________________________________________________________________________________________________________


# === Main Application =====================================================================================================================

# = Program Functions =

def read_api_key( fPath ):
    """ Read the Google API key """
    entryFunc = lambda txtLine : [ str( rawToken ) for rawToken in txtLine.split( ',' ) ]
    lines = parse_lines( fPath , entryFunc )
    rtnDict = {}
    for line in lines:
        rtnDict[ line[0] ] = line[1]
    return rtnDict

# _ End Func _

# = Program Vars =



# _ End Vars _

if __name__ == "__main__":
    print __prog_signature__()
    termArgs = sys.argv[1:] # Terminal arguments , if they exist
    
    apiKey = read_api_key( "GNWKEY.txt" )
    print apiKey
    
    clientID = apiKey[ 'clientID' ] # Enter your Client ID here '*******-************************'
    userID   = register( clientID ) # Registration should not be done more than once per session
    
    # The search function requires a clientID, userID, and at least one of either { artist , album , track } to be specified.
    metadata = search(
        clientID = clientID , 
        userID   = userID , 
        artist   = 'Kings Of Convenience' , 
        album    = 'Riot On An Empty Street' , 
        track    = 'Homesick' 
    )
    
    for key , val in metadata.iteritems():
        print key , ":" , val 
    
# ___ End Main _____________________________________________________________________________________________________________________________


# === Spare Parts ==========================================================================================================================



# ___ End Spare ____________________________________________________________________________________________________________________________
