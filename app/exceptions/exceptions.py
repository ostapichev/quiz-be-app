import logging

from fastapi import status

logger = logging.getLogger(__name__)


class UnicornException(Exception):
    def __init__(
        self,
        detail: str,
        status_code: int,
        headers: dict | None = None,
    ) -> None:
        self.detail = detail
        self.status_code = status_code
        self.headers = headers


class BadRequestException(UnicornException):
    def __init__(self, detail="Bad request") -> None:
        logger.error(detail)
        super().__init__(
            detail=detail,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class ConflictException(UnicornException):
    def __init__(self, detail: str) -> None:
        logger.error(detail)
        super().__init__(
            detail=detail,
            status_code=status.HTTP_409_CONFLICT,
        )


class CredentialsException(UnicornException):
    def __init__(self, detail="Could not validate credentials") -> None:
        logger.error(detail)
        super().__init__(
            detail=detail,
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        )


class NotFoundException(UnicornException):
    def __init__(self, detail="Page not found") -> None:
        logger.error(detail)
        super().__init__(
            detail=detail,
            status_code=status.HTTP_404_NOT_FOUND,
        )


class PermissionException(UnicornException):
    def __init__(
        self,
        detail="You do not have permission to perform this action",
    ) -> None:
        logger.error(detail)
        super().__init__(
            detail=detail,
            status_code=status.HTTP_403_FORBIDDEN,
        )


class UnauthorizedException(UnicornException):
    def __init__(self, detail="Incorrect email or password") -> None:
        logger.error(detail)
        super().__init__(
            detail=detail,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
