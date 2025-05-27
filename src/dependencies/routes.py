from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.db.main import get_db
from src.dependencies.schemas import DependencyResponse
from src.dependencies.services import DependencyService, get_dependency_service

dependency_router = APIRouter()


@dependency_router.get("/{app_name}", response_model=List[DependencyResponse])
async def get_application_dependencies(
    app_name: str,
    db_session: Session = Depends(get_db),
    dep_service: DependencyService = Depends(get_dependency_service),
):
    """
    Get dependencies for a specific application.
    """
    app_name = app_name.strip()
    if not app_name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="app_name is required",
        )

    return await dep_service.get_application_dependencies(app_name, db_session)


@dependency_router.get("/", response_model=DependencyResponse)
async def get_dependency(
    dep_id: str,
    db_session: Session = Depends(get_db),
    dep_service: DependencyService = Depends(get_dependency_service),
):
    """
    Get details for a specific dependency.
    """
    dep_id = dep_id.strip()
    if not dep_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="dep_id is required",
        )

    return await dep_service.get_dependency(dep_id, db_session)
