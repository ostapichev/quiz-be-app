from fastapi import Request, HTTPException, FastAPI
from starlette.responses import JSONResponse

from app.exceptions.exceptions import NotFoundException, ConflictException


def exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status": exc.status_code,
            "request": request.url.path,
        },
    )


def register_exception_handler(app: FastAPI) -> None:
    app.add_exception_handler(NotFoundException, exception_handler)
    app.add_exception_handler(ConflictException, exception_handler)
