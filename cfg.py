from decouple import config

# Spotify Secrets
SPOTIFY_CLIENT_ID = config("spotify_client_id")
SPOTIFY_CLIENT_SECRET = config("spotify_client_secret")

# Twitter secrets
TWITTER_API_KEY = config("twitter_api_key")
TWITTER_API_SECRET = config("twitter_api_secret")
TWITTER_TOKEN = config("twitter_token")
TWITTER_TOKEN_SECRET = config("twitter_token_secret")