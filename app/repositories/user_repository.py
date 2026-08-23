from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..db import User


class UserRepository:
    def __init__(self, session_db: AsyncSession) -> None:
        self.session_db = session_db

    async def save(self, user: User) -> None:
        self.session_db.add(user)

    async def get_all_users(
        self,
        skip: int,
        limit: int,
        current_user_id: int,
    ) -> tuple[list[User], int]:
        filters = (
            User.is_superuser.is_(False),
            User.id != current_user_id,
        )

        total_count_result = await self.session_db.execute(
            select(func.count(User.id)).where(*filters)
        )
        total_count = total_count_result.scalar_one()

        if total_count == 0:
            return [], 0

        users_result = await self.session_db.execute(
            select(User)
            .where(*filters)
            .options(selectinload(User.profile))
            .offset(skip)
            .limit(limit)
            .order_by(User.id.desc())
        )
        users = list(users_result.scalars().all())
        return users, total_count

    async def get_user_by_id(self, user_id: int) -> User | None:
        filters = (User.is_superuser.is_(False),)
        result = await self.session_db.execute(
            select(User)
            .where(User.id == user_id, *filters)
            .options(selectinload(User.profile))
        )

        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        result = await self.session_db.execute(
            select(User).where(User.email == email).options(selectinload(User.profile))
        )

        return result.scalar_one_or_none()

    async def delete_user(self, user: User) -> None:
        await self.session_db.delete(user)
