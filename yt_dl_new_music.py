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

Dependencies: numpy , youtube-dl , google-api-python-client , urllib2 , FFmpeg
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
[ ] Build a list of music to listen to
    [ ] Study Jams
    [Y] Establish a input playlist format - COMPLETE:
        # Comment
        <URL>,<SEQNUM>
    [Y] Parse a file - COMPLETE , made sure that strings are ASCII
    [ ] Review list
    [ ] Artists to try
[Y] Make API connection functions persistent functors - Not possible, just run connections once per script
    [Y] Write an IDE object persistence test - Objects in the script cannot persist between runs of the script, console is erased each run
[ ] Adjust program behavior
    [ ] Limit download speed with random spacing between requests
    [ ] Change user agent to FF browser
[ ] Cache scraped data && Pickle
    [ ] URL
    [ ] HTML
    [ ] JSON objects
        [ ] Metadata
        [ ] Comment info
    [ ] Identified categories
        [ ] Timestamps
    [ ] Locations of raw files
        [ ] Check if exist && flag
    [ ] Unpickle on startup
    [ ] Cache flag
    [ ] WARN: Switch to database at 10k entries
[ ] Store raw files
[ ] If no tracklist is found, then Download video comments
[ ] Remove log files from repo
{ } Bandcamp Scraper

~~~ Test Plan ~~~
NOTE: This utility must be run in Linux
[ ] 1. Download and Store
    [ ] Open API
    [ ] Check Write location
    [ ] Create Dir for each video
    [ ] Raw File
    [ ] Raw File Location
    [ ] File Success
    [ ] URL
    [ ] Description Data
    [ ] Comment Data
    [ ] LOG
    [ ] Pickle all data
    [ ] Close API
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
                                  validate_dirs_writable , LogMH , Stopwatch , )

# ~~ Constants , Shortcuts , Aliases ~~
EPSILON = 1e-7
infty   = 1e309 # URL: http://stackoverflow.com/questions/1628026/python-infinity-any-caveats#comment31860436_1628026
endl    = os.linesep

# ~~ Script Signature ~~
def __prog_signature__(): return __progname__ + " , Version " + __version__ # Return a string representing program name and verions

# ___ End Init _____________________________________________________________________________________________________________________________


# === Main Application =====================================================================================================================

# = youtube-dl Logging =

class MyLogger( object ):
    """ Logging class for YT downloads """
    # https://github.com/rg3/youtube-dl/blob/master/README.md#embedding-youtube-dl
    global LOG
    
    def __init__( self ):
        """ Put ther noisier output in separate logs for easier debugging """
        self.dbgLog = LogMH()
        self.wrnLog = LogMH()
        
    def debug( self , msg ):
        """ Log debug output """
        self.dbgLog.prnt( "DEBUG:" , msg )
        
    def warning( self , msg ):
        """ Log warnings """
        self.wrnLog.prnt( "WARN:" , msg )
        
    def error( self , msg ):
        """ Log erros in the main log """
        LOG.prnt( "ERROR:" , msg )

def my_hook( d ):
    # https://github.com/rg3/youtube-dl/blob/master/README.md#embedding-youtube-dl
    if d[ 'status' ] == 'finished':
        print( 'Done downloading, now converting ...' )

# _ End Logging _


# = Program Functions =

def get_id_from_URL( URLstr ):
    """ Get the 11-char video ID from the URL string """
    # NOTE: This function assumes that the URL has only one "=" and that the ID follows it
    components = URLstr.split( '=' , 1 )
    if len( components ) > 1:
        return ascii( components[1] )
    return ''

def parse_video_entry( txtLine ):
    """ Obtain the video url from the line """
    components = [ rawToken for rawToken in txtLine.split( ',' ) ]
    return { ascii( "url" ) : str( components[0] )             ,
             ascii( "seq" ) : int( components[1] )             ,
             ascii( "id"  ) : get_id_from_URL( components[0] ) }

def process_video_list( fPath ):
    """ Get all the URLs from the prepared list """
    return parse_lines( fPath , parse_video_entry )

