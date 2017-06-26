#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division

"""
Graph.py , Built on Spyder for Python 2.7
James Watson, 2017 March
General purpose graph classes and methods
"""

# ~~ Libraries ~~
# ~ Standard ~
import collections , sys 
# ~ Special ~
# ~ Local ~

if "CV_Utils" not in sys.modules:
    print "Loading special vars ..." , 
    import os
    EPSILON = 1e-7
    infty = 1e309 # URL: http://stackoverflow.com/questions/1628026/python-infinity-any-caveats#comment31860436_1628026
    endl = os.linesep
    DISPLAYPLACES = 5 # Display 5 decimal places by default
    print "Loaded!"

# === Data Structures ===

# == Tagged Object ==

class TaggedObject(object):
    """ An object with a unique tag and a string alias """
    
    def __init__( self ):
        """ The simplest means to give each object a unique tag """ # NOTE: No need for a global lookup at this time
        self.desc = self.__class__.__name__ # Shorten name access
        self.tag = self.desc + str( id( self ) ) # Create a tag composed of the class name and memory id
        self.alias = "" # Init alias to the empty string
        
    def __str__( self ):
        """ String representation , by class and then by alias ( or tag if alias is not available ) """
        if self.has_alias():
            return self.__class__.__name__ + ":" + str( self.alias )
        else:
            return self.__class__.__name__ + ":" + str( self.tag )
        
    def give_alias( self , nick ):
        """ Assign alias , must be hashable , should use this to assign alias """
        if isinstance( nick , collections.Hashable ):
            self.alias = nick
        else:
            raise ValueError( "TaggedObject.give_alias: Alias must be hashable, received unhashable object" + str( nick ) )
        
    def has_alias( self ):
        """ Return True if an alias other than an empty string has been set """
        return self.alias != ""
    
    def best_ID( self ):
        """ Return the alias if it exists , otherwise return the tag """
        return self.alias if self.has_alias() else self.tag
  
# = class TaggedLookup =
    
class TaggedLookup( list ):
    """ A container for TaggedObjects, can be used for lookup and removal by tag and alias """
    
    def __init__( self , *args ):
        """ Normal 'list' init """
        list.__init__( self , *args )
        self.lookupByTag = {} # Dictionary of objects stored by tag
        self.lookupByAls = {} # Dictionary of objects stored by alias
        self.verbose = False
        
    def append( self , item ):
        """ Add an item to the lookup """
        list.append( self , item )
        self.lookupByTag[ item.tag ] = item
        if item.alias:
            self.lookupByAls[ item.alias ] = item
            
    def extend( self , extList ):
        """ Add a list of items to the lookup """
        for item in extList:
            self.append( item )
        
    def get_by_tag(self, pTag):
        """ Return an object reference from the lookup with a matching tag if it exists, otherwise return None """
        rtnObj = None
        try:
            rtnObj = self.lookupByTag[pTag]
        except KeyError:
            if self.verbose:
                print "Object with tag",pTag,"DNE in this problem"
        return rtnObj
        
    def get_by_als(self, pAls):
        """ Return an object reference from the lookup with a matching alias if it exists, otherwise return None """
        try:
            return self.lookupByAls[pAls]
        except KeyError:
            if self.verbose:
                print "Object with alias",pAls,"DNE in this problem"
            return None
                        
    def __str__(self):
        """ Print all contents by tag """
        rtnStr = ''
        for key, val in self.lookupByTag.iteritems():
            rtnStr += str(key) + '\t\t' + str(val) + endl # depends on 'ResearchEnv'
        return rtnStr
        
    # '__len__' inherited from 'list'
        
    def get_list( self ):
        """ Get all the elements in the lookup in a list """
        return self[:] # This object is already a list , just copy and return
        
    # TODO: .pop()
    # TODO: .remove() # This will work with object references

# = End TaggedLookup =  

# == End Tagged ==

# == Weighted List ==

