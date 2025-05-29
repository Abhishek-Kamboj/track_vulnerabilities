from typing import Optional

import redis.asyncio as aioredis
from redis.asyncio import ConnectionPool, Redis

from src.app_constants import (
    CACHE_TTL_SECONDS,
    REDIS_HOST,
    REDIS_MAX_CONNECTIONS,
    REDIS_PORT,
    REDIS_SOCKET_CONNECTION_TIMEOUT,
)

# Redis connection with connection pool and timeout
redis_pool: ConnectionPool = aioredis.ConnectionPool(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True,
    max_connections=REDIS_MAX_CONNECTIONS,
    socket_connect_timeout=REDIS_SOCKET_CONNECTION_TIMEOUT,  # Wait up to 15 seconds for connection
)
redis_client: Redis = aioredis.Redis(connection_pool=redis_pool)


def get_redis() -> Redis:
    """
    Provide the Redis client. used for dependency injection
    """
    try:
        yield redis_client
    finally:
        pass  # No need to close the client here; handled on shutdown


async def get_cache_ttl(
    key: str, redis_client: Redis, ttl: int = CACHE_TTL_SECONDS
) -> Optional[str]:
    """
    Retrieve a value from Redis cache and extend its TTL if found.

    Args:
        key (str): The key to retrieve from the Redis cache.
        redis_client (Redis): The initialized and connected redis client instance for cache operations.
        ttl (int, optional): Time-to-live in seconds for the key's expiration.
            Defaults to CACHE_TTL_SECONDS.

    Returns:
        Optional[str]: The cached value if found, otherwise None.
    """
    value = await redis_client.get(key)
    if value:
        # Extend TTL on access
        await redis_client.expire(key, ttl)
    return value


async def set_cache_ttl(
    key: str, value: str, redis_client: Redis, ttl: int = CACHE_TTL_SECONDS
):
    """Set a key-value pair in Redis cache with a specified TTL.

    Args:
        key (str): The key to set in the Redis cache.
        value (str): The value to associate with the key.
        redis_client (redis.Redis): The Redis client instance for cache operations.
        ttl int: Time-to-live in seconds for the key's expiration.
            Defaults to CACHE_TTL_SECONDS.
    """
    await redis_client.set(key, value, ex=ttl or CACHE_TTL_SECONDS)
