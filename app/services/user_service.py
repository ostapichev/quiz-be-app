import logging
import math
import re

from sqlalchemy.exc import IntegrityError

from ..core.pagination_config import PaginationConfig
from ..core.security import PasswordHasher
from ..db import UnitOfWork, User, Profile
from ..exceptions import (
    BadRequestException,
    NotFoundException,
    ConflictException,
)
from ..schemas import (
    NewUserRequest,
    Pagination,
    ProfileUpdateRequest,
    SuperUserRequest,
    UpdatePasswordRequest,
    UserDetailsResponse,
    UserUpdateRequest,
    UserResponse,
)

logger = logging.getLogger(__name__)


class UserService:
    def __init__(
        self,
        uow: UnitOfWork,
        security: PasswordHasher,
    ) -> None:
        self.uow = uow
        self.security = security

    async def create_user(
        self,
        user_data: NewUserRequest | SuperUserRequest,
    ) -> UserDetailsResponse:
        try:
            user = User(
                email=user_data.email,
                hashed_password=self.security.get_password_hash(user_data.password),
                is_active=True,
                is_admin=user_data.is_admin,
                is_superuser=user_data.is_superuser,
            )
            profile = Profile(
                name=user_data.name,
                surname=user_data.surname,
                gender=user_data.gender,
                phone=user_data.phone,
            )
            user.profile = profile
            await self.uow.user_repository.save(user)

            logger.info(f"User {user.email} created successfully!")

            return await self._save_user_data(user)

        except IntegrityError as err:
            detail = self._get_integrity_error_detail(err)
            raise ConflictException(detail)

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

        logger.info(f"User {user.email} retrieved successfully")

        return UserDetailsResponse.model_validate(user)

    async def update_user(
        self,
        user_data: UserUpdateRequest,
        current_user: UserDetailsResponse,
    ) -> UserDetailsResponse:
        user = await self.uow.user_repository.get_user_by_id(current_user.id)
        profile_fields = frozenset(ProfileUpdateRequest.model_fields.keys())
        password_field = frozenset(UpdatePasswordRequest.model_fields.keys())

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
        error_text = getattr(err.orig, "detail", str(err.orig))
        match = re.search(r"\((.*?)\)=\((.*?)\)", error_text)

        if match:
            field, value = match.groups()
            detail = f"{field}: {value} already exists"
        else:
            detail = "Unique constraint violation"

        return detail
