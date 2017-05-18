#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ~~ Future First ~~
from __future__ import division # Future imports must be called before everything else, including triple-quote docs!

"""
ResearchEnv.py , Built on Wing IDE 101 for Python 2.7
Erik Lindstrom , Adam Sperry , James Watson, 2016 October
Helper functions for assembly planning
"""

# ~ PATH Changes ~ 
import sys, os
def localize(scriptHandle): # For some reason this is needed in Windows 10 Spyder (Py 2.7) # 2016-07-22: Seem to be okay without it?
    """ Add the current directory to Python path if it is not already there """
    containerDir = os.path.dirname(scriptHandle)
    if containerDir not in sys.path:
        sys.path.append( containerDir )

def find_in_path(term):
    """ Search for a term in 'sys.path' and print all the matching entries """
    term = str(term).lower()
    for key,val in sys.modules.iteritems():
        if term in str(key).lower() or term in str(val).lower():
            print("{: >60} {: >60} ".format(key,val))

# ~~ Libraries ~~
# ~ Standard Libraries ~
import math, datetime, cPickle , heapq , time , operator
from math import sqrt, ceil, trunc, sin, cos, tan, atan2, asin, acos, atan, pi, degrees, radians, log, log10, exp, e, factorial
from random import random, randrange
from timeit import default_timer as timer # URL, Benchmarking: http://stackoverflow.com/a/25823885
# ~ Special Libraries ~
import matplotlib.pyplot as plt # 2016-07-14: Spends forever building fonts at the beginning of every run!
import numpy as np
# ~ Local Libraries ~

#set_dbg_lvl(1) # Debug 'eq_in_list'

# ~~ Constants , Shortcuts , Aliases ~~
import __builtin__ # URL, add global vars across modules: http://stackoverflow.com/a/15959638/893511
__builtin__.EPSILON = 1e-7 # Assume floating point errors below this level
__builtin__.infty = 1e309 # URL: http://stackoverflow.com/questions/1628026/python-infinity-any-caveats#comment31860436_1628026
__builtin__.endl = os.linesep # Line separator
__builtin__.pyEq = operator.eq # Default python equality
__builtin__.piHalf = pi/2

# == Helper Functions ==

def sep( title = "" , width = 6 , char = '=' , strOut = False ): # <<< resenv
    """ Print a separating title card for debug """
    LINE = width * char
    if strOut:
        return LINE + ' ' + title + ' ' + LINE
    else:
        print LINE + ' ' + title + ' ' + LINE
    
# == End Helper ==
        

# == General Math Helpers ==

# = Equality Tests =

def eq(op1, op2): # <<< resenv
    """ Return true if op1 and op2 are close enough """
    return abs(op1 - op2) <= EPSILON
    
def eq_margin( op1 , op2 , margin = EPSILON ): # >>> resenv
    """ Return true if op1 and op2 are within 'margin' of each other, where 'margin' is a positive real number """
    return abs( op1 - op2 ) <= margin

def equality_test_w_margin( margin = EPSILON ):
    """ Return a function that performs an 'eq' comparison with the specified margin """
    def eq_test( op1 , op2 ):
        return eq_margin( op1 , op2 , margin )
    return eq_test

def round_small(val): 
    """ Round a number to 0 if it is within 'EPSILON' of 0 , otherwise return the number """
    # print "Compare to zero:" ,  val
    return 0.0 if eq( val , 0.0 ) else val

# = End Equality =

def wrap_normalize( wrapBounds , number ):
    """ Normalize 'number' to be within 'wrapBounds' on a number line that wraps to 'wrapBounds[0]' when 'wrapBounds[1]' is surpassed and vice-versa """
    span = abs( wrapBounds[1] - wrapBounds[0] )
    if number < wrapBounds[0]:
        return wrapBounds[1] - ( abs( wrapBounds[0] - number ) % span )
    elif number > wrapBounds[1]:
        return ( number % span ) + wrapBounds[0]
    else:
        return number

def within_wrap_bounds( wrapBounds , checkBounds , number ):
    """ Return True if 'number' falls within 'checkBounds' on a wrapped number line defined by 'wrapBounds' , Both directions possible , closed interval """
    # Normalize the number and the checked bounds within wrap bounds so that we can deal with them in a simple way
    number = wrap_normalize( wrapBounds , number )
    checkBounds = [ wrap_normalize( wrapBounds , checkBounds[0] ) , wrap_normalize( wrapBounds , checkBounds[1] ) ] 
    if checkBounds[0] <= checkBounds[1]: # Increasing order indicates a normal , number-line bounds check
        return ( number >= checkBounds[0] ) and ( number <= checkBounds[1] )
    else: # Decreasing order indicates that the checked bounds cross the wrapping boundary
        return ( number <= checkBounds[0] ) or  ( number >= checkBounds[1] )
    
