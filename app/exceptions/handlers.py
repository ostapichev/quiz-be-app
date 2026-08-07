from fastapi import Request, FastAPI
from starlette.responses import JSONResponse

from ..exceptions.exceptions import (
    BadRequestException,
    ConflictException,
    CredentialsException,
    NotFoundException,
    PermissionException,
    UnauthorizedException,
    UnicornException,
)


def exception_handler(request: Request, exc: UnicornException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status": exc.status_code,
            "request": request.url.path,
        },
    )


def register_exception_handler(app: FastAPI) -> None:
    app.add_exception_handler(BadRequestException, exception_handler)
    app.add_exception_handler(ConflictException, exception_handler)
    app.add_exception_handler(CredentialsException, exception_handler)
    app.add_exception_handler(NotFoundException, exception_handler)
    app.add_exception_handler(PermissionException, exception_handler)
    app.add_exception_handler(UnauthorizedException, exception_handler)
