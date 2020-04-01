#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Template Version: 2018-03-23

# ~~ Future First ~~
from __future__ import division # Future imports must be called before everything else, including triple-quote docs!

"""
file_org_ops.py
James Watson, 2019 May
File ops for music organization
"""

# ~~~ Imports ~~~
# ~~ Standard ~~
import os
from math import pi , sqrt
from random import choice
# ~~ Special ~~
import numpy as np
# ~~ Local ~~

# ~~ Constants , Shortcuts , Aliases ~~
EPSILON = 1e-7
infty   = 1e309 # URL: http://stackoverflow.com/questions/1628026/python-infinity-any-caveats#comment31860436_1628026
endl    = os.linesep

# URL: http://code.activestate.com/recipes/65117-converting-between-ascii-numbers-and-characters/
ASCII_ALPHANUM = [chr(code) for code in xrange(48,57+1)]+[chr(code) for code in xrange(65,90+1)]+[chr(code) for code in xrange(97,122+1)]
DISALLOWEDCHARS = "\\/><|:&; \r\t\n.\"\'?*" # Do not create a directory or file with these chars

# === RENAMING =============================================================================================================================

def safe_dir_name( trialStr , defaultChar = None ):
    """ Return a string stripped of all disallowed chars """
    rtnStr = ""
    if trialStr: # if a string was received 
        for char in trialStr: # for each character of the input string
            if char not in DISALLOWEDCHARS and not char.isspace(): # If the character is not disallowed and is not whitespace
                try:
                    char = char.encode( 'ascii' , 'ignore' ) # Ignore conv errors but inconsistent # http://stackoverflow.com/a/2365444/893511
                    rtnStr += char # Append the char to the proper directory name
                except:
                    if defaultChar == None:
                        rtnStr += choice( ASCII_ALPHANUM ) # Random ASCII character so that completely unreadable names are not overwritten
                    else:
                        rtnStr += defaultChar
        return rtnStr
    else:
        return None

# ___ END NAME _____________________________________________________________________________________________________________________________


# === DIRECTORIES ==========================================================================================================================

def makedirs_exist_ok( path ):
    """ Mimic the 3.6 behavior 'os.makedirs( path , exist_ok = 1 )' """
    if not os.path.isdir( path ):
        os.makedirs( path )
        print path , "- CREATED"
    else:
        print path , "- EXISTS!"

# ___ END DIR ________________________________________________________________________________________________________________________________


# === Testing ==============================================================================================================================

if __name__ == "__main__":
    pass

# ___ End Tests ____________________________________________________________________________________________________________________________