def wrap_bounds_fraction( wrapBounds , checkBounds , number ):
    """ If 'number' is within 'checkBounds' return a number on a scale with checkBounds[0]-->0 and checkBounds[1]-->1 , else return None , Both directions possible """
    # NOTE: 'wrapBounds' MUST be specified in increasing order!
    # Normalize the number and the checked bounds within wrap bounds so that we can deal with them in a simple way
    number = wrap_normalize( wrapBounds , number )
    checkBounds = [ wrap_normalize( wrapBounds , checkBounds[0] ) , wrap_normalize( wrapBounds , checkBounds[1] ) ] 
    if checkBounds[0] <= checkBounds[1]: # Increasing order indicates a normal , number-line bounds check
        if ( number >= checkBounds[0] ) and ( number <= checkBounds[1] ):
            return abs( number - checkBounds[0] ) * 1.0 / abs( checkBounds[1] - checkBounds[0] )
        elif checkBounds[0] == checkBounds[1]:
            return 1
        else:
            return None # Careful , 0 == False!
    else: # Decreasing order indicates that the checked bounds cross the wrapping boundary
        if ( number <= checkBounds[0] ) or ( number >= checkBounds[1] ):
            return abs( number - checkBounds[0] ) * 1.0 / ( abs( checkBounds[1] - wrapBounds[0] ) + abs( wrapBounds[1] - checkBounds[0] ) )
        elif checkBounds[0] == checkBounds[1]:
            return 1
        else:
            return None

def roundint( num ):
    """ Round 'num' to the nearest int """
    return int( round( num ) )

# == End Math Helpers ==

# == Time Reporting and Formatting ==

def elapsed_w_msg( msg = "Elapsed:" ): # >>> resenv
    """ Return the time elapsed and print with a msg """
    if elapsed_w_msg.lastTime == None:
        print msg , "Timer started!"
        elapsed_w_msg.lastTime = time.time()
        return 0
    else:
        seconds = elapsed = time.time() - elapsed_w_msg.lastTime
        hours = int( elapsed / elapsed_w_msg.s_in_hr )
        elapsed = elapsed % elapsed_w_msg.s_in_hr
        mins = int( elapsed / elapsed_w_msg.s_in_mn )
        elapsed = elapsed % elapsed_w_msg.s_in_mn 
        print msg , hours , "hrs" , mins , "min" , elapsed , "sec"
        elapsed_w_msg.lastTime = time.time()
        return seconds
elapsed_w_msg.lastTime = None
elapsed_w_msg.s_in_hr = 60 * 60
elapsed_w_msg.s_in_mn = 60

nowTimeStamp = lambda: datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') # http://stackoverflow.com/a/5215012/893511 # <<< resenv
""" Return a formatted timestamp string, useful for logging and debugging """

nowTimeStampFine = lambda: datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f') # http://stackoverflow.com/a/5215012/893511 # <<< resenv
""" Return a formatted timestamp string, useful for logging and debugging """

def format_epoch_timestamp( sysTime ):
    """ Format epoch time into a readable timestamp """
    return datetime.datetime.fromtimestamp( sysTime ).strftime('%Y-%m-%d_%H-%M-%S-%f')

class Timer: 
    """ The simplest timer possible """
    startTime = 0 # init timer to zero so that 'Timer.elapsed' does not fail if 'Timer.begin' is not called first 
    
    @staticmethod
    def begin():
        """ Begin / reset the timer and return the start time """
        Timer.startTime = time.time()
        return Timer.startTime
        
    @staticmethod
    def elapsed():
        """ Return the number of seconds that have passed since the last time 'Timer.begin' was called """
        return time.time() - Timer.startTime

def tick_progress( div = 1000 , reset = False ):
    """ Print the 'marker' every 'div' calls """
    if reset:
        tick_progress.totalCalls = 0
    else:
        tick_progress.totalCalls += 1
        if tick_progress.totalCalls % div == 0:
            tick_progress.ticks += 1
            print tick_progress.sequence[ tick_progress.ticks % ( len( tick_progress.sequence ) ) ] ,
