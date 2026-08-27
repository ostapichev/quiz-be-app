import pytest
from urllib.parse import urlparse

from fastapi import Request
from starlette.datastructures import UploadFile
from io import BytesIO
from pathlib import Path
from PIL import Image
from starlette.datastructures import Headers

from ..exceptions import BadRequestException, NotFoundException
from ..schemas import NewUserRequest, UserDetailsResponse
from ..services import ImageService, UserService
from .conftest import ImageFactory, UserFactory


@pytest.mark.asyncio
async def test_upload_avatar(
    image_service: ImageService,
    make_image_file: ImageFactory,
    test_request: Request,
    current_user: UserDetailsResponse,
) -> None:
    response = await image_service.upload_avatar(
        request=test_request,
        current_user=current_user,
        avatar=make_image_file(),
    )

    parsed = urlparse(response.profile.picture)
    filepath = Path(parsed.path.lstrip("/"))
    image = Image.open(filepath)

    assert isinstance(response, UserDetailsResponse)
    assert response.profile.picture is not None
    assert filepath.exists()

    assert image.size == (
        ImageService.AVATAR_SIZE,
        ImageService.AVATAR_SIZE,
    )


@pytest.mark.asyncio
async def test_delete_avatar_removes_file_from_disk(
    image_service: ImageService,
    make_image_file: ImageFactory,
    test_request: Request,
    current_user: UserDetailsResponse,
) -> None:
    await image_service.upload_avatar(
        request=test_request,
        current_user=current_user,
        avatar=make_image_file(),
    )

    user_before = await image_service.uow.user_repository.get_user_by_id(
        current_user.id
    )
    relative_path = user_before.profile.picture
    full_path = image_service.STATIC_FOLDER / relative_path

    assert full_path.exists()
    await image_service.delete_avatar(current_user)

    assert not full_path.exists()
    assert not full_path.parent.exists()


@pytest.mark.asyncio
async def test_delete_avatar_when_no_avatar_exists(
    image_service: ImageService,
    current_user: UserDetailsResponse,
) -> None:
    with pytest.raises(NotFoundException):
        await image_service.delete_avatar(current_user)


@pytest.mark.asyncio
async def test_delete_avatar_when_file_missing_on_disk(
    image_service: ImageService,
    current_user: UserDetailsResponse,
) -> None:
    user = await image_service.uow.user_repository.get_user_by_id(current_user.id)
    user.profile.picture = "avatars/user_fake/nonexistent.png"

    await image_service.uow.user_repository.save(user)
    await image_service.uow.flush()

    deleted = await image_service.delete_avatar(current_user)

    assert deleted.profile.picture is None


@pytest.mark.asyncio
async def test_delete_avatar_twice_raises_not_found(
    image_service: ImageService,
    test_request: Request,
    current_user: UserDetailsResponse,
    make_image_file: ImageFactory,
) -> None:
    await image_service.upload_avatar(
        request=test_request,
        current_user=current_user,
        avatar=make_image_file(),
    )
    await image_service.delete_avatar(current_user)

    with pytest.raises(NotFoundException):
        await image_service.delete_avatar(current_user)


@pytest.mark.asyncio
async def test_delete_avatar_does_not_affect_other_users(
    image_service: ImageService,
    user_service: UserService,
    current_user: UserDetailsResponse,
    test_request: Request,
    make_image_file: ImageFactory,
    user_factory: UserFactory,
) -> None:
    user_data = NewUserRequest(**user_factory(1)[0].model_dump())
    another_user = await user_service.create_user(user_data)

    await image_service.upload_avatar(
        request=test_request,
        current_user=current_user,
        avatar=make_image_file(),
    )

    await image_service.upload_avatar(
        request=test_request,
        current_user=another_user,
        avatar=make_image_file(),
    )

    await image_service.delete_avatar(current_user)

    another_user_data = await image_service.uow.user_repository.get_user_by_id(
        another_user.id
    )
    assert another_user_data.profile.picture is not None


@pytest.mark.asyncio
async def test_upload_avatar_invalid_content_type(
    image_service: ImageService,
    test_request: Request,
    current_user: UserDetailsResponse,
) -> None:
    file = UploadFile(
        filename="text.txt",
        file=BytesIO(b"Hello"),
        headers=Headers({"content-type": "text/plain"}),
    )

    with pytest.raises(BadRequestException):
        await image_service.upload_avatar(
            request=test_request,
            current_user=current_user,
            avatar=file,
        )


@pytest.mark.asyncio
async def test_upload_avatar_invalid_image(
    image_service: ImageService,
    test_request: Request,
    current_user: UserDetailsResponse,
) -> None:
    file = UploadFile(
        filename="image.png",
        file=BytesIO(b"abcdef"),
        headers=Headers({"content-type": "image/png"}),
    )

    with pytest.raises(BadRequestException):
        await image_service.upload_avatar(
            request=test_request,
            current_user=current_user,
            avatar=file,
        )


@pytest.mark.asyncio
async def test_upload_avatar_large_file(
    image_service: ImageService,
    test_request: Request,
    current_user: UserDetailsResponse,
) -> None:
    file = UploadFile(
        filename="large.png",
        file=BytesIO(b"x" * (ImageService.MAX_FILE_SIZE + 1)),
        headers=Headers({"content-type": "image/png"}),
    )

    with pytest.raises(BadRequestException):
        await image_service.upload_avatar(
            request=test_request,
            current_user=current_user,
            avatar=file,
        )


def test_image_converter(image_service: ImageService) -> None:
    image = Image.new(
        "RGB",
        (600, 300),
        "red",
    )
    converted = image_service._image_converter(image)

    assert converted.size == (
        ImageService.AVATAR_SIZE,
        ImageService.AVATAR_SIZE,
    )


def test_build_url(image_service: ImageService, test_request: Request) -> None:
    path = Path("avatars/user_1/avatar.png")
    url = image_service._build_url(test_request, path)

    assert url == "http://test_server:80/static/avatars/user_1/avatar.png"
