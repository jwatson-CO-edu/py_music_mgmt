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
   1.1. [X] Fetch all relevant metadata and display / return
   1.2. [X] Generate Simplified Band Names
   1.3. [X] Generate Simplified folder names
   1.4. [ ] Generate a movement plan , per file
   1.5. [ ] Check with directory creation plans
   1.6. [ ] Check with directory deletion plans
2. Empty Dir Cleaning - NOT STARTED
3. Inbox Processing - NOT STARTED
4. Adapt #1 for 2 & 3

  == TODO ==
* Print basic overall stats
* Section numbers using 'util.Counter' from Berkeley, candidate for "ResearchEnv"
* Handle the case where the artist tag is readable but empty
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
# ~ Special Libraries ~
import eyed3 # This script was built for eyed3 0.7.9
# ~ Local Libraries ~
# from ResearchEnv import * # Load the custom environment
# from ResearchUtils.DebugLog import *

# == End Init ==============================================================================================================================

def format_epoch_timestamp( sysTime ):
    """ Format epoch time into a readable timestamp """
    return datetime.fromtimestamp( sysTime ).strftime('%Y-%m-%d_%H-%M-%S-%f')

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
	    if char not in DISALLOWEDCHARS: # If the character is not disallowed
		rtnStr += char # Append the char to the proper directory name
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

def fetch_library_metadata( libraryPath ):
    """ Get information about all the files in the 'libraryPath' """
    # The goal of this function is to get the information we need for all follow-up file operations
    
    allRecords = []
    
    # Walk the 'libraryPath'
    for dirName , subdirList , fileList in os.walk( libraryPath ): # for each subdir in 'srchDir', including 'srchDir'
	for fName in fileList: # for each file in this subdir    
	    
	    record = {} # Create a dictionary to store everything we find out about the file

	    # Information to get:
	    # ~ File Metadata ~
	    record[ 'folder' ] = dirName # ------------------------------------ Containing Directory
	    record[ 'fileName' ] = fName # ------------------------------------ filename
	    fullPath = os.path.join( dirName , fName )
	    record[ 'fullPath' ] = fullPath # --------------------------------- full path
	    record[ 'EXT' ] = os.path.splitext(fName)[1][1:].upper() # -------- extension
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

# [ ] Generate a movement plan , per file

def create_move_plan( recordList ):
    """ Given a 'recordList' created by 'fetch_library_metadata' generate a movement plan , per file """
    
    plannedMoves = []
    
    for record in recordList:
	# 1.   Get the file type
	# 1.1. The action depends on the file type
	# 2.   Get the artist and proper file name
	# 3.   Determine the proper folder for this file
	# 4.   Determine whether the file is in the right folder
	# 4.1.
	pass # FIXME: START HERE!





# == Main ==================================================================================================================================

if __name__ == "__main__":
    
    # ~~ Locate Music Library ~~
    #          Drive letter separator for Windows --v
    TEST_LIBRARY_LOCATIONS = [ os.path.join( "D:" , os.sep , "Python" , "py-music-mgmt" , "Amzn_2017-01-30" ) ]
    LIBDIR = first_valid_dir( TEST_LIBRARY_LOCATIONS )    
    
    if LIBDIR: # If the library was found , process it
	
	fileInfo = fetch_library_metadata( LIBDIR )
	for record in fileInfo:
	    print record
	print
	for key , val in fileInfo[0].iteritems():
	    print key , '\t' , val
	print
	for key , val in fileInfo[-1].iteritems():
	    print key , '\t' , val	
	    
    else: # else no library was found , notify
	print "No valid directory in" , TEST_LIBRARY_LOCATIONS
    
    
    

# == End Main ==============================================================================================================================


# === Spare Parts ===
#set_dbg_lvl(1) # Debug log file creation

## == Run Flags ==
## Use these flags to change how the script runs
#SCRAPECRRPTEXT = True # If there are particular file extensions that your music player chokes on, set this flag to True
##                       and edit 'CRRPTDFILEEXTS' before running the script
## == End Flags ==

