from fastapi import FastAPI

from starlette.middleware.cors import CORSMiddleware

from app.core.logging_config import LoggingConfig
from app.core.settings import settings
from app.core.lifespan import lifespan


LoggingConfig.setup()

app = FastAPI(
    title="QUIZ api",
    version="0.1.0",
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
