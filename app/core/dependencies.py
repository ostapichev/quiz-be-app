from typing import AsyncGenerator, Annotated

from fastapi import Request, Depends
from fastapi.security import OAuth2PasswordBearer

from ..db import UnitOfWork, async_session_factory
from ..schemas import UserDetailsResponse
from ..services import RedisService, UserService, AuthService, ImageService
from .security import PasswordHasher

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_redis_service(request: Request) -> RedisService:
    return await request.app.state.redis


async def get_uow() -> AsyncGenerator[UnitOfWork, None]:
    async with async_session_factory() as session:
        async with UnitOfWork(session) as uow:
            yield uow


def get_security() -> PasswordHasher:
    return PasswordHasher()


def get_auth_service(
    uow: UnitOfWork = Depends(get_uow),
    security: PasswordHasher = Depends(get_security),
) -> AuthService:
    return AuthService(uow, security)


def get_user_service(
    uow: UnitOfWork = Depends(get_uow),
    security: PasswordHasher = Depends(get_security),
) -> UserService:
    return UserService(uow, security)


def get_image_service(
    uow: UnitOfWork = Depends(get_uow),
) -> ImageService:
    return ImageService(uow)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    service: AuthService = Depends(get_auth_service),
) -> UserDetailsResponse:
    return await service.get_current_user(token)
