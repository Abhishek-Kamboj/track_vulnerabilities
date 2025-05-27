import json
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.db.models import Application, Dependency
from src.dependencies.schemas import DependencyResponse
from src.logging_utils import logger


class DependencyService:
    async def get_application_dependencies(
        self, app_name: str, db_session: Session
    ) -> List[DependencyResponse]:
        try:
            app = (
                db_session.query(Application)
                .filter(Application.name == app_name)
                .first()
            )
            if not app:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Application not found",
                )

            return [
                DependencyResponse(
                    id=dep.id,
                    name=dep.name,
                    version=dep.version,
                    applications=[app.name for app in dep.applications],
                    vulnerabilities=json.loads(dep.vulnerabilities),
                )
                for dep in app.dependencies
            ]
        except Exception as e:
            logger.error(f"Error retrieving application dependencies: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve dependencies",
            )

    async def get_dependency(self, dep_id: str, db_session: Session) -> DependencyResponse:
        """
        Get details for a specific dependency.
        """
        try:
            dep = db_session.query(Dependency).filter(Dependency.id == dep_id).first()
            if not dep:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Dependency not found"
                )
            return DependencyResponse(
                id=dep.id,
                name=dep.name,
                version=dep.version,
                applications=[app.name for app in dep.applications],
                vulnerabilities=json.loads(dep.vulnerabilities),
            )
        except Exception as e:
            logger.error(f"Error retrieving dependency {dep_id} : {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve dependency",
            )


dep_service = DependencyService()


def get_dependency_service():
    try:
        yield dep_service
    finally:
        pass
