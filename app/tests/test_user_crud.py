import math

import pytest
from fastapi import status

from ..core.pagination_config import PaginationConfig
from ..db import UnitOfWork
from ..enums import GenderEnum
from ..exceptions import (
    NotFoundException,
    ConflictException,
)
from ..schemas import (
    NewUserRequest,
    UserDetailsResponse,
    UserUpdateRequest,
    UserResponse,
)
from ..services import UserService
from .conftest import UserFactory


@pytest.mark.asyncio
async def test_create_user_without_avatar(
    uow: UnitOfWork,
    user_service: UserService,
    single_user: UserResponse,
) -> None:
    user_data = NewUserRequest(**single_user.model_dump())
    new_user = await user_service.create_user(user_data)
    user_model = await uow.user_repository.get_user_by_id(new_user.id)
    hashed_password = user_model.hashed_password

    with pytest.raises(ConflictException) as exc_info:
        await user_service.create_user(user_data)

    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert new_user.id is not None

    assert user_data.email == new_user.email
    assert user_data.password != hashed_password
    assert user_data.name == new_user.profile.name
    assert user_data.surname == new_user.profile.surname

    assert new_user.is_active == True
    assert new_user.is_admin == False
    assert new_user.is_superuser == False

    assert isinstance(new_user, UserDetailsResponse)
    assert isinstance(exc_info.value, ConflictException)


@pytest.mark.asyncio
async def test_get_user_by_id(
    user_service: UserService,
    current_user: UserDetailsResponse,
    user_factory: UserFactory,
) -> None:
    user_data = NewUserRequest(**user_factory(1)[0].model_dump())
    new_user = await user_service.create_user(user_data)
    fetched_user = await user_service.get_user_by_id(
        new_user.id,
        current_user,
    )

    assert fetched_user.id == new_user.id
    assert fetched_user.email == new_user.email
    assert fetched_user.profile.name == new_user.profile.name
    assert fetched_user.id != current_user.id


@pytest.mark.asyncio
async def test_update_user(
    uow: UnitOfWork,
    user_service: UserService,
    current_user: UserDetailsResponse,
) -> None:
    update_data = UserUpdateRequest(
        name="update_name",
        surname="update_surname",
        password="12345678_update_password",
        phone="+380675441236",
        gender=GenderEnum.female,
    )

    updated_user = await user_service.update_user(update_data, current_user)
    fetched_user = await uow.user_repository.get_user_by_id(current_user.id)

    assert updated_user.id == current_user.id
    assert updated_user.profile.name == update_data.name
    assert updated_user.profile.surname == update_data.surname
    assert updated_user.email == current_user.email

    assert fetched_user.profile.name == update_data.name
    assert fetched_user.profile.surname == update_data.surname


@pytest.mark.asyncio
async def test_get_all_users_with_pagination(
    user_service: UserService,
    user_factory: UserFactory,
    current_user: UserDetailsResponse,
) -> None:
    input_users = user_factory(22)

    with pytest.raises(NotFoundException) as empty_db:
        await user_service.get_all_users(
            pagination=PaginationConfig(page=1, size=5),
            current_user=current_user,
        )

    pagination_page_1 = PaginationConfig(page=1, size=5)
    pagination_page_3 = PaginationConfig(page=3, size=5)

    for user in input_users:
        await user_service.create_user(user)

    users_page_1 = await user_service.get_all_users(
        pagination_page_1,
        current_user,
    )
    users_page_3 = await user_service.get_all_users(
        pagination_page_3,
        current_user,
    )
    users_last_page = await user_service.get_all_users(
        PaginationConfig(page=5, size=5),
        current_user,
    )

    ids_page_1 = [user.id for user in users_page_1.items]
    users_page_2 = await user_service.get_all_users(
        PaginationConfig(page=2, size=5),
        current_user,
    )
    ids_page_2 = [user.id for user in users_page_2.items]

    with pytest.raises(NotFoundException) as exc_info:
        await user_service.get_all_users(
            PaginationConfig(page=6, size=5),
            current_user,
        )

    assert empty_db.value.status_code == status.HTTP_404_NOT_FOUND
    assert isinstance(empty_db.value, NotFoundException)

    assert not set(ids_page_1) & set(ids_page_2)
    assert ids_page_1 == sorted(ids_page_1, reverse=True)

    assert users_page_1.total_items == len(input_users)
    assert users_page_3.total_items == len(input_users)
    assert users_last_page.total_pages == math.ceil(
        len(input_users) / users_last_page.size
    )

    assert len(users_page_1.items) == pagination_page_1.size
    assert len(users_page_3.items) == pagination_page_3.size
    assert len(users_last_page.items) == 2

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert isinstance(exc_info.value, NotFoundException)

    for user in users_page_1.items:
        assert isinstance(user, UserResponse)

    for user in users_page_3.items:
        assert isinstance(user, UserResponse)
