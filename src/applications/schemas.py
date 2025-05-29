from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator


class ApplicationCreate(BaseModel):
    name: str
    user_id: str
    description: Optional[str] = None

    @field_validator("name")
    def check_trimmed_length(cls, v: str) -> str:
        if len(v.strip()) == 0:
            raise ValueError("Name cannot be empty")
        return v.strip()

    @field_validator("user_id")
    def user_id_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("user_id cannot be empty")
        return v.strip()


class ApplicationsGet(BaseModel):
    user_id: str

    @field_validator("user_id")
    def user_id_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("user_id cannot be empty")
        return v.strip()


class ApplicationGet(BaseModel):
    name: str

    @field_validator("name")
    def check_trimmed_length(cls, v: str) -> str:
        if len(v.strip()) == 0:
            raise ValueError("Name cannot be empty")
        return v.strip()


class ApplicationResponse(BaseModel):
    name: str
    description: Optional[str]
    is_vulnerable: bool
    created_at: datetime
    user_id: str
