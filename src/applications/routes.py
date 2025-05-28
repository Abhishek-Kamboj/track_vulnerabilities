from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import ValidationError
from redis.asyncio import Redis
from sqlalchemy.orm import Session

from src.app_constants import MAX_FILE_SIZE_BYTES
from src.applications.schemas import ApplicationCreate, ApplicationResponse
from src.applications.services import ApplicationService, get_application_service
from src.db.main import get_db
from src.db.models import Application
from src.logging_utils import logger
from src.redis_utils import get_redis

application_router = APIRouter()


# Application Endpoints
@application_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ApplicationResponse,
)
async def create_application(
    name: str,
    user_id: str,
    description: Optional[str] = None,
    file: UploadFile = File(...),
    db_session: Session = Depends(get_db),
    redis_client: Redis = Depends(get_redis),
    appl_service: ApplicationService = Depends(get_application_service),
):
    """
    Create a new application with requirements.txt.
    """
    # Since FastAPI doesn't handle mix of file upload and pydantic model as input
    # we create pydantic model here.
    try:
        app_create = ApplicationCreate(
            name=name, description=description, user_id=user_id
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.json(include_url=False),
        )

    # Check file size before reading
    if file.size is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to determine file size",
        )
    if file.size > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds limit of {MAX_FILE_SIZE_BYTES // 1024} KB",
        )
    try:
        content = await file.read()
        content_str = content.decode("utf-8")
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid requirements.txt file",
        )

    application = await appl_service.create_application(
        app_create.name,
        app_create.description,
        app_create.user_id,
        content_str,
        db_session,
        redis_client,
    )

    return application


@application_router.delete("/{app_name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_application(
    app_name: str,
    db_session: Session = Depends(get_db),
    redis_client: Redis = Depends(get_redis),
    appl_service: ApplicationService = Depends(get_application_service),
):
    """
    Delete an application.
    """
    app_name = app_name.strip()
    if not app_name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="app_name is required",
        )

    return await appl_service.delete_application(app_name, db_session, redis_client)


@application_router.get("/{user_id}", response_model=List[ApplicationResponse])
async def get_applications(
    user_id: str,
    db_session: Session = Depends(get_db),
    appl_service: ApplicationService = Depends(get_application_service),
):
    """
    List all applications of the user.
    """
    user_id = user_id.strip()
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="user_id is required",
        )
    try:
        return await appl_service.get_applications(user_id, db_session)
    except Exception as e:
        logger.error(f"Error retrieving applications: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve applications")


@application_router.get("/{app_name}", response_model=List[ApplicationResponse])
async def get_application(
    app_name: str,
    db_session: Session = Depends(get_db),
    appl_service: ApplicationService = Depends(get_application_service),
    redis_client: Redis = Depends(get_redis),
):
    """
    get application by name.
    """
    app_name = app_name.strip()
    if not app_name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="app_name is required",
        )
    try:
        return await appl_service.get_application(app_name, db_session, redis_client)
    except Exception as e:
        logger.error(f"Error retrieving applications: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve application")
