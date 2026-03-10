# QUIZ Backend API

A backend application for the Quiz system built with **FastAPI**.

The project provides a REST API for managing quizzes and questions.

The current version includes basic endpoints, tests, environment configuration, and automated code formatting.

## Technology stack
- Python 3.12
- FastAPI
- Uvicorn
- Docker
- Pydantic
- Pytest
- Pipenv
- Pre-commit
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
5. Start the server:
```bash
pipenv run uvicorn app.main:app --reload
```
6. Access the API at: http://127.0.0.1:8000
---

## API Documentation
1. Swagger UI available at: http://127.0.0.1:8000/docs
2. Alternative automatic documentation: http://127.0.0.1:8000/redoc
2. OpenAPI schema: http://127.0.0.1:8000/openapi.json
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
docker run --rm --env-file .env quiz-api pipenv run pytest
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
