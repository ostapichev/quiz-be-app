import uuid
from typing import Annotated

from sqlalchemy import String, Boolean, false, true, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base
from ..enums import GenderEnum, AuthMethodEnum

optional_str = Annotated[str | None, mapped_column(String(255), nullable=True)]
boolean_flag_false = Annotated[
    bool,
    mapped_column(Boolean, default=False, server_default=false()),
]
boolean_flag_true = Annotated[
    bool,
    mapped_column(Boolean, default=True, server_default=true()),
]


class User(Base):
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )
    hashed_password: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    auth_provider: Mapped[AuthMethodEnum]
    is_active: Mapped[boolean_flag_true]
    is_admin: Mapped[boolean_flag_false]
    is_superuser: Mapped[boolean_flag_false]
    profile: Mapped["Profile"] = relationship(
        "Profile",
        back_populates="user",
        uselist=False,
        lazy="selectin",
    )


class Profile(Base):
    name: Mapped[optional_str]
    surname: Mapped[optional_str]
    gender: Mapped[GenderEnum | None]
    picture: Mapped[optional_str]
    phone: Mapped[str | None] = mapped_column(
        String(20),
        unique=True,
        nullable=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        primary_key=True,
    )
    user: Mapped["User"] = relationship(
        "User",
        back_populates="profile",
        uselist=False,
    )
