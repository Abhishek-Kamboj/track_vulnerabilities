from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from src.logging_utils import logger
from src.redis_utils import aioredis, redis_client, redis_pool
from src.applications.routes import application_router
from src.dependencies.routes import dependency_router
from src.db.main import create_db


version = "v1"

description = """
A REST API  for Python Application Vulnerability Tracking.

This REST API is able to;
- Create applications and its dependencies
- Update application dependencies
- get all depenencies and vulnerabilities of an application
- get all applications associated with a dependency and its vulnerabilities
"""

version_prefix = f"/api/{version}"

create_db()
logger.info("sqllite db tables created")

@asynccontextmanager
async def lifespan(_):
    """
    Fast API lifespan callback to handle redis connection.

    Raises:
        RuntimeError: in event redis connection cannot be established.
    """
    try:
        await redis_client.ping()
        logger.info("Connected to Redis successfully")
        logger.info(f"Swagger docs available at: {version_prefix}/docs")
    except aioredis.RedisError as e:
        logger.error(f"Failed to connect to Redis: {str(e)}")
        raise RuntimeError("Redis connection failed")
    try:
        yield
    finally:
        await redis_client.close()
        await redis_pool.disconnect()
        logger.info("Redis connection pool closed")


app = FastAPI(
    title="Python Application Vulnerability Tracker",
    description=description,
    version=version,
    license_info={
        "name": "AGPL-3.0",
        "url": "https://www.gnu.org/licenses/agpl-3.0.en.html",
    },
    contact={
        "name": "Abhishek Kamboj",
        "url": "https://github.com/Abhishek-Kamboj",
        "email": "abhishekkam@gmail.com",
    },
    lifespan=lifespan,
    openapi_url=f"{version_prefix}/openapi.json",
    docs_url=f"{version_prefix}/docs",
    redoc_url=f"{version_prefix}/redoc",
)

app.include_router(
    application_router, prefix=f"{version_prefix}/applications", tags=["applications"]
)
app.include_router(
    dependency_router, prefix=f"{version_prefix}/dependencies", tags=["dependencies"]
)

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unexpected error: {str(exc)}")
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": "Internal server error"})
