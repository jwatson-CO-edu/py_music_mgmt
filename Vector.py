#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

"""
Vector.py , Built on Spyder for Python 2.7
Erik Lindstrom , Adam Sperry , James Watson, 2016 October
Vectors, Turns, Frames, and common operations in 2D geometry

== LOG ==


== TODO ==

"""

# ~ Standard Libraries ~
import Tkinter
from math import sqrt, cos, sin, radians, acos, pi, atan2, asin, e
from numbers import Number # for checking if a thing is a NumberR3triple
from copy import deepcopy
from random import random
# ~ Special Libraries ~
import numpy as np
# ~ Local Libraries ~
from AsmEnv import PriorityQueue , elemw , format_dec_list , eq_margin , round_small 

# set_dbg_lvl(1) # Transformation of objects contained in Frames

# ~~ Constants , Shortcuts , Aliases ~~
EPSILON = 1e-7
infty = 1e309 # URL: http://stackoverflow.com/questions/1628026/python-infinity-any-caveats#comment31860436_1628026

# === Vector Mathematics ===

def vec_mag(vec): # <<< resenv
    """ Return the magnitude of a vector """
    return np.linalg.norm(vec)
    
def vec_sqr( vec ): # TODO: ADD TO RESENV
    """ Return the squared magnitude of the vector (avoid sqrt for quick comparison) """
    return np.dot( vec , vec ) # The squared magnitude is just the vector dotted with itself
    
def vec_dif_sqr( vec1 , vec2 ): # TODO: ADD TO RESENV
    """ Return the squared magnitude of the vector difference between 'vec1' and 'vec2' """
    vecDiff = np.subtract( vec1 , vec2 )
    return np.dot( vecDiff , vecDiff ) # The squared magnitude is just the vector dotted with itself
    
def vec_dif_mag( vec1 , vec2 ):
    """ Return the magnitude of the vector difference between 'vec1' and 'vec2' """
    return vec_mag( np.subtract( vec1 , vec2 ) )
    
def vec_dif_unt( vec1 , vec2 ):
    """ Return the unit of the vector difference between 'vec1' and 'vec2' """
    return vec_unit( np.subtract( vec1 , vec2 ) )

def vec_zeros( dim ):
    """ Return a vector of 'dim' zeros """
    return [ 0 for d in xrange( dim ) ]

def vec_round_small( vec ): 
    """ Round components that are have an absolute value less than 'EPSILON' to 0 """
    rtnVec = []
    for i in range( len( vec ) ):
        rtnVec.append( round_small( vec[i] ) )
    return rtnVec
        
def vec_unit(vec): # <<< resenv
    """ Return a unit vector in the direction of 'vec', using numpy """
    return np.divide( vec , np.linalg.norm(vec) )

def vec_proj( a , b ): # <<< resenv
    """ a projected onto b, a scalar length, using numpy """
    return np.dot(a,b) / np.linalg.norm(b) # Note that the result will be negative if the angle between a and b is > pi/2
    
def vec_proj_onto( a , b ): # <<< resenv
    """ a projected onto b,  vector in the direction of b """
    return np.multiply( vec_unit( b ) , vec_proj( a , b ) )
    
def vec_angle_between( v1 , v2 ): # <<< resenv
    """ Returns the angle in radians between vectors 'v1' and 'v2' """
	# URL, angle between two vectors: http://stackoverflow.com/a/13849249/893511
    v1_u = vec_unit(v1)
    v2_u = vec_unit(v2)
    angle = np.arccos(np.dot(v1_u, v2_u))
    if np.isnan(angle):
        if (v1_u == v2_u).all():
            return 0.0
        else:
            return np.pi
    return angle
    
def vec_parallel( v1 , v2 ):
    """ Return true if 'v1' and 'v2' are parallel within EPSILON, false otherwise """
    angle = vec_angle_between( v1 , v2 )
    return eq( angle , 0.0 ) or eq( angle , pi )

