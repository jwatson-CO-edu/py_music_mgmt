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
_AUTOLOAD_CONST = True

# === PATH AND ENVIRONMENT ===========================================================================================================

def install_constants():
    """ Add the constants that you use the most """
    # NOTE: No, I don't feel guilty for adding keywords to Python in this way
    builtins.EPSILON = 1e-7 # ------ Assume floating point errors below this level
    builtins.infty   = 1e309 # ----- URL: http://stackoverflow.com/questions/1628026/python-infinity-any-caveats#comment31860436_1628026
    builtins.endl    = os.linesep #- Line separator
    builtins.pyEq    = operator.eq # Default python equality
    builtins.piHalf  = pi/2
    print( "Constants now available in `builtins`" )

if _AUTOLOAD_CONST:
    install_constants()
    
def test_constants():
    """ Test if the standard MARCHHARE constants have been loaded """
    try:
        EPSILON
        infty
        endl 
        pyEq 
        piHalf
        return True
    except NameError:
        return False

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

def pretty_list( pList ):
    """ Print a list that is composed of the '__str__' of each of the elements in the format "[ elem_0 , ... , elem_n ]" , 
    separated by commas & spaces """
    prnStr = "[ "
    for index , elem in enumerate( pList ):
        if index < len( pList ) - 1:
            prnStr += str( elem ) + " , "
        else:
            prnStr += str( elem ) + " ]"
    return prnStr

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

def build_sublists_by_cadence( flatList , cadence ): 
    """ Return a list in which each element is a list of consecutive 'flatList' elements of length 'cadence' elements if elements remain """
    rtnList = []
    for flatDex , flatElem in enumerate( flatList ):
        if flatDex % cadence == 0:
            rtnList.append( [] )
        rtnList[-1].append( flatElem )
    return rtnList

def tandem_sorted( keyList , *otherLists ): 
    """ Sort multiple lists of equal length in tandem , with the elements of each in 'otherLists' reordered to correspond with a sorted 'keyList' """
    # URL , Sort two lists in tandem: http://stackoverflow.com/a/6618543/893511
    bundle = sorted( zip( keyList , *otherLists ) , key = lambda elem: elem[0] ) # Sort the tuples by the key element
    # print "DEBUG , zipped lists:" , bundle
    rtnLists = [ [] for i in xrange( len( bundle[0] ) ) ]
    for elemTuple in bundle:
        for index , elem in enumerate( elemTuple ):
            rtnLists[ index ].append( elem ) # Send the element to the appropriate list
    return rtnLists

# ___ END CONTAINER FUNC _____________________________________________________________________________________________________________


# === CONTAINER CLASSES ==============================================================================================================

class PriorityQueue( list ): # Requires heapq 
    """ Implements a priority queue data structure. """ 
    # NOTE: PriorityQueue does not allow you to change the priority of an item. 
    #       You may insert the same item multiple times with different priorities. 

    def __init__( self , *args ):
        """ Normal 'list' init """
        list.__init__( self , *args )   
        self.count = 0
        self.s = set([])    

    def push( self , item , priority , hashable = None ):
        """ Push an item on the queue and automatically order by priority , optionally provide 'hashable' version of item for set testing """
        entry = ( priority , self.count , item )
        heapq.heappush( self , entry )
        self.count += 1
        if hashable:
            self.s.add( hashable ) 

    def contains( self , hashable ): 
        ''' Test if 'node' is in the queue '''
        return hashable in self.s

    def pop( self ):
        """ Pop the lowest-priority item from the queue """
        priority , count , item = heapq.heappop( self )
        return item

    def pop_with_priority( self ):
        """ Pop the item and the priority associated with it """
        priority , count , item = heapq.heappop( self )
        return item , priority

    def pop_opposite( self ):
        """ Remove the item with the longest priority , opoosite of the usual pop """
        priority , count , item = self[-1]
        del self[-1]
        return item

    def isEmpty(self):
        """ Return True if the queue has no items, otherwise return False """
        return len( self ) == 0

    # __len__ is provided by 'list'

    def unspool( self , N = infty , limit = infty ):
        """ Pop all items as two sorted lists, one of increasing priorities and the other of the corresponding items """
        vals = []
        itms = []
        count = 0
        while not self.isEmpty() and count < N and self.top_priority() <= limit:
            item , valu = self.pop_with_priority()
            vals.append( valu )
            itms.append( item )
            count += 1
        return itms , vals

    def peek( self ):
        """ Return the top priority item without popping it """
        priority , count , item = self[0]
        return item

    def peek_opposite( self ):
        """ Return the bottom priority item without popping it """
        priority , count , item = self[-1]
        return item

    def top_priority( self ):
        """ Return the value of the top priority """
        return self[0][0]

    def btm_priority( self ):
        """ Return the value of the bottom priority """
        return self[-1][0]

    def get_priority_and_index( self , item , eqFunc = pyEq ):
        """ Return the priority for 'item' and the index it was found at , using the secified 'eqFunc' , otherwise return None if 'item' DNE """
        for index , elem in enumerate( self ): # Implement a linear search
            if eqFunc( elem[-1] , item ): # Check the contents of each tuple for equality
                return elem[0] , index # Return priority if a match
        return None , None # else search completed without match , return None

    def reprioritize_at_index( self , index , priority ):
        """ Replace the priority of the element at 'index' with 'priority' """
        temp = list.pop( self , index ) # Remove the item at the former priority
        self.push( temp[-1] , priority ) # Push with new priority , this item should have the same hashable lookup

