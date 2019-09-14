#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Template Version: 2017-05-30

"""
OGL_Shapes.py
James Watson , 2019 August
Primitive shapes and meshes to display in Pyglet / OpenGL 

Dependencies: numpy , pyglet , MARCHHARE
"""

"""
~~~~~ Development Plan ~~~~~

[ ] Add transform notes to the template, should only really be done when using the default mode
[ ] Vector array optimization ( See Drawable )

"""

# === Init =================================================================================================================================

# ~~ Helpers ~~


# ~~ Imports ~~
# ~ Standard ~
import sys , os
from math import sqrt , atan2 , sin , cos , pi
from random import randrange
# ~ Special ~
import numpy as np
import pyglet # --------- Package for OpenGL
# OpenGL flags and state machine
from pyglet.gl import ( GL_LINES , glColor3ub , GL_TRIANGLES , glTranslated , GL_QUADS , glRotated , glClearColor , glEnable ,
                        GL_DEPTH_TEST , glMatrixMode , GL_PROJECTION , glLoadIdentity , gluPerspective ,
                        GL_MODELVIEW , gluLookAt , GL_POINTS , glPointSize )
from pyglet.window import key

# ~ Local ~
from marchhare.VectorMath.HomogXforms import xform_points_np

from marchhare.Vector import vec_mag , vec_unit , vec_proj , vec_angle_between
from marchhare.VectorMath.Vector3D import vec_sphr
from marchhare.Utils3 import concat_arr

_DEBUG = False

# ==== Helper Functions ====

def origin_xform():
    """ Return the homogeneous coordinates of the origin """
    return np.array(
        [ [ 1 , 0 , 0 , 0 ] ,
          [ 0 , 1 , 0 , 0 ] ,
          [ 0 , 0 , 1 , 0 ] ,
          [ 0 , 0 , 0 , 1 ] ]
    )

def rand_color():
    """ Return a random (R,G,B) tuple in the range 0-255 """
    return (randrange(0,256),randrange(0,256),randrange(0,256),)

# ____ End Helper ____


# ==== OpenGL Classes ====
        
# === Drawable Classes ===

# == class OGLDrawable ==

class OGLDrawable( object ):
    """ Template class for drawing rigid objects in Pyglet and performing rigid transformations """
    
    def __init__( self ):
        self.xform    = origin_xform()
        self.vertices = []
        self.labVerts = []
        self.color    =  tuple( [  88 , 181 , 74 ] ) # Body color
        
    def set_verts( self , nVerts ):
        """ Store the vertices as `ndarray` """
        self.vertices = np.array( nVerts )
        
    def append_vert( self , nVert ):
        """ Add a vertex to the list """
        # NOTE: This function assumes that `vertices` is already an `np.ndarray`
        if len( self.vertices ) > 0:
            self.vertices = np.vstack(  ( self.vertices , nVert ,)  )
        else:
            self.set_verts( [ nVert ] )
        
    def xform_lab( self ):
        """ Transform all of the relative points into absolute points """
        self.labVerts = xform_points_np( self.vertices , self.xform )
        self.labVerts = self.labVerts.flatten()
        
    def set_color( self , clrTpl ):
        """ Set the color of the object """
        self.color = tuple( clrTpl )
    
    def draw( self ):  # VIRTUAL
        """ Render the INHERITED_CLASS """
        # ~~ Implementation Template ~~
        # 1. Transform points
        # self.xform_lab()
        # 2. Render! 
        # pyglet.graphics.draw_indexed( 
        #     10 , # ----------------- Number of seqential triplet in vertex list
        #     GL_LINES , # ----------- Draw quadrilaterals
        #     self.vectors[i] , # ---- Indices where the coordinates are stored
        #     ( 'v3f' , self.vertX ) # vertex list , OpenGL offers an optimized vertex list object , but this is not it
        # )
        # [4]. If OGL transforms enabled , Return the OGL state machine to previous rendering frame
        # self.state_untransform()
        raise NotImplementedError( "Please OVERRIDE: YOU RAN THE INHERITED VIRTUAL VERSION OF THE 'draw' function!" ) 
        
        
# __ end OGLDrawable __


# == class Point ==
     
