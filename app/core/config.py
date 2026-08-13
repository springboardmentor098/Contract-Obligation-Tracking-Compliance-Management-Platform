import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:Rathna210@localhost:5432/contractiq_db"
    )

    class Config:
        env_file = ("Backend/.env", ".env")
        extra = "ignore"


settings = Settings()