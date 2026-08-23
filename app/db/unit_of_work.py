from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories import UserRepository


class UnitOfWork:
    def __init__(self, session_db: AsyncSession) -> None:
        self.session_db = session_db
        self.user_repository = UserRepository(self.session_db)

    async def __aenter__(self) -> Self:
        return self

    async def rollback(self) -> None:
        await self.session_db.rollback()

    async def flush(self) -> None:
        await self.session_db.flush()

    async def refresh(self, instance) -> None:
        await self.session_db.refresh(instance)

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if exc:
            await self.session_db.rollback()
        else:
            await self.session_db.commit()
        await self.session_db.close()
