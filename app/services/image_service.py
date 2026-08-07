import logging
import shutil
import uuid

from fastapi import Request, UploadFile
from io import BytesIO
from pathlib import Path
from PIL import Image, UnidentifiedImageError

from ..db import UnitOfWork
from ..exceptions import BadRequestException
from ..schemas import UserDetailsResponse


class ImageService:
    STATIC_FOLDER = Path("static")
    MAX_FILE_SIZE = 5 * 1024 * 1024
    AVATAR_SIZE = 128

    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def upload_avatar(
        self,
        request: Request,
        current_user: UserDetailsResponse,
        file: UploadFile,
    ) -> UserDetailsResponse:
        folder = self.STATIC_FOLDER / Path("avatars") / f"user_{current_user.id}"
        filepath = folder / f"{uuid.uuid4().hex}.png"

        if folder.exists():
            shutil.rmtree(folder)

        self._save_and_process_image(file, filepath)

        return await self._update_user_avatar_path(
            request,
            current_user,
            filepath,
        )

    def _save_and_process_image(
        self,
        file: UploadFile,
        filepath: Path,
    ) -> None:

        if file.content_type not in {
            "image/jpeg",
            "image/png",
            "image/webp",
        }:
            logging.warning("This is not an image!")
            raise BadRequestException

        try:
            contents = file.file.read()
            if len(contents) > self.MAX_FILE_SIZE:
                details = "This is file too large!"
                logging.warning(details)
                raise BadRequestException(details)
            image = Image.open(BytesIO(contents))
        except UnidentifiedImageError:
            details = "Invalid image format!"
            logging.warning(details)
            raise BadRequestException(details)

        image_converted = self._image_converter(image)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        image_converted.save(filepath, format="PNG", optimize=True)

    async def _update_user_avatar_path(
        self,
        request: Request,
        current_user: UserDetailsResponse,
        filepath: Path,
    ) -> UserDetailsResponse:
        user = await self.uow.user_repository.get_user_by_id(current_user.id)
        user.profile.picture = self._build_url(request, filepath)

        await self.uow.user_repository.save(user)
        await self.uow.flush()
        await self.uow.refresh(user)

        logging.info(f"Updated avatar for {current_user.id} is saved to {filepath}")

        return UserDetailsResponse.model_validate(user)

    def _build_url(self, request: Request, filepath: Path) -> str:
        relative_path = Path(filepath).relative_to(self.STATIC_FOLDER)

        return f"{request.base_url}{self.STATIC_FOLDER}/{relative_path.as_posix()}"

    def _image_converter(self, image: Image.Image) -> Image.Image:
        image = image.convert("RGBA")
        width, height = image.size
        min_side = min(width, height)

        offset_x = (width - min_side) // 2
        offset_y = (height - min_side) // 2

        right = offset_x + min_side
        bottom = offset_y + min_side
        new_image = image.crop((offset_x, offset_y, right, bottom))

        return new_image.resize(
            (self.AVATAR_SIZE, self.AVATAR_SIZE),
            Image.Resampling.LANCZOS,
        )
