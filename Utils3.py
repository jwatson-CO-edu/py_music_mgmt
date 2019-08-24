#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Template Version: 2018-03-23

"""
Utils3.py
James Watson, 2019 April
[M]odule [ARCH]ive for a [H]obby and [R]esearch [E]nvironment
Helper functions
NOTE: This file is the 3.6 replacement for the 2.7 "marchhare.py"
"""

# ~~~ Imports ~~~
# ~~ Standard ~~
import os , __builtin__ , operator
from math import pi , sqrt
# ~~ Special ~~
import numpy as np
# ~~ Local ~~

# ~~ Constants , Shortcuts , Aliases ~~
EPSILON = 1e-7
infty   = 1e309 # URL: http://stackoverflow.com/questions/1628026/python-infinity-any-caveats#comment31860436_1628026
endl    = os.linesep
sqt2    = sqrt(2)

# === PATH AND ENVIRONMENT ===========================================================================================================

def install_constants():
    """ Add the constants that you use the most """
    __builtin__.EPSILON = 1e-7 # ------ Assume floating point errors below this level
    __builtin__.infty   = 1e309 # ----- URL: http://stackoverflow.com/questions/1628026/python-infinity-any-caveats#comment31860436_1628026
    __builtin__.endl    = os.linesep #- Line separator
    __builtin__.pyEq    = operator.eq # Default python equality
    __builtin__.piHalf  = pi/2
    

# __ End Environment __

# ___ END PATH & ENV _________________________________________________________________________________________________________________


# === FILE OPERATIONS ======================================================================================================================

def lines_from_file( fPath ): 
    """ Open the file at 'fPath' , and return lines as a list of strings """
    with open( fPath , 'r' ) as f:
        lines = f.readlines()
    return lines

def strip_endlines_from_lines( lines ):
    """ Remove the endlines from a list of lines read from a file """
    rtnLines = []
    for line in lines:
        currLine = ''
        for char in line:
            if char != '\n' and char != '\r':
                currLine += char
        rtnLines.append( currLine )
    return rtnLines

def strip_comments_from_lines( lines ):
    """ Remove everything after each # """
    # NOTE: This function does not take into account a '#' within a string
    rtnLines = []
    for line in lines:
        rtnLines.append( str( line.split( '#' , 1 )[0] ) )
    return rtnLines

def purge_empty_lines( lines ):
    """ Given a list of lines , Remove all lines that are only whitespace """
    rtnLines = []
    for line in lines:
        if ( not line.isspace() ) and ( len( line ) > 0 ):
            rtnLines.append( line )
    return rtnLines

def parse_lines( fPath , parseFunc ):
    """ Parse lines with 'parseFunc' while ignoring Python-style # comments """
    # NOTE: This function does not take into account a '#' within a string
    rtnExprs = []
    # 1. Fetch all the lines
    lines = lines_from_file( fPath )
    # 2. Scrub comments from lines
    lines = strip_comments_from_lines( lines )
    # 3. Purge empty lines
    lines = purge_empty_lines( lines )
    # 3.5. Remove newlines
    lines = strip_endlines_from_lines( lines )
    # 4. For each of the remaining lines , Run the parse function and save the results
    for line in lines:
        rtnExprs.append( parseFunc( line ) )
    # 5. Return expressions that are the results of processing the lines
    return rtnExprs

def parse_lines_into_columns( fPath , parseFunc ):
    """ Parse lines with 'parseFunc' into equal-length columns of data, while ignoring Python-style # comments """
    prsdExprs = parse_lines( fPath , parseFunc )
    numCols   = len( prsdExprs[0] )
    rntCols   = [ [] for i in range( numCols ) ]
    for expr in prsdExprs:
        if len( expr ) != numCols:
            print( "WARNING: " )
            return rntCols
        for j in range( numCols ):
            rntCols[j].append( expr[j] )
    return rntCols
        
def tokenize_with_char( rawStr , separator = ',' ,  evalFunc = str ): 
    """ Return a list of tokens taken from 'rawStr' that is partitioned with a separating character, transforming each token with 'evalFunc' """
    return [ evalFunc( rawToken ) for rawToken in rawStr.split( separator ) ]

def get_tokenizer_with_char( separator = ',' ,  evalFunc = str ):
    """ Return a function that returns a list of tokens from 'rawStr' that is split on separating character, transforming each token with 'evalFunc' """
    def rtnFunc( rawStr ):
        return [ evalFunc( rawToken ) for rawToken in rawStr.split( separator ) ]
    return rtnFunc

# ___ END FILE _____________________________________________________________________________________________________________________________


# === CONTAINER FUNCTIONS ==================================================================================================================
    
def size( struct ):
    """ Return the size of a rectangual nD array """
    # NOTE: This function assumes that the first element of each list reflects the size of all other elements at the same level
    dims = []
    level = struct
    while 1:
        try:
            dims.append( len( level ) )
            level = level[0]
        except Exception:
            break
    return dims

# ___ END CONTAINER ________________________________________________________________________________________________________________________


# === Testing ==============================================================================================================================

if __name__ == "__main__":
    pass

# ___ End Tests ____________________________________________________________________________________________________________________________