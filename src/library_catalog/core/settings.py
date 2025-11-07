from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    storage: str | None = None
    jsonbin_api_key: str | None = None
    jsonbin_bin_id: str | None = None
    jsonbin_base_url: str | None = None

    class Config:
        env_file = ".env"


settings = Settings()

