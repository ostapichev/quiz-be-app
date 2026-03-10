from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    PORT: int
    HOST: str
    CLIENT_HOST: str
    SECRET_KEY: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",
    )


settings = BaseConfig()
