#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ~~ Future First ~~
from __future__ import division , unicode_literals # Future imports must be called before everything else, including triple-quote docs!

__progname__ = "yt_dl_new_music.py"
__version__  = "2018.10" 
__desc__     = "Fetch videos and music files from youtube for free"
"""
James Watson , Template Version: 2018-05-14
Built on Wing 101 IDE for Python 2.7

Dependencies: numpy , youtube-dl , FFmpeg
"""


"""  
~~~ Developmnent Plan ~~~
[Y] Test at the command line
[ ] Fetch example from the docs
    [ ] Test the example under linux
[ ] Build a list of music to listen to
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

# ~~ Constants , Shortcuts , Aliases ~~
EPSILON = 1e-7
infty   = 1e309 # URL: http://stackoverflow.com/questions/1628026/python-infinity-any-caveats#comment31860436_1628026
endl    = os.linesep

# ~~ Script Signature ~~
def __prog_signature__(): return __progname__ + " , Version " + __version__ # Return a string representing program name and verions

# ___ End Init _____________________________________________________________________________________________________________________________


# === Main Application =====================================================================================================================

# = Classes =

class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)

# _ End Class _

# = Program Functions =

def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')

# _ End Func _

# = Program Vars =



# _ End Vars _

if __name__ == "__main__":
    print __prog_signature__()
    termArgs = sys.argv[1:] # Terminal arguments , if they exist
    
    # Downloading youtube videos as MP3: https://github.com/rg3/youtube-dl/blob/master/README.md#embedding-youtube-dl
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'logger': MyLogger(),
        'progress_hooks': [my_hook],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download(['https://www.youtube.com/watch?v=BaW_jenozKc'])  
    

# ___ End Main _____________________________________________________________________________________________________________________________


# === Spare Parts ==========================================================================================================================



# ___ End Spare ____________________________________________________________________________________________________________________________

