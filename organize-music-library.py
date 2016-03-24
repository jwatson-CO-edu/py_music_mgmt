# -*- coding: utf-8 -*-
"""
organize-music-library.py , Built on Spyder for Python 2.7
James Watson, 2016 March
Organize music library, try to gracefully handle duplicates and problem files

  == NOTES ==
* Abandoned file location assumptions.  File locations are declared explicitly in the file or via the menu
  and verified automatically before each run
"""

# == Init Environment ==

# ~ PATH Changes ~ 
def localize():
    """ Add the current directory to Python path if it is not already there """
    from sys import path # I know it is bad style to load modules in function
    import os.path as os_path
    containerDir = os_path.dirname(__file__)
    if containerDir not in path:
        path.append( containerDir )

localize() # You can now load local modules!

# Standard Libraries
import os, time, shutil, sys
#from sys import path
from datetime import date, datetime
# Special Libraries
import eyeD3

# ~ Shortcuts and Aliases ~
endl = os.linesep # URL: http://stackoverflow.com/a/1223303

# = Setup Directories =
SOURCEDIR = os.path.dirname(os.path.abspath(__file__)) # URL: http://stackoverflow.com/a/7783326
PARENTDIR = os.path.dirname(SOURCEDIR)

print "Source Dir  : ", str(SOURCEDIR) # directory containing the script file
print "Library Dir : ", str(PARENTDIR) # directory containing that directory
# = End Directories =

# == String Processing ==

# = Artist Names =

DISALLOWEDCHARS = "\\/><|:&; \r\t\n.\"\'?" # Do not create a directory with these chars

def strip_the(artistName):
    """ Strip a musical artist's name of a leading 'the ' , case insensitive """
    # Note this will have no effect if 'proper_dir_name' has already been run!
    if artistName and artistName[:4].lower() == "the ": 
        return artistName[4:]
    else:
        return artistName

def proper_dir_name(trialStr):
    """ Return a string stripped of all disallowed chars """
    rtnStr = ""
    if trialStr:
        for char in trialStr:
            if char not in DISALLOWEDCHARS:
                rtnStr += char
    return rtnStr
            
def proper_artist_dir(trialStr):
    """ Return a musical artist's name stripped of disallowed chars and any leading 'the ' """
    return proper_dir_name(strip_the(trialStr)).encode('ascii','ignore')
    #                      ^-- Must call this before 'proper_dir_name' in order for it to work

# = End Names =

# = Log Names =

FILEPREFIX = "Music-Lib-Org-Log_"

def today_YYYY_MM_DD():
    """ Return today's date as YYYY-MM-DD """
    return str(date.today().year) + "-" + str(date.today().month) + "-" + str(date.today().day)
    
def todays_log_name():
    """ Return a string that is the file name prefix plus today's date """
    return FILEPREFIX + today_YYYY_MM_DD()
    
LOGFILEEXTENSION = 'txt'

NUMLOGSTODAY = 0 # The number of files in this dir with the file prefix and today's date

def gen_log_name():
    """ Return the full file name of the next log assuming NUMLOGSTODAY is correct """
    return todays_log_name() + "_" + str( 0 if NUMLOGSTODAY == 0 else NUMLOGSTODAY ) + "." + LOGFILEEXTENSION
    
def section(titleStr):
    borderStr = '=========='
    return borderStr + ' ' + str(titleStr) + ' ' + borderStr + endl

# = End Log =

# == End String ==


# == File Operation Logging ==

def count_todays_logs():
    global NUMLOGSTODAY
    count = 0
    namesInDir = os.listdir(SOURCEDIR)
    for name in namesInDir:
        if todays_log_name() in name:
            count += 1
    NUMLOGSTODAY = count
    print "Found", NUMLOGSTODAY, "logs with today's date."
 
CURRENTLOG = None # The current log file, only one should be open at a time
   
def open_new_log():
    """ Generate the next log file in the series, open for logging, and write preamble to file """
    global CURRENTLOG
    if not CURRENTLOG: # If there is no file currently open
        count_todays_logs()
        currentLogName = gen_log_name() # generate the name of the next log file
        CURRENTLOG = open( os.path.join( SOURCEDIR , currentLogName ) , 'w') # Open a new file in write mode
        # URL: http://stackoverflow.com/a/13891070
        CURRENTLOG.write( "Opened new file " + currentLogName + " at " + datetime.fromtimestamp(time.time()).strftime('%H:%M:%S') + endl )
        #CURRENTLOG.write( section( 'File Operations' ) + endl )
    else: # Else there was already a file open, warn the user
        print "open_new_log : There is already a log open!"
        