class Point_OGL( OGLDrawable ):
    """ Visible representation of a 1D point """
    
    def __init__( self , pnt = [ 0 , 0 , 0 ] , size = 8 , color = ( 255 , 255 , 255 ) ):
        """ Define a single point """
        OGLDrawable.__init__( self ) #- Parent class init
        self.size    = size # --------- Width of point marker
        self.color   = tuple( color ) # Point marker color
        self.indices = tuple( [ 0 ] ) # Tuple of indices of 'vertX' that determine which are used to draw what parts of the geometry
        self.set_verts( [ pnt ] )
        
    def set_pos( self , pos ):
        """ Set the position of the point """
        self.set_verts( [ pos ] )
        
    def draw( self ):
        """ Render the point """
        # 1. Transform
        self.xform_lab()
        # 2. Set color and size
        glColor3ub( *self.color ) 
        glPointSize( self.size )
        # 3. Draw
        pyglet.graphics.draw_indexed( 
            1 , # --------------------- Number of seqential triplet in vertex list
            GL_POINTS , # ------------- Draw quadrilaterals
            self.indices , # ----------------- Indices where the coordinates are stored
            ( 'v3f' , self.labVerts ) # -- vertex list , OpenGL offers an optimized vertex list object , but this is not it
        )
        
# __ End Point __

# == class CartAxes ==

class CartAxes( OGLDrawable ):
    """ Standard set of Cartesian coordinate axes """
    # NOTE: At this time , will only draw the axes at the lab frame
    
    def __init__( self , origin = [ 0 , 0 , 0 ] , unitLen = 1.0 ):
        """ Set up the vertices for a coordinate axes """
        OGLDrawable.__init__( self  ) # ------------------------- Parent class init
        subLen = unitLen / 8.0 # Arrowhead 20% of the total length        
        
        self.set_verts( [# --------------------------------------------- Tuples of vertices that define the drawable geometry
           [       0 ,       0 ,       0 ],     # 0 , Orgn
           [ unitLen ,       0 ,       0 ],     # 1 , X vec / arw
           [       0 , unitLen ,       0 ],     # 2 , Y vec / arw
           [       0 ,       0 , unitLen ],     # 3 , Z vec / arw
           [ unitLen - subLen ,  subLen , 0 ],  # 4 , X arw
           [ unitLen - subLen , -subLen , 0 ],  # 5 , X arw 
           [ 0 , unitLen - subLen ,  subLen ],  # 6 , Y arw                   
           [ 0 , unitLen - subLen , -subLen ],  # 7 , Y arw
           [  subLen , 0 , unitLen - subLen ],  # 8 , Z arw
           [ -subLen , 0 , unitLen - subLen ]   # 9 , Z arw
        ] )
        # These indices are used to draw the individual 
        # components of the coordinate axes
        self.ndx_Xvec = ( 0 , 1 ) ; self.ndx_Xarw = ( 1 , 4 , 5 ) # ----- Tuple of indices of 'vertX' that determine the which are 
        self.ndx_Yvec = ( 0 , 2 ) ; self.ndx_Yarw = ( 2 , 6 , 7 ) #       used to draw what parts of the geometry
        self.ndx_Zvec = ( 0 , 3 ) ; self.ndx_Zarw = ( 3 , 8 , 9 )
        self.vectors = ( self.ndx_Xvec , self.ndx_Yvec , self.ndx_Zvec )
        self.arrows  = ( self.ndx_Xarw , self.ndx_Yarw , self.ndx_Zarw )
        
        self.colors  = ( ( 255 ,   0 ,   0 ) ,  # ----------------------- All of the colors used to paint the object
                         (   0 , 255 ,   0 ) ,  # R = X , G = Y , B = Z
                         (   0 ,   0 , 255 )  ) # by convention
        
    def draw( self ):
        """ Draw the axes """
        self.xform_lab()
        # 1. Set color , size , and shape-specific parameters
        pyglet.gl.glLineWidth( 3 )
        # [3]. Render! # Basis vectors are drawn one at a time in the conventional colors
        for i in range(3): # 
            glColor3ub( *self.colors[i] )
            # Draw the arrow tail
            pyglet.graphics.draw_indexed( 
                10 , # ------------------ Number of seqential triplet in vertex list
                GL_LINES , # ------------ Draw quadrilaterals
                self.vectors[i] , # ----- Indices where the coordinates are stored
                ( 'v3f' , self.labVerts ) #- Vertex list , OpenGL offers an optimized vertex list object , but this is not it
            )
            # Draw the arrow head
            pyglet.graphics.draw_indexed( 
                10 , # ------------------ Number of seqential triplet in vertex list
                GL_TRIANGLES , # -------- Draw quadrilaterals
                self.arrows[i] , # ------ Indices where the coordinates are stored
                ( 'v3f' , self.labVerts ) #- Vertex list , OpenGL offers an optimized vertex list object , but this is not it
            )
            
