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
from marchhare import Counter

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
        if item.has_alias():
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
            rtnStr += str(key) + '\t\t' + str(val) + endl 
        return rtnStr
        
    # '__len__' inherited from 'list'
        
    def get_list( self ):
        """ Get all the elements in the lookup in a list """
        return self[:] # This object is already a list , just copy and return
    
    def recalc_alias_lookup( self ):
        """ Make sure that any elements that have recently acquired an alias appear in the alias lookup """
        for elem in self:
            if elem.has_alias():
                self.lookupByAls[ elem.alias ] = elem
    
    def assign_aliases_by_index( self ):
        """ Set the alias of each of the contained objects to be its corresponding index in the list , NOTE: Rewrites all element aliases! """
        for index , elem in enumerate( self ):
            elem.give_alias( index )
        self.recalc_alias_lookup() # Now that aliases have been assigned , add them to the lookup
        
    # TODO: .pop()
    # TODO: .remove() # This will work with object references

# = End TaggedLookup =  

# == End Tagged ==

# == Weighted List ==

class WeightedList( list ): 
    """ A list in which every element is labelled with a dictionary , Use this when it is not convenient to add new attibutes to list elements """
    
    def __init__( self , *args ):
        """ Normal 'list' init """
        list.__init__( self , *args )
        self.weights = [ None for elem in xrange( len( self ) ) ]
        
    def append( self , item , weight = {} ):
        """ Append an item and its label """
        list.append( self , item )
        self.weights.append( weight )
        
    def extend( self , items , weights = None ):
        if weights == None or len( items ) == len( weights ):
            list.extend( self , items )
            self.weights.extend( weights if weights != None else [ {} for elem in xrange( len( items ) ) ] )
        elif weights != None:
            raise IndexError( "LabeleWeightedListdList.extend: Items and labels did not have the same length! " + str( len( items ) ) + " , " + str( len( weights ) ) )
        
    def get_weight( self , index , weightName ):
        """ Get the 'label' value for the item at 'index' , if that label DNE at that index return None """
        try:
            return self.weights[ index ][ weightName ]
        except IndexError:
            return None
        
    def set_weight( self , index , weightName , value ):
        """ Set the 'weight' value for the item at 'index' to 'value' """
        self.weight[ index ][ weightName ] = value
        
    def index( self , val ):
        """ Return he index of the first occurrence of 'val' or 'None' """
        try:
            return list.index( self , val )
        except:
            return None
        
    # Only add other 'list' functions as needed
    
# == End Weighted ==
      
# === End Structures ===


# === Graph Classes ===

# == class Node ==

class Node(TaggedObject):
    """ A graph node with edges """    
    
    def __init__( self , pGraph = None , alias = None ):
        super( Node , self ).__init__()
        self.edges = WeightedList() # NOTE: These represent outgoing edges. Incoming edges are represented as references to this Node in other Nodes
        self.graph = pGraph # The graph that this node belongs to
        if alias != None:
            self.give_alias( alias )
        self.bag = Counter( default = None ) # This is a generic place to dump miscellaneous
        
    def connect_to( self , pNode , pDir = False , weight = {} ):
        """ Connect an edge between this Node and 'pNode' """
        # NOTE: This function assumes that an undirected edge has the same weight in both directions
        self.edges.append( pNode , weight ) # NOTE: This function assumes this Node is the tail
        if not pDir: # If the edge is not directed, add a reference from 'pNode' back to this Node
            pNode.edges.append( self , weight )
        if self.alias != None and pNode.alias != None:
            return ( self.alias , pNode.alias , pDir ) # Return a representation of this edge for use with Graph
            #      ( Tail        , Head       , Directed? )  : Tail ---> Head
        else:
            return ( self.tag , pNode.tag , pDir ) # Return a representation of this edge for use with Graph
            #      ( Tail     , Head      , Directed? )  : Tail ---> Head
        
    def connect_to_checked( self , pNode , pDir = False , weight = {}  ):
        """ Connect an edge between this Node and 'pNode' , avoiding duplicates """
        if pNode not in self.edges and self not in pNode.edges:
            return self.connect_to( pNode , pDir , weight )
            #      ( Tail     , Head      , Directed? )  : Tail ---> Head
        else: # Else this edge exists, connection failed
            return None
        
# == End Node ==

# == class Graph ==

class Graph(TaggedObject):
    """ A simple graph structure with nodes and edges """
    
    def __init__( self , rootNode = None ):
        super( Graph , self ).__init__()
        self.nodes = TaggedLookup()
        self.edges = [] # For now not providing any sort of fancy lookup structure for edges
        self.root = rootNode
        
    def add_node_by_ref( self , nodeRef ):
        """ Add a Node , make note of tag and alias for easy lookup """ 
        # NOTE: A Node needn't be a member of the Graph in order to be reachable , this function is for establishing the relationship when it is important
        nodeRef.graph = self # Establish node membership
        self.nodes.append( nodeRef )
        
    def create_node_with_als( self , alias ):
        """ Create a Node with a given 'alias' and add it to the graph """
        temp = Node( self , alias )
        temp.graph = self # Establish node membership
        self.nodes.append( temp )
        
    def get_node_by_als( self , nodeAls ):
        """ Search for a node by its alias and return the reference if the node exists in the problem """
        return self.nodes.get_by_als( nodeAls )
        
    def connect_by_ref( self , tail , head , pDir = False , weight = {} ):
        """ Connect two nodes , assuming we already have references to them """
        self.edges.append( tail.connect_to( head , pDir , weight ) )
        
    def get_node_list( self ):
        """ Return a list of nodes in this graph """
        return self.nodes.get_list()
    
    def assign_indices_to_nodes( self ):
        """ Load each of the nodes with information about their current index """
        for noDex , currNode in enumerate( self.get_node_list() ):
            currNode.bag['index'] = noDex
            
    def erase_indices_from_nodes( self ):
        """ Safely erase index information from all of the node in this graph """
        for noDex , currNode in enumerate( self.get_node_list() ):
            # URL , Two ways to remove dict key: https://stackoverflow.com/questions/11277432/how-to-remove-a-key-from-a-python-dictionary
            currNode.bag.pop( 'index' , None ) # Remove the 'index' key , if it exists
        
# == End Graph ==
        
# === End Graphs ===