def close_current_log():
    """ Close the current log if there is one open and mark the global var closed """
    global CURRENTLOG
    if CURRENTLOG:
        CURRENTLOG.write( "Closed file at " + datetime.fromtimestamp(time.time()).strftime('%H:%M:%S') + endl )
        CURRENTLOG.close()
        CURRENTLOG = None # Mark the current log closed
    else:
        print "close_current_log : There was no log open!"

# == End Logging ==


# == Music File Organization ==

NUMPROCESSED = 0 # The number of files processed this session
PROCESSTIME = time.clock() # Time since the last milestone
MISCFOLDERNAME = "Various" # Name of the folder for files without a readable artist name
ERRLIST = [] # List of errors for this session
DISALLOWEDEXTS = ['txt', 'py'] # folders with these file extensions should not be moved from the source dir
DUPFOLDERNAME = "zzz_Duplicates" # folder name to store dupicate files

def repair_music_library_structure(srchDir, currLog):
    """ Walk the entire music library 'srchDir', restore to an assumed structure, write results to currLog """
    for dirName, subdirList, fileList in os.walk(srchDir):
        pass

def sort_all_songs(arg, dirname, names):
    pass
    """ Copy all songs in 'SOURCEDIR' to 'PARENTDIR', sorted by artist 
    
    This fuction is designed to be used with 'os.path.walk' in order the recursively search and process the source
    directory 
    
    Assumes that 'CURRENTLOG' is an open TXT file available for writing """