# __ End CartAxes __


# == class Vector ==
        
class Vector_OGL( OGLDrawable ):
    """ A directed line segment """
    
    lineWidth  = 4 # - "LineWidth" # --------- Line width 
    arwLenFrac = 0.2 # "ArrowLengthFraction" # Fraction of the vector length that the arrowhead occupies
    arwWdtFrac = 0.1 # "ArrowWidthFraction" #- Fraction of the vector length that the arrowhead extends perpendicularly to the vector
    arwLngtLim = 0.5 # "ArrowLengthLimit" # -- Hard limit on arrowhead length in units -OR- Constant arrowhead length
    arwWdthLim = 0.5 # "ArrowWidthLimit" # --- Hard limit on arrowhead width in units  -OR- Constant arrowhead width
    
    @classmethod
    def set_vec_props( cls , **kwargs ):
        """ Set the visual properties of all the 'Vector_OGL' that will be subsequently created """
        if "LineWidth" in kwargs:
            cls.lineWidth  = kwargs["LineWidth"]
        if "ArrowLengthFraction" in kwargs:
            cls.arwLenFrac = kwargs["ArrowLengthFraction"]
        if "ArrowWidthFraction" in kwargs:
            cls.arwWdtFrac = kwargs["ArrowWidthFraction"]
        if "ArrowLengthLimit" in kwargs:
            cls.arwLngtLim = kwargs["ArrowLengthLimit"]
        if "ArrowWidthLimit" in kwargs:
            cls.arwWdthLim = kwargs["ArrowWidthLimit"]
    
    def set_origin_displace( self , origin , vec ):
        """ Set the vector so that it begins at 'origin' and has 'offset' """
        thisCls = self.__class__
        
        self.origin = origin
        self.offset = vec
        self.color  = ( 125 , 125 , 125 )
        
        # print "DEBUG , origin _______________________________________ :" , origin
        # print "DEBUG , np.multiply( vec , ( 1 - thisCls.arwLenFrac ) ):" , np.multiply( vec , ( 1 - thisCls.arwLenFrac ) )
        
        drct80 = np.add( origin , np.multiply( vec , ( 1 - thisCls.arwLenFrac ) ) )
        
        if vec_mag( drct80 ) * thisCls.arwLenFrac > thisCls.arwLngtLim:
            drct80 = np.add( origin , np.multiply( vec , ( 1 - thisCls.arwLngtLim / vec_mag( drct80 ) ) ) )
        totalV = np.add( origin , vec )
        vecLen = vec_mag( vec )
        subLen = vecLen * thisCls.arwWdtFrac 
        hd1dir = vec_unit( np.cross( vec , [ 1 , 0 , 0 ] ) )
        hd2dir = vec_unit( np.cross( vec , hd1dir        ) )
        pointA = np.add( drct80 , np.multiply( hd1dir ,  subLen ) )
        pointB = np.add( drct80 , np.multiply( hd1dir , -subLen ) )
        pointC = np.add( drct80 , np.multiply( hd2dir ,  subLen ) )
        pointD = np.add( drct80 , np.multiply( hd2dir , -subLen ) )
        
        self.set_verts( [ # --------------------------------------------- Tuples of vertices that define the drawable geometry
            [origin[0] , origin[1] , origin[2]] , # 0. Vector Tail
            [totalV[0] , totalV[1] , totalV[2]] , # 1. Vector Head
            [pointA[0] , pointA[1] , pointA[2]] , # 2. Fletching 1 Side 1
            [pointB[0] , pointB[1] , pointB[2]] , # 3. Fletching 1 Side 2
            [pointC[0] , pointC[1] , pointC[2]] , # 4. Fletching 2 Side 1
            [pointD[0] , pointD[1] , pointD[2]] , # 5. Fletching 2 Side 2
        ] )
        
        self.ndx_vctr = ( 0 , 1 )
        self.ndx_flt1 = ( 1 , 2 , 3 )
        self.ndx_flt2 = ( 1 , 4 , 5 )
        self.fltchngs = [ self.ndx_flt1 , self.ndx_flt2 ]
    
    def __init__( self , origin = [ 0 , 0 , 0 ] , vec = [ 1 , 0 , 0 ] ):
        """ Set up the vertices for the vector """
        OGLDrawable.__init__( self) # ------------------------- Parent class init
        
    def draw( self ):
        """ Draw the Vector """
        self.xform_lab()
        # [2]. Set color , size , and shape-specific parameters
        pyglet.gl.glLineWidth( self.__class__.lineWidth )
        # [3]. Render! # Basis vectors are drawn one at a time in the conventional colors
        glColor3ub( *self.color ) # There is only one color
        # Draw the vector shaft
        pyglet.graphics.draw_indexed( 
            6 , # ------------------ Number of seqential triplet in vertex list
            GL_LINES , # ------------ Draw quadrilaterals
            self.ndx_vctr , # ----- Indices where the coordinates are stored
            ( 'v3f' , self.labVerts ) #- Vertex list , OpenGL offers an optimized vertex list object , but this is not it
        )
        # Draw the fletchings
        for i in range( len( self.fltchngs ) ): 
            pyglet.graphics.draw_indexed( 
                6 , # ------------------ Number of seqential triplet in vertex list
                GL_TRIANGLES , # -------- Draw quadrilaterals
                self.fltchngs[i] , # ------ Indices where the coordinates are stored
                ( 'v3f' , self.labVerts ) #- Vertex list , OpenGL offers an optimized vertex list object , but this is not it
            )
        
