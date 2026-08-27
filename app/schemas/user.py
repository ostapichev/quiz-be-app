from typing import Self

from pydantic import EmailStr, field_validator

from ..enums import AuthMethodEnum, GenderEnum
from ..schemas import BaseSchema, IDMixinSchema, TimeStampMixinSchema
from ..utils import normalize_phone_number, password_validator


class ProfilePublic(BaseSchema):
    name: str
    surname: str
    picture: str | None = None


class ProfileBase(ProfilePublic):
    gender: GenderEnum | None = None
    phone: str | None = None


class PhoneNumberRequest(BaseSchema):
    phone: str | None = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        if not v:
            return None
        return normalize_phone_number(v)


class PasswordRequest(BaseSchema):
    password: str | None = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str | None) -> str | None:
        if not v:
            return None
        return password_validator(v)


class ProfileUpdateNumberRequest(PhoneNumberRequest):
    name: str | None = None
    surname: str | None = None
    picture: str | None = None
    gender: GenderEnum | None = None


class UserPublicBase(BaseSchema):
    email: EmailStr
    is_active: bool
    profile: ProfilePublic


class UserBase(UserPublicBase):
    is_admin: bool
    is_superuser: bool


class UserResponse(UserPublicBase, IDMixinSchema, TimeStampMixinSchema):
    pass


class UserDetailsResponse(UserBase, IDMixinSchema, TimeStampMixinSchema):
    auth_provider: AuthMethodEnum
    profile: ProfileBase


class UserSignInRequest(BaseSchema):
    username: str
    password: str


class UserSignUpRequest(PhoneNumberRequest, PasswordRequest):
    email: EmailStr
    name: str = "Name"
    surname: str = "Surname"
    gender: GenderEnum | None = None


class NewUserRequest(UserSignUpRequest):
    is_active: bool = True
    is_admin: bool = False
    is_superuser: bool = False
    auth_method: AuthMethodEnum = AuthMethodEnum.local

    @classmethod
    def from_form(
        cls,
        email: EmailStr,
        password: str,
        name: str,
        surname: str,
        phone: str | None = None,
        gender: GenderEnum | None = None,
    ) -> Self:
        return cls(
            email=email,
            password=password,
            name=name,
            surname=surname,
            phone=phone,
            gender=gender,
        )


class UserUpdateRequest(PhoneNumberRequest, PasswordRequest):
    name: str | None = None
    surname: str | None = None
    gender: GenderEnum | None = None