tick_progress.totalCalls = 0
tick_progress.sequence = [ "'" , "-" , "," , "_" , "," , "-" , "'" , "`" , "`" ] # This makes a quite pleasant wave
tick_progress.ticks = 0

# == End Time ==

# ~ Cleanup ~
plt.close('all') # clear any figures we may have created before 


# == Trigonometry ==
# = Trig in Degrees =
def cosd(angleDeg): # <<< resenv
    """ Return the cosine of the angle specified in degrees """
    return cos( radians( angleDeg ) )

def sind(angleDeg): # <<< resenv
    """ Return the sine of the angle specified in degrees """
    return sin( radians( angleDeg ) )

def tand(angleDeg): # <<< resenv
    """ Return the tangent of the angle specified in degrees """
    return tan( radians( angleDeg ) )
    
def atan2d( y , x ): # <<< resenv
    """ Return the angle, in degrees, of a vector/phasor specified by 'y' and 'x' """
    return degrees( atan2( y , x) )
    
def asind( ratio ): # <<< resenv
    """ Return the arcsine of a ratio, degrees """
    return degrees( asin( ratio ) ) 
    
def acosd( ratio ): # <<< resenv
    """ Return the arccosine of a ratio, degrees """
    return degrees( acos( ratio ) )
    
def atand( ratio ): # <<< resenv
    """ Return the arctangent of a ratio, degrees """
    return degrees( atan( ratio ) )
# = End Deg Trig =
# == End Trig ==


# == Data Structures , Special Lists , and Iterable Operations ==

def elemw(i, iterable): 
    """ Return the 'i'th index of 'iterable', wrapping to index 0 at all integer multiples of 'len(iterable)' """
    return iterable[ i % ( len(iterable) ) ]
                    
def indexw( i , iterable ): # TODO: ADD TO RESENV
    """ Return the 'i'th index of 'iterable', wrapping to index 0 at all integer multiples of 'len(iterable)' """
    return i % ( len(iterable) )

def eq_in_list(item, pLst, eqFunc = eq): # <<< resenv
    """ Return true if there is at least one element in 'pLst' that is equal to 'item' according to 'eqFunc' """
    # NOTE: This function is not recursive
    hasEq = False
    for elem in pLst:
        # dbgLog(1, elem,',', item)
        if eqFunc(elem, item):
            hasEq = True
            break
    return hasEq
    
def eq_list(lst1 , lst2 , eps = EPSILON ): # <<< resenv
    """ Determine if every item in 'lst1' and 'lst2' are close enough """ 
    # NOTE: This function is not recursive
    if len(lst1) != len(lst2): # If the lists do not have equal length, lists are not equal
        return False
    else: # else lists are of equal length, iterate
        for index in xrange(len(lst1)): # for every item in the list
            if not abs( lst1[index] - lst2[index] ) <= eps: # test equality, if not equal, then return False
                return False
        return True # Made it through the list without failed tests, return True

def lst(*args): # <<< resenv
    """ Return a list composed of the arbitrary 'args' """
    return list(args)

def tpl(*args): # <<< resenv
    """ Return a tuple composed of the arbitrary 'args' """
    return tuple(args)     

def sort_list_to_tuple( pList ):
    """ Return a tuple that contains the sorted elements of 'pList' """
    return tuple( sorted( pList ) )

def sort_tuple( tup ):
    """ Return a sorted copy of 'tup' """
    return sort_list_to_tuple( list( tup ) ) 

def sum_abs_diff_lists( op1 , op2 ): # <<< resenv
    """ Return the cumulative, absolute, element-wise difference between two lists of equal length """
    # NOTE: This function is not recursive
    return sum( np.abs( np.subtract( op1 , op2 ) ) ) # NOTE: There will be an error if lists not of equal length

def incr_min_step( bgn , end , stepSize ): # formerly 'incr_steps'  # <<< resenv
    """ Return a list of numbers from 'bgn' to 'end' (inclusive), separated by at LEAST 'stepSize'  """
    # NOTE: The actual step size will be the size that produces an evenly-spaced list of trunc( (end - bgn) / stepSize ) elements
    return np.linspace( bgn , end , num = trunc( (end - bgn) / stepSize ) , endpoint=True )

