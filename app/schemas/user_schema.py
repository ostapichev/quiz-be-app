from pydantic import EmailStr, SecretStr
from pydantic_extra_types.phone_numbers import PhoneNumber

from app.db.base_model import TimestampMixinModel
from app.schemas import BaseSchema, IDMixinSchema


class UserSignInRequestSchema(BaseSchema):
    email: EmailStr
    password: SecretStr


class UserSignUpRequestSchema(BaseSchema):
    name: str
    surname: str
    username: str
    email: EmailStr
    password: SecretStr
    phone: PhoneNumber


class UserUpdateRequestSchema(BaseSchema):
    name: str
    surname: str
    username: str
    password: SecretStr


class UserDetailsResponseSchema(BaseSchema, IDMixinSchema, TimestampMixinModel):
    name: str
    surname: str
    username: str
    email: EmailStr
    phone_number: PhoneNumber


class UserListResponseSchema(BaseSchema, IDMixinSchema, TimestampMixinModel):
    username: str
    email: EmailStr
