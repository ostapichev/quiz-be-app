import pytest

from fastapi import status

from ..exceptions import UnauthorizedException
from ..schemas import NewUserRequest, UserSignInRequest
from ..services import AuthService, UserService


@pytest.mark.asyncio
async def test_get_token(
    auth_service: AuthService,
    user_service: UserService,
    single_user: NewUserRequest,
) -> None:
    await user_service.create_user(single_user)

    login_data = UserSignInRequest(
        username=single_user.email,
        password=single_user.password,
    )
    wrong_password = UserSignInRequest(
        username=single_user.email,
        password="wrong_password",
    )
    wrong_email = UserSignInRequest(
        username="wrong_email",
        password=single_user.password,
    )
    wrong_email_password = UserSignInRequest(
        username="wrong_email",
        password="wrong_password",
    )

    token = await auth_service.get_token(login_data)
    user = await auth_service.get_current_user(token.access_token)

    with pytest.raises(UnauthorizedException) as exc:
        await auth_service.get_token(wrong_password)

    with pytest.raises(UnauthorizedException):
        await auth_service.get_token(wrong_email)

    with pytest.raises(UnauthorizedException):
        await auth_service.get_token(wrong_email_password)

    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc.value.detail == "Incorrect email or password"

    assert token.access_token
    assert token.token_type == "bearer"

    assert user.email == single_user.email
    assert user.profile.name == single_user.name
