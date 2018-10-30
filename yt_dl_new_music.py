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
[ ] Fetch example from the docs
    [ ] Test the example under linux
[ ] Build a list of music to listen to
    [ ] Study Jams
    [ ] Establish a input playlist format
    [ ] Review list
    [ ] Artists to try
[ ] Find example of how to split songs by track
    [ ] URL , Split songs with multiprocess: https://codereview.stackexchange.com/q/166158
    [ ] Test with dummy times
[ ] Split songs by track
    [ ] Locate timestamps in the description or comments
    [ ] Discern artist & track for each listing
    { } artist-track check: Google , Wikipedia?
    [ ] Split audio by confirmed timestamps
    [ ] Load id3 metadata for individual tracks
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
# ~~ Special ~~
import numpy as np
import youtube_dl
# ~~ Local ~~
from marchhare.marchhare import parse_lines

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

def parse_video_entry( txtLine ):
    """ Obtain the video url from the line """
    components = [ rawToken for rawToken in txtLine.split( ',' ) ]
    return { 'url' : components[0] ,
             'seq' : components[1] }

def process_video_list( fPath ):
    """ Get all the URLs from the prepared list """
    return parse_lines( fPath , parse_video_entry )

def my_hook( d ):
    # https://github.com/rg3/youtube-dl/blob/master/README.md#embedding-youtube-dl
    if d[ 'status' ] == 'finished':
        print( 'Done downloading, now converting ...' )

# _ End Func _

# = Program Vars =



# _ End Vars _

if __name__ == "__main__":
    print __prog_signature__()
    termArgs = sys.argv[1:] # Terminal arguments , if they exist
    
    # Downloading youtube videos as MP3: https://github.com/rg3/youtube-dl/blob/master/README.md#embedding-youtube-dl
    
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

