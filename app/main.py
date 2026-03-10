from fastapi import FastAPI

from app.routers import response_router

app = FastAPI(title="QUIZ backend app", version="0.0.1", docs_url="/docs")
app.include_router(response_router, prefix="/api")