def comma_sep_key_val_from_file( fPath ):
    """ Read a file, treating each line as a key-val pair separated by a comma """
    entryFunc = lambda txtLine : [ str( rawToken ).strip() for rawToken in txtLine.split( ',' ) ]
    lines = parse_lines( fPath , entryFunc )
    rtnDict = {}
    for line in lines:
        rtnDict[ line[0] ] = line[1]
    return rtnDict

def remove_empty_kwargs( **kwargs ):
    """ Remove keyword arguments that are not set """
    good_kwargs = {}
    if kwargs is not None:
        for key, value in kwargs.iteritems():
            if value:
                good_kwargs[key] = value
    return good_kwargs

def print_response( response ):
    """ Print the thing , Return the thing """
    print( response )
    return response

def videos_list_by_id( client , **kwargs ):
    """ Fetch the specified video info """
    kwargs   = remove_empty_kwargs( **kwargs )
    response = client.videos().list( **kwargs ).execute()
    return print_response( response )

def comment_threads_list_by_video_id( client , **kwargs ):
    # See full sample for function
    kwargs   = remove_empty_kwargs(**kwargs)
    response = client.commentThreads().list( **kwargs ).execute()
    return print_response( response )

def extract_description_lines( metadata ):
    """ Retrieve the description from the video data """
    return metadata['items'][0]['snippet']['localized']['description'].splitlines()

def extract_video_duration( metadata ):
    """ Get the ISO 8601 string from the video metadata """
    return ascii( metadata['items'][0]['contentDetails']['duration'] )

def get_last_digits( inputStr ):
    """ Get the last contiguous substring of digits in the 'inputStr' """
    rtnStr = ""
    lastWasDigit = False
    # 1. For each character in the string
    for char in inputStr:
        # 2. If the character is a digit, then we potentially care about it
        if char.isdigit():
            # 3. If the last character was a digit , then add it to the string of digits to return
            if lastWasDigit:
                rtnStr += char
            # 4. else last character was not digit , Begin new digit string
            else:
                rtnStr = char
            # 5. Set flag for digit char
            lastWasDigit = True
        # else the character is not digit , Set flag
        else:
            lastWasDigit = False
    return rtnStr
        
def get_first_digits( inputStr ):
    """ Get the first contiguous substring of digits in the 'inputStr' """
    rtnStr = ""
    gatheredDigits = False
    # 1. For each character in the string
    for char in inputStr:
        # 2. If the character is a digit, then we care about it
        if char.isdigit():
            gatheredDigits = True
            rtnStr += char
        # 3. else char was not digit, but we have collected digits , so return them
        elif gatheredDigits:
            return rtnStr
        # else was not digit and have no digits, keep searching
    # 4. If we made it here then either no digits were found, or the string ended with the first digit substring which we wish to return
    return rtnStr    

def get_timestamp_from_line( line ):
    """ Search for a timestamp substring and return it or [] """
    # NOTE: Only accepting timestamps with ':' in between numbers
    # NOTE: This function assumest that ':' is used only for separating parts of the timestamp
    
    # 1. Fetch the parts of the string that are separated by ":"s
    components = line.split(':') 
    stampParts = []
    
    # 2. If there was at least one interior ":"
    if len( components ) and ":" in line:
        # 3. For each of the split components
        for i , comp in enumerate( components ):
            # 4. For the first component, assume that the pertinent substring appears last
            if i == 0:
                # 5. Fetch last digits and cast to int if they exist , append to timestamp
                digits = get_last_digits( comp )
                if len( digits ) > 0:
                    stampParts.append( int( digits ) )
            # 5. For the last component, assume that the pertinent substring appears first
            elif i == len( components ) - 1: 
                # 6. Fetch first digits and cast to int if they exist , append to timestamp
                digits = get_first_digits( comp )
                if len( digits ) > 0:
                    stampParts.append( int( digits ) )  
            # 7. Middle components should have digits only
            else:
                comp = comp.strip()
                # 8. If middle was digits only, add to stamp
                if comp.isdigit():
                    stampParts.append( int( comp ) ) 
                # 9. else middle was somthing else, fail
                else:
                    return []
    # N. Return timestamp components if found, Otherwise return empty list
    return stampParts
        
