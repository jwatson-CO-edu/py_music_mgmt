# -*- coding: utf-8 -*-
"""
file-ext-logger_2016-01.py , Built on Spyder for Python 2.7
James Watson, 2016 January
Search containing directory and all sub-directories for files with a certain extension (MP3) log results for further
consideration. No file operations performed

  == NOTES ==
* 
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
import os, time, shutil
#from sys import path
from datetime import date, datetime
# Special Libraries
import eyeD3

# ~ Shortcuts and Aliases ~
endl = os.linesep # URL: http://stackoverflow.com/a/1223303

# = Setup Directories =
SOURCEDIR = os.path.dirname(os.path.abspath(__file__)) # URL: http://stackoverflow.com/a/7783326
#PARENTDIR = os.path.dirname(SOURCEDIR)

print "Source Dir  : ", str(SOURCEDIR) # directory containing the script file
#print "Library Dir : ", str(PARENTDIR) # directory containing that directory
# = End Directories =

# == String Processing ==

# = Log Names =

FILEPREFIX = "MP3-Location-Log_"

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


# == File Location Logging ==

NUMPROCESSED = 0 # The number of files processed this session
PROCESSTIME = time.clock() # Time since the last milestone
#MISCFOLDERNAME = "Various" # Name of the folder for files without a readable artist name
ERRLIST = [] # List of errors for this session
#DISALLOWEDEXTS = ['txt', 'py'] # folders with these file extensions should not be moved from the source dir'
DESIREDEXTS = ['mp3', 'flac', 'ogg', 'aac', 'm4p', 'm4a'] # File extensions to search for
#DUPFOLDERNAME = "zzz_Duplicates" # folder name to store dupicate files

def search_extensions_and_log(arg, dirname, names):
    """ Search SOURCEDIR and all subdirectories for files with extensions matching 'DESIREDEXTS' and log the type of 
    file found along with the location it was found in. 
    
    This fuction is designed to be used with 'os.path.walk' in order the recursively search and process the source
    directory 
    
    Assumes that 'CURRENTLOG' is an open TXT file available for writing """
    
    global NUMPROCESSED, PROCESSTIME, CURRENTLOG, ERRLIST
    
    

# FIXME : START HERE