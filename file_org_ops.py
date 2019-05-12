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
# ~~ Special ~~
import numpy as np
# ~~ Local ~~

# ~~ Constants , Shortcuts , Aliases ~~
EPSILON = 1e-7
infty   = 1e309 # URL: http://stackoverflow.com/questions/1628026/python-infinity-any-caveats#comment31860436_1628026
endl    = os.linesep

# URL: http://code.activestate.com/recipes/65117-converting-between-ascii-numbers-and-characters/
ASCII_ALPHANUM = [chr(code) for code in xrange(48,57+1)]+[chr(code) for code in xrange(65,90+1)]+[chr(code) for code in xrange(97,122+1)]

# === RENAMING =============================================================================================================================

def safe_dir_name( trialStr ):
    """ Return a string stripped of all disallowed chars """
    rtnStr = ""
    if trialStr: # if a string was received 
        for char in trialStr: # for each character of the input string
            if char not in DISALLOWEDCHARS and not char.isspace(): # If the character is not disallowed and is not whitespace
                try:
                    char = char.encode( 'ascii' , 'ignore' ) # Ignore conv errors but inconsistent # http://stackoverflow.com/a/2365444/893511
                    rtnStr += char # Append the char to the proper directory name
                except:
                    rtnStr += choice( ASCII_ALPHANUM ) # Random ASCII character so that completely unreadable names are not overwritten
        return rtnStr
    else:
        return None

# ___ END NAME _____________________________________________________________________________________________________________________________


# === TOPIC 2 ==============================================================================================================================


# ___ END 2 ________________________________________________________________________________________________________________________________


# === Testing ==============================================================================================================================

if __name__ == "__main__":
    pass

# ___ End Tests ____________________________________________________________________________________________________________________________