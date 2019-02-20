#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Template Version: 2018-03-23

# ~~ Future First ~~
from __future__ import division # Future imports must be called before everything else, including triple-quote docs!

# ~~ Local ~~
from marchhare.marchhare import ( LogMH , parse_lines )

"""
retrieve_yt.py
James Watson, 2019 February
Retrieve audio from YouTube videos
"""

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
    """ Fetch the comment thread IDs from the specified video info """
    kwargs   = remove_empty_kwargs( **kwargs )
    response = client.commentThreads().list( **kwargs ).execute()
    return print_response( response )

def comment_thread_by_thread_id( client , **kwargs ):
    """ Fetch the comments from the specified thread """
    kwargs   = remove_empty_kwargs( **kwargs ) 
    response = client.comments().list( **kwargs ).execute()
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

def timestamp_dict( hr = 0 , mn = 0 , sc = 0 ):
    """ Given hours, minutes, and seconds, return a timestamp of the type used by this program """
    return { 'H' : hr , 'M' : mn , 'S' : sc }

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
            
def get_timestamps_from_lines( lines , duration ):
    """ Attempt to get the tracklist from the list of 'lines' and return it , but only Return if all stamps are lesser than 'duration' """
    # 3. Get candidate tracklist from the description 
    trkLstFltrd = []
    for line in lines:
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
            
def duration_from_yt_response( reponseObj ):
    """ Get the timestamp from the YouTube search result """
    return parse_ISO8601_timestamp( extract_video_duration( reponseObj ) )
            
def scrape_and_check_timestamps_desc( reponseObj ):
    """ Attempt to get the tracklist from the response object and return it , Return if all the stamps are lesser than the duration """
    # NOTE: This function assumes that a playlist can be found in the decription
    # NOTE: This function assumes that if there is a number representing a songs's place in the sequence, then it is the first digits in a line
    
    # 1. Get the description from the response object
    descLines = extract_description_lines( reponseObj )
    # 2. Get the video length from the response object
    duration  = duration_from_yt_response( reponseObj )
    # 3. Scrape lines from the description
    return get_timestamps_from_lines( descLines , duration )

def extract_candidate_artist_and_track( inputStr ):
    """ Given the balance of the timestamp-sequence extraction , Attempt to infer the artist and track names """
    # 1. Split on dividing char "- "
    components = inputStr.split( '- ' )
    # 2. Strip leading and trailing whitespace
    components = [ comp.strip() for comp in components ]
    # 3. Retain nonempty strings
    components = [ comp for comp in components if len( comp ) ]
    #print components
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
    flagPrint = False
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

def fetch_metadata_by_yt_video_ID( ytVideoID ):
    """ Fetch and return the response object that results from a YouTube API search for 'ytVideoID' """
    global youtube , METADATA_SPEC
    return videos_list_by_id(
        youtube ,
        part = METADATA_SPEC ,
        id   = ytVideoID
    )  

def fetch_comment_threads_by_yt_ID( ytVideoID ): 
    """ Fetch and return comment thread metadata that results from a YouTube API search for 'ytVideoID' """
    global youtube , COMMENT_THREAD_SPEC
    return comment_threads_list_by_video_id(
        youtube ,
        part       = COMMENT_THREAD_SPEC ,
        videoId    = ytVideoID ,
        textFormat = "plainText",
        maxResults = 100       
    )

def fetch_comments_by_thread_id( ytThreadID ):
    """ Fetch and return thread comments that results from a YouTube API search for 'ytThreadID' """
    global youtube , COMMENT_LIST_SPEC
    return comment_thread_by_thread_id(
        youtube ,
        part       = COMMENT_LIST_SPEC ,
        parentId   = ytThreadID ,
        textFormat = "plainText"
    )

def list_all_files_w_EXT( searchPath , EXTlst ):
    """ Return all of the paths in 'searchPath' that have extensions that appear in 'EXTlst' , Extensions are not case sensitive """
    items = os.listdir( searchPath )
    rtnLst = []
    for item in items:
        fEXT = get_EXT( item )
        if fEXT in EXTlst:
            rtnLst.append( item )
    return rtnLst




# === Testing ==============================================================================================================================

if __name__ == "__main__":
    pass

# ___ End Tests ____________________________________________________________________________________________________________________________