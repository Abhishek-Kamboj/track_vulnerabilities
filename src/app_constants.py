API_VERSION: str = "v1"

DATABASE_URL = "sqlite:///vulnerability_tracker.db"
DEFAULT_USER_ID: str = "default@user.com"

OSV_SERVICE_URL: str = "https://api.osv.dev/v1/query"
ECO_SYSTEM: str = "PyPI"

MAX_FILE_SIZE_BYTES: int = 500 * 1024  # 500 * 1024 bytes , 500KB

CACHE_TTL_SECONDS: int = 30
REDIS_HOST: str="localhost"
REDIS_PORT: int=6379
REDIS_MAX_CONNECTIONS: int=5
REDIS_SOCKET_CONNECTION_TIMEOUT: int =15  # Wait up to 15 seconds for connection