#PARENTDIR = first_valid_dir( [ '/home/jwatson/Music',
                               #'/media/jwatson/FILEPILE/Python/py-music-mgmt/test_lib' , 
                               #'F:/Python/py-music-mgmt/test_lib'] )
#if not PARENTDIR:
    #raise IOError("Parent directory structure not found")

#dbgLog(1, "Parent dir:", PARENTDIR)

## None of the segments sent to 'os.path.join' after the first should start with a "/", otherwise previous segments will 
##be discarded, URL: http://stackoverflow.com/questions/17429044/constructing-absolute-path-with-os-join
## = Setup Directories =
#SEARCHDIR = PARENTDIR # FIXME: This is a test dir
#MUSLIBDIR = PARENTDIR # FIXME: This is a test dir
#VARIUSDIR = os.path.join( PARENTDIR , 'Various' ) # FIXME: This is a test dir
#RUNLOGDIR = os.path.join( PARENTDIR , 'logs' ) # FIXME: This is a test dir
#dbgLog(1, "Running log dir:", RUNLOGDIR)
#CORRPTDIR = os.path.join( PARENTDIR , 'Corrupt' ) # FIXME: This is a test dir

#def create_dirs(*dirList): # TODO: Move to ResearchEnv
    #""" Create the directories in 'dirList', and notify the user if errors occur """
    #success = True
    #for drctry in dirList:
	#if not os.path.exists( drctry ):
	    #try:
		#os.mkdir( drctry )
	    #except Exception as err:
		#success = False
		#print "create_dirs: Could not create",drctry,":",str(err)
	#else:
	    #print "Directory",drctry,"already exists"
    #return success


#def music_dir_validation():
    #""" Validate music library directories """
    #return validate_dirs_writable( SEARCHDIR , MUSLIBDIR , VARIUSDIR , RUNLOGDIR , CORRPTDIR )

#def music_dir_prep():
    #""" Create the expected folders where they are not present """
    #return create_dirs( SEARCHDIR , MUSLIBDIR , VARIUSDIR , RUNLOGDIR , CORRPTDIR )
    
## = End Directories =

## == String Processing ==

## = Artist Names =


            
#def proper_artist_dir(trialStr):
    #""" Return a musical artist's name stripped of disallowed chars and any leading 'the ' """
    #return proper_dir_name(strip_the(trialStr)).encode('ascii','ignore')
    ##                      ^-- Must call this before 'proper_dir_name' in order for it to work

## = End Names =

## = Log Names =

#nowTimeStamp = lambda: datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') # http://stackoverflow.com/a/5215012/893511
#""" Return a formatted timestamp string, useful for logging and debugging """

#FILEPREFIX = "Music-Lib-Org-Log_"
#LOGFILEEXTENSION = '.txt'
    
#def todays_log_name():
    #""" Return a string that is the file name prefix plus today's date and time plus the proper file extension """
    #return FILEPREFIX + nowTimeStamp() + LOGFILEEXTENSION
    
## NUMLOGSTODAY = 0 # The number of files in this dir with the file prefix and today's date # NOT IN USE

#def gen_log_name():
    #""" Return the full file name of the next log """ # assuming NUMLOGSTODAY is correct 
    #return todays_log_name() # + "_" + str( 0 if NUMLOGSTODAY == 0 else NUMLOGSTODAY ) + "." + LOGFILEEXTENSION
    
#def section(titleStr):
    #borderStr = '=========='
    #return borderStr + ' ' + str(titleStr) + ' ' + borderStr + endl

## = End Log =

## == End String ==


## == File Operation Logging ==

##def count_todays_logs():
##    global NUMLOGSTODAY
##    count = 0
##    namesInDir = os.listdir(SOURCEDIR)
##    for name in namesInDir:
##        if todays_log_name() in name:
##            count += 1
##    NUMLOGSTODAY = count
##    print "Found", NUMLOGSTODAY, "logs with today's date."
 
