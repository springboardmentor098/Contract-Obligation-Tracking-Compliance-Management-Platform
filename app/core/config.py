from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None

    class Config:
        env_file = ".env"


settings = Settings()