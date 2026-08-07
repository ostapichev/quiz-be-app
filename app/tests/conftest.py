import pytest
import pytest_asyncio

from io import BytesIO
from typing import TypeAlias, Callable

from fastapi import Request, UploadFile
from faker import Faker
from PIL import Image
from starlette.datastructures import Headers
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncEngine,
)

from ..core.dependencies import (
    get_auth_service,
    get_user_service,
    get_image_service,
)
from ..core.security import PasswordHasher
from ..core.settings import settings
from ..db import User, UnitOfWork
from ..enums import GenderEnum
from ..schemas import (
    NewUserRequest,
    UserResponse,
)
from ..services import AuthService, ImageService, UserService

UserFactory: TypeAlias = Callable[[int], list[NewUserRequest]]


@pytest_asyncio.fixture(scope="function")
async def engine() -> AsyncEngine:
    engine = create_async_engine(settings.test_db.url, echo=settings.DEBUG)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function", autouse=True)
async def prepare_db(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(User.metadata.drop_all)
        await conn.run_sync(User.metadata.create_all)


@pytest_asyncio.fixture(scope="function")
async def session(engine: AsyncEngine) -> AsyncSession:
    async_session = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
def uow(session: AsyncSession) -> UnitOfWork:
    return UnitOfWork(session)


@pytest.fixture
def password_hasher() -> str:
    return PasswordHasher()


@pytest.fixture
def user_service(
    uow: UnitOfWork,
    password_hasher: PasswordHasher,
) -> UserService:
    return get_user_service(uow, password_hasher)


@pytest.fixture
def auth_service(
    uow: UnitOfWork,
    password_hasher: PasswordHasher,
) -> AuthService:
    return get_auth_service(uow, password_hasher)


@pytest.fixture
def image_service(uow: UnitOfWork) -> ImageService:
    return get_image_service(uow)


@pytest.fixture(scope="session")
def faker_instance() -> Faker:
    faker = Faker()
    faker.unique.clear()
    return faker


@pytest.fixture
def user_factory(faker_instance: Faker) -> UserFactory:
    def _create(count: int) -> list[UserResponse]:
        return [
            NewUserRequest(
                name=faker_instance.first_name(),
                surname=faker_instance.last_name(),
                email=faker_instance.unique.email(),
                gender=GenderEnum.male,
                phone=f"+180{faker_instance.msisdn()[3:]}",
                password=faker_instance.password(),
            )
            for _ in range(count)
        ]

    return _create


@pytest.fixture
def single_user(user_factory: UserFactory) -> NewUserRequest:
    return user_factory(1)[0]


@pytest_asyncio.fixture
async def current_user(
    user_service: UserService,
    single_user: NewUserRequest,
) -> User:
    return await user_service.create_user(single_user)


@pytest.fixture
def image_file() -> UploadFile:
    buffer = BytesIO()

    Image.new("RGB", (500, 300), color="red").save(
        buffer,
        format="PNG",
    )
    buffer.seek(0)

    return UploadFile(
        filename="avatar.png",
        file=buffer,
        headers=Headers({"content-type": "image/png"}),
    )


@pytest.fixture
def test_request() -> Request:
    scope = {
        "type": "http",
        "scheme": "http",
        "server": ("test_server", "80"),
        "path": "/",
        "headers": [],
    }

    return Request(scope)
