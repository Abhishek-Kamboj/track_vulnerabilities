import json
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from src.logging_utils import logger
from src.applications.schemas import ApplicationResponse
from src.applications.services import fetch_vulnerabilities
from src.applications.utils import parse_requirements
from src.db.main import get_db
from src.db.models import Application, Dependency

application_router = APIRouter()


# Application Endpoints
@application_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ApplicationResponse,
)
async def create_application(
    name: str,
    description: Optional[str] = None,
    file: UploadFile = File(...),
    db_session: Session = Depends(get_db),
):
    """
    Create a new application with requirements.txt.
    """
    name = name.strip()
    if not name:
        raise HTTPException(status_code=422, detail="Name is required")

    try:
        if not (
            db_session.query(Application).filter(Application.name == name).first()
            is None
        ):
            raise HTTPException(status_code=422, detail="App already exists")
        content = await file.read()
        content_str = content.decode("utf-8")
        deps = parse_requirements(content_str)
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Invalid requirements.txt file")

    vulnerabilities = []
    # first  Create application
    new_app = Application(
        name=name,
        description=description,
        is_vulnerable=False,
        created_at=datetime.now(),
    )
    try:
        for dep in deps:
            vulns = await fetch_vulnerabilities(dep["name"], dep["version"])
            if vulns:
                vulnerabilities.extend(vulns)

            dep_id = f"{dep['name']}:{dep['version']}"
            # Check if dependency exists
            existing_dep = (
                db_session.query(Dependency).filter(Dependency.id == dep_id).first()
            )
            if not existing_dep:
                new_dep = Dependency(
                    id=dep_id,
                    name=dep["name"],
                    version=dep["version"],
                    vulnerabilities=json.dumps(vulns),
                )
                new_dep.applications.append(new_app)
                db_session.add(new_dep)
            else:
                existing_dep.applications.append(new_app)
        # update vulnerability status , now that all the dependencies have been added.
        new_app.is_vulnerable = len(vulnerabilities) > 0
        db_session.add(new_app)
        db_session.commit()
        db_session.refresh(new_app)
        return new_app
    except Exception as e:
        db_session.rollback()
        logger.error(f"Error creating application: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create application")


@application_router.delete(
    "/{app_name}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_application(app_name: str, db_session: Session = Depends(get_db)):
    """Delete an application and its associations with dependencies."""
    name = name.strip()
    try:
        app = db_session.query(Application).filter(Application.name == app_name).first()
        if not app:
            raise HTTPException(status_code=404, detail="Application not found")

        db_session.delete(app)
        db_session.commit()
        return {}
    except Exception as e:
        db_session.rollback()
        logger.error(f"Error deleting application: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete application")


@application_router.get("/", response_model=List[ApplicationResponse])
async def get_applications(db_session: Session = Depends(get_db)):
    """List all applications."""
    try:
        return db_session.query(Application).all()
    except Exception as e:
        logger.error(f"Error retrieving applications: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve applications")