def incr_max_step( bgn , end , stepSize ): # <<< resenv
    """ Return a list of numbers from 'bgn' to 'end' (inclusive), separated by at MOST 'stepSize'  """
    numSteps = (end - bgn) / stepSize
    rtnLst = [ bgn + i * stepSize for i in xrange( trunc(numSteps) + 1 ) ]
    if numSteps % 1 > 0: # If there is less than a full 'stepSize' between the last element and the end
        rtnLst.append( end )
    return rtnLst

def assoc_lists( keys , values ): # Added to ResearchEnv 2016-09-13 # <<< resenv
    """ Return a dictionary with associated 'keys' and 'values' """
    return dict( zip( keys , values ) )

def assoc_sort_tuples( keyList , valList ):
    """ Associate each element of 'keyList' with each element of 'valList' , sort on 'keyList' , return list of tuples """
    return [ elem for elem in sorted( zip( keyList , valList ) , key = lambda pair: pair[0] ) ]

def tandem_sorted( keyList , *otherLists ): # URL , Sort two lists in tandem: http://stackoverflow.com/a/6618543/893511
    """ Sort multiple lists of equal length in tandem , with the elements of each in 'otherLists' reordered to correspond with a sorted 'keyList' """
    # keySorted = sorted( keyList )
    bundle = sorted( zip( keyList , *otherLists ) , key = lambda elem: elem[0] ) # Sort the tuples by the key element
    # print "DEBUG , zipped lists:" , bundle
    rtnLists = [ [] for i in xrange( len( bundle[0] ) ) ]
    for elemTuple in bundle:
        for index , elem in enumerate( elemTuple ):
            rtnLists[ index ].append( elem ) # Send the element to the appropriate list
    return rtnLists

def tandem_sorted_reverse( keyList , *otherLists ): # URL , Sort two lists in tandem: http://stackoverflow.com/a/6618543/893511
    """ Sort multiple lists of equal length in tandem , with the elements of each in 'otherLists' reordered to correspond with a sorted 'keyList' """
    # keySorted = sorted( keyList )
    bundle = sorted( zip( keyList , *otherLists ) , key = lambda elem: elem[0] , reverse = True ) # Sort the tuples by the key element
    # print "DEBUG , zipped lists:" , bundle
    rtnLists = [ [] for i in xrange( len( bundle[0] ) ) ]
    for elemTuple in bundle:
        for index , elem in enumerate( elemTuple ):
            rtnLists[ index ].append( elem ) # Send the element to the appropriate list
    return rtnLists
    
def index_max( pList ):
    """ Return the first index of 'pList' with the maximum numeric value """
    return pList.index( max( pList ) )
    
def index_min( pList ): # Added , 2017-02-16
    """ Return the first index of 'pList' with the maximum numeric value """
    return pList.index( min( pList ) )
    
def linspace_space( dim , sMin , sMax , num  ): # <<< resenv
    """ Return vector list covering a 'dim'-dimensional space with 'num' points in each dimension, from 'sMin' to 'sMax' in each dimension , O(n^2) """
    rtnLst = [] # List of vectors to return
    currDim = np.linspace( sMin , sMax , num ) # Get evenly-spaced points in this dimension
    if dim == 1: # Base case, this is the last dimension in the vector
        return [ [item] for item in currDim ]
    elif dim > 1: # Recursive case , for every combination of the first m dimensions, create every combination of the remaining m-n dimensions
        for item in currDim:
            for sub in linspace_space( dim-1 , sMin , sMax , num  ):
                rtnLst.append( [item] + sub )
    return rtnLst

def find_pop( iterable , item ): # >>> resenv
    """ Pop 'item' from 'iterable' , ValueError if not in 'iterable' """
    return iterable.pop( iterable.index( item ) )
    
def insert_sublist( bigList , index , subList ): # TODO: Add to resenv
    """ Insert 'subList' into 'bigList' at 'index' and return resulting list """
    return bigList[ :index ] + subList + bigList[ index: ]

def replace_sublist( bigList , begDex , endDex , subList ): # TODO: Add to resenv
    """ Replace the elements in 'bigList' from 'begDex' to 'endDex' with 'subList' """
    return bigList[ :begDex ] + subList + bigList[ endDex: ]

def index_eq( pList , num , margin = EPSILON ):
    """ Return the index of the first occurrence of 'num' in 'pList' , otherwise return None """
    for index , elem in enumerate( pList ):
        if eq_margin( num , elem , margin ):
            return index
    return None
    
# = Containers for Algorithms =

class Stack(list): # <<< resenv
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
        
