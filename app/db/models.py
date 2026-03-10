from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import BaseModel, IDMixinModel, TimestampMixinModel


class UserModel(BaseModel, IDMixinModel, TimestampMixinModel):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(20))
    surname: Mapped[str] = mapped_column(String(30))
    username: Mapped[str] = mapped_column(String(30), unique=True)
    email: Mapped[str] = mapped_column(String(30), unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=True)
    phone: Mapped[str] = mapped_column(String(12), unique=True)
