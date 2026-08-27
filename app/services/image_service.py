import logging
import shutil
import uuid
from io import BytesIO
from pathlib import Path

import httpx
from fastapi import Request, UploadFile
from starlette.datastructures import Headers, UploadFile as StarletteUploadFile
from PIL import Image, UnidentifiedImageError

from ..core.settings import settings
from ..db import UnitOfWork, User
from ..exceptions import BadRequestException, NotFoundException
from ..schemas import UserDetailsResponse

logger = logging.getLogger(__name__)


class ImageService:
    STATIC_FOLDER = settings.STATIC_FOLDER
    MAX_FILE_SIZE = settings.MAX_FILE_SIZE
    AVATAR_SIZE = settings.AVATAR_SIZE

    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def upload_avatar(
        self,
        request: Request,
        current_user: UserDetailsResponse,
        avatar: UploadFile,
    ) -> UserDetailsResponse:
        filepath = self.create_filepath(current_user.public_id)
        self._save_and_process_image(avatar, filepath)
        relative_path = self._to_relative(filepath)

        return await self._update_user_avatar_path(
            request,
            current_user,
            relative_path,
        )

    async def delete_avatar(
        self,
        current_user: UserDetailsResponse,
    ) -> UserDetailsResponse:
        user = await self.uow.user_repository.get_user_by_id(current_user.id)
        if user is None or not user.profile or not user.profile.picture:
            raise NotFoundException(f"{current_user.email} - has no avatar")

        relative_path = user.profile.picture
        full_path = self.STATIC_FOLDER / relative_path
        if full_path.exists():
            try:
                shutil.rmtree(full_path.parent)
            except OSError:
                logger.warning(f"Failed to clean up avatar file at {full_path}")
        else:
            logger.warning(
                f"Avatar file not found on disk at {full_path}, nothing to delete"
            )

        user.profile.picture = None
        await self._save_user_data(user)

        logger.warning(f"Avatar deleted for user: {user.email}")
        return UserDetailsResponse.model_validate(user)

    async def create_avatar(
        self,
        user_id: str,
        avatar_file: UploadFile | None = None,
    ) -> str | None:
        if avatar_file is not None:
            filepath = self.create_filepath(user_id)
            self._save_and_process_image(avatar_file, filepath)

            return self._to_relative(filepath)
        return None

    async def create_avatar_from_url(
        self,
        user_id: str,
        picture_url: str,
    ) -> str | None:
        if not picture_url:
            return None

        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(picture_url, timeout=10.0)
                response.raise_for_status()
        except httpx.HTTPError:
            logger.warning(
                f"Failed to download avatar for user {user_id} from {picture_url}"
            )
            return None

        filepath = self.create_filepath(user_id)
        content_type = response.headers.get("content-type", "image/png")

        fake_upload_file = StarletteUploadFile(
            file=BytesIO(response.content),
            filename="avatar.png",
            headers=Headers({"content-type": content_type}),
        )
        self._save_and_process_image(fake_upload_file, filepath)

        return self._to_relative(filepath)

    def create_filepath(self, user_id: str) -> Path:
        folder = self.STATIC_FOLDER / Path("avatars") / f"user_{user_id}"
        filepath = folder / f"{uuid.uuid4().hex}.png"

        if folder.exists():
            shutil.rmtree(folder)

        return filepath

    def _to_relative(self, filepath: Path) -> str:
        return str(filepath.relative_to(self.STATIC_FOLDER))

    def _save_and_process_image(
        self,
        avatar: UploadFile,
        filepath: Path,
    ) -> None:
        if avatar.content_type not in {
            "image/jpeg",
            "image/png",
            "image/webp",
        }:
            details = "This is not an image!"
            logging.warning(details)
            raise BadRequestException(details)

        try:
            contents = avatar.file.read()
            if len(contents) > self.MAX_FILE_SIZE:
                raise BadRequestException("This is file too large!")
            image = Image.open(BytesIO(contents))
        except UnidentifiedImageError:
            raise BadRequestException("Invalid image format!")

        image_converted = self._image_converter(image)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        image_converted.save(filepath, format="PNG", optimize=True)

    async def _update_user_avatar_path(
        self,
        request: Request,
        current_user: UserDetailsResponse,
        relative_path: str,
    ) -> UserDetailsResponse:
        user = await self.uow.user_repository.get_user_by_id(current_user.id)
        user.profile.picture = relative_path
        await self._save_user_data(user)

        logging.info(
            f"Updated avatar for user id: {current_user.id}, is saved to {relative_path}"
        )
        return self._to_response(request, user)

    async def _save_user_data(self, user: UserDetailsResponse) -> None:
        await self.uow.user_repository.save(user)
        await self.uow.flush()
        await self.uow.refresh(user)

    def _to_response(self, request: Request, user: User) -> UserDetailsResponse:
        response = UserDetailsResponse.model_validate(user)
        if response.profile and response.profile.picture:
            response.profile.picture = self._build_url(
                request, response.profile.picture
            )
        return response

    def _build_url(self, request: Request, relative_path: str) -> str:
        return f"{request.base_url}{self.STATIC_FOLDER}/{relative_path}"

    def _image_converter(self, image: Image.Image) -> Image.Image:
        avatar_size = self.AVATAR_SIZE

        image = image.convert("RGBA")
        width, height = image.size
        min_side = min(width, height)

        offset_x = (width - min_side) // 2
        offset_y = (height - min_side) // 2

        right = offset_x + min_side
        bottom = offset_y + min_side
        new_image = image.crop((offset_x, offset_y, right, bottom))

        return new_image.resize(
            (avatar_size, avatar_size),
            Image.Resampling.LANCZOS,
        )