def np_add(*args): # <<< resenv
    """ Perform 'np.add' on more than two args """
    if len(args) > 2: # If there are more than 2 args, add the first arg to recur on remainder of args
        return np.add( args[0] , np_add(*args[1:]) ) # Note the star operator is needed for recursive call, unpack to positional args
    else: # base case, there are 2 args*, use vanilla 'np.add'
        return np.add( args[0] , args[1] ) # *NOTE: This function assumes there are at least two args, if only 1 an error will occur

def np_subtract(*args): # <<< resenv
    """ Perform 'np.subtract' on more than two args """
    if len(args) > 2: # If there are more than 2 args, subtract the last arg from the preceeding remainder of args
        return np.subtract( np_subtract(*args[:-1]) , args[-1] ) # Note the star operator is needed for recursive call, unpack to positional args
    else: # base case, there are 2 args*, use vanilla 'np.subtract'
        return np.subtract( args[0] , args[1] ) # *NOTE: This function assumes there are at least two args, if only 1 an error will occur
        
def vec_sum_chain(vecList): # <<< resenv
    """ Create a list of vectors that are the resultants of summing correspong vector in 'vecList' and all preceding vectors """
    ptsList = [ vecList[0][:] ] # first vector is the same as first in 'vecList'
    for i in range(1,len(vecList)): # for every successive vector
        ptsList.append( np.add( ptsList[-1] , vecList[i] ) )
    return ptsList

def vec_eq( vec1 , vec2 , margin = EPSILON ): # <<< resenv
    """ Return true if two vectors are equal enough, otherwise false """
    if len(vec1) == len(vec2):
        for i in range(len(vec1)):
            if not eq_margin( vec1[i] , vec2[i] , margin):
                return False
    else:
        return False
    return True

def vec_eq_test_w_margin( margin = EPSILON ):
    """ Return a function that performs an 'vec_eq' comparison with the specified margin """
    def eq_test( op1 , op2 ):
        return vec_eq( vec1 , vec2 , margin )
    return eq_test
    
def vec_linspace( vec1 , vec2, numPts ): # <<< resenv
    """ Return a list of 'numPts' points (vectors) evenly spaced from 'vec1' to 'vec2', inclusive """
    diff = np.subtract( vec2 , vec1 ) # Vector from point 1 to point 2
    direction = vec_unit( diff ) # Direction of the vector between the two
    span = vec_mag( diff ) # the Euclidian distance between the two points
    ptsList = [] 
    for value in np.linspace(0, span, num=numPts): # For each value in the range
        ptsList.append( np.add( vec1 , # append the sum of the first point and
                                np.multiply( direction , # a vector that is an additional space along the difference
                                             value ) ) )
    return ptsList
    
def vec_avg( *vectors ): # <<< resenv
    """ Return a vector that is the average of all the 'vectors', equal weighting """
    vecSum = np_add( *vectors ) # NOTE: This function assumes that all vectors are the same dimensionality
    return np.divide( vecSum , len(vectors) * 1.0 )

def is_vector( vec ): # <<< resenv
    """ Return true if 'vec' is any of { list , numpy array } and thus may particpate in vector operations """
    return isinstance( vec , ( list , np.ndarray ) )
    
def vec_copy( vec ): # <<< resenv
    """ Return a copy of 'vec', using the appropriate copy mechanism for the underlying datatype """
    if isinstance( vec , list ): 
        return vec[:] 
    elif isinstance( vec , np.ndarray ):
        return vec.copy()
    else:
        raise TypeError("vec_copy: " + str(vec) + " was neither a 'list' nor a 'np.ndarray'!")
    
def vec_copy_deep( vec ): # <<< resenv
    """ Return a deep copy of 'vec', using the appropriate copy mechanism for the underlying datatype """
    if isinstance( vec , list ): 
        return deepcopy( vec )
    elif isinstance( vec , np.ndarray ):
        return vec.copy()
    else:
	raise TypeError("vec_copy_deep: " + str(vec) + " was neither a 'list' nor a 'np.ndarray'!")
 