def parse_ISO8601_timestamp( PT_H_M_S ):
    """ Return a dictionary representing the time represented by the ISO 8601 standard for durations """
    # ISO 8601 standard for durations: https://en.wikipedia.org/wiki/ISO_8601#Durations
    dividers = ( 'H' , 'M' , 'S' )
    H = '' ; M = '' ; S = ''
    currStr = ''
    rtnStamp = {}
    for char in PT_H_M_S:
        if char.isdigit():
            currStr += char
        elif ( char in dividers ) and ( len( currStr ) > 0 ):
            rtnStamp[ char ] = int( currStr )
            currStr = ''
    return rtnStamp

def parse_list_timestamp( compList ):
    """ Standardise the list of timestamp components into a standard dictionary """
    # NOTE: This function assumes that 'compList' will have no more than 3 elements , If it does then only the last 3 will be parsed
    # NOTE: This function assumes that 'compList' is ordered largest to smallest time division, and that it will always include at least seconds
    dividers = ( 'H' , 'M' , 'S' )
    j = 0
    tsLen = len( compList )
    rtnStamp = {}
    for i in range( -1 , -4 , -1 ):
        if j < tsLen:
            rtnStamp[ dividers[i] ] = compList[i]
            j += 1
    return rtnStamp

def timestamp_leq( op1 , op2 ):
    """ Return true if 'op1' <= 'op2' """
    # For each descending devision in time
    for div in ( 'H' , 'M' , 'S' ): 
        try:
            val1 = op1[ div ] ; val2 = op2[ div ]
            if val1 < val2:
                return True
            elif val1 > val2:
                return False
        except KeyError:
            pass
    return True

def remove_timestamp_from_line( line ):
    """ Remove timestamp from the line """
    # NOTE: This function assumes that the timestamp is contiguous
    # NOTE: This function assumes the timestampe begins and ends with a number
    foundNum = False ; foundCln = False
    bgnDex = 0 ; endDex = 0
    
    for i , char in enumerate( line ):
        if char.isdigit():
            if not foundNum:
                foundNum = True
                bgnDex   = i
            if foundNum and foundCln:
                endDex   = i
        elif char == ':':
            foundCln = True
        elif foundNum and foundCln:
            break
        else:
            foundNum = False ; foundCln = False
            bgnDex = 0 ; endDex = 0            
            
    if foundNum and foundCln:
        return line[ :bgnDex ] + line[ endDex+1: ]
    else:
        return line

def remove_leading_digits_from_line( line ):
    """ Remove the leading digits and leading space from a string """
    bgnDex = 0
    for i , char in enumerate( line ):
        if char.isdigit() or char.isspace():
            pass
        else:
            bgnDex = i
            break
    return line[bgnDex:]
            
def scrape_and_check_timestamps( reponseObj ):
    """ Attempt to get the tracklist from the response object and return it , Return if all the stamps are lesser than the duration """
    # NOTE: This function assumes that a playlist can be found in the decription
    # NOTE: This function assumes that if there is a number representing a songs's place in the sequence, then it is the first digits in a line
    
    # 1. Get the description from the response object
    descLines = extract_description_lines( reponseObj )
    # 2. Get the video length from the response object
    duration  = parse_ISO8601_timestamp( extract_video_duration( reponseObj ) )
    # 3. Get candidate tracklist from the description 
    trkLstFltrd = []
    for line in descLines:
        stamp = get_timestamp_from_line( line )
        if len( stamp ) > 0:
            stamp = parse_list_timestamp( stamp )
            if timestamp_leq( stamp , duration ):
                linBal = remove_timestamp_from_line( line )
                vidSeq = get_first_digits( line )
                if vidSeq:
                    vidSeq = int( vidSeq )
                    linBal = remove_leading_digits_from_line( linBal )
                else:
                    vidSeq = -1
                trkLstFltrd.append(
                    { ascii( 'timestamp' ) : stamp  , # When the song begins in the video
                      ascii( 'videoSeq' ) :  vidSeq , # Sequence number in the video, if labeled
                      ascii( 'balance' ) :   linBal , # Remainder of scraped line after the timestamp and sequence number are removed
                      ascii( 'line' ) :      line   } # Full text of the scraped line 
                )
    # N. Return tracklist
    return trkLstFltrd

