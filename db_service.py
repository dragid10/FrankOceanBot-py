from abc import abstractmethod
from typing import List, Dict

import redis

from spotify_client import Album


class BaseDbService:

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def store_album(self, album: Album):
        raise NotImplementedError

    @abstractmethod
    def store_albums(self, albums: List[Album]):
        raise NotImplementedError


class ElastiCacheService(BaseDbService):
    def __init__(self):
        super().__init__()
        redis_client = redis.Redis(host='TODO', port=0000, db=0)

    def store_album(self, album: Album):
        pass

    def store_albums(self, albums: Dict[Album]):
        for k, v in albums.items():
            pass