def vec_random( dim ): # <<< resenv
    """ Return a random vector in R-'dim' space with coordinates in [0,1) """
    rtnVec = []
    for i in range(dim):
        rtnVec.append( random() )
    return rtnVec
    
def vec_random_range( dim , limLo , limHi ): # <<< resenv
    """ Return a vector in which each element takes on a random value between 'limLo' and 'limHi' with a uniform distribution """
    rtnVec = []
    randVec = vec_random( dim )
    span = abs( limHi - limLo )
    for elem in randVec:
        rtnVec.append( elem * span + limLo )
    return rtnVec

def vec_random_limits( dim , limits ): # <<< resenv
    """ Return a vector in which each element takes on a random value between 'limits[i][0]' and 'limits[i][1]' with a uniform distribution """
    rtnVec = []
    randVec = vec_random( dim )
    for i , elem in enumerate( randVec ):
        span = abs( limits[i][1] - limits[i][0] )
        rtnVec.append( elem * span + limits[i][0] )
    return rtnVec
    
def vec_random_perturb( center , radius ): # <<< resenv
    """ Return a vector perturbed by length 'radius' away from 'center' in a random direction """
    randDir = vec_unit( vec_random( len( center ) ) ) # Construct a random unit vector with the same dimensionality as 'center'
    offset = np.multiply( randDir , radius )
    return np.add( center , offset )
        
def vec_round( vec , places=0 ): # <<< resenv
    """ Round each element of 'vec' to specified 'places' """
    rtnVec = []
    for elem in vec:
        rtnVec.append( round( elem , places ) )
    return rtnVec
    
def vec_clamp( vec , loBnd , upBnd ): # <<< resenv
    """ Return a version of 'vec' with all elements clamped b/n ['loBnd' , 'upBnd'], inclusive """
    rtnVec = []
    for coord in vec:
        if coord < loBnd:
            rtnVec.append( loBnd )
        elif coord > upBnd:
            rtnVec.append( upBnd )
        else:
            rtnVec.append( coord )
    return rtnVec

def vec_clamp_fraction( vec , loBnd , upBnd ): # <<< resenv
    mid = (upBnd + loBnd) / 2
    scales = []
    for i , elem in enumerate( vec ):
        if elem <= mid: # If the angle is less than 'mid', then scale
            scales.append( abs( ( mid - elem ) / ( mid - loBnd ) ) )
        else: # else angle greater than mid, scale
            scales.append( abs( ( elem - mid ) / ( upBnd - mid ) ) )
    return scales
    
def vec_scaled_clamp( vec , loBnd , upBnd ): # <<< resenv
    """ If any element of 'vec' is out of bounds, return a scaled copy of 'vec' such that the most-offending element is within bounds, or return 'vec' """
    if not vec_check_bounds( vec , loBnd , upBnd ):
        return np.divide( vec , max( vec_limit_fraction( vec , loBnd , upBnd ) ) )
    else:
        return vec
    
def vec_check_bounds( vec , loBnd , upBnd ): # <<< resenv
    """ Return true if all elements  of 'vec' are b/n ['loBnd' , 'upBnd'], inclusive """
    for coord in vec:
        if coord < loBnd:
            return False
        elif coord > upBnd:
            return False
    return True
    
def vec_check_limits( vec , limits ): # <<< resenv
    """ Return True of 'vec' [x_0 ... x_N] falls within 'limits' ( ( x0min , x0max ) ... ( xNmin , xNmax ) ) , otherwise false """
    for i , lim in enumerate(limits):
        if vec[i] < lim[0]:
            return False
        elif vec[i] > lim[1]:
            return False
    return True

