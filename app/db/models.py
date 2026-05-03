from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import BaseModel, IDMixinModel, TimestampMixinModel


class UserModel(BaseModel, IDMixinModel, TimestampMixinModel):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(50), nullable=False)
    surname: Mapped[str] = mapped_column(String(50), nullable=False)
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )
    phone: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=True,
    )
