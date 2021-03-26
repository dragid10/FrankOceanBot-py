import tweepy
from tweepy import Status

from util import cfg, base_logger

logger = base_logger.get_logger()


class TwitterClient:
    __TWEET_CHAR_LIMIT = 280

    def __init__(self):
        auth = tweepy.OAuthHandler(cfg.TWITTER_API_KEY, cfg.TWITTER_API_SECRET)
        auth.set_access_token(cfg.TWITTER_TOKEN, cfg.TWITTER_TOKEN_SECRET)

        self.client = tweepy.API(auth)

    def tweet(self, lyrics: str) -> bool:
        # Do a pre-check if the lyrics go over the twitter char limit
        if len(lyrics) > self.__TWEET_CHAR_LIMIT:
            return False

        # Try to send tweet, and raise error status if any
        try:
            resp: Status = self.client.update_status(lyrics)

            # if tweet successfully sent, we'll get the tweet back with a created ts
            if not hasattr(resp, "created_at"):
                raise Exception("Tweet Failed to Post")
        except Exception as ex:
            logger.exception(ex)
            return False

        return True