def vec_limit_fraction( vec , limits ): # <<< resenv
    scales = []
    for i , elem in enumerate( vec ):
        mid = ( limits[i][0] + limits[i][1] ) / 2
        if elem <= mid: # If the angle is less than 'mid', then scale
            scales.append( abs( ( mid - elem ) / ( mid - limits[i][0] ) ) )
        else: # else angle greater than mid, scale
            scales.append( abs( ( elem - mid ) / ( limits[i][1] - mid ) ) )
    return scales

def vec_scaled_limits( vec , limits ): # <<< resenv
    """ If any element of 'vec' is out of bounds, return a scaled copy of 'vec' such that the most-offending element is within bounds, or return 'vec' """
    if not vec_check_limits( vec , limits ):
        return np.divide( vec , np.absolute( vec_limit_fraction( vec , limits ) ) )
    else:
        return vec
    
def vec_from_seg( segment ):
    """ Return the vector that points in the direction from point 'segment[0]' to 'segment[1]' """
    return np.subtract( segment[1] , segment[0] )

def bbox_from_points( ptsList ):
    """ Return the axis-aligned bounding box that contains all of 'ptsList' , Takes the form [ [ VEC_OF_MINS ... ] , [ VEC_OF_MAXS ... ] ] """
    bbox = [ [ infty for i in ptsList[0] ] , [ -infty for i in ptsList[0] ] ] # NOTE: This function assumes that all points have the same dimensionality
    for point in ptsList: # For every point in the list
        for i in xrange( len( point ) ): # For every dimension of the point
            bbox[0][i] = min( bbox[0][i] , point[i] ) # Compare the component of the point to the min of the dimension
            bbox[1][i] = max( bbox[1][i] , point[i] ) # Compare the component of the point to the max of the dimension
    return bbox

# == Plotting Helpers ==

def split_to_components( vecList ): 
    """ Separate a list of R^n vectors into a list of n lists of components , in order """ # because matplotlib likes it that way
    components = [ [] for dim in xrange( len( vecList[0] ) ) ] # NOTE: This function assumes that all vectors of 'vecList' are the same dimensionality
    for vec in vecList:
        for i , elem in enumerate( vec ):
            components[i].append( elem )

# == End Helpers ==

# = Drawing Init =    # ARE THESE USED? SEE IF REMOVING THEM BREAKS SOMETHING
def attach_geometry(rootFrame, pCanvas): # <<< resenv
    """ Traverse geometry from the root frame to the all subframes, recursively, attaching all drawable geometry to canvas """
    for obj in rootFrame.objs:
        obj.attach_to_canvas( pCanvas )
    for frame in rootFrame.subFrames:
        attach_geometry( frame , pCanvas )
        
def attach_transform( rootFrame, pTransform ): # <<< resenv
    """ Traverse geometry from the root frame to the all subframes, recursively, attaching a coordinate transformation to each drawable """
    for obj in rootFrame.objs:
        obj.transform = pTransform
    for frame in rootFrame.subFrames:
        attach_transform( frame , pTransform )
        
def color_all(rootFrame, pColor): # <<< resenv
    """ Traverse geometry from the root frame to the all subframes, recursively, setting all graphics to 'pColor' """
    if 'colorize' in rootFrame.__dict__:
        rootFrame.colorize(pColor)
    else:
        for obj in rootFrame.objs:
            obj.set_color( pColor )   
    for frame in rootFrame.subFrames:
        color_all( frame , pColor )
# = End Drawing =        
# == End Frames ==
        
# TODO : Consider whether having a parent class geometric object would overcomplicate things

""" NOTES: In a previous implementation, every geometrical object was essentially a Frame that could contain other objects
           that could be nested indefinitely. That probably overcomplicated things a great deal. For now will only consider
           a line segment to be just that, and not represent anything greater than a straight connection between two points. 
           
           For now, not considering a point to be its own class. A point can be just a simple triple represented with np.ndarray 
           
           For now, leaving all the Tkinter stuff inside the geometry classes, even though I would like geometry and its calculations
           to remain separate from drawing. These have to be linked in some way to be useful, at any rate. """

