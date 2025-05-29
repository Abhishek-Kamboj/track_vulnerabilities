import json
from typing import List, Set

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.db.models import Application, Dependency, User
from src.dependencies.schemas import DependencyResponse
from src.logging_utils import logger


class DependencyService:
    async def get_application_dependencies(
        self, app_name: str, db_session: Session
    ) -> List[DependencyResponse]:
        """
        Get the dependencies of a specified application.

        Args:
            app_name (str): The name of the application whose dependencies are being fetched.
            db_session (Session): The database session.

        Returns: List[DependencyResponse]

        Raises:
            HTTPException:
                - 404 if the specified application is not found in the database
        """
        app = db_session.query(Application).filter(Application.name == app_name).first()
        if not app:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application {app_name} not found",
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

    async def get_dependency(
        self, dep_id: str, db_session: Session
    ) -> DependencyResponse:
        """
        Get details of a specific dependency by its ID.

        Args:
            dep_id (str): The unique identifier of the dependency to retrieve.
            db_session (Session): The database session used for querying the dependency.

        Returns: DependencyResponse

        Raises:
            HTTPException:
                - 404 if the dependency is not found.
        """
        dep = db_session.query(Dependency).filter(Dependency.id == dep_id).first()
        if not dep:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dependency {dep_id} not found",
            )

        return DependencyResponse(
            id=dep.id,
            name=dep.name,
            version=dep.version,
            applications=[app.name for app in dep.applications],
            vulnerabilities=json.loads(dep.vulnerabilities),
        )

    async def get_dependency_by_user(
        self, user_id: str, db_session: Session
    ) -> List[DependencyResponse]:
        """
        Get all unique dependencies associated with a given user.

        Args:
            user_id (str): The unique identifier of the user whose dependencies are to be retrieved.
            db_session (Session): The database session used for querying user and dependency information.

        Returns:  List[DependencyResponse]

        Raises:
            HTTPException:
                - 404 if the user is not found in the database.
        """
        user: User = db_session.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found",
            )

        # Collect unique dependencies across all applications
        unique_dependencies: Set[Dependency] = set()
        for app in user.applications:  # lazy-loaded
            for dep in app.dependencies:  # lazy-loaded
                unique_dependencies.add(dep)

        return [
            DependencyResponse(
                id=dep.id,
                name=dep.name,
                version=dep.version,
                applications=[app.name for app in dep.applications],  # lazy-loaded
                vulnerabilities=json.loads(dep.vulnerabilities),
            )
            for dep in unique_dependencies
        ]


dep_service = DependencyService()


def get_dependency_service():
    try:
        yield dep_service
    finally:
        pass