# __ End Vector __


# == class Trace_OGL ==

class Trace_OGL( OGLDrawable ):
    """ A persistent collection of segments drawn end-to-end """
    
    def __init__( self ):
        OGLDrawable.__init__( self) # ------------------------- Parent class init
        self.lineWidth  = 2 # - "LineWidth" # --------- Line width
        self.indices    = []
        
    def add_point( self , pnt ):
        """ Add a point to the end of the trace, creating a new segment after the first point """
        self.append_vert( pnt )
        if len( self.vertices ) > 1:
            self.indices.extend( [ len( self.vertices ) - 2 , len( self.vertices ) - 1 ] )
        
    def draw( self ):
        """ Draw the trace """
        # 1. Transform points
        self.xform_lab()
        # 2. Set line width and color
        pyglet.gl.glLineWidth( self.lineWidth )
        glColor3ub( *self.color ) # There is only one color
        # 3. Render!
        pyglet.graphics.draw_indexed( 
            len( self.vertices ) , # -- Number of seqential triplet in vertex list
            GL_LINES , # -------------- Draw segments
            tuple( self.indices ) , # - Indices where the coordinates are stored
            ( 'v3f' , self.labVerts ) # Vertex list , OpenGL offers an optimized vertex list object , but this is not it
        )
    
# __ End Trace_OGL __


# == Rendering Classes ==

class CameraOrbit:
    """ Represent a camera that orbits a point of interest """
    
    def __init__( self, POI = [0,0,0] , radius = 1.0 , theta = 0.0 , psi = 0.0 ):
        """ Initialize a camera position """
        self.center = POI 
        self.r      = radius 
        self.th     = theta 
        self.ps     = psi
        self.up     = [ 0.0 , 0.0 , 1.0 ]
        self.dTheta = pi / 16
        self.dPsi   = pi / 16
        self.dR     = 0.05
        
    def get_camera_position( self ):
        """ Get the camera position associated with the present params """
        return np.add( self.center , vec_sphr( self.r , self.th , self.ps ) )
    
    def get_cam_vectors( self ):
        """ Return the vectors needed to specify the camer view """
        if _DEBUG: print( "Pos:" , self.get_camera_position() , "Cen:" , self.center , "Up:" , self.up )
        return self.get_camera_position() , self.center , self.up
        
    def orbit_pos( self ): self.th += self.dTheta
    def orbit_neg( self ): self.th -= self.dTheta
    def angle_inc( self ): self.ps += self.dPsi
    def angle_dec( self ): self.ps -= self.dPsi
    def zoom_in( self ): self.r -= self.dR
    def zoom_out( self ): self.r += self.dR
    
    def attach_controls( self , window ):
        @window.event
        def on_key_press( symbol , modifiers ):
            # Handle Keyboard Events
            if symbol == key.LEFT:
                self.orbit_neg()
                if _DEBUG: print( "Theta:" , cam.th )
            
            if symbol == key.RIGHT:
                self.orbit_pos()
                if _DEBUG: print( "Theta:" , cam.th )
            
            if symbol == key.UP:
                self.angle_inc()
                if _DEBUG: print( "Psi:" , cam.ps )
            
            if symbol == key.DOWN:
                self.angle_dec()
                if _DEBUG: print( "Psi:" , cam.ps )
            
            # Alphabet keys:
            elif symbol == key.O:
                self.zoom_out()
                if _DEBUG: print( "d:" , cam.r )
                
            elif symbol == key.P:
                self.zoom_in()
                if _DEBUG: print( "d:" , cam.r )

            # Number keys:
            elif symbol == key._1:
                pass

            # Number keypad keys:
            elif symbol == key.NUM_1:
                pass

            # Modifiers:
            if modifiers & key.MOD_CTRL:
                pass