def extract_candidate_artist_and_track( inputStr ):
    """ Given the balance of the timestamp-sequence extraction , Attempt to infer the artist and track names """
    # 1. Split on dividing char "- "
    components = inputStr.split( '- ' )
    # 2. Strip leading and trailing whitespace
    components = [ comp.strip() for comp in components ]
    # 3. Retain nonempty strings
    components = [ comp for comp in components if len( comp ) ]
    print components
    numComp    = len( components )
    if numComp > 2:
        # If there are more than 2 components, then only take the longest 2
        components.sort( lambda x , y : cmp( len(y) , len(x) ) ) # Sort Longest --to-> Shortest
        print "WARN: There were more than 2 components! ," , components
        return components[:2]
    elif numComp == 2:
        return components
    else:
        for i in range( 2 - numComp ):
            components.append( '' )
        return components
    
def obj_to_dict( obj ):
    """ Return a dictionary version of the object """
    # Easy: The object already has a dictionary
    try:
        if len( obj.__dict__ ) == 0:
            raise KeyError( "Empty Dict" )
        print "About to return a dictionary with" , len( obj.__dict__ ) , "attributes"
        return obj.__dict__
    # Hard: Fetch and associate attributes
    except:
        objDict = {}
        attrs = dir( obj )
        print "Found" , len( attrs ) , "attributes in the" , type( obj )
        for attr in attrs:
            objDict[ attr ] = getattr( obj , attr )
        return objDict
    
def GN_dictify_response_obj( resultObj ):
    """ Iterate over the response object and convert into a dictionary """
    # being able to 'pretty_print_dict' seems to imply that we can just iterate over keys in a for loop and access them with 'response[ key ]'
    rtnDict = {}
    try:
        for item in resultObj:
            #print "key:" , str( item ) , ", val:" , resultObj[ item ]
            rtnDict[ item ] = resultObj[ item ]
    except TypeError:
        print "WARN:" , type( resultObj ) , "is not iterable!"
    return rtnDict

def count_nested_values( superDict , val ):
    """ Count the number of times that 'val' occurs in 'superDict' """
    debugPrnt = False
    # 1. Base Case : This is a value of the dictionary
    if type( superDict ) not in ( dict , pygn.pygn.gnmetadata , list ):
        if debugPrnt: print "Base case with type" , type( superDict )
        try:
            if debugPrnt: print "Got" , superDict , ", Type:" , type( superDict )
            num = superDict.count( val )
            if debugPrnt: print "Base: Searching" , superDict , 'for' , val , ", Occurrences:" , num
            return num
        except:
            return 0
    # 2. Recursive Case : This is an inner list
    elif type( superDict ) == list:
        total = 0
        for item in superDict:
            total += count_nested_values( item , val )
        return total
    # 3. Recursive Case : This is an inner dictionary or object
    else:
        if debugPrnt: print "Recursive case with type" , type( superDict )
        total = 0
        if type( superDict ) == dict:
            for key , dVal in superDict.iteritems():
                if debugPrnt: print "Reecurring on" , dVal , "..."
                total += count_nested_values( dVal , val )
        elif type( superDict ) == pygn.pygn.gnmetadata:
            gotDict = GN_dictify_response_obj( superDict )
            #print gotDict
            for key , dVal in gotDict.iteritems():
                if debugPrnt: print "Reecurring on" , dVal , "..."
                total += count_nested_values( dVal , val )  
        else:
            if debugPrnt: print "Found some other type:" , type( superDict )
        return total
    
"""
### ISSUE: 'GN_score_result_with_components' DOES NOT FIND OBVIOUS MATCHES ###
There are occurrences of search keys that are not turning up in the count
"""
    
def GN_score_result_with_components( resultObj , components ):
    """ Tally the instances for each of the components in the result object """
    total = 0
    currCount = 0
    debugPrnt = False
    for comp in components:
        currCount = count_nested_values( resultObj , comp )
        total += currCount
        if debugPrnt: print "Component:" , comp , ", Occurrences:" , currCount
    return total

def GN_examine_response_obj( resultObj ):
    """ CAN WE JUST ITERATE OVER THIS? : YES """
    # being able to 'pretty_print_dict' seems to imply that we can just iterate over keys in a for loop and access them with 'response[ key ]'
    try:
        for item in resultObj:
            print "key:" , str( item ) , ", val:" , resultObj[ item ]
    except TypeError:
        print "WARN:" , type( resultObj ) , "is not iterable!"
    
