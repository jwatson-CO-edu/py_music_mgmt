# ~~~ Imports ~~~
# ~~ Standard ~~
import shutil , os , traceback
from math import pi , sqrt
from random import randrange
from time import sleep
from warnings import warn
# ~~ Local ~~
from marchhare.Utils3 import ( Stopwatch , strip_EXT , yesno , unpickle_dict ,
                               ensure_dirs_writable , struct_to_pkl , nowTimeStampFine , 
                               confirm_or_crash , LogMH , parse_lines , load_pkl_struct )

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
    print( "Loaded 'apiclient'! (Google)" )
except:
    print( "Could not import `apiclient.discovery`, attempt `googleapiclient`" )
    try:
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
        print( "Loaded 'googleapiclient'!" )
    except:
        print( "COULD NOT IMPORT API UNDER EITHER ALIAS" )
import oauth2client  
print( "Loaded 'oauth2client'!" )
import pygn
from pygn.pygn import register , search
print( "Loaded 'pygn'! (GraceNote)" )

def comma_sep_key_val_from_file( fPath ):
    """ Read a file, treating each line as a key-val pair separated by a comma """
    entryFunc = lambda txtLine : [ str( rawToken ).strip() for rawToken in txtLine.split( ',' ) ]
    lines = parse_lines( fPath , entryFunc )
    rtnDict = {}
    for line in lines:
        rtnDict[ line[0] ] = line[1]
    return rtnDict

# == youtube-dl Logging ==

class MyLogger( object ):
    """ Logging class for YT downloads """
    # https://github.com/rg3/youtube-dl/blob/master/README.md#embedding-youtube-dl
    
    def __init__( self ):
        """ Put ther noisier output in separate logs for easier debugging """
        self.dbgLog = LogMH()
        self.wrnLog = LogMH()
        self.errLog = LogMH()
        
    def debug( self , msg ):
        """ Log debug output """
        self.dbgLog.prnt( "DEBUG:" , msg )
        
    def warning( self , msg ):
        """ Log warnings """
        self.wrnLog.prnt( "WARN:" , msg )
        
    def error( self , msg ):
        """ Log erros in the main log """
        self.errLog.prnt( "ERROR:" , msg )

def my_hook( d ):
    # https://github.com/rg3/youtube-dl/blob/master/README.md#embedding-youtube-dl
    if d[ 'status' ] == 'finished':
        print( 'Done downloading, now converting ...' )

# __ End Logging __


# ===== class Session =====