#CURRENTLOG = None # The current log file, only one should be open at a time
   
#def open_new_log():
    #""" Generate the next log file in the series, open for logging, and write preamble to file """
    #global CURRENTLOG
    #if not CURRENTLOG: # If there is no file currently open
        ##count_todays_logs()
        #currentLogName = gen_log_name() # generate the name of the next log file
        #CURRENTLOG = open( os.path.join( RUNLOGDIR , currentLogName ) , 'w') # Open a new file in write mode
        ## URL: http://stackoverflow.com/a/13891070
        #CURRENTLOG.write( "Opened new file " + currentLogName + " at " + #datetime.today()datetime.fromtimestamp(time.time()).strftime('%H:%M:%S') + endl )
                          #nowTimeStamp() + endl + endl )
        ##CURRENTLOG.write( section( 'File Operations' ) + endl )
    #else: # Else there was already a file open, warn the user
        #print "open_new_log : There is already a log open!"
        
#def close_current_log():
    #""" Close the current log if there is one open and mark the global var closed """
    #global CURRENTLOG
    #if CURRENTLOG:
        #CURRENTLOG.write( endl + "Closed file at " + nowTimeStamp() + endl )
        #CURRENTLOG.close()
        #CURRENTLOG = None # Mark the current log closed
    #else:
        #print "close_current_log : There was no log open!"

#def logln(*logItems):
    #""" Log Line: Write a line of text to the currently open log """
    #global CURRENTLOG
    #if CURRENTLOG: # If there is a log open, write 'logStr' to it on its own line
        #temp = ''
        #for msg in logItems:
            #temp += str(msg) + ' ' # Auto-insert spaces between args just like 'print <OUTPUT>,'
        ##temp += endl # double space not necessary
        #CURRENTLOG.write( str( temp ) + endl )
    #else: # else there was no log open, warn user
        #print "logln : There was no log open!"
    

## == End Logging ==


## == Directory Manipulation ==

#def parent_folder(path, nLevelsUp):
    #""" Return the containing directory that is 'nLevelsUp' from 'path' """
    #if nLevelsUp == 0:
        #return path
    #else:
        #return parent_folder(os.path.dirname(path), nLevelsUp-1)
        
#def last_X_to_end(longStr,charX):
    #""" Return the portion of 'longStr' that is occurs after the last instance of 'charX' is present, otherwise return 'longStr' """
    #rtnStr = ''
    #charDex = -1
    #while longStr[charDex] != charX and charDex >= -len(longStr):
        #rtnStr = longStr[charDex] + rtnStr
        #charDex -= 1
    #return rtnStr
    
#def parent_folder_name_only(path, nLevelsUp):
    #""" Return the name of the containing directory that is 'nLevelsUp' from 'item' """
    #return last_X_to_end( parent_folder(path, nLevelsUp) , '/')

## == End Directory ==

## == Music File Organization ==

#NUMPROCESSED = 0 # The number of files processed this session
#PROCESSTIME = time.clock() # Time since the last milestone
#MISCFOLDERNAME = "Various" # Name of the folder for files without a readable artist name
##ERRLIST = [] 
#DISALLOWEDEXTS = [ '.txt' , '.py' ] # folders with these file extensions should not be moved from the source dir
#CRRPTDFILEEXTS = [ '.Mp3' , '.MP3' ] # files with these extensions seem to have problems in MusicBee
#DUPFOLDERNAME = "zzz_Duplicates" # folder name to store dupicate files

