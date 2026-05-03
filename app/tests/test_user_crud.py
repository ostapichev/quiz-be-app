import math
from typing import TypeAlias, Callable

import pytest
from fastapi import status

from app.core.pagination_config import PaginationConfig
from app.db import UnitOfWork
from app.exceptions import NotFoundException, ConflictException
from app.schemas import (
    UserDetailsResponseSchema,
    UserUpdateRequestSchema,
    UserResponseSchema,
    UserSignUpRequestSchema,
)
from app.services import UserService

UserFactory: TypeAlias = Callable[[int], list[UserSignUpRequestSchema]]


@pytest.mark.asyncio
async def test_create_user(
    uow: UnitOfWork,
    single_user: UserSignUpRequestSchema,
    user_service: UserService,
) -> None:
    created_user = await user_service.create_user(single_user)
    user_model = await uow.user_repository.get_user_by_id(created_user.id)
    hashed_password = user_model.hashed_password

    with pytest.raises(ConflictException) as exc_info:
        await user_service.create_user(single_user)

    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert created_user.id is not None

    assert single_user.password != hashed_password
    assert single_user.name == created_user.name
    assert single_user.surname == created_user.surname
    assert single_user.username == created_user.username
    assert single_user.email == created_user.email

    assert isinstance(created_user, UserDetailsResponseSchema)
    assert isinstance(exc_info.value, ConflictException)


@pytest.mark.asyncio
async def test_get_user_by_id(
    uow: UnitOfWork,
    single_user: UserSignUpRequestSchema,
    user_service: UserService,
) -> None:
    created_user = await user_service.create_user(single_user)
    fetched_user = await user_service.get_user_by_id(created_user.id)

    with pytest.raises(NotFoundException) as exc_info:
        await user_service.get_user_by_id(9999999)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    assert fetched_user.created_at is not None
    assert fetched_user is not None
    assert fetched_user is not created_user
    assert fetched_user.id == created_user.id
    assert fetched_user.name == created_user.name
    assert fetched_user.email == created_user.email
    assert fetched_user.username == created_user.username

    assert isinstance(fetched_user, UserDetailsResponseSchema)
    assert isinstance(exc_info.value, NotFoundException)


@pytest.mark.asyncio
async def test_update_user(
    uow: UnitOfWork,
    single_user: UserSignUpRequestSchema,
    user_service: UserService,
) -> None:
    created_user = await user_service.create_user(single_user)

    update_data = UserUpdateRequestSchema(
        name="update_name",
        surname="update_surname",
        password="12345678_update_password",
    )

    updated_user = await user_service.update_user(created_user.id, update_data)
    fetched_user = await user_service.get_user_by_id(created_user.id)

    assert updated_user.id == created_user.id
    assert updated_user.name == update_data.name
    assert updated_user.surname == update_data.surname
    assert updated_user.email == created_user.email
    assert updated_user.username == created_user.username

    assert fetched_user.name == update_data.name
    assert fetched_user.surname == update_data.surname


@pytest.mark.asyncio
async def test_delete_user(
    uow: UnitOfWork,
    single_user: UserSignUpRequestSchema,
    user_service: UserService,
) -> None:
    created_user = await user_service.create_user(single_user)
    await user_service.delete_user(created_user.id)

    with pytest.raises(NotFoundException) as exc_info:
        await user_service.get_user_by_id(created_user.id)

    with pytest.raises(NotFoundException) as not_user_info:
        await user_service.delete_user(created_user.id)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert not_user_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert isinstance(exc_info.value, NotFoundException)
    assert isinstance(not_user_info.value, NotFoundException)


@pytest.mark.asyncio
async def test_get_all_users_with_pagination(
    uow: UnitOfWork,
    user_factory: UserFactory,
    user_service: UserService,
) -> None:
    input_users = user_factory(22)

    with pytest.raises(NotFoundException) as empty_db:
        await user_service.get_all_users(PaginationConfig(page=1, size=5))

    pagination_page_1 = PaginationConfig(page=1, size=5)
    pagination_page_3 = PaginationConfig(page=3, size=5)

    for user in input_users:
        await user_service.create_user(user)

    users_page_1 = await user_service.get_all_users(pagination_page_1)
    users_page_3 = await user_service.get_all_users(pagination_page_3)
    users_last_page = await user_service.get_all_users(PaginationConfig(page=5, size=5))

    ids_page_1 = [user.id for user in users_page_1.items]
    users_page_2 = await user_service.get_all_users(PaginationConfig(page=2, size=5))
    ids_page_2 = [user.id for user in users_page_2.items]

    with pytest.raises(NotFoundException) as exc_info:
        await user_service.get_all_users(PaginationConfig(page=6, size=5))

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
        assert isinstance(user, UserResponseSchema)

    for user in users_page_3.items:
        assert isinstance(user, UserResponseSchema)
