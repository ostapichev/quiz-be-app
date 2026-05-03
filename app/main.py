from fastapi import FastAPI

from starlette.middleware.cors import CORSMiddleware

from app.core.logging_config import LoggingConfig
from app.core.settings import settings
from app.core.lifespan import lifespan
from app.exceptions import register_exception_handler
from app.routers import user_router

LoggingConfig.setup()

app = FastAPI(
    title="QUIZ api",
    version="0.2.0",
    docs_url="/docs",
    lifespan=lifespan,
)
origins = [settings.CLIENT_HOST]
register_exception_handler(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(user_router, prefix="/api")
