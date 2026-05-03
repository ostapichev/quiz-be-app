import logging
import math
import re

from sqlalchemy.exc import IntegrityError

from app.core.pagination_config import PaginationConfig
from app.db import UnitOfWork, UserModel
from app.exceptions import NotFoundException, ConflictException
from app.schemas import (
    PaginationSchema,
    UserSignUpRequestSchema,
    UserDetailsResponseSchema,
    UserUpdateRequestSchema,
    UserResponseSchema,
)
from app.utils import hash_password

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def create_user(
        self,
        user_data: UserSignUpRequestSchema,
    ) -> UserDetailsResponseSchema:
        try:
            new_user = UserModel(
                name=user_data.name,
                surname=user_data.surname,
                username=user_data.username,
                email=user_data.email,
                phone=user_data.phone,
                hashed_password=hash_password(user_data.password),
            )
            await self.uow.user_repository.add_user(new_user)
            logger.info(f"User {new_user.username} created successfully!")
            return await self._save_user_data(new_user)

        except IntegrityError as err:
            await self.uow.rollback()
            detail = self._get_integrity_error_detail(err)
            raise ConflictException(detail)

    async def get_all_users(
        self,
        pagination: PaginationConfig,
    ) -> PaginationSchema[UserResponseSchema]:
        users, total_count = await self.uow.user_repository.get_all_users(
            skip=pagination.skip,
            limit=pagination.limit,
        )
        items = [UserResponseSchema.model_validate(user) for user in users]
        if pagination.page > math.ceil(total_count / pagination.size):
            raise NotFoundException
        logger.info("All users retrieved!")
        return PaginationSchema(
            page=pagination.page,
            size=pagination.size,
            items=items,
            total_items=total_count,
            total_pages=pagination.get_total_pages(total_count),
        )

    async def get_user_by_id(self, user_id: int) -> UserDetailsResponseSchema:
        user = await self._get_user_exists(user_id)
        logger.info(f"User {user.username} retrieved successfully")
        return UserDetailsResponseSchema.model_validate(user)

    async def update_user(
        self,
        user_id: int,
        user_data: UserUpdateRequestSchema,
    ) -> UserDetailsResponseSchema:
        user = await self._get_user_exists(user_id)
        try:
            update_data = user_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                if field == "password":
                    user.hashed_password = hash_password(value)
                else:
                    setattr(user, field, value)
            logger.info(f"User {user.username} updated successfully")
            return await self._save_user_data(user)
        except IntegrityError as err:
            await self.uow.rollback()
            detail = self._get_integrity_error_detail(err)
            raise ConflictException(detail)

    async def delete_user(self, user_id: int) -> None:
        user = await self._get_user_exists(user_id)
        await self.uow.user_repository.delete_user(user)
        await self.uow.flush()
        logger.info(f"User {user.username} deleted successfully")

    async def _get_user_exists(self, user_id: int) -> UserModel:
        user = await self.uow.user_repository.get_user_by_id(user_id)
        if not user:
            raise NotFoundException(
                detail=f"User with id {user_id} does not exist",
            )
        return user

    async def _save_user_data(
        self,
        user: UserModel,
    ) -> UserDetailsResponseSchema:
        await self.uow.flush()
        await self.uow.refresh(user)
        return UserDetailsResponseSchema.model_validate(user)

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
