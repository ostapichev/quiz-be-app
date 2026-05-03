from typing import TypeVar

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from app.db import BaseModel
from app.repositories import UserRepository

ModelType = TypeVar("ModelType", bound=BaseModel)


class UnitOfWork:
    def __init__(self, session_db: AsyncSession) -> None:
        self.session_db = session_db
        self.user_repository = UserRepository(self.session_db)

    async def __aenter__(self):
        return self

    async def rollback(self):
        await self.session_db.rollback()

    async def flush(self):
        await self.session_db.flush()

    async def refresh(self, instance):
        await self.session_db.refresh(instance)

    async def __aexit__(self, exc_type, exc, tb):
        if exc:
            await self.session_db.rollback()
        else:
            await self.session_db.commit()
        await self.session_db.close()
