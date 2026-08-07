from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from .core.lifespan import lifespan
from .core.logging_config import LoggingConfig
from .core.settings import settings
from .exceptions import register_exception_handler
from .routers import user_router, auth_router

LoggingConfig.setup()

app = FastAPI(
    title="QUIZ api",
    version="0.6.0",
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
app.include_router(auth_router, prefix="/api")
