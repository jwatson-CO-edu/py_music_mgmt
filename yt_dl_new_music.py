#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ~~ Future First ~~
from __future__ import division , unicode_literals # Future imports must be called before everything else, including triple-quote docs!

__progname__ = "yt_dl_new_music.py"
__version__  = "2018.10" 
__desc__     = "Fetch videos from youtube and convert to music files , hopefully split by track"
"""
James Watson , Template Version: 2018-05-14
Built on Wing 101 IDE for Python 2.7

~ Dependencies ~
    Packages: numpy , youtube-dl , google-api-python-client , oauth2client , urllib2 
    Programs: FFmpeg
"""


"""  
~~~ Developmnent Plan ~~~

[Y] Test download at the command line
[Y] Fetch example from the docs
    [Y] Test the example under linux
[Y] Build Tracklist
    [Y] Establish YouTube API with key
    [Y] Download video descriptions
    [Y] Locate timestamps in the description or comments
        [Y] Search for timestamp candidates
    [Y] Discern artist & track for each listing
	[Y] GraceNote Test
	[Y] Separate candidate artist and track
	[Y] Query (1,2) and (2,1) to see which one returns a hit
        [Y] pygn pull request "__init__.py": https://github.com/cweichen/pygn/pull/15
            [Y] Fork pygn
            [Y] Submit request
	{ } artist-track fallback: 
            { } MusicBrainz - Open Access Database
            { } Google , Wikipedia?
[ ] Split songs by track
    [ ] If no tracklist is found in description or toplevel comments, then Download video comment threads
    [ ] Assign most likely artist and track names
    [ ] Hash of known artist names
    [ ] Handle one-artist albums
    [ ] Handle one-song videos
    [ ] Find example of how to split songs by track
        [ ] URL , Split songs with multiprocess: https://codereview.stackexchange.com/q/166158
        [ ] Test with dummy times
    [ ] Split audio by confirmed timestamps
    [ ] Load id3 metadata for individual tracks  
        [ ] Artist
        [ ] Title
        [ ] Album
        [ ] Album Art (Or YT thumbnail) , Can this be obtained from GN?
        [ ] Additional GN data
[Y] Build a list of music to listen to
    [Y] Study Jams
    [Y] Establish a input playlist format - COMPLETE:
        # Comment
        <URL>,<SEQNUM>
    [Y] Parse a file - COMPLETE , made sure that strings are ASCII
    [Y] Review list
    [Y] Artists to try
[Y] Make API connection functions persistent functors - Not possible, just run connections once per script
    [Y] Write an IDE object persistence test - Objects in the script cannot persist between runs of the script, console is erased each run
[N] Adjust program behavior
    [N] Limit download speed with random spacing between requests - ffmpeg conversion takes a considerable time
    [N] Change user agent to FF browser - Does not seem to be necessary at this point given infrequency of use
[ ] Cache scraped data && Pickle
    [Y] URL
    [N] HTML
    [Y] API objects
        [Y] Metadata
        [Y] Comment info
    [ ] Identified categories
        [ ] Timestamps
    [Y] Locations of raw files
        [Y] Check if exist && flag
    [Y] Unpickle on startup of each stage
    [Y] Cache flag
    { } WARN: Switch to database at 10k entries
[Y] Store raw files
[Y] Remove log files from repo
{ } Bandcamp Scraper

~~~ Test Plan ~~~
NOTE: This utility must be run in Linux
[Y] 1. Download and Store - STAGE 1 COMPLETE!
    [Y] Open API
    [Y] Check Write location
    [Y] Create Dir for each video
    [Y] Raw File
    [Y] Raw File Location
    [Y] File Success
    [Y] URL
    [Y] Description Data
    [Y] Comment Data
    [Y] LOG
    [Y] Pickle all data
    [N] Close API - There is no close function
[ ] 2. Process and Split
    [ ] Restore Pickle
    [ ] Tracklist Success
    [ ] Tracklist Data
    [ ] Split File Success
    [ ] Split File Metadata
    [ ] Split File Locations
[ ] 3. Edit Metadata and Finish
    [ ] Add ID3 metadata
    [ ] Copy all output files to the Song Inbox
"""

