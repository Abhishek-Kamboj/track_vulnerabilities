from typing import List

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Table, Text
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.sql import func

from src.db.main import Base

app_dependencies = Table(
    "app_dependencies",
    Base.metadata,
    Column(
        "app_name",
        String,
        ForeignKey("applications.name", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column("dep_id", String, ForeignKey("dependencies.id"), primary_key=True),
)


class Application(Base):
    __tablename__ = "applications"
    name = Column(String, primary_key=True)
    description = Column(Text, nullable=True)
    is_vulnerable = Column(Boolean, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    user_id = Column(String, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="applications")
    dependencies: Mapped[List["Dependency"]] = relationship(
        "Dependency", secondary=app_dependencies, back_populates="applications"
    )


class Dependency(Base):
    __tablename__ = "dependencies"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    version = Column(String, nullable=False)
    vulnerabilities = Column(Text, nullable=False)
    applications: Mapped[List["Application"]] = relationship(
        "Application", secondary=app_dependencies, back_populates="dependencies"
    )


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)  # Unique identifier (e.g., email or username)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    applications: Mapped[List["Application"]] = relationship(
        "Application", back_populates="user"
    )
