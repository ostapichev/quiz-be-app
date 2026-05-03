from typing import Optional

from pydantic import EmailStr

from app.schemas import BaseSchema, IDMixinSchema, TimeStampMixinSchema


class UserBaseSchema(BaseSchema):
    name: str
    surname: str
    username: str
    email: EmailStr
    phone: str


class UserSignInRequestSchema(BaseSchema):
    email: EmailStr
    password: str


class UserSignUpRequestSchema(UserBaseSchema):
    password: str


class UserUpdateRequestSchema(BaseSchema):
    name: Optional[str] = None
    surname: Optional[str] = None
    password: Optional[str] = None


class UserResponseSchema(
    BaseSchema,
    IDMixinSchema,
    TimeStampMixinSchema,
):
    username: str
    email: EmailStr


class UserDetailsResponseSchema(
    UserBaseSchema,
    IDMixinSchema,
    TimeStampMixinSchema,
):
    pass