# === Init Environment =====================================================================================================================
# ~~~ Prepare Paths ~~~
import sys , os.path , os
SOURCEDIR = os.path.dirname( os.path.abspath( '__file__' ) ) # URL, dir containing source file: http://stackoverflow.com/a/7783326
PARENTDIR = os.path.dirname( SOURCEDIR )
# ~~ Path Utilities ~~
def prepend_dir_to_path( pathName ): sys.path.insert( 0 , pathName ) # Might need this to fetch a lib in a parent directory

# ~~~ Imports ~~~
# ~~ Standard ~~
from math import pi , sqrt
import shutil
from random import randrange
from time import sleep
from warnings import warn

try:
    from urllib2 import urlopen
except:
    try:
        from urllib.request import urlopen
    except:
        print( "COULD NOT IMPORT ANY URL OPENER" )
        
# ~~ Special ~~
import numpy as np
import youtube_dl
# https://medium.com/greyatom/youtube-data-in-python-6147160c5833
try:
    from apiclient.discovery import build
    from apiclient.errors import HttpError
    print "Loaded 'apiclient'! (Google)"
except:
    try:
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
        print "Loaded 'googleapiclient'!"
    except:
        print( "COULD NOT IMPORT API UNDER EITHER ALIAS" )
from oauth2client.tools import argparser
print "Loaded 'oauth2client'!"
import pygn
from pygn.pygn import register , search
print "Loaded 'pygn'! (GraceNote)"
# ~~ Local ~~
prepend_dir_to_path( SOURCEDIR )
from marchhare.marchhare import ( parse_lines , ascii , sep , is_nonempty_list , pretty_print_dict , unpickle_dict , yesno ,
                                  validate_dirs_writable , LogMH , Stopwatch , nowTimeStampFine , struct_to_pkl , strip_EXT , touch , )
from retrieve_yt import *

# ~~ Constants , Shortcuts , Aliases ~~
EPSILON = 1e-7
infty   = 1e309 # URL: http://stackoverflow.com/questions/1628026/python-infinity-any-caveats#comment31860436_1628026
endl    = os.linesep

# ~~ Script Signature ~~
def __prog_signature__(): return __progname__ + " , Version " + __version__ # Return a string representing program name and verions

# ___ End Init _____________________________________________________________________________________________________________________________


# == Program Vars ==



# ~ Session Vars ~

class Session:
    """ Flags and vars representing a session , Also acts as a repo for what would otherwise be globals """
    
    def __init__( self ):
        """ Create a default empty session """
        
        # ~ API Connection Vars ~
        self.GOOG_KEY_PATH            = "APIKEY.txt" 
        self.GRNT_KEY_PATH            = "GNWKEY.txt"
        self.DEVELOPER_KEY            = None
        self.YOUTUBE_API_SERVICE_NAME = "youtube"
        self.YOUTUBE_API_VERSION      = "v3"
        self.METADATA_SPEC            = 'snippet,contentDetails,statistics'
        self.COMMENT_THREAD_SPEC      = 'id,snippet,replies'
        self.COMMENT_LIST_SPEC        = 'snippet'
        
        # ~ Authentication Vars ~
        self.authDict = {}
        self.youtube  = None
        self.gnKey    = None
        self.gnClient = None
        self.gnUser   = None        
         
        # ~ Session Vars ~
        self.ACTIVE_SESSION = False
        self.SESSION_PATH   = "session.txt"        
        
        # ~ Binary Output ~
        self.RAW_FILE_DIR     = ""
        self.CHOPPED_SONG_DIR = ""
        self.PICKLE_DIR       = ""
        
        # ~ Processing Metadata ~
        self.ACTIVE_PICKLE_PATH = ""
        self.ARTIST_PICKLE_PATH = ""
        self.METADATA           = {} 
        self.ARTISTS            = {}        
        
        # ~ Logging ~
        self.LOG_DIR = ""
        self.LOG     = LogMH() # Instantiate a global logger object
        
        # ~ Processing Vars ~
        self.YDL_OPTS = { 
            # Options for youtube-dl
            'format': 'bestaudio/best',
            'postprocessors': [ {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            } ] ,
            'logger': MyLogger(),
            'progress_hooks': [my_hook],
        }

