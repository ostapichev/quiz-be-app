from enum import StrEnum


class AuthMethodEnum(StrEnum):
    local = "local"
    auth0 = "auth0"


class GenderEnum(StrEnum):
    male = "male"
    female = "female"
