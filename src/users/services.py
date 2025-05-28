from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.db.models import Application, User
from src.dependencies.schemas import DependencyResponse
from src.users.schemas import UserResponse
from src.logging_utils import logger
from src.app_constants import DEFAULT_USER_ID


class UserService:
    async def create_user(
        self, user_id: str, db_session: Session
    ) -> DependencyResponse:
        """
        Creates a new user in the database.

        This function checks if the given user ID already exists in the database.
        If the user does not exist, it creates a new user entry and commits the transaction.

        Args:
            user_id (str): The unique identifier for the new user.
            db_session (Session): The database session .

        Returns: UserResponse

        Raises:
            HTTPException:
                - 422 if the user already exists.
                - 500 if there is an error during creation.
        """
        # Check if the user exists
        existing_user = db_session.query(User).filter(User.id == user_id).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"User {user_id} already exists",
            )

        try:
            new_user = User(id=user_id, created_at=datetime.now())
            db_session.add(new_user)
            db_session.commit()
            db_session.refresh(new_user)
            return UserResponse(
                id=new_user.id, created_at=new_user.created_at, applications=[]
            )
        except Exception as e:
            db_session.rollback()
            logger.error(f"Error creating user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user",
            )

    async def delete_user(self, user_id: str, db_session: Session):
        """
        Deletes a user from the database while handling special cases.

        This function checks if the user exists, ensures the default user cannot be deleted,
        and reassigns the user's applications before deletion.

        Args:
            user_id (str): The unique identifier of the user to be deleted.
            db_session (Session): The database session.

        Returns:
            dict: An empty dictionary indicating successful deletion.

        Raises:
            HTTPException:
                - 404 if the user does not exist.
                - 400 if attempting to delete the default user.
        """
        default_user_id = DEFAULT_USER_ID

        # Check if the user exists
        user = db_session.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found",
            )

        # Prevent deleting the default user
        if user_id == default_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete the default user",
            )

        # Check if the default user exists
        default_user = db_session.query(User).filter(User.id == default_user_id).first()
        if not default_user:
            raise Exception(" Default user doesnt exist in DB")

        # Reassign applications to the default user
        db_session.query(Application).filter(Application.user_id == user_id).update(
            {Application.user_id: default_user_id}
        )

        # Delete the user
        db_session.delete(user)
        db_session.commit()
        return {}


user_service = UserService()


def get_user_service():
    try:
        yield user_service
    finally:
        pass