# __ End Vars __

def load_session( sessionPath ):
    """ Read session file and populate session vars """
    session = Session()
    sesnDict = comma_sep_key_val_from_file( sessionPath );          print "Loaded session file:" , sessionPath
    session.RAW_FILE_DIR       = sesnDict['RAW_FILE_DIR'];          print "RAW_FILE_DIR:" , session.RAW_FILE_DIR
    session.CHOPPED_SONG_DIR   = sesnDict['CHOPPED_SONG_DIR'];      print "CHOPPED_SONG_DIR:" , session.CHOPPED_SONG_DIR
    session.PICKLE_DIR         = sesnDict['PICKLE_DIR'];            print "PICKLE_DIR:" , session.PICKLE_DIR 
    session.ACTIVE_PICKLE_PATH = sesnDict['ACTIVE_PICKLE_PATH'];    print "ACTIVE_PICKLE_PATH:" , session.ACTIVE_PICKLE_PATH
    session.LOG_DIR            = sesnDict['LOG_DIR'];               print "LOG_DIR" , session.LOG_DIR
    session.ACTIVE_SESSION     = sesnDict['ACTIVE_SESSION'];        print "ACTIVE_SESSION:" , yesno( session.ACTIVE_SESSION )
    session.ARTIST_PICKLE_PATH = sesnDict['ARTIST_PICKLE_PATH'];    print "ARTIST_PICKLE_PATH:" , session.ARTIST_PICKLE_PATH
    return session

def open_all_APIs( sssn ):
    """ Open an API connection for {Google , GraceNote} """
    # NOTE: 'load_session' must be run first
    try:
        # 2. Init Google API connection
        sssn.authDict = comma_sep_key_val_from_file( sssn.GOOG_KEY_PATH ) # "APIKEY.txt"
        sssn.DEVELOPER_KEY = sssn.authDict['key']
        #print( authDict )
        youtube = build( sssn.YOUTUBE_API_SERVICE_NAME , 
                         sssn.YOUTUBE_API_VERSION , 
                         developerKey = sssn.DEVELOPER_KEY )
        # 3. Init GraceNote API Connection
        sssn.gnKey = comma_sep_key_val_from_file( sssn.GRNT_KEY_PATH ) # "GNWKEY.txt"
        sssn.gnClient = sssn.gnKey[ 'clientID' ] #_ Enter your Client ID here '*******-************************'
        sssn.gnUser   = register( sssn.gnClient ) # Registration should not be done more than once per session      
        
        print "API Connection SUCCESS!"
        
    except Exception as ex:
        print "API Connection FAILURE!" , str( ex )

def default_session():
    """ Set the session vars to reasonable values """
    session = Session()
    session.RAW_FILE_DIR       = "output";                           print "RAW_FILE_DIR:" , cRAW_FILE_DIR
    session.CHOPPED_SONG_DIR   = session.RAW_FILE_DIR + "/chopped";  print "CHOPPED_SONG_DIR:" , session.CHOPPED_SONG_DIR
    session.PICKLE_DIR         = session.RAW_FILE_DIR;               print "PICKLE_DIR:" , session.PICKLE_DIR 
    session.ACTIVE_PICKLE_PATH = "output/session.pkl";               print "ACTIVE_PICKLE_PATH:" , session.ACTIVE_PICKLE_PATH
    session.LOG_DIR            = "logs";                             print "LOG_DIR" , session.LOG_DIR
    session.ACTIVE_SESSION     = bool( int( 1 ) );                   print "ACTIVE_SESSION:" , yesno( session.ACTIVE_SESSION )
    session.ARTIST_PICKLE_PATH = "output/artists.pkl";               print "ARTIST_PICKLE_PATH:" , session.ARTIST_PICKLE_PATH
    return session    
    