#def repair_music_library_structure(srchDir, currLog):
    #""" Walk the entire music library 'srchDir', restore to an assumed structure, write results to CURRENTLOG """
    #if not CURRENTLOG: # If there is no log currently open, open one
        #open_new_log()
    #logln( "START , " + nowTimeStamp() + ": Music directory cleanup with 'repair_music_library_structure'" )
        
    #cpmvList = [] # list of copy / move operations to carry out, each element takes the form
    ## ( SOURCE , DESTINATION , one of {cp,mv,rm} )
    #errList = [] # List of errors for this session
    #idleList = [] # List of files that will not be moved
    ## ( "No Action," , FULLPATH )
    #mkdrList = [] # List of directories to create
    
    #fCount = 0
    #errCount = 0
    
    #for dirName, subdirList, fileList in os.walk(srchDir): # for each subdir in 'srchDir', including 'srchDir'
        #for fName in fileList: # for each file in this subdir
	    #fCount += 1
            #fullPath = os.path.join(dirName,fName) # construct the full path for this file
            #containingFolder = parent_folder_name_only(fullPath, 1) # Name of folder containing this file
            #extension = os.path.splitext(fName)[1] # Retrieve the file extension of the current item
            #mp3TagsLoaded = False
            #if extension == '.mp3': # If found mp3
            
                ## = Attept to load tags for an MP3 file = 
                #audiofile = None # var for current file
                #try: 
                    ## audiofile = eyed3.Tag() 
                    #audiofile = eyed3.core.load(fullPath) # Load the file
                    #audiofileTag = audiofile.tag # Instantiate an audio metadata object
                    ##audiofile.link(fullPath) # Grab info from an actual audio file
                    #if audiofileTag:
                        #mp3TagsLoaded = True # Flag success for an MP3 load
                #except Exception: # eyeD3 could not read the tags or otherwise load the file, report
		    #print "== Error =="
                    #errType, value, tb = sys.exc_info() # URL, get exception details:http://stackoverflow.com/a/15890953
                    ##errMsg = "Problem reading " + str(fullPath) + " tags!" + ", 'Python says: {0} , {1} , {2}".format(str(errType), str(value), 
		    ##                                                                                                  traceback.format_tb(traceback))
		    #errMsg = traceback.format_exception( errType, value, tb )
                    #for line in errMsg:
			#print line
                    #errList.append( errMsg )
		    #errCount += 1
                    
                    #accum.write( fullPath ) # Write the file path to the accumulator
                    
                    ##errList.append('Python says: %s , %s , %s' % (str(errType), str(value), str(traceback)))
                    ##logln( errMsg )
                ## = End tag load = 
                    
                ## 2.a Generate the name of the subdir where this file belongs
                #if mp3TagsLoaded and audiofileTag.artist: # If MP3 metadata is available for this file
                    ## 1. Find out if this current subdir is where the file belongs
		    ## FIXME: Need to account for an empty artist tag
                    #properDirName = proper_artist_dir( audiofileTag.artist ) # We have tags so generate proper dir name
                    #if not containingFolder == properDirName: # 2. If the current subdir does not meet standards
                        #targetDir = os.path.join( MUSLIBDIR , properDirName )
                        #if not os.path.isdir( targetDir ): # 2.b Find out if that subdir exists
                            #try:
				## 2.b.a If the proper dir does not exist, create it
				#os.mkdir( targetDir )
			    #except OSError as err:
				#errStr = "Unable to create dir " + str(targetDir) + endl + str(err)
				#errList.append( errStr )
                        ## 2.c Add the current file to the copy list to be sent to the proper directory
                        #cpmvList.append( (fullPath , targetDir , 'mv' ) ) # Move the file to the dir in either case
                    #else: # else, this file is already in the proper folder
                        #idleList.append( ( "No Action," , fullPath ) )
                #else: # else tags were not able to be loaded from this MP3 file
                    ## Send it to the various artist dir, if it is not already there
		    #errMsg = "MP3 did not have a readable artist, sent to " + str(VARIUSDIR) + endl + str(fullPath)
		    #errList.append( errMsg )
                    #if not containingFolder == VARIUSDIR:
                        #cpmvList.append( (fullPath , VARIUSDIR , 'mv' ) )
                    #else: # else, this file is already in the proper folder
                        #idleList.append( ( "No Action," , fullPath ) )
            ## 1. Get the file extension, already stored in 'extension'
            #elif extension not in DISALLOWEDEXTS: # The file is not an MP3, organize it by file type
                #if SCRAPECRRPTEXT and (extension in CRRPTDFILEEXTS): # If there are problem extensions and if this is one of them
                    #cpmvList.append( (fullPath , CORRPTDIR , 'mv' ) ) 
                #else:
                    ## 2. Generate the proper folder name 
                    #properDirName = extension[1:].upper()
                    #if not containingFolder == properDirName: # 2. If the current subdir does not meet standards
                        #targetDir = os.path.join( MUSLIBDIR , properDirName )
                        #if not os.path.isdir( targetDir ): # 2.b Find out if that subdir exists
			    #try:
				## 2.b.a If the proper dir does not exist, create it
				#os.mkdir( targetDir )
			    #except OSError as err:
				#errStr = "Unable to create dir " + str(targetDir) + endl + str(err)
				#errList.append( errStr )
                        ## 2.c Add the current file to the copy list to be sent to the proper directory
                        #cpmvList.append( (fullPath , targetDir , 'mv' ) ) # Move the file to the dir in either case
                    #else: # else, this file is already in the proper folder
                        #idleList.append( ( "No Action," , fullPath ) )
            ## else extension is disallowed and should be left alone (ex. log files, Python files)
            #else: # else, this file is already in the proper folder
                #idleList.append( ( "No Action," , fullPath ) )
    #print 
    #print "Processed" , fCount , "files with" , errCount , "errors"
    #logln( "END   , " + nowTimeStamp() + ": Music directory cleanup with 'repair_music_library_structure'" )
    ##close_current_log() # close the current log # Assumes that a log is open
    
    #accum.out_and_clear( 'output/badFiles.txt' )
    
    #return cpmvList, errList, idleList

