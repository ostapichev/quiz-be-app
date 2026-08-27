import pytest
from _pytest.monkeypatch import MonkeyPatch
from io import BytesIO

from faker import Faker
from fastapi import Request, status
from respx import MockRouter
from PIL import Image

from ..exceptions import UnauthorizedException
from ..schemas import NewUserRequest, UserResponse, UserSignInRequest
from ..services import AuthService, UserService
from .conftest import (
    ImageFactory,
    PayloadAuth0Factory,
    MokeVerifyTokenFactory,
)


@pytest.mark.asyncio
async def test_get_token(
    auth_service: AuthService,
    user_service: UserService,
    single_user: UserResponse,
) -> None:
    user_data = NewUserRequest(**single_user.model_dump())
    await user_service.create_user(user_data)

    login_data = UserSignInRequest(
        username=user_data.email,
        password=user_data.password,
    )
    wrong_password = UserSignInRequest(
        username=user_data.email,
        password="wrong_password",
    )
    wrong_email = UserSignInRequest(
        username="wrong_email",
        password=user_data.password,
    )
    wrong_email_password = UserSignInRequest(
        username="wrong_email",
        password="wrong_password",
    )

    token = await auth_service.get_token(login_data)
    user = await auth_service.get_current_user(token.access_token)

    with pytest.raises(UnauthorizedException) as exc:
        await auth_service.get_token(wrong_password)

    with pytest.raises(UnauthorizedException) as exc_email:
        await auth_service.get_token(wrong_email)

    with pytest.raises(UnauthorizedException) as exc_email_password:
        await auth_service.get_token(wrong_email_password)

    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc.value.detail == "Incorrect email or password"

    assert exc_email.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc.value.detail == "Incorrect email or password"

    assert exc_email_password.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc.value.detail == "Incorrect email or password"

    assert token.access_token
    assert token.token_type == "bearer"

    assert user.email == user_data.email
    assert user.profile.name == user_data.name


@pytest.mark.asyncio
async def test_verify_auth0_user_business_logic(
    auth_service: AuthService,
    test_request: Request,
    make_auth0_payload: PayloadAuth0Factory,
    mock_verify_token: MokeVerifyTokenFactory,
    monkeypatch: MonkeyPatch,
    faker_instance: Faker,
) -> None:
    email = faker_instance.unique.email()
    payload = make_auth0_payload(email)
    mock_verify_token(payload)
    result = await auth_service.verify_auth0_user(test_request)

    assert result.email == email


@pytest.mark.asyncio
async def test_verify_auth0_user_creates_new_user(
    auth_service: AuthService,
    make_auth0_payload: PayloadAuth0Factory,
    mock_verify_token: MokeVerifyTokenFactory,
    test_request: Request,
    faker_instance: Faker,
) -> None:
    email = faker_instance.unique.email()
    payload = make_auth0_payload(email)
    mock_verify_token(payload)
    result = await auth_service.verify_auth0_user(test_request)

    assert result.email == email
    assert result.profile.name == "Name"
    assert result.profile.surname == "Surname"


async def test_verify_auth0_user_existing_user_reuses_record(
    auth_service: AuthService,
    make_auth0_payload: PayloadAuth0Factory,
    mock_verify_token: MokeVerifyTokenFactory,
    test_request: Request,
) -> None:
    payload = make_auth0_payload(email="existing@example.com")
    mock_verify_token(payload)

    first = await auth_service.verify_auth0_user(test_request)
    second = await auth_service.verify_auth0_user(test_request)

    assert first.id == second.id


async def test_verify_auth0_user_missing_name_fields_uses_fallback(
    auth_service: AuthService,
    make_auth0_payload: PayloadAuth0Factory,
    mock_verify_token: MokeVerifyTokenFactory,
    test_request: Request,
) -> None:
    payload = make_auth0_payload(
        email="noname@example.com",
        given_name=None,
        family_name=None,
    )
    mock_verify_token(payload)
    result = await auth_service.verify_auth0_user(test_request)

    assert result.email == "noname@example.com"
    assert result.profile.name
    assert result.profile.surname is not None


@pytest.mark.asyncio
async def test_verify_auth0_user_with_picture_downloads_avatar(
    auth_service: AuthService,
    make_auth0_payload: PayloadAuth0Factory,
    mock_verify_token: MokeVerifyTokenFactory,
    make_image_file: ImageFactory,
    test_request: Request,
    respx_mock: MockRouter,
) -> None:
    picture_url = "https://s.gravatar.com/avatar/fake.png"
    payload = make_auth0_payload(email="withpic@example.com", picture=picture_url)
    mock_verify_token(payload)

    buffer = BytesIO()
    Image.new("RGB", (10, 10), color="blue").save(buffer, format="PNG")
    respx_mock.get(picture_url).respond(
        content=buffer.getvalue(),
        headers={"content-type": "image/png"},
    )

    result = await auth_service.verify_auth0_user(test_request)

    assert result.profile.picture is not None


async def test_verify_auth0_user_without_picture(
    auth_service: AuthService,
    make_auth0_payload: PayloadAuth0Factory,
    mock_verify_token: MokeVerifyTokenFactory,
    test_request: Request,
) -> None:
    payload = make_auth0_payload(email="nopic@example.com", picture=None)
    mock_verify_token(payload)
    result = await auth_service.verify_auth0_user(test_request)

    assert result.email == "nopic@example.com"
    assert result.profile.picture is None