def save_session( session ):
    """ Write session vars to the session file """
    # 1. If a file exists at this path, erase it
    if os.path.isfile( session.SESSION_PATH ):
        print "Session" , session.SESSION_PATH , "was overwritten!"
        os.remove( session.SESSION_PATH )
    # 2. Write each line
    f = open( session.SESSION_PATH , "w+" )
    f.write( 'RAW_FILE_DIR'       + ',' + str( session.RAW_FILE_DIR )        + '\n' )
    f.write( 'CHOPPED_SONG_DIR'   + ',' + str( session.CHOPPED_SONG_DIR )    + '\n' )
    f.write( 'PICKLE_DIR'         + ',' + str( session.PICKLE_DIR )          + '\n' )
    f.write( 'ACTIVE_PICKLE_PATH' + ',' + str( session.ACTIVE_PICKLE_PATH )  + '\n' )
    f.write( 'LOG_DIR'            + ',' + str( session.LOG_DIR )             + '\n' )
    f.write( 'ACTIVE_SESSION'     + ',' + str( session.ACTIVE_SESSION )      + '\n' )
    f.write( 'ARTIST_PICKLE_PATH' + ',' + str( session.ARTIST_PICKLE_PATH )  + '\n' )
    print "Session saved to" , session.SESSION_PATH
  
def verify_session_writable( sssn ):
    """ Make sure that we can write to the relevant directories """
    allWrite = validate_dirs_writable(  
        os.path.join( SOURCEDIR , sssn.RAW_FILE_DIR )     ,
        os.path.join( SOURCEDIR , sssn.CHOPPED_SONG_DIR ) ,
        os.path.join( SOURCEDIR , sssn.PICKLE_DIR )       ,
        os.path.join( SOURCEDIR , sssn.LOG_DIR )          ,
    )
    print "Session dirs writable:" , yesno( allWrite )
    return allWrite




# ===== STAGE 1 ============================================================================================================================

# == Stage 1 Vars ==



# __ End Vars __

def set_session_active( active = 1 ):
    """ Set the session active flag """
    global ACTIVE_SESSION , SESSION_PATH
    ACTIVE_SESSION = bool( active )
    
def begin_session( inputPath ):
    """ Set all vars that we will need to run a session """
    # 2. Instantiate a timer
    dlTimer = Stopwatch()   
    # 3. Construct session path
    SESSION_PATH = strip_EXT( inputPath ) + "_session.txt"
    # 4. Load session  &&  Activate
    try:
        session = load_session( SESSION_PATH )
    except IOError:
        touch( SESSION_PATH )
        session = default_session()
    session.SESSION_PATH = SESSION_PATH
    set_session_active( True )
    # 4. Construct pickle path
    session.ACTIVE_PICKLE_PATH = session.RAW_FILE_DIR + '/' + strip_EXT( str( os.path.split( inputPath )[-1] ) ) + "_metadata.pkl"
    # 5. Unpickle session metadata
    session.METADATA = unpickle_dict( session.ACTIVE_PICKLE_PATH ) 
    if session.METADATA:
        session.LOG.prnt( "Found cached metadata at" , session.ACTIVE_PICKLE_PATH , "with" , len( session.METADATA ) , "entries" )
    else:
        session.LOG.prnt( "NO cached metadata at" , session.ACTIVE_PICKLE_PATH )
    # Unpickle artist set
    session.ARTISTS = unpickle_dict( session.ARTIST_PICKLE_PATH ) 
    if session.ARTISTS:
        session.LOG.prnt( "Found cached artist set at" , session.ARTIST_PICKLE_PATH , "with" , len( session.ARTISTS ) , "entries" )
    else:
        session.LOG.prnt( "NO cached artist set at" , session.ARTIST_PICKLE_PATH )
    #  1.1. Activate session
    session.ACTIVE_SESSION = True
    #  2. Check Write locations
    dirsWritable = verify_session_writable( session )
    return session , dirsWritable , dlTimer
    
