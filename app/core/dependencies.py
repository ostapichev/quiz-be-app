from typing import AsyncGenerator, Annotated

from fastapi import Request, Depends, Form
from fastapi.security import OAuth2PasswordBearer
from pydantic import EmailStr

from ..db import UnitOfWork, async_session_factory
from ..enums import GenderEnum
from ..schemas import NewUserRequest, UserDetailsResponse
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


def get_image_service(
    uow: UnitOfWork = Depends(get_uow),
) -> ImageService:
    return ImageService(uow)


def get_user_service(
    uow: UnitOfWork = Depends(get_uow),
    image_service: ImageService = Depends(get_image_service),
    security: PasswordHasher = Depends(get_security),
) -> UserService:
    return UserService(uow, image_service, security)


def get_auth_service(
    uow: UnitOfWork = Depends(get_uow),
    user_service: UserService = Depends(get_user_service),
    image_service: ImageService = Depends(get_image_service),
    security: PasswordHasher = Depends(get_security),
) -> AuthService:
    return AuthService(uow, user_service, image_service, security)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    service: AuthService = Depends(get_auth_service),
) -> UserDetailsResponse:
    return await service.get_current_user(token)


def get_new_user_request(
    email: EmailStr = Form(...),
    password: str = Form(...),
    name: str = Form(...),
    surname: str = Form(...),
    phone: str | None = Form(None),
    gender: GenderEnum | None = Form(None),
) -> NewUserRequest:
    return NewUserRequest.from_form(
        email=email,
        password=password,
        name=name,
        surname=surname,
        phone=phone,
        gender=gender,
    )
