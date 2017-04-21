#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
organize-music-library.py , Built on Spyder for Python 2.7
James Watson, 2016 March
Organize music library, try to gracefully handle duplicates and problem files

== REBOOT PLAN ==

Principles
* Test one thing at a time
* Do the simplest thing first!
* Modular design
* File-by-file plan
* Maintain lists of directories to create / destroy

Modules
1. Fetch all relevant metadata and display / return
2. Generate Simplified Band Names
3. Generate a movement plan , per file
4. Generate a per-file record that contains all { metadata , movement plans } , can be queried
4. Check with directory creation plans
5. Check with directory deletion plans

Main Sequence
1. Scan all music folders , generating movement plans , per file , NO CHECKS made for directory existence , NO CHECKS on duplicates
   a. Test each on one file , then test on entire library
2. Create folders in the target dir
3. Execute movement plans
   a. Check destination
   b. Move
      i. Handle duplicates : Eliminate low-quality duplicates , eliminite exact duplicates , Discriminate versions
   c. Check success
   d. Check gone from origin
4. Execute directory deletion plans
   a. Check dir empty
   b. Delete dir
   c. Check dir deleted

== END REBOOT ==



  == NOTES ==
* Abandoned file location assumptions.  File locations are declared explicitly in the file or via the menu
  and verified automatically before each run
* Adding a full timestamp down to the second to log filenames so that the number of logs in a day do not have to be counted

  == USAGE ==
1. BACKUP YOUR PLAYLISTS AND MUSIC BEFORE RUNNING THIS FILE! 
   It is unknown how MusicBee will handle playlists and metadata after the music is moved
2. Verify that the global directory vars are pointing to the correct locations

== PROJECT ==
1. Library Repair - IN PROPGRESS
   1.1.   [X] Fetch all relevant metadata and display / return
   1.2.   [X] Generate Simplified Band Names
   1.3.   [X] Generate Simplified folder names
   1.3.1. [ ] Log a snapshot of the library
   1.4.   [X] Generate a movement plan , per file , with enough information to carry out the instructions
   1.5.   [X] Check and execute directory creation plans
   1.6.   [X] Check and execute file move/rename plans
   1.6.1. [ ] Log the success of the plan execution 
   1.7.   [X] Check and execute directory deletion plans
2. Empty Dir Cleaning - COMPLETE
3. Inbox Processing - NOT STARTED # This should be the default action to running the main file
4. Adapt #1 for 2 & 3 

  == TODO ==
* All of the 'cpmvList' entries seem the be malformed, review the 'shutil' docs for what the move function wants
* The repair function should record all move/erase decisions, even when no action is taken
* The sort-inbox function should only record actions taken
* Perhaps encapsulate the meat of repair/sort in a single function that is run with options. The operations are nearly identical
* See if there are ways to read tags in other filetypes