def close_session( sssn ):
    """ Cache data and write logs """
    # 23. Pickle all data
    struct_to_pkl( sssn.METADATA , sssn.ACTIVE_PICKLE_PATH )
    struct_to_pkl( sssn.ARTISTS  , sssn.ARTIST_PICKLE_PATH )
    # 24. Save session && output log data
    save_session( sssn )
    sssn.LOG.out_and_clear( os.path.join( sssn.LOG_DIR , "YouTube-Music-Log_" + nowTimeStampFine() + ".txt" ) )     
    
def Stage_1_Download_w_Data( inputFile ,
                             minDelay_s = 20 , maxDelay_s = 180 ):
    """ Check environment for download , Fetch files and metadata , Save files and metadata """
    # NOTE: You may have to run this function several times, especially for long lists of URLs
    doSleep = False # ffmpeg conversion seems to be a sufficient wait time, especially for large files 
    # DEBUG
    dbugLim = False
    limit = 1
    count = 0
    #  0. Load session
    session , dirsWritable , dlTimer = begin_session( inputFile )
    open_all_APIs( session )
    #  1. Indicate file
    session.LOG.prnt( "Processing" , inputFile , "..." )
    #  2. How much metadat?   
    numEntry = len( session.METADATA )
    session.LOG.prnt( "Current metadata has" , numEntry , "entries." )
    #  3. Determine if dirs writable
    if not dirsWritable:
        session.LOG.prnt( "ERROR: Program does NOT have permission to modify the indicated directories!" )
        return False
    else:
        session.LOG.prnt( "Program has appropriate directory permissions." )
    #  3. Process input file
    lstMeta = init_metadata_from_list( inputFile )
    inCount = len( lstMeta )
    session.LOG.prnt( "Read input file with" , inCount , "entries" )
    
    
    # FIXME: dict_A_add_B_new_only( dctA , dctB )
    
    ##  4. Init downloaded
    #ydl = youtube_dl.YoutubeDL( YDL_OPTS )
    ##  5. For each entry
    #LOG.prnt( "## Media Files ##" )
    #for enDex , entry in enumerate( entries ):
        ##  6. If the debug file limit exceeded, exit loop
        #if dbugLim and ( not count < limit ):
            #break        
        #LOG.prnt( '#\n# Entry' , enDex+1 , 'of' , inCount , '#' )
        #enID = entry['id']
        ##  7. URL
        #enURL = entry['url']        
        #cacheMod = False        
        #try:
            ##  8. Attempt to fetch cached data for this entry
            #if( enID in METADATA ):
                #LOG.prnt( "Found cached data for" , enID )
                #enCache = METADATA[ enID ]
            #else:
                #enCache = None
                #cacheMod = True
            ##  9. Create Dir
            #enRawDir = os.path.join( RAW_FILE_DIR , enID )
            #if not os.path.isdir( enRawDir ):
                #try:  
                    #os.mkdir( enRawDir )
                #except OSError:  
                    #LOG.prnt(  "Creation of the directory %s failed" % enRawDir )
                #else:  
                    #LOG.prnt(  "Successfully created the directory %s " % enRawDir )            
            ## 10. Download Raw MP3 File
            ## 11. If this file does not have an entry, the raw file exists, and the file is ok, then download
            #if not ( enCache and enCache['fSuccess'] ):
                #cacheMod = True
                #LOG.prnt( "No file from" , entry['url'] , ", dowloading ..." )
                #dlTimer.start()
                #ydl.download( [ entry['url'] ] )  # This function MUST be passed a list!
                #enElapsed = dlTimer.elapsed()
                #LOG.prnt( "Downloading and Processing:" , enElapsed , "seconds" )
                ## 12. Locate and move the raw file
                #fNames = list_all_files_w_EXT( SOURCEDIR , [ 'MP3' ] )
                #if len( fNames ) > 0:
                    ## Assume that the first item is the newly-arrived file
                    #fSaved = fNames[0]
                    ## 13. Raw File End Destination
                    #enDest = os.path.join( enRawDir , fSaved )
                    #enCpSuccess = False # I. File Success
                    #try:
                        #shutil.move( fSaved , enDest )
                        #enCpSuccess = True
                        #LOG.prnt( "Move success!:" , fSaved , "--to->" , enDest )
                    #except Exception:
                        #enCpSuccess = False
                #else:
                    #LOG.prnt( "No downloaded MP3s detected!" )
                    #enDest = None
                    #enCpSuccess = False            
            ## 14. else skip download
            #else:
                #LOG.prnt( "Raw file from" , entry['url'] , "was previously cached at" , enCache['Timestamp'] )
                #enDest      = None
                #enCpSuccess = True
                #enElapsed   = None
            ## 15. Fetch Description Data
            #if not ( enCache and enCache['Metadata'] ):
                #cacheMod = True
                #enMeta = fetch_metadata_by_yt_video_ID( entry['id'] )
            #else:
                #enMeta = enCache['Metadata']
            ## 16. Verify that the downloaded file is as long as the original video
            #enDur = parse_ISO8601_timestamp( extract_video_duration( enMeta ) ) 
            #print "Duration:" , enDur
            ## 17. Fetch Comment Data
            #if not ( enCache and enCache['Threads'] ):
                #cacheMod = True
                #enComment = fetch_comment_threads_by_yt_ID( entry['id'] )
            #else:
                #enComment = enCache['Threads']
            ## 18. Get time and date for this file
            #enTime = nowTimeStampFine()
            #LOG.prnt( "Recorded Time:" , enTime )
            ## 19. Add file data to a dictionary
            #METADATA[ enID ] = {
                #'ID' :        enID ,
                #'RawPath' :   enDest if enDest else enCache['RawPath'] ,
                #'fSuccess' :  enCpSuccess ,
                #'ProcTime' :  enElapsed if enElapsed else enCache['ProcTime'] ,
                #'URL' :       enURL ,
                #'Metadata' :  enMeta ,
                #'Threads' :   enComment ,
                #'Timestamp' : enTime if cacheMod else enCache['Timestamp'] , 
                #'Duration' :  enDur
            #}
            ## 20. Sleep (if requested)
            #if doSleep:
                #sleepDur = randrange( minDelay_s , maxDelay_s+1 )
                #LOG.prnt( "Sleeping for" , sleepDur , "seconds" )
                #sleep( sleepDur )
            ## 21. Increment counter
            #count += 1
            #LOG.prnt( "# ~~~~~" )   
        ## Need to catch errors here so that the data from the already processed files in not lost
        #except Exception as err:
            ## 22. Add file data to a dictionary
            #METADATA[ enID ] = {
                #'ID' :        enID ,
                #'RawPath' :   None ,
                #'fSuccess' :  False ,
                #'ProcTime' :  None ,
                #'URL' :       enURL ,
                #'Metadata' :  None ,
                #'Threads' :   None ,
                #'Timestamp' : nowTimeStampFine() , 
                #'Duration' :  timestamp_dict( 0,0,0 )
            #}            
            #LOG.prnt( "ERROR: There was an error processing the item _ " , enID , "\n" , err )
            
    # Pickle data and write files
    close_session( session )