# __ End Render __


# == class OGL_App ==
        
class OGL_App( pyglet.window.Window ):
    """ Bookkeepping for Pyglet rendering """
    
    def __init__( self , drawSpec = [] , caption = 'Pyglet Rendering Window' , dispWidth = 640 , dispHeight = 480 , 
                  clearColor = [ 0.7 , 0.7 , 0.8 , 1 ] ):
        """ Instantiate the environment with a list of objhects to render """
        super( OGL_App , self ).__init__( resizable = True , caption = caption ,  width = dispWidth , height = dispHeight )
        glClearColor( *clearColor ) # Set the BG color for the OGL window
        
        # URL: https://www.opengl.org/discussion_boards/showthread.php/165839-Use-gluLookAt-to-navigate-around-the-world
        self.camera = [  2 ,  2 ,  2 , # eyex    , eyey    , eyez    : Camera location , point (world) , XYZ
                         0 ,  0 ,  0 , # centerx , centery , centerz : Center of the camera focus , point (world) , XYZ
                         0 ,  0 ,  1 ] # upx     , upy     , upz     : Direction of "up" in the world frame , vector , XYZ
        
        # Determine if we are drawing a list of objects or using a custom function
        if type( drawSpec ).__name__ == 'function':
            self.customDraw = True
            self.drawFunc   = drawSpec
            self.renderlist = None
        else:
            self.renderlist = objList
            self.customDraw = False
            self.drawFunc   = None
        
        self.showFPS    = False
        self.yFOV       = 70 # FOV, in degrees, in the y direction.
        self.aspect     = self.width / float( self.height )  # The aspect ratio is the ratio of x (width) to y (height)
        self.nearClipZ  = 0.1 # distance from the viewer to the near clipping plane (always positive)
        self.farClipZ   = 200 # distance from the viewer to the far clipping plane (always positive)
        
    def set_custom_draw( self , func ):
        """ Set a custom draw function """
        self.customDraw = True
        self.drawFunc   = func
        
    def set_camera( self , cameraLocationPnt , lookAtPoint , upDirection ):
        """ Specify the camera view """
        if ( len( cameraLocationPnt ) != 3 or len( lookAtPoint ) != 3 or len( upDirection ) != 3 ):
            raise IndexError( "OGL_App.set_camera: All parameters must be 3D vectors" )
        self.camera = concat_arr( cameraLocationPnt , # eyex    , eyey    , eyez    : Camera location , point (world) , XYZ
                                  lookAtPoint , #       centerx , centery , centerz : Center of the camera focus , point (world) , XYZ
                                  upDirection ) #       upx     , upy     , upz     : Direction of "up" in the world frame , vector , XYZ
        
    def set_view_params( self , yFOV , nearClipZ , farClipZ ):
        """ Set the camera fustrum parameters """
        self.yFOV      = yFOV # ---- FOV, in degrees, in the y direction.
        self.nearClipZ = nearClipZ # distance from the viewer to the near clipping plane (always positive)
        self.farClipZ  = farClipZ #- distance from the viewer to the far clipping plane (always positive)
        
    def get_view_vectors( self ):
        """ Get the vectors that pertain to the camera """
        return self.camera[:3] , self.camera[3:6] , self.camera[6:]
        
    def prnt_view_params( self ):
        """ Print the view params to stdout """
        print( "FOV:" , self.yFOV , ", Near Clip:" , self.nearClipZ , ", Far Clip" , self.farClipZ )
     
    def p_point_visible( self , pnt ):
        """ Return True if the point is in the view fustrum, otherwise return False """
        withinView = True
        reasons    = []
        # 0. Fetch camera vectors
        cntr , lookPnt , up = self.get_view_vectors()
        # 1. Get relevant distances
        pntVec = np.subtract( pnt , cntr )
        lookDir = vec_unit( np.subtract( lookPnt , cntr ) )
        sideDir = vec_unit( np.cross( up , lookDir ) )
        upDir   = vec_unit( np.cross( lookDir , sideDir ) )
        d_view  = vec_proj( pntVec , lookDir )
        d_up    = vec_proj( pntVec , upDir )
        d_side  = vec_proj( pntVec , sideDir )
        # 2. Calc relevant angles
        ang_y = abs( atan2( d_up   , d_view ) )
        ang_x = abs( atan2( d_side , d_view ) )
        
        # 1. Check FOV_y
        if ang_y > self.yFOV:
            withinView = False
            reasons.append( "FOV_y" )
        
        # 2. Calc and check FOV_x
        xFOV = self.yFOV * self.aspect
        if ang_x > xFOV:
            withinView = False
            reasons.append( "FOV_x" )
            
        # 3. Check far clip
        if d_view > self.farClipZ:
            withinView = False
            reasons.append( "Clip_Far" )
        
        # 4. Check near clip
        if d_view < self.nearClipZ:
            reasons.append( "Clip_Near" )
        
        # 5. Return
        return ( withinView , tuple( reasons ) )
    
    def point_in_view( self , pnt ):
        """ Return information about the point in the camera view """
        # 0. Fetch camera vectors
        cntr , lookPnt , up = self.get_view_vectors()
        # 1. Get relevant distances
        pntVec = np.subtract( pnt , cntr )
        lookDir = vec_unit( np.subtract( lookPnt , cntr ) )
        sideDir = vec_unit( np.cross( up , lookDir ) )
        upDir   = vec_unit( np.cross( lookDir , sideDir ) )
        d_view  = vec_proj( pntVec , lookDir )
        d_up    = vec_proj( pntVec , upDir )
        d_side  = vec_proj( pntVec , sideDir )
        # 2. Calc relevant angles
        ang_y = abs( atan2( d_up   , d_view ) )
        ang_x = abs( atan2( d_side , d_view ) )
        
        return {
            'dist'    : vec_mag( np.subtract( pnt , cntr ) ) ,
            'visible' : self.p_point_visible( pnt ) ,
            'x' : self.nearClipZ * sin( ang_x ) ,
            'y' : self.nearClipZ * sin( ang_y ) ,
            'angle' : vec_angle_between( lookDir , pntVec )
        }
        
     
    def calc_aspect_from_win( self ):
        """ Recalculate the aspect ratio and store """
        self.aspect = self.width / float( self.height )
        
    def setup_3D( self ):
        """ Setup the 3D matrix """
        # ~ Modes and Flags ~
        # Use 'GL_DEPTH_TEST' to ensure that OpenGL maintains a sensible drawing order for polygons no matter the viewing angle
        glEnable( GL_DEPTH_TEST ) # Do these setup functions really have to be run every single frame? # TODO: Try moving these to the '__init__' , see what happens
        # glEnable( GL_CULL_FACE ) # Uncomment to preform backface culling # This might erase arrowheads if they are away-facing!
        # ~ View Frustum Setup ~
        glMatrixMode( GL_PROJECTION )
        glLoadIdentity()
        # Camera properties
        self.calc_aspect_from_win()
        gluPerspective( self.yFOV , # FOV, in degrees, in the y direction.
                        self.aspect , # The aspect ratio is the ratio of x (width) to y (height)
                        self.nearClipZ , # distance from the viewer to the near clipping plane (always positive)
                        self.farClipZ ) # distance from the viewer to the far clipping plane (always positive)
        # ~ View Direction Setup ~
        glMatrixMode( GL_MODELVIEW )
        glLoadIdentity()
        gluLookAt( *self.camera )
            
    def on_draw( self ):
        """ Repaint the window , per-frame activity """
        # 0. Erase last frame
        self.clear()
        # 1. Set up camera in projection mode
        self.setup_3D()
        # 2. Draw geometry in model mode
        # Option 1: Draw each object in sequence (Note that this option does not easily allow nested transforms)
        if not self.customDraw:
            for obj in self.renderlist:
                obj.draw()
        # Option 2: Invoke a user-defined function (Allows aribtrary complexity including transforms)
        else:
            self.drawFunc()
        if self.showFPS:
                print( "FPS:" , pyglet.clock.get_fps() ) # Print the framerate

# __ End OGL_App __


# URL , Spatial Transforms: http://drake.mit.edu/doxygen_cxx/group__multibody__spatial__pose.html

if __name__ == "__main__":
    print( "~~~ OGL Tests ~~~" )
    foo = OGLDrawable()
    foo.set_verts( [ [1,2,3] ] )
    foo.xform_lab()
    print( foo.labVerts )