#def sort_all_songs(arg, dirname, names):
    #pass
    #""" Copy all songs in 'SOURCEDIR' to 'PARENTDIR', sorted by artist 
    
    #This fuction is designed to be used with 'os.path.walk' in order the recursively search and process the source
    #directory 
    
    #Assumes that 'CURRENTLOG' is an open TXT file available for writing """
#""" global SOURCEDIR, PARENTDIR, NUMPROCESSED, PROCESSTIME, CURRENTLOG, ERRLIST
    #for item in names: # For each item in the present directory
        #NUMPROCESSED += 1
        #if NUMPROCESSED % 100 == 0: # Report the amount of time that it took to process the last 100 files
            #print "Processed " + str(NUMPROCESSED) + " files. Last 100 in " + str(time.clock() - PROCESSTIME)
            #PROCESSTIME = time.clock()
        #namePath = os.path.join(dirname, item) # Reconstruct the full path of the current item
        ##print "Processing " + str(namePath)
        #extension = os.path.splitext(item)[1] # Retrieve the file extension of the current item
        #if extension == '.mp3': # If found mp3
            #audiofile = None # var for current file
            #try: 
                ##audiofile = eyeD3.core.load(namePath) # Ask eyeD3 to load and scan the current file for metadata
                ##audiofile = eyeD3.load(namePath) # Ask eyeD3 to load and scan the current file for metadata
                #audiofile = eyeD3.Tag()
                #audiofile.link(namePath)
            #except: # eyeD3 could not read the tags or otherwise load the file, report
                #errMsg = "Problem reading " + str(namePath) + " tags!"
                #print errMsg
                #ERRLIST.append( errMsg )
                ## URL, get exception details:http://stackoverflow.com/a/15890953
                #type, value,  = sys.exc_info()
                #ERRLIST.append('Python says: %s , %s , %s' % (str(type), str(value), str(traceback)))
                #CURRENTLOG.write( errMsg + endl )
            #if audiofile: #and audiofile.tag: # If file loaded and artist metadata found
                ##artName = proper_artist_dir(audiofile.tag.artist) # format the artist's name for a directory name
                #artName = proper_artist_dir( audiofile.getArtist() )
            #else:
                #artName = ""
            #if len(artName) > 0: # If an appropriate artist name was generated
                #artistPath = os.path.join(PARENTDIR, artName) # find the path to that artist's folder
            #else:
                #artistPath = os.path.join(PARENTDIR, MISCFOLDERNAME) # find the path to the 'misc' bin
            #targetPath = os.path.join(artistPath, item) # generate a full destination path for the file
            #if os.path.isfile(namePath): # only attempt to move files, not directories
                #if os.path.exists(artistPath): # if the selected artist folder exists in the filesystem
                    #if not os.path.exists(targetPath): # if the target filename does not exist
                        #try: # Try to copy the file to the artist folder if exists
                            ## URL: https://docs.python.org/2/library/shutil.html#shutil.move
                            #shutil.move(namePath, targetPath) # Attempt to move the file
                            ##shutil.copy2(namePath, targetPath)
                            #CURRENTLOG.write( "Moved to " + str(targetPath) + endl )
                        #except:
                            #errMsg = "ERROR: Unable to move " + str(namePath)
                            #print errMsg
                            #ERRLIST.append( errMsg )
                            ## URL, get exception details:http://stackoverflow.com/a/15890953
                            #type, value, traceback = sys.exc_info()
                            #ERRLIST.append('Python says: %s , %s , %s' % (str(type), str(value), str(traceback)))
                            #CURRENTLOG.write( errMsg + endl )
                            ##print "Unable to copy " #+ str(namePath)
                    ## else target filename exists, but not same size, assume new version
                    #elif os.path.getsize(namePath) != os.path.getsize(targetPath):
                        #incVar = 0
                        #while os.path.exists(targetPath): # rename until new!
                            #incVar += 1
                            #newName = os.path.splitext(item)[0] + str(incVar) + os.path.splitext(item)[1]
                            #print "Attempt rename: " + newName
                            #targetPath = os.path.join(artistPath, newName)
                        #try: # Try to copy the file with a new name
                            #shutil.move(namePath, targetPath)
                            #CURRENTLOG.write( "Renamed and moved " + str(targetPath) + endl )
                            ##print "Copied " #+ str(targetPath)
                        #except:
                            #errMsg = "ERROR: Unable to move " + str(namePath)
                            #print errMsg
                            #ERRLIST.append( errMsg )
                            ## URL, get exception details:http://stackoverflow.com/a/15890953
                            #type, value, traceback = sys.exc_info()
                            #ERRLIST.append('Python says: %s , %s , %s' % (str(type), str(value), str(traceback)))
                            #CURRENTLOG.write( errMsg + endl )
                    #else: # else there is a file at the target location with the same name of the same size
                        #duplicatePath = os.path.join( os.path.join(PARENTDIR, DUPFOLDERNAME) , item )
                        #if not os.path.exists( os.path.join(PARENTDIR, DUPFOLDERNAME) ): # if there is no folder for duplicates
                            #try:  # try to create a duplicates folder
                                #os.mkdir( os.path.join(PARENTDIR, DUPFOLDERNAME) ) # try create dir 
                                #CURRENTLOG.write( "Created dir " + str(os.path.join(PARENTDIR, DUPFOLDERNAME)) + endl )
                            #except:
                                #errMsg = "ERROR: Unable to create dir " + str( os.path.join(PARENTDIR, DUPFOLDERNAME) )
                                #print errMsg
                                #ERRLIST.append( errMsg )
                                ## URL, get exception details:http://stackoverflow.com/a/15890953
                                #type, value, traceback = sys.exc_info()
                                #ERRLIST.append('Python says: %s , %s , %s' % (str(type), str(value), str(traceback)))
                                #CURRENTLOG.write( errMsg + endl )
                        #try: # Try to copy the file to the artist folder if exists
                            ## URL: https://docs.python.org/2/library/shutil.html#shutil.move
                            #shutil.move(namePath, duplicatePath) # Attempt to move the file
                            ##shutil.copy2(namePath, targetPath)
                            #CURRENTLOG.write( "Duplicate moved to " + str(duplicatePath) + endl )
                        #except:
                            #errMsg = "ERROR: Unable to move " + str(namePath)
                            #print errMsg
                            #ERRLIST.append( errMsg )
                            ## URL, get exception details:http://stackoverflow.com/a/15890953
                            #type, value, traceback = sys.exc_info()
                            #ERRLIST.append('Python says: %s , %s , %s' % (str(type), str(value), str(traceback)))
                            #CURRENTLOG.write( errMsg + endl )
                        
                #else: # else folder does not exist
                    #try:  
                        ## try create dir then copy
                        #os.mkdir(artistPath)
                        #CURRENTLOG.write( "Created dir " + str(artistPath) + endl )
                        #shutil.move(namePath, targetPath)
                        #CURRENTLOG.write( "Moved " + str(targetPath) + endl )
                    #except:
                        #errMsg = "Unable to move " + str(namePath)
                        #print errMsg
                        #ERRLIST.append( errMsg )
                        ## URL, get exception details:http://stackoverflow.com/a/15890953
                        #type, value, traceback = sys.exc_info()
                        #ERRLIST.append('Python says: %s , %s , %s' % (str(type), str(value), str(traceback)))
                        #CURRENTLOG.write( errMsg + endl )
        #else: # else, file is not an mp3
            #print "DEBUG: Founf file not MP3 at " + str(namePath)
            #typePath = os.path.join(PARENTDIR, extension[1:].upper()) # Create a path based on file type
            #if extension[1:].lower() not in DISALLOWEDEXTS: # do not allow logs or scripts to be moved
                #if os.path.exists(typePath):
                    #try: # Try to copy the file to the type folder if exists
                        #shutil.move(namePath, os.path.join(typePath, item))
                        #CURRENTLOG.write(  "Moved to " + str(targetPath) + endl )
                    #except:
                        #errMsg =  "Unable to move " + str(namePath) 
                        #print errMsg
                        #ERRLIST.append( errMsg )
                        ## URL, get exception details:http://stackoverflow.com/a/15890953
                        #type, value, traceback = sys.exc_info()
                        #ERRLIST.append('Python says: %s , %s , %s' % (str(type), str(value), str(traceback)))
                        #CURRENTLOG.write( errMsg + endl )
                #else:
                    #try: # else folder does not exist, try create dir then copy
                        #os.mkdir(typePath)
                        #shutil.move(namePath, os.path.join(typePath, item))
                        #CURRENTLOG.write( "Moved " + str(os.path.join(typePath, item)) + endl )
                    #except:
                        #errMsg =  "Unable to move " + str(namePath) 
                        #print errMsg
                        #ERRLIST.append( errMsg )
                        ## URL, get exception details:http://stackoverflow.com/a/15890953
                        #type, value, traceback = sys.exc_info()
                        #ERRLIST.append('Python says: %s , %s , %s' % (str(type), str(value), str(traceback)))
                        #CURRENTLOG.write( errMsg + endl )