class Counter( dict ): 
    """ The counter object acts as a dict, but sets previously unused keys to 0 , in the style of 6300 """
    # TODO: Add Berkeley / 6300 functionality

    def __init__( self , *args , **kw ):
        """ Standard dict init """
        dict.__init__( self , *args , **kw )
        if "default" in kw:
            self.defaultReturn = kw['default']
        else:
            self.defaultReturn = 0

    def set_default( self , val ):
        """ Set a new default value to return when there is no """
        self.defaultReturn = val

    def __getitem__( self , a ):
        """ Get the val with key , otherwise return 0 if key DNE """
        if a in self: 
            return dict.__getitem__( self , a )
        return 0

    # __setitem__ provided by 'dict'

    def sorted_keyVals( self ):
        """ Return a list of sorted key-value tuples """
        sortedItems = self.items()
        sortedItems.sort( cmp = lambda keyVal1 , keyVal2 :  np.sign( keyVal2[1] - keyVal1[1] ) )
        return sortedItems

    def sample_until_unique( self , sampleFromSeq , sampleLim = int( 1e6 ) ):
        """ Sample randomly from 'sampleFromSeq' with a uniform distribution until a new key is found or the trial limit is reached , return it """
        # NOTE: If 'sampleLim' is set to 'infty' , the result may be an infinite loop if the Counter has a key for each 'sampleFromSeq'
        trial = 1
        while( trial <= sampleLim ):
            testKey = choice( sampleFromSeq )
            if self[ testKey ] == 0:
                return testKey
            trial += 1
        return None
    
class Stack(list): 
    """ LIFO container based on 'list' """    

    def __init__( self , *args ):
        """ Normal 'list' init """
        list.__init__( self , *args )

    def push( self , elem ):
        """ Push 'elem' onto the Stack """
        self.append( elem )

    # 'Stack.pop' is inherited from 'list'

    def is_empty(self):
        """ Returns true if the Stack has no elements """
        return len(self) == 0

# ___ END CONTAINER CLASS ____________________________________________________________________________________________________________


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

def iter_contains_None( listOrTuple ):
    """ Return True if any of 'listOrTuple' is None or contains None , Otherwise return False """
    if isinstance( listOrTuple , ( list , tuple ) ): # Recursive Case: Arg is an iterable , inspect each
        for elem in listOrTuple:
            if iter_contains_None( elem ):
                return True
        return False
    else: # Base Case: Arg is single value
        return True if listOrTuple == None else False
    
def elemw( iterable , i ): 
    """ Return the 'i'th index of 'iterable', wrapping to index 0 at all integer multiples of 'len(iterable)' , Wraps forward and backwards """
    seqLen = len( iterable )
    if i >= 0:
        return iterable[ i % ( seqLen ) ]
    else:
        revDex = abs( i ) % ( seqLen )
        if revDex == 0:
            return iterable[ 0 ]
        return iterable[ seqLen - revDex ]

# ___ END ITERABLE ___________________________________________________________________________________________________________________


# === Testing ==============================================================================================================================

if __name__ == "__main__":
    pass

# ___ End Tests ____________________________________________________________________________________________________________________________