#!/usr/bin/env python
# -*- coding: utf-8 -*-


# == Init Environment ==================================================================================================
import sys, os.path , stat
SOURCEDIR = os.path.dirname(os.path.abspath(__file__)) # URL, dir containing source file: http://stackoverflow.com/a/7783326

def first_valid_dir(dirList):
    """ Return the first valid directory in 'dirList', otherwise return False if no valid directories exist in the list """
    rtnDir = False
    for drctry in dirList:
        if os.path.exists( drctry ):
			rtnDir = drctry 
			break
    return rtnDir
        
def add_first_valid_dir_to_path(dirList):
    """ Add the first valid directory in 'dirList' to the system path """
    # In lieu of actually installing the library, just keep a list of all the places it could be in each environment
    validDir = first_valid_dir(dirList)
    if validDir:
        if validDir in sys.path:
            print "Already in sys.path:", validDir
        else:
            sys.path.append( validDir )
            print 'Loaded:', str(validDir)
    else:
        raise ImportError("None of the specified directories were loaded") # Assume that not having this loaded is a bad thing
# List all the places where the research environment could be
add_first_valid_dir_to_path( [ '/media/jwatson/FILEPILE/ME-6225_Motion-Planning/Assembly_Planner/ResearchEnv',
                               '/media/mawglin/FILEPILE/Python/ResearchEnv',
                               '/home/jwatson/regrasp_planning/researchenv',
                               '/media/jwatson/FILEPILE/Python/ResearchEnv',
                               'F:\Python\ResearchEnv'] )

# ~~ Libraries ~~
# ~ Standard Libraries ~
import os, time, shutil, sys , traceback
from datetime import datetime
# ~ Special Libraries ~
import eyed3 # This script was built for eyed3 0.7.9
# ~ Local Libraries ~
from ResearchEnv import * # Load the custom environment
from ResearchUtils.DebugLog import *

# == End Init ==========================================================================================================

badPaths = lines_from_file( 'output/badFiles.txt' )
# print badPaths[0]

totalFnum = len( badPaths )
exists = 0

if False:
    print "Working directory" , os.getcwd()
    print "changing ..."
    os.chdir( '/home/jwatson/Music/' )
    print "Working directory" , os.getcwd()
    
if True:
    print stat.S_IMODE(os.stat('/home/jwatson/Music/').st_mode) # 511
    # print os.stat('/home/jwatson/Music/').st_mode #           16895

if True:
    for path in badPaths:
	# 1. Test that the file exists
	# if os.path.isfile( path.strip() ):
	# stripPath = remove_all_from( '/home/jwatson/Music/' , path )
	# print stripPath
	# if os.path.isfile( stripPath ): # Not finding ANY of the files, all signs point to this being a permissions problem
	# if os.path.exists( stripPath ):
	# if os.path.exists( path ):
	print path
	if os.access( path , os.F_OK ):
	    exists += 1
	# 2. If Python does not recognize the file, find out why not
	#
	# 3. Try loading the file
	# 4. Try fetching metadata
    
    print exists , "exist out of" , totalFnum , "bad files" # 0 exist out of 4990 bad files