"""

# == Init Environment ======================================================================================================================
import sys, os.path
SOURCEDIR = os.path.dirname(os.path.abspath(__file__)) # URL, dir containing source file: http://stackoverflow.com/a/7783326

def first_valid_dir( dirList ):
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
#add_first_valid_dir_to_path( [ '/media/jwatson/FILEPILE/Utah_Research/Assembly_Planner/ResearchEnv',
                               #'F:\Utah_Research\Assembly_Planner\ResearchEnv',
                               #'/media/jwatson/FILEPILE/ME-6225_Motion-Planning/Assembly_Planner/ResearchEnv',
                               #'/media/mawglin/FILEPILE/Python/ResearchEnv',
                               #'/home/jwatson/regrasp_planning/researchenv',
                               #'/media/jwatson/FILEPILE/Python/ResearchEnv',
                               #'F:\Python\ResearchEnv'] )

# ~~ Constants , Shortcuts , Aliases ~~
import __builtin__ # URL, add global vars across modules: http://stackoverflow.com/a/15959638/893511
__builtin__.EPSILON = 1e-7 # Assume floating point errors below this level
__builtin__.infty = 1e309 # URL: http://stackoverflow.com/questions/1628026/python-infinity-any-caveats#comment31860436_1628026
__builtin__.endl = os.linesep # Line separator

# ~~ Libraries ~~
# ~ Standard Libraries ~
import os, time, shutil, sys , traceback
from datetime import datetime
from random import choice
from copy import deepcopy
# ~ Special Libraries ~
import eyed3 # This script was built for eyed3 0.7.9
# ~ Local Libraries ~

# ~~ Script Signature ~~
__progname__ = "PROGRAM NAME"
__version__  = "YYYY.MM.DD"
def __prog_signature__(): return __progname__ + " , Version " + __version__ # Return a string representing program name and verions

# == End Init ==============================================================================================================================

# == Helper Functions ==

def sep( title = "" , width = 6 , char = '=' , strOut = False ): # <<< resenv
    """ Print a separating title card for debug """
    LINE = width * char
    if strOut:
        return LINE + ' ' + title + ' ' + LINE
    else:
        print LINE + ' ' + title + ' ' + LINE

def format_epoch_timestamp( sysTime ): # TODO: Send to AsmEnv
    """ Format epoch time into a readable timestamp """
    return datetime.fromtimestamp( sysTime ).strftime('%Y-%m-%d_%H-%M-%S-%f')
    
# == End Helper ==



# TODO: Send to AsmEnv
# URL: http://code.activestate.com/recipes/65117-converting-between-ascii-numbers-and-characters/
ASCII_ALPHANUM = [chr(code) for code in xrange(48,57+1)]+[chr(code) for code in xrange(65,90+1)]+[chr(code) for code in xrange(97,122+1)]

""" URL: https://msdn.microsoft.com/en-us/library/windows/desktop/aa365247(v=vs.85).aspx
Use any character in the current code page for a name, including Unicode characters and characters in the extended character set (128–255), 
except for the following reserved characters:
< (less than)
> (greater than)
: (colon)
" (double quote)
/ (forward slash)
\ (backslash)
| (vertical bar or pipe)
? (question mark)
* (asterisk)
"""

# [X] Generate NTFS-safe Band Names with definite article removed

DISALLOWEDCHARS = "\\/><|:&; \r\t\n.\"\'?*" # Do not create a directory or file with these chars

def strip_the( artistName ):
    """ Strip a musical artist's name of a leading 'the ' , case insensitive """
    # NOTE: This must be run BEFORE 'proper_dir_name' because it relies on there being a space after "The"
    if artistName and artistName[:4].lower() == "the ": 
        return artistName[4:]
    else:
        return artistName

# [X] Generate Simplified folder names # safe path with safe filename

def safe_dir_name( trialStr ):
    """ Return a string stripped of all disallowed chars """
    rtnStr = ""
    if trialStr: # if a string was received 
	for char in trialStr: # for each character of the input string
	    if char not in DISALLOWEDCHARS and not char.isspace(): # If the character is not disallowed and is not whitespace
		try:
		    char = char.encode( 'ascii' , 'ignore' ) # Ignore conv errors but inconsistent # http://stackoverflow.com/a/2365444/893511
		    rtnStr += char # Append the char to the proper directory name
		except:
		    rtnStr += choice( ASCII_ALPHANUM ) # Random ASCII character so that completely unreadable names are not overwritten
	return rtnStr
    else:
	return None
    
def safe_artist_name( artistName ):
    """ Return a version of the artist name that has neither the definite article nor any disallowed chars """
    artistName = strip_the( artistName )
    return safe_dir_name( artistName )

# [X] Generate NTFS-safe filename

def safe_file_name( fName ):
    """ Return a modified file name that conforms to NTFS naming rules """ 
    # NOTE: This function assumes it is okay to begin filenames with a digit
    rtnName = list( os.path.splitext( fName ) ) # Split fname
    rtnName[0] = safe_dir_name( rtnName[0] )# transform name w/o ext
    return rtnName[0] + rtnName[1] # reapply ext & return

# [X] Fetch all relevant metadata and display / return