# == class Segment ==

class Segment(object): # <<< resenv
    """ A line segment to be displayed on a Tkinter canvas """ # TODO: * Generalize for any display?
#                                                                      * Consider extending this class for particular displays?

    def __init__(self , pCoords = None , TKcanvas=None , color=None): # candidate super signature
        """ Assign vars and conditionally create the canvas object 'self.drawHandle' """
        self.transform = self.dummy_transform # Optionally change this for a different rendering engine
        self.display_xform = self.scaled_coords_to_list
        self.displayScale = 1 # /4.0
        #                    v--- Need to make a copy here, otherwise relative coords will be transformed
        self.coords = vec_copy_deep( pCoords ) if pCoords else [ [0.0 , 0.0] , [0.0 , 0.0] ] # Coordinates expressed in the parent reference Frame
        # Coordinates expressed in the lab frame, used for drawing and lab frame calcs
        self.labCoords = vec_copy_deep( pCoords ) if pCoords else [ [0.0 , 0.0] , [0.0 , 0.0] ] 
        self.canvas = None
        if TKcanvas: # If canvas is available at instantiation, go ahead and create the widget
            self.canvas = TKcanvas
            self.drawHandle = TKcanvas.create_line( self.coords[0][0] , self.coords[0][1] , self.coords[1][0] , self.coords[1][1])
            if color:
                self.canvas.itemconfig(self.drawHandle,fill=color)
        self.hidden = False

    def __str__(self):
        """ Return the endpoints of the Segment as a String """
        return str( self.coords )

    # = Drawing Methods =
    
    def old_dummy_transform(self, pntList, scale): # candidate super fuction
        """ Dummy coordinate transformation, to be replaced with whatever the application calls for """
        print "OLD DUMMY CALLED , FIND OUT WHY!"
        rtnList = []
        for pnt in pntList:
            rtnList.extend( pnt )
        return rtnList # no actual transformation done to coords
        
    def scaled_coords_to_list( self , coords , scale = 1 ):
        """ Unravel lab coord pairs as [ x_1 , y_1 , ... , x_n , y_n ] """
        rtnList = []
        for pair in coords:
            rtnList.extend( np.multiply( pair , scale ) ) # FIXME: Scaling this twice seems redundant
        return rtnList 
        
    def dummy_transform(self, pntList, scale): # candidate super fuction
        """ Dummy coordinate transformation, to be replaced with whatever the application calls for """
        return pntList 
    
    def set_color(self, color): # candidate super functions
        """ Set the 'color' of the line """
        self.canvas.itemconfig(self.drawHandle,fill=color)
        self.canvas.itemconfig(self.drawHandle, width=3)
        
    def attach_to_canvas(self, TKcanvas): # candidate super function
        """ Given a 'TKcanvas', create the graphics widget and attach it to the that canvas """
        self.drawHandle = TKcanvas.create_line( -10 , -10 , -5 , -5 ) # Init to dummy coords x1, y1 , x2 , y2
        self.canvas = TKcanvas
            
    def update(self): # candidate super function
        """ Update the position of the segment on the canvas """
        temp1 = self.transform( self.labCoords, self.displayScale ) # Project 3D to 2D
        temp2 = self.display_xform( temp1 , 1 )
        self.canvas.coords( self.drawHandle , *temp2 ) 
        
    def set_hidden( self , hidden ):
        """ Set this line Segment hidden (True) or visible (False) """
        self.hidden = hidden
        if hidden:
            self.canvas.itemconfig( self.drawHandle , state=Tkinter.HIDDEN )
        else:
            self.canvas.itemconfig( self.drawHandle , state=Tkinter.NORMAL )

    # = End Drawing =

# == End Segment ==
        
# === End Geometry ===