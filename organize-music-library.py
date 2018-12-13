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
   1.3.1. [X] Log a snapshot of the library
   1.4.   [X] Generate a movement plan , per file , with enough information to carry out the instructions
   1.5.   [X] Check and execute directory creation plans
   1.6.   [X] Check and execute file move/rename plans
   1.6.1. [X] Log the success of the plan execution 
   1.7.   [X] Check and execute directory deletion plans
   1.8.   [X] Implement a user menu
2. Empty Dir Cleaning - COMPLETE
3. Inbox Processing - NOT STARTED # This should be the default action to running the main file
4. Adapt #1 for 2 & 3 

  == TODO ==


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
from xml.dom.minidom import parseString
# ~ Special Libraries ~
import eyed3 # This script was built for eyed3 0.7.9
from dicttoxml import dicttoxml # For logging
# ~ Local Libraries ~

# ~~ Script Signature ~~
__progname__ = "Music Library Organizer"
__version__  = "2017.04.21"
def __prog_signature__(): return __progname__ + " , Version " + __version__ # Return a string representing program name and verions

# == End Init ==============================================================================================================================

# == Helper Functions ==

def sep( title = "" , width = 6 , char = '=' , strOut = False ): 
    """ Print a separating title card for debug , if 'strOut' return the string instead """
    LINE = width * char
    if strOut:
        return LINE + ' ' + title + ' ' + LINE
    else:
        print LINE + ' ' + title + ' ' + LINE

def format_epoch_timestamp( sysTime ): 
    """ Format epoch time into a readable timestamp """
    return datetime.fromtimestamp( sysTime ).strftime('%Y-%m-%d_%H-%M-%S-%f')

def validate_dirs_writable( *dirList ): 
    """ Return true if every directory argument both exists and is writable, otherwise return false """
    # NOTE: This function exits on the first failed check and does not provide info for any subsequent element of 'dirList'
    # NOTE: Assume that a writable directory is readable
    for directory in dirList:
        if not os.path.isdir( directory ):
            print "Directory" , directory , "does not exist!"
            return False
        if not os.access( directory , os.W_OK ): # URL, Check write permission: http://stackoverflow.com/a/2113511/893511
            print "System does not have write permission for" , directory , "!"
            return False
    return True # All checks finished OK, return true

def tokenize_with_wspace( rawStr , evalFunc = str ): 
    """ Return a list of tokens taken from 'rawStr' that is partitioned with whitespace, transforming each token with 'evalFunc' """
    return [ evalFunc( rawToken ) for rawToken in rawStr.split() ]

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
                except Exception: # Could not retrieve a safe artist , send to MISC
                    # print "DEBUG:" , libraryPath , MISCFOLDERNAME
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
        """ Local helper function to add success/failure data to the record of each attempted operation """
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
                try:
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
                except Exception as err:
                    dirSuccess = False
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
    return opReport

# [X] Check and execute directory deletion plans

def del_empty_subdirs( searchDir ):
    """ Delete all the empty subdirectories under 'searchDir', URL: http://stackoverflow.com/a/22015788/7186022 """
    for dirpath , _ , _ in os.walk( searchDir, topdown = False ):  # Walk the directory from the bottom up
        if dirpath == searchDir: # Do not attempt to delete the top level
            break
        try:
            if len( os.listdir( dirpath ) ) == 0: # If there are no files or subfolders in the directory
                os.rmdir( dirpath )
            # else , the directory is not empty , do not attempt deletion
        except OSError as ex:
            print "Rejected" , ex

# == Test Functions ==

def gather_files( searchPath ): 
    """ Find all the singular files under 'searchPath' (recursive) and move them directly to 'searchPath' , undoes organiztion """
    # Walk the 'searchPath'
    for dirName , subdirList , fileList in os.walk( searchPath ): # for each subdir in 'srchDir', including 'srchDir'
        if dirName != LOGDIR:
            for fName in fileList: # for each file in this subdir  
                if os.path.splitext( fName )[1][1:].upper() not in EXTIGNORE:
                    fullPath = os.path.join( dirName , fName )
                    if os.path.isfile( fullPath ):
                        print "Moving" , fullPath , "to" , os.path.join( searchPath , fName )
                        shutil.move( fullPath , os.path.join( searchPath , fName ) )
        else:
            print "Skipping the logging directory ..."

