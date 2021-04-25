import newrelic.agent
from typing import List

from lyricsgenius import Genius
from lyricsgenius.song import Song

from util import cfg, base_logger

logger = base_logger.get_logger()


class GeniusClient:
    def __init__(self):
        self.genius_client = Genius(cfg.GENIUS_ACCESS_TOKEN)
        self.genius_client.remove_section_headers = True  # Remove section headers (e.g. [Chorus]) from lyrics when searching
        self.genius_client.verbose = False  # Turn off status messages
        self.genius_client.skip_non_songs = True  # Exclude hits thought to be non-songs (e.g. track lists)
        self.genius_client.excluded_terms = ["Clean", "(Side A)", "(Side B)"]  # Exclude songs with these words in their title

    @newrelic.agent.background_task()
    @newrelic.agent.function_trace()
    def get_lyrics(self, song: str, artist: str = None) -> List[str]:
        if song == "End" and "Frank Ocean" in artist:
            song = "End/Golden Girl"
        try:
            if not artist:
                lyrics: Song = self.genius_client.search_song(title=song)
            else:
                lyrics: Song = self.genius_client.search_song(title=song, artist=artist)

            logger.debug(f"Got lyrics for song {song}")
            return lyrics.lyrics.strip().replace("\n\n", "\n").split("\n")
        except Exception as ex:
            logger.exception(f"Caught an exception getting lyrics: {ex}")
