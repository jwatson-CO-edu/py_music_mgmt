#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ~~ Future First ~~
from __future__ import division # Future imports must be called before everything else, including triple-quote docs!

"""
test_marchhare.py , Built on Spyder for Python 2.7
James Watson, 2017 May
TEST of the main marchhare file
"""

# == Tested Module =========================================================================================================================

# ~~ Add the parent directory to the path ~~
import sys , os
sys.path.append( os.path.dirname( os.path.dirname( __file__ ) ) )
# ~~ Import the library to be tested ~~ 
import marchhare as mh

# == End Module ==

import unittest

class TEST_marchhare( unittest.TestCase ):
    """ Main test case for the main MARCHHARE file """
    
    # ~~ PATH Manipulation ~~
    
    def test_findInPath( self ):
        self.assertTrue( "marchhare" in mh.find_in_path( "marchhare" , True ) )
        
    def test_findInLoaded( self ):
        self.assertTrue( "marchhare" in mh.find_in_loaded( "marchhare" , True ) )
        
    def test_addContainerToPath( self ):
        fPath = os.path.join( "rabbit" , "rabbit.py" )
        mh.add_container_to_path( fPath )
        # print mh.find_in_path( "rabbit" , True )
        self.assertTrue( "rabbit" in mh.find_in_path( "rabbit" , True ) )
        
    # ~~ Helper Functions ~~
    
    def test_sep( self ):
        self.assertTrue( mh.sep( title = "test" , width = 2 , char = '*' , strOut = True ) , "** test **" )
        
    # ~~ General Math Helpers ~~
    
    def test_eq( self ):
        num = 4.0
        self.assertTrue( mh.eq( 0.0 , EPSILON ) )
        self.assertTrue( mh.eq( num , num + EPSILON/2.0 ) )
        self.assertFalse( mh.eq( num , num + EPSILON*2.0 ) )
        
        
if __name__ == "__main__":
    unittest.main()