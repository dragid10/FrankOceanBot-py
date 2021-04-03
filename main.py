import logging

import newrelic.agent
from util import cfg

newrelic.agent.global_settings().license_key = cfg.NEW_RELIC_KEY
newrelic.agent.initialize(config_file="newrelic.ini", environment="production", log_file="stderr",
                          log_level=logging.DEBUG)

from loguru import logger
import random
import genius_service
import twitter_service
import spotify_client


@newrelic.agent.background_task()
def handler(event, context):
    # Init all api clients
    spotibot = spotify_client.SpotifyService()
    geniusbot = genius_service.GeniusClient()
    twitterbot = twitter_service.TwitterClient()

    # Get all songs for artist (defined in cfg)
    songs = spotibot.get_all_artist_songs()

    # Choose random song to get lyrics for
    random_song = random.choice(songs)

    # Get lyrics for random song
    lyrics = geniusbot.get_lyrics(random_song.track_name, random_song.artist)

    # Get random pair of lyrics from song
    lyric_index = random.randint(0, len(lyrics) - 2)
    lyric1 = lyrics[lyric_index]
    lyric2 = lyrics[lyric_index + 1]
    tweet_lyrics = f"{lyric1}\n{lyric2}"
    logger.debug(f"Extraced 2 random lyrics")

    # Actually tweet  Lyrics
    status = False
    retry_limit = 0

    # Try to send tweet x times before ultimately failing
    logger.debug(f"Tweeting lyrics")
    while not status and retry_limit < 2:
        status = twitterbot.tweet(tweet_lyrics)
        retry_limit += 1
    retry_limit = 0


if __name__ == '__main__':
    app = newrelic.agent.register_application(timeout=10.0)
    with newrelic.agent.BackgroundTask(app, name="handler"):
        handler(None, None)
