"""
Redis client factory.

Used for active call state, TTL-based sessions, live risk state, caching,
rate limiting and event coordination (Architecture.md section 9).
"""

from redis.asyncio import Redis, from_url

from app.config import get_settings

_redis: Redis | None = None


def get_redis() -> Redis:
    global _redis
    if _redis is None:
        _redis = from_url(get_settings().redis_url, decode_responses=True)
    return _redis


async def ping_redis() -> bool:
    try:
        redis = get_redis()
        return bool(await redis.ping())
    except Exception:
        return False
