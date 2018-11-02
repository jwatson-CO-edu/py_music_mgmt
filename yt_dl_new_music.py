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

Dependencies: numpy , youtube-dl , FFmpeg
"""


"""  
~~~ Developmnent Plan ~~~

[Y] Test download at the command line
[Y] Fetch example from the docs
    [Y] Test the example under linux
[ ] Split songs by track
    [Y] Establish YouTube API with key
    [Y] Download video descriptions
    [ ] Download video comments
    [ ] Locate timestamps in the description or comments
        [ ] Search for timestamp candidates
    [ ] Discern artist & track for each listing
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
{ } Bandcamp Scraper
"""

# === Init Environment =====================================================================================================================
# ~~~ Prepare Paths ~~~
import sys, os.path
SOURCEDIR = os.path.dirname( os.path.abspath( __file__ ) ) # URL, dir containing source file: http://stackoverflow.com/a/7783326
PARENTDIR = os.path.dirname( SOURCEDIR )
# ~~ Path Utilities ~~
def prepend_dir_to_path( pathName ): sys.path.insert( 0 , pathName ) # Might need this to fetch a lib in a parent directory

# ~~~ Imports ~~~
# ~~ Standard ~~
from math import pi , sqrt
import urllib2
# ~~ Special ~~
import numpy as np
import youtube_dl
# https://medium.com/greyatom/youtube-data-in-python-6147160c5833
from apiclient.discovery import build
from apiclient.errors import HttpError
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
    return ascii( URLstr.split( '=' , 1 )[1] )

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

def get_timestamp_from_line( line ):
    """ Search for a timestamp substring and return it or [] """
    rtnDict  = {}
    rtnStamp = []
    currNum  = ''
    lastDigit_i = 0
    for i , char in enumerate( line ):
        if char.isdigit():
            currNum += char
            lastDigit_i = i
        elif char == ':':
            rtnStamp.append( int( currNum ) )
            currNum  = ''
        elif not char.isspace():
            if len( currNum ) > 0:
                tnStamp.append( int( currNum ) )
            currNum  = ''  
    balance = line[ lastDigit_i+1 : ]
    return { 'stamp'   : rtnStamp , 
             'balance' : balance  }

def get_tracklist_from_lines( lines ):
    """ Return candidate tracklist or 'None' """
    trackList
    # 1. For each line
    for line in lines:
        # 2. Check the line for timestamp
        is_nonempty_list( get_timestamp_from_line( line )['stamp'] )

# _ End Func _

# = Program Vars =



# _ End Vars _

if __name__ == "__main__":
    print __prog_signature__()
    termArgs = sys.argv[1:] # Terminal arguments , if they exist
    
    # 1. Load video playlist
    entries = process_video_list( "input/url_sources.txt" )
    if 1:
        for entry in entries:
            print entry
        
    entry = entries[-2]    
    
    # 2. Init API connection
    authDict = read_api_key( "APIKEY.txt" )
    print authDict 
    
    DEVELOPER_KEY            = authDict['key']
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION      = "v3"
    METADATA_SPEC            = 'snippet,contentDetails,statistics'
    COMMENT_THREAD_SPEC      = 'replies'
    
    
    youtube = build( YOUTUBE_API_SERVICE_NAME , 
                     YOUTUBE_API_VERSION , 
                     developerKey = DEVELOPER_KEY )
    
    print "Created an API connection with key" , youtube._developerKey
    
    # 3. Fetch video data
    
    # Fetch video data
    result = videos_list_by_id(
        youtube ,
        part = METADATA_SPEC ,
        id   = entry['id']
    )    
    
    # Fetch comment threads
    allThreads = comment_threads_list_by_video_id(
        youtube ,
        part    = COMMENT_THREAD_SPEC,
        videoId = entry['id']
    )
    
    print
    sep( "Video Metadata" )
    for key , val in result.iteritems():
        print key , ':' , val
      
    print
    sep( "Comment Data" )     
    for key , val in allThreads.iteritems():
        print key , ':' , val    
        
    for item in allThreads['items']:
        print item
        
    for item in allThreads['items'][0]['replies']['comments']:
        print item
        
    for key , val in result['items'][0].iteritems():
        print key , ":" , val
        
    print
    
    if 0:
        components = dir( youtube )
        for comp in components:
            print comp
    
    
    if 0:
        response = urllib2.urlopen( entry['url'] )
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



# ___ End Spare ____________________________________________________________________________________________________________________________

