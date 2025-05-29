from typing import Dict, List

from pydantic import BaseModel


class DependencyResponse(BaseModel):
    id: str
    name: str
    version: str
    applications: List[str]
    vulnerabilities: List[Dict]
