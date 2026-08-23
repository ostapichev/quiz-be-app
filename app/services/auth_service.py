import logging
from datetime import timedelta, datetime, timezone

from fastapi import Request
from fastapi.security import OAuth2PasswordRequestForm
from jwt import (
    InvalidTokenError,
    decode,
    encode,
    ExpiredSignatureError,
    InvalidAudienceError,
    InvalidIssuerError,
    PyJWKClient,
    PyJWKClientError,
)

from ..core.security import PasswordHasher
from ..core.settings import settings
from ..db import UnitOfWork
from ..enums import AuthMethodEnum
from ..exceptions import (
    CredentialsException,
    InvalidTokenException,
    UnauthorizedException,
)
from ..schemas import (
    NewUserRequest,
    UserSignInRequest,
    UserDetailsResponse,
    Token,
    TokenData,
)
from ..services.image_service import ImageService
from ..services.user_service import UserService

logger = logging.getLogger(__name__)


class AuthService:
    AUTH0_DOMAIN = settings.auth.AUTH0_DOMAIN
    AUTH0_AUDIENCE = settings.auth.AUTH0_AUDIENCE
    AUTH0_JWKS_URL = settings.auth.jwks_url
    AUTH0_ISSUER_URL = settings.auth.issuer_url
    AUTH0_ACTIONS_NAMESPACE = settings.auth.AUTH0_ACTIONS_NAMESPACE
    AUTH0_ALGORITHMS = ["RS256"]

    JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = settings.auth.ACCESS_TOKEN_EXPIRE_MINUTES

    _credentials_exception = CredentialsException

    def __init__(
        self,
        uow: UnitOfWork,
        user_service: UserService,
        image_service: ImageService,
        security: PasswordHasher,
    ) -> None:
        self.uow = uow
        self.user_service = user_service
        self.image_service = image_service
        self.security = security
        self.jwks_client = PyJWKClient(self.AUTH0_JWKS_URL)

    async def get_token(
        self,
        form_data: OAuth2PasswordRequestForm,
    ) -> Token:
        login_data = UserSignInRequest(
            username=form_data.username,
            password=form_data.password,
        )

        auth_user = await self._authenticate_user(login_data)

        if not auth_user:
            raise UnauthorizedException

        access_token_expires = timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self._create_access_token(
            data={"sub": login_data.username},
            expires_delta=access_token_expires,
        )

        logger.info(f"{form_data.username} get access token")
        return Token(token_type="bearer", access_token=access_token)

    async def get_current_user(self, token: str) -> UserDetailsResponse:
        try:
            payload = decode(
                token,
                settings.SECRET_KEY,
                algorithms=[self.JWT_ALGORITHM],
            )
            email = payload.get("sub") or payload.get("email")

            if email is None:
                raise self._credentials_exception

            token_data = TokenData(email=email)
        except InvalidTokenError:
            raise self._credentials_exception

        user = await self.uow.user_repository.get_user_by_email(token_data.email)

        logger.info(f"Current user: {token_data.email.__str__()} retrieved!")
        return user

    async def verify_auth0_user(self, request: Request) -> UserDetailsResponse:
        namespace = self.AUTH0_ACTIONS_NAMESPACE
        payload = await self.decode_auth0_token(request)

        email = payload.get(f"{namespace}/email")
        if not email:
            raise UnauthorizedException("Email claim is missing from token")

        user = await self.uow.user_repository.get_user_by_email(email)
        if user:
            return UserDetailsResponse.model_validate(user)

        name = payload.get(f"{namespace}/given_name")
        surname = payload.get(f"{namespace}/family_name")
        picture_url = payload.get(f"{namespace}/picture")
        email_verified = payload.get(f"{namespace}/email_verified")
        user_id = payload.get(f"{namespace}/user_id")

        avatar_path = await self.image_service.create_avatar_from_url(
            user_id,
            picture_url,
        )

        new_user = NewUserRequest(
            email=email,
            name=name or surname or email.split("@")[0],
            surname=surname or "",
            auth_method=AuthMethodEnum.auth0,
        )

        logger.info(
            f"User {email.__str__()}, email verified: {email_verified.__str__()} saved"
        )
        return await self.user_service.create_user(
            user_data=new_user,
            avatar_path=avatar_path,
        )

    async def decode_auth0_token(self, request: Request) -> dict:
        token = self._get_token_from_header(request)

        try:
            signing_key = self.jwks_client.get_signing_key_from_jwt(token)
        except PyJWKClientError:
            raise UnauthorizedException

        try:
            return decode(
                token,
                signing_key.key,
                algorithms=self.AUTH0_ALGORITHMS,
                audience=self.AUTH0_AUDIENCE,
                issuer=self.AUTH0_ISSUER_URL,
            )
        except ExpiredSignatureError:
            raise InvalidTokenException(detail="Token expired")
        except InvalidAudienceError:
            raise InvalidTokenException(detail="Invalid audience")
        except InvalidIssuerError:
            raise InvalidTokenException(detail="Invalid issuer")
        except InvalidTokenError:
            raise InvalidTokenException(detail="Unable to parse token")

    async def _authenticate_user(self, login_data: UserSignInRequest) -> bool:
        user = await self.uow.user_repository.get_user_by_email(login_data.username)
        if not user or not user.is_active or not user.hashed_password:
            self.security.verify_password(
                login_data.password,
                self.security.get_password_hash(
                    settings.auth.DUMMY_PASSWORD.get_secret_value()
                ),
            )
            return False

        if not self.security.verify_password(
            login_data.password,
            user.hashed_password,
        ):
            return False
        return True

    @classmethod
    def _get_token_from_header(cls, request: Request) -> Token:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise cls._credentials_exception

        try:
            scheme, token = auth_header.split(" ")
            if scheme.lower() != "bearer":
                raise cls._credentials_exception
        except ValueError:
            raise cls._credentials_exception

        return token

    def _create_access_token(
        self,
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

        return encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=self.JWT_ALGORITHM,
        )
