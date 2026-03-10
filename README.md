# QUIZ Backend API

A backend application for the Quiz system built with **FastAPI**.

The project provides a REST API for managing quizzes and questions.

The current version includes basic endpoints, tests, environment configuration, and automated code formatting.

## Technology stack
- Python 3.12
- FastAPI
- Uvicorn
- Docker
- Docker Compose
- Pipenv
- PostgreSQL
- Pre-commit
- Pydantic
- Pytest
- Redis
- SQL Alchemy
---

## Installation and launch
1. Clone the repository and navigate into it:
```bash
git clone https://github.com/ostapichev/quiz-be-app
```
```bash
cd quiz-be-app
```
2. Install dependencies:
```bash
pipenv install
```
3. Create <code>.env</code> file using <code>.env.sample</code>:
```bash
cp .env.sample .env
```
4. Activate the virtual environment:
```bash
pipenv shell
```
---

## Testing
To run tests:
```bash
pipenv run pytest
```
---

## Docker Workflow
1. Check Docker installation:
```bash
docker --version
```
2. Build the image:
```bash
docker build -t quiz-api .
```
or to run with Docker Compose (Recommended):

```bash
docker compose up --build
```
3. Verify image:
```bash
docker images
```
4. Run container::
```bash
docker run -p 88:80 --env-file .env quiz-api
```
5. Access application:
   - the API will be available at: http://localhost:88
   - swagger documentation: http://localhost:88/docs
   - alternative automatic documentation: http://localhost:88/redoc
6. To view running containers:
```bash
docker ps
```
7. Check env file:
```bash
docker exec -it <container_id> env
```
8. Run tests inside Docker:
```bash
docker run --rm --env-file .env <container_name> pipenv run pytest
```
   - connect to container::
```bash
docker exec -it <container_id> bash
```
or
```bash
docker exec -it <container_id> sh
```
   - running tests:
```bash
pipenv run pytest
```
- exit
```bash
exit
```
9. To stop a running container:
```bash
docker stop <container_id>
```
10. To remove the container:
```bash
docker rm <container_id>
```
---

## Redis Cache

Redis is used for caching API responses and temporary data storage.
It runs as a separate service inside Docker.

1. Redis is used to:
   - Store cached responses
   - Improve performance
   - Reduce database load
   - Demonstrate cache integration

2. Implementation
   - The project uses an asynchronous Redis client (redis.asyncio).
   - Caching logic is implemented in RedisService.

3. Main features:
   - HSET/HGETALL/DELETE for hash storage
   - Automatic TTL expiration
   - Connection pooling
   - Pipeline usage for atomic operations

4. Cache Structure
   - Cached response example:
```bash
Key: response

Hash:
  status_code → 200
  detail      → success
  result      → created
```

5. TTL (Time To Live)
   - Cache expiration is controlled by:<code>REDIS_TTL=3600</code>
   - All cached data is automatically removed after expiration.

6. Cache Deletion
   - Cached data can be removed manually using the Redis DELETE command.
   - This is useful when: cached data becomes outdated,
      data was updated in the database
   - Cache invalidation is required
   - Manual cleanup is needed

7. Redis Service Usage Example:
```bash
await redis_service.hset(
    "response",
    status_code=200,
    detail="ok",
    result="working",
)

data = await redis_service.hgetall("response")
```

## Code review (pre-commit)
Manually launching checks:
```bash
pipenv run pre-commit run --all-files
```
---

## Contacts:
- Author - [Oleh Ostapenko](https://github.com/ostapichev)
- Mail me - ytoxos@gmail.com
- Call me - 38-(093)-721-68-19