def fetch_library_metadata( searchPath ):
    """ Get information about all the files in the 'libraryPath' , this will be used to generate file management actions """
    # The goal of this function is to get the information for everything in 'searchPath' we need for all follow-up file operations
    
    allRecords = []
    
    # Walk the 'searchPath'
    for dirName , subdirList , fileList in os.walk( searchPath ): # for each subdir in 'searchPath', including 'searchPath'
	for fName in fileList: # for each file in this subdir    
	    
	    record = {} # Create a dictionary to store everything we find out about the file

	    # Information to get:
	    # ~ File Metadata ~
	    record[ 'folder' ] = dirName # ------------------------------------ Containing Directory
	    record[ 'fileName' ] = fName # ------------------------------------ filename
	    fullPath = os.path.join( dirName , fName )
	    record[ 'fullPath' ] = fullPath # --------------------------------- full path
	    record[ 'EXT' ] = os.path.splitext( fName )[1][1:].upper() # -------- extension
	    # creation date # This is not consistent across OS
	    record[ 'modDate' ] = os.path.getmtime( fullPath ) # -------------- modification date 
	    record[ 'modDateReadable' ] = \
	        format_epoch_timestamp( record[ 'modDate' ] ) # --------------- modification date (human readable)
	    record[ 'size' ] = os.path.getsize( fullPath ) # ------------------ size on disk
	    # ~ Song Metadata ~
	    try:
		audiofile = eyed3.core.load( fullPath ) # Load the file
		audiofileTag = audiofile.tag # Instantiate an audio metadata object
	    except:
		audiofileTag = None
	    if audiofileTag: # if the metadata was able to be loaded
		record[ 'artist' ] = audiofileTag.artist # -------------------- MP3 Artist
		record[ 'title' ] = audiofileTag.title # ---------------------- MP3 Title
		record[ 'album' ] = audiofileTag.album # ---------------------- MP3 Album
		record[ 'albumArtist' ] = audiofileTag.album_artist # --------- Album Artist
		record[ 'total_seconds' ] = audiofile.info.time_secs # -------- MP3 Length
		record[ 'mm:ss' ] = ( int( audiofile.info.time_secs / 60 ) , 
		                      audiofile.info.time_secs % 60 )# -------- Time in mm:ss
	    else: # else could not load MP3 tags , Load dummy data
		record[ 'artist' ] = 'Various' # ------------------------------ MP3 Artist
		record[ 'title' ] = None # ------------------------------------ MP3 Title
		record[ 'album' ] = None # ------------------------------------ MP3 Album
		record[ 'albumArtist' ] = None # ------------------------------ Album Artist
		record[ 'total_seconds' ] = None # ---------------------------- MP3 Length
		record[ 'mm:ss' ] = ( None , None ) # ------------------------- Time in mm:ss
	    # ~ Generated Metadata ~
	    record[ 'artistSafe' ] = safe_artist_name( record[ 'artist' ] ) # - MP3 Artist (NTFS Safe)
	    record[ 'fileNameSafe' ] = safe_file_name( record[ 'fileName' ] ) # File Name (NTFS Safe)
	    
	    allRecords.append( record )
	    
    return allRecords

# [X] Generate a movement plan , per file

EXTIGNORE = [ item.upper() for item in [ "txt" , "py" , "pyc" ] ]
MISCFOLDERNAME = "Various" # Name of the folder for files without a readable artist name

