# from pydantic_settings import BaseSettings

# class Settings(BaseSettings):
#     DATABASE_URL: str

#     class Config:
#         env_file = ".env"

# settings = Settings()


# from pydantic_settings import BaseSettings


# class Settings(BaseSettings):
#     DATABASE_URL: str
#     JWT_SECRET_KEY: str
#     JWT_ALGORITHM: str = "HS256"
#     ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

#     class Config:
#         env_file = ".env"


# settings = Settings()

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    SMTP_HOST: str
    SMTP_PORT: int = 587
    SMTP_USERNAME: str
    SMTP_PASSWORD: str

    class Config:
        env_file = ".env"


settings = Settings()