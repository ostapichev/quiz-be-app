from fastapi import Request, FastAPI, status
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.responses import JSONResponse

from ..exceptions.exceptions import (
    BadRequestException,
    ConflictException,
    CredentialsException,
    InvalidTokenException,
    NotFoundException,
    PermissionException,
    UnauthorizedException,
    UnicornException,
)


def exception_handler(
    request: Request,
    exc: UnicornException,
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status": exc.status_code,
            "request": request.url.path,
        },
    )


def validation_exception_handler(
    request: Request,
    exc: ValidationError,
) -> JSONResponse:
    errors = [
        {key: value for key, value in error.items() if key != "ctx"}
        for error in exc.errors()
    ]
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT

    return JSONResponse(
        status_code=status_code,
        content={
            "detail": errors,
            "status": status_code,
            "request": request.url.path,
        },
    )


def register_exception_handler(app: FastAPI) -> None:
    app.add_exception_handler(BadRequestException, exception_handler)
    app.add_exception_handler(ConflictException, exception_handler)
    app.add_exception_handler(CredentialsException, exception_handler)
    app.add_exception_handler(InvalidTokenException, exception_handler)
    app.add_exception_handler(NotFoundException, exception_handler)
    app.add_exception_handler(PermissionException, exception_handler)
    app.add_exception_handler(UnauthorizedException, exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)
    app.add_exception_handler(
        RequestValidationError,
        request_validation_exception_handler,
    )