class Queue(list): # >>> resenv
    """ FIFO container based on 'list' """ 
    
    def __init__( self , *args ):
        """ Normal 'list' init """
        list.__init__( self , *args )

    def push( self , elem ):
        """ Push an item (prepend) to the back of the Queue """
        self.insert( 0 , elem )

    # 'Queue.pop' is inherited from 'list'

    def is_empty(self):
        """ Returns true if the Queue has no elements """
        return len(self) == 0
        
    def item_list( self ):
        """ Return a copy of the Queue as a list """
        return self[:]

class PriorityQueue(list): # Requires heapq 
    """ Implements a priority queue data structure. """ 
    # NOTE: PriorityQueue does not allow you to change the priority of an item. You may insert the same item multiple times with different priorities. 
        
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

class BPQ( PriorityQueue ):
    """ Bounded Priority Queue , does not keep more than N items in the queue """
    
    def __init__( self , boundN , *args ):
        """ Create a priority queue with a specified bound """
        PriorityQueue.__init__( self , *args )
        self.bound = boundN
    
    def push( self , item , priority , hashable=None ):
        """ Push an item onto the queue and discard largest priority items that are out of bounds """
        PriorityQueue.push( self , item , priority , hashable ) # The usual push
        while len( self ) > self.bound: # If we exceeded the bounds , then discard down to the limit
            self.pop_opposite()
            
class LPQ( PriorityQueue ):
    """ Limited Priority Queue , does not keep items with priorities longer than 'limit' """
    
    def __init__( self , limitR , *args ):
        """ Create a priority queue with a specified bound """
        PriorityQueue.__init__( self , *args )
        self.limit = limitR
    
    def push( self , item , priority , hashable=None ):
        """ Push an item onto the queue and discard largest priority items that are out of bounds """
        if priority <= self.limit:
            PriorityQueue.push( self , item , priority , hashable ) # The usual push

class PQwR(list): # Requires heapq # TODO: UPDATE ASMENV
    """ Implements a priority queue data structure, replaces items with identical priorituies """ 
    # NOTE: PriorityQueue does not allow you to change the priority of an item. You may insert the same item multiple times with different priorities. 
        
    def __init__( self , *args ):
        """ Normal 'list' init """
        list.__init__( self , *args )   
        self.count = 0
        self.s = set([])    
        
    def push( self , item , priority , hashable=None ):
        """ Push an item on the queue and automatically order by priority , optionally provide 'hashable' version of item for set testing """
        entry = ( priority , item )
        heapq.heappush( self , entry )
        if hashable:
            self.s.add( hashable ) 
    
    def contains( self , hashable ): 
        ''' Test if 'node' is in the queue '''
        return hashable in self.s

    def pop( self ):
        """ Pop the lowest-priority item from the queue """
        priority , item = heapq.heappop( self )
        return item
        
    def pop_with_priority( self ):
        """ Pop the item and the priority associated with it """
        priority , item = heapq.heappop( self )
        return item , priority
        
    def pop_opposite( self ):
        """ Remove the item with the longest priority , opoosite of the usual pop """
        priority , item = self[-1]
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
        """ Return the shortest priority item without popping it """
        priority , item = self[0]
        return item
        
    def peek_opposite( self ):
        """ Return the longest priority item without popping it """
        priority , item = self[-1]
        return item
        
    def top_priority( self ):
        """ Return the value of the top priority """
        return self[0][0]
        
    def btm_priority( self ):
        """ Return the value of the bottom priority """
        return self[-1][0]

class BPQwR( PQwR ): # TODO: ADD TO ASMENV
    """ Bounded Priority Queue , does not keep more than N items in the queue """
    
    def __init__( self , boundN , *args ):
        """ Create a priority queue with a specified bound """
        PQwR.__init__( self , *args )
        self.bound = boundN
    
    def push( self , item , priority , hashable=None ):
        """ Push an item onto the queue and discard largest priority items that are out of bounds """
        PQwR.push( self , item , priority , hashable ) # The usual push
        while len( self ) > self.bound: # If we exceeded the bounds , then discard down to the limit
            self.pop_opposite()
 
class LPQwR( PQwR ): # TODO: ADD TO ASMENV
    """ Limited Priority Queue , does not accept items with priorities longer than 'limit' """
    
    def __init__( self , limitR , *args ):
        """ Create a priority queue with a specified bound """
        PQwR.__init__( self , *args )
        self.limit = limitR
    
    def push( self , item , priority , hashable = None ):
        """ Push an item onto the queue if it is leq the limit """
        if priority <= self.limit:
            PQwR.push( self , item , priority , hashable ) # The usual push
          
