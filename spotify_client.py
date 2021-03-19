import os

import spotipy
from spotipy import SpotifyClientCredentials


class SpotifyBot:
    def __init__(self):
        client = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id= ,
                                                                       client_secret=))
