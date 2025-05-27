import redis.asyncio as aioredis
from redis.asyncio import ConnectionPool, Redis

# Redis connection with connection pool and timeout
redis_pool: ConnectionPool = aioredis.ConnectionPool(
    host="localhost",
    port=6379,
    decode_responses=True,
    max_connections=5,
    socket_connect_timeout=15,  # Wait up to 5 seconds for connection
)
redis_client: Redis = aioredis.Redis(connection_pool=redis_pool)


def get_redis() -> Redis:
    """
    Provide the Redis client.
    """
    try:
        yield redis_client
    finally:
        pass  # No need to close the client here; handled on shutdown
