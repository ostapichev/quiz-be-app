import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import select

from ..db import get_session, session_close
from ..services import RedisService

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting app...")

    redis_service = RedisService()
    app.state.redis = await redis_service.get_redis_client()

    try:
        logger.info("Checking database connection...")
        async for session in get_session():
            await session.execute(select(1))
        logger.info("Database connection successful")
    except Exception as err:
        logger.exception(f"Database connection failed: {err}")
        raise

    try:
        logger.info("Checking redis connection...")
        await redis_service.get_redis_client()
        logger.info("Redis connection successful")
    except Exception as err:
        logger.exception(f"Redis connection failed: {err}")
        raise

    yield

    logger.info("Shutting down application...")

    await redis_service.close()
    logger.info("Redis disconnected!")

    await session_close()
    logger.info("Database disconnected!")