# _____ END STAGE 1 ________________________________________________________________________________________________________________________


# ===== STAGE 2 ============================================================================================================================

"""
~~~ DEV PLAN ~~~
[ ] Artist Store: set <--> pkl
[ ] Artist Lookup
[ ] Track Edit Menu
[ ] Tracklist Complete Flag
"""

ARTIST_SET = set([])



def Stage_2_Separate_and_Tag():
    """ Process each of the downloaded raw files: 1. Separate into songs , 2. Apply appropriate ID3 tags , 3. Save """
    # 0. Setup debug vars
    global LOG , METADATA
    LOG = LogMH()
    dlTimer = Stopwatch()
    dbugLim = False
    dbSuppressLog = False
    limit = 1
    count = 0
    stampCount = 0
    # 1. Setup diagnostic vars <-- Pickle these so that we can come back for addition
    FAILED_DL_ID    = []
    FAILED_TRACK_ID = []
    FAILED_SEP_ID   = []
    FULL_SUCCESS_ID = []
    # 2. Retreive session vars and cached metadata
    # 2.1. Activate session
    ACTIVE_SESSION = True    
    set_session_active( True )
    #  1. Load session
    session , dirsWritable , dlTimer = begin_session()
    numEntry = len( METADATA )
    if not dirsWritable:
        return False
    # 4. For every cached entry
    shortCount = 0
    session.LOG.prnt( "~~~" )
    for enID , enCache in METADATA.iteritems():
        if not dbSuppressLog: LOG.prnt( "Processing" , enID , "..." )
        enMeta  = enCache['Metadata']
        enTitle = get_video_title( enMeta )
        enCache['Title'] = enTitle
        # 5. Check if the download was a success
        if enCache['fSuccess']:
            if not dbSuppressLog: LOG.prnt( "Raw file from" , enCache['URL'] , "was previously cached at" , enCache['Timestamp'] )
            # If there was not a previously cached tracklist
            if ( 'TrackSuccess' not in enCache ) or ( not enCache['TrackSuccess'] ):
                # 6. Check for a tracklist  &&  Mark if found
                stamps = timestamps_from_cached_item( enCache )
                numStamp = len( stamps )
                if not dbSuppressLog: LOG.prnt( "Found" , numStamp , "stamps for" , enID )
                if numStamp > 1:
                    enCache['stampsFound']  = True
                    enCache['TrackSuccess'] = True
                    enCache['Tracklist']    = stamps 
                    process_entry_tracklist( enCache , stamps )
                else:
                    enCache['stampsFound'] = False
                    enCache['Tracklist']   = [] 
                    # 7. Check if it is a short video ( <= 15 min )
                    if timestamp_leq( enCache['Duration'] , timestamp_dict( 0 , 15 , 0 ) ):
                        shortCount += 1
                        components = extract_candidate_artist_and_track( enTitle )
                        print "~ Short Video ~"
                        print "Title:" , enCache['Title']
                        print "Desc:" , extract_description_lines( enCache['Metadata'] )
                        
                        # TODO: HANDLE SHORT VIDEOS WITH NO TRACK DATA
                        
                    else:
                        print "Long and unlabeled"
                        print "Title:" , enCache['Title']
                        print "Desc:" , extract_description_lines( enCache['Metadata'] )
                        
                        # TODO: HANDLE LONG VIDEOS WITH NO TRACK DATA
                        
            # else there was a cached tracklist found, count
            else:
                stampCount += 1
                process_entry_tracklist( enCache , enCache['Tracklist'] )                
                
        # I. else skip
        else:
            LOG.prnt( "Raw file from" , enCache['URL'] , ", Retrieval failed!" )
        if not dbSuppressLog: LOG.prnt( "~~~" )
    # I. Write log file
    session.LOG.prnt( "Found stamps for" , stampCount , "of" , numEntry , "cached items" )
    session.LOG.prnt( "Of video without stamps:" , shortCount , "were short" )
    session.LOG.prnt( numEntry - ( stampCount + shortCount ) , "possibly without song data!" , 
              ( numEntry - ( stampCount + shortCount ) ) / numEntry * 100.0 , "%" )
    # I. Pickle with new metadata
    # I. Write session vars
    close_session( session )
    