class Counter(dict): # >> resenv
    """ The counter object acts as a dict, but sets previously unused keys to 0 , in the style of 6300 """
    # TODO: Add Berkeley / 6300 functionality
    
    def __init__( self , *args , **kw ):
        """ Standard dict init """
        dict.__init__( self , *args , **kw )
        
    def __getitem__( self , a ):
        """ Get the val with key , otherwise return 0 if key DNE """
        if a in self: 
            return dict.__getitem__( self , a )
        return 0
    
    # __setitem__ provided by 'dict'
    
    def sorted_keyVals( self ):
        """ Return a list of sorted key-value tuples """
        sortedItems = self.items()
        sortedItems.sort( cmp = lambda keyVal1 , keyVal2 :  sign( keyVal2[1] - keyVal1[1] ) )
        return sortedItems

# = End Algo Containers =

def is_nonempty_list( obj ): return isinstance( obj , list ) and len( obj ) > 0 # Return true if 'obj' is a 'list' with length greater than 0  # <<< resenv

# == End Structures ==


# == Generators, Iterators, and Custom Comprehensions ==

def enumerate_reverse(L): # <<< resenv
    """ A generator that works like 'enumerate' but in reverse order """
    # URL, Generator that is the reverse of 'enumerate': http://stackoverflow.com/a/529466/893511
    for index in reversed(xrange(len(L))):
        yield index, L[index]

# == End Generators ==


# == Printing Helpers ==

def lists_as_columns_with_titles(titles, lists): # <<< resenv
    """ Print each of the 'lists' as columns with the appropriate 'titles' """
    longestList = 0
    longestItem = 0
    prntLists = []
    pad = 4 * ' '
    if len(titles) == len(lists):
        for lst in lists:
            if len(lst) > longestItem:
                longestList = len(lst)
            prntLists.append( [] )
            for item in lst:
                strItem = str(item)
                prntLists[-1].append( strItem )
                if len(strItem) > longestItem:
                    longestItem = len(strItem)
        line = ''
        for title in titles:
            line += title[ : len(pad) + longestItem -1 ].rjust( len(pad) + longestItem , ' ' )
        print line
        for index in range(longestList):
            line = ''
            for lst in prntLists:
                if index < len(lst):
                    line += pad + lst[index].ljust(longestItem, ' ')
                else:
                    line += pad + longestItem * ' '
            print line
    else:
        print "Titles" , len(titles) , "and lists" , len(lists) , "of unequal length"

def print_list( pList ):
    """ Print a list that is composed of the '__str__' of each of the elements in the format "[ elem_0 , ... , elem_n ]" , separated by commas & spaces """
    prnStr = "[ "
    for index , elem in enumerate( pList ):
        if index < len( pList ) - 1:
            prnStr += str( elem ) + " , "
        else:
            prnStr += str( elem ) + " ]"
    print prnStr
    
def str_args( *args , **kwargs ):
    """ Print a sequence that is composed of the '__str__' of each of the arguments in the format "elem_0 , ... , elem_n" , separated by commas & spaces """
    prnStr = ""
    for index , elem in enumerate( args ):
        if index < len( args ) - 1:
            prnStr += str( elem ) + " , "
        else:
            prnStr += str( elem )
    if "printStr" in kwargs:
        print prnStr
    else:
        return prnStr

# == End Printing ==


# == File Operations ==

def struct_to_pkl( struct , pklPath ): # <<< resenv
    """ Serialize a 'struct' to 'pklPath' """
    f = open( pklPath , 'wb') # open a file for binary writing to receive pickled data
    cPickle.dump( struct , f ) # changed: pickle.dump --> cPickle.dump
    f.close()
    
def load_pkl_struct( pklPath ): # <<< resenv
    """ Load a pickled object and return it, return None if error """
    fileLoaded = False
    rtnStruct = None
    try:
        f = open( pklPath , 'rb')
        fileLoaded = True
    except Exception as err:
        print "load_pkl_struct: Could not open file,",pklPath,",",err
    if fileLoaded:
        try:
            rtnStruct = cPickle.load( f )
        except Exception as err:
            print "load_pkl_struct: Could not unpickle file,",pklPath,",",err
        f.close()
    return rtnStruct
    
