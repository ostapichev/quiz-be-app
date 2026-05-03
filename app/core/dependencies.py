from typing import AsyncGenerator

from fastapi import Request, Depends

from app.db import UnitOfWork, async_session_factory
from app.services import RedisService, UserService


async def get_redis_service(request: Request) -> RedisService:
    return await request.app.state.redis


async def get_uow() -> AsyncGenerator[UnitOfWork, None]:
    async with async_session_factory() as session:
        async with UnitOfWork(session) as uow:
            yield uow


def get_user_service(uow: UnitOfWork = Depends(get_uow)) -> UserService:
    return UserService(uow)