""" global SOURCEDIR, PARENTDIR, NUMPROCESSED, PROCESSTIME, CURRENTLOG, ERRLIST
    for item in names: # For each item in the present directory
        NUMPROCESSED += 1
        if NUMPROCESSED % 100 == 0: # Report the amount of time that it took to process the last 100 files
            print "Processed " + str(NUMPROCESSED) + " files. Last 100 in " + str(time.clock() - PROCESSTIME)
            PROCESSTIME = time.clock()
        namePath = os.path.join(dirname, item) # Reconstruct the full path of the current item
        #print "Processing " + str(namePath)
        extension = os.path.splitext(item)[1] # Retrieve the file extension of the current item
        if extension == '.mp3': # If found mp3
            audiofile = None # var for current file
            try: 
                #audiofile = eyeD3.core.load(namePath) # Ask eyeD3 to load and scan the current file for metadata
                #audiofile = eyeD3.load(namePath) # Ask eyeD3 to load and scan the current file for metadata
                audiofile = eyeD3.Tag()
                audiofile.link(namePath)
            except: # eyeD3 could not read the tags or otherwise load the file, report
                errMsg = "Problem reading " + str(namePath) + " tags!"
                print errMsg
                ERRLIST.append( errMsg )
                # URL, get exception details:http://stackoverflow.com/a/15890953
                type, value, traceback = sys.exc_info()
                ERRLIST.append('Python says: %s , %s , %s' % (str(type), str(value), str(traceback)))
                CURRENTLOG.write( errMsg + endl )
            if audiofile: #and audiofile.tag: # If file loaded and artist metadata found
                #artName = proper_artist_dir(audiofile.tag.artist) # format the artist's name for a directory name
                artName = proper_artist_dir( audiofile.getArtist() )
            else:
                artName = ""
            if len(artName) > 0: # If an appropriate artist name was generated
                artistPath = os.path.join(PARENTDIR, artName) # find the path to that artist's folder
            else:
                artistPath = os.path.join(PARENTDIR, MISCFOLDERNAME) # find the path to the 'misc' bin
            targetPath = os.path.join(artistPath, item) # generate a full destination path for the file
            if os.path.isfile(namePath): # only attempt to move files, not directories
                if os.path.exists(artistPath): # if the selected artist folder exists in the filesystem
                    if not os.path.exists(targetPath): # if the target filename does not exist
                        try: # Try to copy the file to the artist folder if exists
                            # URL: https://docs.python.org/2/library/shutil.html#shutil.move
                            shutil.move(namePath, targetPath) # Attempt to move the file
                            #shutil.copy2(namePath, targetPath)
                            CURRENTLOG.write( "Moved to " + str(targetPath) + endl )
                        except:
                            errMsg = "ERROR: Unable to move " + str(namePath)
                            print errMsg
                            ERRLIST.append( errMsg )
                            # URL, get exception details:http://stackoverflow.com/a/15890953
                            type, value, traceback = sys.exc_info()
                            ERRLIST.append('Python says: %s , %s , %s' % (str(type), str(value), str(traceback)))
                            CURRENTLOG.write( errMsg + endl )
                            #print "Unable to copy " #+ str(namePath)
                    # else target filename exists, but not same size, assume new version
                    elif os.path.getsize(namePath) != os.path.getsize(targetPath):
                        incVar = 0
                        while os.path.exists(targetPath): # rename until new!
                            incVar += 1
                            newName = os.path.splitext(item)[0] + str(incVar) + os.path.splitext(item)[1]
                            print "Attempt rename: " + newName
                            targetPath = os.path.join(artistPath, newName)
                        try: # Try to copy the file with a new name
                            shutil.move(namePath, targetPath)
                            CURRENTLOG.write( "Renamed and moved " + str(targetPath) + endl )
                            #print "Copied " #+ str(targetPath)
                        except:
                            errMsg = "ERROR: Unable to move " + str(namePath)
                            print errMsg
                            ERRLIST.append( errMsg )
                            # URL, get exception details:http://stackoverflow.com/a/15890953
                            type, value, traceback = sys.exc_info()
                            ERRLIST.append('Python says: %s , %s , %s' % (str(type), str(value), str(traceback)))
                            CURRENTLOG.write( errMsg + endl )
                    else: # else there is a file at the target location with the same name of the same size
                        duplicatePath = os.path.join( os.path.join(PARENTDIR, DUPFOLDERNAME) , item )
                        if not os.path.exists( os.path.join(PARENTDIR, DUPFOLDERNAME) ): # if there is no folder for duplicates
                            try:  # try to create a duplicates folder
                                os.mkdir( os.path.join(PARENTDIR, DUPFOLDERNAME) ) # try create dir 
                                CURRENTLOG.write( "Created dir " + str(os.path.join(PARENTDIR, DUPFOLDERNAME)) + endl )
                            except:
                                errMsg = "ERROR: Unable to create dir " + str( os.path.join(PARENTDIR, DUPFOLDERNAME) )
                                print errMsg
                                ERRLIST.append( errMsg )
                                # URL, get exception details:http://stackoverflow.com/a/15890953
                                type, value, traceback = sys.exc_info()
                                ERRLIST.append('Python says: %s , %s , %s' % (str(type), str(value), str(traceback)))
                                CURRENTLOG.write( errMsg + endl )
                        try: # Try to copy the file to the artist folder if exists
                            # URL: https://docs.python.org/2/library/shutil.html#shutil.move
                            shutil.move(namePath, duplicatePath) # Attempt to move the file
                            #shutil.copy2(namePath, targetPath)
                            CURRENTLOG.write( "Duplicate moved to " + str(duplicatePath) + endl )
                        except:
                            errMsg = "ERROR: Unable to move " + str(namePath)
                            print errMsg
                            ERRLIST.append( errMsg )
                            # URL, get exception details:http://stackoverflow.com/a/15890953
                            type, value, traceback = sys.exc_info()
                            ERRLIST.append('Python says: %s , %s , %s' % (str(type), str(value), str(traceback)))
                            CURRENTLOG.write( errMsg + endl )
                        
                else: # else folder does not exist
                    try:  
                        # try create dir then copy
                        os.mkdir(artistPath)
                        CURRENTLOG.write( "Created dir " + str(artistPath) + endl )
                        shutil.move(namePath, targetPath)
                        CURRENTLOG.write( "Moved " + str(targetPath) + endl )
                    except:
                        errMsg = "Unable to move " + str(namePath)
                        print errMsg
                        ERRLIST.append( errMsg )
                        # URL, get exception details:http://stackoverflow.com/a/15890953
                        type, value, traceback = sys.exc_info()
                        ERRLIST.append('Python says: %s , %s , %s' % (str(type), str(value), str(traceback)))
                        CURRENTLOG.write( errMsg + endl )
        else: # else, file is not an mp3
            print "DEBUG: Founf file not MP3 at " + str(namePath)
            typePath = os.path.join(PARENTDIR, extension[1:].upper()) # Create a path based on file type
            if extension[1:].lower() not in DISALLOWEDEXTS: # do not allow logs or scripts to be moved
                if os.path.exists(typePath):
                    try: # Try to copy the file to the type folder if exists
                        shutil.move(namePath, os.path.join(typePath, item))
                        CURRENTLOG.write(  "Moved to " + str(targetPath) + endl )
                    except:
                        errMsg =  "Unable to move " + str(namePath) 
                        print errMsg
                        ERRLIST.append( errMsg )
                        # URL, get exception details:http://stackoverflow.com/a/15890953
                        type, value, traceback = sys.exc_info()
                        ERRLIST.append('Python says: %s , %s , %s' % (str(type), str(value), str(traceback)))
                        CURRENTLOG.write( errMsg + endl )
                else:
                    try: # else folder does not exist, try create dir then copy
                        os.mkdir(typePath)
                        shutil.move(namePath, os.path.join(typePath, item))
                        CURRENTLOG.write( "Moved " + str(os.path.join(typePath, item)) + endl )
                    except:
                        errMsg =  "Unable to move " + str(namePath) 
                        print errMsg
                        ERRLIST.append( errMsg )
                        # URL, get exception details:http://stackoverflow.com/a/15890953
                        type, value, traceback = sys.exc_info()
                        ERRLIST.append('Python says: %s , %s , %s' % (str(type), str(value), str(traceback)))
                        CURRENTLOG.write( errMsg + endl )
"""
    