def process_txt_for_LaTeX( TXTpath ):  # <<< resenv
    """ Add appropriate line breaks to a TXT file and return as TEX """
    if os.path.isfile( TXTpath ):
        drctry , txtName = os.path.split( TXTpath )
        ltxName = txtName[:-4] + ".tex"
        txtFile = file( TXTpath , 'r' )
        txtLines = txtFile.readlines()
        txtFile.close()
        ltxPath = os.path.join( drctry , ltxName )
        ltxFile = file( ltxPath , 'w' )
        for line in txtLines:
            # print "Line is:", line
            if len(line) > 3:
                ltxFile.write( line.rstrip() + " \\\\ " + endl ) 
            else:
                ltxFile.write( " $\\ $ \\\\ " + endl ) 
        ltxFile.close()
    else:
        raise IOError( "process_txt_for_LaTeX: " +str(TXTpath)+ " did not point to a file!" )
        
def lines_from_file( fPath ): # Added , 2016-09-27 # <<< resenv
    """ Open the file at 'fPath' , and return lines as a list of strings """
    f = file( fPath , 'r' )
    lines = f.readlines()
    f.close()
    return lines
    
def string_from_file( fPath ): # <<< resenv
    """ Open the file at 'fPath' , and return the entire file as a single string """
    f = file( fPath , 'r' )
    fStr = f.read() # https://docs.python.org/2/tutorial/inputoutput.html#methods-of-file-objects
    f.close()
    return fStr
    
def txt_file_for_w( fPath ): return file( fPath , 'w' )  # <<< resenv
    
class accum: # <<< resenv
    """ Singleton text buffer object to hold script output, with facilities to write contents """
    
    totalStr = ""

    @staticmethod
    def prnt( *args ):
        """ Print args and store them in a string """
        for arg in args:
            accum.totalStr += str(arg) + " "
            print str(arg),
        print
        accum.totalStr += endl

    @staticmethod
    def accum_sep( title = "" , char = '=' , width = 6 , strOut = False ):
        """ Print a separating title card for debug """
        LINE = width * char
        if strOut:
            return LINE + ' ' + title + ' ' + LINE
        else:
            accum.prnt( LINE + ' ' + title + ' ' + LINE )
        
    @staticmethod
    def write( *args ):
        """ Store 'args' in the accumulation string without printing """
        for arg in args:
            accum.totalStr += str(arg) + " "
        accum.totalStr += endl

    @staticmethod
    def out_and_clear( outPath ):
        """ Write the contents of 'accum.totalStr' to a file and clear """
        outFile = file( outPath , 'w' )
        outFile.write( accum.totalStr )
        outFile.close()
        accum.totalStr = ""

# == End File ==

# == Batch Operations ==

def validate_dirs_writable(*dirList):
    """ Return true if every directory argument both exists and is writable, otherwise return false """
    # NOTE: This function exits on the first failed check and does not provide info for any subsequent element of 'dirList'
    # NOTE: Assume that a writable directory is readable
    for directory in dirList:
        if not os.path.isdir(directory):
            print "Directory",directory,"does not exist!"
            return False
        if not os.access(directory, os.W_OK): # URL, Check write permission: http://stackoverflow.com/a/2113511/893511
            print "System does not have write permission for",directory,"!"
            return False
    return True # All checks finished OK, return true

# == End Batch ==

# == String Processing ==

def strip_after_first( pStr , char ): # <<< resenv
    """ Return a version of 'pStr' in which the first instance of 'char' and everything that follows is removed, if 'char' exists in 'pStr', otherwise return 'pStr' """
    firstDex = pStr.find( char )
    if firstDex > -1:
        return pStr[:firstDex]
    return pStr
    
def tokenize_with_wspace( rawStr , evalFunc = str ): 
    """ Return a list of tokens taken from 'rawStr' that is partitioned with whitespace, transforming each token with 'evalFunc' """
    return [ evalFunc( rawToken ) for rawToken in rawStr.split() ]
    
def format_dec_list( numList , places = 2 ): # <<< resenv
    """ Return a string representing a list of decimal numbers limited to 'places' """
    rtnStr = "[ "
    for nDex , num in enumerate( numList ):
        if isinstance( numList , np.ndarray ):
            scalar = num.item()
        else:
            scalar = num 
        if nDex < len(numList) - 1:
            rtnStr += ('{0:.' + str(places) + 'g}').format(scalar) + ' , '
        else:
            rtnStr += ('{0:.' + str(places) + 'g}').format(scalar)
    rtnStr += " ]"
    return rtnStr
    
