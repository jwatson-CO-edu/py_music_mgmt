
# ~~~ Imports ~~~
# ~~ Standard ~~
import shutil , os
from math import pi , sqrt
from random import randrange
from time import sleep
from warnings import warn
# ~~ Local ~~
from marchhare.marchhare import ( Stopwatch , strip_EXT , yesno , unpickle_dict ,
                                  ensure_dirs_writable , struct_to_pkl , nowTimeStampFine , 
                                  confirm_or_crash , )

# ~~~ Init ~~~
SOURCEDIR = os.path.dirname( os.path.abspath( '__file__' ) ) # URL, dir containing source file: http://stackoverflow.com/a/7783326
PARENTDIR = os.path.dirname( SOURCEDIR )


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
import oauth2client  
print "Loaded 'oauth2client'!"
import pygn
from pygn.pygn import register , search
print "Loaded 'pygn'! (GraceNote)"

from marchhare.marchhare import ( LogMH , parse_lines )

def comma_sep_key_val_from_file( fPath ):
    """ Read a file, treating each line as a key-val pair separated by a comma """
    entryFunc = lambda txtLine : [ str( rawToken ).strip() for rawToken in txtLine.split( ',' ) ]
    lines = parse_lines( fPath , entryFunc )
    rtnDict = {}
    for line in lines:
        rtnDict[ line[0] ] = line[1]
    return rtnDict

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
    
def confirm_session( session ):
    """ Print the session vars, then ask for confirmation """
    print
    print "RAW_FILE_DIR:" ,         session.RAW_FILE_DIR
    print "CHOPPED_SONG_DIR:" ,     session.CHOPPED_SONG_DIR
    print "PICKLE_DIR:" ,           session.PICKLE_DIR 
    print "ACTIVE_PICKLE_PATH:" ,   session.ACTIVE_PICKLE_PATH
    print "LOG_DIR" ,               session.LOG_DIR
    print "ACTIVE_SESSION:" ,       yesno( session.ACTIVE_SESSION )
    print "ARTIST_PICKLE_PATH:" ,   session.ARTIST_PICKLE_PATH
    confirm_or_crash( "Enter Text to Reject Session: " )
    print
    

def open_all_APIs( sssn ):
    """ Open an API connection for {Google , GraceNote} """
    # NOTE: 'load_session' must be run first
    try:
        # 2. Init Google API connection
        sssn.authDict = comma_sep_key_val_from_file( sssn.GOOG_KEY_PATH ) # "APIKEY.txt"
        sssn.DEVELOPER_KEY = sssn.authDict['key']
        #print( authDict )
        sssn.youtube = build( sssn.YOUTUBE_API_SERVICE_NAME , 
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
    session.RAW_FILE_DIR       = "output";                             print "RAW_FILE_DIR:" , cRAW_FILE_DIR
    session.CHOPPED_SONG_DIR   = session.RAW_FILE_DIR + "/chopped";    print "CHOPPED_SONG_DIR:" , session.CHOPPED_SONG_DIR
    session.PICKLE_DIR         = "input";                              print "PICKLE_DIR:" , session.PICKLE_DIR 
    session.ACTIVE_PICKLE_PATH = session.PICKLE_DIR + "/session.pkl";  print "ACTIVE_PICKLE_PATH:" , session.ACTIVE_PICKLE_PATH
    session.LOG_DIR            = "logs";                               print "LOG_DIR" , session.LOG_DIR
    session.ACTIVE_SESSION     = bool( int( 1 ) );                     print "ACTIVE_SESSION:" , yesno( session.ACTIVE_SESSION )
    session.ARTIST_PICKLE_PATH = session.PICKLE_DIR + "/artists.pkl";  print "ARTIST_PICKLE_PATH:" , session.ARTIST_PICKLE_PATH
    return session    
    
def construct_session( session ):
    """ Ensure that the session makes sense """
    session.CHOPPED_SONG_DIR = session.RAW_FILE_DIR + "/chopped"
    
    
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
    """ Make sure that we can write to the relevant directories , If DNE then create && check """
    allWrite = ensure_dirs_writable(  
        os.path.join( SOURCEDIR , sssn.RAW_FILE_DIR )     ,
        os.path.join( SOURCEDIR , sssn.CHOPPED_SONG_DIR ) ,
        os.path.join( SOURCEDIR , sssn.PICKLE_DIR )       ,
        os.path.join( SOURCEDIR , sssn.LOG_DIR )          ,
    )
    print "Session dirs writable:" , yesno( allWrite )
    return allWrite

def set_session_active( active = 1 ):
    """ Set the session active flag """
    global ACTIVE_SESSION , SESSION_PATH
    ACTIVE_SESSION = bool( active )
    
def begin_session( inputPath , overridePath = None ):
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
    # 5. If there was an override file provided, load
    if overridePath:
        sesnDict = comma_sep_key_val_from_file( overridePath );     
        print "Loaded session file:" , overridePath
        for key , val in sesnDict.iteritems():
            try:
                setattr( session , key , val )
                print "Override: Set" , key , "to" , val
            except:
                print key , "is not a session variable!"
    else:
        print "There was no override file provided"
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
