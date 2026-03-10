import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.core.settings import settings
from app.db import DatabaseManager
from app.services import RedisService

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting app...")

    redis_service = RedisService()
    db_session = DatabaseManager(url=settings.db.url, echo=settings.DEBUG)

    app.state.redis = redis_service
    app.state.db = db_session

    try:
        logger.info("Checking database connection...")
        async for session in db_session.get_session():
            await session.execute(text("SELECT 1"))
        logger.info("Database connection successful")
    except Exception as e:
        error_message = f"Database connection failed: {e}"
        logger.exception(error_message)
        raise RuntimeError(error_message)

    try:
        logger.info("Checking redis connection...")
        await redis_service.get_redis_client()
        logger.info("Redis connection successful")
    except Exception as e:
        error_message = f"Redis connection failed: {e}"
        logger.exception(error_message)
        raise RuntimeError(error_message)

    yield

    logger.info("Shutting down application...")

    await redis_service.close()
    await db_session.close()

    logger.info("Database disconnected!")
    logger.info("Shutting down app!")
