import logging

from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


class ConflictException(HTTPException):
    def __init__(self, detail: str) -> None:
        logger.error(detail)
        super().__init__(
            detail=detail,
            status_code=status.HTTP_409_CONFLICT,
        )


class NotFoundException(HTTPException):
    def __init__(self, detail="Page not found") -> None:
        logger.error(detail)
        super().__init__(
            detail=detail,
            status_code=status.HTTP_404_NOT_FOUND,
        )
