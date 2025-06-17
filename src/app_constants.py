import os

from src.logging_utils import logger


def convert_to_int(variable_name: str, default: int):
    try:
        return int(os.getenv(variable_name, default))
    except:
        logger.warning(
            f"Error converting value from environment variable {variable_name} to int, falling back on default{default}"
        )
        return default


# Define default constants
API_VERSION: str = os.getenv("API_VERSION", "v1")

DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///vulnerability_tracker.db")

DEFAULT_USER_ID: str = os.getenv("DEFAULT_USER_ID", "default@user.com")

OSV_SERVICE_URL: str = os.getenv("OSV_SERVICE_URL", "https://api.osv.dev/v1/query")
ECO_SYSTEM: str = os.getenv("ECO_SYSTEM", "PyPI")

MAX_FILE_SIZE_BYTES: int = convert_to_int("MAX_FILE_SIZE_BYTES", 500 * 1024)  # 500KB

CACHE_TTL_SECONDS: int = convert_to_int("CACHE_TTL_SECONDS", 30)
REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT: int = convert_to_int("REDIS_PORT", 6379)
REDIS_MAX_CONNECTIONS:int =  convert_to_int("REDIS_MAX_CONNECTIONS", 5)
REDIS_SOCKET_CONNECTION_TIMEOUT: int = convert_to_int(
    "REDIS_SOCKET_CONNECTION_TIMEOUT", 15
)
