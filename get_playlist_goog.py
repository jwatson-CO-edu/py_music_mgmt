# -*- coding: utf-8 -*-

# Sample Python code for youtube.playlistItems.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/guides/code_samples#python
# https://developers.google.com/youtube/v3/docs/playlistItems/list?apix_params=%7B%22part%22%3A%22contentDetails%2Cid%2Csnippet%22%2C%22maxResults%22%3A50%2C%22playlistId%22%3A%22PLxgoClQQBFjgTMrhvedWk8Q_CVLWwy3ak%22%7D#usage
# Get more than 50
# https://stackoverflow.com/a/24186305 , https://stackoverflow.com/a/18806043
# pageToken -   string
# The pageToken parameter identifies a specific page in the result set that should be returned.
# In an API response, the nextPageToken and prevPageToken properties identify other pages that could be retrieved.
#{
# "kind": "youtube#playlistItemListResponse",
# "etag": "\"ksCrgYQhtFrXgbHAhi9Fo5t0C2I/G99mykgtUP1skutiTa1KYZRom7w\"",
# "nextPageToken": "CDIQAA",
# "pageInfo": {
# "totalResults": 178,
#  "resultsPerPage": 50
# },

########################################################################################################################

__progname__ = "get_playlist_goog.py"
__version__  = "2020.04" 
__desc__     = "Get all the video links from a playlist"

# === Init Environment =================================================================================================
# ~~~ Prepare Paths ~~~
import sys, os.path
SOURCEDIR = os.path.dirname( os.path.abspath( __file__ ) ) 
PARENTDIR = os.path.dirname( SOURCEDIR )
# ~~ Path Utilities ~~
def prepend_dir_to_path( pathName ): sys.path.insert( 0 , pathName ) # Might need this to fetch a lib in a parent directory

from math import sqrt
# ~~ Local ~~
# from API_session import Session , open_all_APIs
# from retrieve_yt import fetch_metadata_by_yt_video_ID 

# ~~ Constants , Shortcuts , Aliases ~~
EPSILON = 1e-7
infty   = 1e309 # URL: http://stackoverflow.com/questions/1628026/python-infinity-any-caveats#comment31860436_1628026
endl    = os.linesep
sqt2    = sqrt(2)

# ~~ Script Signature ~~
def __prog_signature__(): return __progname__ + " , Version " + __version__ # Return a string representing program info

# ___ End Init _________________________________________________________________________________________________________

def get_all_playlist_videos( playlistURL ):
    """ Request playlist pages until all the videos on the playlist are listed """
    
    request = youtube.playlistItems().list(
        part="contentDetails,id,snippet",
        maxResults=50,
        playlistId="PLxgoClQQBFjgTMrhvedWk8Q_CVLWwy3ak"
    )
    response = request.execute()

if __name__ == "__main__":
    pass

########################################################################################################################

import os

# pip# install google-auth-oauthlib google-api-python-client --user
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

def main():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "YOUR_CLIENT_SECRET_FILE.json"

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    request = youtube.playlistItems().list(
        part="contentDetails,id,snippet",
        maxResults=50,
        playlistId="PLxgoClQQBFjgTMrhvedWk8Q_CVLWwy3ak"
    )
    response = request.execute()

    print(response)

