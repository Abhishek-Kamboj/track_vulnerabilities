import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.logging_utils import logger
from src.db.main import get_db
from src.db.models import Application, Dependency
from src.dependencies.schemas import DependencyResponse

dependency_router = APIRouter()


@dependency_router.get(
    "/app_dependencies/{app_name}", response_model=List[DependencyResponse]
)
async def get_application_dependencies(
    app_name: str, db_session: Session = Depends(get_db)
):
    """
    Get dependencies for a specific application.
    """
    try:
        app = db_session.query(Application).filter(Application.name == app_name).first()
        if not app:
            raise HTTPException(status_code=404, detail="Application not found")

        return [
            {
                "name": dep.name,
                "version": dep.version,
                "applications": [app.name for app in dep.applications],
                "vulnerabilities": json.loads(dep.vulnerabilities),
            }
            for dep in app.dependencies
        ]
    except Exception as e:
        logger.error(f"Error retrieving application dependencies: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve dependencies")


# Dependency Endpoints
@dependency_router.get("/", response_model=List[DependencyResponse])
async def get_all_dependencies(db_session: Session = Depends(get_db)):
    """
    List all dependencies across applications.
    """
    try:
        dependencies = db_session.query(Dependency).all()
        return [
            DependencyResponse(
                id=dep.id,
                name=dep.name,
                version=dep.version,
                applications=[app.name for app in dep.applications],
                vulnerabilities=json.loads(dep.vulnerabilities),
            )
            for dep in dependencies
        ]
    except Exception as e:
        logger.error(f"Error retrieving dependencies: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve dependencies")


@dependency_router.get("/{dep_id}", response_model=DependencyResponse)
async def get_dependency(dep_id: str, db_session: Session = Depends(get_db)):
    """
    Get details for a specific dependency.
    """
    try:
        dep = db_session.query(Dependency).filter(Dependency.id == dep_id).first()
        if not dep:
            raise HTTPException(status_code=404, detail="Dependency not found")
        return DependencyResponse(
                id=dep.id,
                name=dep.name,
                version=dep.version,
                applications=[app.name for app in dep.applications],
                vulnerabilities=json.loads(dep.vulnerabilities),
            )
    except Exception as e:
        logger.error(f"Error retrieving dependency: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve dependency")