# _____ END STAGE 2 ________________________________________________________________________________________________________________________


# === Main Application =====================================================================================================================

if __name__ == "__main__":
    print( __prog_signature__() )
    termArgs = sys.argv[1:] # Terminal arguments , if they exist
    
    # 1. Open API connections ()
    if 0:
        open_all_APIs( GOOG_KEY_PATH , GRNT_KEY_PATH )
        
    # ~~~ Stage 0: Testing ~~~
    if 0:
        session = load_session( SESSION_PATH )
        set_session_active( True )
        if os.path.isfile( ACTIVE_PICKLE_PATH ):
            METADATA = unpickle_dict( ACTIVE_PICKLE_PATH ) 
            print "Found cached metadata at" , ACTIVE_PICKLE_PATH , "with" , len( METADATA ) , "entries" 
            numEntry = len( METADATA )
        else:
            print "NO cached metadata at" , ACTIVE_PICKLE_PATH , ", Empty dict" 
            METADATA = {} 
        if METADATA:
            #for enID , entry in METADATA.iteritems():
                #scrape_and_check_timestamps_cmnts( entry['Threads'] )
                #break
            if 1:
                repopulate_duration( METADATA )
                struct_to_pkl( METADATA , ACTIVE_PICKLE_PATH )
    
    # ~~~ Stage 1: Downloading ~~~
    if 1:
        Stage_1_Download_w_Data( "input/url_src_02.txt" ,
                                 minDelay_s = 30 , maxDelay_s = 60 )
    
    # ~~~ Stage 2: Processing ~~~
    if 0:
        Stage_2_Separate_and_Tag()
    

