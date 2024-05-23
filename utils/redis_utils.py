import redis
from redis import Redis

from config import get_config_by_name

redis_client = None


def get_redis_client() -> Redis:
    global redis_client
    if redis_client is None:
        redis_client = redis.StrictRedis(host=get_config_by_name("REDIS_HOST"),
                                         port=get_config_by_name("REDIS_PORT"),
                                         db=get_config_by_name("REDIS_DATABASE"))
    return redis_client


def init_redis_cache():
    get_redis_client()


def get_redis_cache(key):
    return get_redis_client().get(key)


def set_redis_cache(key, value):
    get_redis_client().set(key, value)
