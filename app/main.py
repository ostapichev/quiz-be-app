from fastapi import FastAPI

from starlette.middleware.cors import CORSMiddleware

from app.core.settings import settings
from app.core.lifespan import lifespan
from app.routers import response_router

app = FastAPI(
    title="QUIZ api",
    version="0.0.3",
    docs_url="/docs",
    lifespan=lifespan,
)
origins = [settings.CLIENT_HOST]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(response_router, prefix="/api")