#"""
    
## == End File Organization ==


## == Directory Cleanup ==

#ALLEMPTYDIRS = [] # list of directories to delete

#def find_empty_dirs(searchDir, safeToDel = False):
    #pass
    #""" Find all the empty directories and tag them for deletion in 'ALLEMPTYDIRS' 
    
    #Note: Because the searching and deleting functions are separate, a dir full of only empty dirs will not appear empty,
    #therefore this function must be run after each lowest level of empty dir deletions has taken place. This is not 
    #efficient """
#""" global ALLEMPTYDIRS # Allow editing of directory list
    #namesInDir = os.listdir(searchDir) # get a list of items in 'searchDir'
    #if len(namesInDir) > 0: # if items found
        #for name in namesInDir: # for each of the items found
            #subPath = os.path.join(searchDir, name) # reconstruct the complete path to the item
            #if os.path.isdir(subPath): # if the complete path is a directory
                #find_empty_dirs(subPath, True) # recurse on that directory, all dirs below top level are deletable
        #namesInDir = os.listdir(searchDir) # reset list of items in 'searchDir'
        #if len(namesInDir) == 0 and safeToDel: # If we have erased all the items, then
            #ALLEMPTYDIRS.append( searchDir ) # Add this to the list of dirs to delete
    #else: # else, there were no items found in this dir, delete it if safe
        #if safeToDel:
            #ALLEMPTYDIRS.append( searchDir )  # Add this to the list of dirs to delete
    ## After operating on all the names in this dir
