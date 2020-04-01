#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Template Version: 2018-03-23

# ~~ Future First ~~
from __future__ import division # Future imports must be called before everything else, including triple-quote docs!

"""
FILENAME.py
James Watson, YYYY MONTHNAME
A ONE LINE DESCRIPTION OF THE FILE
"""

def comments_from_thread_cache( cmntThreads ):
    """ Fetch the best comment text from the item cache , and cache the comments in each item """
    commentList = []
    for item in cmntThreads['items']:
        textDisplay  = item['snippet']['topLevelComment']['snippet']['textDisplay']
        textOriginal = item['snippet']['topLevelComment']['snippet']['textOriginal']
        if len( textOriginal ) > len( textDisplay ):
            commentList.append( textOriginal )
        else:
            commentList.append( textDisplay )
    return commentList

def scrape_and_check_timestamps_cmnts( reponseObj , cmntThreads ):
    """ Look for timestamps in the comments """
    # 1. Get list of comments
    cmntList  = comments_from_thread_cache( cmntThreads )
    duration  = duration_from_yt_response( reponseObj )
    longest   = 0
    rtnStamps = []
    for comment in cmntList:
        cmntLines = comment.splitlines()
        stamps = get_timestamps_from_lines( cmntLines , duration )      
        if len( stamps ) > longest:
            rtnStamps = stamps
    return rtnStamps

def timestamps_from_cached_item( itemCacheDict ):
    """ Recover timestamps from either the description or the comments """
    wasInDesc = False
    wasInCmnt = False
    enMeta    = itemCacheDict['Metadata']
    enThreads = itemCacheDict['Threads']
    # 1. Attempt to scrape from the description
    descStamps = scrape_and_check_timestamps_desc( enMeta )
    # 2. Attempt to scrape from the comments
    cmntStamps = scrape_and_check_timestamps_cmnts( enMeta , enThreads )
    # 3. Choose the list of comments with the most entries
    if len( descStamps ) > len( cmntStamps ):
        return descStamps
    else:
        return cmntStamps
    
def repopulate_comments( cacheDict ):
    """ Fetch comments for each of the cached items , Replacing old """
    for enID , enCache in cacheDict.iteritems():
        enComment = fetch_comment_threads_by_yt_ID( enID )
        enCache['Threads'] = enComment
        
def repopulate_duration( cacheDict ):
    """ Fetch duration for each of the cached items , Adding a new category """
    for enID , enCache in cacheDict.iteritems():
        enCache['Duration'] = parse_ISO8601_timestamp( extract_video_duration( enCache['Metadata'] ) )

def get_video_title( ytCacheItem ):
    """ Get the video title from the cached data item """
    return ytCacheItem['items'][0]['snippet']['title']

def levenshteinDistance( str1 , str2 ):
    """ Compute the edit distance between strings , Return:
        'ldist': Number of edits between the strings 
        'ratio': Number of edits over the sum of the lengths of 'str1' and 'str2' """
    # URL , Levenshtein Distance: https://rosettacode.org/wiki/Levenshtein_distance#Python
    m = len( str1 )
    n = len( str2 )
    lensum = float( m + n )
    d = []           
    for i in range( m + 1 ):
        d.append( [i] )        
    del d[0][0]    
    for j in range( n + 1 ):
        d[0].append(j)       
    for j in range( 1 , n+1 ):
        for i in range( 1 , m+1 ):
            if str1[ i-1 ] == str2[ j-1 ]:
                d[i].insert( j , d[ i-1 ][ j-1 ] )           
            else:
                minimum = min( d[ i-1 ][ j ] + 1   , 
                               d[ i ][ j-1 ] + 1   , 
                               d[ i-1 ][ j-1 ] + 2 )
                d[i].insert( j , minimum )
    ldist = d[-1][-1] 
    ratio = ( lensum - ldist ) / lensum
    return { 'distance' : ldist , 'ratio' : ratio }

