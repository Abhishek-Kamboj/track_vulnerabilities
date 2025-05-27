from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ApplicationCreate(BaseModel):
    name: str
    description: Optional[str] = None


class ApplicationResponse(BaseModel):
    name: str
    description: Optional[str]
    is_vulnerable: bool
    created_at: datetime
