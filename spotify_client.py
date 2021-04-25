import re

import newrelic.agent
from typing import Dict

from prodict import Prodict
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials

from util import cfg, base_logger

logger = base_logger.get_logger()


class Album:
    def __init__(self, album_id: str, tracks: list):
        self.album_id = album_id
        self.tracks = tracks


class SpotifyService:
    _client = None

    def __init__(self):
        # Create spotify client to perform activities on
        self._client = Spotify(
            auth_manager=SpotifyClientCredentials(client_id=cfg.SPOTIFY_CLIENT_ID,
                                                  client_secret=cfg.SPOTIFY_CLIENT_SECRET))

        # self.db = ElastiCacheService()

    @newrelic.agent.function_trace()
    def get_all_artist_songs(self) -> list:
        albums = {}

        # First get all album names
        albums.update(self.__retrieve_albums("album"))
        albums.update(self.__retrieve_albums("single"))

        # Get all songs for each album
        for album, id in albums.items():
            # Probs really bad to overwrite val as I'm iterating through view, but oh whale 🤷🏿‍♂️
            albums[album] = Album(album_id=id, tracks=self.__retrieve_songs(album_id=id))

        # TODO - Store albums in a database (go to cache instead of hitting spotify each time)
        # self.db.store_albums(albums=albums)

        logger.debug(f"Succesfully retrieved artist songs")

        flat_track_list = []
        for albs in albums.values():
            for song in albs.tracks:
                flat_track_list.append(song)
        return flat_track_list

    @newrelic.agent.function_trace()
    def __retrieve_albums(self, alb_type: str = "album") -> dict:
        albums: Dict[str, str] = {}
        results = self._client.artist_albums(cfg.ARTIST_ID, album_type=alb_type, country="US")

        # Add all results (album_name: album_id) from first set to dict
        for item in results["items"]:
            # Check if the album already exits in the dict (solves slightly different album titles for same album)
            album_name = item["name"]
            if "(Solo)" in album_name:
                stripped_album_name = album_name.strip()
            else:
                paren_regex_str = r"\((?!(Solo)$).+\)$"
                parenth_reg = re.compile(paren_regex_str)
                stripped_album_name = re.sub(parenth_reg, "", album_name)
                stripped_album_name = stripped_album_name.strip()

            albums[stripped_album_name] = item["id"]

        # Just get the name and id of the album
        while results["next"]:
            results = self._client.next(results)
            for item in results["items"]:
                albums[item["name"]] = item["id"]

        return albums

    @newrelic.agent.function_trace()
    def __retrieve_songs(self, album_id: str) -> list:
        tracks, results = [], self._client.album_tracks(album_id)

        for track in results["items"]:
            track_name = track["name"]
            track_id = track["id"]
            artist = track["artists"][0]["name"]

            # Try to not include (Side) part of name, to make genius lookups easier
            end_index = len(track_name)
            if track_name.find("(Side") != -1:
                end_index = track_name.find("(Side")

            tracks.append(Prodict.from_dict(
                {"track_name": track_name[:end_index].strip(),
                 "track_id": track_id,
                 "artist": artist,
                 }))

        return tracks
