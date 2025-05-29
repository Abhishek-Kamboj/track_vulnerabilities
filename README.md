# Python Application Vulnerability Tracker Documentation

## Overview
The Python Application Vulnerability Tracker is a FastAPI-based web application designed to manage and track Python applications, their dependencies, and associated security vulnerabilities. It enables users to upload application requirements (requirements.txt), analyze dependencies for known vulnerabilities, and associate applications with users in a one-to-many relationship. The application uses SQLite as its database and Redis for caching vulnerability data to enhance performance.

## Key Features

 - Application Management: Create, retrieve, and delete applications with associated dependencies.

 - Dependency Vulnerability Tracking: Parse requirements.txt files, fetch vulnerabilities for dependencies, and store them in the database.

 - User Management: Manage users with a one-to-many relationship to applications, ensuring applications are reassigned to a default user `default@example.com` when user assoctated with the aplication is deleted using delete use api end point.

 - Lazy Loading: Use SQLAlchemy’s lazy=`select` strategy for relationships (e.g., Application.dependencies) to optimize database queries.

 - Caching: Utilize Redis to cache vulnerability data, which is retrieved from `https://api.osv.dev/v1/query` reducing external API calls.


- Error Handling: Robust exception handling with db session rollbacks and logging.
- Error Handling: input request payload is verified using pydantic and manual verification in certain cases.
- Robust handling fo data integrity  by handling cases such as fail creation fo app if similar app exists already and other similar cases.

## Architecture
 - Framework: FastAPI

 - Database: SQLite (vulnerability_tracker.db)

 - ORM: SQLAlchemy

 - Caching: Redis

 - Logging: Python logging module for debugging and monitoring

 - Deploymen: Gunicorn with uvicorn for running multiple processes of uvicorn to leverage multicores or modern architecture.

## Caching Strategy

The application uses Redis to cache vulnerability data for dependencies, minimizing external API calls (e.g., to PyPI or a mock vulnerability API).

- calls to `.osv.dev` are cached permanently. This is because for a given PyPI package and a given version, vulnerabilities are unlikely to change.( This is, ofcourse an assumption and strategy can change based on requirements.)
- calls to create application are cached till 30 seconds. However if it is accessed within 30 seconds then cache TTL is extended for another thiry seconds , a custom function is written in `redis_utils.py` file for it. This is to demonstrate cache strategy of keeting the cache alive if accessed often. if application is deleted then it is removed from cache. Hence life cycle of cache of the response is managed with lifecycle of the application.
- for all cache implementation, a fall back is always provided for fetching data eith from db or from external source in case of cache miss.

### Redis connection
- Initialized on startup: redis_client = redis.Redis(...)

- Closed on shutdown: await redis_client.close()

### Benefits
- since we are using external cache, the app is scalable and hence in deployment we use gunicorn for scaling the app.

### Considerations
- Caching can be more granular per api end point. we can implement api end points to fetch data from db / api and refresh cache with a flag. fro this demo app, this is kept as a future enhancement.

## Requirement.txt file
Currently only simple requirement.txt files are supported that is files with requirements as shown below:

```text
aiohttp==3.12.0
fastapi==0.115.12
gunicorn==23.0.0
python-multipart==0.0.20
redis==6.1.0
SQLAlchemy==2.0.41
uvicorn==0.34.2
```

if requiremet.txt file has requirements such as below:
```
aiohttp=<3.11.0
fastapi>=0.114.0,<0.115
```
 then api will return http 400 error with ' response with `Cannot parse requirements.txt file` as detail response. This is an assumption made to keep demo app development time under limit.

## Deployment
Docker is needed for running the app. Install docker desktop on your machine if your are running windows, other wise on linux install `docker` & `docker-compose` from package manager. Check following website for detail installation instruction for your distro [docs.docker.com/engine/install](https://docs.docker.com/engine/install/).

A docker compose file is provided for quick deployment on local machine.

- To build the containers run
```sh
docker-compose build
```

- to start app run
```sh
docker-compose up -d
```
Application will be avaiable on :
```
127.0.0.1:8000/api/v1/docs
```
This is a swagger page , where api points can be tested. A documentatino of each api end-point is described in the swagger doc.
## Future Improvements
 - Implement user authentication insted of user creatino and deletion endpoint
 - Add pagination for large datasets.Espceially for api calls such as get all dependencies for a given user accross all its application.
 - Handle all kinds of requirements.txt files.
 - Enhance cache invalidation and fresh call from api with flags in api call.
 - Implement celery for long running task and have seperate api end points for running long runnig task and their statuses.













