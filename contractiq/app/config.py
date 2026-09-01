from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/contractiq_db"

    SECRET_KEY: str = "insecure-dev-secret-change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "ContractIQ <no-reply@contractiq.com>"

    RENEWAL_REMINDER_DAYS: str = "90,60,30,7"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def renewal_reminder_days_list(self) -> list[int]:
        return [int(x.strip()) for x in self.RENEWAL_REMINDER_DAYS.split(",") if x.strip()]


settings = Settings()