# == End Test ==

# == Serialization and Archival ==

nowTimeStamp = lambda: datetime.now().strftime('%Y-%m-%d_%H-%M-%S') # http://stackoverflow.com/a/5215012/893511
""" Return a formatted timestamp string, useful for logging and debugging """

def fname_timestamp_with_prefix( prefix , ext ):
    """ Return a timestamped filename with a 'prefix'ed name and the specified file 'ext'ension """
    if ext[0] == '.': # If the user passed the extension with the period , then remove it
        ext = ext[1:]
    return prefix + nowTimeStamp() + '.' + ext # Return the file

def remove_XML_header( pString ):
    """ Remove the front of 'pString' up to and including the first closing ">" , Removes the XML header from 'pString' """
    skipping = True
    skipStop = '>' 
    rtnStr = ""
    for char in pString:
        if not skipping:
            rtnStr += char        
        if char == skipStop:
            skipping = False
    return rtnStr

def records_to_XML_string( recordsList , outPath = None ):
    """ Convert a 'recordsList' to a string representing an XML document """
    rtnStr = """<?xml version="1.0" encoding="UTF-8" ?>""" + endl + """<log>""" + endl
    for record in recordsList:
        rtnStr += remove_XML_header( dicttoxml( record , custom_root = 'record' ) ) + endl
    rtnStr += """</log>"""
    if outPath: # If the user provided an output path , write the XML string to a file
        outFile = open( outPath , 'w' )
        outFile.write( rtnStr )
        outFile.close()
    return rtnStr

# == End Archival ==

# == User Interaction ==

modeEnum = { "REPAIR": "Repair music libary" , "INBOX": "Process files from inbox" }
mode = "REPAIR"
# configPath = "musicOrganizer.config" 

