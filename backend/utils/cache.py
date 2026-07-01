import os
import json

import redis
from dotenv import load_dotenv


load_dotenv()

cache = redis.from_url(
    os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    decode_responses=True,
)


def delete_pattern(pattern):
    try:
        for key in cache.scan_iter(pattern):
            cache.delete(key)
    except redis.RedisError as error:
        print(f"Redis cache delete pattern failed: {error}")


def cache_get_json(key):
    try:
        cached_value = cache.get(key)
        if cached_value:
            return json.loads(cached_value)
    except (redis.RedisError, json.JSONDecodeError) as error:
        print(f"Redis cache read failed for {key}: {error}")

    return None


def cache_set_json(key, value, seconds=300):
    try:
        cache.setex(key, seconds, json.dumps(value))
    except (redis.RedisError, TypeError) as error:
        print(f"Redis cache write failed for {key}: {error}")


def cache_delete(key):
    try:
        cache.delete(key)
    except redis.RedisError as error:
        print(f"Redis cache delete failed for {key}: {error}")