def create_move_plan( recordList , libraryPath ):
    """ Given a 'recordList' created by 'fetch_library_metadata' generate a movement plan , per file """
    
    plannedMoves = []
    
    for record in recordList:
	# 1.   Get the file type
	ext = record[ 'EXT' ]
	# 1.1. The action depends on the file type
	if ext not in EXTIGNORE: 
	    if ext == 'MP3':
		# 2.   Get the artist and proper file name , Determine the proper folder for this file
		try:
		    properDir = os.path.join( libraryPath , record[ 'artistSafe' ] ) # The file should be stored under the safe artist name
		except AttributeError: # Could not retrieve a safe artist , send to MISC
		    properDir = os.path.join( libraryPath , MISCFOLDERNAME ) 
	    else: # For non-MP3 files , the file should be in a folder that is the capitalized extension
		properDir = os.path.join( libraryPath , ext )	    
	    # 4.   Determine whether the file is in the right folder
	    correctLoc = record[ 'folder' ] == properDir
	    # 4.1. If the file is not in the right folder , move and perhaps rename
	    if not correctLoc: # If the file is not in the proper directory , move and perhaps rename
		# 4.1. If the file is not in the right folder , specify a move action    
		plannedMoves.append( { 'op': 'mv' , # move operation
		                       'orgn': record[ 'fullPath' ] , # from the current path
		                       'orginDir' : record[ 'folder' ] ,
		                       'dest': os.path.join( properDir , record[ 'fileNameSafe' ] ) , 
		                       'destDir': properDir } ) # to the proper dir with a safe name
	    elif not record[ 'fileNameSafe' ] == record[ 'fileName' ]:
		plannedMoves.append( { 'op': 'nm' , 
		                       'orgn': record[ 'fullPath' ] , 
		                       'orginDir' : record[ 'folder' ] , # Origin and destination folders are the same in this case
		                       'dest': os.path.join( record[ 'folder' ] , record[ 'fileNameSafe' ] ) , # Renamed in the same folder
		                       'destDir': record[ 'folder' ] } )
	    # else the file is both in the proper dir and has a safe name , no action
    return plannedMoves

# [X] Check and execute directory creation plans
# [X] Check and execute file move/rename plans

def execute_move_plan( movePlan , verbose = False ): # Set simulate to 'True' to disable actual file operations
    """ Carry out all dir creation / file move / file rename operations determined by 'create_move_plan' , return operation status """
    opReport = deepcopy( movePlan ) # operation status , Create a deep copy of the move plan so that it can be annotated as we go
    
    def log_status( reportList , op ,  index , success , msg , verbose ):
	reportList[ index ][ 'success' ] = success
	reportList[ index ][ 'statusMsg' ] = msg
	if verbose:
	    print op[ 'op' ] , op[ 'orgn' ] , "Success?" , reportList[ index ][ 'success' ] , "Msg:" , reportList[ index ][ 'statusMsg' ]    
    
    for opDex , operation in enumerate( movePlan ):
	opReport[ opDex ][ 'opNum' ] = opDex
	if operation[ 'op' ] == 'mv': # MOVE operation
	    dirSuccess = False
	    # Check that the origin file exists
	    if os.path.isfile( operation[ 'orgn' ] ):
		# Check that the destination directory exists
		if not os.path.isdir( operation[ 'destDir' ] ):
		    # If the dest dir does not exist , create it
		    try: # http://stackoverflow.com/a/5032238/7186022
			os.makedirs( operation[ 'destDir' ] )
			dirSuccess = True
		    except OSError as exception:
			if exception.errno != errno.EEXIST: # For any other error than an already existent directory , raise
			    raise
		else: # else the directory already exists , make sure to set the flag to allow move
		    dirSuccess = True
		if dirSuccess: # If the directory exists
		    # Move the file , else simulate
		    shutil.move( operation[ 'orgn' ] , operation[ 'dest' ] )
		    # Check that the file was successfully moved and report status		
		    if os.path.isfile( operation[ 'dest' ] ):
			log_status( opReport , operation , opDex , True , "SUCCESS" , verbose )
		    else: # else could not find file at the intended destination
			log_status( opReport , operation , opDex , False , "FAIL: FILE NOT MOVED" , verbose )			
		else: # else the directory was not found and was not created
		    log_status( opReport , operation , opDex , False , "FAIL: DIRECTORY NOT CREATED" , verbose )    
	    else: # else the file was not found at the origin location
		log_status( opReport , operation , opDex , False , "FAIL: ORIGIN FILE DNE" , verbose )    
	elif operation[ 'op' ] == 'nm': # RENAME operation
	    # Check that the target file exists
	    if os.path.isfile( operation[ 'orgn' ] ):
		os.rename( operation[ 'orgn' ] , operation[ 'dest' ] )
		if os.path.isfile( operation[ 'dest' ] ):
		    log_status( opReport , operation , opDex , True , "SUCCESS" , verbose )
		else:
		    log_status( opReport , operation , opDex , False , "FAIL: FILE NOT RENAMED" , verbose )	    
	    else:
		log_status( opReport , operation , opDex , False , "FAIL: ORIGIN FILE DNE" , verbose )
	else: # else an unrecognized operation was requested , notify
	    print "execute_move_plan: Operations type" , operation[ 'op' ] , "is not recognized!"
	    log_status( opReport , operation , opDex , False , "FAIL: OPERATION NOT RECOGNIZED" , verbose )