def menu_loop():
    """ Display and run the user menu """
    global mode , LIBDIR , SCANDIR , LOGDIR
    menuRun = True

    while( menuRun ):
        sep( __prog_signature__() )
        print "The library dir is set to:  " , LIBDIR
        print "The scanning dir is set to: " , SCANDIR
        print "The logging dir is set to:  " , LOGDIR
        print "The current mode is:        " , mode
        if not os.path.isdir( LOGDIR ):
            try:
                os.makedirs( LOGDIR )
            except:
                print "Could not create the logging directory!"
        accessible = validate_dirs_writable( LIBDIR , SCANDIR , LOGDIR )
        print "Directories are accessible:" , accessible
        print \
              """ ~~ MENU ~~ 
	      0. Quit
	      1. Change Mode
	      2. Execute: Scan -> Repair -> Clean
	      3. Change Library Directory
	      4. Change Scanning Directory
	      5. Change Logging Directory 
	      6. Flatten Library ( Gather files , Delete dirs )"""
        try:
            response = int( raw_input( "Menu Choice >> " ) )
        except ValueError:
            print "ERROR: Please enter a number corresponding to the desired menu choice!"

        if   response == 0: 
            menuRun = False
            print "EXIT"
            break

        elif response == 1:
            sep( "Change Mode" , 1 )
            choices = list( modeEnum.iteritems() )
            for i in xrange( len( choices ) ):
                print str(i) + ": " + str( choices[i][0] ) + " , " + str( choices[i][0] )
            choice = None
            validChoice = False
            while choice.__class__.__name__ != 'int' and not validChoice:
                try:
                    choice = int( raw_input( "Choose a mode and press enter: " ) )
                    if choice > -1 and choice < len( choices ):
                        validChoice = True
                    else:
                        print choice , "is not a valid option, try again."
                except:
                    print "ERROR: Could not parse user selection"
            mode = modeEnum[ choices[ choice ][0] ] # Set the mode to the user choice
            print "Mode was set to" , mode

        elif response == 2:
            sep( "Execute: Scan -> Repair -> Clean" , 1 )
            if not accessible: # If the user does not have access to any one of the relevant directory
                print "ALERT: This action is barred! User does not have write permission to relevant directories or directories DNE!"
            else:
                # Scan , Plan , Move
                fileInfo = fetch_library_metadata( SCANDIR ) # For a repair , the 'SCANDIR' and 'LIBDIR' should be the same
                moves = create_move_plan( fileInfo , LIBDIR )
                execution = execute_move_plan( moves , verbose = True )
                # Log everything 
                records_to_XML_string( fileInfo  , outPath = os.path.join( LOGDIR , fname_timestamp_with_prefix( "fileLog" , 'txt' ) ) )
                records_to_XML_string( moves     , outPath = os.path.join( LOGDIR , fname_timestamp_with_prefix( "planLog" , 'txt' ) ) ) 
                records_to_XML_string( execution , outPath = os.path.join( LOGDIR , fname_timestamp_with_prefix( "execLog" , 'txt' ) ) )
                # Erase empty dirs in the 'SCANDIR' (It's possible we removed a large number of files from this dir)
                del_empty_subdirs( SCANDIR )

        elif response == 3:
            sep( "Change Library Directory" , 1 )
            nuPath = tokenize_with_wspace( raw_input( "Enter the components of the library path, separated by spaces.\n>> " ) )
            try:
                nuPath = os.path.join( nuPath )
                if os.path.isdir( nuPath ):
                    if validate_dirs_writable( nuPath ):
                        LIBDIR = nuPath
                    else:
                        print "ERROR: You do not have write permission to this path!"
                else:
                    print "ERROR: Not a path!"
            except Exception as err:
                print "ERROR: Could not change directory" , endl , err

        elif response == 4:
            sep( "Change Scanning Directory" , 1 )
            nuPath = tokenize_with_wspace( raw_input( "Enter the components of the library path, separated by spaces.\n>> " ) )
            try:
                nuPath = os.path.join( nuPath )
                if os.path.isdir( nuPath ):
                    if validate_dirs_writable( nuPath ):
                        SCANDIR = nuPath
                    else:
                        print "ERROR: You do not have write permission to this path!"
                else:
                    print "ERROR: Not a path!"
            except Exception as err:
                print "ERROR: Could not change directory" , endl , err

        elif response == 5:
            sep( "Change Logging Directory" , 1 ) 
            nuPath = tokenize_with_wspace( raw_input( "Enter the components of the library path, separated by spaces.\n>> " ) )
            try:
                nuPath = os.path.join( nuPath )
                if os.path.isdir( nuPath ):
                    if validate_dirs_writable( nuPath ):
                        LOGDIR = nuPath
                    else:
                        print "ERROR: You do not have write permission to this path!"
                else:
                    print "ERROR: Not a path!"
            except Exception as err:
                print "ERROR: Could not change directory" , endl , err

        elif response == 6:
            sep( "Flatten Library" , 1 )
            print "Gathering files ..."
            gather_files( LIBDIR )
            print "Erasing empty dirs ..."
            del_empty_subdirs( LIBDIR )
            print "Complete!"

        else:
            print "ERROR: Please enter a number corresponding to the desired menu choice!"    

# == End Interaction ==

# == Main ==================================================================================================================================

if __name__ == "__main__":

    # ~~ Locate Music Library ~~
    #          Drive letter separator for Windows --v
    LIBRARY_LOCATIONS = [ "/media/mawglin/MUSIC/Music", 
                          os.path.join( "D:" , os.sep , "Python" , "py-music-mgmt" , "Amzn_2017-01-30" ) ]
    SCANDIR_LOCATIONS = [ "/media/mawglin/MUSIC/Music/zzz_Inbox" ]
    LIBDIR = first_valid_dir( LIBRARY_LOCATIONS )   
    SCANDIR = first_valid_dir( SCANDIR_LOCATIONS )
    print LIBDIR
    LOGDIR = os.path.join( LIBDIR , "Logs" )

    menu_loop()


# == End Main ==============================================================================================================================


# === Spare Parts ===



# === End Spare ===