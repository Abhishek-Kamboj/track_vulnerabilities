# Python Application Vulnerability Tracker Documentation
[[_TOC_]]
## Overview
The Python Application Vulnerability Tracker is a FastAPI-based web application designed to manage and track Python applications, their dependencies, and associated security vulnerabilities. It enables users to upload application requirements (requirements.txt), analyze dependencies for known vulnerabilities, and associate applications with users in a one-to-many relationship. The application uses SQLite as its database and Redis for caching vulnerability data to enhance performance.

## Key Features

 - Application Management: Create, retrieve, and delete applications with associated dependencies.

 - Dependency Vulnerability Tracking: Parse requirements.txt files, fetch vulnerabilities for dependencies, and store them in the database.

 - User Management: Manage users with a one-to-many relationship to applications, ensuring applications are reassigned to a default user (default@example.com) upon user deletion.

 - Lazy Loading: Use SQLAlchemy’s lazy=`select` strategy for relationships (e.g., Application.dependencies) to optimize database queries.

 - Caching: Utilize Redis to cache vulnerability data, which is retrieved from `https://api.osv.dev/v1/query` reducing external API calls.


- Error Handling: Robust exception handling with db session rollbacks and logging.

## Architecture
 - Framework: FastAPI

 - Database: SQLite (vulnerability_tracker.db)

 - ORM: SQLAlchemy

 - Caching: Redis

 - Logging: Python logging module for debugging and monitoring

 - Deploymen: Gunicorn with uvicorn for running multiple processes of uvicorn to leverage multicores or modern architecture.

## Caching Strategy




