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
import os , builtins , operator
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
    builtins.EPSILON = 1e-7 # ------ Assume floating point errors below this level
    builtins.infty   = 1e309 # ----- URL: http://stackoverflow.com/questions/1628026/python-infinity-any-caveats#comment31860436_1628026
    builtins.endl    = os.linesep #- Line separator
    builtins.pyEq    = operator.eq # Default python equality
    builtins.piHalf  = pi/2

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


# === STRING OPERATIONS ==============================================================================================================

def format_dec_list( numList , places = 2 ): 
    """ Return a string representing a list of decimal numbers limited to 'places' """
    rtnStr = "[ "
    for nDex , num in enumerate( numList ):
        if isinstance( numList , np.ndarray ):
            scalar = num.item()
        else:
            scalar = num 
        if nDex < len(numList) - 1:
            rtnStr += ('{0:.' + str( places ) + 'g}').format( scalar ) + ' , '
        else:
            rtnStr += ('{0:.' + str( places ) + 'g}').format( scalar )
    rtnStr += " ]"
    return rtnStr

# ___ END STRING _____________________________________________________________________________________________________________________


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

def concat_arr( *arrays ):
    """ Concatenate all 'arrays' , any of which can be either a Python list or a Numpy array """
    # URL , Test if any in an iterable belongs to a certain class : https://stackoverflow.com/a/16705879
    if any( isinstance( arr , np.ndarray ) for arr in arrays ): # If any of the 'arrays' are Numpy , work for all cases , 
        if len( arrays ) == 2: # Base case 1 , simple concat    # but always returns np.ndarray
            return np.concatenate( ( arrays[0] , arrays[1] ) )
        elif len( arrays ) > 2: # If there are more than 2 , concat the first two and recur
            return concat_arr( 
                np.concatenate( ( arrays[0] , arrays[1] ) ) , 
                *arrays[2:] 
            )
        else: # Base case 2 , there is only one arg , return it
            return arrays[0]
    if len( arrays ) > 1: # else no 'arrays' are Numpy 
        rtnArr = arrays[0]
        for arr in arrays[1:]: # If there are more than one , just use addition operator in a line
            rtnArr += arr
        return rtnArr
    else: # else there was only one , return it
        return arrays[0] 

# ___ END CONTAINER ________________________________________________________________________________________________________________________


# === ITERABLE STRUCTURES ============================================================================================================

def incr_min_step( bgn , end , stepSize ):
    """ Return a list of numbers from 'bgn' to 'end' (inclusive), separated by at LEAST 'stepSize'  """
    # NOTE: The actual step size will be the size that produces an evenly-spaced list of trunc( (end - bgn) / stepSize ) elements
    return np.linspace( bgn , end , num = trunc( (end - bgn) / stepSize ) , endpoint=True )

def incr_max_step( bgn , end , stepSize ):
    """ Return a list of numbers from 'bgn' to 'end' (inclusive), separated by at MOST 'stepSize'  """
    numSteps = ( end - bgn ) / ( stepSize * 1.0 )
    rtnLst = [ bgn + i * stepSize for i in xrange( trunc(numSteps) + 1 ) ]
    if numSteps % 1 > 0: # If there is less than a full 'stepSize' between the last element and the end
        rtnLst.append( end )
    return rtnLst

# ___ END ITERABLE ___________________________________________________________________________________________________________________


# === Testing ==============================================================================================================================

if __name__ == "__main__":
    pass

# ___ End Tests ____________________________________________________________________________________________________________________________