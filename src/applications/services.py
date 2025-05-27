import json
from datetime import datetime
from typing import Dict, List, Optional

import aiohttp
import redis.asyncio as aioredis
from fastapi import HTTPException, status
from redis.asyncio import Redis
from sqlalchemy.orm import Session

from src.applications.utils import parse_requirements
from src.db.models import Application, Dependency
from src.logging_utils import logger
from src.redis_utils import get_cache_ttl, set_cache_ttl
from src.applications.schemas import ApplicationResponse

OSV_SERVICE_URL: str = "https://api.osv.dev/v1/query"
ECO_SYSTEM = "PyPI"


class ApplicationService:
    def __init__(self):
        self.app_cache_key = "app_name:{}"

    async def _fetch_vulnerabilities(
        self, package: str, version: str, redis_client: Redis
    ) -> List[Dict]:
        """
        Fetch vulnerabilities from OSV API with Redis caching.
        """
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
                # if not all vulnerabilities are fetched then fail the job
                # we can leave cache as it is, since existing packages that were sucessfully retrieved have valid vulnerabilities list
                raise Exception(e)

    async def create_application(
        self,
        name: str,
        description: Optional[str],
        file_content: str,
        db_session: Session,
        redis_client: Redis,
    ) -> ApplicationResponse:
        """
        Create a new application with dependencies and check for vulnerabilities.
        - Parses dependencies from `file_content` using `parse_requirements`.
        - Fetches vulnerabilities for each dependency using `_fetch_vulnerabilities` with Redis.
        - Stores dependencies in the database, linking them to the new application.
        - Sets `is_vulnerable` on the application based on detected vulnerabilities.
        - Commits changes to the database or rolls back on error.

        Args:
            self: The instance of the class containing this method.
            name (str): The name of the application.
            description (Optional[str]): An optional description of the application.
            file_content (str): The content of a requirements.txt file containing dependencies.
            db_session (Session): The database session for SQLAlchemy operations.
            redis_client (redis.Redis): The Redis client.

        Returns:
            Application: The created application object with associated dependencies.

        Raises:
            HTTPException:
            - 422 (Unprocessable Entity) if an application with the given name already exists.
            - 400 (Bad Request) if the requirements.txt file is invalid (e.g., Unicode decode error).
            - 500 (Internal Server Error) if an error occurs during database or vulnerability processing.
        """
        try:
            if not (
                db_session.query(Application).filter(Application.name == name).first()
                is None
            ):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="App already exists",
                )
            deps = parse_requirements(file_content)
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid requirements.txt file",
            )

        vulnerabilities = []
        # first create application
        new_app = Application(
            name=name,
            description=description,
            is_vulnerable=False,
            created_at=datetime.now(),
        )
        try:
            for dep in deps:
                vulns = await self._fetch_vulnerabilities(
                    dep["name"], dep["version"], redis_client
                )
                if vulns:
                    vulnerabilities.extend(vulns)

                dep_id = f"{dep['name']}:{dep['version']}"
                # Check if dependency exists
                existing_dep = (
                    db_session.query(Dependency).filter(Dependency.id == dep_id).first()
                )
                if not existing_dep:
                    new_dep = Dependency(
                        id=dep_id,
                        name=dep["name"],
                        version=dep["version"],
                        vulnerabilities=json.dumps(vulns),
                    )
                    new_dep.applications.append(new_app)
                    db_session.add(new_dep)
                else:
                    existing_dep.applications.append(new_app)
            # update vulnerability status, now that all the dependencies have been added.
            new_app.is_vulnerable = len(vulnerabilities) > 0
            db_session.add(new_app)
            db_session.commit()
            db_session.refresh(new_app)

            app_response = ApplicationResponse(
                name=new_app.name,
                description=new_app.description,
                is_vulnerable=new_app.is_vulnerable,
                created_at=new_app.created_at,
            )
            cache_key = self.app_cache_key.format(new_app.name)
            set_cache_ttl(
                cache_key, json.dumps(app_response.model_dump_json()), redis_client, 30
            )
            return app_response
        except Exception as e:
            db_session.rollback()
            logger.error(f"Error creating application: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create application",
            )

    async def delete_application(
        self, app_name: str, db_session: Session, redis_client: Redis
    ):
        cache_key = self.app_cache_key.format(app_name)
        app = db_session.query(Application).filter(Application.name == app_name).first()
        if not app:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
            )
        try:
            db_session.delete(app)
            db_session.commit()
            await redis_client.delete(cache_key)
            return {}
        except Exception as e:
            db_session.rollback()
            logger.error(f"Error deleting application: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to delete application")

    async def get_application(
        self, app_name: str, db_session: Session, redis_client: Redis
    ) -> ApplicationResponse:
        cache_key = self.app_cache_key.format(app_name)

        try:
            cached_data = await get_cache_ttl(cache_key, redis_client, 30)
            if cached_data:
                logger.info(f"Redis cache hit for {cache_key}")
                return ApplicationResponse(**json.loads(cached_data))
        except aioredis.RedisError as e:
            logger.error(f"Redis error: {str(e)}")
            # Continue without cache if Redis fails

        app: Application = (
            db_session.query(Application).filter(Application.name == app_name).first()
        )
        if not app:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
            )
        else:
            app_response = ApplicationResponse(
                name=app.name,
                description=app.description,
                is_vulnerable=app.is_vulnerable,
                created_at=app.created_at,
            )
            set_cache_ttl(
                cache_key, json.dumps(app_response.model_dump_json()), redis_client, 30
            )

            return app_response


appl_service = ApplicationService()


def get_application_service():
    try:
        yield appl_service
    finally:
        pass
