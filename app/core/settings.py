from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",
    )


class DataBaseSettings(BaseConfig):
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    @property
    def url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


class RedisSettings(BaseConfig):
    REDIS_PORT: int
    REDIS_HOST: str
    REDIS_DB: int
    REDIS_TTL: int

    @property
    def url(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


class Settings(BaseConfig):
    PORT: int
    HOST: str
    CLIENT_HOST: str
    SECRET_KEY: str
    DEBUG: bool = False

    db: DataBaseSettings = DataBaseSettings()
    redis: RedisSettings = RedisSettings()


settings = Settings()