def GN_most_likely_artist_and_track( GN_client , GN_user , components ):
    """ Given the strings 'op1' and 'op2' , Determine which of the two are the most likely artist and track according to GraceNote """
    op1 = components[0]
    op2 = components[1]    
    flagPrint = True
    rtnScores = []
    
    # 1. Perform search (1,0)
    # The search function requires a clientID, userID, and at least one of either { artist , album , track } to be specified.
    metadata = search(
        clientID = GN_client , 
        userID   = GN_user   , 
        artist   = op2       , 
        track    = op1
    )
    
    score21 = GN_score_result_with_components( metadata , components )
    
    rtnScores.append(
        { 'artist' : metadata['album_artist_name'] ,
          'track'  : metadata['track_title']       ,
          'score'  : score21                       }
    )
    
    if flagPrint: 
        pretty_print_dict( metadata )
        #GN_examine_response_obj( metadata )
        print "Score for this result:" , score21
    
    # 2. Perform search (0,1)   
    # The search function requires a clientID, userID, and at least one of either { artist , album , track } to be specified.
    metadata = search(
        clientID = GN_client , 
        userID   = GN_user   , 
        artist   = op1       , 
        track    = op2
    )    
    
    score12 = GN_score_result_with_components( metadata , components )
    
    rtnScores.append(
        { 'artist' : metadata['album_artist_name'] ,
          'track'  : metadata['track_title']       ,
          'score'  : score12                       }
    )    
    
    if flagPrint: 
        pretty_print_dict( metadata )
        #GN_examine_response_obj( metadata )
        print "Score for this result:" , score12
        
    return rtnScores
    
    # FIXME : START HERE
    # FIXME : GRACENOTE SEARCH (1,2) AND (2,1) , Assign Score
    
    # ~ Dev Plan ~
    # [Y] Try a GN search with each and review the results
    # [y] Determine failure mode of the results - Search returns whatever the closest hit is, there is no failure mode
    #     [N] Introduce a small, intentional error into a good search to see how GN handles it
    # [y] Assign scores
    # [Y] Return a structure with scores
    
# FIXME : ASSIGN MOST LIKELY ARTIST AND TRACK NAMES
# FIXME : HASH OF KNOWN ARTIST NAMES    
    

    
# FIXME : WHAT TO DO ABOUT ONE-ARTIST ALBUMS?
# FIXME : WHAT TO DO ABOUT ONE-SONG VIDEOS?

# ~~~ MAIN EXECUTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# == Program Vars ==

# ~ API Connection Vars ~
DEVELOPER_KEY            = None
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION      = "v3"
METADATA_SPEC            = 'snippet,contentDetails,statistics'
#METADATA_SPEC            = 'id,snippet,contentDetails,statistics'
COMMENT_THREAD_SPEC      = 'replies'

# ~ Authentication Vars ~
authDict = {}
youtube  = None
gnKey    = None
gnClient = None
gnUser   = None

# ~ Session Vars ~
RAW_FILE_DIR       = ""
CHOPPED_SONG_DIR   = ""
PICKLE_DIR         = ""
ACTIVE_PICKLE_PATH = ""
LOG_DIR            = ""
ACTIVE_SESSION     = False
SESSION_PATH       = "session.txt"
LOG                = None
METADATA           = {} 

