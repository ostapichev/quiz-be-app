import pytest
import pytest_asyncio
from io import BytesIO
from collections.abc import Callable, AsyncGenerator

from _pytest.monkeypatch import MonkeyPatch
from fastapi import Request
from faker import Faker
from PIL import Image
from starlette.datastructures import Headers, UploadFile as StarletteUploadFile
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
    UserDetailsResponse,
    UserResponse,
)
from ..services import AuthService, ImageService, UserService
from ..utils import valid_test_phone_number

type UserFactory = Callable[[int], list[UserResponse]]
type ImageFactory = Callable[[], StarletteUploadFile]
type PayloadAuth0Factory = Callable[..., dict]
type MokeVerifyTokenFactory = Callable[[dict], None]


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
def uow(session: AsyncSession) -> AsyncGenerator[UnitOfWork, None]:
    return UnitOfWork(session)


@pytest.fixture
def password_hasher() -> PasswordHasher:
    return PasswordHasher()


@pytest.fixture
def user_service(
    uow: UnitOfWork,
    image_service: ImageService,
    password_hasher: PasswordHasher,
) -> UserService:
    return get_user_service(uow, image_service, password_hasher)


@pytest.fixture
def auth_service(
    uow: UnitOfWork,
    user_service: UserService,
    image_service: ImageService,
    password_hasher: PasswordHasher,
) -> AuthService:
    return get_auth_service(uow, user_service, image_service, password_hasher)


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
                phone=valid_test_phone_number(
                    faker_instance.unique.random_int(min=0, max=9999)
                ),
                password=faker_instance.password(),
            )
            for _ in range(count)
        ]

    return _create


@pytest.fixture
def single_user(user_factory: UserFactory) -> UserResponse:
    return user_factory(1)[0]


@pytest_asyncio.fixture
async def current_user(
    user_service: UserService,
    single_user: NewUserRequest,
) -> UserDetailsResponse:
    return await user_service.create_user(single_user)


@pytest.fixture
def make_image_file() -> ImageFactory:
    def _make() -> StarletteUploadFile:
        buffer = BytesIO()
        image = Image.new("RGB", (128, 128), color="red")
        image.save(buffer, format="PNG")
        buffer.seek(0)

        return StarletteUploadFile(
            file=buffer,
            filename="avatar.png",
            headers=Headers({"content-type": "image/png"}),
        )

    return _make


@pytest.fixture
def make_auth0_payload(faker_instance: Faker) -> PayloadAuth0Factory:
    def _make(
        email: str = faker_instance.unique.email(),
        given_name: str | None = "Name",
        family_name: str | None = "Surname",
        picture: str | None = None,
        email_verified: bool = True,
        sub: str = "auth0|123456",
    ) -> dict:
        issuer = settings.auth.issuer_url
        namespace = settings.auth.AUTH0_ACTIONS_NAMESPACE
        audience = settings.auth.AUTH0_AUDIENCE

        return {
            "iss": issuer,
            "sub": sub,
            "aud": [audience],
            f"{namespace}/email": email,
            f"{namespace}/email_verified": email_verified,
            f"{namespace}/given_name": given_name,
            f"{namespace}/family_name": family_name,
            f"{namespace}/picture": picture,
        }

    return _make


@pytest.fixture
def mock_verify_token(
    auth_service: AuthService,
    monkeypatch: MonkeyPatch,
) -> MokeVerifyTokenFactory:
    def _mock(payload: dict) -> None:
        async def _fake_verify_token(request: Request) -> dict:
            return payload

        monkeypatch.setattr(
            auth_service,
            "decode_auth0_token",
            _fake_verify_token,
        )

    return _mock


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
