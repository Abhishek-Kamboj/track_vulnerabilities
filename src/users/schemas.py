from typing import Dict, List
from datetime import datetime
from pydantic import BaseModel

class UserCreate(BaseModel):
    id: str  # e.g., email or username

class UserResponse(BaseModel):
    id: str
    created_at: datetime
    applications: List[str]

