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
    [Y] Locate timestamps in the description or comments
        [Y] Search for timestamp candidates
    [ ] Discern artist & track for each listing
	[Y] GraceNote Test
	[Y] Separate candidate artist and track
	[Y] Query (1,2) and (2,1) to see which one returns a hit
        [ ] pygn pull request "__init__.py"
            [Y] Fork pygn
	{ } artist-track fallback: 
            { } MusicBrainz - Open Access Database
            { } Google , Wikipedia?
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
from marchhare.marchhare import parse_lines , ascii , sep , is_nonempty_list , pretty_print_dict

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

def my_hook( d ):
    # https://github.com/rg3/youtube-dl/blob/master/README.md#embedding-youtube-dl
    if d[ 'status' ] == 'finished':
        print( 'Done downloading, now converting ...' )

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

def read_api_key( fPath ):
    """ Read the Google API key """
    entryFunc = lambda txtLine : [ str( rawToken ) for rawToken in txtLine.split( ',' ) ]
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
        
    entry = entries[30]    
    
    # 2. Init Google API connection
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
    
    # 3. Init GraceNote API Connection
    
    gnKey = read_api_key( "GNWKEY.txt" )
    print gnKey
    
    gnClient = gnKey[ 'clientID' ] #_ Enter your Client ID here '*******-************************'
    gnUser   = register( gnClient ) # Registration should not be done more than once per session    
    
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
        
    #for item in allThreads['items'][0]['replies']['comments']:
        #print( item )
        
    for key , val in result['items'][0].iteritems():
        print( key , ":" , val )
        
    print extract_video_duration( result )
    print parse_ISO8601_timestamp( extract_video_duration( result ) )
    stamps = scrape_and_check_timestamps( result )
    for stamp in stamps:
        print stamp
        # print extract_and_query_artist_and_track( stamp['balance'] )
        print
        
    print
    
    print GN_most_likely_artist_and_track( gnClient , gnUser , 
                                           extract_candidate_artist_and_track( stamps[6]['balance'] ) )
    
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