class WeightedList( list ): # TODO: Send this to AsmEnv when it is confirmed to work
    """ A list in which every element is labelled with a dictionary , Use this when it is not convenient to add new attibutes to list elements """
    
    def __init__( self , *args ):
        """ Normal 'list' init """
        list.__init__( self , *args )
        self.weights = [ None for elem in xrange( len( self ) ) ]
        
    def append( self , item , weight = None ):
        """ Append an item and its label """
        list.append( self , item )
        self.weights.append( weight )
        
    def extend( self , items , pLabels = None ):
        if pLabels == None or len( items ) == len( pLabels ):
            list.extend( self , items )
            self.weights.extend( pLabels if pLabels != None else [ None for elem in xrange( len( items ) ) ] )
        elif pLabels != None:
            raise IndexError( "LabeleWeightedListdList.extend: Items and labels did not have the same length! " + str( len( items ) ) + " , " + str( len( pLabels ) ) )
        
    def get_weight( self , index , weight ):
        """ Get the 'label' value for the item at 'index' , if that label DNE at that index return None """
        try:
            return self.weights[ index ]
        except IndexError:
            return None
        
    def set_label( self , index , weight ):
        """ Set the 'weight' value for the item at 'index' to 'value' """
        self.weight[ index ] = value
        
    # Only add other 'list' functions as needed
    
# == End Weighted ==
      
# === End Structures ===


# === Graph Classes ===

# == class Node ==

class Node(TaggedObject):
    """ A graph node with edges """    
    
    def __init__( self , pGraph = None , alias = None):
        super( Node , self ).__init__()
        self.edges = WeightedList() # NOTE: These represent outgoing edges. Incoming edges are represented as references to this Node in other Nodes
        self.graph = pGraph # The graph that this node belongs to
        if alias != None:
            self.give_alias( alias )
        
    def connect_to( self , pNode , pDir = False ):
        """ Connect an edge between this Node and 'pNode' """
        self.edges.append( pNode ) # NOTE: This function assumes this Node is the tail
        if not pDir: # If the edge is not directed, add a reference from 'pNode' back to this Node
            pNode.edges.append( self )
        if self.alias != None and pNode.alias != None:
            return ( self.alias , pNode.alias , pDir ) # Return a representation of this edge for use with Graph
            #      ( Tail        , Head       , Directed? )  : Tail ---> Head
        else:
            return ( self.tag , pNode.tag , pDir ) # Return a representation of this edge for use with Graph
            #      ( Tail     , Head      , Directed? )  : Tail ---> Head
        
    def connect_to_checked( self , pNode , pDir = False ):
        """ Connect an edge between this Node and 'pNode' , avoiding duplicates """
        if pNode not in self.edges and self not in pNode.edges:
            return self.connect_to( pNode , pDir )
            #      ( Tail     , Head      , Directed? )  : Tail ---> Head
        else: # Else this edge exists, connection failed
            return None
        
# == End Node ==

# == class Graph ==

class Graph(TaggedObject):
    """ A simple graph structure with nodes and edges """
    
    def __init__( self , rootNode = None ):
        self.nodes = TaggedLookup()
        self.edges = []
        self.root = rootNode
        
    def add_node( self , pNode ):
        """ Add a Node , make note of tag and alias for easy lookup """ 
        # NOTE: A Node needn't be a member of the Graph in order to be reachable , this function is for establishing the relationship when it is important
        pNode.graph = self # Establish node membership
        self.nodes.append( pNode )
        
    def get_node_by_als( self , nodeAls ):
        """ Search for a node by its alias and return the reference if the node exists in the problem """
        return self.nodes.get_by_als( nodeAls )
    
    def connect_by_als( self , tailAls , headAls , pDir = False ):
        """ Connect two nodes by their aliases , add the connection to  """
        tail = self.connect_by_als( tailAls )
        head = self.connect_by_als( headAls )
        assert ( tail != None ) and ( head != None ) , "One of " + str(tailAls) + " or " + str(headAls) + " DNE in the problem"
        self.edges.append( tail.connect_to( head , pDir ) )
        
    def connect_by_ref( self , tail , head , pDir = False ):
        """ Connect two nodes , assuming we already have references to them """
        self.edges.append( tail.connect_to( head , pDir ) )
        
# == End Graph ==
        
# === End Graphs ===