#"""       
#def purge_empty_dirs(searchDir):
    #pass
    #""" Search for and delete all empty dirs in 'searchDir', recursively """
#""" global ALLEMPTYDIRS
    #find_empty_dirs(searchDir)
    #if len(ALLEMPTYDIRS) == 0:
        #print "purge_empty_dirs : No empty dirs to delete!"
    #elif not CURRENTLOG:
        #print "purge_empty_dirs : No log file open!"
    #else: # else we have dirs to delete and a valid log file
        #while len(ALLEMPTYDIRS) > 0:
            #for emptyDir in ALLEMPTYDIRS:
                #try:
                    #shutil.rmtree(emptyDir) # try removing the dir
                    #CURRENTLOG.write( "Removed directory " + str(emptyDir) + endl )
                #except OSError: # if there was an error, log it
                    #errMsg = "Unable to remove directory " + str(emptyDir) + endl
                    #print errMsg
                    #ERRLIST.append( errMsg )
                    #CURRENTLOG.write( errMsg + endl )
            #ALLEMPTYDIRS = [] # Reset empty dirs
            #find_empty_dirs(searchDir)
#"""
## == End Cleanup ==


## == Main ==
#print "Directories are ready for repair:" , music_dir_validation()
#if not music_dir_validation():
    #print "Attempting preparation of music directories ...",
    #if music_dir_prep():
	#print "SUCCESS"
    #else:
	#print "FAILURE"
    #print "Directories are ready for repair:" , music_dir_validation()

