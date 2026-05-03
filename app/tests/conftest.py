from typing import TypeAlias, Callable

import pytest
from faker import Faker
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)

from app.core.dependencies import get_user_service
from app.core.settings import settings
from app.db import UserModel, UnitOfWork
from app.schemas import UserSignUpRequestSchema
from app.services import UserService
from app.utils import hash_password

UserFactory: TypeAlias = Callable[[int], list[UserSignUpRequestSchema]]


@pytest.fixture(scope="function")
async def session() -> AsyncSession:
    engine = create_async_engine(settings.test_db.url, echo=settings.DEBUG)
    async_session = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(UserModel.metadata.drop_all)
        await conn.run_sync(UserModel.metadata.create_all)
    async with async_session() as session:
        yield session
        await engine.dispose()


@pytest.fixture
def uow(session: AsyncSession) -> UnitOfWork:
    return UnitOfWork(session)


@pytest.fixture
def user_service(uow: UnitOfWork) -> UserService:
    return get_user_service(uow)


@pytest.fixture
def faker_instance() -> Faker:
    return Faker()


@pytest.fixture
def user_factory(faker_instance: Faker) -> UserFactory:
    def _create(count: int) -> list[UserSignUpRequestSchema]:
        return [
            UserSignUpRequestSchema(
                name=faker_instance.first_name(),
                surname=faker_instance.last_name(),
                email=faker_instance.email(),
                username=faker_instance.user_name(),
                phone=f"+180{faker_instance.msisdn()[3:]}",
                password=hash_password(faker_instance.password()),
            )
            for _ in range(count)
        ]

    return _create


@pytest.fixture
def single_user(user_factory: UserFactory) -> UserSignUpRequestSchema:
    return user_factory(1)[0]