# [X] Check and execute directory deletion plans

def del_empty_subdirs( searchDir ):
    """ Delete all the empty subdirectories under 'searchDir', URL: http://stackoverflow.com/a/22015788/7186022 """
    for dirpath , _ , _ in os.walk( searchDir, topdown = False ):  # Walk the directory from the bottom up
        if dirpath == searchDir: # Do not attempt to delete the top level
            break
        try:
	    # TODO: Check if the directory is actually empty before attempting deletion
            os.rmdir( dirpath )
        except OSError as ex:
            print "Rejected" , ex
	    
# def log_str_ # FIXME: START HERE

# == Test Functions ==

def gather_files( searchPath ): # UNDO organization
    """ Find all the singular files under 'searchPath' (recursive) and move them directly to 'searchPath' """
    # Walk the 'searchPath'
    for dirName , subdirList , fileList in os.walk( searchPath ): # for each subdir in 'srchDir', including 'srchDir'
	for fName in fileList: # for each file in this subdir    
	    fullPath = os.path.join( dirName , fName )    
	    if os.path.isfile( fullPath ):
		print "Moving" , fullPath , "to" , os.path.join( searchPath , fName )
		shutil.move( fullPath , os.path.join( searchPath , fName ) )

# == End Test ==

# == User Interaction ==

def menu_loop():
    """ Display and run the user menu """
    
    menuRun = True

    while( menuRun ):
	sep( __prog_signature__() )
	print "The library dir is set to:  " , LIBDIR
	print "The scanning dir is set to: " , SCANDIR
	print "The current mode is:        " , mode
	print \
	      """ ~~ MENU ~~ 
	      0. Change Mode
	      1. Change Library Directory
	      2. Change Scanning Directory
	      3. Execute: Scan -> Repair -> Clean
	      4. Quit """
	try:
	    response = int( raw_input( "Menu Choice >>" ) )
	except ValueError:
	    print "ERROR: Please enter a number corresponding to the desired menu choice!"
	    
	if   response == 0:
	    sep( "Change Mode" , 1 )
	elif response == 1:
	    sep( "Change Library Directory" , 1 )
	elif response == 2:
	    sep( "Change Scanning Directory" , 1 )
	elif response == 3:
	    sep( "Execute: Scan -> Repair -> Clean" , 1 )
	elif response == 4:
	    menuRun = False
	    print "EXIT"
	    break
	else:
	    print "ERROR: Please enter a number corresponding to the desired menu choice!"    

# == End Interaction ==

# == Main ==================================================================================================================================

if __name__ == "__main__":
    
    # ~~ Locate Music Library ~~
    #          Drive letter separator for Windows --v
    TEST_LIBRARY_LOCATIONS = [ "/home/jwatson/Music" , 
                               os.path.join( "D:" , os.sep , "Python" , "py-music-mgmt" , "Amzn_2017-01-30" ) ,
                               "/media/jwatson/FILEPILE/Python/py-music-mgmt/Amzn_2017-01-30" ]
    LIBDIR = first_valid_dir( TEST_LIBRARY_LOCATIONS )    
    
    if LIBDIR: # If the library was found , process it
	
	fileInfo = fetch_library_metadata( LIBDIR )
	for record in fileInfo:
	    print record
	print
	for key , val in fileInfo[0].iteritems():
	    print key , '\t' , val
	
	moves = create_move_plan( fileInfo , LIBDIR )
	for move in moves:
	    print move
	    
	execute_move_plan( moves , verbose = True )
	    
    else: # else no library was found , notify
	print "No valid directory in" , TEST_LIBRARY_LOCATIONS
    
    
    modeEnum = ( "REPAIR" , "INBOX" )
    menuRun = True
    mode = modeEnum[ 0 ]
    SCANDIR = LIBDIR
    
    

# == End Main ==============================================================================================================================


# === Spare Parts ===



# === End Spare ===