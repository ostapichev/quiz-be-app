from fastapi import APIRouter, status, Depends

from app.dependencies import get_response_service
from app.schemas import ResponseSchema
from app.services import ResponseService

response_router = APIRouter(tags=["First route"], prefix="/response")


@response_router.get(
    "/",
    response_model=ResponseSchema,
    status_code=status.HTTP_200_OK,
)
def index(
    service: ResponseService = Depends(get_response_service),
) -> ResponseSchema:
    return service.get_response()


@response_router.post(
    "/cache/{detail}/{result}",
    response_model=ResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_cache(
    detail: str,
    result: str,
    service: ResponseService = Depends(get_response_service),
) -> ResponseSchema:
    return await service.create_cache_response(detail, result)


@response_router.get(
    "/cache",
    response_model=ResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_cache(
    service: ResponseService = Depends(get_response_service),
) -> ResponseSchema:
    return await service.get_cache_response()


@response_router.delete(
    "/cache", response_model=None, status_code=status.HTTP_204_NO_CONTENT
)
async def del_cache(
    service: ResponseService = Depends(get_response_service),
) -> None:
    return await service.delete_cache_response()