# ~ Processing Vars ~
# Options for youtube-dl
YDL_OPTS = {
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

def open_all_APIs( googKeyFile , GNKeyFile ):
    """ Open an API connection for {Google , GraceNote} """
    global DEVELOPER_KEY , authDict , youtube , gnKey , gnClient , gnUser
    
    # 2. Init Google API connection
    authDict = comma_sep_key_val_from_file( googKeyFile ) # "APIKEY.txt"
    DEVELOPER_KEY = authDict['key']
    print( authDict )
    youtube = build( YOUTUBE_API_SERVICE_NAME , 
                     YOUTUBE_API_VERSION , 
                     developerKey = DEVELOPER_KEY )
    
    # 3. Init GraceNote API Connection
    gnKey = comma_sep_key_val_from_file( GNKeyFile ) # "GNWKEY.txt"
    gnClient = gnKey[ 'clientID' ] #_ Enter your Client ID here '*******-************************'
    gnUser   = register( gnClient ) # Registration should not be done more than once per session      
    
def fetch_metadata_by_yt_video_ID( ytVideoID ):
    """ Fetch and return the response object that results from a YouTube API search for 'ytVideoID' """
    global youtube , METADATA_SPEC
    return videos_list_by_id(
        youtube ,
        part = METADATA_SPEC ,
        id   = ytVideoID
    )  

def fetch_comment_threads_by_yt_ID( ytVideoID ): 
    """ Fetch and return comment thread data that results from a YouTube API search for 'ytVideoID' """
    global youtube , COMMENT_THREAD_SPEC
    return comment_threads_list_by_video_id(
        youtube ,
        part    = COMMENT_THREAD_SPEC,
        videoId = ytVideoID 
    )

def load_session( sessionPath ):
    """ Read session file and populate session vars """
    global RAW_FILE_DIR , CHOPPED_SONG_DIR , PICKLE_DIR , ACTIVE_PICKLE_PATH , LOG_DIR , ACTIVE_SESSION
    sesnDict = comma_sep_key_val_from_file( sessionPath );              print "Loaded session file:" , sessionPath
    RAW_FILE_DIR       = sesnDict['RAW_FILE_DIR'];                      print "RAW_FILE_DIR:" , RAW_FILE_DIR
    CHOPPED_SONG_DIR   = sesnDict['CHOPPED_SONG_DIR'];                  print "CHOPPED_SONG_DIR:" , CHOPPED_SONG_DIR
    PICKLE_DIR         = sesnDict['PICKLE_DIR'];                        print "PICKLE_DIR:" , PICKLE_DIR 
    ACTIVE_PICKLE_PATH = sesnDict['ACTIVE_PICKLE_PATH'];                print "ACTIVE_PICKLE_PATH:" , ACTIVE_PICKLE_PATH
    LOG_DIR            = sesnDict['LOG_DIR'];                           print "LOG_DIR" , LOG_DIR
    ACTIVE_SESSION     = bool( int( sesnDict['ACTIVE_SESSION'] ) );     print "ACTIVE_SESSION:" , yesno( ACTIVE_SESSION )
    return sesnDict
    
def save_session( sessionPath ):
    """ Write session vars to the session file """
    # 1. If a file exists at this path, erase it
    if os.path.isfile( sessionPath ):
        print "Session" , sessionPath , "was overwritten!"
        os.remove( sessionPath )
    # 2. Write each line
    f = open( sessionPath , "w+" )
    f.write( 'RAW_FILE_DIR'       + ',' + str( sesnDict['RAW_FILE_DIR'] )          + '\n' )
    f.write( 'CHOPPED_SONG_DIR'   + ',' + str( sesnDict['CHOPPED_SONG_DIR'] )      + '\n' )
    f.write( 'PICKLE_DIR'         + ',' + str( sesnDict['PICKLE_DIR'] )            + '\n' )
    f.write( 'ACTIVE_PICKLE_PATH' + ',' + str( sesnDict['ACTIVE_PICKLE_PATH'] )    + '\n' )
    f.write( 'LOG_DIR'            + ',' + str( sesnDict['LOG_DIR'] )               + '\n' )
    f.write( 'ACTIVE_SESSION'     + ',' + str( int( sesnDict['ACTIVE_SESSION'] ) ) + '\n' )
  
def verify_session_writable( sesnDict ):
    """ Make sure that we can write to the relevant directories """
    allWrite = validate_dirs_writable(  
        os.path.join( SOURCEDIR , sesnDict['RAW_FILE_DIR'] )     ,
        os.path.join( SOURCEDIR , sesnDict['CHOPPED_SONG_DIR'] ) ,
        os.path.join( SOURCEDIR , sesnDict['PICKLE_DIR'] )       ,
        os.path.join( SOURCEDIR , sesnDict['LOG_DIR'] )          ,
    )
    print "Session dirs writable:" , yesno( allWrite )
    return allWrite

def get_EXT( fName ):
    """ Return the capitalized file extension at the end of a path without the period """
    return os.path.splitext( fName )[-1][1:].upper()

def list_all_files_w_EXT( searchPath , EXTlst ):
    """ Return all of the paths in 'searchPath' that have extensions that appear in 'EXTlst' , Extensions are not case sensitive """
    items = os.listdir( searchPath )
    rtnLst = []
    for item in items:
        fEXT = get_EXT( item )
        if fEXT in EXTlst:
            rtnLst.append( item )
    return rtnLst
    
def Stage1_Download_w_Data( inputFile ,
                            minDelay_s = 20 , maxDelay_s = 180 ):
    """ Check environment for download , Fetch files and metadata , Save files and metadata """
    global LOG , METADATA
    LOG = LogMH()
    dlTimer = Stopwatch()
    # DEBUG
    limit = 1
    count = 0
    # 0. Indicate file
    LOG.prnt( "Processing" , inputFile , "..." )
    # 1. Load session
    session = load_session( SESSION_PATH )
    if os.path.isfile( ACTIVE_PICKLE_PATH ):
        LOG.prnt( "Found cached metadata at" , ACTIVE_PICKLE_PATH )
        METADATA = unpickle_dict( ACTIVE_PICKLE_PATH ) 
    else:
        METADATA = {}
    # 1.1. Activate session
    ACTIVE_SESSION = True
    # 2. Check Write locations
    dirsWritable = verify_session_writable( session )
    if not dirsWritable:
        return False
    # 3. Process input file
    entries = process_video_list( "input/url_sources.txt" )
    LOG.prnt( "Read input file with" , len( entries ) , "entries" )
    # 4. Init downloaded
    ydl = youtube_dl.YoutubeDL( YDL_OPTS )
    # 4. For each entry
    for entry in entries:
        # I. If the debug file limit exceeded, exit loop
        if not count < limit:
            break
        dlTimer.start()
        # 5. Create Dir
        enID = entry['id']
        enRawDir = os.path.join( RAW_FILE_DIR , enID )
        if not os.path.isdir( enRawDir ):
            try:  
                os.mkdir( enRawDir )
            except OSError:  
                LOG.prnt(  "Creation of the directory %s failed" % enRawDir )
            else:  
                LOG.prnt(  "Successfully created the directory %s " % enRawDir )            
        # 6. Download Raw MP3 File
        LOG.prnt( "Downloading" , entry['url'] )
        
        # DEBUG: DISABLE DOWNLOAD UNTIL CACHING IS IMPLEMENTED
        #ydl.download( [ entry['url'] ] )  # This function MUST be passed a list!
        
        enElapsed = dlTimer.elapsed()
        LOG.prnt( "Downloading and Processing:" , enElapsed , "seconds" )
        # [ ] Locate and move the raw file
        # [ ] Raw File End Location
        # [ ] File Success
        # [ ] URL
        # [ ] Fetch Description Data
        # [ ] Verify that the downloaded file is as long as the original video
        # [ ] Fetch Comment Data
        # [ ] Add file data to a dictionary
        count += 1
    # [ ] Pickle all data
    # { } Close APIs?

# _ End Func _

# = Program Vars =



# _ End Vars _

if __name__ == "__main__":
    print( __prog_signature__() )
    termArgs = sys.argv[1:] # Terminal arguments , if they exist
    
    # ~~~ Stage 1 ~~~
    Stage1_Download_w_Data( "input/url_sources.txt" ,
                            minDelay_s = 20 , maxDelay_s = 180 )
    
    

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

#def get_timelinks_from_HTML( ytHTML ):
    #""" Attempt to scrape times links from page HTML """
    ## NOTE: This function assumes that the link can be found on a single line, beginning with "&t="
    #lines = ytHTML.splitlines()
    #linkToken = "&t="
    #rtnStamps = []
    #for line in lines:
        #if linkToken in line:
            ## FIXME: ATTEMPT TO GET THE NUMBER THAT PRECEEDS EACH TIME DIVISION
            ## FIXME: WHAT TO DO ABOUT TIME LINKS IN THE COMMENTS THAT ARE NOT TRACK LISTS?
            #pass
            
#def get_tracklist_from_lines( lines ):
    #""" Return candidate tracklist or 'None' """
    #trackList
    ## 1. For each line
    #for line in lines:
        ## 2. Check the line for timestamp
        #is_nonempty_list( get_timestamp_from_line( line )['stamp'] )

# ___ End Spare ____________________________________________________________________________________________________________________________

