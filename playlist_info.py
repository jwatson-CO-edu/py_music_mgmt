#!/usr/bin/python

# https://gist.github.com/bondurantdt/3913d4f92597a0fa39e0

'''
This code will query the Youtube Data API (requires a client.json file, see below)
to determine videos in the ICA webcast playlist and their viewcount.

Queries the playlistItems method first to obtain video IDs (Cost 1 unit, in addition 
to the costs of the resource parts queried).

Queries the videos method next to parse the friendly name and view count
of obtained video IDs (Cost 1 unit, in addition to the costs of the resource 
parts queried).

Spits out results (currently limited to 50).
'''

import httplib2
import os
import sys

from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow


# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the Google Developers Console at
# https://console.developers.google.com/.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = "client_secrets.json"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the Developers Console
https://console.developers.google.com/

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))

# This OAuth 2.0 access scope allows for read-only access to the authenticated
# user's account, but not other types of account access.
YOUTUBE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
  message=MISSING_CLIENT_SECRETS_MESSAGE,
  scope=YOUTUBE_SCOPE)

storage = Storage("%s-oauth2.json" % sys.argv[0])
credentials = storage.get()

if credentials is None or credentials.invalid:
  flags = argparser.parse_args()
  credentials = run_flow(flow, storage, flags)

youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
  http=credentials.authorize(httplib2.Http()))

#Call the playlistItems API      
playlist_response = youtube.playlistItems().list(
    part="snippet,contentDetails,id,status",
    playlistId="PLFnRbMKeEztEc2GrIddxvq_4wAssSoIdB",
    maxResults=50
)

while playlist_response:
    playlist_response_ex = playlist_response.execute()

    playlist_videos=[]

# Merge video ids
    for entry in playlist_response_ex.get("items", []):
        playlist_videos.append(entry["contentDetails"]["videoId"])
        video_ids = ",".join(playlist_videos)

  # Call the videos.list method to retrieve location details for each video.
    video_response = youtube.videos().list(
        id=video_ids,
        part='snippet, statistics'
    ).execute()

    videos = []

# Add each result to the list, and then display the list of matching videos.
    for video_result in video_response.get("items", []):
        videos.append("Title: %s \nViews: %s\n" % (video_result["snippet"]["title"],
                              video_result["statistics"]["viewCount"]))
    print "\n".join(videos)
    playlist_response = youtube.playlistItems().list_next(
        playlist_response, playlist_response_ex)