#if __name__ == "__main__" and music_dir_validation():

    ## ~ Prep Work ~
    #open_new_log()
    
    
    #moveList, errors, noAction = repair_music_library_structure( SEARCHDIR , CURRENTLOG )
    
    #logln("-- File Operations List --")
    #for item in moveList:
	#logln( "\t" + str(item) )
    #logln("-- End Operations --")
    
    #logln("-- File Errors List --")
    #for item in errors:
	#logln( "\t" + str(item) )
    #logln("-- End Errors --")
    
    #logln("-- Skipped Files List --")
    #for item in noAction:
	#logln( "\t" + str(item) )
    #logln("-- End Skipped --")
    
    #"""
    ## Check that conditions are met for running the file sorting function
    #if not os.path.exists(SOURCEDIR):
	#print "Source path " + str(SOURCEDIR) + " not found!"
    #elif not os.path.exists(PARENTDIR):
	#print "Destination path " + str(PARENTDIR) + " not found!"
    #elif not CURRENTLOG:
	#print "No log file open!"
    #else:
	## Perform file organization operations    
	#CURRENTLOG.write( section('File Operations') )
	#os.path.walk(SOURCEDIR, sort_all_songs, False)
	#procMsg =  "Processed " + str(NUMPROCESSED) + " files."
	#CURRENTLOG.write( endl + procMsg + endl + endl )
	## Find and erase all empty dirs
	#CURRENTLOG.write( section('Cleanup') )
	##find_empty_dirs(SOURCEDIR)    
	#purge_empty_dirs(SOURCEDIR)
	## Log all the errors encountered during organization and cleanup
	#CURRENTLOG.write( section('Errors') )
	#for err in ERRLIST:
	    #CURRENTLOG.write( err + endl )
	#CURRENTLOG.write( section('End') )
    #"""
    ## ~ Cleanup Work ~
    #close_current_log() # Record time of script end and close the log file
    
    ## == End Main ==
# === End Spare ===