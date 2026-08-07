from typing import TypeAlias, Callable
from urllib.parse import urlparse

import pytest

from fastapi import Request, UploadFile
from io import BytesIO
from pathlib import Path
from PIL import Image
from starlette.datastructures import Headers

from ..exceptions import BadRequestException
from ..schemas import UserDetailsResponse, NewUserRequest
from ..services import ImageService

UserFactory: TypeAlias = Callable[[int], list[NewUserRequest]]


@pytest.mark.asyncio
async def test_upload_avatar(
    image_service: ImageService,
    image_file: UploadFile,
    test_request: Request,
    current_user: UserDetailsResponse,
) -> None:
    response = await image_service.upload_avatar(
        request=test_request,
        current_user=current_user,
        file=image_file,
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
            file=file,
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
            file=file,
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
            file=file,
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
    path = Path("static/avatars/user_1/avatar.png")
    url = image_service._build_url(test_request, path)

    assert url == "http://test_server:80/static/avatars/user_1/avatar.png"
