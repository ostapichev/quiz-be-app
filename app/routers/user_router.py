from fastapi import APIRouter, status, Depends, Response

from app.core.dependencies import get_user_service
from app.core.pagination_config import PaginationConfig
from app.schemas import (
    UserResponseSchema,
    UserDetailsResponseSchema,
    UserSignUpRequestSchema,
    UserUpdateRequestSchema,
)
from app.schemas import PaginationSchema
from app.services import UserService

user_router = APIRouter(tags=["Users"], prefix="/users")


@user_router.post(
    "/",
    description="Create a new user",
    response_model=UserDetailsResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user: UserSignUpRequestSchema,
    service: UserService = Depends(get_user_service),
) -> UserDetailsResponseSchema:
    return await service.create_user(user)


@user_router.get(
    "/",
    description="Retrieve a paginate list of users",
    response_model=PaginationSchema[UserResponseSchema],
    status_code=status.HTTP_200_OK,
)
async def get_user_list(
    pagination: PaginationConfig = Depends(),
    service: UserService = Depends(get_user_service),
) -> PaginationSchema[UserResponseSchema]:
    return await service.get_all_users(pagination)


@user_router.get(
    "/{user_id}",
    description="Get a user by id",
    response_model=UserDetailsResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_user_details(
    user_id: int,
    service: UserService = Depends(get_user_service),
) -> UserDetailsResponseSchema:
    return await service.get_user_by_id(user_id)


@user_router.patch(
    "/{user_id}",
    description="Update a user",
    response_model=UserDetailsResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def update_user(
    user_id: int,
    user_data: UserUpdateRequestSchema,
    service: UserService = Depends(get_user_service),
) -> UserDetailsResponseSchema:
    return await service.update_user(user_id, user_data)


@user_router.delete(
    "/{user_id}",
    description="Delete a user",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
) -> Response:
    await service.delete_user(user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
