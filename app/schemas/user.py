from pydantic import EmailStr

from ..enums import GenderEnum
from ..schemas import Base, IDMixinSchema, TimeStampMixinSchema


class ProfilePublic(Base):
    name: str
    surname: str
    picture: str | None = None


class ProfileBase(ProfilePublic):
    gender: GenderEnum
    phone: str


class ProfileUpdateRequest(Base):
    name: str | None = None
    surname: str | None = None
    picture: str | None = None
    phone: str | None = None


class UserPublicBase(Base):
    email: EmailStr
    is_active: bool
    profile: ProfilePublic


class UserBase(UserPublicBase):
    is_admin: bool
    is_superuser: bool


class UserResponse(UserPublicBase, IDMixinSchema, TimeStampMixinSchema):
    pass


class UserDetailsResponse(UserBase, IDMixinSchema, TimeStampMixinSchema):
    profile: ProfileBase


class UserSignInRequest(Base):
    username: str
    password: str


class UserSignUpRequest(Base):
    email: EmailStr
    password: str
    name: str
    surname: str
    gender: GenderEnum
    phone: str


class SuperUserRequest(UserSignUpRequest):
    is_active: bool = True
    is_admin: bool = True
    is_superuser: bool = True


class NewUserRequest(UserSignUpRequest):
    is_active: bool = True
    is_admin: bool = False
    is_superuser: bool = False


class UserUpdateRequest(Base):
    name: str | None = None
    surname: str | None = None
    password: str | None = None
    phone: str | None = None


class UpdatePasswordRequest(Base):
    password: str
