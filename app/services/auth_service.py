import logging
from datetime import timedelta, datetime, timezone

from fastapi.security import OAuth2PasswordRequestForm
from jwt import InvalidTokenError, decode, encode

from ..core.security import PasswordHasher
from ..core.settings import settings
from ..db import UnitOfWork
from ..exceptions import CredentialsException, UnauthorizedException
from ..schemas import (
    UserSignInRequest,
    UserDetailsResponse,
    Token,
    TokenData,
)

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, uow: UnitOfWork, security: PasswordHasher) -> None:
        self.uow = uow
        self.security = security

    async def get_token(self, form_data: OAuth2PasswordRequestForm) -> Token:
        login_data = UserSignInRequest(
            username=form_data.username,
            password=form_data.password,
        )
        auth_user = await self._authenticate_user(login_data)
        if not auth_user:
            raise UnauthorizedException
        access_token_expires = timedelta(
            minutes=settings.auth.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        access_token = self._create_access_token(
            data={"sub": login_data.username},
            expires_delta=access_token_expires,
        )

        logger.info(f"{form_data.username} get access token")

        return Token(token_type="bearer", access_token=access_token)

    async def _authenticate_user(self, login_data: UserSignInRequest) -> bool:
        user = await self.uow.user_repository.get_user_by_email(login_data.username)

        if not user or not user.is_active:
            self.security.verify_password(
                login_data.password,
                self.security.get_password_hash(settings.auth.DUMMY_PASSWORD),
            )
            return False

        if not self.security.verify_password(
            login_data.password,
            user.hashed_password,
        ):
            return False

        return True

    async def get_current_user(self, token: str) -> UserDetailsResponse:
        credentials_exception = CredentialsException

        try:
            payload = decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.auth.ALGORITHM],
            )
            email = payload.get("sub")

            if email is None:
                raise credentials_exception

            token_data = TokenData(email=email)
        except InvalidTokenError:
            raise credentials_exception

        user = await self.uow.user_repository.get_user_by_email(token_data.email)

        if not user:
            raise credentials_exception

        logger.info(f"Current user: {token_data.email.__str__()} retrieved!")

        return user

    @staticmethod
    def _create_access_token(
        data: dict,
        expires_delta: timedelta | None = None,
    ) -> str:
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=settings.auth.ACCESS_TOKEN_EXPIRE_MINUTES
            )

        to_encode.update({"exp": expire})

        encoded_jwt = encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.auth.ALGORITHM,
        )

        return encoded_jwt