# == End Strings ==


# == Statistics ==

def itself( item ): return item # dummy function, return the argument itself # Added to ResearchEnv 2016-09-13
    
def accumulate(pLst , func=itself): # >>> resenv
    """ Return the sum of func(item) for all items in 'pLst'. Return the total number of non-list/tuple items in 'pLst'. Recursive """
    total = 0 # Accumulated total for results of 'func(item)'
    N = 0 # Number of items encountered
    for item in pLst: # for each item in the list
        if isinstance(item, (list,tuple)): # if the list item is itself an iterable
            partTot, partN = accumulate( item , func ) # recur on item
            total += partTot # Accumulate results from greater depth
            N += partN
        else: # else assume item is a number
            total += func( item ) # invoke 'func' on item and accumulate
            N += 1 # count the item
    return total, N # Return the accumulation total and the number of items

def avg(*args): # >>> resenv
    """ Average of args, where args can be numbers, a list, or nested lists """
    total, N = accumulate(args) # Accumulate a straight sum
    if N == 0:
        print "avg: Undefined for 0 items!"
        return None
    return float(total) / N # return mean
    
def variance(*args): # >>> resenv
    """ Variance of args, where args can be numbers, a list of numbers, or nested lists of numbere """
    total, N = accumulate(args) # calc mean
    if N == 0:
        print "variance: Undefined for 0 items!"
        return None
    print total , 
    mu = float(total) / N
    totSqDiffs , N = accumulate( args , lambda x: ( x - mu )**2 ) # calc the per-item variance
    print totSqDiffs
    return (1.0 / N) * totSqDiffs # return variance

def std_dev( *args ): # >>> resenv
    """ Standard deviation of args, where args can be numbers, a list of numbers, or nested lists of numbere """
    var = variance(*args)
    if var == None:
        print "std_dev: Undefined for 0 items!"
        return None
    return sqrt( var )
    
def percent_change( oldVal , newVal ):
    """ Return the precent change from 'oldVal' to 'newVal' , This version avoids div/0 errors """
    if eq( oldVal , 0 ): # If the old value is zero
        if eq( newVal , 0 ):
            return 0.0 # If both values are zero, no change
        else:
            return infty # else div/0 , undefined , return infinity
    return ( newVal - oldVal ) / oldVal * 100.0

# = Dice Rolls =

def normalize_die( distribution ): 
    """ Given relative odds, return partitions of a distribution on a number line from 0 to 1 """
    # This function assumes that all numbers in the distribution are positive
    total = sum( distribution ) # get the sum of all items
    normed = [ prob / total for prob in distribution ] # normalize the distribution
    accum = 0 # current partition boundary
    die = [] # monotonically increasing partitions for a dice roll
    for prob in normed: # Accumulate the total probability of sampling lesser than or equal to the partition
        accum += prob
        die.append( accum )
    return die # return partitions in [0,1]
    
def roll_die( distribution ): 
    """ Roll a die with a distribution of increasing values ending in 1 , as created by normalize_die """
    sample = random() # sample from a uniform distribution [0,1)
    i = 0 # index of the partition
    while distribution[i] < sample and i < len( distribution ): # while sample is greater than or equal to partition
        i += 1 # advance partition
    return i # This is the index of the least partition greater than the sample
    
def named_odds_to_distribution( oddsDict ):
    """ Unspool the 'oddsDict' into a pairing of ordered names and odds , then normalize the odds into a probability distribution """
    nameList = []
    distList = []
    for name , odds in oddsDict.iteritems():
        nameList.append( name )
        distList.append( odds )
    distList = normalize_die( distList )
    return ( tuple( nameList ) , tuple( distList ) )
    
def roll_for_outcome( namedDist ):
    """ Roll the die on an ordered ( ( NAMES ... ) , ( PROBS ... ) ) tuple with named outcomes and probabilities associated by index """
    return namedDist[0][ roll_die( namedDist[1] ) ] # Return the name corresponding with the index chosen by die roll

def sample_unfrm_real( rMin , rMax ):
    """ Sample from a uniform distribution [ rMin , rMax ) """
    span = abs( rMax - rMin )
    return random() * span + rMin

# = End Rolls =

def nCr( n , r ): 
    """ Number of combinations for 'n' Choose 'r' """
    return int( factorial( n ) / ( factorial( r ) * factorial( n - r ) ) )

# == End Stats ==