from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

# SQLAlchemy setup
DATABASE_URL = "sqlite:///vulnerability_tracker.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Initialize databas
def create_db():
    Base.metadata.create_all(bind=engine)

# Helper functions
def get_db() -> Session:
    """
    Provide a database session.
    """
    db_session = session()
    try:
        yield db_session
    finally:
        db_session.close()