def similarity_to_artists( candidateArtist , mxRtn = 10 ):
    """ Return a list of increasing distance up to 'mxRtn' """
    limRtn = False
    if mxRtn:
        limRtn = True
    pQ = PriorityQueue()
    if len( ARTISTS ):
        for artist in ARTISTS:
            pQ.push( artist , levenshteinDistance( artist , candidateArtist )['distance'] , hashable = artist )
        itms , vals = pQ.unspool()
        if len( itms ) > mxRtn:
            return itms[:mxRtn]
        else:
            return itms
    else:
        return []

def make_proper_track_meta( artistName , trackName , trackNum , stampBgnISO , stampEndISO , albumName , complete ):
    """ Return a standardized dictionary with enough info to chop the song from the raw file """
    return {
        'artist' :   artistName , 
        'title' :    trackName ,
        'track' :    trackNum ,
        'timeBgn' :  stampBgnISO ,
        'timeEnd' :  stampEndISO , 
        'album' :    albumName ,
        'complete' : complete
    }

_MENUTRACKLONG = \
"""~ Options ~
1. Choose from candidates
2. Search known artists
3. Manual Title
4. Manual Track
5. END"""

def resolve_track_long( trackData , trkDex ):
    """ Propmt user for resolution on this track """
    # NOTE: This function assumes multi-track data has been extracted
    
    # 1. Fetch web data
    print trackData
    components = extract_candidate_artist_and_track( trackData[ trkDex ]['balance'] )
    candidates = GN_most_likely_artist_and_track( gnClient , gnUser , components ) 
    print "Balance:" , trackData[ trkDex ]['balance']    
    
    def run_menu( cmpnnts , cnddts ):
        """ Handle user input for long video resolution """
        runMenu = True
        while runMenu:
            print _MENUTRACKLONG
            usrChoice = int( raw_input( "Select Option and Press [Enter]:" ) )
            # 1. Choose from candidates
            if usrChoice == 1:
                for canDex , candidate in enumerate( cnddts ):
                    print "Choice" , canDex , ":" , endl , candidate
                usrChoice = int( raw_input( "Select Option and Press [Enter]:" ) )
                    
                # FIXME : HANDLE THE USER CHOICE FOR BEST CANDIDATE
                # FIXME : CODE CHOICE
                    
                    
            # 2. Search known artists
            elif usrChoice == 2:
                pass # FIXME : CODE CHOICE
            # 3. Manual Title            
            elif usrChoice == 3:
                pass # FIXME : CODE CHOICE
            # 4. Manual Track                        
            elif usrChoice == 4:
                pass # FIXME : CODE CHOICE
            # 5. END
            elif usrChoice == 5:
                runMenu = False
            # N. USER GOOFED or OTHER ERROR
            else:
                print usrChoice , "is not a valid option!"
                runMenu = True
    run_menu( components , candidates )
    # QUIT
    exit()

def track_time_bounds( enCache , tracklist ):
    """ Define a beginning and ending time for each track, in-place, given the beginning of each track and the ending time of the video """
    numTrax = len( tracklist )
    mostDex = numTrax - 1
    for trkDex , track in enumercate( tracklist ):
        if trkDex < mostDex:
            pass # FIXME : CODE CASE
        else:
            pass # FIXME : CODE CASE
    

def process_entry_tracklist( enCache , tracklist ):
    """ Ask the user for help with assigning song and artist to the track , The result can be used to chop the raw file """
    # NOTE: This function assumes that the tracklist has at least one antry
    # NOTE: The output of this function must be usable for chopping
    enID     = enCache['ID']
    enTracks = enCache['Timestamp']
    approvedTracks = []
    print "Processing tracklist for" , enID , "..."
    # 1. How many tracks did the initial pass find?
    print "Cached tracklist has" , len( enTracks ) , "items."
    # 2. For each track in the list
    for trkDex , track in enumerate( tracklist ):
        trackDict = resolve_track_long( tracklist , trkDex )
        approvedTracks.append( trackDict )
    # 3. Return approved tracklist
    return approvedTracks

# === Testing ==============================================================================================================================

if __name__ == "__main__":
    pass

# ___ End Tests ____________________________________________________________________________________________________________________________