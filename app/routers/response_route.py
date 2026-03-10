from fastapi import APIRouter, status

from app.schemas import ResponseSchema

response_router = APIRouter(tags=["First route"], prefix="/response")


@response_router.get(
    "/",
    response_model=ResponseSchema,
    status_code=status.HTTP_200_OK,
)
def index() -> ResponseSchema:
    return ResponseSchema(
        status_code=status.HTTP_200_OK,
        detail="ok",
        result="working",
    )
