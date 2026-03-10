from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.core.settings import settings
from app.db import DatabaseManager
from app.services import RedisService


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_service = RedisService()
    db_session = DatabaseManager(url=settings.db.url, echo=settings.DEBUG)

    app.state.redis = redis_service
    app.state.db = db_session

    try:
        async for session in db_session.get_session():
            await session.execute(text("SELECT 1"))
    except Exception as e:
        raise RuntimeError(f"Database connection failed: {e}")

    try:
        await redis_service.get_redis_client()
    except Exception as e:
        raise RuntimeError(f"Redis connection failed: {e}")

    yield

    await redis_service.close()
    await db_session.close()
