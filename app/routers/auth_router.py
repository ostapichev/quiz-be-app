from typing import Annotated

from fastapi import APIRouter, status, Depends, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from ..core.dependencies import get_auth_service
from ..schemas import Token, UserDetailsResponse
from ..services import AuthService

auth_router = APIRouter(tags=["Auth"], prefix="/auth")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


@auth_router.post(
    "/login",
    description="Login user",
    response_model=Token,
    status_code=status.HTTP_200_OK,
)
async def user_login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: AuthService = Depends(get_auth_service),
) -> Token:
    return await service.get_token(form_data)


@auth_router.get(
    "/login/auth0_callback",
    description="Login user with auth0",
    response_model=UserDetailsResponse,
    status_code=status.HTTP_200_OK,
)
async def user_login_auth0(
    request: Request,
    service: AuthService = Depends(get_auth_service),
) -> UserDetailsResponse:
    return await service.verify_auth0_user(request)


@auth_router.get(
    "/me",
    description="My user info",
    response_model=UserDetailsResponse,
    status_code=status.HTTP_200_OK,
)
async def user_me(
    token: Annotated[str, Depends(oauth2_scheme)],
    service: AuthService = Depends(get_auth_service),
) -> UserDetailsResponse:
    return await service.get_current_user(token)
