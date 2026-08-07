from typing import Annotated

from fastapi import APIRouter, status, Depends, Request, Form, UploadFile

from ..core.dependencies import (
    get_user_service,
    get_image_service,
    get_current_user,
)
from ..core.pagination_config import PaginationConfig
from ..schemas import (
    NewUserRequest,
    Pagination,
    UserResponse,
    UserDetailsResponse,
    UserSignUpRequest,
    UserUpdateRequest,
)
from ..services import ImageService, UserService

user_router = APIRouter(tags=["Users"], prefix="/users")


@user_router.post(
    "/",
    description="Create a new user",
    response_model=UserDetailsResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user: Annotated[UserSignUpRequest, Form()],
    service: UserService = Depends(get_user_service),
) -> UserDetailsResponse:
    new_user = NewUserRequest(**user.model_dump())
    return await service.create_user(new_user)


@user_router.post(
    "/upload_avatar",
    description="Upload an avatar",
    response_model=UserDetailsResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_avatar(
    request: Request,
    file: UploadFile,
    service: ImageService = Depends(get_image_service),
    current_user=Depends(get_current_user),
) -> UserDetailsResponse:
    return await service.upload_avatar(request, current_user, file)


@user_router.put(
    "/",
    description="Update a user",
    response_model=UserDetailsResponse,
    status_code=status.HTTP_200_OK,
)
async def update_user(
    user_data: Annotated[UserUpdateRequest, Form()],
    service: UserService = Depends(get_user_service),
    current_user=Depends(get_current_user),
) -> UserDetailsResponse:
    return await service.update_user(user_data, current_user)


@user_router.get(
    "/",
    description="Retrieve a paginate list of users",
    response_model=Pagination[UserResponse],
    status_code=status.HTTP_200_OK,
)
async def get_user_list(
    pagination: PaginationConfig = Depends(),
    service: UserService = Depends(get_user_service),
    current_user=Depends(get_current_user),
) -> Pagination[UserResponse]:
    return await service.get_all_users(pagination, current_user)


@user_router.get(
    "/{user_id}",
    description="Get a user by id",
    response_model=UserDetailsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_user_details(
    user_id: int,
    service: UserService = Depends(get_user_service),
    current_user=Depends(get_current_user),
) -> UserDetailsResponse:
    return await service.get_user_by_id(user_id, current_user)
