import random

from app.services import spotify_client, genius_service, twitter_service

if __name__ == '__main__':
    # Init all api clients
    spotibot = spotify_client.SpotifyService()
    geniusbot = genius_service.GeniusClient()
    twitterbot = twitter_service.TwitterClient()

    # Get all songs for artist (defined in cfg)
    songs = spotibot.get_all_artist_songs()

    # Choose random song to get lyrics for
    random_song = random.choice(songs)

    # Get lyrics for random song
    lyrics = geniusbot.get_lyrics(random_song.track_name)

    # Get random pair of lyrics from song
    lyric_index = random.randint(0, len(lyrics) - 2)
    lyric1 = lyrics[lyric_index]
    lyric2 = lyrics[lyric_index + 1]
    tweet_lyrics = f"{lyric1}\n{lyric2}"

    # Actually tweet  Lyrics
    status = False
    retry_limit = 0

    # Try to send tweet x times before ultimately failing
    while not status and retry_limit < 2:
        status = twitterbot.tweet(tweet_lyrics)
        retry_limit += 1
    retry_limit = 0
