from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str

    smtp_host: str
    smtp_port: int = 587
    smtp_username: str
    smtp_password: str

    class Config:
        env_file = ".env"


settings = Settings()