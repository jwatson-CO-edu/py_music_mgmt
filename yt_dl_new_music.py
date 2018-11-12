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
[ ] Split songs by track
    [Y] Establish YouTube API with key
    [Y] Download video descriptions
        [ ] If no tracklist is found, then Download video comments
    [Y] Locate timestamps in the description or comments
        [Y] Search for timestamp candidates
    [ ] Discern artist & track for each listing
	[Y] GraceNote Test
        [ ] pygn pull request "__init__.py"
	[ ] Separate candidate artist and track
	[ ] Query (1,2) and (2,1) to see which one returns a hit
	[ ] If gracenote fails, Query wikiP
    { } artist-track check: Google , Wikipedia?
    [ ] Find example of how to split songs by track
        [ ] URL , Split songs with multiprocess: https://codereview.stackexchange.com/q/166158
        [ ] Test with dummy times
    [ ] Split audio by confirmed timestamps
    [ ] Load id3 metadata for individual tracks    
[ ] Build a list of music to listen to
    [ ] Study Jams
    [Y] Establish a input playlist format - COMPLETE:
        # Comment
        <URL>,<SEQNUM>
    [Y] Parse a file - COMPLETE , made sure that strings are ASCII
    [ ] Review list
    [ ] Artists to try
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
{ } Bandcamp Scraper
"""

# === Init Environment =====================================================================================================================
# ~~~ Prepare Paths ~~~
import sys, os.path
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
except:
    try:
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
    except:
        print( "COULD NOT IMPORT API UNDER EITHER ALIAS" )
from oauth2client.tools import argparser
# ~~ Local ~~
prepend_dir_to_path( SOURCEDIR )
from marchhare.marchhare import parse_lines , ascii , sep , is_nonempty_list

# ~~ Constants , Shortcuts , Aliases ~~
EPSILON = 1e-7
infty   = 1e309 # URL: http://stackoverflow.com/questions/1628026/python-infinity-any-caveats#comment31860436_1628026
endl    = os.linesep

# ~~ Script Signature ~~
def __prog_signature__(): return __progname__ + " , Version " + __version__ # Return a string representing program name and verions

# ___ End Init _____________________________________________________________________________________________________________________________


# === Main Application =====================================================================================================================

# = Classes =

class MyLogger( object ):
    """ Logging class for YT downloads """
    # https://github.com/rg3/youtube-dl/blob/master/README.md#embedding-youtube-dl
    
    def debug( self , msg ):
        pass

    def warning( self , msg ):
        pass

    def error( self , msg ):
        print( msg )

# _ End Class _

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
    # print "Original Line:" , txtLine
    # print "Components:   " , components
    return { ascii( "url" ) : str( components[0] )             ,
             ascii( "seq" ) : int( components[1] )             ,
             ascii( "id"  ) : get_id_from_URL( components[0] ) }

def process_video_list( fPath ):
    """ Get all the URLs from the prepared list """
    return parse_lines( fPath , parse_video_entry )

def read_api_key( fPath ):
    """ Read the Google API key """
    entryFunc = lambda txtLine : [ str( rawToken ) for rawToken in txtLine.split( ',' ) ]
    lines = parse_lines( fPath , entryFunc )
    rtnDict = {}
    for line in lines:
        rtnDict[ line[0] ] = line[1]
    return rtnDict

def my_hook( d ):
    # https://github.com/rg3/youtube-dl/blob/master/README.md#embedding-youtube-dl
    if d[ 'status' ] == 'finished':
        print( 'Done downloading, now converting ...' )

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

# :: FIXME ::
# 2. Try to evaluate text stamps 
# 3. Notify if no stamps of any kind are found
# 4. If no stamps were found, Then attempt to split by pauses and give generic names to tracks

def digits_before_char( inputStr , char ):
    """ Get all the digits that preceed 'char' in 'inputStr' """
    # FIXME: FOR EACH OCCURRENCE, SEARCH FOR DIGITS BEFORE LETTER AND PREPEND TO THE RETURN STRING
    pass

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
            
def scrape_and_check_timestamps( reponseObj ):
    """ Attempt to get the tracklist from the response object and return it , Return if all the stamps are lesser than the duration """
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
                trkLstFltrd.append(
                    { ascii( 'timestamp' ) : stamp ,
                      ascii( 'line' ) :      line  }
                )
    # N. Return tracklist
    return trkLstFltrd
    
#def query_and_

# _ End Func _

# = Program Vars =



# _ End Vars _

if __name__ == "__main__":
    print( __prog_signature__() )
    termArgs = sys.argv[1:] # Terminal arguments , if they exist
    
    # 1. Load video playlist
    entries = process_video_list( "input/url_sources.txt" )
    if 0:
        for entry in entries:
            print( entry )
        
    entry = entries[0]    
    
    # 2. Init API connection
    authDict = read_api_key( "APIKEY.txt" )
    print( authDict )
    
    DEVELOPER_KEY            = authDict['key']
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION      = "v3"
    METADATA_SPEC            = 'snippet,contentDetails,statistics'
    #METADATA_SPEC            = 'id,snippet,contentDetails,statistics'
    COMMENT_THREAD_SPEC      = 'replies'
    
    
    youtube = build( YOUTUBE_API_SERVICE_NAME , 
                     YOUTUBE_API_VERSION , 
                     developerKey = DEVELOPER_KEY )
    
    print( "Created an API connection with key" , youtube._developerKey )
    
    # 3. Fetch video data
    
    # Fetch video data
    result = videos_list_by_id(
        youtube ,
        part = METADATA_SPEC ,
        id   = entry['id']
    )    
    
    if 0:
        descLines = extract_description_lines( result )
        sep( "Candidate Tracklist" , 2 )
        for line in descLines:
            stamp = get_timestamp_from_line( line )
            if len( stamp ) > 0:
                print( line , "," , stamp )
        print()
        sep( "Complete Description" )
        for line in descLines:
            print( line.strip() )    
    
    # Fetch comment threads
    allThreads = comment_threads_list_by_video_id(
        youtube ,
        part    = COMMENT_THREAD_SPEC,
        videoId = entry['id']
    )
    
    print
    sep( "Video Metadata" )
    for key , val in result.iteritems():
        print( key , ':' , val )
      
    print()
    sep( "Comment Data" )     
    for key , val in allThreads.iteritems():
        print( key , ':' , val )
        
    for item in allThreads['items']:
        print( item )
        
    for item in allThreads['items'][0]['replies']['comments']:
        print( item )
        
    for key , val in result['items'][0].iteritems():
        print( key , ":" , val )
        
    print extract_video_duration( result )
    print parse_ISO8601_timestamp( extract_video_duration( result ) )
    stamps = scrape_and_check_timestamps( result )
    for stamp in stamps:
        print stamp
        
    print()
    
    if 0:
        components = dir( youtube )
        for comp in components:
            print( comp )
    
    
    if 0:
        response = urlopen( entry['url'] )
        html = response.read()   
    
    
    
    # ~~~~~~~~~~~~~~~ Downloading youtube videos as MP3: https://github.com/rg3/youtube-dl/blob/master/README.md#embedding-youtube-dl ~~~~~~
    if 0:
        
        # Options for youtube-dl
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [ {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            } ] ,
            'logger': MyLogger(),
            'progress_hooks': [my_hook],
        }
        
        # Download file
        with youtube_dl.YoutubeDL( ydl_opts ) as ydl:
            ydl.download( [ 'https://www.youtube.com/watch?v=BaW_jenozKc' ] )  
    

# ___ End Main _____________________________________________________________________________________________________________________________


# === Spare Parts ==========================================================================================================================

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

