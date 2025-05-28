from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.db.main import get_db
from src.users.schemas import UserCreate, UserResponse
from src.db.models import User, Application
from datetime import datetime
from src.logging_utils import logger
from src.app_constants import DEFAULT_USER_ID
from src.users.services import get_user_service, UserService

user_router = APIRouter()


@user_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse,
)
async def create_user(
    user: UserCreate,
    db_session: Session = Depends(get_db),
    user_service: UserService = Depends(get_user_service),
):
    """
    Create a new user.
    """
    user_id = user.id.strip()
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="User ID is required",
        )
    return await user_service.create_user(user_id, db_session)


@user_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    db_session: Session = Depends(get_db),
    user_service: UserService = Depends(get_user_service),
):
    """Delete a user and reassign their applications to the default user."""
    user_id = user_id.strip()
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="User ID is required",
        )
    return await user_service.delete_user(user_id, db_session)
