from datetime import datetime

from src.app_constants import DEFAULT_USER_ID
from src.db.main import Base, engine, session
from src.db.models import User
from src.logging_utils import logger


def create_default_user():
    """
    Ensure a default user exists on startup.
    """
    db_session = session()
    try:
        existing_user = (
            db_session.query(User).filter(User.id == DEFAULT_USER_ID).first()
        )
        if not existing_user:
            default_user = User(id=DEFAULT_USER_ID, created_at=datetime.now())
            db_session.add(default_user)
            db_session.commit()
            logger.info("Default user created.")
    except Exception as e:
        db_session.rollback()
        logger.error(f"Error creating default user: {str(e)}")
        raise Exception("Cannot create Default user")
    finally:
        db_session.close()



def create_db():
    """
    Initialize database
    """
    Base.metadata.create_all(bind=engine)
    create_default_user()