# == End File Organization ==


# == Directory Cleanup ==

ALLEMPTYDIRS = [] # list of directories to delete

def find_empty_dirs(searchDir, safeToDel = False):
    pass
    """ Find all the empty directories and tag them for deletion in 'ALLEMPTYDIRS' 
    
    Note: Because the searching and deleting functions are separate, a dir full of only empty dirs will not appear empty,
    therefore this function must be run after each lowest level of empty dir deletions has taken place. This is not 
    efficient """
""" global ALLEMPTYDIRS # Allow editing of directory list
    namesInDir = os.listdir(searchDir) # get a list of items in 'searchDir'
    if len(namesInDir) > 0: # if items found
        for name in namesInDir: # for each of the items found
            subPath = os.path.join(searchDir, name) # reconstruct the complete path to the item
            if os.path.isdir(subPath): # if the complete path is a directory
                find_empty_dirs(subPath, True) # recurse on that directory, all dirs below top level are deletable
        namesInDir = os.listdir(searchDir) # reset list of items in 'searchDir'
        if len(namesInDir) == 0 and safeToDel: # If we have erased all the items, then
            ALLEMPTYDIRS.append( searchDir ) # Add this to the list of dirs to delete
    else: # else, there were no items found in this dir, delete it if safe
        if safeToDel:
            ALLEMPTYDIRS.append( searchDir )  # Add this to the list of dirs to delete
    # After operating on all the names in this dir
"""       
def purge_empty_dirs(searchDir):
    pass
    """ Search for and delete all empty dirs in 'searchDir', recursively """
""" global ALLEMPTYDIRS
    find_empty_dirs(searchDir)
    if len(ALLEMPTYDIRS) == 0:
        print "purge_empty_dirs : No empty dirs to delete!"
    elif not CURRENTLOG:
        print "purge_empty_dirs : No log file open!"
    else: # else we have dirs to delete and a valid log file
        while len(ALLEMPTYDIRS) > 0:
            for emptyDir in ALLEMPTYDIRS:
                try:
                    shutil.rmtree(emptyDir) # try removing the dir
                    CURRENTLOG.write( "Removed directory " + str(emptyDir) + endl )
                except OSError: # if there was an error, log it
                    errMsg = "Unable to remove directory " + str(emptyDir) + endl
                    print errMsg
                    ERRLIST.append( errMsg )
                    CURRENTLOG.write( errMsg + endl )
            ALLEMPTYDIRS = [] # Reset empty dirs
            find_empty_dirs(searchDir)
"""
# == End Cleanup ==


# == Main ==

# ~ Prep Work ~
open_new_log()

"""
# Check that conditions are met for running the file sorting function
if not os.path.exists(SOURCEDIR):
    print "Source path " + str(SOURCEDIR) + " not found!"
elif not os.path.exists(PARENTDIR):
    print "Destination path " + str(PARENTDIR) + " not found!"
elif not CURRENTLOG:
    print "No log file open!"
else:
    # Perform file organization operations    
    CURRENTLOG.write( section('File Operations') )
    os.path.walk(SOURCEDIR, sort_all_songs, False)
    procMsg =  "Processed " + str(NUMPROCESSED) + " files."
    CURRENTLOG.write( endl + procMsg + endl + endl )
    # Find and erase all empty dirs
    CURRENTLOG.write( section('Cleanup') )
    #find_empty_dirs(SOURCEDIR)    
    purge_empty_dirs(SOURCEDIR)
    # Log all the errors encountered during organization and cleanup
    CURRENTLOG.write( section('Errors') )
    for err in ERRLIST:
        CURRENTLOG.write( err + endl )
    CURRENTLOG.write( section('End') )
"""
# ~ Cleanup Work ~
close_current_log() # Record time of script end and close the log file

# == End Main ==