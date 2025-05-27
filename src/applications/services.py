from typing import List, Dict
import aiohttp

import redis.asyncio as aioredis
from redis.asyncio import Redis
from fastapi import Depends

import json

from src.logging_utils import logger
from src.redis_utils import get_redis

OSV_SERVICE_URL: str = "https://api.osv.dev/v1/query"
ECO_SYSTEM = "PyPI"


async def fetch_vulnerabilities(
    package: str, version: str, redis_client: Redis = Depends(get_redis)
) -> List[Dict]:
    """Fetch vulnerabilities from OSV API with Redis caching."""
    cache_key = f"vuln:{package}:{version}"

    # async method to retrieve redis cache
    try:
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            logger.info(f"Redis cache hit for {cache_key}")
            return json.loads(cached_data)
    except aioredis.RedisError as e:
        logger.error(f"Redis error: {str(e)}")
        # Continue without cache if Redis fails

    async with aiohttp.ClientSession() as session:
        try:
            url = OSV_SERVICE_URL
            payload = {
                "version": version,
                "package": {"name": package, "ecosystem": ECO_SYSTEM},
            }
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    vulns = data.get("vulns", [])
                    # update redis cache here
                    # no need to set expiry value, a vulnerability associated with a
                    # library of a particular version never changes
                    await redis_client.set(cache_key, json.dumps(vulns))
                    return vulns
                return []
        except Exception as e:
            logger.error(
                f"Error fetching vulnerabilities for {package}:{version}: {str(e)}"
            )
            # if not all vulnerabilities are fetched and fail the job and don't write to the database
            # we can leave cache as it is, since existing packages that were sucessfully retrieved have valid vulnerabilities list
            raise Exception(e)