class Session:
    """ Flags and vars representing a session , Also acts as a repo for what would otherwise be globals """
    
    DEFAULT_PKL_PATH = "music_record.pkl";
    
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
        self.SOURCEDIR = SOURCEDIR
        
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
        
        # ~ BEGIN ~
        self.start_session()
        
    def open_all_APIs( self ):
        """ Open an API connection for {Google , GraceNote} """
        # NOTE: 'load_session' must be run first
        try:
            # 2. Init Google API connection
            self.authDict = comma_sep_key_val_from_file( self.GOOG_KEY_PATH ) # "APIKEY.txt"
            self.DEVELOPER_KEY = self.authDict['key']
            #print( authDict )
            self.youtube = build( self.YOUTUBE_API_SERVICE_NAME , 
                                  self.YOUTUBE_API_VERSION , 
                                  developerKey = self.DEVELOPER_KEY )
            # 3. Init GraceNote API Connection
            self.gnKey = comma_sep_key_val_from_file( self.GRNT_KEY_PATH ) # "GNWKEY.txt"
            self.gnClient = self.gnKey[ 'clientID' ] #_ Enter your Client ID here '*******-************************'
            self.gnUser   = register( self.gnClient ) # Registration should not be done more than once per session      
            
            print( "API Connection SUCCESS!" )
            
        except Exception as ex:
            print( "API Connection FAILURE!" , str( ex ) )
            
    def default_session( self ):
        """ Set the session vars to reasonable values """
        self.RAW_FILE_DIR       = "output";                        print( "RAW_FILE_DIR:" , self.RAW_FILE_DIR )
        self.CHOPPED_SONG_DIR   = self.RAW_FILE_DIR + "/chopped";  print( "CHOPPED_SONG_DIR:" , self.CHOPPED_SONG_DIR )
        self.PICKLE_DIR         = "";                              print( "PICKLE_DIR:" , self.PICKLE_DIR )
        self.LOG_DIR            = "logs";                          print( "LOG_DIR" , self.LOG_DIR )
        self.RECORD_PICKLE_PATH = Session.DEFAULT_PKL_PATH;        print( "RECORD_PICKLE_PATH:" , self.RECORD_PICKLE_PATH )
        self.ARTIST_PICKLE_PATH = "artists.pkl";                   print( "ARTIST_PICKLE_PATH:" , self.ARTIST_PICKLE_PATH )
        self.record             = {};                              print( "Record structure created!" )           
        
    def save_session( self ):
        """ Serialize Music information """
        self.record[ 'RAW_FILE_DIR' ]       = self.RAW_FILE_DIR
        self.record[ 'CHOPPED_SONG_DIR' ]   = self.CHOPPED_SONG_DIR
        self.record[ 'PICKLE_DIR' ]         = self.PICKLE_DIR
        self.record[ 'LOG_DIR' ]            = self.LOG_DIR
        self.record[ 'ARTIST_PICKLE_PATH' ] = self.ARTIST_PICKLE_PATH
        self.record[ 'RECORD_PICKLE_PATH' ] = self.RECORD_PICKLE_PATH
        try:
            struct_to_pkl( self.record , self.RECORD_PICKLE_PATH )
        except:
            print( "FAILED to save" , self.RECORD_PICKLE_PATH )
            traceback.print_exc()
        
    def load_session( self , path ):
        """ De-Serialize Music information """
        self.record = load_pkl_struct( path )
        if self.record == None:
            print( "FAILED to load" , path )
            return False
        else:
            self.RAW_FILE_DIR       = self.record[ 'RAW_FILE_DIR' ] 
            self.CHOPPED_SONG_DIR   = self.record[ 'CHOPPED_SONG_DIR' ] 
            self.PICKLE_DIR         = self.record[ 'PICKLE_DIR' ] 
            self.LOG_DIR            = self.record[ 'LOG_DIR' ] 
            self.ARTIST_PICKLE_PATH = self.record[ 'ARTIST_PICKLE_PATH' ] 
            self.RECORD_PICKLE_PATH = self.record[ 'RECORD_PICKLE_PATH' ] 
            return True
            
    def verify_session_writable( self ):
        """ Make sure that we can write to the relevant directories , If DNE then create && check """
        allWrite = ensure_dirs_writable(  
            os.path.join( SOURCEDIR , self.RAW_FILE_DIR )     ,
            os.path.join( SOURCEDIR , self.CHOPPED_SONG_DIR ) ,
            os.path.join( SOURCEDIR , self.PICKLE_DIR )       ,
            os.path.join( SOURCEDIR , self.LOG_DIR )          ,
        )
        print( "Session dirs writable:" , yesno( allWrite ) )
        return allWrite            
                
    def start_session( self , path = None ):
        """ Get object ready for music processing """
        if path == None:
            path = self.DEFAULT_PKL_PATH
        print()
        # 1. Attempt to load the existing music database
        if not self.load_session( path ):
            self.default_session()
            print( "Started a default session" )
        else:
            print( "Loaded session from" , path )
        print()
        # 2. Connect to APIs
        self.open_all_APIs()
        print()
        # 3. Confirm that program has permission to write
        self.verify_session_writable()
        
    def close_session( self ):
        """ Cache data and write logs """
        # 1. Save the record
        self.save_session()
        # N. Report
        print( "\nSession CLOSED!" )
    
    

# _____ End Session _____

# ~~~ TESTING ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ == '__main__':
    sssn = Session()
    sssn.close_session()