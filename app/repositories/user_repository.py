from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import UserModel


class UserRepository:
    def __init__(self, session_db: AsyncSession) -> None:
        self.session_db = session_db

    async def add_user(self, user: UserModel) -> None:
        self.session_db.add(user)

    async def get_all_users(self, skip, limit) -> tuple[list[UserModel], int]:
        total_count = (
            select(func.count(UserModel.id)).select_from(UserModel).scalar_subquery()
        )
        query = (
            select(UserModel, total_count.label("total_count"))
            .offset(skip)
            .limit(limit)
            .order_by(UserModel.id.desc())
        )
        result = await self.session_db.execute(query)
        rows = result.all()
        if not rows:
            return [], 0
        items = [row[0] for row in rows]
        total_items = rows[0][1]
        return items, total_items

    async def count_all(self) -> int:
        result = await self.session_db.execute(select(func.count(UserModel.id)))
        return result.scalar_one()

    async def get_user_by_id(self, user_id: int) -> UserModel:
        result = await self.session_db.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        return result.scalar_one_or_none()

    async def search_user_by_email(self, email: str) -> UserModel:
        result = await self.session_db.execute(
            select(UserModel).where(UserModel.email == email)
        )
        return result.scalar_one_or_none()

    async def delete_user(self, user: UserModel) -> None:
        await self.session_db.delete(user)
