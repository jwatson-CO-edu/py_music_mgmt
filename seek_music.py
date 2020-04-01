# ~~ Standard ~~
import os , shutil , traceback , sys , requests
import urllib.request 
# Importing libraries 
import bs4 as bs 
from PyQt5.QtWebEngineWidgets import ( QWebEnginePage , QWebEngineView , QWebEngineProfile )
# from PyQt5.QtWebEngineWidgets import QWebEngineView
# from PyQt5.QtWebEngineWidgets import QWebEngineProfile
from PyQt5.QtWidgets import QApplication 
from PyQt5.QtCore import QUrl 
import pytube # library for downloading youtube videos 
# ~~ Local ~~
SOURCEDIR = os.path.dirname( os.path.abspath( '__file__' ) ) # URL, dir containing source file: http://stackoverflow.com/a/7783326
PARENTDIR = os.path.dirname( SOURCEDIR )
# ~~ Path Utilities ~~
def prepend_dir_to_path( pathName ): sys.path.insert( 0 , pathName ) # Might need this to fetch a lib in a parent directory
prepend_dir_to_path( SOURCEDIR )


# === Playlist Extraction ==============================================================================================









"""
2019-12-29: At the current time, trying to unpack JS frames manually is too time consuming to consider
"""
# Author "md1844" , https://www.geeksforgeeks.org/python-program-to-download-complete-youtube-playlist/

# https://www.whoishostingthis.com/tools/user-agent/
_USERAGENT = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:71.0) Gecko/20100101 Firefox/71.0"

# == class Page ==

class Page( QWebEnginePage ):
    """ Object representing a webpage loaded into memory """
    
    def __init__( self , url , UA = _USERAGENT ):
        """ Load the page at `url` """
        # 1. Set up the web application engine
        
        self.app = QApplication( sys.argv )
        
        # https://doc.qt.io/qtforpython/PySide2/QtWebEngineWidgets/QWebEnginePage.html
        # https://doc.qt.io/qtforpython/PySide2/QtWebEngineWidgets/QWebEngineProfile.html#PySide2.QtWebEngineWidgets.QWebEngineProfile
        # https://doc.qt.io/qtforpython/PySide2/QtWebEngineWidgets/QWebEngineProfile.html#PySide2.QtWebEngineWidgets.PySide2.QtWebEngineWidgets.QWebEngineProfile.setHttpUserAgent
        profile = QWebEngineProfile()
        profile.setHttpUserAgent( UA )
        print( "Created a web viewer with UA\n" , profile.httpUserAgent() )
        # https://doc.qt.io/qtforpython/PySide2/QtWebEngineWidgets/QWebEnginePage.html#PySide2.QtWebEngineWidgets.PySide2.QtWebEngineWidgets.QWebEnginePage.runJavaScript
        QWebEnginePage.__init__( self , profile ) 
        self.html = '' 
        self.loadFinished.connect( self._on_load_finished )
        # 2. Set up the user agent
        self.load( QUrl( url ) ) 
        self.app.exec_() 

    def _on_load_finished( self ):
        """ Load page HTML and report """
        self.html = self.toHtml( self.Callable ) 
        print( 'Load finished' ) 

    def Callable( self , html_str ):
        # Probably a callback?
        self.html = html_str 
        self.app.quit()
        
def page_request( url , UA = _USERAGENT ):
    """ Request a page with a spoofed user agent """
    headers = { 'User-Agent' : UA }
    r       = requests.get( url , headers = headers )
    return r.text

# __ End Page __

def exact_link( link ):
    """ Construct a valid URL """
    vid_id = link.split( '=' ) 
    Str = "" 
    for i in vid_id[0:2]: 
        Str += i + "="
    str_new  = Str[ 0 : len( Str )-1 ] 
    index    = str_new.find( "&" ) 
    new_link = "https://www.youtube.com" + str_new[ 0:index ] 
    return new_link 

def get_all_playlist_vid_links( lstURL ):
    """ Return a list of URLs for individual videos in a playlist """
    count = 0
    links = [] 
    # 1. Load the page
    if 1:
        page = Page( lstURL )
        soup = bs.BeautifulSoup( page.html , 'html.parser' )
    else:
        soup = bs.BeautifulSoup( page_request( lstURL ) , 'html.parser' )
    # 2. Iterate over page
    matches = soup.find_all( 'a' , id = 'thumbnail' ) 
    #matches = soup.find_all( 'a' , {'class':'pl-video-title-link'} ) 
    #matches = soup.find_all( 'a' , {'class':'yt-simple-endpoint inline-block style-scope ytd-thumbnail'} )
    print( "Found" , len( matches ) , "matches." )
    for link in matches:
        # Not using first link because it is playlist link not particular video link 
        if count == 0: 
            count += 1
            continue
        else:
            print( link , '\n' )
            #vid_src = link[ 'href' ] 
            # keeping the format of link to be given to pytube otherwise in some cases 
            #new_link = exact_link( vid_src ) 
        # appending the link to the links array 
        #links.append( new_link )
    return links
    
# ___ End Playlist _____________________________________________________________________________________________________


# ~~~ TESTING ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if __name__ == '__main__':
    
    URL = 'https://www.youtube.com/watch?v=Ig5v4jhLLWI&list=PL63ZO-jXFTasqvj7WdEFQ6QtG6UBrl9CR'
    for i , link in enumerate( get_all_playlist_vid_links( URL ) ):
        print( i+1 , ':' , link )
    