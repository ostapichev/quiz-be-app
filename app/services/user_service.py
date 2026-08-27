import logging
import math
import re
import uuid

from fastapi import UploadFile
from sqlalchemy.exc import IntegrityError

from ..core.pagination_config import PaginationConfig
from ..core.security import PasswordHasher
from ..db import UnitOfWork, User, Profile
from ..enums import AuthMethodEnum
from ..exceptions import (
    BadRequestException,
    NotFoundException,
    ConflictException,
)
from ..schemas import (
    NewUserRequest,
    Pagination,
    ProfileUpdateNumberRequest,
    PasswordRequest,
    UserDetailsResponse,
    UserUpdateRequest,
    UserResponse,
    UserSignUpRequest,
)
from ..services.image_service import ImageService

logger = logging.getLogger(__name__)


class UserService:
    def __init__(
        self,
        uow: UnitOfWork,
        image_service: ImageService,
        security: PasswordHasher,
    ) -> None:
        self.uow = uow
        self.image_service = image_service
        self.security = security

    async def signup_user(
        self,
        user_data: UserSignUpRequest,
        avatar_file: UploadFile | None = None,
    ) -> UserDetailsResponse:
        user_data = NewUserRequest(
            email=user_data.email,
            password=user_data.password,
            name=user_data.name,
            surname=user_data.surname,
            phone=user_data.phone,
        )
        return await self.create_user(user_data, avatar_file)

    async def create_user(
        self,
        user_data: NewUserRequest,
        avatar_file: UploadFile | None = None,
        picture_url: str | None = None,
    ) -> UserDetailsResponse:
        if user_data.auth_method == AuthMethodEnum.local and not user_data.password:
            raise ValueError("Password is required for registration")

        try:
            hashed_password = (
                self.security.get_password_hash(user_data.password)
                if user_data.password
                else None
            )
            user = User(
                email=user_data.email,
                hashed_password=hashed_password,
                is_active=user_data.is_active,
                is_admin=user_data.is_admin,
                is_superuser=user_data.is_superuser,
                auth_provider=user_data.auth_method,
                public_id=uuid.uuid4(),
            )
            profile = Profile(
                name=user_data.name,
                surname=user_data.surname,
                gender=user_data.gender,
                phone=user_data.phone,
            )
            user.profile = profile

            await self.uow.user_repository.save(user)
            await self.uow.flush()
        except IntegrityError as err:
            detail = self._get_integrity_error_detail(err)
            raise ConflictException(detail)

        if avatar_file:
            picture_url = await self.image_service.create_avatar(
                user_id=user.public_id,
                avatar_file=avatar_file,
            )

        if picture_url:
            avatar_path = await self.image_service.create_avatar_from_url(
                user_id=user.public_id,
                picture_url=picture_url,
            )
            profile.picture = avatar_path
            await self.uow.user_repository.save(user)

        logger.info(f"User {user.email} created successfully!")
        return await self._save_user_data(user)

    async def get_all_users(
        self,
        pagination: PaginationConfig,
        current_user: UserDetailsResponse,
    ) -> Pagination[UserResponse]:
        users, total_count = await self.uow.user_repository.get_all_users(
            skip=pagination.skip,
            limit=pagination.limit,
            current_user_id=current_user.id,
        )

        items = [UserResponse.model_validate(user) for user in users]

        if pagination.page > math.ceil(total_count / pagination.size):
            raise NotFoundException

        logger.info("All users retrieved!")
        return Pagination(
            page=pagination.page,
            size=pagination.size,
            items=items,
            total_items=total_count,
            total_pages=pagination.get_total_pages(total_count),
        )

    async def get_user_by_id(
        self,
        user_id: int,
        current_user: UserDetailsResponse,
    ) -> UserDetailsResponse:
        if current_user.id == user_id:
            raise BadRequestException

        user = await self.uow.user_repository.get_user_by_id(user_id)
        if not user:
            raise NotFoundException

        logger.info(f"User {user.id} retrieved successfully")
        return UserDetailsResponse.model_validate(user)

    async def update_user(
        self,
        user_data: UserUpdateRequest,
        current_user: UserDetailsResponse,
    ) -> UserDetailsResponse:
        user = await self.uow.user_repository.get_user_by_id(current_user.id)
        profile_fields = frozenset(ProfileUpdateNumberRequest.model_fields.keys())
        password_field = frozenset(PasswordRequest.model_fields.keys())

        try:
            update_data = user_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                if field in password_field:
                    user.hashed_password = self.security.get_password_hash(value)
                elif field in profile_fields:
                    setattr(user.profile, field, value)

            logger.info(f"User {user.email} updated successfully")
            return await self._save_user_data(user)

        except IntegrityError as err:
            detail = self._get_integrity_error_detail(err)
            raise ConflictException(detail)

    async def _save_user_data(
        self,
        user: User,
    ) -> UserDetailsResponse:
        await self.uow.flush()
        await self.uow.refresh(user)

        return UserDetailsResponse.model_validate(user)

    @staticmethod
    def _get_integrity_error_detail(err: IntegrityError) -> str:
        error_text = getattr(err.orig, "detail", str(err.orig.__str__()))
        match = re.search(r"\((.*?)\)=\((.*?)\)", error_text)

        if match:
            field, value = match.groups()
            detail = f"{field}: {value} already exists"
        else:
            detail = "Unique constraint violation"

        return detail
