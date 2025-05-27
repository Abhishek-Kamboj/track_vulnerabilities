from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator


class ApplicationCreate(BaseModel):
    name: str
    description: Optional[str] = None

    @field_validator('name')
    def check_trimmed_length(cls, v: str) -> str:
        if len(v.strip()) == 0:
            raise ValueError('Name cannot be empty')
        return v.strip()

class ApplicationResponse(BaseModel):
    name: str
    description: Optional[str]
    is_vulnerable: bool
    created_at: datetime