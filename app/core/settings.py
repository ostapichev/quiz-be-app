from pydantic import Field, EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from ..enums import GenderEnum


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",
    )


class DataBaseTestConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env.test",
        env_file_encoding="utf-8",
        extra="allow",
    )

    POSTGRES_DB: str = Field(...)
    POSTGRES_USER: str = Field(...)
    POSTGRES_PASSWORD: str = Field(...)
    POSTGRES_HOST: str = Field(...)
    POSTGRES_PORT: int = Field(...)

    @property
    def url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


class DataBaseConfig(BaseConfig):
    POSTGRES_DB: str = Field(...)
    POSTGRES_USER: str = Field(...)
    POSTGRES_PASSWORD: str = Field(...)
    POSTGRES_HOST: str = Field(...)
    POSTGRES_PORT: int = Field(...)

    @property
    def url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


class RedisConfig(BaseConfig):
    REDIS_PORT: int = Field(...)
    REDIS_HOST: str = Field(...)
    REDIS_DB: int = Field(...)
    REDIS_TTL: int = Field(...)

    @property
    def url(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


class SuperUserConfig(BaseConfig):
    EMAIL: EmailStr = Field(...)
    PASSWORD: str = Field(...)

    NAME: str = Field(...)
    SURNAME: str = Field(...)
    GENDER: GenderEnum = Field(...)
    PICTURE: str | None = Field(...)
    PHONE: str = Field(...)


class AuthConfig(BaseConfig):
    ALGORITHM: str = Field(...)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(...)
    DUMMY_PASSWORD: str = Field(...)


class Settings(BaseConfig):
    PORT: int = Field(...)
    HOST: str = Field(...)
    CLIENT_HOST: str = Field(...)
    SECRET_KEY: str = Field(...)
    DEBUG: bool = False

    auth: AuthConfig = AuthConfig()
    superuser: SuperUserConfig = SuperUserConfig()
    db: DataBaseConfig = DataBaseConfig()
    test_db: DataBaseTestConfig = DataBaseTestConfig()
    redis: RedisConfig = RedisConfig()


settings = Settings()
