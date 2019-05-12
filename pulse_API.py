#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ~~ Future First ~~
from __future__ import division # Future imports must be called before everything else, including triple-quote docs!

__progname__ = "pulse_API.py"
__version__  = "2019.05" 
__desc__     = "Query the API to keep it from dying"
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


from math import sqrt
# ~~ Local ~~
from API_session import Session , open_all_APIs
from retrieve_yt import fetch_metadata_by_yt_video_ID 

# ~~ Constants , Shortcuts , Aliases ~~
EPSILON = 1e-7
infty   = 1e309 # URL: http://stackoverflow.com/questions/1628026/python-infinity-any-caveats#comment31860436_1628026
endl    = os.linesep
sqt2    = sqrt(2)

# ~~ Script Signature ~~
def __prog_signature__(): return __progname__ + " , Version " + __version__ # Return a string representing program name and verions

# ___ End Init _____________________________________________________________________________________________________________________________


# === Main Program =========================================================================================================================


# === Program Classes ===



# ___ End Class ___


# === Program Functions ===



# __ End Func __


# === Program Vars ===



# ___ End Vars ___


# === Main Func ===

if __name__ == "__main__":
    print __prog_signature__()
    termArgs = sys.argv[1:] # Terminal arguments , if they exist
    
    # 1. Open the API
    sssn = Session()
    open_all_APIs( sssn )
    
    # 2. Query a video
    discard = fetch_metadata_by_yt_video_ID( sssn.youtube , sssn.METADATA_SPEC , "PG1R9OPofEg" )
    
    # 3. Close session
    if 0: # WARNING: Calling this MAY overwrite the current session file
        close_session( sssn )
    
# ___ End Main ___

# ___ End Program __________________________________________________________________________________________________________________________


# === Spare Parts ==========================================================================================================================



# ___ End Spare ____________________________________________________________________________________________________________________________
