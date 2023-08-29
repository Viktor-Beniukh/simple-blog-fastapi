from pydantic.v1 import BaseSettings

from config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME


class Settings(BaseSettings):
    PROJECT_NAME: str = "simple-blog-fastapi"
    DATABASE_URL: str | None = (
        f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
