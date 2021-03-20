from typing import Dict

import spotipy
from prodict import Prodict
from spotipy.oauth2 import SpotifyClientCredentials

from app.db_service import ElasticacheService
from util import cfg, base_logger

logger = base_logger.get_logger()


class Album:
    def __init__(self, album_id: str, tracks: list):
        self.album_id = album_id
        self.tracks = tracks


class SpotifyBot:
    _client = None

    def __init__(self):
        # Create spotify client to perform activities on
        self._client = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(client_id=cfg.SPOTIFY_CLIENT_ID,
                                                  client_secret=cfg.SPOTIFY_CLIENT_SECRET))

        self.db = ElasticacheService()

    def __get_all_artist_songs(self):
        albums = {}

        # First get all album names
        albums.update(self.__retrieve_albums("album"))
        albums.update(self.__retrieve_albums("single"))

        # Get all songs for each album
        for album, id in albums.items():
            # Probs really bad to overwrite val as I'm iterating through view, but oh whale 🤷🏿‍♂️
            albums[album] = Album(album_id=id, tracks=self.__retrieve_songs(album_id=id))

        # Store albums in a database (go to cache instead of hitting spotify each time)
        self.db.store_albums(albums=albums)

    def __retrieve_albums(self, alb_type: str = "album") -> dict:
        albums: Dict[str, str] = {}
        results = self._client.artist_albums(cfg.ARTIST_ID, album_type=alb_type, country="US")

        # Add all results (album_name: album_id) from first set to dict
        for item in results["items"]:
            albums[item["name"]] = item["id"]

        # Just get the name and id of the album
        while results["next"]:
            results = self._client.next(results)
            for item in results["items"]:
                albums[item["name"]] = item["id"]

        return albums

    def __retrieve_songs(self, album_id: str) -> list:
        tracks, results = [], self._client.album_tracks(album_id)

        for track in results["items"]:
            tracks.append(Prodict.from_dict({"track_name": track["name"], "track_id": track["id"]}))

        return tracks

    # TODO - REMOVE FUNCTION
    def run_test(self):
        self.__get_all_artist_songs()
