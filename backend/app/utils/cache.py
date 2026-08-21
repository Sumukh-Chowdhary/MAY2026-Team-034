import json
import redis

from app.extensions import redis_client


DEFAULT_CACHE_TTL = 300


def get_cached(key):
    try:
        cached = redis_client.get(key)

        if cached is None:
            return None

        return json.loads(cached)

    except (redis.RedisError, json.JSONDecodeError):
        return None


def set_cached(key, value, ttl=DEFAULT_CACHE_TTL):
    try:
        redis_client.setex(
            key,
            ttl,
            json.dumps(value)
        )
    except (redis.RedisError, TypeError):
        pass


def delete_cached(key):
    try:
        redis_client.delete(key)
    except redis.RedisError:
        pass