# ___ End Main _____________________________________________________________________________________________________________________________


# === Spare Parts ==========================================================================================================================

## 1. Load video playlist
#entries = process_video_list( "input/url_sources.txt" )

## 2. Set test entry
#entry = entries[8]    

## 3. Open APIs
#open_all_APIs( "APIKEY.txt" , "GNWKEY.txt" )
#print "Created a YouTube API connection with key  " , youtube._developerKey 
#print "Created a GraceNote API connection with key" , gnKey    

## 3. Fetch video metadata
#result = fetch_metadata_by_yt_video_ID( entry['id'] ) 

## Fetch comment threads
#allThreads = fetch_comment_threads_by_yt_ID( entry['id'] )

#print
#sep( "Video Metadata" )
#for key , val in result.iteritems():
    #print( key , ':' , val )
  
#print()
#sep( "Comment Data" )     
#for key , val in allThreads.iteritems():
    #print( key , ':' , val )
    
#for item in allThreads['items']:
    #print( item )
    
##for item in allThreads['items'][0]['replies']['comments']:
    ##print( item )
    
#for key , val in result['items'][0].iteritems():
    #print( key , ":" , val )
    
#print extract_video_duration( result )
#print parse_ISO8601_timestamp( extract_video_duration( result ) )
#stamps = scrape_and_check_timestamps( result )
#for stamp in stamps:
    #print stamp
    ## print extract_and_query_artist_and_track( stamp['balance'] )
    #print
    
#print

#print GN_most_likely_artist_and_track( gnClient , gnUser , 
                                       #extract_candidate_artist_and_track( stamps[0]['balance'] ) )

#if 0:
    #components = dir( youtube )
    #for comp in components:
        #print( comp )


#if 0:
    #response = urlopen( entry['url'] )
    #html = response.read()   



## ~~~~~~~~~~~~~~~ Downloading youtube videos as MP3: https://github.com/rg3/youtube-dl/blob/master/README.md#embedding-youtube-dl ~~~~~~
#if 0:
    
    ## Options for youtube-dl
    #ydl_opts = {
        #'format': 'bestaudio/best',
        #'postprocessors': [ {
            #'key': 'FFmpegExtractAudio',
            #'preferredcodec': 'mp3',
            #'preferredquality': '192',
        #} ] ,
        #'logger': MyLogger(),
        #'progress_hooks': [my_hook],
    #}
    
    ## Download file
    #with youtube_dl.YoutubeDL( ydl_opts ) as ydl:
        #ydl.download( [ 'https://www.youtube.com/watch?v=BaW_jenozKc' ] )  
            
#def get_tracklist_from_lines( lines ):
    #""" Return candidate tracklist or 'None' """
    #trackList
    ## 1. For each line
    #for line in lines:
        ## 2. Check the line for timestamp
        #is_nonempty_list( get_timestamp_from_line( line )['stamp'] )

# ___ End Spare ____________________________________________________________________________________________________________________________

